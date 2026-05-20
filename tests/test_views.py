import pytest
from workspace.models import Sala
from tests.factories import SalaFactory


@pytest.mark.django_db
class TestSalaListCreate:
    url = '/api/salas/'

    def test_listar_salas_retorna_200(self, api_client, tres_salas):
        response = api_client.get(self.url)
        assert response.status_code == 200

    def test_listar_retorna_todas_as_salas(self, api_client, tres_salas):
        response = api_client.get(self.url)
        assert len(response.data) == 3

    def test_criar_sala_valida_retorna_201(self, api_client, db):
        payload = {
            'nome': 'Nova Sala',
            'localizacao': 'Andar 2',
            'capacidade': 10,
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == 201
        assert response.data['nome'] == 'Nova Sala'

    def test_criar_sala_salva_no_banco(self, api_client, db):
        payload = {
            'nome': 'Sala Persistida',
            'localizacao': 'Andar 1',
            'capacidade': 5,
        }
        api_client.post(self.url, payload)
        assert Sala.objects.filter(nome='Sala Persistida').exists()

    def test_criar_sala_sem_nome_retorna_400(self, api_client, db):
        payload = {'localizacao': 'Andar 1', 'capacidade': 5}
        response = api_client.post(self.url, payload)
        assert response.status_code == 400

    def test_criar_sala_capacidade_zero_retorna_400(self, api_client, db):
        payload = {'nome': 'Sala X', 'localizacao': 'Andar 1', 'capacidade': 0}
        response = api_client.post(self.url, payload)
        assert response.status_code == 400

    def test_criar_sala_capacidade_negativa_retorna_400(self, api_client, db):
        payload = {'nome': 'Sala X', 'localizacao': 'Andar 1', 'capacidade': -1}
        response = api_client.post(self.url, payload)
        assert response.status_code == 400