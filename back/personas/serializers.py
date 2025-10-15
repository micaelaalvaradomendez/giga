from rest_framework import serializers
from .models import Agente, Area, Rol, CuentaAcceso


class AreaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Area
    """
    class Meta:
        model = Area
        fields = '__all__'


class AgenteSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Agente
    """
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    
    class Meta:
        model = Agente
        fields = '__all__'


class RolSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Rol
    """
    class Meta:
        model = Rol
        fields = '__all__'


class CuentaAccesoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo CuentaAcceso
    """
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    
    class Meta:
        model = CuentaAcceso
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }