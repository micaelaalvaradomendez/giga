from rest_framework import serializers
from .models import Asistencia, Marca, Licencia, Novedad, Adjunto, TipoLicencia, ParteDiario


class AsistenciaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Asistencia"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = '__all__'


class MarcaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Marca"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    
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


class TipoLicenciaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo TipoLicencia"""
    
    class Meta:
        model = TipoLicencia
        fields = '__all__'


class ParteDiarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ParteDiario"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    
    class Meta:
        model = ParteDiario
        fields = '__all__'