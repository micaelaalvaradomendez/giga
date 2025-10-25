from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from personas.models import Agente, Area
from datetime import date
import uuid

# back/guardias/models.py

class Feriado(models.Model):
    """Días feriados que afectan guardias"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=255)
    es_nacional = models.BooleanField(default=True)
    es_provincial = models.BooleanField(default=False)
    es_local = models.BooleanField(default=False)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='feriados_creados')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='feriados_actualizados')
    
    class Meta:
        db_table = 'guardias_feriado'
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['es_nacional', 'es_provincial', 'es_local']),
        ]
    
    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"

class ReglaPlus(models.Model):
    """Reglas para cálculo de plus salarial"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    
    # Condiciones
    horas_minimas_diarias = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    horas_minimas_mensuales = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Tipos de área aplicables
    aplica_areas_operativas = models.BooleanField(default=True)
    aplica_areas_administrativas = models.BooleanField(default=True)
    
    # Plus a aplicar
    porcentaje_plus = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ej: 20.00 para 20%, 40.00 para 40%")
    
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reglas_plus_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reglas_plus_actualizadas')
    
    class Meta:
        db_table = 'guardias_regla_plus'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(vigente_hasta__isnull=True) | models.Q(vigente_hasta__gt=models.F('vigente_desde')),
                name='vigencia_regla_plus_valida'
            ),
            models.CheckConstraint(
                condition=models.Q(porcentaje_plus__gte=0) & models.Q(porcentaje_plus__lte=100),
                name='porcentaje_plus_valido'
            )
        ]
        indexes = [
            models.Index(fields=['vigente_desde', 'vigente_hasta', 'activa']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.porcentaje_plus}%"

class CronogramaGuardias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=40, blank=True, null=True)
    estado = models.CharField(max_length=30, default='generada', choices=[
        ('generada', 'Generada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('publicada', 'Publicada')
    ])
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='cronogramas_creados')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='cronogramas_actualizados')
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='cronogramas_aprobados')
    aprobado_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F('hora_inicio')),
                name='hora_fin_mayor_inicio'
            )
        ]
        indexes = [
            models.Index(fields=['area', 'fecha', 'hora_inicio', 'hora_fin'])
        ]

class Guardia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(CronogramaGuardias, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardias_asignadas')
    fecha = models.DateField()
    
    # Asistencia real (NULL si no asistió)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    
    tipo = models.CharField(max_length=40, blank=True, null=True)
    activa = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, default='borrador', choices=[
        ('borrador', 'Borrador'),
        ('aprobada', 'Aprobada'),
        ('publicada', 'Publicada'),
        ('anulada', 'Anulada')
    ])
    
    # Control de horas
    horas_planificadas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horas_efectivas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='guardias_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='guardias_actualizadas')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_inicio__isnull=True, hora_fin__isnull=True) |
                         models.Q(hora_inicio__isnull=False, hora_fin__isnull=False, hora_fin__gt=models.F('hora_inicio')),
                name='horas_consistentes'
            )
        ]
        unique_together = ['cronograma', 'usuario', 'fecha']

class HorasGuardias(models.Model):
    """Resumen mensual de horas por agente"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumen_horas_guardias')
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    
    # Período
    año = models.IntegerField()
    mes = models.IntegerField()  # 1-12
    
    # Totales
    horas_planificadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    horas_efectivas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    guardias_totales = models.IntegerField(default=0)
    guardias_cumplidas = models.IntegerField(default=0)
    
    # Plus calculado
    plus_aplicable = models.BooleanField(default=False)
    porcentaje_plus = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    regla_plus_aplicada = models.ForeignKey(ReglaPlus, on_delete=models.SET_NULL, null=True, blank=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='resumenes_horas_creados')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='resumenes_horas_actualizados')
    
    class Meta:
        db_table = 'guardias_horas_guardias'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(mes__gte=1) & models.Q(mes__lte=12),
                name='mes_valido'
            ),
            models.CheckConstraint(
                condition=models.Q(año__gte=2020),
                name='año_valido'
            ),
            models.CheckConstraint(
                condition=models.Q(guardias_cumplidas__lte=models.F('guardias_totales')),
                name='guardias_cumplidas_validas'
            )
        ]
        unique_together = ['agente', 'area', 'año', 'mes']
        indexes = [
            models.Index(fields=['agente', 'año', 'mes']),
            models.Index(fields=['area', 'año', 'mes']),
        ]
    
    def __str__(self):
        return f"Resumen {self.agente} - {self.año}/{self.mes:02d}"

class AsignacionPlus(models.Model):
    """Asignaciones calculadas de plus"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asignaciones_plus')
    resumen_horas = models.ForeignKey(HorasGuardias, on_delete=models.CASCADE, related_name='asignaciones_plus')
    regla_plus = models.ForeignKey(ReglaPlus, on_delete=models.CASCADE)
    
    # Cálculo
    porcentaje_aplicado = models.DecimalField(max_digits=5, decimal_places=2)
    monto_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_plus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, default='calculado', choices=[
        ('calculado', 'Calculado'),
        ('aprobado', 'Aprobado'),
        ('pagado', 'Pagado'),
        ('anulado', 'Anulado')
    ])
    
    observaciones = models.TextField(blank=True, null=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='asignaciones_plus_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='asignaciones_plus_actualizadas')
    
    class Meta:
        db_table = 'guardias_asignacion_plus'
        unique_together = ['agente', 'resumen_horas', 'regla_plus']
        indexes = [
            models.Index(fields=['agente', 'estado']),
            models.Index(fields=['resumen_horas', 'estado']),
        ]
    
    def __str__(self):
        return f"Plus {self.agente} - {self.porcentaje_aplicado}%"