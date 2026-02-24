from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from gmp.usuarios.constants import (
    LABEL_CONFIRMAR_SENHA,
    LABEL_EMAIL,
    LABEL_FOTO_PERFIL,
    LABEL_IDADE,
    LABEL_NOME,
    LABEL_ORIGEM,
    LABEL_PACIENTE,
    LABEL_QUEIXA,
    LABEL_ROLE,
    LABEL_SENHA,
    LABEL_TELEFONE,
    MSG_VALIDATION_ERROR_CAMPOS_OBRIGATORIOS,
)
from gmp.usuarios.models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label=LABEL_SENHA,
        widget=forms.PasswordInput,
    )

    password2 = forms.CharField(label=LABEL_CONFIRMAR_SENHA, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [
            "nome",
            "email",
            "idade",
            "queixa",
            "role",
            "telefone",
            "origem",
            "foto_perfil",
        ]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        self.fields["nome"].label = LABEL_NOME
        self.fields["email"].label = LABEL_EMAIL
        self.fields["idade"].label = LABEL_IDADE
        self.fields["queixa"].label = LABEL_QUEIXA
        self.fields["role"].label = LABEL_ROLE
        self.fields["telefone"].label = LABEL_TELEFONE
        self.fields["origem"].label = LABEL_ORIGEM
        self.fields["foto_perfil"].label = LABEL_FOTO_PERFIL

        if not self.request_user:
            self.fields.pop("role")
            return

        if self.request_user.role == CustomUser.ROLE_MEDICO:
            self.fields["role"].choices = [(CustomUser.ROLE_PACIENTE, LABEL_PACIENTE)]

        if self.request_user.role == CustomUser.ROLE_SUPERADM:
            self.fields["role"].choices = CustomUser.ROLE_CHOICES


class CustomAuthenticationForm(forms.Form):

    email = forms.EmailField(label=LABEL_EMAIL)
    password = forms.CharField(label=LABEL_SENHA, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            raise forms.ValidationError(MSG_VALIDATION_ERROR_CAMPOS_OBRIGATORIOS)

        return cleaned_data


class CustomUserChangeForm(UserChangeForm):

    password = None

    class Meta:
        model = CustomUser
        fields = [
            "nome",
            "email",
            "idade",
            "queixa",
            "role",
            "telefone",
            "origem",
            "foto_perfil",
        ]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        if not self.request_user:
            self.fields.pop("role", None)
            return

        if self.request_user.role == CustomUser.ROLE_PACIENTE:
            self.fields.pop("role", None)
            return

        if self.request_user.role == CustomUser.ROLE_MEDICO:
            self.fields.pop("role", None)
            self.fields.pop("idade", None)
            self.fields.pop("queixa", None)
            return

        if self.request_user.role == CustomUser.ROLE_SUPERADM:
            self.fields["role"].choices = CustomUser.ROLE_CHOICES

    def clean_role(self):
        if not self.request_user:
            return self.instance.role

        if self.request_user.role != CustomUser.ROLE_SUPERADM:
            return self.instance.role

        return self.cleaned_data.get("role")
