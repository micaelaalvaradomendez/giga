"""
URLs para el módulo guardias
"""
from django.urls import path
from core.urls import create_standard_urls
from .views import (
    ModalidadViewSet,
    GuardiaViewSet,
    CuadroGuardiaViewSet,
    AsignacionGuardiaViewSet,
    PlanificarCronogramaView,
)

app_name = 'guardias'

urlpatterns = create_standard_urls(app_name, [
    ('modalidades', ModalidadViewSet, 'modalidad'),
    ('guardias', GuardiaViewSet, 'guardia'),
    ('cuadros', CuadroGuardiaViewSet, 'cuadro'),
    ('asignaciones', AsignacionGuardiaViewSet, 'asignacion'),
    ('planificar', PlanificarCronogramaView, 'planificar'),
])
