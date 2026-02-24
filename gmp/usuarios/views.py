from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from gmp.usuarios.constants import (
    MSG_CONTA_CRIADA_SUCESSO,
    MSG_LOGIN_REALIZADO_SUCESSO,
    MSG_LOGOUT_REALIZADO_SUCESSO,
    MSG_PERFIL_ATUALIZADO_SUCESSO,
    MSG_USUARIO_CRIADO_SUCESSO,
    URL_HOME,
    URL_LOGIN,
    URL_PERFIL_USUARIO,
    URL_STAFF,
)

from .decorators import medico_or_superadmin_required
from .exceptions import UserDomainException
from .forms import (
    CustomAuthenticationForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from .services import UserService


def home(request):
    return render(request, "gmp/home.html")


def cadastro_view(request):

    if request.method == "POST":
        signup_form = CustomUserCreationForm(
            request.POST,
            request.FILES,
            request_user=request.user if request.user.is_authenticated else None,
        )

        if signup_form.is_valid():
            try:
                UserService.create_user(
                    data=signup_form.cleaned_data, request_user=request.user
                )

                messages.success(request, MSG_CONTA_CRIADA_SUCESSO)
                return redirect(URL_LOGIN)

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        signup_form = CustomUserCreationForm(
            request_user=request.user if request.user.is_authenticated else None
        )

    return render(request, "gmp/cadastro.html", {"signup_form": signup_form})


def login_view(request):

    if request.method == "POST":
        login_form = CustomAuthenticationForm(data=request.POST)

        if login_form.is_valid():
            try:
                user = UserService.authenticate_user(
                    request=request,
                    email=login_form.cleaned_data.get("email"),
                    password=login_form.cleaned_data.get("password"),
                )

                login(request, user)
                messages.success(request, MSG_LOGIN_REALIZADO_SUCESSO)
                return redirect(URL_HOME)

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        login_form = CustomAuthenticationForm()

    return render(request, "gmp/login.html", {"login_form": login_form})


@login_required(login_url=URL_LOGIN)
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, MSG_LOGOUT_REALIZADO_SUCESSO)
    return redirect(URL_HOME)


@login_required(login_url=URL_LOGIN)
def profile_view(request):

    if request.method == "POST":
        form = CustomUserChangeForm(
            request.POST,
            request.FILES,
            instance=request.user,
            request_user=request.user,
        )

        if form.is_valid():
            try:
                UserService.update_user(
                    instance=request.user,
                    data=form.cleaned_data,
                    request_user=request.user,
                )

                messages.success(request, MSG_PERFIL_ATUALIZADO_SUCESSO)
                return redirect(URL_PERFIL_USUARIO)

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        form = CustomUserChangeForm(instance=request.user, request_user=request.user)

    return render(request, "gmp/perfil_usuario.html", {"edit_form": form})


@medico_or_superadmin_required
def staff_user_create(request):

    if request.method == "POST":
        form = CustomUserCreationForm(
            request.POST, request.FILES, request_user=request.user
        )

        if form.is_valid():
            try:
                UserService.create_user(
                    data=form.cleaned_data, request_user=request.user
                )

                messages.success(request, MSG_USUARIO_CRIADO_SUCESSO)
                return redirect(URL_STAFF)

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        form = CustomUserCreationForm(request_user=request.user)

    return render(request, "gmp/staff.html", {"signup_form": form})

