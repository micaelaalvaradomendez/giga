"""
URLs para el módulo asistencia
"""
from django.urls import path
from django.http import JsonResponse

def asistencia_placeholder(request):
    return JsonResponse({
    })

urlpatterns = [
    path('', asistencia_placeholder, name='asistencia_placeholder'),
]
