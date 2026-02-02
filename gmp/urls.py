from django.urls import path, include
from . import views

urlpatterns = [

    # path('tickets/', include('helpdesk.tickets.ticket_urls')),

    # HOME

    path('home/', views.home, name="home"),

    # URLs - Usuário


    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil_usuario/', views.profile_view, name='perfil_usuario'),
    path('staff/', views.staff_user_create, name='staff'),
    path('perfil_usuario/login_required/', views.login_required_view, name='login_required'),

    # Reset de senha

    # path('forgot-password/', password_views.CustomPasswordResetView.as_view(), name='forgot-password'),
    # path('forgot-password/done/', password_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', password_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset-complete/', password_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
