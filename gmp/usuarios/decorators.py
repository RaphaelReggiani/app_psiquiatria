from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .constants import MSG_ERRO_ACESSO_RESTRITO, URL_HOME, URL_LOGIN
from .models import CustomUser


def role_required(*allowed_roles):

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.role not in allowed_roles:
                messages.error(request, MSG_ERRO_ACESSO_RESTRITO)
                return redirect(URL_HOME)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def superadmin_required(view_func):
    return login_required(login_url=URL_LOGIN)(
        role_required(CustomUser.ROLE_SUPERADM)(view_func)
    )


def medico_or_superadmin_required(view_func):
    return login_required(login_url=URL_LOGIN)(
        role_required(CustomUser.ROLE_MEDICO, CustomUser.ROLE_SUPERADM)(view_func)
    )
