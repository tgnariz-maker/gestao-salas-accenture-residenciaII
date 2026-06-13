import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.hashers import make_password
from workspace.models import (
    Sala, PostoDeTrabalho, PerfilProfissional,
    Usuario, Reserva, Equipe,
)


class PerfilProfissionalFactory(DjangoModelFactory):
    class Meta:
        model = PerfilProfissional

    nome = factory.Sequence(lambda n: f'Perfil {n}')
    descricao = factory.Faker('sentence', locale='pt_BR')
    tipos_recurso_necessarios = []


class UsuarioFactory(DjangoModelFactory):
    class Meta:
        model = Usuario

    username = factory.Sequence(lambda n: f'usuario{n}@growup.com')
    email = factory.LazyAttribute(lambda o: o.username)
    password = factory.LazyFunction(lambda: make_password('senha123'))
    tipo_perfil = 'PADRAO'
    departamento = 'Engenharia'
    perfil_profissional = factory.SubFactory(PerfilProfissionalFactory)


class AdminFactory(UsuarioFactory):
    tipo_perfil = 'ADMIN'


class SalaFactory(DjangoModelFactory):
    class Meta:
        model = Sala

    nome = factory.Sequence(lambda n: f'Sala {n}')
    localizacao = factory.Faker('street_address', locale='pt_BR')
    capacidade = factory.Faker('random_int', min=2, max=30)
    ativo = True
    status = 'LIVRE'


class PostoDeTrabalhoFactory(DjangoModelFactory):
    class Meta:
        model = PostoDeTrabalho

    sala = factory.SubFactory(SalaFactory)
    coord_x = factory.Faker('random_int', min=10, max=500)
    coord_y = factory.Faker('random_int', min=10, max=500)
    disponivel = True
    tem_maquina = True
    tipo = 'INDIVIDUAL'


class ReservaFactory(DjangoModelFactory):
    class Meta:
        model = Reserva

    usuario = factory.SubFactory(UsuarioFactory)
    posto = factory.SubFactory(PostoDeTrabalhoFactory)
    data_hora_inicio = factory.Faker('future_datetime', tzinfo=factory.LazyFunction(
        lambda: __import__('django.utils.timezone', fromlist=['utc']).utc
    ))
    data_hora_fim = factory.LazyAttribute(
        lambda o: o.data_hora_inicio + __import__('datetime').timedelta(hours=2)
    )
    status = 'CONFIRMADA'


class EquipeFactory(DjangoModelFactory):
    class Meta:
        model = Equipe

    nome = factory.Sequence(lambda n: f'Equipe {n}')
    descricao = factory.Faker('sentence', locale='pt_BR')