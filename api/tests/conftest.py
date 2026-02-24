import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from gmp.consultas.models import AgendamentoConsulta

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def superadm(db):
    return User.objects.create_user(
        email="super@test.com", password="123456", role="superadm"
    )


@pytest.fixture
def medico(db):
    return User.objects.create_user(
        email="medico@test.com", password="123456", role="medico"
    )


@pytest.fixture
def paciente(db):
    return User.objects.create_user(
        email="paciente@test.com", password="123456", role="paciente"
    )


@pytest.fixture
def paciente2(db):
    return User.objects.create_user(
        email="paciente2@test.com", password="123456", role="paciente"
    )


@pytest.fixture
def agendamento_realizado(db, paciente, medico):
    return AgendamentoConsulta.objects.create(
        paciente=paciente,
        medico=medico,
        data_hora=timezone.make_aware(datetime.datetime(2030, 1, 1, 10, 0, 0)),
        status="realizada",
    )
