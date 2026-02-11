from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
import uuid


User = settings.AUTH_USER_MODEL


class AgendamentoConsulta(models.Model):

    STATUS_CHOICES = [
        ('marcada', 'Marcada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('nao_realizada', 'Não Realizada'),
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

    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cancelamentos_realizados'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.data_hora} - {self.medico} - {self.paciente}"

    def save(self, *args, **kwargs):
        if self.status == 'cancelada' and not self.cancelado_em:
            self.cancelado_em = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        unique_together = [
            ('medico', 'data_hora'),
            ('paciente', 'data_hora')
        ]
        ordering = ['-data_hora']

    @classmethod
    def atualizar_consultas_expiradas(cls):
        agora = timezone.now()
        limite = agora - timedelta(hours=2)

        consultas_expiradas = cls.objects.filter(
            status='marcada',
            data_hora__lt=limite
        ).select_related('paciente', 'medico')

        for consulta in consultas_expiradas:
            with transaction.atomic():
                status_anterior = consulta.status
                consulta.status = 'nao_realizada'
                consulta.save()

                ConsultaLog.objects.create(
                    consulta=consulta,
                    usuario=None,
                    status_anterior=status_anterior,
                    status_novo='nao_realizada'
                )


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
    

class ConsultaLog(models.Model):

    consulta = models.ForeignKey(
        AgendamentoConsulta,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    status_anterior = models.CharField(max_length=15)
    status_novo = models.CharField(max_length=15)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consulta} - {self.status_anterior} → {self.status_novo}"
