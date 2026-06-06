import math
from django.utils import timezone
from .models import Usuario, Sala, Recurso, PostoDeTrabalho, Reserva, PerfilProfissional


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


def get_sugestoes_por_perfil(usuario):
    perfil = usuario.perfil_profissional
    if not perfil:
        return PostoDeTrabalho.objects.filter(disponivel=True).select_related('sala')

    tipos = perfil.tipos_recurso_necessarios
    qs = PostoDeTrabalho.objects.filter(disponivel=True, sala__ativo=True).select_related('sala')

    if not tipos:
        return qs.order_by('sala__nome', 'coord_x', 'coord_y')

    if 'COMPUTADOR' in tipos:
        qs = qs.filter(tem_maquina=True)
    else:
        qs = qs.filter(tem_maquina=False)

    return qs.order_by('sala__nome', 'coord_x', 'coord_y')


def get_sugestoes_por_equipe(usuario):
    postos_compativeis = list(get_sugestoes_por_perfil(usuario))

    if not postos_compativeis:
        return PostoDeTrabalho.objects.none()

    if not usuario.departamento:
        return get_sugestoes_por_perfil(usuario)

    agora = timezone.now()
    proximos_7_dias = agora + timezone.timedelta(days=7)

    reservas_equipe = Reserva.objects.filter(
        usuario__departamento=usuario.departamento,
        status=Reserva.Status.CONFIRMADA,
        data_hora_inicio__gte=agora,
        data_hora_inicio__lte=proximos_7_dias,
    ).exclude(usuario=usuario).select_related('posto')

    if not reservas_equipe.exists():
        return get_sugestoes_por_perfil(usuario)

    coords_equipe = [(r.posto.coord_x, r.posto.coord_y) for r in reservas_equipe]

    def distancia_minima(posto):
        return min(
            math.sqrt((posto.coord_x - cx) ** 2 + (posto.coord_y - cy) ** 2)
            for cx, cy in coords_equipe
        )

    postos_ordenados = sorted(postos_compativeis, key=distancia_minima)
    ids_ordenados = [p.id for p in postos_ordenados]
    postos_por_id = {p.id: p for p in postos_compativeis}
    return [postos_por_id[i] for i in ids_ordenados]


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