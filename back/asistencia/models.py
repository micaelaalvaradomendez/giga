from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from personas.models import Agente, Area
import uuid

class TipoLicencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=255, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

class ParteDiario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    fecha_parte = models.DateField()
    estado = models.CharField(max_length=20, default='borrador', choices=[
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('anulado', 'Anulado')
    ])
    observaciones = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.CASCADE)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='partes_creados')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='partes_actualizados')
    
    class Meta:
        indexes = [
            models.Index(fields=['area', 'fecha_parte', 'agente'])
        ]