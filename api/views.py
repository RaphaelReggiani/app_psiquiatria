from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from gmp.usuarios.models import CustomUser
from gmp.consultas.models import Consulta, AgendamentoConsulta

from .serializers import (
    UserSerializer,
    ConsultaSerializer,
    AgendamentoConsultaSerializer
)

from .permissions import (
    IsUserOwnerOrSuperAdmin,
    IsAgendamentoOwnerOrSuperAdmin,
    IsConsultaOwnerOrSuperAdmin
)


class UserViewSet(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):

        if self.action == 'create':
            return [AllowAny()]

        if self.action in ['retrieve', 'update', 'partial_update']:
            return [IsUserOwnerOrSuperAdmin()]

        if self.action == 'list':
            return [IsAuthenticated()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):

        user = self.request.user

        if not user.is_authenticated:
            serializer.save(role='paciente')
            return

        if user.role == 'superadm':
            serializer.save()
            return

        raise PermissionDenied("Você não tem permissão para criar usuários.")

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return CustomUser.objects.none()

        if user.role == 'superadm':
            return CustomUser.objects.all()

        return CustomUser.objects.filter(id=user.id)


class ConsultaViewSet(viewsets.ModelViewSet):

    serializer_class = ConsultaSerializer
    permission_classes = [IsConsultaOwnerOrSuperAdmin]

    def get_queryset(self):

        user = self.request.user

        if user.role == 'superadm':
            return Consulta.objects.all()

        if user.role == 'medico':
            return Consulta.objects.filter(
                agendamento__medico=user
            )

        return Consulta.objects.filter(
            agendamento__paciente=user,
            agendamento__status='realizada'
        )

    def perform_create(self, serializer):

        user = self.request.user

        if user.role != 'medico':
            raise PermissionDenied("Apenas médicos podem registrar consultas.")

        agendamento = serializer.validated_data['agendamento']

        if agendamento.status != 'realizada':
            raise PermissionDenied(
                "Consulta só pode ser registrada para agendamento realizado."
            )

        if agendamento.medico != user:
            raise PermissionDenied(
                "Você não pode registrar consulta de outro médico."
            )

        serializer.save()


class AgendamentoConsultaViewSet(viewsets.ModelViewSet):

    serializer_class = AgendamentoConsultaSerializer
    permission_classes = [IsAgendamentoOwnerOrSuperAdmin]

    def get_queryset(self):

        user = self.request.user

        if user.role == 'superadm':
            return AgendamentoConsulta.objects.all()

        if user.role == 'medico':
            return AgendamentoConsulta.objects.filter(medico=user)

        return AgendamentoConsulta.objects.filter(paciente=user)

    def perform_create(self, serializer):

        user = self.request.user

        if user.role == 'medico':
            raise PermissionDenied("Médicos não podem marcar consultas.")

        if user.role == 'paciente':
            serializer.save(paciente=user)
            return

        if user.role == 'superadm':
            serializer.save()
            return

        raise PermissionDenied("Sem permissão.")

