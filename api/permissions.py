from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'superadm'


class IsUserOwnerOrSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'superadm':
            return True
        return obj == request.user


class IsAgendamentoOwnerOrSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == 'superadm':
            return True

        return obj.paciente == user or obj.medico == user


class IsConsultaOwnerOrSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == 'superadm':
            return True

        return (
            obj.agendamento.paciente == user or
            obj.agendamento.medico == user
        )
