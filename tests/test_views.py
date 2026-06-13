import pytest
from datetime import timedelta, date
from django.utils import timezone

from workspace.models import Sala, Reserva, PostoDeTrabalho, PerfilProfissional, Equipe
from tests.factories import (
    SalaFactory, PostoDeTrabalhoFactory, ReservaFactory,
    UsuarioFactory, AdminFactory, PerfilProfissionalFactory, EquipeFactory,
)


@pytest.mark.django_db
class TestSalaListCreate:
    url = '/api/v1/salas/'

    def test_listar_salas_sem_autenticacao_retorna_401(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 401

    def test_listar_salas_autenticado_retorna_200(self, api_client_autenticado, tres_salas):
        response = api_client_autenticado.get(self.url)
        assert response.status_code == 200

    def test_listar_retorna_apenas_salas_ativas(self, api_client_autenticado):
        SalaFactory.create_batch(3, ativo=True)
        SalaFactory.create_batch(2, ativo=False)
        response = api_client_autenticado.get(self.url)
        assert len(response.data) == 3

    def test_criar_sala_sem_autenticacao_retorna_401(self, api_client):
        payload = {'nome': 'Nova Sala', 'localizacao': 'Andar 2', 'capacidade': 10}
        response = api_client.post(self.url, payload)
        assert response.status_code == 401

    def test_criar_sala_usuario_padrao_retorna_403(self, api_client_autenticado):
        payload = {'nome': 'Nova Sala', 'localizacao': 'Andar 2', 'capacidade': 10}
        response = api_client_autenticado.post(self.url, payload)
        assert response.status_code == 403

    def test_criar_sala_admin_retorna_201(self, api_client_admin):
        payload = {'nome': 'Nova Sala', 'localizacao': 'Andar 2', 'capacidade': 10}
        response = api_client_admin.post(self.url, payload)
        assert response.status_code == 201
        assert response.data['nome'] == 'Nova Sala'

    def test_criar_sala_salva_no_banco(self, api_client_admin):
        payload = {'nome': 'Sala Persistida', 'localizacao': 'Andar 1', 'capacidade': 5}
        api_client_admin.post(self.url, payload)
        assert Sala.objects.filter(nome='Sala Persistida').exists()

    def test_criar_sala_sem_nome_retorna_400(self, api_client_admin):
        payload = {'localizacao': 'Andar 1', 'capacidade': 5}
        response = api_client_admin.post(self.url, payload)
        assert response.status_code == 400

    def test_criar_sala_capacidade_zero_retorna_400(self, api_client_admin):
        payload = {'nome': 'Sala X', 'localizacao': 'Andar 1', 'capacidade': 0}
        response = api_client_admin.post(self.url, payload)
        assert response.status_code == 400

    def test_criar_sala_capacidade_negativa_retorna_400(self, api_client_admin):
        payload = {'nome': 'Sala X', 'localizacao': 'Andar 1', 'capacidade': -1}
        response = api_client_admin.post(self.url, payload)
        assert response.status_code == 400


@pytest.mark.django_db
class TestSalaDelete:

    def test_deletar_sala_admin_aplica_soft_delete(self, api_client_admin, sala):
        url = f'/api/v1/salas/{sala.pk}/'
        response = api_client_admin.delete(url)
        assert response.status_code == 204
        sala.refresh_from_db()
        assert sala.ativo is False

    def test_deletar_sala_nao_aparece_na_listagem(self, api_client_admin, sala):
        url = f'/api/v1/salas/{sala.pk}/'
        api_client_admin.delete(url)
        response = api_client_admin.get('/api/v1/salas/')
        ids = [s['id'] for s in response.data]
        assert sala.pk not in ids

    def test_deletar_sala_usuario_padrao_retorna_403(self, api_client_autenticado, sala):
        url = f'/api/v1/salas/{sala.pk}/'
        response = api_client_autenticado.delete(url)
        assert response.status_code == 403

    def test_deletar_sala_com_reserva_ativa_retorna_400(self, api_client_admin):
        sala = SalaFactory()
        posto = PostoDeTrabalhoFactory(sala=sala)
        ReservaFactory(
            posto=posto,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        url = f'/api/v1/salas/{sala.pk}/'
        response = api_client_admin.delete(url)
        assert response.status_code == 400


@pytest.mark.django_db
class TestReservas:
    url = '/api/v1/reservas/'

    def test_criar_reserva_sem_autenticacao_retorna_401(self, api_client):
        response = api_client.post(self.url, {})
        assert response.status_code == 401

    def test_criar_reserva_valida_retorna_201(self, api_client_autenticado, usuario):
        posto = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=2)
        payload = {
            'posto': posto.pk,
            'data_hora_inicio': inicio.isoformat(),
            'data_hora_fim': fim.isoformat(),
        }
        response = api_client_autenticado.post(self.url, payload)
        assert response.status_code == 201

    def test_criar_reserva_posto_indisponivel_retorna_400(self, api_client_autenticado):
        posto = PostoDeTrabalhoFactory(disponivel=False)
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=2)
        payload = {
            'posto': posto.pk,
            'data_hora_inicio': inicio.isoformat(),
            'data_hora_fim': fim.isoformat(),
        }
        response = api_client_autenticado.post(self.url, payload)
        assert response.status_code == 400

    def test_criar_reserva_sem_antecedencia_retorna_400(self, api_client_autenticado):
        posto = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(minutes=10)
        fim = inicio + timedelta(hours=1)
        payload = {
            'posto': posto.pk,
            'data_hora_inicio': inicio.isoformat(),
            'data_hora_fim': fim.isoformat(),
        }
        response = api_client_autenticado.post(self.url, payload)
        assert response.status_code == 400

    def test_listar_reservas_autenticado_retorna_200(self, api_client_autenticado):
        response = api_client_autenticado.get(self.url)
        assert response.status_code == 200

    def test_cancelar_reserva_propria_retorna_204(self, api_client_autenticado, usuario):
        reserva = ReservaFactory(
            usuario=usuario,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        url = f'/api/v1/reservas/{reserva.pk}/'
        response = api_client_autenticado.delete(url)
        assert response.status_code == 204

    def test_cancelar_reserva_de_outro_usuario_retorna_403(self, api_client_autenticado):
        outro_usuario = UsuarioFactory()
        reserva = ReservaFactory(
            usuario=outro_usuario,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        url = f'/api/v1/reservas/{reserva.pk}/'
        response = api_client_autenticado.delete(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestPerfis:
    url = '/api/v1/perfis/'

    def test_listar_perfis_autenticado_retorna_200(self, api_client_autenticado):
        response = api_client_autenticado.get(self.url)
        assert response.status_code == 200

    def test_criar_perfil_admin_retorna_201(self, api_client_admin):
        payload = {'nome': 'Desenvolvedor', 'descricao': 'Dev backend', 'tipos_recurso_necessarios': ['COMPUTADOR']}
        response = api_client_admin.post(self.url, payload, format='json')
        assert response.status_code == 201

    def test_criar_perfil_usuario_padrao_retorna_403(self, api_client_autenticado):
        payload = {'nome': 'Designer', 'descricao': 'UX', 'tipos_recurso_necessarios': []}
        response = api_client_autenticado.post(self.url, payload, format='json')
        assert response.status_code == 403

    def test_deletar_perfil_sem_usuarios_retorna_204(self, api_client_admin):
        perfil = PerfilProfissionalFactory()
        url = f'/api/v1/perfis/{perfil.pk}/'
        response = api_client_admin.delete(url)
        assert response.status_code == 204

    def test_deletar_perfil_com_usuario_vinculado_retorna_400(self, api_client_admin):
        perfil = PerfilProfissionalFactory()
        UsuarioFactory(perfil_profissional=perfil)
        url = f'/api/v1/perfis/{perfil.pk}/'
        response = api_client_admin.delete(url)
        assert response.status_code == 400


@pytest.mark.django_db
class TestUsuarios:

    def test_me_autenticado_retorna_200(self, api_client_autenticado):
        response = api_client_autenticado.get('/api/v1/usuarios/me/')
        assert response.status_code == 200

    def test_me_sem_autenticacao_retorna_401(self, api_client):
        response = api_client.get('/api/v1/usuarios/me/')
        assert response.status_code == 401

    def test_listar_usuarios_admin_retorna_200(self, api_client_admin):
        response = api_client_admin.get('/api/v1/usuarios/')
        assert response.status_code == 200

    def test_listar_usuarios_padrao_retorna_403(self, api_client_autenticado):
        response = api_client_autenticado.get('/api/v1/usuarios/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestEquipes:
    url = '/api/v1/equipes/'

    def test_listar_equipes_autenticado_retorna_200(self, api_client_autenticado):
        response = api_client_autenticado.get(self.url)
        assert response.status_code == 200

    def test_criar_equipe_admin_retorna_201(self, api_client_admin):
        payload = {'nome': 'Equipe Alpha', 'descricao': 'Descricao', 'membros_ids': []}
        response = api_client_admin.post(self.url, payload, format='json')
        assert response.status_code == 201

    def test_criar_equipe_usuario_padrao_retorna_403(self, api_client_autenticado):
        payload = {'nome': 'Equipe Beta', 'descricao': 'Descricao', 'membros_ids': []}
        response = api_client_autenticado.post(self.url, payload, format='json')
        assert response.status_code == 403

    def test_deletar_equipe_admin_retorna_204(self, api_client_admin):
        equipe = EquipeFactory()
        url = f'/api/v1/equipes/{equipe.pk}/'
        response = api_client_admin.delete(url)
        assert response.status_code == 204

    def test_criar_equipe_com_membros(self, api_client_admin):
        usuario = UsuarioFactory()
        payload = {'nome': 'Equipe Gamma', 'descricao': 'Desc', 'membros_ids': [usuario.pk]}
        response = api_client_admin.post(self.url, payload, format='json')
        assert response.status_code == 201
        equipe = Equipe.objects.get(pk=response.data['id'])
        assert usuario in equipe.membros.all()


@pytest.mark.django_db
class TestPosicoes:

    def test_listar_posicoes_de_sala_retorna_200(self, api_client_autenticado):
        sala = SalaFactory()
        PostoDeTrabalhoFactory.create_batch(3, sala=sala)
        url = f'/api/v1/salas/{sala.pk}/posicoes/'
        response = api_client_autenticado.get(url)
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_sugestoes_por_perfil_retorna_200(self, api_client_autenticado):
        PostoDeTrabalhoFactory.create_batch(3)
        response = api_client_autenticado.get('/api/v1/posicoes/sugestoes/')
        assert response.status_code == 200

    def test_sugestoes_por_equipe_sem_equipe_id_retorna_400(self, api_client_autenticado):
        response = api_client_autenticado.get('/api/v1/posicoes/sugestoes/equipe/')
        assert response.status_code == 400

    def test_sugestoes_por_equipe_com_equipe_id_retorna_200(self, api_client_autenticado):
        equipe = EquipeFactory()
        PostoDeTrabalhoFactory.create_batch(3)
        url = f'/api/v1/posicoes/sugestoes/equipe/?equipe_id={equipe.pk}'
        response = api_client_autenticado.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestHealth:

    def test_health_retorna_200(self, api_client):
        response = api_client.get('/api/v1/health/')
        assert response.status_code == 200
        assert response.data['status'] == 'ok'