import cv2
import numpy as np
import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Sala, PostoDeTrabalho, Reserva, PerfilProfissional
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
    if sala.reservas.filter(
        status=Reserva.Status.CONFIRMADA,
        data_hora_fim__gte=timezone.now()
    ).exists():
        raise ValidationError('Não é possível remover uma sala com reservas ativas.')
    sala.delete()


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
    area_imagem = h_img * w_img

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    candidatos = []
    contornos_validos = 0

    for c in contornos:
        area = cv2.contourArea(c)
        if area > area_imagem * 0.5:
            continue
        if 500 <= area <= 2000:
            x, y, w, h = cv2.boundingRect(c)
            ratio = w / h if h > 0 else 0
            if 0.5 <= ratio <= 2.0:
                perimetro = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.04 * perimetro, True)
                contornos_validos += 1
                if len(approx) == 4:
                    candidatos.append((x + w // 2, y + h // 2))

    postos_coords = _deduplicar_pontos(candidatos, distancia_min=25)

    postos_coords = [
        (x, y) for x, y in postos_coords
        if not (y < 200)
        and not (x > 1150 and y < 500)
        and not (x > 1380 and 400 < y < 1000)
    ]

    if not postos_coords:
        raise ValidationError(
            'Nenhum posto de trabalho identificado na imagem. '
            'Verifique se a imagem é uma planta baixa válida com fundo escuro e linhas claras.'
        )

    precisao = round((len(postos_coords) / contornos_validos * 100), 1) if contornos_validos > 0 else 0
    precisao = min(precisao, 100.0)

    postos_criados = []
    for coord_x, coord_y in postos_coords:
        posto = PostoDeTrabalho.objects.create(
            sala=sala,
            coord_x=coord_x,
            coord_y=coord_y,
            disponivel=True,
            tem_maquina=True,
            tipo=PostoDeTrabalho.Tipo.INDIVIDUAL,
        )
        postos_criados.append(posto)

    logger.info(
        'Planta processada: sala=%s, postos_detectados=%d, precisao=%.1f%%',
        sala.nome, len(postos_criados), precisao
    )

    return {
        'postos_criados': postos_criados,
        'total_detectado': len(postos_criados),
        'precisao_estimada': precisao,
        'alerta_precisao': precisao < 85,
    }


def _deduplicar_pontos(pontos, distancia_min=25):
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