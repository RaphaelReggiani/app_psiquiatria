from datetime import datetime, time, timedelta

from django.utils import timezone

from gmp.consultas.constants import (
    ANTECEDENCIA_MINIMA_HORAS,
    CACHE_TIMEOUT_HORARIOS,
    DIA_UTIL_FINAL,
    FORMATO_DATA,
    FORMATO_HORA,
    HORA_FIM_ATENDIMENTO,
    HORA_INICIO_ATENDIMENTO,
    INTERVALO_MINUTOS,
)
from gmp.consultas.models import AgendamentoConsulta
from gmp.consultas.services.cache_service import get_cache, set_cache
from gmp.consultas.utils.cache_keys import horarios_medico_key


def horarios_disponiveis_service(medico_id, data_str):

    if not medico_id or not data_str:
        return []

    cache_key = horarios_medico_key(medico_id, data_str)
    cached = get_cache(cache_key)

    if cached is not None:
        return cached

    data = datetime.strptime(data_str, FORMATO_DATA).date()

    if data.weekday() > DIA_UTIL_FINAL:
        return []

    agora = timezone.now()
    minimo = agora + timedelta(hours=ANTECEDENCIA_MINIMA_HORAS)

    horarios = []

    for h in range(HORA_INICIO_ATENDIMENTO, HORA_FIM_ATENDIMENTO):
        for m in INTERVALO_MINUTOS:
            dt = timezone.make_aware(datetime.combine(data, time(h, m)))
            if dt >= minimo:
                horarios.append(dt)

    ocupados = (
        AgendamentoConsulta.objects.only("data_hora")
        .filter(
            medico_id=medico_id,
            data_hora__date=data,
            status=AgendamentoConsulta.STATUS_MARCADA,
        )
        .values_list("data_hora", flat=True)
    )

    ocupados = set(ocupados)

    disponiveis = [h.strftime(FORMATO_HORA) for h in horarios if h not in ocupados]

    set_cache(cache_key, disponiveis, CACHE_TIMEOUT_HORARIOS)

    return disponiveis
