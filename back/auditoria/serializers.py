from rest_framework import serializers
from .models import Auditoria


class AuditoriaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Auditoria"""
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Auditoria
        fields = '__all__'


# Alias para compatibilidad con ViewSets existentes
ParametrosControlHorarioSerializer = AuditoriaSerializer
RegistroAuditoriaSerializer = AuditoriaSerializer