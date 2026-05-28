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
    return Sala.objects.get(id=sala_id)


def get_todas_salas(filtros=None):
    qs = Sala.objects.all()

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
    """
    Retorna postos disponíveis compatíveis com o perfil profissional do usuário.
    Se o perfil exige COMPUTADOR, filtra postos com tem_maquina=True.
    Para outros tipos de recurso, a compatibilidade é verificada via recursos da sala.
    Postos sem máquina são sugeridos para perfis que não exigem COMPUTADOR.
    """
    perfil = usuario.perfil_profissional
    if not perfil:
        return PostoDeTrabalho.objects.none()

    tipos = perfil.tipos_recurso_necessarios
    qs = PostoDeTrabalho.objects.filter(disponivel=True).select_related('sala')

    if 'COMPUTADOR' in tipos:
        qs = qs.filter(tem_maquina=True)
    else:
        qs = qs.filter(tem_maquina=False)

    return qs.order_by('sala__nome', 'coord_x', 'coord_y')


def get_recursos_by_sala(sala_id):
    return Recurso.objects.filter(sala_id=sala_id)


def get_reservas_by_usuario(usuario_id):
    return Reserva.objects.filter(usuario_id=usuario_id).select_related('posto', 'posto__sala').order_by('-data_hora_inicio')


def get_todas_reservas():
    return Reserva.objects.all().select_related('usuario', 'posto', 'posto__sala').order_by('-data_hora_inicio')


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