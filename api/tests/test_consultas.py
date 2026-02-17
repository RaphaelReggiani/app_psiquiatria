import pytest
from django.urls import reverse
from gmp.consultas.models import Consulta, AgendamentoConsulta
from django.utils import timezone
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestConsulta:

    def test_medico_cria_consulta(self, api_client, medico, paciente):

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            name="receita.pdf",
            content=b"%PDF-1.4 fake pdf content",
            content_type="application/pdf",
        )

        api_client.force_authenticate(user=medico)

        url = reverse("consultas-list")

        response = api_client.post(
            url,
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Consulta teste",
                "receita": receita_pdf,
            },
            format="multipart",
        )

        assert response.status_code == 201
        assert Consulta.objects.count() == 1

        consulta = Consulta.objects.first()
        assert consulta.agendamento == agendamento
        assert consulta.descricao == "Consulta teste"


    def test_paciente_nao_pode_criar_consulta(self, api_client, paciente):

        api_client.force_authenticate(user=paciente)

        url = reverse("consultas-list")

        response = api_client.post(url, {
            "agendamento": 1,
            "condicao_paciente": "Instável",
            "descricao": "Tentativa inválida",
            "receita": "Nenhuma",
        })

        assert response.status_code == 400
        assert Consulta.objects.count() == 0

    def test_medico_nao_pode_criar_consulta_nao_realizada(
        self, api_client, medico, paciente
    ):

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="marcada",
        )

        api_client.force_authenticate(user=medico)

        url = reverse("consultas-list")

        response = api_client.post(url, {
            "agendamento": agendamento.id,
            "condicao_paciente": "Estável",
            "descricao": "Erro esperado",
            "receita": "Nenhuma",
        })

        assert response.status_code == 400
        assert Consulta.objects.count() == 0

    def test_medico_nao_pode_criar_consulta_de_outro_medico(
        self, api_client, medico, paciente, django_user_model
    ):
        outro_medico = django_user_model.objects.create_user(
            email="outro_medico@test.com",
            password="123456",
            role="medico",
        )

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=outro_medico,
            data_hora=data_hora,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        api_client.force_authenticate(user=medico)

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Tentativa inválida",
                "receita": receita_pdf,
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert Consulta.objects.count() == 0

    def test_nao_pode_criar_duas_consultas_para_mesmo_agendamento(
        self, api_client, medico, paciente
    ):
        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        Consulta.objects.create(
            agendamento=agendamento,
            condicao_paciente="estavel",
            descricao="Primeira",
            receita=receita_pdf,
        )

        api_client.force_authenticate(user=medico)

        nova_receita = SimpleUploadedFile(
            "receita2.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Segunda tentativa",
                "receita": nova_receita,
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert Consulta.objects.count() == 1

    def test_nao_pode_criar_consulta_para_agendamento_no_passado(
        self, api_client, medico, paciente
    ):
        data_passada = timezone.make_aware(
            datetime.datetime(2020, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_passada,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        api_client.force_authenticate(user=medico)

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Consulta inválida",
                "receita": receita_pdf,
            },
            format="multipart",
        )

        assert response.status_code == 400

    def test_upload_invalido_nao_pdf(
        self, api_client, medico, paciente
    ):
        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        arquivo_txt = SimpleUploadedFile(
            "receita.txt",
            b"conteudo invalido",
            content_type="text/plain",
        )

        api_client.force_authenticate(user=medico)

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Upload inválido",
                "receita": arquivo_txt,
            },
            format="multipart",
        )

        assert response.status_code == 400

    def test_usuario_nao_autenticado_nao_pode_criar_consulta(
        self, api_client, medico, paciente
    ):
        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Sem login",
                "receita": receita_pdf,
            },
            format="multipart",
        )

        assert response.status_code in [401, 403]

    def test_nao_pode_criar_consulta_para_agendamento_cancelado(
        self, api_client, medico, paciente
    ):
        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="cancelada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        api_client.force_authenticate(user=medico)

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Erro esperado",
                "receita": receita_pdf,
            },
            format="multipart",
        )

        assert response.status_code == 400

    def test_consulta_nao_pode_ser_editada(
        self, api_client, medico, paciente
    ):
        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        consulta = Consulta.objects.create(
            agendamento=agendamento,
            condicao_paciente="estavel",
            descricao="Original",
            receita=receita_pdf,
        )

        api_client.force_authenticate(user=medico)

        response = api_client.patch(
            reverse("consultas-detail", args=[consulta.id]),
            {"descricao": "Alterado"},
        )

        assert response.status_code == 400

    def test_paciente_nao_ve_consulta_de_outro(
        self, api_client, medico, paciente, django_user_model
    ):
        outro_paciente = django_user_model.objects.create_user(
            email="outro@test.com",
            password="123456",
            role="paciente",
        )

        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=outro_paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        receita_pdf = SimpleUploadedFile(
            "receita.pdf",
            b"%PDF-1.4 teste",
            content_type="application/pdf",
        )

        Consulta.objects.create(
            agendamento=agendamento,
            condicao_paciente="estavel",
            descricao="Privada",
            receita=receita_pdf,
        )

        api_client.force_authenticate(user=paciente)

        response = api_client.get(reverse("consultas-list"))

        assert response.status_code == 200
        assert len(response.data) == 0

    def test_upload_maior_que_limite(
        self, api_client, medico, paciente
    ):
        data_hora = timezone.make_aware(
            datetime.datetime(2030, 1, 1, 10, 0, 0)
        )

        agendamento = AgendamentoConsulta.objects.create(
            paciente=paciente,
            medico=medico,
            data_hora=data_hora,
            status="realizada",
        )

        arquivo_grande = SimpleUploadedFile(
            "receita.pdf",
            b"x" * (6 * 1024 * 1024),  # 6MB
            content_type="application/pdf",
        )

        api_client.force_authenticate(user=medico)

        response = api_client.post(
            reverse("consultas-list"),
            {
                "agendamento": agendamento.id,
                "condicao_paciente": "estavel",
                "descricao": "Grande",
                "receita": arquivo_grande,
            },
            format="multipart",
        )

        assert response.status_code == 400






