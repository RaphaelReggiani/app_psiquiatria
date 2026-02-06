from django import forms
from django.utils import timezone
from django.conf import settings
from .models import Consulta, AgendamentoConsulta

User = settings.AUTH_USER_MODEL


class AgendamentoConsultaForm(forms.ModelForm):

    class Meta:
        model = AgendamentoConsulta
        fields = ['paciente', 'medico', 'data_hora']

        widgets = {
            'data_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            )
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        from gmp.usuarios.models import CustomUser

        self.fields['paciente'].queryset = CustomUser.objects.filter(role='paciente')
        self.fields['medico'].queryset = CustomUser.objects.filter(role='medico')
        self.fields['medico'].empty_label = "Selecione o médico"

        if user and user.role == 'paciente':
            self.fields.pop('paciente')

    def clean_data_hora(self):
        data_hora = self.cleaned_data['data_hora']

        minimo = timezone.now() + timezone.timedelta(hours=2)

        if data_hora < minimo:
            raise forms.ValidationError(
                "A consulta deve ser marcada com pelo menos 2 horas de antecedência."
            )

        return data_hora


    def clean_data_hora(self):
        data_hora = self.cleaned_data['data_hora']

        minimo = timezone.now() + timezone.timedelta(hours=2)

        if data_hora < minimo:
            raise forms.ValidationError(
                "A consulta deve ser marcada com pelo menos 2 horas de antecedência."
            )

        return data_hora


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

