"""
URLs para el módulo asistencia
"""
from django.urls import path
from django.http import JsonResponse

def asistencia_placeholder(request):
    return JsonResponse({
        'message': 'API de asistencia en desarrollo',
        'module': 'asistencia',
        'available_endpoints': [
            'GET /api/asistencia/ - Lista de asistencias',
            'POST /api/asistencia/ - Crear asistencia',
        ]
    })

urlpatterns = [
    path('', asistencia_placeholder, name='asistencia_placeholder'),
]
