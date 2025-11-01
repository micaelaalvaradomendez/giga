"""
Mixins base para ViewSets del sistema GIGA
Centraliza funcionalidades comunes y evita repetición de código
"""
try:
    from rest_framework import viewsets, filters
    from rest_framework.permissions import IsAuthenticated
    from django_filters.rest_framework import DjangoFilterBackend
    from auditoria.models import Auditoria
except ImportError:
    # Fallback para entornos sin Django
    class MockClass:
        pass
    viewsets = filters = IsAuthenticated = DjangoFilterBackend = Auditoria = MockClass


class AuditoriaMixin:
    """
    Mixin que agrega funcionalidad de auditoría automática a los ViewSets
    """
    
    def perform_create(self, serializer):
        """Crear objeto y registrar auditoría automáticamente"""
        instance = serializer.save(
            creado_por=getattr(self.request, 'user', None)
        )
        
        # Registrar auditoría si existe usuario autenticado
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            Auditoria.objects.create(
                creado_por=self.request.user,
                nombre_tabla=instance.__class__.__name__,
                pk_afectada=str(instance.id),
                accion='create',
                valor_nuevo=serializer.data
            )
        
        return instance
    
    def perform_update(self, serializer):
        """Actualizar objeto y registrar auditoría automáticamente"""
        instance_anterior = self.get_object()
        
        # Capturar valores anteriores relevantes
        valores_previos = self._get_valores_auditoria(instance_anterior)
        
        instance = serializer.save(
            actualizado_por=getattr(self.request, 'user', None)
        )
        
        # Registrar auditoría si existe usuario autenticado
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            Auditoria.objects.create(
                creado_por=self.request.user,
                nombre_tabla=instance.__class__.__name__,
                pk_afectada=str(instance.id),
                accion='update',
                valor_previo=valores_previos,
                valor_nuevo=serializer.data
            )
        
        return instance
    
    def perform_destroy(self, instance):
        """Eliminar objeto y registrar auditoría automáticamente"""
        valores_previos = self._get_valores_auditoria(instance)
        
        # Registrar auditoría antes de eliminar
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            Auditoria.objects.create(
                creado_por=self.request.user,
                nombre_tabla=instance.__class__.__name__,
                pk_afectada=str(instance.id),
                accion='delete',
                valor_previo=valores_previos
            )
        
        instance.delete()
    
    def _get_valores_auditoria(self, instance):
        """Obtener valores relevantes para auditoría según el modelo"""
        valores = {}
        
        # Campos comunes que siempre queremos auditar
        campos_comunes = ['nombre', 'email', 'activo', 'activa', 'legajo', 'codigo']
        
        for campo in campos_comunes:
            if hasattr(instance, campo):
                valores[campo] = getattr(instance, campo)
        
        return valores


class BaseConfigMixin:
    """
    Mixin con configuración estándar para ViewSets del sistema GIGA
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Paginación automática (se toma de settings)
    # Ordenamiento por defecto se define en cada ViewSet específico


class GIGABaseViewSet(AuditoriaMixin, BaseConfigMixin, viewsets.ModelViewSet):
    """
    ViewSet base para todos los modelos CRUD del sistema GIGA
    Combina auditoría automática con configuración estándar
    """
    pass


class GIGAReadOnlyViewSet(BaseConfigMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet base para modelos de solo lectura (catálogos, reportes, etc.)
    """
    pass


class GIGAViewSet(BaseConfigMixin, viewsets.ViewSet):
    """
    ViewSet base para endpoints personalizados (reportes dinámicos, acciones especiales)
    """
    pass