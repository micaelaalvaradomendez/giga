from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from personas.models import Agente, Area
from datetime import date
import uuid

# back/guardias/models.py

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