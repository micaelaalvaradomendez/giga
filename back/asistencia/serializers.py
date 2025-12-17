"""
Serializers para el módulo de asistencia - Sistema GIGA
"""

from rest_framework import serializers
from .models import Asistencia, IntentoMarcacionFraudulenta, Licencia, TipoLicencia
from personas.models import Agente, Area


class AsistenciaSerializer(serializers.ModelSerializer):
    agente_nombre = serializers.SerializerMethodField()
    agente_dni = serializers.SerializerMethodField()
    area_nombre = serializers.SerializerMethodField()
    corregido_por_nombre = serializers.SerializerMethodField()
    horario_esperado_entrada = serializers.SerializerMethodField()
    horario_esperado_salida = serializers.SerializerMethodField()
    estado = serializers.ReadOnlyField()
    
    class Meta:
        model = Asistencia
        fields = [
            'id_asistencia', 'fecha', 'hora_entrada', 'hora_salida', 'horas_efectivas',
            'marcacion_entrada_automatica', 'marcacion_salida_automatica',
            'es_correccion', 'corregido_por', 'corregido_por_nombre',
            'observaciones', 'creado_en', 'actualizado_en',
            'id_agente', 'agente_nombre', 'agente_dni',
            'id_area', 'area_nombre', 'estado',
            'horario_esperado_entrada', 'horario_esperado_salida'
        ]
        read_only_fields = ['id_asistencia', 'creado_en', 'actualizado_en', 'estado', 'horas_efectivas']
    
    def get_agente_nombre(self, obj):
        if obj.id_agente:
            return f"{obj.id_agente.nombre} {obj.id_agente.apellido}"
        return None
    
    def get_agente_dni(self, obj):
        if obj.id_agente:
            return obj.id_agente.dni
        return None
    
    def get_area_nombre(self, obj):
        if obj.id_area:
            return obj.id_area.nombre
        return None
    
    def get_horario_esperado_entrada(self, obj):
        if obj.id_agente and obj.id_agente.horario_entrada:
            return str(obj.id_agente.horario_entrada)
        return None
    
    def get_horario_esperado_salida(self, obj):
        if obj.id_agente and obj.id_agente.horario_salida:
            return str(obj.id_agente.horario_salida)
        return None
    
    def get_corregido_por_nombre(self, obj):
        if obj.corregido_por:
            return f"{obj.corregido_por.nombre} {obj.corregido_por.apellido}"
        return None


class IntentoFraudulentoSerializer(serializers.ModelSerializer):
    agente_sesion_nombre = serializers.SerializerMethodField()
    agente_dni_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = IntentoMarcacionFraudulenta
        fields = [
            'id_intento', 'fecha', 'hora', 'dni_ingresado',
            'id_agente_sesion', 'agente_sesion_nombre',
            'id_agente_dni', 'agente_dni_nombre',
            'tipo_intento', 'ip_address', 'creado_en'
        ]
        read_only_fields = ['id_intento', 'creado_en']
    
    def get_agente_sesion_nombre(self, obj):
        if obj.id_agente_sesion:
            return f"{obj.id_agente_sesion.nombre} {obj.id_agente_sesion.apellido}"
        return None
    
    def get_agente_dni_nombre(self, obj):
        if obj.id_agente_dni:
            return f"{obj.id_agente_dni.nombre} {obj.id_agente_dni.apellido}"
        return None


class TipoLicenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoLicencia
        fields = ['id_tipo_licencia', 'codigo', 'descripcion']


class LicenciaSerializer(serializers.ModelSerializer):
    agente_nombre = serializers.SerializerMethodField()
    agente_dni = serializers.SerializerMethodField()
    tipo_licencia_descripcion = serializers.SerializerMethodField()
    area_nombre = serializers.SerializerMethodField()
    dias_licencia = serializers.ReadOnlyField()
    aprobada_por_nombre = serializers.SerializerMethodField()
    rechazada_por_nombre = serializers.SerializerMethodField()
    solicitada_por_nombre = serializers.SerializerMethodField()
    agente_rol = serializers.SerializerMethodField()
    id_agente_area = serializers.SerializerMethodField()
    
    class Meta:
        model = Licencia
        fields = [
            'id_licencia', 'estado', 'id_tipo_licencia', 'tipo_licencia_descripcion',
            'id_licencia', 'estado', 'id_tipo_licencia', 'tipo_licencia_descripcion',
            'fecha_desde', 'fecha_hasta', 'id_agente', 'agente_nombre', 'agente_dni', 'area_nombre',
            'observaciones', 'justificacion', 'dias_licencia',
            'aprobada_por', 'aprobada_por_nombre', 'fecha_aprobacion', 'observaciones_aprobacion',
            'rechazada_por', 'rechazada_por_nombre', 'fecha_rechazo', 'motivo_rechazo',
            'solicitada_por', 'solicitada_por_nombre', 'creado_en', 'actualizado_en',
            'agente_rol', 'id_agente_area'
        ]
        read_only_fields = ['id_licencia', 'creado_en', 'actualizado_en', 'dias_licencia']
    
    def get_agente_nombre(self, obj):
        if obj.id_agente:
            return f"{obj.id_agente.nombre} {obj.id_agente.apellido}"
        return None
    
    def get_agente_dni(self, obj):
        if obj.id_agente:
            return obj.id_agente.dni
        return None
    
    def get_tipo_licencia_descripcion(self, obj):
        if obj.id_tipo_licencia:
            return f"{obj.id_tipo_licencia.codigo} - {obj.id_tipo_licencia.descripcion}"
        return None
    
    def get_area_nombre(self, obj):
        if obj.id_agente and obj.id_agente.id_area:
            return obj.id_agente.id_area.nombre
        return None
    
    def get_aprobada_por_nombre(self, obj):
        if obj.aprobada_por:
            return f"{obj.aprobada_por.nombre} {obj.aprobada_por.apellido}"
        return None
    
    def get_rechazada_por_nombre(self, obj):
        if obj.rechazada_por:
            return f"{obj.rechazada_por.nombre} {obj.rechazada_por.apellido}"
        return None
    
    def get_solicitada_por_nombre(self, obj):
        if obj.solicitada_por:
            return f"{obj.solicitada_por.nombre} {obj.solicitada_por.apellido}"
        return None
    
    def get_agente_rol(self, obj):
        if obj.id_agente:
            agente_rol = obj.id_agente.agenterol_set.first()
            if agente_rol:
                return agente_rol.id_rol.nombre
        return None
    
    def get_id_agente_area(self, obj):
        if obj.id_agente and obj.id_agente.id_area:
            return obj.id_agente.id_area.id_area
        return None


class ResumenAsistenciaSerializer(serializers.Serializer):
    """Serializer para el resumen de asistencias por área"""
    fecha = serializers.DateField()
    total_agentes = serializers.IntegerField()
    presentes = serializers.IntegerField()
    ausentes = serializers.IntegerField()
    sin_salida = serializers.IntegerField()
    salidas_automaticas = serializers.IntegerField()
    en_licencia = serializers.IntegerField()
    area_id = serializers.IntegerField(required=False)
    area_nombre = serializers.CharField(required=False)
