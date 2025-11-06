"""
URLs para el módulo auditoria
"""
from django.urls import path
from django.http import JsonResponse

def auditoria_placeholder(request):
    return JsonResponse({
    })

urlpatterns = [
    path('', auditoria_placeholder, name='auditoria_placeholder'),
]
