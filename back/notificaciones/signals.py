from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from .models import Notificacion
from guardias.models import Guardia, HoraCompensacion, Feriado, Cronograma
from asistencia.models import Licencia, Asistencia
from incidencias.models import Incidencia
from personas.models import Agente, AgenteRol, Organigrama, SesionActiva
import logging

logger = logging.getLogger(__name__)


def get_users_by_role(role_name):
    """Helper para encontrar Agentes con un nombre de rol específico vía AgenteRol"""
    agente_ids = AgenteRol.objects.filter(id_rol__nombre=role_name).values_list('id_agente', flat=True)
    return Agente.objects.filter(id_agente__in=agente_ids)


@receiver(post_save, sender=Guardia)
def notificar_guardia_asignada(sender, instance, created, **kwargs):
    try:
        # Solo notificar si el cronograma ya está aprobado o publicado
        should_notify = False
        try:
             if instance.id_cronograma.estado in ['aprobada', 'publicada']:
                 should_notify = True
        except:
             # Si falla el acceso al cronograma, por seguridad no notificamos (o asumimos draft)
             should_notify = False

        if created and instance.id_agente and should_notify:
            Notificacion.objects.create(
                agente=instance.id_agente,
                titulo="Nueva Guardia Asignada",
                mensaje=f"Se te ha asignado una guardia para el día {instance.fecha}",
                tipo="GUARDIA",
                link="/guardias"
            )
    except Exception as e:
        logger.error(f"Error creando notificación de guardia: {e}")

@receiver(pre_save, sender=HoraCompensacion)
def track_compensacion_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = HoraCompensacion.objects.get(pk=instance.pk)
            instance._old_estado = old.estado
        except:
            instance._old_estado = None
    else:
        instance._old_estado = None

@receiver(post_save, sender=HoraCompensacion)
def notificar_compensacion(sender, instance, created, **kwargs):
    old_estado = getattr(instance, '_old_estado', None)
    
    if not created and old_estado != 'aprobada' and instance.estado == 'aprobada':
        if instance.id_agente:
             Notificacion.objects.create(
                agente=instance.id_agente,
                titulo="Compensación Aprobada",
                mensaje=f"Se te ha aprobado una compensación de {instance.horas_extra}hs por el servicio del {instance.fecha_servicio}",
                tipo="HORA_EXTRA",
                link="/guardias/compensaciones"
            )
            
    if not created and old_estado != 'rechazada' and instance.estado == 'rechazada':
        if instance.id_agente:
             Notificacion.objects.create(
                agente=instance.id_agente,
                titulo="Compensación Rechazada",
                mensaje=f"Tu solicitud de compensación del {instance.fecha_servicio} ha sido rechazada",
                tipo="HORA_EXTRA",
                link="/guardias/compensaciones"
            )

@receiver(pre_save, sender=Incidencia)
def track_incidencia_state_change(sender, instance, **kwargs):
    try:
        if instance.pk:
            old_instance = Incidencia.objects.get(pk=instance.pk)
            instance._old_estado = old_instance.estado
        else:
            instance._old_estado = None
    except Incidencia.DoesNotExist:
        instance._old_estado = None

@receiver(post_save, sender=Incidencia)
def notificar_cambio_estado_incidencia(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_estado') and instance._old_estado != instance.estado:
        if instance.creado_por:
            Notificacion.objects.create(
                agente=instance.creado_por,
                titulo="Actualización de Incidencia",
                mensaje=f"La incidencia {instance.numero} ha cambiado de estado a: {instance.get_estado_display()}",
                tipo="INCIDENCIA",
                link=f"/incidencias/{instance.pk}"
            )

    if instance.es_correccion:
         if instance.id_agente:
            Notificacion.objects.create(
                agente=instance.id_agente,
                titulo="Corrección de Asistencia",
                mensaje=f"Se ha registrado una corrección en tu asistencia del {instance.fecha}",
                tipo="ASISTENCIA",
                link="/asistencia"
            )
        
         if instance.id_area and instance.id_area.jefe_area:
             if instance.id_area.jefe_area != instance.id_agente:
                 Notificacion.objects.create(
                    agente=instance.id_area.jefe_area,
                    titulo="Corrección de Asistencia en Área",
                    mensaje=f"Se corrigió asistencia de {instance.id_agente} en tu área",
                    tipo="ASISTENCIA",
                    link="/paneladmin/asistencias"
                )



@receiver(pre_save, sender=Agente)
def track_agente_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Agente.objects.get(pk=instance.pk)
            instance._old_data = {
                'nombre': old.nombre,
                'apellido': old.apellido,
                'dni': old.dni,
                'legajo': old.legajo
            }
        except:
            instance._old_data = {}
    else:
        instance._old_data = None

@receiver(post_save, sender=Agente)
def notificar_cambio_datos_agente(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_data') and instance._old_data:
        changed = False
        for field, old_val in instance._old_data.items():
            if getattr(instance, field) != old_val:
                changed = True
                break
        if changed:
            Notificacion.objects.create(
                agente=instance,
                titulo="Actualización de Datos",
                mensaje="Tus datos personales han sido actualizados en el sistema",
                tipo="USUARIO",
                link="/perfil"
            )

@receiver(pre_save, sender=Licencia)
def track_licencia_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Licencia.objects.get(pk=instance.pk)
            instance._old_estado = old.estado
        except:
            instance._old_estado = None
    else:
        instance._old_estado = None

@receiver(post_save, sender=Licencia)
def notificar_licencia(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_estado') and instance._old_estado != instance.estado:
        if instance.id_agente:
            estado_msg = "aprobada" if instance.estado == 'aprobada' else "rechazada"
            if instance.estado in ['aprobada', 'rechazada']:
                Notificacion.objects.create(
                    agente=instance.id_agente,
                    titulo=f"Licencia {estado_msg.capitalize()}",
                    mensaje=f"Tu solicitud de licencia ha sido {estado_msg}",
                    tipo="LICENCIA",
                    link="/licencias"
                )
    
    if not created and instance.estado == 'aprobada' and (not hasattr(instance, '_old_estado') or instance._old_estado != 'aprobada'):
        agente = instance.id_agente
        if agente and agente.id_area and agente.id_area.jefe_area:
             # Notificar al jefe de área
             if agente.id_area.jefe_area != agente:
                Notificacion.objects.create(
                    agente=agente.id_area.jefe_area,
                    titulo="Licencia Aprobada en Área",
                    mensaje=f"Se aprobó licencia para {agente.nombre} {agente.apellido}",
                    tipo="LICENCIA",
                    link="/paneladmin/licencias"
                )

@receiver(post_save, sender=Feriado)
def notificar_nuevo_feriado(sender, instance, created, **kwargs):
    if created:
        agentes_activos = Agente.objects.filter(activo=True)
        notificaciones = []
        
        titulo = "Nuevo Feriado"
        mensaje = f"Se ha agregado un nuevo feriado al calendario: {instance.nombre} ({instance.fecha_inicio})"
        
        for agente in agentes_activos:
            notificaciones.append(Notificacion(
                agente=agente,
                titulo=titulo,
                mensaje=mensaje,
                tipo="FERIADO",
                link="/calendario"
            ))
        
        if notificaciones:
            Notificacion.objects.bulk_create(notificaciones)

@receiver(post_save, sender=Organigrama)
def notificar_organigrama(sender, instance, created, **kwargs):
    titulo = "Actualización de Organigrama"
    mensaje = f"Se ha publicado una nueva versión del organigrama: {instance.nombre} (v{instance.version})"
    
    agentes_activos = Agente.objects.filter(activo=True)
    notificaciones = []
    
    for agente in agentes_activos:
        notificaciones.append(Notificacion(
            agente=agente,
            titulo=titulo,
            mensaje=mensaje,
            tipo="ORGANIGRAMA",
            link="/organigrama"
        ))
            
    if notificaciones:
        Notificacion.objects.bulk_create(notificaciones)



@receiver(post_save, sender=AgenteRol)
def notificar_nuevo_rol(sender, instance, created, **kwargs):
    if created and instance.id_agente:
         Notificacion.objects.create(
            agente=instance.id_agente,
            titulo="Nuevo Rol Asignado",
            mensaje=f"Se te ha asignado el rol: {instance.id_rol.nombre}",
            tipo="ROL",
            link="/perfil"
        )

@receiver(user_logged_in)
def notificar_concurrent_login(sender, request, user, **kwargs):
    try:
        agente = None
        if hasattr(user, 'agente'): 
            agente = user.agente
        elif hasattr(user, 'email'):
             agente = Agente.objects.filter(email=user.email).first()
        
        if agente:
            active_sessions = SesionActiva.objects.filter(id_agente=agente, activa=True)
            if active_sessions.count() > 1: 
                 Notificacion.objects.create(
                    agente=agente,
                    titulo="Inicio de Sesión Detectado",
                    mensaje="Se ha detectado un nuevo inicio de sesión en tu cuenta desde otro dispositivo",
                    tipo="LOGIN",
                    link="/perfil/seguridad"
                )
    except Exception as e:
        logger.error(f"Error verificando login concurrente: {e}")

@receiver(pre_save, sender=Cronograma)
def track_cronograma_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Cronograma.objects.get(pk=instance.pk)
            instance._old_estado = old.estado
        except:
             instance._old_estado = None
    else:
         instance._old_estado = None

@receiver(post_save, sender=Cronograma)
def notificar_cronograma(sender, instance, created, **kwargs):
    estado = instance.estado
    old_estado = getattr(instance, '_old_estado', None)
    
    if estado != old_estado:
        if estado == 'pendiente_aprobacion':
            directores = get_users_by_role('Director')
            for director in directores:
                Notificacion.objects.create(
                    agente=director,
                    titulo="Cronograma Pendiente de Aprobación",
                    mensaje=f"Hay un cronograma pendiente para el área {instance.id_area.nombre}",
                    tipo="CRONOGRAMA",
                    link="/paneladmin/guardias/aprobaciones"
                )
        elif estado in ['aprobada', 'publicada']:
            if instance.id_jefe:
                 Notificacion.objects.create(
                    agente=instance.id_jefe,
                    titulo="Cronograma Aprobado",
                    mensaje=f"El cronograma de {instance.id_area.nombre} ha sido aprobado/publicado",
                    tipo="CRONOGRAMA",
                    link="/guardias"
                )
            
            # Notificar a todos los agentes involucrados en el cronograma
            try:
                agentes_ids = Guardia.objects.filter(id_cronograma=instance).values_list('id_agente', flat=True).distinct()
                agentes = Agente.objects.filter(id_agente__in=agentes_ids)
                notificaciones_agentes = []
                for agente in agentes:
                    notificaciones_agentes.append(Notificacion(
                        agente=agente,
                        titulo="Aviso de Cronograma",
                        mensaje=f"Se ha publicado el cronograma de {instance.id_area.nombre}. Revisa tus guardias.",
                        tipo="CRONOGRAMA",
                        link="/guardias"
                    ))
                if notificaciones_agentes:
                    Notificacion.objects.bulk_create(notificaciones_agentes)
            except Exception as e:
                logger.error(f"Error notificando agentes del cronograma: {e}")
