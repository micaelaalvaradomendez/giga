from rest_framework import serializers
from .models import Asistencia, Marca, Licencia, Novedad, Adjunto


class AsistenciaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Asistencia"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = '__all__'


class MarcaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Marca"""
    asistencia_info = serializers.CharField(source='asistencia.agente.nombre_completo', read_only=True)
    
    class Meta:
        model = Marca
        fields = '__all__'


class AdjuntoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Adjunto"""
    
    class Meta:
        model = Adjunto
        fields = '__all__'


class LicenciaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Licencia"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    adjuntos = AdjuntoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Licencia
        fields = '__all__'


class NovedadSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Novedad"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    adjuntos = AdjuntoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Novedad
        fields = '__all__'