"""
URLs para el módulo personas
"""
from django.urls import path, include
from personas import views
from personas.auth_views import (
    login_view,
    logout_view, 
    check_session,
    recover_password,
    change_password,
    update_profile,
    update_email
)

# URLs de autenticación
auth_patterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('check-session/', check_session, name='check_session'),
    path('recover-password/', recover_password, name='recover_password'),
    path('change-password/', change_password, name='change_password'),
    path('update-profile/', update_profile, name='update_profile'),
    path('update-email/', update_email, name='update_email'),
]

# URLs de gestión de agentes
agentes_patterns = [
    path('', views.get_agentes, name='get_agentes'),
    path('create/', views.create_agente, name='create_agente'),
    path('<int:agente_id>/', views.get_agente, name='get_agente'),
    path('<int:agente_id>/update/', views.update_agente, name='update_agente'),
    path('<int:agente_id>/delete/', views.delete_agente, name='delete_agente'),
]

# URLs de áreas y roles
catalog_patterns = [
    path('areas/', views.get_areas, name='get_areas'),
    path('roles/', views.get_roles, name='get_roles'),
]

# URLs de asignaciones
asignaciones_patterns = [
    path('', views.get_asignaciones, name='get_asignaciones'),
    path('create/', views.create_asignacion, name='create_asignacion'),
    path('<int:asignacion_id>/delete/', views.delete_asignacion, name='delete_asignacion'),
]

# URLs de parámetros del sistema
parametros_patterns = [
    # Gestión de áreas
    path('areas/create/', views.create_area, name='create_area'),
    path('areas/<int:area_id>/update/', views.update_area, name='update_area'),
    path('areas/<int:area_id>/delete/', views.delete_area, name='delete_area'),
    path('areas/<int:area_id>/schedule/', views.update_area_schedule, name='update_area_schedule'),
    
    # Gestión de agrupaciones organizacionales
    path('agrupaciones/', views.get_agrupaciones, name='get_agrupaciones'),
    path('agrupaciones/create/', views.create_agrupacion, name='create_agrupacion'),
    path('agrupaciones/<int:agrupacion_id>/update/', views.update_agrupacion, name='update_agrupacion'),
    path('agrupaciones/<int:agrupacion_id>/delete/', views.delete_agrupacion, name='delete_agrupacion'),
    path('agrupaciones/schedule/', views.update_agrupacion_schedule, name='update_agrupacion_schedule'),
    path('agrupaciones/rename/', views.rename_agrupacion, name='rename_agrupacion'),
]

# URLs de organigrama
organigrama_patterns = [
    path('', views.get_organigrama, name='get_organigrama'),
    path('save/', views.save_organigrama, name='save_organigrama'),
    path('historial/', views.get_organigrama_historial, name='get_organigrama_historial'),
    path('<int:organigrama_id>/restore/', views.restore_organigrama, name='restore_organigrama'),
]

# Import temporal para testing
from .test_views import get_agentes_test

# URLs temporales para testing
test_patterns = [
    path('agentes-test/', get_agentes_test, name='get_agentes_test'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('agentes/', include(agentes_patterns)),
    path('catalogs/', include(catalog_patterns)),
    path('asignaciones/', include(asignaciones_patterns)),
    path('parametros/', include(parametros_patterns)),
    path('organigrama/', include(organigrama_patterns)),
    path('test/', include(test_patterns)),
]
