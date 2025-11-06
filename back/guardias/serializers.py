"""
Serializers para la app guardias - Incluyendo nuevos modelos de cronogramas.
"""

from rest_framework import serializers
from .models import Cronograma, Guardia, ResumenGuardiaMes, ReglaPlus, ParametrosArea, Feriado


class ReglaPlusSerializer(serializers.ModelSerializer):
    """Serializer para reglas de plus salarial"""
    
    esta_vigente = serializers.ReadOnlyField()
    
    class Meta:
        model = ReglaPlus
        fields = [
            'id_regla_plus', 'nombre', 'horas_minimas_diarias', 
            'horas_minimas_mensuales', 'porcentaje_plus',
            'aplica_areas_operativas', 'aplica_areas_administrativas',
            'vigente_desde', 'vigente_hasta', 'activa', 
            'creado_en', 'actualizado_en', 'esta_vigente'
        ]
        read_only_fields = ['id_regla_plus', 'creado_en', 'actualizado_en']


class ParametrosAreaSerializer(serializers.ModelSerializer):
    """Serializer para parámetros de control horario por área"""
    
    area_nombre = serializers.CharField(source='id_area.nombre', read_only=True)
    esta_vigente = serializers.ReadOnlyField()
    
    class Meta:
        model = ParametrosArea
        fields = [
            'id_parametros_area', 'id_area', 'area_nombre',
            'ventana_entrada_inicio', 'ventana_entrada_fin',
            'ventana_salida_inicio', 'ventana_salida_fin',
            'tolerancia_entrada_min', 'tolerancia_salida_min',
            'horas_trabajo_dia', 'vigente_desde', 'vigente_hasta',
            'activo', 'creado_en', 'actualizado_en', 'esta_vigente'
        ]
        read_only_fields = ['id_parametros_area', 'creado_en', 'actualizado_en']


class FeriadoSerializer(serializers.ModelSerializer):
    """Serializer para feriados"""
    
    tipo_feriado = serializers.ReadOnlyField()
    
    class Meta:
        model = Feriado
        fields = [
            'id_feriado', 'fecha', 'descripcion',
            'es_nacional', 'es_provincial', 'es_local',
            'activo', 'creado_en', 'tipo_feriado'
        ]
        read_only_fields = ['id_feriado', 'creado_en']


class CronogramaExtendidoSerializer(serializers.ModelSerializer):
    """Serializer extendido para cronogramas con nuevos campos"""
    
    area_nombre = serializers.CharField(source='id_area.nombre', read_only=True)
    jefe_nombre = serializers.CharField(source='id_jefe.nombre', read_only=True)
    jefe_apellido = serializers.CharField(source='id_jefe.apellido', read_only=True)
    total_guardias = serializers.SerializerMethodField()
    
    class Meta:
        model = Cronograma
        fields = [
            'id_cronograma', 'fecha_aprobacion', 'tipo',
            'hora_inicio', 'hora_fin', 'creado_en', 'actualizado_en',
            'id_jefe', 'jefe_nombre', 'jefe_apellido',
            'id_area', 'area_nombre', 'total_guardias'
        ]
        read_only_fields = ['id_cronograma', 'creado_en', 'actualizado_en', 'total_guardias']
    
    def get_total_guardias(self, obj):
        """Cuenta el total de guardias del cronograma"""
        return obj.guardia_set.count()


class GuardiaResumenSerializer(serializers.ModelSerializer):
    """Serializer para guardias con información resumida"""
    
    agente_nombre = serializers.CharField(source='id_agente.nombre', read_only=True)
    agente_apellido = serializers.CharField(source='id_agente.apellido', read_only=True)
    agente_legajo = serializers.CharField(source='id_agente.legajo', read_only=True)
    cronograma_tipo = serializers.CharField(source='id_cronograma.tipo', read_only=True)
    
    class Meta:
        model = Guardia
        fields = [
            'id_guardia', 'fecha', 'hora_inicio', 'hora_fin',
            'tipo', 'estado', 'activa', 'horas_planificadas', 'horas_efectivas',
            'observaciones', 'agente_nombre', 'agente_apellido', 
            'agente_legajo', 'cronograma_tipo'
        ]


class ResumenGuardiaMesExtendidoSerializer(serializers.ModelSerializer):
    """Serializer extendido para resumen mensual con cálculo automático de plus"""
    
    agente_nombre = serializers.CharField(source='id_agente.nombre', read_only=True)
    agente_apellido = serializers.CharField(source='id_agente.apellido', read_only=True)
    agente_legajo = serializers.CharField(source='id_agente.legajo', read_only=True)
    area_nombre = serializers.CharField(source='id_agente.id_area.nombre', read_only=True)
    
    plus_aplicable = serializers.ReadOnlyField()
    compatibilidad_legacy = serializers.ReadOnlyField()
    periodo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumenGuardiaMes
        fields = [
            'id_resumen_guardia_mes', 'id_agente',
            'agente_nombre', 'agente_apellido', 'agente_legajo', 'area_nombre',
            'mes', 'anio', 'periodo_display',
            # Campos legacy
            'plus20', 'plus40', 'total_horas_guardia',
            # Campos nuevos
            'horas_efectivas', 'porcentaje_plus', 'monto_calculado',
            'estado_plus', 'fecha_calculo', 'aprobado_en',
            # Campos calculados
            'plus_aplicable', 'compatibilidad_legacy'
        ]
        read_only_fields = [
            'id_resumen_guardia_mes', 'plus_aplicable', 
            'compatibilidad_legacy', 'periodo_display'
        ]
    
    def get_periodo_display(self, obj):
        """Formato amigable del período"""
        return f"{obj.mes:02d}/{obj.anio}"


class PlanificacionCronogramaSerializer(serializers.Serializer):
    """Serializer para planificación automática de cronogramas"""
    
    area_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    agentes_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    tipo_cronograma = serializers.CharField(max_length=50, default='automatico')
    hora_inicio = serializers.TimeField(default='08:00:00')
    hora_fin = serializers.TimeField(default='20:00:00')
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if data['hora_inicio'] >= data['hora_fin']:
            raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de fin")
        
        return data


class CalculoPlusSerializer(serializers.Serializer):
    """Serializer para disparar cálculo de plus mensual"""
    
    mes = serializers.IntegerField(min_value=1, max_value=12)
    anio = serializers.IntegerField(min_value=2020, max_value=2030)
    agentes_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="IDs de agentes específicos. Si está vacío, calcula para todos."
    )
    
    def validate(self, data):
        """Validaciones para el cálculo de plus"""
        from datetime import date
        
        # No permitir cálculos de meses futuros
        hoy = date.today()
        if data['anio'] > hoy.year or (data['anio'] == hoy.year and data['mes'] > hoy.month):
            raise serializers.ValidationError("No se puede calcular plus para períodos futuros")
        
        return data


class AprobacionPlusSerializer(serializers.Serializer):
    """Serializer para aprobar asignaciones de plus"""
    
    resumen_ids = serializers.ListField(child=serializers.IntegerField())
    aprobado_por = serializers.IntegerField()
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_resumen_ids(self, value):
        """Valida que los IDs de resumen existan y estén en estado pendiente"""
        resumenes = ResumenGuardiaMes.objects.filter(
            id_resumen_guardia_mes__in=value,
            estado_plus='pendiente'
        )
        
        if resumenes.count() != len(value):
            raise serializers.ValidationError("Algunos resúmenes no existen o no están en estado pendiente")
        
        return value