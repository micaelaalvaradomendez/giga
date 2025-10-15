from rest_framework import serializers
from .models import Reporte, Notificacion, PlantillaCorreo, EnvioLoteNotificaciones, RenderCorreo, Vista


class ReporteSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Reporte"""
    generado_por_nombre = serializers.CharField(source='generado_por.nombre_completo', read_only=True)
    
    class Meta:
        model = Reporte
        fields = '__all__'


class PlantillaCorreoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo PlantillaCorreo"""
    
    class Meta:
        model = PlantillaCorreo
        fields = '__all__'


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Notificacion"""
    remitente_nombre = serializers.CharField(source='remitente.nombre_completo', read_only=True)
    destinatario_nombre = serializers.CharField(source='destinatario.nombre_completo', read_only=True)
    plantilla_nombre = serializers.CharField(source='plantilla.nombre', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = '__all__'


class EnvioLoteNotificacionesSerializer(serializers.ModelSerializer):
    """Serializador para el modelo EnvioLoteNotificaciones"""
    cronograma_nombre = serializers.CharField(source='cronograma.nombre', read_only=True)
    
    class Meta:
        model = EnvioLoteNotificaciones
        fields = '__all__'


class RenderCorreoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo RenderCorreo"""
    
    class Meta:
        model = RenderCorreo
        fields = '__all__'


class VistaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Vista"""
    
    class Meta:
        model = Vista
        fields = '__all__'