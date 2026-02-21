from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import localdate
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from gmp.consultas.services.consulta_service import (
    cancelar_consulta_service, 
    registrar_consulta_service, 
    marcar_consulta_service, 
)
from gmp.consultas.services.horarios_service import ( 
    horarios_disponiveis_service,
)
from gmp.consultas.services.receita_service import ( 
    gerar_receita_preview_service,
    validar_visualizacao_receita_service,
)

from gmp.consultas.exceptions import ConsultaError

from gmp.usuarios.models import CustomUser

from .models import AgendamentoConsulta
from .forms import AgendamentoConsultaForm, ConsultaForm
from .selectors import (
    consultas_do_paciente, 
    consultas_realizadas_por_medico,
    pacientes_com_consulta_realizada_do_medico,
    historico_paciente_realizadas,
    agenda_medico_com_filtros,
    consulta_marcada_por_id,
    consulta_por_id,
)
from gmp.consultas.constants import (
    PAGINACAO_PADRAO,
    MSG_CONSULTA_MARCADA_SUCESSO,
    MSG_CONSULTA_CANCELADA_SUCESSO,
    MSG_CONSULTA_REGISTRADA_SUCESSO,
    MSG_ERRO_SEM_PERMISSAO,
    MSG_INFO_SEM_CONSULTAS_FILTRO,
    MSG_INFO_SEM_PACIENTES_QUEIXA,
)

from .decorators import role_required


User = get_user_model()

def paciente_ou_superadmin(user):
    return user.is_authenticated and user.role in [CustomUser.ROLE_PACIENTE, CustomUser.ROLE_SUPERADM]


def medico_ou_superadmin(user):
    return user.is_authenticated and user.role in [CustomUser.ROLE_MEDICO, CustomUser.ROLE_SUPERADM]


@login_required
@role_required([CustomUser.ROLE_PACIENTE, CustomUser.ROLE_SUPERADM])
def marcar_consulta(request):

    if request.method == 'POST':
        form = AgendamentoConsultaForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                marcar_consulta_service(form, request.user)
                messages.success(request, MSG_CONSULTA_MARCADA_SUCESSO)
                return redirect('minhas_consultas')
            except ConsultaError as e:
                messages.error(request, str(e))
    else:
        form = AgendamentoConsultaForm(user=request.user)

    return render(request, 'gmp/marcar_consulta.html', {
        'form': form,
        'paciente_logado': request.user if request.user.role == CustomUser.ROLE_PACIENTE else None
    })


@login_required
def horarios_disponiveis(request):

    medico_id = request.GET.get('medico')
    data = request.GET.get('data')

    horarios = horarios_disponiveis_service(medico_id, data)

    return JsonResponse(horarios, safe=False)


@login_required
@role_required([CustomUser.ROLE_MEDICO, CustomUser.ROLE_SUPERADM])
def agenda_medico(request):

    hoje = localdate()

    data = request.GET.get('data')
    paciente_id = request.GET.get('paciente_id')
    queixa = request.GET.get('queixa')
    status = request.GET.get('status')

    consultas = agenda_medico_com_filtros(
        medico=request.user,
        data=data,
        paciente_id=paciente_id,
        queixa=queixa,
        status=status,
    )

    if (data or paciente_id or queixa or status) and not consultas.exists():
        messages.info(request, MSG_INFO_SEM_CONSULTAS_FILTRO)

    pacientes = pacientes_com_consulta_realizada_do_medico(request.user)

    return render(request, 'gmp/agenda_medico.html', {
        'consultas': consultas,
        'hoje': hoje,
        'now': timezone.now(),
        'pacientes': pacientes,
        'queixas_choices': CustomUser.QUEIXA_CHOICES,
        'status_choices': AgendamentoConsulta.STATUS_CHOICES,
    })

@login_required
@role_required([CustomUser.ROLE_PACIENTE])
def minhas_consultas(request):

    consultas = consultas_do_paciente(request.user)

    paginator = Paginator(consultas, PAGINACAO_PADRAO)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gmp/minhas_consultas.html', {
        'page_obj': page_obj,
        'now': timezone.now()
    })


@login_required
@role_required([CustomUser.ROLE_MEDICO, CustomUser.ROLE_SUPERADM])
def historico_paciente(request, paciente_id):

    consultas = historico_paciente_realizadas(paciente_id)

    return render(request, 'gmp/historico_paciente.html', {
        'consultas': consultas
    })


@login_required
@role_required([CustomUser.ROLE_MEDICO, CustomUser.ROLE_SUPERADM])
def cadastrar_consulta(request, agendamento_id):

    agendamento = get_object_or_404(
        AgendamentoConsulta.objects.select_related('paciente', 'medico'),
        id=agendamento_id,
        medico=request.user
    )

    if request.method == 'POST':
        form = ConsultaForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                registrar_consulta_service(agendamento, form, request.user)
                messages.success(request, MSG_CONSULTA_REGISTRADA_SUCESSO)
                return redirect('agenda_medico')
            except ConsultaError as e:
                messages.error(request, str(e))
    else:
        form = ConsultaForm()

    return render(request, 'gmp/cadastrar_consulta.html', {
        'form': form,
        'agendamento': agendamento,
        'paciente': agendamento.paciente
    })


@login_required
@role_required([CustomUser.ROLE_MEDICO, CustomUser.ROLE_PACIENTE])
def cancelar_consulta(request, consulta_id):

    consulta = get_object_or_404(
        consulta_marcada_por_id(consulta_id)
    )

    try:
        cancelar_consulta_service(consulta, request.user)
        messages.success(request, MSG_CONSULTA_CANCELADA_SUCESSO)
    except ConsultaError as e:
        messages.error(request, str(e))

    return redirect(
        'agenda_medico' if request.user.role == CustomUser.ROLE_MEDICO
        else 'minhas_consultas'
    )


@login_required
def historico_medico_consultas(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied(MSG_ERRO_SEM_PERMISSAO)

    consultas = consultas_realizadas_por_medico(request.user)

    data = request.GET.get('data')
    paciente_id = request.GET.get('paciente_id')
    queixa = request.GET.get('queixa')

    if data:
        consultas = consultas.filter(data_hora__date=data)

    if paciente_id:
        consultas = consultas.filter(paciente_id=paciente_id)

    if queixa:
        consultas = consultas.filter(
            paciente__queixa=queixa
        )

    pacientes = pacientes_com_consulta_realizada_do_medico(request.user)

    if (data or paciente_id or queixa) and not consultas.exists():
        messages.info(request, MSG_INFO_SEM_CONSULTAS_FILTRO)

    paginator = Paginator(consultas, PAGINACAO_PADRAO)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gmp/historico_medico_consultas.html', {
        'page_obj': page_obj,
        'pacientes': pacientes,
        'queixas_choices': CustomUser.QUEIXA_CHOICES,
    })


@login_required
def medico_pacientes(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied(MSG_ERRO_SEM_PERMISSAO)

    queixa = request.GET.get('queixa')

    pacientes = pacientes_com_consulta_realizada_do_medico(request.user)

    if queixa:
        pacientes = pacientes.filter(queixa=queixa)

    if queixa and not pacientes.exists():
        messages.info(request, MSG_INFO_SEM_PACIENTES_QUEIXA)

    return render(request, 'gmp/medico_pacientes.html', {
        'pacientes': pacientes,
        'queixas_choices': CustomUser.QUEIXA_CHOICES,
    })


@login_required
def visualizar_receita(request, consulta_id):

    agendamento = get_object_or_404(
        consulta_por_id(consulta_id)
    )

    try:
        consulta = validar_visualizacao_receita_service(
            agendamento,
            request.user
        )
    except ConsultaError as e:
        raise PermissionDenied(str(e))

    return render(request, 'gmp/receita.html', {
        'consulta': consulta
    })

@login_required
def gerar_receita_preview(request, agendamento_id):

    agendamento = get_object_or_404(
        consulta_marcada_por_id(agendamento_id)
    )

    crm = request.GET.get("crm")
    descricao = request.GET.get("descricao")

    try:
        pdf_buffer = gerar_receita_preview_service(
            agendamento,
            request.user,
            crm,
            descricao
        )

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="receita_preview.pdf"'
        return response

    except ConsultaError as e:
        return HttpResponse(str(e), status=400)
