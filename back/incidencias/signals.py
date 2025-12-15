"""
Signals para el envío automático de emails cuando se crean o asignan incidencias.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Incidencia
from .email_service import IncidenciaEmailService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Incidencia)
def enviar_email_nueva_incidencia(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar una incidencia.
    Envía email al agente asignado cuando se crea una nueva incidencia con asignación.
    """
    if created and instance.asignado_a:
        # Es una nueva incidencia Y tiene agente asignado
        logger.info(f"Nueva incidencia {instance.numero} creada y asignada a {instance.asignado_a.nombre}")
        IncidenciaEmailService.enviar_notificacion_asignacion(instance)


@receiver(pre_save, sender=Incidencia)
def detectar_cambio_asignacion(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de guardar una incidencia.
    Detecta si se está cambiando la asignación de agente.
    """
    if instance.pk:  # Solo para incidencias existentes (no nuevas)
        try:
            incidencia_anterior = Incidencia.objects.get(pk=instance.pk)
            
            # Verificar si cambió la asignación
            if (incidencia_anterior.asignado_a != instance.asignado_a and 
                instance.asignado_a is not None):
                
                logger.info(f"Incidencia {instance.numero} reasignada de "
                           f"{incidencia_anterior.asignado_a} a {instance.asignado_a}")
                
                # Marcar que se debe enviar email después del save
                instance._enviar_email_asignacion = True
            else:
                instance._enviar_email_asignacion = False
                
        except Incidencia.DoesNotExist:
            # La incidencia no existe previamente, es nueva
            instance._enviar_email_asignacion = False


@receiver(post_save, sender=Incidencia)
def enviar_email_reasignacion(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar una incidencia.
    Envía email cuando se reasigna una incidencia existente.
    """
    if not created and getattr(instance, '_enviar_email_asignacion', False):
        # Es una incidencia existente Y se marcó para enviar email
        logger.info(f"Enviando email de reasignación para incidencia {instance.numero}")
        IncidenciaEmailService.enviar_notificacion_asignacion(instance)
        
        # Limpiar el flag
        del instance._enviar_email_asignacion