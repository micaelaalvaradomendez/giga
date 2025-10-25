"""
ViewSets  s para el módulo auditoría
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, timezone
)
from django.db.models import Count, Q
from datetime import timedelta
from .models import Auditoria
from .serializers import AuditoriaSerializer


class AuditoriaViewSet(GIGAReadOnlyViewSet):
    """
    ViewSet   para consulta de registros de auditoría
    Solo lectura - los registros se crean automáticamente
    """
    queryset = Auditoria.objects.all().select_related('creado_por')
    serializer_class = AuditoriaSerializer
    search_fields = ['nombre_tabla', 'accion', 'pk_afectada']
    filterset_fields = ['nombre_tabla', 'accion', 'creado_por']
    ordering_fields = ['creado_en', 'nombre_tabla', 'accion']
    ordering = ['-creado_en']

    @action(detail=False, methods=['get'])
    @require_authenticated
    def por_usuario(self, request):
        """Obtener registros de auditoría por usuario"""
        usuario_id = request.query_params.get('usuario')
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        
        if not usuario_id:
            return create_error_response('Se requiere parámetro usuario')
        
        queryset = self.queryset.filter(creado_por_id=usuario_id)
        
        if fecha_desde:
            queryset = queryset.filter(creado_en__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(creado_en__lte=fecha_hasta)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @require_authenticated
    def por_tabla(self, request):
        """Obtener registros de auditoría por tabla/modelo"""
        tabla = request.query_params.get('tabla')
        pk_afectada = request.query_params.get('pk')
        
        if not tabla:
            return create_error_response('Se requiere parámetro tabla')
        
        queryset = self.queryset.filter(nombre_tabla=tabla)
        
        if pk_afectada:
            queryset = queryset.filter(pk_afectada=pk_afectada)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @require_authenticated
    def resumen(self, request):
        """Obtener resumen de actividad de auditoría"""
        # Último periodo (últimos 30 días)
        fecha_desde = timezone.now() - timedelta(days=30)
        
        registros_periodo = self.queryset.filter(creado_en__gte=fecha_desde)
        
        # Estadísticas por acción
        por_accion = registros_periodo.values('accion').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Estadísticas por tabla
        por_tabla = registros_periodo.values('nombre_tabla').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Usuarios más activos
        por_usuario = registros_periodo.values('creado_por__username').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        return Response({
            'periodo': {
                'desde': fecha_desde.date(),
                'hasta': timezone.now().date()
            },
            'total_registros': registros_periodo.count(),
            'por_accion': list(por_accion),
            'tablas_mas_modificadas': list(por_tabla),
            'usuarios_mas_activos': list(por_usuario)
        })

    @action(detail=False, methods=['get'])
    @require_authenticated  
    def exportar(self, request):
        """Exportar registros de auditoría en formato CSV"""
        import csv
        from django.http import HttpResponse
        
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        tabla = request.query_params.get('tabla')
        
        queryset = self.queryset.all()
        
        # Aplicar filtros
        if fecha_desde:
            queryset = queryset.filter(creado_en__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(creado_en__lte=fecha_hasta)
        if tabla:
            queryset = queryset.filter(nombre_tabla=tabla)
        
        # Crear response CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="auditoria.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Fecha', 'Usuario', 'Tabla', 'Registro ID', 'Acción',
            'Valor Anterior', 'Valor Nuevo'
        ])
        
        for registro in queryset[:1000]:  # Limitar a 1000 registros
            writer.writerow([
                registro.creado_en.strftime('%Y-%m-%d %H:%M:%S'),
                registro.creado_por.username if registro.creado_por else 'Sistema',
                registro.nombre_tabla,
                registro.pk_afectada,
                registro.accion,
                registro.valor_previo or '',
                registro.valor_nuevo or ''
            ])
        
        return response

    @action(detail=False, methods=['get'])
    @require_authenticated
    def actividad_reciente(self, request):
        """Obtener actividad reciente (últimas 24 horas)"""
        fecha_desde = timezone.now() - timedelta(hours=24)
        
        registros = self.queryset.filter(
            creado_en__gte=fecha_desde
        ).select_related('creado_por')[:50]
        
        serializer = self.get_serializer(registros, many=True)
        
        return Response({
            'periodo': '24 horas',
            'total': registros.count(),
            'registros': serializer.data
        })