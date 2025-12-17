"""
Signals para el envío automático de emails y auditoría de incidencias.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Incidencia
from .email_service import IncidenciaEmailService
from auditoria.models import Auditoria
import logging

logger = logging.getLogger(__name__)


def registrar_auditoria(accion, incidencia, valor_previo=None, valor_nuevo=None, agente=None):
    """Registrar acción en auditoría"""
    try:
        Auditoria.objects.create(
            pk_afectada=incidencia.id,
            nombre_tabla='incidencia',
            creado_en=timezone.now(),
            valor_previo=valor_previo,
            valor_nuevo=valor_nuevo,
            accion=accion,
            id_agente=agente
        )
    except Exception as e:
        logger.error(f"Error al registrar auditoría de incidencia: {str(e)}")


@receiver(post_save, sender=Incidencia)
def enviar_email_nueva_incidencia(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar una incidencia.
    Envía email y registra auditoría cuando se crea una nueva incidencia.
    """
    if created:
        # Registrar creación en auditoría
        valor_nuevo = {
            'numero': instance.numero,
            'titulo': instance.titulo,
            'estado': instance.estado,
            'prioridad': instance.prioridad,
            'creado_por': f"{instance.creado_por.nombre} {instance.creado_por.apellido}",
            'area': instance.area_involucrada.nombre if instance.area_involucrada else None,
        }
        
        if instance.asignado_a:
            valor_nuevo['asignado_a'] = f"{instance.asignado_a.nombre} {instance.asignado_a.apellido}"
        
        registrar_auditoria(
            accion='CREAR',
            incidencia=instance,
            valor_nuevo=valor_nuevo,
            agente=instance.creado_por
        )
        
        # Enviar email si tiene agente asignado
        if instance.asignado_a:
            logger.info(f"Nueva incidencia {instance.numero} creada y asignada a {instance.asignado_a.nombre}")
            IncidenciaEmailService.enviar_notificacion_asignacion(instance)


@receiver(pre_save, sender=Incidencia)
def detectar_cambios(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de guardar una incidencia.
    Detecta cambios en asignación, estado y resolución.
    """
    if instance.pk:  # Solo para incidencias existentes (no nuevas)
        try:
            incidencia_anterior = Incidencia.objects.get(pk=instance.pk)
            
            # Detectar cambio de asignación
            if (incidencia_anterior.asignado_a != instance.asignado_a and 
                instance.asignado_a is not None):
                
                logger.info(f"Incidencia {instance.numero} reasignada de "
                           f"{incidencia_anterior.asignado_a} a {instance.asignado_a}")
                
                instance._enviar_email_asignacion = True
                instance._cambio_asignacion = {
                    'previo': f"{incidencia_anterior.asignado_a.nombre} {incidencia_anterior.asignado_a.apellido}" if incidencia_anterior.asignado_a else None,
                    'nuevo': f"{instance.asignado_a.nombre} {instance.asignado_a.apellido}"
                }
            else:
                instance._enviar_email_asignacion = False
                instance._cambio_asignacion = None
            
            # Detectar cambio de estado
            if incidencia_anterior.estado != instance.estado:
                instance._cambio_estado = {
                    'previo': incidencia_anterior.estado,
                    'nuevo': instance.estado
                }
            else:
                instance._cambio_estado = None
            
            # Detectar resolución
            if not incidencia_anterior.fecha_resolucion and instance.fecha_resolucion:
                instance._fue_resuelta = True
            else:
                instance._fue_resuelta = False
                
        except Incidencia.DoesNotExist:
            # La incidencia no existe previamente, es nueva
            instance._enviar_email_asignacion = False
            instance._cambio_asignacion = None
            instance._cambio_estado = None
            instance._fue_resuelta = False


@receiver(post_save, sender=Incidencia)
def registrar_cambios(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar una incidencia.
    Registra auditoría y envía emails para cambios.
    """
    if not created:
        # Registrar cambio de asignación
        if getattr(instance, '_cambio_asignacion', None):
            registrar_auditoria(
                accion='ASIGNAR' if instance._cambio_asignacion['previo'] is None else 'REASIGNAR',
                incidencia=instance,
                valor_previo={'asignado_a': instance._cambio_asignacion['previo']},
                valor_nuevo={'asignado_a': instance._cambio_asignacion['nuevo']},
                agente=instance.creado_por
            )
        
        # Registrar cambio de estado
        if getattr(instance, '_cambio_estado', None):
            registrar_auditoria(
                accion='CAMBIAR_ESTADO',
                incidencia=instance,
                valor_previo={'estado': instance._cambio_estado['previo']},
                valor_nuevo={'estado': instance._cambio_estado['nuevo']},
                agente=instance.creado_por
            )
        
        # Registrar resolución
        if getattr(instance, '_fue_resuelta', False):
            registrar_auditoria(
                accion='RESOLVER',
                incidencia=instance,
                valor_nuevo={
                    'resolucion': instance.resolucion[:100] if instance.resolucion else None,
                    'fecha_resolucion': str(instance.fecha_resolucion)
                },
                agente=instance.creado_por
            )
        
        # Enviar email de reasignación
        if getattr(instance, '_enviar_email_asignacion', False):
            logger.info(f"Enviando email de reasignación para incidencia {instance.numero}")
            IncidenciaEmailService.enviar_notificacion_asignacion(instance)
        
        # Limpiar flags
        for attr in ['_enviar_email_asignacion', '_cambio_asignacion', '_cambio_estado', '_fue_resuelta']:
            if hasattr(instance, attr):
                delattr(instance, attr)