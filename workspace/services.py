import cv2
import numpy as np
import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Sala, PostoDeTrabalho, Reserva, PerfilProfissional, Equipe
from . import selectors

logger = logging.getLogger('workspace')


def criar_perfil_profissional(dados):
    from .serializers import PerfilProfissionalSerializer
    serializer = PerfilProfissionalSerializer(data=dados)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def atualizar_perfil_profissional(perfil, dados):
    from .serializers import PerfilProfissionalSerializer
    serializer = PerfilProfissionalSerializer(perfil, data=dados, partial=True)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def deletar_perfil_profissional(perfil):
    if perfil.usuarios.exists():
        raise ValidationError('Não é possível remover um perfil vinculado a usuários.')
    perfil.delete()


def criar_usuario(dados):
    from .serializers import UsuarioCadastroSerializer
    serializer = UsuarioCadastroSerializer(data=dados)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def atualizar_perfil(usuario, dados):
    campos_permitidos = ['first_name', 'last_name', 'departamento', 'perfil_profissional']
    for campo in campos_permitidos:
        if campo in dados:
            setattr(usuario, campo, dados[campo])
    usuario.save()
    return usuario


def criar_equipe(dados):
    from .serializers import EquipeSerializer
    serializer = EquipeSerializer(data=dados)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def atualizar_equipe(equipe, dados):
    from .serializers import EquipeSerializer
    serializer = EquipeSerializer(equipe, data=dados, partial=True)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def criar_sala(dados):
    _validar_manutencao(dados)
    return Sala.objects.create(**dados)


def atualizar_status_sala(sala, dados):
    _validar_manutencao(dados, instance=sala)
    for campo, valor in dados.items():
        setattr(sala, campo, valor)
    sala.save()
    return sala


def deletar_sala(sala):
    if Reserva.objects.filter(
        posto__sala=sala,
        status=Reserva.Status.CONFIRMADA,
        data_hora_fim__gte=timezone.now()
    ).exists():
        raise ValidationError('Não é possível remover uma sala com reservas ativas.')
    sala.ativo = False
    sala.save(update_fields=['ativo'])


def atualizar_posto(posto, dados):
    posto.disponivel = dados.get('disponivel', posto.disponivel)
    posto.save()
    return posto


def rotular_posto(posto, dados):
    campos_permitidos = ['tipo', 'tem_maquina', 'disponivel']
    for campo in campos_permitidos:
        if campo in dados:
            setattr(posto, campo, dados[campo])
    posto.save()
    return posto


def criar_reserva(usuario, dados):
    if not usuario.perfil_profissional:
        raise ValidationError('Seu usuário não possui perfil profissional. Solicite ao administrador.')

    posto_id = dados.get('posto').id if hasattr(dados.get('posto'), 'id') else dados.get('posto')
    inicio = dados.get('data_hora_inicio')
    fim = dados.get('data_hora_fim')

    posto = selectors.get_posto_by_id(posto_id)

    if not posto.disponivel:
        raise ValidationError('Este posto está indisponível.')

    if posto.sala.status == Sala.Status.MANUTENCAO:
        raise ValidationError('Não é possível reservar postos em salas em manutenção.')

    antecedencia_minima = timezone.now() + timedelta(minutes=30)
    if inicio < antecedencia_minima:
        raise ValidationError('A reserva deve ser feita com pelo menos 30 minutos de antecedência.')

    conflitos = selectors.get_reservas_conflitantes(posto_id, inicio, fim)
    if conflitos.exists():
        raise ValidationError('Horário indisponível para este posto.')

    reserva_dupla = Reserva.objects.filter(
        usuario=usuario,
        status=Reserva.Status.CONFIRMADA,
        data_hora_inicio__lt=fim,
        data_hora_fim__gt=inicio,
    ).exists()

    if reserva_dupla:
        raise ValidationError('Você já possui uma reserva neste horário.')

    return Reserva.objects.create(
        usuario=usuario,
        posto=posto,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
        status=Reserva.Status.CONFIRMADA,
    )


def cancelar_reserva(reserva, usuario):
    if reserva.usuario != usuario and usuario.tipo_perfil != 'ADMIN':
        raise PermissionDenied('Você não tem permissão para cancelar esta reserva.')

    if reserva.status == Reserva.Status.CANCELADA:
        raise ValidationError('Esta reserva já foi cancelada.')

    if reserva.data_hora_inicio <= timezone.now():
        raise ValidationError('Não é possível cancelar uma reserva que já iniciou.')

    reserva.status = Reserva.Status.CANCELADA
    reserva.save()
    return reserva


def processar_planta_baixa(imagem_bytes, sala_id):
    sala = selectors.get_sala_by_id(sala_id)

    nparr = np.frombuffer(imagem_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValidationError('Não foi possível processar a imagem. Verifique o formato do arquivo.')

    h_img, w_img = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    media_brilho = np.mean(gray)
    if media_brilho > 127:
        gray = cv2.bitwise_not(gray)

    margem_borda = int(min(h_img, w_img) * 0.04)

    candidatos_tm = _detectar_por_template(gray, h_img, w_img)
    candidatos_canny = _detectar_por_canny(gray, h_img, w_img)

    todos_coords = [(x, y) for x, y, _ in candidatos_tm] + candidatos_canny
    distancia_dedup = max(20, int(min(h_img, w_img) * 0.018))
    postos_coords = _deduplicar_pontos(todos_coords, distancia_min=distancia_dedup)

    postos_coords = [
        (x, y) for x, y in postos_coords
        if margem_borda < x < w_img - margem_borda
        and margem_borda < y < h_img - margem_borda
    ]

    if not postos_coords:
        raise ValidationError(
            'Nenhum posto de trabalho identificado na imagem. '
            'Verifique se a imagem é uma planta baixa válida.'
        )

    scores_tm = [s for _, _, s in candidatos_tm]
    confianca_media = round(float(np.mean(scores_tm)) * 100, 1) if scores_tm else 0.0
    confianca_media = min(confianca_media, 100.0)

    postos_criados = []
    for coord_x, coord_y in postos_coords:
        posto = PostoDeTrabalho.objects.create(
            sala=sala,
            coord_x=int(coord_x),
            coord_y=int(coord_y),
            disponivel=True,
            tem_maquina=True,
            tipo=PostoDeTrabalho.Tipo.INDIVIDUAL,
        )
        postos_criados.append(posto)

    logger.info(
        'Planta processada: sala=%s, postos_detectados=%d, confianca=%.1f%%',
        sala.nome, len(postos_criados), confianca_media
    )

    return {
        'postos_criados': postos_criados,
        'total_detectado': len(postos_criados),
        'confianca_media': confianca_media,
        'alerta_revisao': confianca_media < 75,
    }


def _detectar_por_template(gray, h_img, w_img):
    regioes_template = [
        (0.06, 0.87),
        (0.11, 0.87),
        (0.02, 0.67),
        (0.62, 0.88),
        (0.67, 0.88),
        (0.71, 0.88),
        (0.62, 0.95),
        (0.93, 0.95),
        (0.93, 0.85),
    ]

    margem_rel = 0.019
    resultados = []

    for rx, ry in regioes_template:
        cx = int(rx * w_img)
        cy = int(ry * h_img)
        margem = int(margem_rel * min(h_img, w_img))

        y1, y2 = max(0, cy - margem), min(h_img, cy + margem)
        x1, x2 = max(0, cx - margem), min(w_img, cx + margem)
        t = gray[y1:y2, x1:x2]

        if t.shape[0] < 5 or t.shape[1] < 5:
            continue

        for escala in [0.85, 0.95, 1.0, 1.05, 1.15]:
            ts = cv2.resize(t, (0, 0), fx=escala, fy=escala)
            if ts.shape[0] < 5 or ts.shape[1] < 5:
                continue
            res = cv2.matchTemplate(gray, ts, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.58)
            th, tw = ts.shape[:2]
            for px, py in zip(loc[1].tolist(), loc[0].tolist()):
                score = float(res[py, px])
                resultados.append((px + tw // 2, py + th // 2, score))

    return resultados


def _detectar_por_canny(gray, h_img, w_img):
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )
    bordas = cv2.Canny(thresh, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    bordas = cv2.dilate(bordas, kernel, iterations=1)
    contornos, _ = cv2.findContours(bordas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    area_min = h_img * w_img * 0.0001
    area_max = h_img * w_img * 0.005
    candidatos = []

    for c in contornos:
        area = cv2.contourArea(c)
        if area < area_min or area > area_max:
            continue
        x, y, w, h = cv2.boundingRect(c)
        ratio = w / h if h > 0 else 0
        if not (0.3 <= ratio <= 3.0):
            continue
        perim = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * perim, True)
        if 3 <= len(approx) <= 6:
            candidatos.append((x + w // 2, y + h // 2))

    return candidatos


def _deduplicar_pontos(pontos, distancia_min=25):
    if not pontos:
        return []
    usados = [False] * len(pontos)
    resultado = []
    for i, (x1, y1) in enumerate(pontos):
        if usados[i]:
            continue
        cluster_x, cluster_y, count = x1, y1, 1
        for j, (x2, y2) in enumerate(pontos):
            if i != j and not usados[j]:
                if abs(x1 - x2) < distancia_min and abs(y1 - y2) < distancia_min:
                    cluster_x += x2
                    cluster_y += y2
                    count += 1
                    usados[j] = True
        resultado.append((cluster_x // count, cluster_y // count))
        usados[i] = True
    return resultado


def _validar_manutencao(dados, instance=None):
    status = dados.get('status', getattr(instance, 'status', None))

    if status == Sala.Status.MANUTENCAO:
        motivo = dados.get('motivo_manutencao', getattr(instance, 'motivo_manutencao', ''))
        prazo = dados.get('prazo_estimado', getattr(instance, 'prazo_estimado', None))

        if not motivo:
            raise ValidationError({'motivo_manutencao': 'Obrigatório quando status é Manutenção.'})
        if not prazo:
            raise ValidationError({'prazo_estimado': 'Obrigatório quando status é Manutenção.'})