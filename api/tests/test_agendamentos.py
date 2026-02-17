import pytest
from django.urls import reverse
from gmp.consultas.models import AgendamentoConsulta
from django.utils import timezone
import datetime


@pytest.mark.django_db
class TestAgendamento:

    def test_paciente_cria_agendamento(self, api_client, paciente, medico):

        api_client.force_authenticate(user=paciente)

        url = reverse("agendamentos-list")

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        response = api_client.post(url, {
            "medico": medico.id,
            "data_hora": data_hora.isoformat(),
        })

        assert response.status_code == 201
        assert AgendamentoConsulta.objects.count() == 1

        agendamento = AgendamentoConsulta.objects.first()
        assert agendamento.paciente == paciente
        assert agendamento.medico == medico
        assert agendamento.status is not None

    def test_medico_nao_pode_criar_agendamento(self, api_client, medico):

        api_client.force_authenticate(user=medico)

        url = reverse("agendamentos-list")

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        response = api_client.post(url, {
            "medico": medico.id,
            "data_hora": data_hora.isoformat(),
        })

        assert response.status_code == 403
        assert AgendamentoConsulta.objects.count() == 0

    def test_paciente_nao_ve_agendamento_de_outro(
        self, api_client, paciente, paciente2, medico
    ):

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        AgendamentoConsulta.objects.create(
            paciente=paciente2,
            medico=medico,
            data_hora=data_hora,
            status="marcada"
        )

        api_client.force_authenticate(user=paciente)

        url = reverse("agendamentos-list")

        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 0

