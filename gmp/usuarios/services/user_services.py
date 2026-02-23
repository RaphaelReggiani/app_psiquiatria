from django.contrib.auth import authenticate
from ..models import CustomUser
from ..exceptions import (
    InvalidRoleAssignment,
    UnauthorizedRoleChange,
    AuthenticationFailed,
    EmailAlreadyExists,
)

from gmp.usuarios.constants import (
    MSG_ERRO_USUARIO_JA_EXISTE,
    MSG_INVALID_ROLE_ASSIGNMENT_MEDICO,
    MSG_INVALID_ROLE_ASSIGNMENT_NOT_SUPERADM,
    MSG_INVALID_ROLE_ASSIGNMENT_PERFIL,
    MSG_AUTHENTICATION_FAILED_CREDENCIAIS,
    MSG_AUTHENTICATION_FAILED_EMAIL_SENHA,
    MSG_AUTHENTICATION_FAILED_CONTA_INATIVA,
)

class UserService:

    @staticmethod
    def create_user(data, request_user=None):

        role = data.get("role", CustomUser.ROLE_PACIENTE)

        if not request_user or not request_user.is_authenticated:
            role = CustomUser.ROLE_PACIENTE

        elif request_user.role == CustomUser.ROLE_MEDICO:
            if role != CustomUser.ROLE_PACIENTE:
                raise InvalidRoleAssignment(MSG_INVALID_ROLE_ASSIGNMENT_MEDICO)

        elif request_user.role != CustomUser.ROLE_SUPERADM:
            raise InvalidRoleAssignment(MSG_INVALID_ROLE_ASSIGNMENT_NOT_SUPERADM)

        if CustomUser.objects.filter(email=data["email"]).exists():
            raise EmailAlreadyExists(MSG_ERRO_USUARIO_JA_EXISTE)

        user = CustomUser.objects.create_user(
            email=data["email"],
            password=data["password1"],
            role=role,
            nome=data.get("nome"),
            idade=data.get("idade"),
            queixa=data.get("queixa"),
            telefone=data.get("telefone"),
            origem=data.get("origem"),
            foto_perfil=data.get("foto_perfil"),
        )

        return user

    @staticmethod
    def authenticate_user(request, email, password):

        if not email or not password:
            raise AuthenticationFailed(MSG_AUTHENTICATION_FAILED_CREDENCIAIS)

        user = authenticate(request, username=email, password=password)

        if user is None:
            raise AuthenticationFailed(MSG_AUTHENTICATION_FAILED_EMAIL_SENHA)

        if not user.is_active:
            raise AuthenticationFailed(MSG_AUTHENTICATION_FAILED_CONTA_INATIVA)

        return user

    @staticmethod
    def update_user(instance, data, request_user):

        new_role = data.get("role", instance.role)

        if request_user.role != CustomUser.ROLE_SUPERADM:
            if new_role != instance.role:
                raise UnauthorizedRoleChange(MSG_INVALID_ROLE_ASSIGNMENT_PERFIL)

        allowed_fields = [
            "nome",
            "email",
            "idade",
            "queixa",
            "telefone",
            "origem",
            "foto_perfil",
        ]

        if request_user.role == CustomUser.ROLE_SUPERADM:
            allowed_fields.append("role")

        for field in allowed_fields:
            if field in data:
                setattr(instance, field, data[field])

        instance.save()
        return instance
