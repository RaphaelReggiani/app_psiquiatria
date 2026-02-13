from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserChangeForm
)


def home(request):
    return render(request, 'gmp/home.html')

def cadastro_view(request):

    signup_form = CustomUserCreationForm(
        request_user=request.user if request.user.is_authenticated else None
    )

    if request.method == 'POST':

        signup_form = CustomUserCreationForm(
            request.POST,
            request.FILES,
            request_user=request.user if request.user.is_authenticated else None
        )

        if signup_form.is_valid():
            user = signup_form.save(commit=False)

            if not request.user.is_authenticated:
                user.role = 'paciente'

            user.save()

            messages.success(request, "Conta criada com sucesso.")
            return redirect('login')

    return render(request, 'gmp/cadastro.html', {
        'signup_form': signup_form
    })


def login_view(request):
    login_form = CustomAuthenticationForm(request=request)

    if request.method == 'POST':
        login_form = CustomAuthenticationForm(
            request=request,
            data=request.POST
        )

        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, "Login realizado com sucesso.")
            return redirect('home')

        messages.error(request, "E-mail ou senha inválido(s).")

    return render(request, 'gmp/login.html', {
        'login_form': login_form
    })


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Você deslogou.")
    return redirect('home')


def login_required_view(request):
    return render(request, 'gmp/login_required.html')


@login_required(login_url='login_required')
def profile_view(request):

    if request.method == 'POST':
        form = CustomUserChangeForm(
            request.POST,
            request.FILES,
            instance=request.user,
            request_user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado.")
            return redirect('perfil_usuario')

    else:
        form = CustomUserChangeForm(
            instance=request.user,
            request_user=request.user
        )

    return render(request, 'gmp/perfil_usuario.html', {'edit_form': form})


def superadmin_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'superadm':
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def medico_or_superadmin_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        if request.user.role not in ['medico', 'superadm']:
            raise PermissionDenied

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
            form.save()
            messages.success(request, "Usuário criado com sucesso.")
            return redirect('staff')

    else:
        form = CustomUserCreationForm(request_user=request.user)

    return render(request, 'gmp/staff.html', {
        'signup_form': form
    })
