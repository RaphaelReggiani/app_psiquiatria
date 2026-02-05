from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from gmp.usuarios.models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        help_text="""
        <ul>
            <li>Mínimo de 8 caracteres</li>
            <li>Não pode ser totalmente numérica</li>
        </ul>
        """
    )

    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ['nome', 'email', 'idade', 'queixa', 'role', 'telefone', 'origem', 'foto_perfil']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        self.fields['nome'].label = "Nome"
        self.fields['email'].label = "E-mail"
        self.fields['idade'].label = "Idade"
        self.fields['queixa'].label = "Queixa"
        self.fields['role'].label = "Perfil"
        self.fields['telefone'].label = "Telefone"
        self.fields['origem'].label = "Estado"
        self.fields['foto_perfil'].label = "Foto"

        if not self.request_user:
            self.fields.pop('role')
            return

        if self.request_user.role == 'medico':
            self.fields['role'].choices = [('paciente', 'Paciente')]

        if self.request_user.role == 'superadm':
            self.fields['role'].choices = [
                ('paciente', 'Paciente'),
                ('medico', 'Médico'),
                ('superadm', 'Super Administrador')
            ]


class CustomAuthenticationForm(forms.Form):

    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user = authenticate(
                self.request,
                username=email,
                password=password
            )

            if self.user is None:
                raise forms.ValidationError("E-mail ou senha inválidos.")

        return self.cleaned_data

    def get_user(self):
        return self.user


class CustomUserChangeForm(UserChangeForm):

    password = None

    class Meta:
        model = CustomUser
        fields = ['nome', 'email', 'idade', 'queixa', 'role', 'telefone', 'origem', 'foto_perfil']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        if self.request_user.role == 'paciente':
            self.fields.pop('role')
            return

        if self.request_user.role == 'medico':
            self.fields.pop('role')
            self.fields.pop('idade')
            self.fields.pop('queixa')
            return

        if self.request_user.role == 'superadm':
            self.fields['role'].choices = [
                ('paciente', 'Paciente'),
                ('medico', 'Médico'),
                ('superadm', 'Super Administrador')
            ]

    def clean_role(self):
        if not self.request_user:
            return self.instance.role

        if self.request_user.role != 'superadm':
            return self.instance.role

        return self.cleaned_data.get('role')

