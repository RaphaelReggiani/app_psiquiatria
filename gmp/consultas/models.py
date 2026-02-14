from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


User = settings.AUTH_USER_MODEL


class AgendamentoConsulta(models.Model):

    STATUS_MARCADA = 'marcada'
    STATUS_REALIZADA = 'realizada'
    STATUS_CANCELADA = 'cancelada'
    STATUS_NAO_REALIZADA = 'nao_realizada'

    STATUS_CHOICES = [
        (STATUS_MARCADA, 'Marcada'),
        (STATUS_REALIZADA, 'Realizada'),
        (STATUS_CANCELADA, 'Cancelada'),
        (STATUS_NAO_REALIZADA, 'Não Realizada'),
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

    data_hora = models.DateTimeField(db_index=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_MARCADA,
        db_index=True
    )

    cancelado_por = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cancelamentos_realizados'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_hora']
        constraints = [
            models.UniqueConstraint(
                fields=['medico', 'data_hora'],
                name='unique_medico_horario'
            ),
            models.UniqueConstraint(
                fields=['paciente', 'data_hora'],
                name='unique_paciente_horario'
            ),
        ]

    def __str__(self):
        return f"{self.data_hora} - {self.medico} - {self.paciente}"

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_CANCELADA and not self.cancelado_em:
            self.cancelado_em = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def atualizar_consultas_expiradas(cls):

        from .models import ConsultaLog

        agora = timezone.now()
        limite = agora - timedelta(hours=2)

        consultas_expiradas = cls.objects.filter(
            status=cls.STATUS_MARCADA,
            data_hora__lt=limite
        )

        for consulta in consultas_expiradas:
            with transaction.atomic():
                consulta.status = cls.STATUS_NAO_REALIZADA
                consulta.save(update_fields=['status', 'atualizado_em'])

                ConsultaLog.objects.create(
                    consulta=consulta,
                    usuario=None,
                    status_anterior=cls.STATUS_MARCADA,
                    status_novo=cls.STATUS_NAO_REALIZADA
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

    crm_medico = models.CharField(max_length=20, blank=True, null=True)
    descricao_receita = models.TextField(blank=True, null=True)
    data_geracao_receita = models.DateTimeField(blank=True, null=True)

    receita_pdf = models.FileField(
        upload_to='receitas/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"[{self.protocolo}] {self.agendamento}"


class ConsultaLog(models.Model):

    consulta = models.ForeignKey(
        AgendamentoConsulta,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    status_anterior = models.CharField(max_length=20)
    status_novo = models.CharField(max_length=20)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consulta} - {self.status_anterior} → {self.status_novo}"

