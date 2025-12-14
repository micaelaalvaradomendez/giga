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

def get_user_from_agente(agente):
    """Helper para encontrar el Usuario Django asociado a un Agente"""
    if not agente:
        return None
    try:
        return User.objects.filter(email=agente.email).first() or \
               User.objects.filter(username=agente.email).first() or \
               User.objects.filter(username=agente.dni).first()
    except Exception as e:
        logger.error(f"Error encontrando usuario para agente {agente.id_agente}: {e}")
        return None

def get_users_by_role(role_name):
    """Helper para encontrar Usuarios con un nombre de rol específico vía AgenteRol"""
    agente_ids = AgenteRol.objects.filter(id_rol__nombre=role_name).values_list('id_agente', flat=True)
    agentes = Agente.objects.filter(id_agente__in=agente_ids)
    users = []
    for ag in agentes:
        u = get_user_from_agente(ag)
        if u: users.append(u)
    return users


@receiver(post_save, sender=Guardia)
def notificar_guardia_asignada(sender, instance, created, **kwargs):
    if created and instance.id_agente:
        user = get_user_from_agente(instance.id_agente)
        if user:
            Notificacion.objects.create(
                usuario=user,
                titulo="Nueva Guardia Asignada",
                mensaje=f"Se te ha asignado una guardia para el día {instance.fecha}",
                tipo="GUARDIA",
                link="/guardias"
            )


        user = get_user_from_agente(instance.id_agente)
        if user:
            Notificacion.objects.create(
                usuario=user,
                titulo="Compensación Aprobada",
                mensaje=f"Se te ha aprobado una compensación de {instance.horas_extra}hs por el servicio del {instance.fecha_servicio}",
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
        user = get_user_from_agente(instance.creado_por)
        if user:
            Notificacion.objects.create(
                usuario=user,
                titulo="Actualización de Incidencia",
                mensaje=f"La incidencia {instance.numero} ha cambiado de estado a: {instance.get_estado_display()}",
                tipo="INCIDENCIA",
                link=f"/incidencias/{instance.pk}"
            )

    if instance.es_correccion:
        user = get_user_from_agente(instance.id_agente)
        if user:
            Notificacion.objects.create(
                usuario=user,
                titulo="Corrección de Asistencia",
                mensaje=f"Se ha registrado una corrección en tu asistencia del {instance.fecha}",
                tipo="ASISTENCIA",
                link="/asistencia"
            )
        
        if instance.id_area and instance.id_area.jefe_area:
             jefe_user = get_user_from_agente(instance.id_area.jefe_area)
             if jefe_user and jefe_user != user:
                 Notificacion.objects.create(
                    usuario=jefe_user,
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
            user = get_user_from_agente(instance)
            if user:
                Notificacion.objects.create(
                    usuario=user,
                    titulo="Actualización de Datos",
                    mensaje="Tus datos personales han sido actualizados en el sistema",
                    tipo="USUARIO",
                    link="/perfil"
                )

@receiver(post_save, sender=Licencia)
def notificar_licencia(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_estado') and instance._old_estado != instance.estado:
        user = get_user_from_agente(instance.id_agente)
        if user:
            estado_msg = "aprobada" if instance.estado == 'aprobada' else "rechazada"
            if instance.estado in ['aprobada', 'rechazada']:
                Notificacion.objects.create(
                    usuario=user,
                    titulo=f"Licencia {estado_msg.capitalize()}",
                    mensaje=f"Tu solicitud de licencia ha sido {estado_msg}",
                    tipo="LICENCIA",
                    link="/licencias"
                )
    
    if not created and instance.estado == 'aprobada' and (not hasattr(instance, '_old_estado') or instance._old_estado != 'aprobada'):
        agente = instance.id_agente
        if agente and agente.id_area and agente.id_area.jefe_area:
            jefe_user = get_user_from_agente(agente.id_area.jefe_area)
            # No notificar si el jefe es quien solicitó (check opcional, se omite por simplicidad)
            if jefe_user:
                Notificacion.objects.create(
                    usuario=jefe_user,
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
            user = get_user_from_agente(agente)
            if user:
                notificaciones.append(Notificacion(
                    usuario=user,
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
        user = get_user_from_agente(agente)
        if user:
            notificaciones.append(Notificacion(
                usuario=user,
                titulo=titulo,
                mensaje=mensaje,
                tipo="ORGANIGRAMA",
                link="/organigrama"
            ))
            
    if notificaciones:
        Notificacion.objects.bulk_create(notificaciones)



@receiver(post_save, sender=AgenteRol)
def notificar_nuevo_rol(sender, instance, created, **kwargs):
    if created:
        user = get_user_from_agente(instance.id_agente)
        if user:
             Notificacion.objects.create(
                usuario=user,
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
                    usuario=user,
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
                    usuario=director,
                    titulo="Cronograma Pendiente de Aprobación",
                    mensaje=f"Hay un cronograma pendiente para el área {instance.id_area.nombre}",
                    tipo="CRONOGRAMA",
                    link="/paneladmin/guardias/aprobaciones"
                )
        elif estado in ['aprobada', 'publicada']:
            if instance.id_jefe:
                jefe_user = get_user_from_agente(instance.id_jefe)
                if jefe_user:
                     Notificacion.objects.create(
                        usuario=jefe_user,
                        titulo="Cronograma Aprobado",
                        mensaje=f"El cronograma de {instance.id_area.nombre} ha sido aprobado/publicado",
                        tipo="CRONOGRAMA",
                        link="/guardias"
                    )
