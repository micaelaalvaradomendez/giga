"""
Serializers base para el sistema GIGA
Centraliza validaciones y campos comunes
"""
from rest_framework import serializers
from django.utils import timezone


class BaseSerializer(serializers.ModelSerializer):
    """
    Serializer base con campos de auditoría comunes
    """
    
    # Campos de solo lectura para auditoría
    creado_en = serializers.DateTimeField(read_only=True)
    actualizado_en = serializers.DateTimeField(read_only=True)
    
    # Campos relacionados de solo lectura (se agregan dinámicamente)
    creado_por_nombre = serializers.SerializerMethodField(read_only=True)
    actualizado_por_nombre = serializers.SerializerMethodField(read_only=True)
    
    def get_creado_por_nombre(self, obj):
        """Obtener nombre del usuario que creó el registro"""
        if hasattr(obj, 'creado_por') and obj.creado_por:
            return obj.creado_por.get_full_name() or obj.creado_por.username
        return None
    
    def get_actualizado_por_nombre(self, obj):
        """Obtener nombre del usuario que actualizó el registro"""
        if hasattr(obj, 'actualizado_por') and obj.actualizado_por:
            return obj.actualizado_por.get_full_name() or obj.actualizado_por.username
        return None
    
    class Meta:
        abstract = True


class PersonaBaseSerializer(BaseSerializer):
    """
    Serializer base para modelos relacionados con personas
    """
    
    # Campo calculado para nombre completo
    nombre_completo = serializers.SerializerMethodField(read_only=True)
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo dependiendo del modelo"""
        if hasattr(obj, 'usuario'):
            return obj.usuario.get_full_name()
        elif hasattr(obj, 'nombre') and hasattr(obj, 'apellido'):
            return f"{obj.nombre} {obj.apellido}"
        elif hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
            return f"{obj.first_name} {obj.last_name}"
        return str(obj)
    
    class Meta:
        abstract = True


class CatalogoSerializer(serializers.ModelSerializer):
    """
    Serializer para modelos de catálogo (tipos, modalidades, etc.)
    """
    
    class Meta:
        abstract = True
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']


class FechaRangoSerializer(serializers.ModelSerializer):
    """
    Serializer base para modelos con rango de fechas
    """
    
    def validate(self, attrs):
        """Validar que fecha_desde sea anterior a fecha_hasta"""
        fecha_desde = attrs.get('fecha_desde')
        fecha_hasta = attrs.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta and fecha_desde >= fecha_hasta:
            raise serializers.ValidationError(
                "La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        return attrs
    
    class Meta:
        abstract = True


class EstadoSerializer(serializers.ModelSerializer):
    """
    Serializer para modelos con estados (pendiente, aprobado, rechazado, etc.)
    """
    
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        abstract = True