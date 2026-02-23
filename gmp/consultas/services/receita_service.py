from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from django.utils import timezone
from django.db import transaction

from gmp.consultas.models import ConsultaLog, AgendamentoConsulta
from gmp.consultas.exceptions import (
    ConsultaError,
    DadosReceitaInvalidosError,
    ConsultaStatusInvalidoError
)

from gmp.consultas.constants import (
    FORMATO_DATA, 
    FORMATO_HORA,
    MSG_ERRO_SEM_PERMISSAO,
    MSG_ERRO_RECEITA_NAO_PERMITIDA,
    MSG_ERRO_CRM_DESCRICAO_OBRIGATORIOS,
)


def gerar_receita_pdf(agendamento, medico_nome, crm, descricao):

    if not crm or not descricao:
        raise DadosReceitaInvalidosError()

    if agendamento.status not in [
        AgendamentoConsulta.STATUS_MARCADA,
        AgendamentoConsulta.STATUS_REALIZADA
    ]:
        raise ConsultaStatusInvalidoError(MSG_ERRO_RECEITA_NAO_PERMITIDA)

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        textColor=colors.HexColor("#065f46"),
        fontSize=18
    )

    normal_style = styles["Normal"]

    elements.append(Paragraph("G.M.P - Receita Médica", titulo_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Médico: {medico_nome}", normal_style))
    elements.append(Paragraph(f"CRM: {crm}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"Paciente: {agendamento.paciente.nome}", normal_style))
    elements.append(Paragraph(f"Idade: {agendamento.paciente.idade}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Descrição da Receita:", styles["Heading3"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(descricao.replace("\n", "<br/>"), normal_style))

    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(
        f"Data: {timezone.now().strftime(FORMATO_DATA + ' ' + FORMATO_HORA)}",
        normal_style
    ))

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Assinatura: ________________________________", normal_style))

    qr_code = qr.QrCodeWidget(str(agendamento.id))
    bounds = qr_code.getBounds()
    size = 100
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    drawing = Drawing(size, size, transform=[
        size / width, 0, 0, size / height, 0, 0
    ])
    drawing.add(qr_code)

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(drawing)

    doc.build(elements)
    buffer.seek(0)

    return buffer


def gerar_receita_preview_service(agendamento, usuario, crm, descricao):

    if usuario.role != usuario.ROLE_MEDICO:
        raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

    if agendamento.medico != usuario:
        raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

    if agendamento.status != AgendamentoConsulta.STATUS_MARCADA:
        raise ConsultaError(MSG_ERRO_RECEITA_NAO_PERMITIDA)

    if not crm or not descricao:
        raise ConsultaError(MSG_ERRO_CRM_DESCRICAO_OBRIGATORIOS)

    pdf_buffer = gerar_receita_pdf(
        agendamento=agendamento,
        medico_nome=usuario.nome,
        crm=crm,
        descricao=descricao
    )

    with transaction.atomic():
        ConsultaLog.objects.create(
            consulta=agendamento,
            usuario=usuario,
            status_anterior=agendamento.status,
            status_novo=ConsultaLog.STATUS_RECEITA_GERADA
        )

    return pdf_buffer


def validar_visualizacao_receita_service(agendamento, usuario):

    if not hasattr(agendamento, 'consulta'):
        raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

    if usuario.role == usuario.ROLE_PACIENTE:
        if agendamento.paciente != usuario:
            raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

        if agendamento.status != AgendamentoConsulta.STATUS_REALIZADA:
            raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

    elif usuario.role == usuario.ROLE_MEDICO:
        if agendamento.medico != usuario:
            raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

    else:
        raise ConsultaError(MSG_ERRO_SEM_PERMISSAO)

    return agendamento.consulta
