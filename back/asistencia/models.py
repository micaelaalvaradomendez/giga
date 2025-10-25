from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from personas.models import Agente, Area
import uuid

class TipoLicencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=255, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class Marca(models.Model):
    """Registro individual de entrada/salida de agentes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='marcas')
    fecha = models.DateField()
    hora = models.TimeField()
    tipo = models.CharField(max_length=10, choices=[
        ('entrada', 'Entrada'),
        ('salida', 'Salida')
    ])
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='marcas_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='marcas_actualizadas')
    
    class Meta:
        indexes = [
            models.Index(fields=['agente', 'fecha', 'hora']),
        ]
        unique_together = ['agente', 'fecha', 'hora', 'tipo']
    
    def __str__(self):
        return f"{self.agente} - {self.fecha} {self.hora} ({self.tipo})"

# Alias para compatibilidad - ParteDiario es el modelo principal de asistencia
Asistencia = None  # Se definirá después

class ParteDiario(models.Model):
    """Consolidación diaria de asistencia por agente"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    fecha_parte = models.DateField()
    estado = models.CharField(max_length=20, default='borrador', choices=[
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('anulado', 'Anulado')
    ])
    observaciones = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.CASCADE, null=True, blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='partes_creados')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='partes_actualizados')
    
    class Meta:
        indexes = [
            models.Index(fields=['area', 'fecha_parte', 'agente'])
        ]
        unique_together = ['fecha_parte', 'agente']
    
    def __str__(self):
        return f"Parte {self.agente} - {self.fecha_parte}"

# Modelo de Asistencia que es requerido por los ViewSets
class Asistencia(models.Model):
    """Registro diario de asistencia por agente"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    horario_entrada = models.TimeField(null=True, blank=True)
    horario_salida = models.TimeField(null=True, blank=True)
    minutos_tarde = models.IntegerField(default=0)
    minutos_extras = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, default='presente', choices=[
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('tardanza', 'Tardanza'),
        ('licencia', 'Licencia')
    ])
    observaciones = models.TextField(blank=True, null=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='asistencias_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='asistencias_actualizadas')
    
    class Meta:
        db_table = 'asistencia_asistencia'
        unique_together = ['agente', 'fecha']
        indexes = [
            models.Index(fields=['agente', 'fecha']),
            models.Index(fields=['estado', 'fecha']),
        ]
    
    def __str__(self):
        return f"Asistencia {self.agente} - {self.fecha} ({self.estado})"

class LicenciaONovedad(models.Model):
    """Clase base abstracta para licencias y novedades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('anulada', 'Anulada')
    ])
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='%(class)s_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='%(class)s_actualizadas')
    
    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
                name='%(app_label)s_%(class)s_fecha_fin_mayor_inicio'
            )
        ]
    
    def duracion_dias(self):
        """Retorna la duración en días"""
        return (self.fecha_fin - self.fecha_inicio).days + 1

class Licencia(LicenciaONovedad):
    """Licencias (vacaciones, enfermedad, personal, estudio)"""
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.CASCADE)
    con_goce_haberes = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'asistencia_licencia'
        indexes = [
            models.Index(fields=['agente', 'fecha_inicio', 'fecha_fin']),
            models.Index(fields=['tipo_licencia', 'estado']),
        ]
    
    def __str__(self):
        return f"Licencia {self.tipo_licencia} - {self.agente} ({self.fecha_inicio} a {self.fecha_fin})"

class Novedad(LicenciaONovedad):
    """Novedades (médica, familiar, capacitación)"""
    TIPO_NOVEDAD_CHOICES = [
        ('medica', 'Médica'),
        ('familiar', 'Familiar'),
        ('capacitacion', 'Capacitación'),
        ('otra', 'Otra')
    ]
    tipo_novedad = models.CharField(max_length=20, choices=TIPO_NOVEDAD_CHOICES)
    requiere_justificativo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'asistencia_novedad'
        indexes = [
            models.Index(fields=['agente', 'fecha_inicio', 'fecha_fin']),
            models.Index(fields=['tipo_novedad', 'estado']),
        ]
    
    def __str__(self):
        return f"Novedad {self.tipo_novedad} - {self.agente} ({self.fecha_inicio} a {self.fecha_fin})"

class Adjunto(models.Model):
    """Archivos adjuntos para licencias y novedades"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones polimórficas
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    archivo = models.FileField(
        upload_to='adjuntos/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    nombre_original = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tamaño = models.BigIntegerField()
    tipo_archivo = models.CharField(max_length=100)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='adjuntos_creados')
    
    class Meta:
        db_table = 'asistencia_adjunto'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Adjunto: {self.nombre_original}"

class ParametrosControlHorario(models.Model):
    """Configuración de ventanas de marcación y tolerancias"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='parametros_horario')
    
    # Ventanas de marcación
    ventana_entrada_inicio = models.TimeField(help_text="Hora más temprana permitida para marcar entrada")
    ventana_entrada_fin = models.TimeField(help_text="Hora más tardía permitida para marcar entrada")
    ventana_salida_inicio = models.TimeField(help_text="Hora más temprana permitida para marcar salida")
    ventana_salida_fin = models.TimeField(help_text="Hora más tardía permitida para marcar salida")
    
    # Tolerancias
    tolerancia_entrada_min = models.IntegerField(default=15, help_text="Tolerancia entrada en minutos")
    tolerancia_salida_min = models.IntegerField(default=15, help_text="Tolerancia salida en minutos")
    
    # Configuraciones adicionales
    requiere_justificacion_fuera_ventana = models.BooleanField(default=True)
    horas_trabajo_por_dia = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='parametros_creados')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='parametros_actualizados')
    
    class Meta:
        db_table = 'asistencia_parametros_control_horario'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ventana_entrada_fin__gt=models.F('ventana_entrada_inicio')),
                name='ventana_entrada_valida'
            ),
            models.CheckConstraint(
                condition=models.Q(ventana_salida_fin__gt=models.F('ventana_salida_inicio')),
                name='ventana_salida_valida'
            ),
            models.CheckConstraint(
                condition=models.Q(vigente_hasta__isnull=True) | models.Q(vigente_hasta__gt=models.F('vigente_desde')),
                name='vigencia_valida'
            )
        ]
        indexes = [
            models.Index(fields=['area', 'vigente_desde', 'vigente_hasta']),
        ]
    
    def __str__(self):
        return f"Parámetros {self.area} - {self.vigente_desde}"