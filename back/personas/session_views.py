"""
Endpoint para cerrar todas las sesiones activas de un usuario
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from personas.models import Agente, SesionActiva
from django.contrib.sessions.models import Session
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acceso público (verificación por token en query)
def cerrar_todas_sesiones(request):
    """
    Cierra todas las sesiones activas de un agente.
    Usado cuando el usuario recibe email de alerta y quiere cerrar todo.
    Ahora: elimina también las filas de SesionActiva para no acumular datos.
    """
    try:
        # Obtener agente_id del token (simplificado)
        agente_id = request.data.get('agente_id') or request.GET.get('token')
        
        if not agente_id:
            return Response({
                'success': False,
                'message': 'Token de usuario requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            agente = Agente.objects.get(id_agente=agente_id, activo=True)
        except Agente.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener todas las sesiones activas del usuario
        sesiones_activas = SesionActiva.objects.filter(
            id_agente=agente,
            activa=True
        )
        
        count = sesiones_activas.count()
        
        if count == 0:
            return Response({
                'success': True,
                'message': 'No hay sesiones activas para cerrar',
                'sesiones_cerradas': 0
            })
        
        # Obtener session_keys antes de eliminarlas
        session_keys = list(sesiones_activas.values_list('session_key', flat=True))
        
        # En una transacción: eliminar sesiones Django y filas de SesionActiva
        with transaction.atomic():
            # Eliminar de django_session
            Session.objects.filter(session_key__in=session_keys).delete()
            # Eliminar registros de SesionActiva para liberar espacio
            SesionActiva.objects.filter(session_key__in=session_keys).delete()
        
        # Registrar en auditoría
        from personas.auth_views import registrar_auditoria
        registrar_auditoria(
            agente.id_agente,
            "CIERRE_MASIVO_SESIONES",
            f"Usuario cerró todas sus sesiones ({count}) por seguridad"
        )
        
        logger.info(f"Cerradas {count} sesiones del agente {agente.id_agente}")
        
        return Response({
            'success': True,
            'message': f'Se cerraron {count} sesión(es) exitosamente',
            'sesiones_cerradas': count
        })
        
    except Exception as e:
        logger.error(f"Error cerrando sesiones: {e}")
        return Response({
            'success': False,
            'message': 'Error al cerrar sesiones'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
