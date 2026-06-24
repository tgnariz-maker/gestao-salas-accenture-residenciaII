import math
from datetime import datetime, date, time
from django.utils import timezone
from .models import Usuario, Sala, Recurso, PostoDeTrabalho, Reserva, PerfilProfissional, Equipe


def get_perfil_profissional_by_id(perfil_id):
    return PerfilProfissional.objects.get(id=perfil_id)


def get_perfil_profissional_by_nome(nome):
    return PerfilProfissional.objects.filter(nome__iexact=nome).first()


def get_todos_perfis_profissionais():
    return PerfilProfissional.objects.all().order_by('nome')


def get_usuario_by_id(usuario_id):
    return Usuario.objects.get(id=usuario_id)


def get_todos_usuarios():
    return Usuario.objects.all().select_related('perfil_profissional').order_by('username')


def get_sala_by_id(sala_id):
    return Sala.objects.get(id=sala_id, ativo=True)


def get_todas_salas(filtros=None):
    qs = Sala.objects.filter(ativo=True)

    if not filtros:
        return qs

    if 'status' in filtros:
        qs = qs.filter(status=filtros['status'])
    if 'capacidade_min' in filtros:
        qs = qs.filter(capacidade__gte=filtros['capacidade_min'])
    if 'tem_projetor' in filtros:
        qs = qs.filter(tem_projetor=filtros['tem_projetor'])
    if 'tem_videoconferencia' in filtros:
        qs = qs.filter(tem_videoconferencia=filtros['tem_videoconferencia'])
    if 'tem_computadores' in filtros:
        qs = qs.filter(tem_computadores=filtros['tem_computadores'])
    if 'tem_televisao' in filtros:
        qs = qs.filter(tem_televisao=filtros['tem_televisao'])
    if 'tem_impressora' in filtros:
        qs = qs.filter(tem_impressora=filtros['tem_impressora'])

    return qs


def get_postos_by_sala(sala_id):
    return PostoDeTrabalho.objects.filter(sala_id=sala_id)


def get_posto_by_id(posto_id):
    return PostoDeTrabalho.objects.get(id=posto_id)


def get_postos_disponiveis_by_sala(sala_id):
    return PostoDeTrabalho.objects.filter(sala_id=sala_id, disponivel=True)


def get_disponibilidade_sala(sala_id, data):
    sala = get_sala_by_id(sala_id)

    inicio_dia = timezone.make_aware(datetime.combine(data, time.min))
    fim_dia = timezone.make_aware(datetime.combine(data, time.max))

    postos_reservados_ids = Reserva.objects.filter(
        posto__sala=sala,
        status=Reserva.Status.CONFIRMADA,
        data_hora_inicio__lt=fim_dia,
        data_hora_fim__gt=inicio_dia,
    ).values_list('posto_id', flat=True)

    todos_postos = PostoDeTrabalho.objects.filter(sala=sala)
    postos_livres = todos_postos.exclude(id__in=postos_reservados_ids).filter(disponivel=True)
    postos_ocupados = todos_postos.filter(id__in=postos_reservados_ids)

    try:
        config = sala.configuracao
        dia_semana = data.weekday()
        sala_aberta = (
            dia_semana in config.dias_funcionamento
            and data not in config.feriados
        )
    except Exception:
        sala_aberta = sala.status != Sala.Status.MANUTENCAO

    return {
        'sala_id': sala.id,
        'sala_nome': sala.nome,
        'data': data.isoformat(),
        'sala_aberta': sala_aberta,
        'total_postos': todos_postos.count(),
        'postos_livres': postos_livres.count(),
        'postos_ocupados': postos_ocupados.count(),
        'ids_postos_livres': list(postos_livres.values_list('id', flat=True)),
        'ids_postos_ocupados': list(postos_ocupados.values_list('id', flat=True)),
    }


def get_sugestoes_por_perfil(usuario):
    perfil = usuario.perfil_profissional
    agora = timezone.now()

    postos_ocupados_ids = Reserva.objects.filter(
        status=Reserva.Status.CONFIRMADA,
        data_hora_inicio__lte=agora,
        data_hora_fim__gt=agora,
    ).values_list('posto_id', flat=True)

    qs = PostoDeTrabalho.objects.filter(
        disponivel=True,
        sala__ativo=True,
    ).exclude(id__in=postos_ocupados_ids).select_related('sala')

    if not perfil or not perfil.tipos_recurso_necessarios:
        return qs.order_by('sala__nome', 'coord_x', 'coord_y')

    tipos = perfil.tipos_recurso_necessarios

    if 'COMPUTADOR' in tipos:
        qs = qs.filter(tem_maquina=True)
    else:
        qs = qs.filter(tem_maquina=False)

    return qs.order_by('sala__nome', 'coord_x', 'coord_y')


def get_todas_equipes():
    return Equipe.objects.prefetch_related('membros').order_by('nome')


def get_equipe_by_id(equipe_id):
    return Equipe.objects.prefetch_related('membros__perfil_profissional').get(id=equipe_id)


def get_sugestoes_por_equipe(usuario, equipe_id):
    equipe = get_equipe_by_id(equipe_id)
    membros = list(equipe.membros.select_related('perfil_profissional').all())

    if not membros:
        return PostoDeTrabalho.objects.none()

    agora = timezone.now()
    postos_ocupados_ids = Reserva.objects.filter(
        status=Reserva.Status.CONFIRMADA,
        data_hora_inicio__lte=agora,
        data_hora_fim__gt=agora,
    ).values_list('posto_id', flat=True)

    postos_disponiveis = list(
        PostoDeTrabalho.objects.filter(
            disponivel=True,
            sala__ativo=True,
        ).exclude(id__in=postos_ocupados_ids).select_related('sala')
    )

    if not postos_disponiveis:
        return PostoDeTrabalho.objects.none()

    def posto_atende_membro(posto, membro):
        perfil = membro.perfil_profissional
        if not perfil or not perfil.tipos_recurso_necessarios:
            return True
        if 'COMPUTADOR' in perfil.tipos_recurso_necessarios:
            return posto.tem_maquina
        return True

    def score_posto(posto):
        return sum(1 for m in membros if posto_atende_membro(posto, m))

    postos_com_score = sorted(postos_disponiveis, key=score_posto, reverse=True)
    melhor_score = score_posto(postos_com_score[0]) if postos_com_score else 0
    postos_filtrados = [p for p in postos_com_score if score_posto(p) == melhor_score]

    if len(postos_filtrados) > 1:
        def proximidade(posto):
            outros = [p for p in postos_filtrados if p.id != posto.id]
            if not outros:
                return 0
            return sum(
                math.sqrt((posto.coord_x - p.coord_x) ** 2 + (posto.coord_y - p.coord_y) ** 2)
                for p in outros
            )
        postos_filtrados = sorted(postos_filtrados, key=proximidade)

    return postos_filtrados[:len(membros)]


def get_recursos_by_sala(sala_id):
    return Recurso.objects.filter(sala_id=sala_id)


def get_reservas_by_usuario(usuario_id):
    return Reserva.objects.filter(
        usuario_id=usuario_id
    ).select_related('posto', 'posto__sala').order_by('-data_hora_inicio')


def get_todas_reservas():
    return Reserva.objects.all().select_related(
        'usuario', 'posto', 'posto__sala'
    ).order_by('-data_hora_inicio')


def get_reserva_by_id(reserva_id):
    return Reserva.objects.get(id=reserva_id)


def get_reservas_conflitantes(posto_id, inicio, fim, excluir_id=None):
    qs = Reserva.objects.filter(
        posto_id=posto_id,
        status=Reserva.Status.CONFIRMADA,
        data_hora_inicio__lt=fim,
        data_hora_fim__gt=inicio,
    )
    if excluir_id:
        qs = qs.exclude(id=excluir_id)
    return qs


def get_historico_by_usuario(usuario_id):
    return Reserva.objects.filter(
        usuario_id=usuario_id
    ).select_related('posto', 'posto__sala').order_by('-data_hora_inicio')


def get_historico_completo():
    return Reserva.objects.all().select_related(
        'usuario', 'posto', 'posto__sala'
    ).order_by('-data_hora_inicio')