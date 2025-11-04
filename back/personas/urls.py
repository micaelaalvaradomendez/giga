"""
URLs para el módulo personas
Usando utilidades centralizadas
"""
from django.urls import path
from core.urls import create_standard_urls
from .views import (
    UsuarioViewSet,
    AgenteViewSet,
    AreaViewSet,
    RolViewSet,
    AsignacionRolViewSet,
    subordinados,
)

app_name = 'personas'

# Configuración simplificada usando utilidad centralizada
urlpatterns = create_standard_urls(app_name, [
    ('usuarios', UsuarioViewSet),
    ('agentes', AgenteViewSet),
    ('areas', AreaViewSet),
    ('roles', RolViewSet),
    ('asignaciones', AsignacionRolViewSet, 'asignaciones-rol'),
    ('subordinados', AsignacionRolViewSet, 'asignaciones-rol'),
])

urlpatterns += [
    path('subordinados/', subordinados, name='api_subordinados'),
]

