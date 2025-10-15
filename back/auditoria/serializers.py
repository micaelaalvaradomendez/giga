from rest_framework import serializers
from .models import ParametrosControlHorario, RegistroAuditoria


class ParametrosControlHorarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ParametrosControlHorario"""
    
    class Meta:
        model = ParametrosControlHorario
        fields = '__all__'


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo RegistroAuditoria"""
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = RegistroAuditoria
        fields = '__all__'