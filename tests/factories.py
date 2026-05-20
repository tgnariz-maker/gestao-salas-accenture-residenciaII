import factory
from factory.django import DjangoModelFactory

from workspace.models import Sala


class SalaFactory(DjangoModelFactory):
    class Meta:
        model = Sala

    nome = factory.Sequence(lambda n: f'Sala {n}')
    localizacao = factory.Faker('street_address', locale='pt_BR')
    capacidade = factory.Faker('random_int', min=2, max=30)