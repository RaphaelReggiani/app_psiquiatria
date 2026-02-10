from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import time, timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import localdate

from .models import AgendamentoConsulta, Consulta
from .forms import AgendamentoConsultaForm, ConsultaForm


def paciente_ou_superadmin(user):
    return user.is_authenticated and user.role in ['paciente', 'superadm']


def medico_ou_superadmin(user):
    return user.is_authenticated and user.role in ['medico', 'superadm']


@login_required
def marcar_consulta(request):

    if request.user.role == 'medico':
        raise PermissionDenied

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

        elif request.user.role == 'superadm':
            if agendamento.paciente is None:
                messages.error(request, "Selecione um paciente.")
                return render(
                    request,
                    'gmp/marcar_consulta.html',
                    {'form': form}
                )

            agendamento.save()

            messages.success(request, "Consulta marcada com sucesso.")
            return redirect('minhas_consultas')
        
    else:
        form = AgendamentoConsultaForm(user=request.user)

    return render(request, 'gmp/marcar_consulta.html', {
        'form': form,
        'paciente_logado': request.user if request.user.role == 'paciente' else None
    })


@login_required
def horarios_disponiveis(request):
    medico_id = request.GET.get('medico')
    data = request.GET.get('data')

    if not medico_id or not data:
        return JsonResponse([], safe=False)

    data = datetime.strptime(data, "%Y-%m-%d").date()

    if data.weekday() >= 5:
        return JsonResponse([], safe=False)

    agora = timezone.now()
    minimo = agora + timedelta(hours=2)

    horarios = []
    for h in range(8, 21):
        for m in (0, 30):
            dt = timezone.make_aware(datetime.combine(data, time(h, m)))
            if dt >= minimo:
                horarios.append(dt)

    ocupados = AgendamentoConsulta.objects.filter(
        medico_id=medico_id,
        data_hora__date=data,
        status='marcada'
    ).values_list('data_hora', flat=True)

    ocupados = set(ocupados)

    disponiveis = [
        h.strftime('%H:%M')
        for h in horarios if h not in ocupados
    ]

    return JsonResponse(disponiveis, safe=False)

@login_required
def agenda_medico(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    hoje = localdate()

    if request.user.role == 'medico':
        consultas = AgendamentoConsulta.objects.filter(
            medico=request.user,
            data_hora__gte=timezone.now()
        ).order_by('data_hora')
    else:
        consultas = AgendamentoConsulta.objects.filter(
            data_hora__date=hoje
        )

    return render(request, 'gmp/agenda_medico.html', {
        'consultas': consultas,
        'hoje': hoje,
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

            send_mail(
                subject='Consulta confirmada',
                message=(
                    f"Sua consulta foi marcada para "
                    f"{agendamento.data_hora.strftime('%d/%m/%Y %H:%M')} "
                    f"com o médico {agendamento.medico.nome}."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agendamento.paciente.email],
                fail_silently=True,
            )

            messages.success(request, "Consulta registrada com sucesso.")
            return redirect('agenda_medico')

    else:
        form = ConsultaForm()

    return render(request, 'gmp/cadastrar_consulta.html', {
        'form': form,
        'agendamento': agendamento,
        'paciente': agendamento.paciente
    })


@login_required
def cancelar_consulta(request, consulta_id):

    consulta = get_object_or_404(
        AgendamentoConsulta,
        id=consulta_id,
        status='marcada'
    )

    if request.user.role == 'medico' and consulta.medico != request.user:
        raise PermissionDenied

    if request.user.role == 'paciente' and consulta.paciente != request.user:
        raise PermissionDenied

    if consulta.data_hora <= timezone.now():
        messages.error(request, "Não é possível cancelar consultas passadas.")
        return redirect('minhas_consultas')

    consulta.status = 'cancelada'
    consulta.save()

    messages.success(request, "Consulta cancelada com sucesso.")

    if request.user.role == 'medico':
        return redirect('agenda_medico')

    return redirect('minhas_consultas')
