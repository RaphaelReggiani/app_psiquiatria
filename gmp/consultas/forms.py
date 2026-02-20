from django import forms
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.conf import settings
from .constants import LIMITE_DIARIO_MEDICO, ANTECEDENCIA_MINIMA_HORAS, HORA_INICIO_ATENDIMENTO, HORA_FIM_ATENDIMENTO, INTERVALO_MINUTOS, DIA_UTIL_FINAL, FORMATO_HORA

from gmp.usuarios.models import CustomUser

from .models import Consulta, AgendamentoConsulta

User = settings.AUTH_USER_MODEL


HORARIOS_ATENDIMENTO = [
    time(h, m)
    for h in range(HORA_INICIO_ATENDIMENTO, HORA_FIM_ATENDIMENTO)
    for m in INTERVALO_MINUTOS
]

class AgendamentoConsultaForm(forms.ModelForm):

    paciente = forms.ModelChoiceField(
        queryset=None,
        required=False
    )

    data = forms.DateField(
        label="Data da Consulta",
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }
        )
    )

    hora = forms.ChoiceField(
        label="Horário",
        choices=[(h.strftime(FORMATO_HORA), h.strftime(FORMATO_HORA)) for h in HORARIOS_ATENDIMENTO]
    )

    class Meta:
        model = AgendamentoConsulta
        fields = ['paciente', 'medico', 'data', 'hora']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


        self.fields['paciente'].queryset = CustomUser.objects.filter(role=CustomUser.ROLE_PACIENTE)
        self.fields['medico'].queryset = CustomUser.objects.filter(role=CustomUser.ROLE_MEDICO)
        self.fields['medico'].empty_label = "Selecione o médico"

        if self.user and self.user.role == CustomUser.ROLE_PACIENTE:
            self.fields['paciente'].widget = forms.HiddenInput()

    def clean(self):

        cleaned = super().clean()

        if self.user and self.user.role == CustomUser.ROLE_MEDICO:
            raise forms.ValidationError(
                "Médicos não podem marcar consultas."
            )

        data = cleaned.get('data')
        hora_str = cleaned.get('hora')
        medico = cleaned.get('medico')
        paciente = cleaned.get('paciente')

        if not paciente and self.user and self.user.role == CustomUser.ROLE_PACIENTE:
            paciente = self.user

        if not data or not hora_str or not medico:
            raise forms.ValidationError("Preencha todos os campos.")

        if data.weekday() > DIA_UTIL_FINAL:
            raise forms.ValidationError(
                "Consultas não são permitidas aos finais de semana."
            )

        total = AgendamentoConsulta.objects.filter(
            medico=medico,
            data_hora__date=data,
            status=AgendamentoConsulta.STATUS_MARCADA
        ).count()

        if total >= LIMITE_DIARIO_MEDICO:
            raise forms.ValidationError(
                "Este médico atingiu o limite de consultas para este dia."
            )
        
        if AgendamentoConsulta.objects.filter(
            paciente=paciente,
            data_hora__gt=timezone.now(),
            status=AgendamentoConsulta.STATUS_MARCADA
        ).exists():
            raise forms.ValidationError(
                "Você já possui uma consulta futura marcada."
            )

        hora = datetime.strptime(hora_str, FORMATO_HORA).time()
        data_hora = timezone.localtime(timezone.make_aware(datetime.combine(data, hora)))

        agora = timezone.now()
        minimo = agora + timedelta(hours=ANTECEDENCIA_MINIMA_HORAS)
        if data_hora < minimo:
            raise forms.ValidationError(
                f"Horário inválido. Escolha um horário futuro com pelo menos {ANTECEDENCIA_MINIMA_HORAS} horas de antecedência."
            )

        if AgendamentoConsulta.objects.filter(
            medico=medico,
            data_hora=data_hora,
            status=AgendamentoConsulta.STATUS_MARCADA
        ).exists():
            raise forms.ValidationError(
                "Este horário já está ocupado."
            )

        if AgendamentoConsulta.objects.filter(
            paciente=paciente,
            data_hora=data_hora,
            status=AgendamentoConsulta.STATUS_MARCADA
        ).exists():
            raise forms.ValidationError(
                "Você já possui uma consulta marcada neste horário."
            )

        cleaned['data_hora'] = data_hora
        cleaned['paciente'] = paciente

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.data_hora = self.cleaned_data['data_hora']
        instance.paciente = self.cleaned_data['paciente']

        if commit:
            instance.save()

        return instance


class ConsultaForm(forms.ModelForm):

    class Meta:
        model = Consulta
        fields = [
            'condicao_paciente',
            'descricao',
            'receita',
            'arquivo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['condicao_paciente'].label = "Condição do Paciente"
        self.fields['descricao'].label = "Descrição da Consulta"
        self.fields['receita'].label = "Receita"
        self.fields['arquivo'].label = "Arquivo"





