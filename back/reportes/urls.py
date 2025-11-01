"""
URLs   para el módulo reportes
"""
from core.urls import create_standard_urls
from .views import (ReporteViewSet, NotificacionViewSet, PlantillaCorreoViewSet,
                   EnvioLoteViewSet, RenderCorreoViewSet, VistaViewSet, ReportesViewSet)

app_name = 'reportes'

urlpatterns = create_standard_urls(app_name, [
    ('reportes', ReporteViewSet),
    ('notificaciones', NotificacionViewSet),
    ('plantillas', PlantillaCorreoViewSet),
    ('envios-lote', EnvioLoteViewSet),
    ('renders', RenderCorreoViewSet),
    ('vistas', VistaViewSet),
    ('dinamicos', ReportesViewSet, 'reportes-dinamicos'),
])