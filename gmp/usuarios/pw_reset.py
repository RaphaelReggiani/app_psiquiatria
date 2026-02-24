from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.utils.translation import gettext_lazy as _


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "gmp/pw_reset_complete.html"


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("E-mail"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "class": "block w-full rounded-md bg-white px-3 py-1.5 text-gray-900 outline outline-1 -outline-offset-1 outline-emerald-400 focus:outline-2 focus:outline-emerald-600 sm:text-sm",
                "placeholder": "Digite seu e-mail",
            }
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("Nova senha"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "block w-full rounded-md bg-white px-3 py-1.5 text-gray-900 outline outline-1 -outline-offset-1 outline-emerald-400 focus:outline-2 focus:outline-emerald-600 sm:text-sm",
                "placeholder": "Digite a nova senha",
            }
        ),
        help_text=_(
            "Sua senha deve atender aos seguintes critérios:<ul>"
            "<li>- Conter pelo menos 8 caracteres;</li>"
            "<li>- Não ser totalmente numérica.</li>"
            "</ul>"
        ),
    )
    new_password2 = forms.CharField(
        label=_("Confirme a senha"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "block w-full rounded-md bg-white px-3 py-1.5 text-gray-900 outline outline-1 -outline-offset-1 outline-emerald-400 focus:outline-2 focus:outline-emerald-600 sm:text-sm",
                "placeholder": "Confirme a nova senha",
            }
        ),
    )


class CustomPasswordResetView(PasswordResetView):
    template_name = "gmp/pw_reset.html"
    email_template_name = "gmp/pw_reset_email.html"
    subject_template_name = "gmp/pw_reset_subject.txt"
    success_url = "/pw_reset/done/"
    form_class = CustomPasswordResetForm


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "gmp/pw_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "gmp/pw_reset_confirm.html"
    success_url = "/login/"
    form_class = CustomSetPasswordForm
