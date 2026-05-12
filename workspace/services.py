from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Sala, PostoDeTrabalho, Reserva
from . import selectors


def criar_usuario(dados):
    from .serializers import UsuarioCadastroSerializer
    serializer = UsuarioCadastroSerializer(data=dados)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def atualizar_perfil(usuario, dados):
    campos_permitidos = ['first_name', 'last_name', 'departamento']
    for campo in campos_permitidos:
        if campo in dados:
            setattr(usuario, campo, dados[campo])
    usuario.save()
    return usuario


def criar_sala(dados):
    _validar_manutencao(dados)
    sala = Sala.objects.create(**dados)
    return sala


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


def criar_reserva(usuario, dados):
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


def _validar_manutencao(dados, instance=None):
    status = dados.get('status', getattr(instance, 'status', None))

    if status == Sala.Status.MANUTENCAO:
        motivo = dados.get('motivo_manutencao', getattr(instance, 'motivo_manutencao', ''))
        prazo = dados.get('prazo_estimado', getattr(instance, 'prazo_estimado', None))

        if not motivo:
            raise ValidationError({'motivo_manutencao': 'Obrigatório quando status é Manutenção.'})
        if not prazo:
            raise ValidationError({'prazo_estimado': 'Obrigatório quando status é Manutenção.'})