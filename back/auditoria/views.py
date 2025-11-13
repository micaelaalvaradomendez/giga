from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Auditoria
from .serializers import AuditoriaSerializer


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
@permission_classes([AllowAny])  # Usamos AllowAny y verificamos manualmente
def registros_auditoria(request):
    """API endpoint para obtener registros de auditoría"""
    try:
        # Verificar autenticación manualmente usando el mismo sistema que check_session
        user_id = request.session.get('user_id')
        is_authenticated = request.session.get('is_authenticated', False)
        
        if not user_id or not is_authenticated:
            return Response({
                'error': 'No autenticado',
                'message': 'Debe iniciar sesión para acceder a este recurso'
            }, status=403)
        
        # Obtener todos los registros con información del agente
        registros = Auditoria.objects.select_related('id_agente').order_by('-creado_en')
        
        # Aplicar filtros si se proporcionan
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
