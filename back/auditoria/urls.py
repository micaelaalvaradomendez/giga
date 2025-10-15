from django.urls import path
from . import views

app_name = 'auditoria'

urlpatterns = [
    # URLs para Parámetros de Control Horario
    path('parametros/', views.ParametrosControlHorarioListView.as_view(), name='parametros-list'),
    path('parametros/<uuid:pk>/', views.ParametrosControlHorarioDetailView.as_view(), name='parametros-detail'),
    
    # URLs para Registros de Auditoría
    path('registros/', views.RegistroAuditoriaListView.as_view(), name='registro-list'),
    path('registros/<uuid:pk>/', views.RegistroAuditoriaDetailView.as_view(), name='registro-detail'),
]