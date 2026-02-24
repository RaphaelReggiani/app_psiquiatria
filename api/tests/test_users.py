import pytest
from django.urls import reverse

from gmp.usuarios.models import CustomUser


@pytest.mark.django_db
class TestUserPermissions:

    def test_paciente_nao_pode_escalar_role(self, api_client, paciente):

        api_client.force_authenticate(user=paciente)

        url = reverse("users-detail", args=[paciente.id])

        response = api_client.patch(url, {"role": CustomUser.ROLE_PACIENTE})

        paciente.refresh_from_db()

        assert response.status_code == 200
        assert paciente.role == CustomUser.ROLE_PACIENTE

    def test_superadm_lista_todos_usuarios(self, api_client, superadm, paciente):

        api_client.force_authenticate(user=superadm)

        url = reverse("users-list")

        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) >= 2
