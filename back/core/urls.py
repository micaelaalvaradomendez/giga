"""
Utilidades para configuración automática de URLs en el sistema GIGA
Centraliza patrones repetitivos de configuración de routers
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include


class GIGARouter:
    """
    Router personalizado para el sistema GIGA
    Simplifica la configuración de ViewSets
    """
    
    def __init__(self, app_name):
        self.app_name = app_name
        self.router = DefaultRouter()
    
    def register_viewset(self, prefix, viewset, basename=None):
        """
        Registrar un ViewSet con configuración estándar
        """
        self.router.register(prefix, viewset, basename=basename)
        return self
    
    def register_multiple(self, viewsets_config):
        """
        Registrar múltiples ViewSets de una vez
        
        Args:
            viewsets_config: Lista de tuplas (prefix, viewset, basename_opcional)
        """
        for config in viewsets_config:
            if len(config) == 2:
                prefix, viewset = config
                self.router.register(prefix, viewset)
            elif len(config) == 3:
                prefix, viewset, basename = config
                self.router.register(prefix, viewset, basename=basename)
        
        return self
    
    def get_urls(self):
        """
        Obtener URLs configuradas con app_name
        """
        return [
            path('', include((self.router.urls, self.app_name))),
        ]


def create_standard_urls(app_name, viewsets_config):
    """
    Función helper para crear URLs estándar de un módulo
    
    Args:
        app_name: Nombre de la app
        viewsets_config: Lista de tuplas (prefix, viewset, basename_opcional)
    
    Returns:
        Lista de URLs configuradas
    """
    giga_router = GIGARouter(app_name)
    giga_router.register_multiple(viewsets_config)
    return giga_router.get_urls()


# Ejemplo de uso:
# En urls.py de cada app:
# 
# from core.urls import create_standard_urls
# from .views import MiViewSet1, MiViewSet2
#
# app_name = 'mi_app'
# 
# urlpatterns = create_standard_urls(app_name, [
#     ('recursos', MiViewSet1),
#     ('tipos', MiViewSet2, 'tipos'),
# ])