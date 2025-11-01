"""
URLs   para el módulo personas
Usando utilidades centralizadas
"""
from core.urls import create_standard_urls
from .views import UsuarioViewSet, AgenteViewSet, AreaViewSet, RolViewSet, AsignacionRolViewSet

app_name = 'personas'

# Configuración simplificada usando utilidad centralizada
urlpatterns = create_standard_urls(app_name, [
    ('usuarios', UsuarioViewSet),
    ('agentes', AgenteViewSet),
    ('areas', AreaViewSet),
    ('roles', RolViewSet),
    ('asignaciones', AsignacionRolViewSet, 'asignaciones-rol'),
])
