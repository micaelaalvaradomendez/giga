from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Auditoria
from .serializers import AuditoriaSerializer

# RBAC Permissions
from common.permissions import IsAuthenticatedGIGA


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consulta de registros de auditoría (solo lectura)"""
    
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        accion = self.request.query_params.get('accion')
        tabla = self.request.query_params.get('tabla')
        agente_id = self.request.query_params.get('agente')
        
        if fecha_desde:
            queryset = queryset.filter(creado_en__date__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(creado_en__date__lte=fecha_hasta)
            
        if accion:
            queryset = queryset.filter(accion__icontains=accion)
            
        if tabla:
            queryset = queryset.filter(nombre_tabla__icontains=tabla)
            
        if agente_id:
            queryset = queryset.filter(id_agente=agente_id)
        
        return queryset.order_by('-creado_en')


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC: Solo usuarios autenticados
def registros_auditoria(request):
    """API endpoint para obtener registros de auditoría con filtrado jerárquico por rol"""
    try:
        # Verificar autenticación manualmente usando el mismo sistema que check_session
        user_id = request.session.get('user_id')
        is_authenticated = request.session.get('is_authenticated', False)
        
        if not user_id or not is_authenticated:
            return Response({
                'error': 'No autenticado',
                'message': 'Debe iniciar sesión para acceder a este recurso'
            }, status=403)
        
        # Obtener agente y su rol desde el sistema de permisos
        from common.permissions import obtener_agente_sesion, obtener_rol_agente, obtener_areas_jerarquia
        from personas.models import Agente
        
        agente = obtener_agente_sesion(request)
        if not agente:
            return Response({
                'error': 'Usuario no encontrado',
                'message': 'No se pudo obtener información del usuario'
            }, status=403)
        
        rol = obtener_rol_agente(agente)
        
        # Verificar que el rol tenga permisos para ver auditoría
        if rol not in ['administrador', 'director', 'jefatura']:
            return Response({
                'error': 'Acceso denegado',
                'message': 'No tiene permisos para acceder a la auditoría'
            }, status=403)
        
        # Obtener todos los registros con información del agente
        registros = Auditoria.objects.select_related('id_agente').order_by('-creado_en')
        
        # Filtrar por áreas según el rol del usuario
        if rol == 'administrador':
            # Administrador ve toda la auditoría del sistema
            pass  # No filtrar por área
        elif rol == 'director':
            # Director ve auditoría de su área + sub-áreas
            areas_accesibles = obtener_areas_jerarquia(agente)
            area_ids = [area.id_area for area in areas_accesibles]
            registros = registros.filter(id_agente__id_area__in=area_ids)
        elif rol == 'jefatura':
            # Jefatura ve auditoría solo de su área (sin sub-áreas)
            if agente.id_area:
                registros = registros.filter(id_agente__id_area=agente.id_area)
            else:
                # Si no tiene área asignada, no ve nada
                registros = registros.none()
        
        # Aplicar filtros adicionales si se proporcionan
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        accion = request.query_params.get('accion')
        tabla = request.query_params.get('tabla')
        
        if fecha_desde:
            registros = registros.filter(creado_en__date__gte=fecha_desde)
        
        if fecha_hasta:
            registros = registros.filter(creado_en__date__lte=fecha_hasta)
            
        if accion:
            registros = registros.filter(accion__icontains=accion)
            
        if tabla:
            registros = registros.filter(nombre_tabla__icontains=tabla)
        
        # Serializar los datos
        data = []
        for registro in registros:
            agente_info = None
            if registro.id_agente:
                agente_info = {
                    'id': registro.id_agente.id,
                    'nombre': registro.id_agente.nombre,
                    'apellido': registro.id_agente.apellido,
                    'legajo': registro.id_agente.legajo
                }
            
            data.append({
                'id_auditoria': registro.id_auditoria,
                'pk_afectada': registro.pk_afectada,
                'nombre_tabla': registro.nombre_tabla,
                'creado_en': registro.creado_en,
                'valor_previo': registro.valor_previo,
                'valor_nuevo': registro.valor_nuevo,
                'accion': registro.accion,
                'id_agente': agente_info,
                'creado_por_nombre': f"{registro.id_agente.nombre} {registro.id_agente.apellido}".strip() if registro.id_agente else 'Sistema'
            })
        
        return Response({
            'count': len(data),
            'results': data
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'count': 0,
            'results': []
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir sin autenticación para registrar intentos fallidos
def log_unauthorized_access(request):
    """
    Registra intentos de acceso no autorizados en auditoría
    """
    try:
        from django.utils import timezone
        
        # Obtener datos del request
        nombre_tabla = request.data.get('nombre_tabla', 'sistema_acceso')
        accion = request.data.get('accion', 'ACCESO_DENEGADO')
        pk_afectada = request.data.get('pk_afectada', 0)
        valor_nuevo = request.data.get('valor_nuevo', {})
        
        # Crear registro de auditoría
        auditoria = Auditoria.objects.create(
            nombre_tabla=nombre_tabla,
            accion=accion,
            pk_afectada=pk_afectada,
            valor_nuevo=valor_nuevo,
            id_agente_id=pk_afectada if pk_afectada > 0 else None,
            creado_en=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': 'Evento de acceso no autorizado registrado',
            'audit_id': auditoria.id_auditoria
        }, status=201)
        
    except Exception as e:
        # No fallar si hay error en auditoría, solo loguear
        print(f"Error al registrar auditoría: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error al registrar auditoría: {str(e)}'
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # Requiere autenticación para accesos exitosos
def log_successful_access(request):
    """
    Registra accesos exitosos al sistema en auditoría
    """
    try:
        from django.utils import timezone
        
        # Obtener datos del request
        nombre_tabla = request.data.get('nombre_tabla', 'sistema_acceso')
        accion = request.data.get('accion', 'ACCESO_EXITOSO')
        pk_afectada = request.data.get('pk_afectada')
        valor_nuevo = request.data.get('valor_nuevo', {})
        
        # Crear registro de auditoría
        auditoria = Auditoria.objects.create(
            nombre_tabla=nombre_tabla,
            accion=accion,
            pk_afectada=pk_afectada,
            valor_nuevo=valor_nuevo,
            id_agente_id=pk_afectada if pk_afectada else None,
            creado_en=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': 'Acceso exitoso registrado',
            'audit_id': auditoria.id_auditoria
        }, status=201)
        
    except Exception as e:
        # No fallar si hay error en auditoría, solo loguear
        print(f"Error al registrar auditoría: {str(e)}")
        return Response({
            'success': False,
            'message': f'Error al registrar auditoría: {str(e)}'
        }, status=500)
