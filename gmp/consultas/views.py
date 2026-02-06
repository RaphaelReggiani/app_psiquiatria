from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone

from .models import AgendamentoConsulta, Consulta
from .forms import AgendamentoConsultaForm, ConsultaForm


def paciente_ou_superadmin(user):
    return user.is_authenticated and user.role in ['paciente', 'superadm']


def medico_ou_superadmin(user):
    return user.is_authenticated and user.role in ['medico', 'superadm']


@login_required
def marcar_consulta(request):

    if not paciente_ou_superadmin(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = AgendamentoConsultaForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():
            agendamento = form.save(commit=False)

            if request.user.role == 'paciente':
                agendamento.paciente = request.user

            agendamento.save()
            messages.success(request, "Consulta marcada com sucesso.")
            return redirect('minhas_consultas')

    else:
        form = AgendamentoConsultaForm(user=request.user)

    return render(request, 'gmp/marcar_consulta.html', {
        'form': form,
        'paciente_logado': request.user
    })


@login_required
def agenda_medico(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    if request.user.role == 'medico':
        consultas = AgendamentoConsulta.objects.filter(
            medico=request.user
        )
    else:
        consultas = AgendamentoConsulta.objects.all()

    return render(request, 'gmp/agenda_medico.html', {
        'consultas': consultas,
        'now': timezone.now()
    })


@login_required
def minhas_consultas(request):

    if request.user.role != 'paciente':
        raise PermissionDenied

    consultas = AgendamentoConsulta.objects.filter(
        paciente=request.user
    )

    return render(request, 'gmp/minhas_consultas.html', {
        'consultas': consultas,
        'now': timezone.now()
    })


@login_required
def historico_paciente(request, paciente_id):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    consultas = AgendamentoConsulta.objects.filter(
        paciente_id=paciente_id,
        status='realizada'
    )

    return render(request, 'gmp/historico_paciente.html', {
        'consultas': consultas
    })


@login_required
def cadastrar_consulta(request, agendamento_id):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    agendamento = get_object_or_404(
        AgendamentoConsulta,
        id=agendamento_id
    )

    if agendamento.status != 'marcada':
        messages.warning(request, "Consulta já registrada ou cancelada.")
        return redirect('agenda_medico')

    if request.method == 'POST':
        form = ConsultaForm(request.POST, request.FILES)

        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.agendamento = agendamento
            consulta.save()

            agendamento.status = 'realizada'
            agendamento.save()

            messages.success(request, "Consulta registrada com sucesso.")
            return redirect('agenda_medico')

    else:
        form = ConsultaForm()

    return render(request, 'gmp/cadastrar_consulta.html', {
        'form': form,
        'agendamento': agendamento,
        'paciente': agendamento.paciente
    })
