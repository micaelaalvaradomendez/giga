"""
URLs para el módulo auditoria
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditoriaViewSet, registros_auditoria

# Router para las APIs REST
router = DefaultRouter()
router.register(r'auditoria', AuditoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registros/', registros_auditoria, name='registros_auditoria'),
]
