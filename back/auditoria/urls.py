"""
URLs para el módulo auditoria
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuditoriaViewSet, 
    registros_auditoria,
    log_unauthorized_access,
    log_successful_access
)

# Router para las APIs REST
router = DefaultRouter()
router.register(r'auditoria', AuditoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registros/', registros_auditoria, name='registros_auditoria'),
    path('log-unauthorized/', log_unauthorized_access, name='log_unauthorized_access'),
    path('log-access/', log_successful_access, name='log_successful_access'),
]
