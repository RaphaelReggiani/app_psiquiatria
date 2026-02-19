from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import CustomUser
from .services import UserService
from .exceptions import UserDomainException
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserChangeForm
)
from functools import wraps


def home(request):
    return render(request, 'gmp/home.html')


def cadastro_view(request):

    if request.method == 'POST':
        signup_form = CustomUserCreationForm(
            request.POST,
            request.FILES,
            request_user=request.user if request.user.is_authenticated else None
        )

        if signup_form.is_valid():
            try:
                UserService.create_user(
                    data=signup_form.cleaned_data,
                    request_user=request.user
                )

                messages.success(request, "Conta criada com sucesso.")
                return redirect('login')

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        signup_form = CustomUserCreationForm(
            request_user=request.user if request.user.is_authenticated else None
        )

    return render(request, 'gmp/cadastro.html', {
        'signup_form': signup_form
    })


def login_view(request):

    if request.method == 'POST':
        login_form = CustomAuthenticationForm(
            request=request,
            data=request.POST
        )

        if login_form.is_valid():
            try:
                user = UserService.authenticate_user(
                    request=request,
                    email=login_form.cleaned_data.get("email"),
                    password=login_form.cleaned_data.get("password"),
                )

                login(request, user)
                messages.success(request, "Login realizado com sucesso.")
                return redirect('home')

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        login_form = CustomAuthenticationForm(request=request)

    return render(request, 'gmp/login.html', {
        'login_form': login_form
    })


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Você deslogou.")
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):

    if request.method == 'POST':
        form = CustomUserChangeForm(
            request.POST,
            request.FILES,
            instance=request.user,
            request_user=request.user
        )

        if form.is_valid():
            try:
                UserService.update_user(
                    instance=request.user,
                    data=form.cleaned_data,
                    request_user=request.user
                )

                messages.success(request, "Perfil atualizado.")
                return redirect('perfil_usuario')

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        form = CustomUserChangeForm(
            instance=request.user,
            request_user=request.user
        )

    return render(request, 'gmp/perfil_usuario.html', {
        'edit_form': form
    })


def superadmin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != CustomUser.ROLE_SUPERADM:
            messages.error(request, "Acesso restrito.")
            return redirect('home')
        return view(request, *args, **kwargs)
    return wrapper


def medico_or_superadmin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Você precisa estar logado.")
            return redirect('login')

        if request.user.role not in [
            CustomUser.ROLE_MEDICO,
            CustomUser.ROLE_SUPERADM
        ]:
            messages.error(request, "Acesso restrito.")
            return redirect('home')

        return view(request, *args, **kwargs)
    return wrapper


@medico_or_superadmin_required
def staff_user_create(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(
            request.POST,
            request.FILES,
            request_user=request.user
        )

        if form.is_valid():
            try:
                UserService.create_user(
                    data=form.cleaned_data,
                    request_user=request.user
                )

                messages.success(request, "Usuário criado com sucesso.")
                return redirect('staff')

            except UserDomainException as e:
                messages.error(request, str(e))

    else:
        form = CustomUserCreationForm(request_user=request.user)

    return render(request, 'gmp/staff.html', {
        'signup_form': form
    })

