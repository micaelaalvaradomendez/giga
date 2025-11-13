"""
URLs para el módulo guardias - Fase 1 implementación cronogramas
"""
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import (
    CronogramaViewSet, GuardiaViewSet, ResumenGuardiaMesViewSet,
    ReglaPlusViewSet, ParametrosAreaViewSet, FeriadoViewSet
)

# Router para las APIs REST
router = DefaultRouter()
router.register(r'cronogramas', CronogramaViewSet)
router.register(r'guardias', GuardiaViewSet)
router.register(r'resumenes-mes', ResumenGuardiaMesViewSet)
router.register(r'reglas-plus', ReglaPlusViewSet)
router.register(r'parametros-area', ParametrosAreaViewSet)
router.register(r'feriados', FeriadoViewSet)

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
        ]
    }), name='guardias_index'),
]
