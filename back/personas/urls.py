from django.urls import path
from . import views

app_name = 'personas'

urlpatterns = [
    # URLs para Agentes
    path('agentes/', views.AgenteListView.as_view(), name='agente-list'),
    path('agentes/<uuid:pk>/', views.AgenteDetailView.as_view(), name='agente-detail'),
    
    # URLs para Áreas
    path('areas/', views.AreaListView.as_view(), name='area-list'),
    path('areas/<uuid:pk>/', views.AreaDetailView.as_view(), name='area-detail'),
    
    # URLs para Roles
    path('roles/', views.RolListView.as_view(), name='rol-list'),
    path('roles/<uuid:pk>/', views.RolDetailView.as_view(), name='rol-detail'),
    
    # URLs para Cuentas de Acceso
    path('cuentas-acceso/', views.CuentaAccesoListView.as_view(), name='cuenta-acceso-list'),
    path('cuentas-acceso/<uuid:pk>/', views.CuentaAccesoDetailView.as_view(), name='cuenta-acceso-detail'),
]