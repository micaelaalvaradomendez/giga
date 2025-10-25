"""
URLs   para el módulo asistencia
"""
from core.urls import create_standard_urls
from .views import AsistenciaViewSet, MarcaViewSet, LicenciaViewSet, NovedadViewSet, AdjuntoViewSet, TipoLicenciaViewSet

app_name = 'asistencia'

urlpatterns = create_standard_urls(app_name, [
    ('asistencias', AsistenciaViewSet),
    ('marcas', MarcaViewSet),
    ('licencias', LicenciaViewSet),
    ('novedades', NovedadViewSet),
    ('adjuntos', AdjuntoViewSet),
    ('tipos-licencia', TipoLicenciaViewSet),
])