from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from gmp.usuarios.models import CustomUser
from gmp.usuarios.services import UserService
from gmp.usuarios.exceptions import UserDomainException
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

    def perform_update(self, serializer):
        try:
            UserService.update_user(
                instance=self.get_object(),
                data=serializer.validated_data,
                request_user=self.request.user
            )
        except UserDomainException as e:
            raise ValidationError(str(e))

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return CustomUser.objects.none()

        if user.role == CustomUser.ROLE_SUPERADM:
            return CustomUser.objects.all()

        return CustomUser.objects.filter(id=user.id)


class ConsultaViewSet(viewsets.ModelViewSet):

    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [IsConsultaOwnerOrSuperAdmin]

    def get_queryset(self):

        user = self.request.user

        if user.role == CustomUser.ROLE_SUPERADM:
            return Consulta.objects.all()

        if user.role == CustomUser.ROLE_MEDICO:
            return Consulta.objects.filter(
                agendamento__medico=user
            )

        return Consulta.objects.filter(
            agendamento__paciente=user,
            agendamento__status='realizada'
        )

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        raise ValidationError("Consulta não pode ser editada após criação.")

    def partial_update(self, request, *args, **kwargs):
        raise ValidationError("Consulta não pode ser editada após criação.")


class AgendamentoConsultaViewSet(viewsets.ModelViewSet):

    serializer_class = AgendamentoConsultaSerializer
    permission_classes = [IsAgendamentoOwnerOrSuperAdmin]

    def get_queryset(self):

        user = self.request.user

        if user.role == CustomUser.ROLE_SUPERADM:
            return AgendamentoConsulta.objects.all()

        if user.role == CustomUser.ROLE_MEDICO:
            return AgendamentoConsulta.objects.filter(medico=user)

        return AgendamentoConsulta.objects.filter(paciente=user)

    def perform_create(self, serializer):

        user = self.request.user

        if user.role == CustomUser.ROLE_MEDICO:
            raise PermissionDenied("Médicos não podem marcar consultas.")

        if user.role == CustomUser.ROLE_PACIENTE:
            serializer.save(paciente=user)
            return

        if user.role == CustomUser.ROLE_SUPERADM:
            serializer.save()
            return

        raise PermissionDenied("Sem permissão.")

