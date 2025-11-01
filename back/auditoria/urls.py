"""
URLs   para el módulo auditoría
"""
from core.urls import create_standard_urls
from .views import AuditoriaViewSet

app_name = 'auditoria'

urlpatterns = create_standard_urls(app_name, [
    ('registros', AuditoriaViewSet),
])