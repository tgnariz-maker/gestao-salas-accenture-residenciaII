import pytest
from rest_framework.test import APIClient
from tests.factories import SalaFactory, UsuarioFactory, AdminFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def usuario(db):
    return UsuarioFactory()


@pytest.fixture
def admin(db):
    return AdminFactory()


@pytest.fixture
def api_client_autenticado(api_client, usuario):
    api_client.force_authenticate(user=usuario)
    return api_client


@pytest.fixture
def api_client_admin(api_client, admin):
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def sala(db):
    return SalaFactory()


@pytest.fixture
def tres_salas(db):
    return SalaFactory.create_batch(3)