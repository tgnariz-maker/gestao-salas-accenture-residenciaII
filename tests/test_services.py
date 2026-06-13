import pytest
from datetime import timedelta, date
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from workspace.models import Sala, PostoDeTrabalho, Reserva, PerfilProfissional, Equipe
from workspace import services
from tests.factories import (
    SalaFactory, PostoDeTrabalhoFactory, ReservaFactory,
    UsuarioFactory, AdminFactory, PerfilProfissionalFactory, EquipeFactory,
)


@pytest.mark.django_db
class TestSalaModel:

    def test_cria_sala_com_dados_validos(self):
        sala = SalaFactory()
        assert sala.pk is not None
        assert sala.nome != ''
        assert sala.capacidade >= 2

    def test_str_retorna_nome_da_sala(self):
        sala = SalaFactory(nome='Sala de Reuniao')
        assert str(sala) == 'Sala de Reuniao'

    def test_capacidade_minima_e_1(self):
        from django.core.exceptions import ValidationError as DjangoValidationError
        sala = SalaFactory.build(capacidade=0)
        with pytest.raises(DjangoValidationError):
            sala.full_clean()

    def test_capacidade_negativa_invalida(self):
        from django.core.exceptions import ValidationError as DjangoValidationError
        sala = SalaFactory.build(capacidade=-5)
        with pytest.raises(DjangoValidationError):
            sala.full_clean()

    def test_capacidade_1_e_valida(self):
        sala = SalaFactory(capacidade=1)
        sala.full_clean()

    def test_nome_max_length(self):
        from django.core.exceptions import ValidationError as DjangoValidationError
        sala = SalaFactory.build(nome='A' * 101)
        with pytest.raises(DjangoValidationError):
            sala.full_clean()

    def test_localizacao_max_length(self):
        from django.core.exceptions import ValidationError as DjangoValidationError
        sala = SalaFactory.build(localizacao='A' * 101)
        with pytest.raises(DjangoValidationError):
            sala.full_clean()

    def test_factory_cria_salas_com_nomes_unicos(self):
        sala1 = SalaFactory()
        sala2 = SalaFactory()
        assert sala1.nome != sala2.nome

    def test_create_batch_cria_quantidade_correta(self):
        SalaFactory.create_batch(5)
        assert Sala.objects.count() == 5

    def test_sala_criada_com_ativo_true_por_padrao(self):
        sala = SalaFactory()
        assert sala.ativo is True

    def test_soft_delete_nao_exclui_fisicamente(self):
        sala = SalaFactory()
        sala_id = sala.pk
        sala.ativo = False
        sala.save(update_fields=['ativo'])
        assert Sala.objects.filter(pk=sala_id).exists()
        assert not Sala.objects.filter(pk=sala_id, ativo=True).exists()


@pytest.mark.django_db
class TestDeletarSala:

    def test_deletar_sala_sem_reservas_aplica_soft_delete(self):
        sala = SalaFactory()
        services.deletar_sala(sala)
        sala.refresh_from_db()
        assert sala.ativo is False

    def test_deletar_sala_com_reserva_ativa_levanta_erro(self):
        sala = SalaFactory()
        posto = PostoDeTrabalhoFactory(sala=sala)
        ReservaFactory(
            posto=posto,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        with pytest.raises(ValidationError):
            services.deletar_sala(sala)

    def test_deletar_sala_com_reserva_cancelada_permite_soft_delete(self):
        sala = SalaFactory()
        posto = PostoDeTrabalhoFactory(sala=sala)
        ReservaFactory(
            posto=posto,
            status='CANCELADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        services.deletar_sala(sala)
        sala.refresh_from_db()
        assert sala.ativo is False


@pytest.mark.django_db
class TestCriarSala:

    def test_criar_sala_manutencao_sem_motivo_levanta_erro(self):
        with pytest.raises(ValidationError):
            services.criar_sala({
                'nome': 'Sala X',
                'localizacao': 'Andar 1',
                'capacidade': 10,
                'status': 'MANUTENCAO',
                'prazo_estimado': date.today(),
            })

    def test_criar_sala_manutencao_sem_prazo_levanta_erro(self):
        with pytest.raises(ValidationError):
            services.criar_sala({
                'nome': 'Sala X',
                'localizacao': 'Andar 1',
                'capacidade': 10,
                'status': 'MANUTENCAO',
                'motivo_manutencao': 'Reforma',
            })

    def test_criar_sala_manutencao_com_dados_completos(self):
        sala = services.criar_sala({
            'nome': 'Sala Manutencao',
            'localizacao': 'Andar 1',
            'capacidade': 10,
            'status': 'MANUTENCAO',
            'motivo_manutencao': 'Reforma eletrica',
            'prazo_estimado': date.today(),
        })
        assert sala.pk is not None
        assert sala.status == 'MANUTENCAO'


@pytest.mark.django_db
class TestCriarReserva:

    def test_reserva_usuario_sem_perfil_levanta_erro(self):
        usuario = UsuarioFactory(perfil_profissional=None)
        posto = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=1)
        with pytest.raises(ValidationError):
            services.criar_reserva(usuario, {'posto': posto, 'data_hora_inicio': inicio, 'data_hora_fim': fim})

    def test_reserva_posto_indisponivel_levanta_erro(self):
        usuario = UsuarioFactory()
        posto = PostoDeTrabalhoFactory(disponivel=False)
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=1)
        with pytest.raises(ValidationError):
            services.criar_reserva(usuario, {'posto': posto, 'data_hora_inicio': inicio, 'data_hora_fim': fim})

    def test_reserva_sala_manutencao_levanta_erro(self):
        usuario = UsuarioFactory()
        sala = SalaFactory(status='MANUTENCAO', motivo_manutencao='Reforma', prazo_estimado=date.today())
        posto = PostoDeTrabalhoFactory(sala=sala)
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=1)
        with pytest.raises(ValidationError):
            services.criar_reserva(usuario, {'posto': posto, 'data_hora_inicio': inicio, 'data_hora_fim': fim})

    def test_reserva_sem_antecedencia_minima_levanta_erro(self):
        usuario = UsuarioFactory()
        posto = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(minutes=10)
        fim = inicio + timedelta(hours=1)
        with pytest.raises(ValidationError):
            services.criar_reserva(usuario, {'posto': posto, 'data_hora_inicio': inicio, 'data_hora_fim': fim})

    def test_reserva_conflito_de_horario_levanta_erro(self):
        usuario1 = UsuarioFactory()
        usuario2 = UsuarioFactory()
        posto = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=2)
        ReservaFactory(usuario=usuario1, posto=posto, data_hora_inicio=inicio, data_hora_fim=fim, status='CONFIRMADA')
        with pytest.raises(ValidationError):
            services.criar_reserva(usuario2, {'posto': posto, 'data_hora_inicio': inicio, 'data_hora_fim': fim})

    def test_reserva_dupla_mesmo_usuario_levanta_erro(self):
        usuario = UsuarioFactory()
        posto1 = PostoDeTrabalhoFactory()
        posto2 = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=2)
        ReservaFactory(usuario=usuario, posto=posto1, data_hora_inicio=inicio, data_hora_fim=fim, status='CONFIRMADA')
        with pytest.raises(ValidationError):
            services.criar_reserva(usuario, {'posto': posto2, 'data_hora_inicio': inicio, 'data_hora_fim': fim})

    def test_reserva_valida_cria_com_status_confirmada(self):
        usuario = UsuarioFactory()
        posto = PostoDeTrabalhoFactory()
        inicio = timezone.now() + timedelta(hours=2)
        fim = inicio + timedelta(hours=2)
        reserva = services.criar_reserva(usuario, {'posto': posto, 'data_hora_inicio': inicio, 'data_hora_fim': fim})
        assert reserva.pk is not None
        assert reserva.status == 'CONFIRMADA'


@pytest.mark.django_db
class TestCancelarReserva:

    def test_cancelar_reserva_propria(self):
        usuario = UsuarioFactory()
        reserva = ReservaFactory(
            usuario=usuario,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        services.cancelar_reserva(reserva, usuario)
        reserva.refresh_from_db()
        assert reserva.status == 'CANCELADA'

    def test_cancelar_reserva_de_outro_usuario_levanta_erro(self):
        usuario1 = UsuarioFactory()
        usuario2 = UsuarioFactory()
        reserva = ReservaFactory(
            usuario=usuario1,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        with pytest.raises(PermissionDenied):
            services.cancelar_reserva(reserva, usuario2)

    def test_cancelar_reserva_ja_cancelada_levanta_erro(self):
        usuario = UsuarioFactory()
        reserva = ReservaFactory(
            usuario=usuario,
            status='CANCELADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        with pytest.raises(ValidationError):
            services.cancelar_reserva(reserva, usuario)

    def test_cancelar_reserva_ja_iniciada_levanta_erro(self):
        usuario = UsuarioFactory()
        reserva = ReservaFactory(
            usuario=usuario,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() - timedelta(hours=1),
            data_hora_fim=timezone.now() + timedelta(hours=1),
        )
        with pytest.raises(ValidationError):
            services.cancelar_reserva(reserva, usuario)

    def test_admin_pode_cancelar_reserva_de_outro_usuario(self):
        admin = AdminFactory()
        usuario = UsuarioFactory()
        reserva = ReservaFactory(
            usuario=usuario,
            status='CONFIRMADA',
            data_hora_inicio=timezone.now() + timedelta(hours=2),
            data_hora_fim=timezone.now() + timedelta(hours=3),
        )
        services.cancelar_reserva(reserva, admin)
        reserva.refresh_from_db()
        assert reserva.status == 'CANCELADA'


@pytest.mark.django_db
class TestDeletarPerfilProfissional:

    def test_deletar_perfil_sem_usuarios_vinculados(self):
        perfil = PerfilProfissionalFactory()
        services.deletar_perfil_profissional(perfil)
        assert not PerfilProfissional.objects.filter(pk=perfil.pk).exists()

    def test_deletar_perfil_com_usuario_vinculado_levanta_erro(self):
        perfil = PerfilProfissionalFactory()
        UsuarioFactory(perfil_profissional=perfil)
        with pytest.raises(ValidationError):
            services.deletar_perfil_profissional(perfil)


@pytest.mark.django_db
class TestEquipe:

    def test_criar_equipe(self):
        equipe = services.criar_equipe({'nome': 'Equipe Alpha', 'descricao': 'Descricao'})
        assert equipe.pk is not None
        assert equipe.nome == 'Equipe Alpha'

    def test_criar_equipe_com_membros(self):
        usuario = UsuarioFactory()
        equipe = services.criar_equipe({'nome': 'Equipe Beta', 'membros_ids': [usuario.pk]})
        assert usuario in equipe.membros.all()

    def test_atualizar_equipe_adiciona_membro(self):
        equipe = EquipeFactory()
        usuario = UsuarioFactory()
        services.atualizar_equipe(equipe, {'membros_ids': [usuario.pk]})
        assert usuario in equipe.membros.all()