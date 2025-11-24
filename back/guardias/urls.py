"""
URLs para el módulo guardias - Fase 1 implementación cronogramas
"""
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import (
    CronogramaViewSet, GuardiaViewSet, ResumenGuardiaMesViewSet,
    ReglaPlusViewSet, ParametrosAreaViewSet, FeriadoViewSet, HoraCompensacionViewSet
)

# Router para las APIs REST
router = DefaultRouter()
router.register(r'cronogramas', CronogramaViewSet)
router.register(r'guardias', GuardiaViewSet)
router.register(r'resumenes-mes', ResumenGuardiaMesViewSet)
router.register(r'reglas-plus', ReglaPlusViewSet)
router.register(r'parametros-area', ParametrosAreaViewSet)
router.register(r'feriados', FeriadoViewSet)
router.register(r'compensaciones', HoraCompensacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs específicas adicionales si se necesitan
    path('', lambda request: JsonResponse({
        'mensaje': 'API Guardias - Sistema de Cronogramas GIGA',
        'version': 'Fase 1',
        'endpoints_disponibles': [
            '/api/cronogramas/',
            '/api/cronogramas/planificar/',
            '/api/cronogramas/{id}/aprobar/',
            '/api/cronogramas/{id}/publicar/',
            '/api/guardias/',
            '/api/guardias/resumen/',
            '/api/resumenes-mes/',
            '/api/resumenes-mes/calcular-mensual/',
            '/api/resumenes-mes/aprobar-lote/',
            '/api/reglas-plus/',
            '/api/reglas-plus/{id}/simular/',
            '/api/parametros-area/',
            '/api/feriados/',
            '/api/feriados/verificar-fecha/',
            '/api/compensaciones/',
            '/api/compensaciones/crear-compensacion/',
            '/api/compensaciones/aprobar-lote/',
            '/api/compensaciones/resumen-mensual/',
            '/api/compensaciones/reporte-compensaciones/',
            # Endpoints de reportes
            '/api/guardias/reporte_individual/',
            '/api/guardias/reporte_general/',
            '/api/guardias/reporte_horas_trabajadas/',
            '/api/guardias/reporte_parte_diario/',
            '/api/guardias/reporte_incumplimiento_normativo/',
            '/api/guardias/exportar_pdf/',
            '/api/guardias/exportar_excel/',
            '/api/cronogramas/reporte_plus_simplificado/',
        ]
    }), name='guardias_index'),
]
