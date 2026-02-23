from django import forms
from django.utils import timezone
from datetime import (
    datetime, 
    time, 
    timedelta,
)

from gmp.usuarios.models import CustomUser

from .models import (
    Consulta, 
    AgendamentoConsulta,
)

from gmp.consultas.constants import (
    LIMITE_DIARIO_MEDICO, 
    ANTECEDENCIA_MINIMA_HORAS, 
    HORA_INICIO_ATENDIMENTO, 
    HORA_FIM_ATENDIMENTO, 
    INTERVALO_MINUTOS, 
    DIA_UTIL_FINAL, 
    FORMATO_HORA,
    LABEL_CONDICAO_PACIENTE,
    LABEL_DESCRICAO_CONSULTA,
    LABEL_RECEITA,
    LABEL_ARQUIVO,
    LABEL_SELECIONE_MEDICO,
    LABEL_DATA_DA_CONSULTA,
    LABEL_HORARIO,
    MSG_ERRO_MEDICO_NAO_PODE_MARCAR,
    MSG_ERRO_PREENCHER_TODOS_CAMPOS,
    MSG_ERRO_FINAL_DE_SEMANA,
    MSG_ERRO_LIMITE_DIARIO_MEDICO,
    MSG_ERRO_JA_POSSUI_CONSULTA_FUTURA,
    MSG_ERRO_ANTECEDENCIA_MINIMA,
    MSG_ERRO_HORARIO_OCUPADO,
    MSG_ERRO_JA_POSSUI_CONSULTA_NO_HORARIO,
)

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
        label= LABEL_DATA_DA_CONSULTA,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }
        )
    )

    hora = forms.ChoiceField(
        label= LABEL_HORARIO,
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
        self.fields['medico'].empty_label = LABEL_SELECIONE_MEDICO

        if self.user and self.user.role == CustomUser.ROLE_PACIENTE:
            self.fields['paciente'].widget = forms.HiddenInput()

    def clean(self):

        cleaned = super().clean()

        if self.user and self.user.role == CustomUser.ROLE_MEDICO:
            raise forms.ValidationError(MSG_ERRO_MEDICO_NAO_PODE_MARCAR)

        data = cleaned.get('data')
        hora_str = cleaned.get('hora')
        medico = cleaned.get('medico')
        paciente = cleaned.get('paciente')

        if not paciente and self.user and self.user.role == CustomUser.ROLE_PACIENTE:
            paciente = self.user

        if not data or not hora_str or not medico:
            raise forms.ValidationError(MSG_ERRO_PREENCHER_TODOS_CAMPOS)

        if data.weekday() > DIA_UTIL_FINAL:
            raise forms.ValidationError(MSG_ERRO_FINAL_DE_SEMANA)

        total = AgendamentoConsulta.objects.filter(
            medico=medico,
            data_hora__date=data,
            status=AgendamentoConsulta.STATUS_MARCADA
        ).count()

        if total >= LIMITE_DIARIO_MEDICO:
            raise forms.ValidationError(MSG_ERRO_LIMITE_DIARIO_MEDICO)
        
        if AgendamentoConsulta.objects.filter(
            paciente=paciente,
            data_hora__gt=timezone.now(),
            status=AgendamentoConsulta.STATUS_MARCADA
        ).exists():
            raise forms.ValidationError(MSG_ERRO_JA_POSSUI_CONSULTA_FUTURA)

        hora = datetime.strptime(hora_str, FORMATO_HORA).time()
        data_hora = data_hora = timezone.make_aware(datetime.combine(data, hora))

        agora = timezone.now()
        minimo = agora + timedelta(hours=ANTECEDENCIA_MINIMA_HORAS)
        if data_hora < minimo:
            raise forms.ValidationError(MSG_ERRO_ANTECEDENCIA_MINIMA.format(horas=ANTECEDENCIA_MINIMA_HORAS))

        if AgendamentoConsulta.objects.filter(
            medico=medico,
            data_hora=data_hora,
            status=AgendamentoConsulta.STATUS_MARCADA
        ).exists():
            raise forms.ValidationError(MSG_ERRO_HORARIO_OCUPADO)

        if AgendamentoConsulta.objects.filter(
            paciente=paciente,
            data_hora=data_hora,
            status=AgendamentoConsulta.STATUS_MARCADA
        ).exists():
            raise forms.ValidationError(MSG_ERRO_JA_POSSUI_CONSULTA_NO_HORARIO)

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

        self.fields['condicao_paciente'].label = LABEL_CONDICAO_PACIENTE
        self.fields['descricao'].label = LABEL_DESCRICAO_CONSULTA
        self.fields['receita'].label = LABEL_RECEITA
        self.fields['arquivo'].label = LABEL_ARQUIVO




