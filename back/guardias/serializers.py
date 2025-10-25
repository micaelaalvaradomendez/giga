from rest_framework import serializers
from .models import CronogramaGuardias, Guardia, HorasGuardias, Feriado, ReglaPlus, AsignacionPlus


class CronogramaGuardiasSerializer(serializers.ModelSerializer):
    """Serializador para el modelo CronogramaGuardias"""
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    total_guardias = serializers.SerializerMethodField()
    
    class Meta:
        model = CronogramaGuardias
        fields = '__all__'
    
    def get_total_guardias(self, obj):
        return obj.guardias.count()


class GuardiaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Guardia"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    cronograma_nombre = serializers.CharField(source='cronograma.nombre', read_only=True)
    
    class Meta:
        model = Guardia
        fields = '__all__'


class HorasGuardiasSerializer(serializers.ModelSerializer):
    """Serializador para el modelo HorasGuardias"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    
    class Meta:
        model = HorasGuardias
        fields = '__all__'


class FeriadoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Feriado"""
    
    class Meta:
        model = Feriado
        fields = '__all__'


class ReglaPlusSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ReglaPlus"""
    
    class Meta:
        model = ReglaPlus
        fields = '__all__'


class AsignacionPlusSerializer(serializers.ModelSerializer):
    """Serializador para el modelo AsignacionPlus"""
    agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
    regla_nombre = serializers.CharField(source='regla_plus.nombre', read_only=True)
    
    class Meta:
        model = AsignacionPlus
        fields = '__all__'


# Alias para compatibilidad con ViewSets existentes
ModalidadSerializer = CronogramaGuardiasSerializer
CuadroGuardiaSerializer = CronogramaGuardiasSerializer  
AsignacionGuardiaSerializer = GuardiaSerializer