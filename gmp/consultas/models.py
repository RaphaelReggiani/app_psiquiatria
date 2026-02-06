from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


User = settings.AUTH_USER_MODEL


class AgendamentoConsulta(models.Model):

    STATUS_CHOICES = [
        ('marcada', 'Marcada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    paciente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consultas_como_paciente'
    )

    medico = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consultas_como_medico'
    )

    data_hora = models.DateTimeField()

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='marcada'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('medico', 'data_hora'),
            ('paciente', 'data_hora')
        ]
        ordering = ['data_hora']

    def __str__(self):
        return f"{self.data_hora} - {self.medico} - {self.paciente}"


class Consulta(models.Model):

    CONDICAO_PACIENTE_CHOICES = [
        ('estavel', 'Estável'),
        ('instavel', 'Instável'),
        ('critica', 'Crítica'),
    ]

    agendamento = models.OneToOneField(
        AgendamentoConsulta,
        on_delete=models.CASCADE,
        related_name='consulta'
    )

    condicao_paciente = models.CharField(
        max_length=15,
        choices=CONDICAO_PACIENTE_CHOICES
    )

    descricao = models.TextField(max_length=1000)

    receita = models.FileField(
        upload_to='consulta_receita/',
        blank=True,
        null=True
    )

    arquivo = models.FileField(
        upload_to='consulta_arquivo/',
        blank=True,
        null=True
    )

    protocolo = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.protocolo}] {self.agendamento}"
