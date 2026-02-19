from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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

        if self.request_user.role == CustomUser.ROLE_MEDICO:
            self.fields['role'].choices = [(CustomUser.ROLE_PACIENTE, 'Paciente')]

        if self.request_user.role == CustomUser.ROLE_SUPERADM:
            self.fields['role'].choices = CustomUser.ROLE_CHOICES


class CustomAuthenticationForm(forms.Form):

    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            raise forms.ValidationError("Preencha todos os campos.")

        return cleaned_data


class CustomUserChangeForm(UserChangeForm):

    password = None

    class Meta:
        model = CustomUser
        fields = ['nome', 'email', 'idade', 'queixa', 'role', 'telefone', 'origem', 'foto_perfil']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        if not self.request_user:
            self.fields.pop('role', None)
            return

        if self.request_user.role == CustomUser.ROLE_PACIENTE:
            self.fields.pop('role', None)
            return

        if self.request_user.role == CustomUser.ROLE_MEDICO:
            self.fields.pop('role', None)
            self.fields.pop('idade', None)
            self.fields.pop('queixa', None)
            return

        if self.request_user.role == CustomUser.ROLE_SUPERADM:
            self.fields['role'].choices = CustomUser.ROLE_CHOICES

    def clean_role(self):
        if not self.request_user:
            return self.instance.role

        if self.request_user.role != CustomUser.ROLE_SUPERADM:
            return self.instance.role

        return self.cleaned_data.get('role')

