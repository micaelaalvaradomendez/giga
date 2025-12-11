"""
Servicio de notificaciones por email para incidencias.
Maneja el envío de emails automáticos cuando se asignan incidencias.
"""

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class IncidenciaEmailService:
    """Servicio para envío de emails relacionados con incidencias"""
    
    @staticmethod
    def enviar_notificacion_asignacion(incidencia):
        """
        Envía un email al agente cuando se le asigna una nueva incidencia.
        
        Args:
            incidencia: Instancia de Incidencia recién asignada
        
        Returns:
            bool: True si el email se envió correctamente, False en caso contrario
        """
        if not incidencia.asignado_a:
            logger.warning(f"Incidencia {incidencia.numero} no tiene agente asignado")
            return False
            
        # Obtener email del agente asignado
        agente_email = IncidenciaEmailService._obtener_email_agente(incidencia.asignado_a)
        if not agente_email:
            logger.warning(f"Agente {incidencia.asignado_a.nombre} no tiene email configurado")
            return False
        
        try:
            # Preparar datos para el template unificado
            context = {
                'incidencia': incidencia,
                'destinatario': incidencia.asignado_a,
                'notificacion_tipo': 'Nueva Asignación de Incidencia',
                'mensaje_principal': 'Se te ha asignado una nueva incidencia que requiere tu atención.',
                'fecha_actual': timezone.now(),
                'sistema_url': f'{settings.FRONTEND_URL}/incidencias'
            }
            
            # Renderizar template HTML unificado
            html_message = render_to_string('emails/incidencia_notificacion.html', context)
            plain_message = strip_tags(html_message)
            
            # Asunto del email
            subject = f'Nueva Asignación - {incidencia.numero}: {incidencia.titulo}'
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agente_email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email enviado correctamente a {agente_email} para incidencia {incidencia.numero}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email para incidencia {incidencia.numero}: {e}")
            return False
    
    @staticmethod
    def _obtener_email_agente(agente):
        """
        Obtiene el email de un agente. Busca en el modelo User relacionado.
        
        Args:
            agente: Instancia de Agente
            
        Returns:
            str: Email del agente o None si no se encuentra
        """
        try:
            # Buscar el usuario Django asociado al agente
            from django.contrib.auth.models import User
            
            # Buscar por DNI (asumiendo que el username es el DNI)
            user = User.objects.filter(username=agente.dni).first()
            if user and user.email:
                return user.email
            
            # Buscar por email directo si el modelo Agente tiene campo email
            if hasattr(agente, 'email') and agente.email:
                return agente.email
            
            # Generar email corporativo basado en nombre y apellido
            email_corporativo = f"{agente.nombre.lower()}.{agente.apellido.lower()}@proteccioncivil.tdf.gov.ar"
            logger.info(f"Usando email corporativo generado: {email_corporativo}")
            return email_corporativo
            
        except Exception as e:
            logger.error(f"Error obteniendo email para agente {agente.dni}: {e}")
            return None
    
    @staticmethod
    def enviar_notificacion_cambio_estado(incidencia, estado_anterior, nuevo_estado, email_destino, agente_destino):
        """
        Envía un email cuando cambia el estado de una incidencia.
        
        Args:
            incidencia: Instancia de Incidencia
            estado_anterior: Estado previo de la incidencia
            nuevo_estado: Nuevo estado de la incidencia
            email_destino: Email del destinatario
            agente_destino: Agente que recibirá la notificación
            
        Returns:
            bool: True si el email se envió correctamente, False en caso contrario
        """
        try:
            # Obtener las etiquetas legibles de los estados
            estados_dict = dict(incidencia.ESTADO_CHOICES)
            estado_anterior_texto = estados_dict.get(estado_anterior, estado_anterior)
            nuevo_estado_texto = estados_dict.get(nuevo_estado, nuevo_estado)
            
            # Preparar datos para el template
            context = {
                'incidencia': incidencia,
                'destinatario': agente_destino,
                'notificacion_tipo': 'Cambio de Estado de Incidencia',
                'mensaje_principal': f'El estado de la incidencia ha cambiado de "{estado_anterior_texto}" a "{nuevo_estado_texto}".',
                'estado_anterior': estado_anterior_texto,
                'nuevo_estado': nuevo_estado_texto,
                'fecha_actual': timezone.now(),
                'sistema_url': f'{settings.FRONTEND_URL}/incidencias/{incidencia.id}'
            }
            
            # Renderizar template HTML
            html_message = render_to_string('emails/incidencia_notificacion.html', context)
            plain_message = strip_tags(html_message)
            
            # Asunto del email
            subject = f'Cambio de Estado - {incidencia.numero}: {nuevo_estado_texto}'
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_destino],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email de cambio de estado enviado correctamente a {email_destino} para incidencia {incidencia.numero}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de cambio de estado para incidencia {incidencia.numero}: {e}")
            return False