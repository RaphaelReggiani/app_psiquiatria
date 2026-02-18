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
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache

from django.http import HttpResponse

from .models import AgendamentoConsulta, Consulta, ConsultaLog
from django.contrib.auth import get_user_model
from .forms import AgendamentoConsultaForm, ConsultaForm

from gmp.consultas.services.receita_service import gerar_receita_pdf

from .selectors import consultas_do_paciente, consultas_realizadas_por_medico, pacientes_do_medico


User = get_user_model()

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
                    return render(request, 'gmp/marcar_consulta.html', {'form': form})
                
            with transaction.atomic():
                
                agendamento.save()
                    
                ConsultaLog.objects.create(
                    consulta=agendamento,
                    usuario=request.user,
                    status_anterior='-',
                    status_novo=AgendamentoConsulta.STATUS_MARCADA
                )

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

    cache_key = f"horarios_{medico_id}_{data}"
    cached = cache.get(cache_key)

    if cached is not None:
        return JsonResponse(cached, safe=False)

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

    ocupados = AgendamentoConsulta.objects.only('data_hora').filter(
        medico_id=medico_id,
        data_hora__date=data,
        status=AgendamentoConsulta.STATUS_MARCADA
    ).values_list('data_hora', flat=True)

    ocupados = set(ocupados)

    disponiveis = [
        h.strftime('%H:%M')
        for h in horarios if h not in ocupados
    ]
    
    cache.set(cache_key, disponiveis, timeout=60)

    return JsonResponse(disponiveis, safe=False)

@login_required
def agenda_medico(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    hoje = localdate()

    consultas = AgendamentoConsulta.objects.select_related(
        'paciente',
        'medico'
    ).only(
        'id',
        'data_hora',
        'status',
        'paciente__id',
        'paciente__nome',
        'medico__id',
        'medico__nome'
    )

    if request.user.role == 'medico':
        consultas = consultas.filter(medico=request.user)

    data = request.GET.get('data')
    paciente_id = request.GET.get('paciente_id')
    queixa = request.GET.get('queixa')
    queixas_choices = User.QUEIXA_CHOICES
    status = request.GET.get('status')
    status_choices = AgendamentoConsulta.STATUS_CHOICES

    if data:
        consultas = consultas.filter(data_hora__date=data)

    if paciente_id:
        consultas = consultas.filter(paciente_id=paciente_id)

    if queixa:
        consultas = consultas.filter(
            paciente__queixa=queixa
        )

    if status:
        consultas = consultas.filter(status=status)

    consultas = consultas.order_by('data_hora')

    if (data or paciente_id or queixa) and not consultas.exists():
        messages.info(
            request,
            "Não há consultas registradas com estes parâmetros."
        )

    if request.user.role == 'medico':
        pacientes = User.objects.filter(
            consultas_como_paciente__medico=request.user
        ).only('id', 'nome').distinct()
    else:
        pacientes = User.objects.none()

    return render(request, 'gmp/agenda_medico.html', {
        'consultas': consultas,
        'hoje': hoje,
        'now': timezone.now(),
        'pacientes': pacientes,
        'queixas_choices': queixas_choices,
        'status_choices': status_choices,
    })


@login_required
def minhas_consultas(request):

    if request.user.role != 'paciente':
        raise PermissionDenied

    consultas = consultas_do_paciente(request.user)

    paginator = Paginator(consultas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gmp/minhas_consultas.html', {
        'page_obj': page_obj,
        'now': timezone.now()
    })

@login_required
def historico_paciente(request, paciente_id):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    consultas = AgendamentoConsulta.objects.select_related(
        'medico'
    ).filter(
        paciente_id=paciente_id,
        status=AgendamentoConsulta.STATUS_REALIZADA
    )

    return render(request, 'gmp/historico_paciente.html', {
        'consultas': consultas
    })


@login_required
def cadastrar_consulta(request, agendamento_id):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    agendamento = get_object_or_404(
        AgendamentoConsulta.objects.select_related('paciente', 'medico'),
        id=agendamento_id,
        medico=request.user
    )

    if agendamento.status != AgendamentoConsulta.STATUS_MARCADA:
        messages.warning(request, "Consulta já registrada ou cancelada.")
        return redirect('agenda_medico')

    if request.method == 'POST':
        form = ConsultaForm(request.POST, request.FILES)

        if form.is_valid():

            with transaction.atomic():

                consulta = form.save(commit=False)
                consulta.agendamento = agendamento
                consulta.save()

                status_anterior = agendamento.status
                agendamento.status = AgendamentoConsulta.STATUS_REALIZADA
                agendamento.save()

                data_str = agendamento.data_hora.date().strftime("%Y-%m-%d")
                cache_key = f"horarios_{agendamento.medico.id}_{data_str}"
                cache.delete(cache_key)

                ConsultaLog.objects.create(
                    consulta=agendamento,
                    usuario=request.user,
                    status_anterior=status_anterior,
                    status_novo=AgendamentoConsulta.STATUS_REALIZADA
                )

                transaction.on_commit(lambda: send_mail(
                    subject='Consulta confirmada',
                    message=(
                        f"Sua consulta foi marcada para "
                        f"{agendamento.data_hora.strftime('%d/%m/%Y %H:%M')} "
                        f"com o médico {agendamento.medico.nome}."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[agendamento.paciente.email],
                    fail_silently=True,
                ))

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
        AgendamentoConsulta.objects.select_related('paciente', 'medico'),
        id=consulta_id,
        status=AgendamentoConsulta.STATUS_MARCADA
    )

    if request.user.role == 'medico' and consulta.medico != request.user:
        raise PermissionDenied

    if request.user.role == 'paciente' and consulta.paciente != request.user:
        raise PermissionDenied

    if consulta.data_hora <= timezone.now():
        messages.error(request, "Não é possível cancelar consultas passadas.")
        return redirect(
            'agenda_medico' if request.user.role == 'medico'
            else 'minhas_consultas'
        )

    with transaction.atomic():

        status_anterior = consulta.status

        consulta.status = AgendamentoConsulta.STATUS_CANCELADA
        consulta.cancelado_por = request.user
        consulta.save(update_fields=['status', 'cancelado_por', 'cancelado_em'])


        data_str = consulta.data_hora.date().strftime("%Y-%m-%d")
        cache_key = f"horarios_{consulta.medico.id}_{data_str}"
        cache.delete(cache_key)

        ConsultaLog.objects.create(
            consulta=consulta,
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo=AgendamentoConsulta.STATUS_CANCELADA
        )

    messages.success(request, "Consulta cancelada com sucesso.")

    return redirect(
        'agenda_medico' if request.user.role == 'medico'
        else 'minhas_consultas'
    )


@login_required
def historico_medico_consultas(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

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

    pacientes = pacientes_do_medico(request.user)

    queixas_choices = User.QUEIXA_CHOICES

    if (data or paciente_id or queixa) and not consultas.exists():
        messages.info(
            request,
            "Não há consultas registradas com estes parâmetros."
        )

    paginator = Paginator(consultas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gmp/historico_medico_consultas.html', {
        'page_obj': page_obj,
        'pacientes': pacientes,
        'queixas_choices': queixas_choices,
    })


@login_required
def medico_pacientes(request):

    if not medico_ou_superadmin(request.user):
        raise PermissionDenied

    queixa = request.GET.get('queixa')

    pacientes = pacientes_do_medico(request.user)

    if queixa:
        pacientes = pacientes.filter(queixa=queixa)

    queixas_choices = User.QUEIXA_CHOICES

    if queixa and not pacientes.exists():
        messages.info(
            request,
            "Nenhum paciente encontrado com essa queixa."
        )

    return render(request, 'gmp/medico_pacientes.html', {
        'pacientes': pacientes,
        'queixas_choices': queixas_choices,
    })


@login_required
def visualizar_receita(request, consulta_id):

    agendamento = get_object_or_404(
        AgendamentoConsulta.objects.select_related('consulta', 'paciente', 'medico'),
        id=consulta_id
    )

    if not hasattr(agendamento, 'consulta'):
        raise PermissionDenied

    consulta = agendamento.consulta

    if request.user.role == 'paciente':
        if agendamento.paciente != request.user:
            raise PermissionDenied
        if agendamento.status != AgendamentoConsulta.STATUS_REALIZADA:
            raise PermissionDenied

    elif request.user.role == 'medico':
        if agendamento.medico != request.user:
            raise PermissionDenied
    else:
        raise PermissionDenied

    return render(request, 'gmp/receita.html', {
        'consulta': consulta
    })

@login_required
def gerar_receita_preview(request, agendamento_id):

    if request.user.role != 'medico':
        raise PermissionDenied

    agendamento = get_object_or_404(
        AgendamentoConsulta.objects.select_related('paciente'),
        id=agendamento_id,
        medico=request.user
    )

    if agendamento.status != AgendamentoConsulta.STATUS_MARCADA:
        return HttpResponse("Esta consulta não permite gerar receita.", status=400)

    crm = request.GET.get("crm")
    descricao = request.GET.get("descricao")

    if not crm or not descricao:
        return HttpResponse("CRM e descrição são obrigatórios.", status=400)

    pdf_buffer = gerar_receita_pdf(
        agendamento=agendamento,
        medico_nome=request.user.nome,
        crm=crm,
        descricao=descricao
    )

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="receita_preview.pdf"'

    ConsultaLog.objects.create(
        consulta=agendamento,
        usuario=request.user,
        status_anterior= agendamento.status,
        status_novo='receita_gerada'
    )

    return response

