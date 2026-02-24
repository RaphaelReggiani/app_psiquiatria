from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from gmp.consultas.constants.constants import (
    FORMATO_DATA,
    FORMATO_HORA,
    LOG_STATUS_INICIAL,
)
from gmp.consultas.constants.messages_constants import (
    MSG_ERRO_CANCELAR_CONSULTA_SERVICE,
    MSG_ERRO_REGISTRAR_CONSULTA_SERVICE,
)
from gmp.consultas.exceptions import (
    ConsultaError,
    ConsultaPassadaError,
    ConsultaPermissaoNegadaError,
    ConsultaStatusInvalidoError,
)
from gmp.consultas.models import AgendamentoConsulta, ConsultaLog
from gmp.consultas.services.cache_service import delete_cache
from gmp.consultas.services.log_service import registrar_log
from gmp.consultas.utils.cache_keys import horarios_medico_key


def marcar_consulta_service(form, usuario):

    with transaction.atomic():

        agendamento = form.save(commit=False)

        if usuario.role == usuario.ROLE_PACIENTE:
            agendamento.paciente = usuario

        if usuario.role == usuario.ROLE_SUPERADM and not agendamento.paciente:
            raise ConsultaError("Selecione um paciente.")

        agendamento.save()

        ConsultaLog.objects.create(
            consulta=agendamento,
            usuario=usuario,
            status_anterior=LOG_STATUS_INICIAL,
            status_novo=AgendamentoConsulta.STATUS_MARCADA,
        )

        transaction.on_commit(
            lambda: send_mail(
                subject="Consulta confirmada",
                message=(
                    f"Sua consulta foi marcada para "
                    f"{agendamento.data_hora.strftime(FORMATO_DATA + ' às ' + FORMATO_HORA)} "
                    f"com o médico {agendamento.medico.nome}."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agendamento.paciente.email],
                fail_silently=True,
            )
        )

    return agendamento


def cancelar_consulta_service(consulta, usuario):

    if consulta.status != AgendamentoConsulta.STATUS_MARCADA:
        raise ConsultaStatusInvalidoError(MSG_ERRO_CANCELAR_CONSULTA_SERVICE)

    if consulta.data_hora <= timezone.now():
        raise ConsultaPassadaError()

    if usuario.role == usuario.ROLE_MEDICO and consulta.medico != usuario:
        raise ConsultaPermissaoNegadaError()

    if usuario.role == usuario.ROLE_PACIENTE and consulta.paciente != usuario:
        raise ConsultaPermissaoNegadaError()

    with transaction.atomic():

        status_anterior = consulta.status

        consulta.status = AgendamentoConsulta.STATUS_CANCELADA
        consulta.cancelado_por = usuario
        consulta.save(update_fields=["status", "cancelado_por", "cancelado_em"])

        data_str = consulta.data_hora.date().strftime(FORMATO_DATA)
        cache.delete(horarios_medico_key(consulta.medico.id, data_str))

    registrar_log(
        consulta=consulta,
        usuario=usuario,
        status_anterior=status_anterior,
        status_novo=AgendamentoConsulta.STATUS_CANCELADA,
    )

    return consulta


def registrar_consulta_service(agendamento, form, usuario):

    if agendamento.status != AgendamentoConsulta.STATUS_MARCADA:
        raise ConsultaStatusInvalidoError(MSG_ERRO_REGISTRAR_CONSULTA_SERVICE)

    if agendamento.medico != usuario:
        raise ConsultaPermissaoNegadaError()

    with transaction.atomic():

        consulta = form.save(commit=False)
        consulta.agendamento = agendamento
        consulta.save()

        status_anterior = agendamento.status
        agendamento.status = AgendamentoConsulta.STATUS_REALIZADA
        agendamento.save(update_fields=["status"])

        data_str = agendamento.data_hora.date().strftime(FORMATO_DATA)
        delete_cache(horarios_medico_key(agendamento.medico.id, data_str))

        ConsultaLog.objects.create(
            consulta=agendamento,
            usuario=usuario,
            status_anterior=status_anterior,
            status_novo=AgendamentoConsulta.STATUS_REALIZADA,
        )

    return consulta
