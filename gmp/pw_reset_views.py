from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .pw_reset_forms import CustomPasswordResetForm, CustomSetPasswordForm

class CustomPasswordResetView(PasswordResetView):
    template_name = 'gmp/pw_reset.html'
    email_template_name = 'gmp/pw_reset_email.html'
    subject_template_name = 'gmp/pw_reset_subject.txt'
    success_url = '/pw_reset/done/'
    form_class = CustomPasswordResetForm

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'gmp/pw_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'gmp/pw_reset_confirm.html'
    success_url = '/login/'
    form_class = CustomSetPasswordForm

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'gmp/pw_reset_complete.html'