"""
URLs   para el módulo guardias
"""
from core.urls import create_standard_urls
from .views import ModalidadViewSet, GuardiaViewSet, CuadroGuardiaViewSet, AsignacionGuardiaViewSet, FeriadoViewSet

app_name = 'guardias'

urlpatterns = create_standard_urls(app_name, [
    ('feriados', FeriadoViewSet, 'feriados'),
    ('modalidades', ModalidadViewSet, 'modalidad'),
    ('guardias', GuardiaViewSet, 'guardia'),
    ('cuadros', CuadroGuardiaViewSet, 'cuadro'),
    ('asignaciones', AsignacionGuardiaViewSet, 'asignacion'),
])
