"""
Serializers para la app guardias - Incluyendo nuevos modelos de cronogramas.
"""

from rest_framework import serializers
from .models import Cronograma, Guardia, ResumenGuardiaMes, ReglaPlus, ParametrosArea, Feriado, NotaGuardia, HoraCompensacion


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
    
    area_nombre = serializers.CharField(source='id_area.nombre', read_only=True, allow_null=True)
    jefe_nombre = serializers.CharField(source='id_jefe.nombre', read_only=True, allow_null=True)
    jefe_apellido = serializers.CharField(source='id_jefe.apellido', read_only=True, allow_null=True)
    total_guardias = serializers.SerializerMethodField()
    
    # Campos de aprobación - con manejo de NULL
    creado_por_nombre = serializers.CharField(source='creado_por_id.nombre', read_only=True, allow_null=True, default=None)
    creado_por_apellido = serializers.CharField(source='creado_por_id.apellido', read_only=True, allow_null=True, default=None)
    aprobado_por_nombre = serializers.CharField(source='aprobado_por_id.nombre', read_only=True, allow_null=True, default=None)
    aprobado_por_apellido = serializers.CharField(source='aprobado_por_id.apellido', read_only=True, allow_null=True, default=None)
    requiere_aprobacion = serializers.SerializerMethodField()
    puede_aprobar_rol = serializers.SerializerMethodField()
    
    class Meta:
        model = Cronograma
        fields = [
            'id_cronograma', 'fecha_aprobacion', 'tipo',
            'hora_inicio', 'hora_fin', 'creado_en', 'actualizado_en',
            'id_jefe', 'jefe_nombre', 'jefe_apellido',
            'id_area', 'area_nombre', 'total_guardias', 'estado', 'fecha_creacion',
            'creado_por_rol', 'creado_por_id', 'creado_por_nombre', 'creado_por_apellido',
            'aprobado_por_id', 'aprobado_por_nombre', 'aprobado_por_apellido',
            'requiere_aprobacion', 'puede_aprobar_rol'
        ]
        read_only_fields = ['id_cronograma', 'creado_en', 'actualizado_en', 'total_guardias', 
                          'requiere_aprobacion', 'puede_aprobar_rol']
    
    def get_total_guardias(self, obj):
        """Cuenta el total de guardias del cronograma"""
        return obj.guardia_set.count()
    
    def get_requiere_aprobacion(self, obj):
        """Calcula si requiere aprobación de forma segura"""
        try:
            return obj.requiere_aprobacion
        except:
            return True  # Por defecto, requiere aprobación
    
    def get_puede_aprobar_rol(self, obj):
        """Calcula roles que pueden aprobar de forma segura"""
        try:
            return obj.puede_aprobar_rol
        except:
            return ['administrador']  # Por defecto, solo admin


class NotaGuardiaSerializer(serializers.ModelSerializer):
    """Serializer para notas personales de guardias"""
    
    agente_nombre = serializers.CharField(source='id_agente.nombre', read_only=True)
    agente_apellido = serializers.CharField(source='id_agente.apellido', read_only=True)
    guardia_fecha = serializers.DateField(source='id_guardia.fecha', read_only=True)
    
    class Meta:
        model = NotaGuardia
        fields = [
            'id_nota', 'id_guardia', 'id_agente', 
            'agente_nombre', 'agente_apellido', 'guardia_fecha',
            'nota', 'fecha_nota', 'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id_nota', 'fecha_nota', 'creado_en', 'actualizado_en']


class GuardiaResumenSerializer(serializers.ModelSerializer):
    """Serializer para guardias con información resumida"""
    
    agente_nombre = serializers.CharField(source='id_agente.nombre', read_only=True)
    agente_apellido = serializers.CharField(source='id_agente.apellido', read_only=True)
    agente_legajo = serializers.CharField(source='id_agente.legajo', read_only=True)
    area_nombre = serializers.CharField(source='id_agente.id_area.nombre', read_only=True, allow_null=True)
    cronograma_tipo = serializers.CharField(source='id_cronograma.tipo', read_only=True)
    cronograma_estado = serializers.CharField(source='id_cronograma.estado', read_only=True)
    notas = NotaGuardiaSerializer(many=True, read_only=True)
    tiene_nota = serializers.SerializerMethodField()
    
    class Meta:
        model = Guardia
        fields = [
            'id_guardia', 'fecha', 'hora_inicio', 'hora_fin',
            'tipo', 'estado', 'activa', 'horas_planificadas', 'horas_efectivas',
            'observaciones', 'agente_nombre', 'agente_apellido', 
            'agente_legajo', 'area_nombre', 'cronograma_tipo', 'cronograma_estado',
            'notas', 'tiene_nota', 'id_cronograma', 'id_agente'
        ]
    
    def get_tiene_nota(self, obj):
        """Verifica si el agente actual tiene una nota en esta guardia"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'agente'):
            return obj.notas.filter(id_agente=request.user.agente).exists()
        return False


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


class HoraCompensacionSerializer(serializers.ModelSerializer):
    """Serializer para horas de compensación por emergencias"""
    
    agente_nombre = serializers.CharField(source='id_agente.nombre', read_only=True)
    agente_apellido = serializers.CharField(source='id_agente.apellido', read_only=True)
    agente_legajo = serializers.CharField(source='id_agente.legajo', read_only=True)
    
    solicitado_por_nombre = serializers.CharField(source='solicitado_por.nombre', read_only=True)
    solicitado_por_apellido = serializers.CharField(source='solicitado_por.apellido', read_only=True)
    
    aprobado_por_nombre = serializers.CharField(source='aprobado_por.nombre', read_only=True, allow_null=True)
    aprobado_por_apellido = serializers.CharField(source='aprobado_por.apellido', read_only=True, allow_null=True)
    
    cronograma_tipo = serializers.CharField(source='id_cronograma.tipo', read_only=True)
    guardia_fecha = serializers.DateField(source='id_guardia.fecha', read_only=True, allow_null=True)
    
    # Campos calculados
    puede_aprobar = serializers.ReadOnlyField()
    esta_vencida = serializers.ReadOnlyField()
    
    # Campos de display
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    motivo_display = serializers.CharField(source='get_motivo_display', read_only=True)
    tipo_compensacion_display = serializers.CharField(source='get_tipo_compensacion_display', read_only=True)
    
    class Meta:
        model = HoraCompensacion
        fields = [
            'id_hora_compensacion', 'id_agente', 'id_guardia', 'id_cronograma',
            'agente_nombre', 'agente_apellido', 'agente_legajo',
            'cronograma_tipo', 'guardia_fecha',
            'fecha_servicio', 'hora_inicio_programada', 'hora_fin_programada', 'hora_fin_real',
            'horas_programadas', 'horas_efectivas', 'horas_extra',
            'motivo', 'motivo_display', 'descripcion_motivo', 'numero_acta',
            'estado', 'estado_display', 'tipo_compensacion', 'tipo_compensacion_display',
            'solicitado_por', 'solicitado_por_nombre', 'solicitado_por_apellido',
            'aprobado_por', 'aprobado_por_nombre', 'aprobado_por_apellido',
            'fecha_solicitud', 'fecha_aprobacion', 'observaciones_aprobacion',
            'valor_hora_extra', 'monto_total',
            'creado_en', 'actualizado_en',
            'puede_aprobar', 'esta_vencida'
        ]
        read_only_fields = [
            'id_hora_compensacion', 'horas_programadas', 'horas_efectivas', 'horas_extra',
            'valor_hora_extra', 'monto_total', 'fecha_solicitud', 'fecha_aprobacion',
            'creado_en', 'actualizado_en', 'puede_aprobar', 'esta_vencida'
        ]


class CrearCompensacionSerializer(serializers.Serializer):
    """Serializer para crear una nueva compensación"""
    
    id_agente = serializers.IntegerField()
    fecha_servicio = serializers.DateField()
    hora_fin_real = serializers.TimeField()
    motivo = serializers.ChoiceField(choices=HoraCompensacion.MOTIVO_CHOICES)
    descripcion_motivo = serializers.CharField(max_length=1000)
    numero_acta = serializers.CharField(max_length=50, required=False, allow_blank=True)
    tipo_compensacion = serializers.ChoiceField(
        choices=HoraCompensacion.TIPO_COMPENSACION_CHOICES,
        default='plus'
    )
    
    def validate(self, data):
        """Validaciones personalizadas"""
        from .models import Guardia
        from .utils import ValidadorHorarios
        
        # Verificar que existe una guardia para esa fecha
        try:
            guardia = Guardia.objects.get(
                id_agente=data['id_agente'],
                fecha=data['fecha_servicio'],
                activa=True
            )
        except Guardia.DoesNotExist:
            raise serializers.ValidationError("No hay guardia programada para esta fecha")
        
        # Validar las horas usando el validador
        es_valida, mensaje, horas_extra = ValidadorHorarios.validar_horas_compensacion(
            guardia.hora_inicio,
            guardia.hora_fin,
            data['hora_fin_real']
        )
        
        if not es_valida:
            raise serializers.ValidationError(f"Horas inválidas: {mensaje}")
        
        # Agregar datos calculados
        data['guardia'] = guardia
        data['horas_extra'] = horas_extra
        
        return data


class AprobacionCompensacionSerializer(serializers.Serializer):
    """Serializer para aprobar/rechazar compensaciones"""
    
    compensacion_ids = serializers.ListField(child=serializers.IntegerField())
    accion = serializers.ChoiceField(choices=[('aprobar', 'Aprobar'), ('rechazar', 'Rechazar')])
    observaciones = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_compensacion_ids(self, value):
        """Valida que las compensaciones existan y se puedan aprobar"""
        from .models import HoraCompensacion
        
        compensaciones = HoraCompensacion.objects.filter(
            id_hora_compensacion__in=value,
            estado='pendiente'
        )
        
        if compensaciones.count() != len(value):
            raise serializers.ValidationError("Algunas compensaciones no existen o no están en estado pendiente")
        
        return value


class ResumenCompensacionSerializer(serializers.Serializer):
    """Serializer para resúmenes de compensaciones"""
    
    agente = serializers.IntegerField()
    mes = serializers.IntegerField(min_value=1, max_value=12)
    anio = serializers.IntegerField(min_value=2020, max_value=2030)
    
    def validate(self, data):
        """Validaciones del resumen"""
        from datetime import date
        
        # Verificar que no sea un período futuro
        hoy = date.today()
        if data['anio'] > hoy.year or (data['anio'] == hoy.year and data['mes'] > hoy.month):
            raise serializers.ValidationError("No se puede consultar períodos futuros")
        
        return data