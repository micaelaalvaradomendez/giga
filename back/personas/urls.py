"""
URLs para el módulo personas
"""
from django.urls import path
from personas import views

urlpatterns = [
    # CRUD de agentes
    path('agentes/', views.agentes_list_create, name='agentes_list_create'),
    path('agentes/<int:pk>/', views.agente_detail, name='agente_detail'),
    
    # CRUD de áreas
    path('areas/', views.areas_list_create, name='areas_list_create'),
    path('areas/<int:pk>/', views.area_detail, name='area_detail'),
    
    # CRUD de roles
    path('roles/', views.roles_list_create, name='roles_list_create'),
    path('roles/<int:pk>/', views.rol_detail, name='rol_detail'),
    
    # Asignaciones de roles (para compatibilidad con frontend)
    path('asignaciones/', views.asignaciones_list_create, name='asignaciones_list_create'),
    path('asignaciones/<int:pk>/', views.asignacion_delete, name='asignacion_delete'),
]
