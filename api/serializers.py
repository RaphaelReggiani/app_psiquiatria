from rest_framework import serializers
from gmp.usuarios.models import CustomUser
from gmp.consultas.models import AgendamentoConsulta, Consulta


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'nome',
            'email',
            'idade',
            'queixa',
            'role',
            'telefone',
            'origem',
            'foto_perfil',
            'password',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):

        request = self.context.get('request')
        password = validated_data.pop('password', None)

        if request and not request.user.is_authenticated:
            validated_data['role'] = 'paciente'

        if request and request.user.is_authenticated and request.user.role != 'superadm':
            validated_data['role'] = request.user.role

        user = CustomUser(**validated_data)

        if password:
            user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):

        request = self.context.get('request')

        if request and 'role' in validated_data:
            if request.user.role != 'superadm':
                validated_data.pop('role')

        password = validated_data.pop('password', None)

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
            'id',
            'paciente',
            'medico',
            'data_hora',
            'status',
        ]
        read_only_fields = [
            'id',
            'paciente',
            'status'
        ]


class ConsultaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Consulta
        fields = [
            'id',
            'agendamento',
            'condicao_paciente',
            'descricao',
            'receita',
            'arquivo'
        ]
        read_only_fields = [
            'id',
            'protocolo',
            'criado_em'
        ]

    def update(self, instance, validated_data):
        validated_data.pop('agendamento', None)
        return super().update(instance, validated_data)
    
    def validate_agendamento(self, value):
        request = self.context.get('request')

        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError(
                "Contexto de requisição inválido."
            )

        user = request.user
        if user.role != 'medico':
            raise serializers.ValidationError(
                "Apenas médicos podem registrar consultas."
            )
        if value.medico != user:
            raise serializers.ValidationError(
                "Você não pode registrar consulta de outro médico."
            )

        if value.status != 'realizada':
            raise serializers.ValidationError(
                "Consulta só pode ser registrada para agendamento realizado."
            )

        return value

