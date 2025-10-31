"""
URLs para el módulo auditoria
"""
from django.urls import path
from django.http import JsonResponse

def auditoria_placeholder(request):
    return JsonResponse({
        'message': 'API de auditoria en desarrollo',
        'module': 'auditoria',
        'available_endpoints': [
            'GET /api/auditoria/ - Lista de auditorias',
            'POST /api/auditoria/ - Crear auditoria',
        ]
    })

urlpatterns = [
    path('', auditoria_placeholder, name='auditoria_placeholder'),
]
