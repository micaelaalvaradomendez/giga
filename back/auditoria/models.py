from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from personas.models import Agente
import uuid

class Auditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_actualizadas')
    nombre_tabla = models.CharField(max_length=255)
    pk_afectada = models.CharField(max_length=255)
    accion = models.CharField(max_length=20, choices=[
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete')
    ])
    valor_previo = models.JSONField(null=True, blank=True)
    valor_nuevo = models.JSONField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['nombre_tabla', 'pk_afectada', 'creado_en'])
        ]