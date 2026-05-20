import pytest
from rest_framework.test import APIClient

from tests.factories import SalaFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sala(db):
    return SalaFactory()


@pytest.fixture
def tres_salas(db):
    return SalaFactory.create_batch(3)