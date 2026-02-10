from django.urls import path
from . import views

urlpatterns = [

    path('marcar/', views.marcar_consulta, name='marcar_consulta'),
    path('agenda/', views.agenda_medico, name='agenda_medico'),
    path('minhas/', views.minhas_consultas, name='minhas_consultas'),
    path('historico/<int:paciente_id>/', views.historico_paciente, name='historico_paciente'),
    path('cadastrar/<int:agendamento_id>/', views.cadastrar_consulta, name='cadastrar_consulta'),
    path('horarios-disponiveis/', views.horarios_disponiveis, name='horarios_disponiveis'),
    path('cancelar/<int:consulta_id>/',views.cancelar_consulta,name='cancelar_consulta'),
]
