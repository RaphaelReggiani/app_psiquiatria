from django.utils import timezone
from rest_framework import serializers

from api.constants import (
    API_ERROR_AGENDAMENTO_FINALIZADO,
    API_ERROR_AGENDAMENTO_PASSADO,
    API_ERROR_APENAS_MEDICO,
    API_ERROR_ARQUIVO_MAX_SIZE,
    API_ERROR_ARQUIVO_NAO_PDF,
    API_ERROR_ARQUIVO_TIPO_INVALIDO,
    API_ERROR_CONSULTA_EXISTENTE,
    API_ERROR_CONSULTA_OUTRO_MEDICO,
    API_ERROR_OUTRO_MEDICO,
    API_ERROR_STATUS_NAO_REALIZADO,
    API_ERROR_STATUS_PERMISSION,
    API_RECEITA_MAX_SIZE,
)
from gmp.consultas.models import AgendamentoConsulta, Consulta
from gmp.usuarios.models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "nome",
            "email",
            "idade",
            "queixa",
            "role",
            "telefone",
            "origem",
            "foto_perfil",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):

        request = self.context.get("request")
        password = validated_data.pop("password", None)

        if request and not request.user.is_authenticated:
            validated_data["role"] = CustomUser.ROLE_PACIENTE

        if (
            request
            and request.user.is_authenticated
            and request.user.role != CustomUser.ROLE_SUPERADM
        ):
            validated_data["role"] = request.user.role

        user = CustomUser(**validated_data)

        if password:
            user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):

        request = self.context.get("request")

        if request and "role" in validated_data:
            if request.user.role != CustomUser.ROLE_SUPERADM:
                validated_data.pop("role")

        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class AgendamentoConsultaSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgendamentoConsulta
        fields = [
            "id",
            "paciente",
            "medico",
            "data_hora",
            "status",
        ]
        read_only_fields = ["id", "paciente", "status"]

    def update(self, instance, validated_data):
        if instance.status in [
            AgendamentoConsulta.STATUS_REALIZADA,
            AgendamentoConsulta.STATUS_NAO_REALIZADA,
        ]:
            raise serializers.ValidationError(API_ERROR_AGENDAMENTO_FINALIZADO)
        return super().update(instance, validated_data)

    def validate(self, data):
        request = self.context.get("request")
        user = request.user

        if "status" in data:
            if user.role not in [CustomUser.ROLE_MEDICO, CustomUser.ROLE_SUPERADM]:
                raise serializers.ValidationError(API_ERROR_STATUS_PERMISSION)

            if user.role == CustomUser.ROLE_MEDICO and self.instance:
                if self.instance.medico != user:
                    raise serializers.ValidationError(API_ERROR_OUTRO_MEDICO)

        return data


class ConsultaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Consulta
        fields = [
            "id",
            "agendamento",
            "condicao_paciente",
            "descricao",
            "receita",
            "arquivo",
            "protocolo",
            "criado_em",
            "crm_medico",
            "descricao_receita",
            "data_geracao_receita",
            "receita_pdf",
        ]

    def validate(self, data):
        agendamento = data.get("agendamento")

        if agendamento and agendamento.data_hora < timezone.now():
            raise serializers.ValidationError(API_ERROR_AGENDAMENTO_PASSADO)

        if agendamento and hasattr(agendamento, "consulta"):
            raise serializers.ValidationError(API_ERROR_CONSULTA_EXISTENTE)

        return data

    def update(self, instance, validated_data):
        validated_data.pop("agendamento", None)
        return super().update(instance, validated_data)

    def validate_agendamento(self, value):
        request = self.context.get("request")

        user = request.user
        if user.role != CustomUser.ROLE_MEDICO:
            raise serializers.ValidationError(API_ERROR_APENAS_MEDICO)
        if value.medico != user:
            raise serializers.ValidationError(API_ERROR_CONSULTA_OUTRO_MEDICO)

        if value.status != AgendamentoConsulta.STATUS_REALIZADA:
            raise serializers.ValidationError(API_ERROR_STATUS_NAO_REALIZADO)

        return value

    def validate_receita(self, value):
        max_size = API_RECEITA_MAX_SIZE

        if value.size >= max_size:
            raise serializers.ValidationError(API_ERROR_ARQUIVO_MAX_SIZE)

        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(API_ERROR_ARQUIVO_NAO_PDF)

        if hasattr(value, "content_type") and value.content_type != "application/pdf":
            raise serializers.ValidationError(API_ERROR_ARQUIVO_TIPO_INVALIDO)

        return value
