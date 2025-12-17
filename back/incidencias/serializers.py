from rest_framework import serializers
from django.utils import timezone
from .models import Incidencia
from personas.serializers import AgenteBasicoSerializer
from personas.views import get_authenticated_agente


class IncidenciaSerializer(serializers.ModelSerializer):
    """Serializer completo para incidencias"""
    creado_por_detalle = AgenteBasicoSerializer(source='creado_por', read_only=True)
    asignado_a_detalle = AgenteBasicoSerializer(source='asignado_a', read_only=True)
    creado_por_nombre = serializers.SerializerMethodField()
    asignado_a_nombre = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='area_involucrada.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    puede_cambiar_estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Incidencia
        fields = [
            'id', 'numero', 'titulo', 'descripcion', 'estado', 'estado_display', 'prioridad', 'prioridad_display',
            'creado_por', 'creado_por_detalle', 'creado_por_nombre',
            'asignado_a', 'asignado_a_detalle', 'asignado_a_nombre',
            'area_involucrada', 'area_nombre', 'fecha_creacion', 'fecha_asignacion',
            'fecha_resolucion', 'resolucion', 'comentarios_seguimiento', 'puede_cambiar_estado'
        ]
        read_only_fields = ['numero', 'fecha_creacion', 'fecha_asignacion', 'fecha_resolucion']
    
    def create(self, validated_data):
        # El área se asigna automáticamente basada en el agente creador
        request = self.context.get('request')
        if request:
            agente = get_authenticated_agente(request)
            if agente:
                validated_data['area_involucrada'] = agente.id_area
                validated_data['creado_por'] = agente
        
        return super().create(validated_data)
    
    def get_creado_por_nombre(self, obj):
        if obj.creado_por:
            return f"{obj.creado_por.nombre} {obj.creado_por.apellido}"
        return None
    
    def get_asignado_a_nombre(self, obj):
        if obj.asignado_a:
            return f"{obj.asignado_a.nombre} {obj.asignado_a.apellido}"
        return None
    
    def get_puede_cambiar_estado(self, obj):
        request = self.context.get('request')
        if request:
            agente = get_authenticated_agente(request)
            if agente:
                return obj.puede_cambiar_estado(agente)
        return False


class IncidenciaCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear incidencias"""
    asignado_a_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Incidencia
        fields = ['titulo', 'descripcion', 'prioridad', 'asignado_a_id']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            agente = get_authenticated_agente(request)
            if agente:
                validated_data['area_involucrada'] = agente.id_area
                validated_data['creado_por'] = agente
        
        # Asignar a jefe específico si se seleccionó
        asignado_a_id = validated_data.pop('asignado_a_id', None)
        if asignado_a_id:
            from personas.models import Agente
            try:
                jefe = Agente.objects.get(id_agente=asignado_a_id, activo=True)
                validated_data['asignado_a'] = jefe
                validated_data['fecha_asignacion'] = timezone.now()
            except Agente.DoesNotExist:
                pass
        
        return Incidencia.objects.create(**validated_data)


class IncidenciaListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listas"""
    creado_por_nombre = serializers.SerializerMethodField()
    asignado_a_nombre = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='area_involucrada.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    class Meta:
        model = Incidencia
        fields = [
            'id', 'numero', 'titulo', 'estado', 'estado_display', 'prioridad', 'prioridad_display',
            'creado_por_nombre', 'asignado_a_nombre', 'area_nombre',
            'fecha_creacion', 'fecha_resolucion'
        ]
    
    def get_creado_por_nombre(self, obj):
        return f"{obj.creado_por.nombre} {obj.creado_por.apellido}"
    
    def get_asignado_a_nombre(self, obj):
        if obj.asignado_a:
            return f"{obj.asignado_a.nombre} {obj.asignado_a.apellido}"
        return None


class ComentarioSerializer(serializers.Serializer):
    """Serializer para agregar comentarios"""
    comentario = serializers.CharField(max_length=1000)


class ResolucionSerializer(serializers.Serializer):
    """Serializer para resolver incidencia"""
    resolucion = serializers.CharField(max_length=2000)


class CambiarEstadoSerializer(serializers.Serializer):
    """Serializer para cambiar el estado de una incidencia"""
    estado = serializers.ChoiceField(choices=Incidencia.ESTADO_CHOICES)
    comentario = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_estado(self, value):
        """Validar que el nuevo estado sea válido"""
        return value