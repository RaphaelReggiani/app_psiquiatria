from .models import AgendamentoConsulta
from django.contrib.auth import get_user_model

User = get_user_model()


def consultas_do_paciente(paciente):
    return (
        AgendamentoConsulta.objects
        .select_related('medico')
        .filter(paciente=paciente)
        .order_by('-data_hora')
    )


def consultas_realizadas_por_medico(medico):
    return (
        AgendamentoConsulta.objects
        .select_related('paciente')
        .filter(
            medico=medico,
            status=AgendamentoConsulta.STATUS_REALIZADA
        )
        .order_by('-data_hora')
    )


def pacientes_do_medico(medico):
    return (
        User.objects
        .filter(
            consultas_como_paciente__medico=medico,
            consultas_como_paciente__status=AgendamentoConsulta.STATUS_REALIZADA
        )
        .distinct()
        .only('id', 'nome')
    )

