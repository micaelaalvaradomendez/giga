from rest_framework import serializers
from .models import Auditoria


class AuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para los registros de auditoría"""
    
    creado_por_nombre = serializers.SerializerMethodField()
    agente_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Auditoria
        fields = [
            'id_auditoria',
            'pk_afectada', 
            'nombre_tabla',
            'creado_en',
            'valor_previo',
            'valor_nuevo',
            'accion',
            'id_agente',
            'creado_por_nombre',
            'agente_info'
        ]
        
    def get_creado_por_nombre(self, obj):
        """Obtiene el nombre completo del agente que realizó la acción"""
        if obj.id_agente:
            return f"{obj.id_agente.nombre} {obj.id_agente.apellido}".strip()
        return 'Sistema'
    
    def get_agente_info(self, obj):
        """Obtiene información detallada del agente"""
        if obj.id_agente:
            return {
                'id': obj.id_agente.id,
                'nombre': obj.id_agente.nombre,
                'apellido': obj.id_agente.apellido,
                'legajo': obj.id_agente.legajo
            }
        return None