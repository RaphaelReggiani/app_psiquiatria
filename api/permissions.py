from rest_framework.permissions import BasePermission

from gmp.usuarios.models import CustomUser


class IsAuthenticatedBase(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsSuperAdmin(IsAuthenticatedBase):

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        return request.user.role == CustomUser.ROLE_SUPERADM


class IsUserOwnerOrSuperAdmin(IsAuthenticatedBase):

    def has_object_permission(self, request, view, obj):
        if request.user.role == CustomUser.ROLE_SUPERADM:
            return True
        return obj == request.user


class IsAgendamentoOwnerOrSuperAdmin(IsAuthenticatedBase):

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == CustomUser.ROLE_SUPERADM:
            return True

        return obj.paciente == user or obj.medico == user


class IsConsultaOwnerOrSuperAdmin(IsAuthenticatedBase):

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == CustomUser.ROLE_SUPERADM:
            return True

        return obj.agendamento.paciente == user or obj.agendamento.medico == user
