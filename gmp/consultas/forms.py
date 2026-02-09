from django import forms
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.conf import settings

from .models import Consulta, AgendamentoConsulta

User = settings.AUTH_USER_MODEL


HORARIOS_ATENDIMENTO = [
    time(h, m)
    for h in range(8, 18)
    for m in (0, 30)
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
        choices=[(h.strftime('%H:%M'), h.strftime('%H:%M')) for h in HORARIOS_ATENDIMENTO]
    )

    class Meta:
        model = AgendamentoConsulta
        fields = ['paciente', 'medico', 'data', 'hora']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        from gmp.usuarios.models import CustomUser

        self.fields['paciente'].queryset = CustomUser.objects.filter(role='paciente')
        self.fields['medico'].queryset = CustomUser.objects.filter(role='medico')
        self.fields['medico'].empty_label = "Selecione o médico"

        if self.user and self.user.role == 'paciente':
            self.fields['paciente'].widget = forms.HiddenInput()

    def clean(self):

        cleaned = super().clean()

        data = cleaned.get('data')
        hora_str = cleaned.get('hora')
        medico = cleaned.get('medico')
        paciente = cleaned.get('paciente')

        if not data or not hora_str or not medico:
            raise forms.ValidationError("Preencha todos os campos.")

        if data.weekday() >= 5:
            raise forms.ValidationError(
                "Consultas não são permitidas aos finais de semana."
            )
        
        limite_diario = 10

        total = AgendamentoConsulta.objects.filter(
            medico=medico,
            data_hora__date=data,
            status='marcada'
        ).count()

        if total >= limite_diario:
            raise forms.ValidationError(
                "Este médico atingiu o limite de consultas para este dia."
            )
        
        if AgendamentoConsulta.objects.filter(
            paciente=paciente,
            data_hora__gt=timezone.now(),
            status='marcada'
        ).exists():
            raise forms.ValidationError(
                "Você já possui uma consulta futura marcada."
            )

        hora = datetime.strptime(hora_str, "%H:%M").time()
        data_hora = timezone.make_aware(datetime.combine(data, hora))

        agora = timezone.now()
        minimo = agora + timedelta(hours=2)
        if data_hora < minimo:
            raise forms.ValidationError(
                "Horário inválido. Escolha um horário futuro com pelo menos 2 horas de antecedência."
            )

        if AgendamentoConsulta.objects.filter(
            medico=medico,
            data_hora=data_hora,
            status='marcada'
        ).exists():
            raise forms.ValidationError(
                "Este horário já está ocupado."
            )

        if AgendamentoConsulta.objects.filter(
            paciente=paciente,
            data_hora=data_hora,
            status='marcada'
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





