from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, AuthenticationForm,
    PasswordResetForm, SetPasswordForm)
from django.contrib.auth import authenticate
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label=_("Senha"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_(
            'Sua senha deve atender aos seguintes critérios:<ul>'
            '<li>- Conter pelo menos 8 caracteres;</li>'
            '<li>- Não ser totalmente numérica.</li>'
            '</ul>'
        ),
    )
    password2 = forms.CharField(
        label=_("Confirme a senha"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_("Digite a senha novamente."),
    )

    class Meta:
        model = CustomUser
        fields = ['nome','email', 'role', 'telefone', 'origem', 'foto_perfil']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        self.fields['nome'].label = "Nome"
        self.fields['email'].label = "E-mail"
        self.fields['role'].label = "Perfil"
        self.fields['telefone'].label = "Telefone"
        self.fields['origem'].label = "Estado de origem"
        self.fields['foto_perfil'].label = "Foto"

        if self.request_user is None:
            self.fields.pop('role')
            return

        if self.request_user.role == 'medico':
            self.fields['role'].choices = [
                ('paciente', 'Paciente'),
            ]
        elif self.request_user.role == 'superadm':
            self.fields['role'].choices = [
                ('paciente', 'Paciente'),
                ('medico', 'Médico'),
                ('superadm', 'Super Administrador'),
            ]

        self.fields['telefone'].widget.attrs.update({
            'placeholder': '(011) XXXXX-XXXX',
            'class': 'telefone-input block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-blue-400 placeholder:text-gray-900 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-blue-600 sm:text-sm'
        })


class CustomAuthenticationForm(forms.Form):

    email = forms.EmailField(label="E-mail")
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput
    )

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
                raise forms.ValidationError("E-mail ou senha inválido(s).")

        return self.cleaned_data

    def get_user(self):
        return self.user

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'widgets/custom_clearable_file_input.html'


class CustomUserChangeForm(UserChangeForm):

    password = None

    class Meta:
        model = CustomUser
        fields = [
            'nome',
            'email',
            'role',
            'telefone',
            'origem',
            'foto_perfil'
        ]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        if self.request_user is None:
            self.fields.pop('role')
            return

        if self.request_user.role == 'medico':
            self.fields['role'].choices = [
                ('paciente', 'Paciente'),
            ]

        if self.request_user.role == 'superadm':
            self.fields['role'].choices = [
                ('paciente', 'Paciente'),
                ('medico', 'Médico'),
                ('superadm', 'Super Administrador')
            ]

    def clean_role(self):
        role = self.cleaned_data.get('role')

        if not self.request_user:
            return self.instance.role

        if self.request_user.role == 'medico' and not role == 'superadm':
            raise forms.ValidationError("Médico não pode definir superadm.")

        return role
