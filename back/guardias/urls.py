"""
URLs para el módulo guardias
"""
from django.urls import path
from django.http import JsonResponse

def guardias_placeholder(request):
    return JsonResponse({
        'message': 'API de guardias en desarrollo',
        'module': 'guardias',
        'available_endpoints': [
            'GET /api/guardias/ - Lista de guardias',
            'POST /api/guardias/ - Crear guardia',
        ]
    })

urlpatterns = [
    path('', guardias_placeholder, name='guardias_placeholder'),
]
