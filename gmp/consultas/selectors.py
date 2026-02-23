from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from .models import AgendamentoConsulta

User = get_user_model()


def consultas_do_paciente(paciente) -> QuerySet:
    return (
        AgendamentoConsulta.objects
        .select_related('medico')
        .filter(paciente_id=paciente.id)
        .order_by('-data_hora')
    )


def historico_paciente_realizadas(paciente_id) -> QuerySet:
    return (
        AgendamentoConsulta.objects
        .select_related('medico')
        .filter(
            paciente_id=paciente_id,
            status=AgendamentoConsulta.STATUS_REALIZADA
        )
        .order_by('-data_hora')
    )


def consultas_realizadas_por_medico(medico) -> QuerySet:
    return (
        AgendamentoConsulta.objects
        .select_related('paciente')
        .filter(
            medico_id=medico.id,
            status=AgendamentoConsulta.STATUS_REALIZADA
        )
        .order_by('-data_hora')
    )


def agenda_medico_com_filtros(
    medico,
    data=None,
    paciente_id=None,
    queixa=None,
    status=None,
) -> QuerySet:
    consultas = (
        AgendamentoConsulta.objects.select_related('paciente', 'medico')
        .only(
            'id',
            'data_hora',
            'status',
            'paciente__id',
            'paciente__nome',
            'medico__id',
            'medico__nome'
        )
    )

    if medico.role != medico.ROLE_SUPERADM:
        consultas = consultas.filter(medico_id=medico.id)

    if data:
        consultas = consultas.filter(data_hora__date=data)

    if paciente_id:
        consultas = consultas.filter(paciente_id=paciente_id)

    if queixa:
        consultas = consultas.filter(paciente__queixa=queixa)

    if status:
        consultas = consultas.filter(status=status)

    return consultas.order_by('-data_hora')


def pacientes_com_consulta_realizada_do_medico(medico) -> QuerySet:
    return (
        User.objects
        .filter(
            consultas_como_paciente__medico_id=medico.id,
            consultas_como_paciente__status=AgendamentoConsulta.STATUS_REALIZADA
        )
        .distinct()
        .only('id', 'nome')
    )


def consulta_por_id(consulta_id) -> QuerySet:
    return (
        AgendamentoConsulta.objects
        .select_related('paciente', 'medico', 'consulta')
        .filter(id=consulta_id)
    )


def consulta_marcada_por_id(consulta_id) -> QuerySet:
    return (
        AgendamentoConsulta.objects
        .select_related('paciente', 'medico')
        .filter(
            id=consulta_id,
            status=AgendamentoConsulta.STATUS_MARCADA
        )
    )

