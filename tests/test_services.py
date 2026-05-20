import pytest
from django.core.exceptions import ValidationError

from workspace.models import Sala
from tests.factories import SalaFactory


@pytest.mark.django_db
class TestSalaModel:

    def test_cria_sala_com_dados_validos(self):
        sala = SalaFactory()
        assert sala.pk is not None
        assert sala.nome != ''
        assert sala.capacidade >= 2

    def test_str_retorna_nome_da_sala(self):
        sala = SalaFactory(nome='Sala de Reunião')
        assert str(sala) == 'Sala de Reunião'

    def test_capacidade_minima_e_1(self):
        sala = SalaFactory.build(capacidade=0)
        with pytest.raises(ValidationError):
            sala.full_clean()

    def test_capacidade_negativa_invalida(self):
        sala = SalaFactory.build(capacidade=-5)
        with pytest.raises(ValidationError):
            sala.full_clean()

    def test_capacidade_1_e_valida(self):
        sala = SalaFactory(capacidade=1)
        sala.full_clean()  # não deve lançar erro

    def test_nome_max_length(self):
        sala = SalaFactory.build(nome='A' * 101)
        with pytest.raises(ValidationError):
            sala.full_clean()

    def test_localizacao_max_length(self):
        sala = SalaFactory.build(localizacao='A' * 101)
        with pytest.raises(ValidationError):
            sala.full_clean()

    def test_factory_cria_salas_com_nomes_unicos(self):
        sala1 = SalaFactory()
        sala2 = SalaFactory()
        assert sala1.nome != sala2.nome

    def test_create_batch_cria_quantidade_correta(self, db):
        SalaFactory.create_batch(5)
        assert Sala.objects.count() == 5