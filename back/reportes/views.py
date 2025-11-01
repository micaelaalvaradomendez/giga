"""
ViewSets  s para el módulo reportes
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, GIGAViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, timezone
)
from django.db.models import Count, Q
from datetime import timedelta, datetime
from .models import Reporte, Notificacion, PlantillaCorreo, EnvioLoteNotificaciones, RenderCorreo, Vista
from .serializers import (ReporteSerializer, NotificacionSerializer, PlantillaCorreoSerializer, 
                         EnvioLoteNotificacionesSerializer, RenderCorreoSerializer, VistaSerializer)


class ReporteViewSet(GIGABaseViewSet):
    """ViewSet   para gestión de reportes guardados"""
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    search_fields = ['nombre']
    filterset_fields = ['tipo', 'activo']
    ordering = ['-creado_en']


class NotificacionViewSet(GIGABaseViewSet):
    """ViewSet   para gestión de notificaciones"""
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    filterset_fields = ['destinatario', 'tipo', 'leido', 'enviado']
    ordering = ['-creado_en']

    @action(detail=False, methods=['get'])
    @require_authenticated
    def mis_notificaciones(self, request):
        """Obtener notificaciones del usuario actual"""
        notificaciones = self.queryset.filter(
            destinatario=request.user,
            enviado=True
        )
        
        serializer = self.get_serializer(notificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    @require_authenticated
    def marcar_leidas(self, request):
        """Marcar notificaciones como leídas"""
        ids = request.data.get('ids', [])
        
        if not ids:
            return create_error_response('Se requiere lista de IDs')
        
        count = self.queryset.filter(
            id__in=ids,
            destinatario=request.user
        ).update(leido=True)
        
        return create_success_response(f'{count} notificaciones marcadas como leídas')


class PlantillaCorreoViewSet(GIGABaseViewSet):
    """ViewSet   para plantillas de correo"""
    queryset = PlantillaCorreo.objects.all()
    serializer_class = PlantillaCorreoSerializer
    search_fields = ['nombre', 'asunto']
    ordering = ['nombre']

    @action(detail=True, methods=['post'])
    @require_authenticated
    def preview(self, request, pk=None):
        """Vista previa de plantilla con datos de ejemplo"""
        plantilla = self.get_object()
        datos_ejemplo = request.data.get('datos', {})
        
        try:
            # Renderizar plantilla con datos de ejemplo
            contenido_renderizado = plantilla.cuerpo_html.format(**datos_ejemplo)
            
            return Response({
                'asunto': plantilla.asunto,
                'contenido': contenido_renderizado,
                'datos_utilizados': datos_ejemplo
            })
        except KeyError as e:
            return create_error_response(f'Variable faltante en datos: {e}')


class EnvioLoteViewSet(GIGAReadOnlyViewSet):
    """ViewSet   para envíos masivos"""
    queryset = EnvioLoteNotificaciones.objects.all()
    serializer_class = EnvioLoteNotificacionesSerializer
    ordering = ['-creado_en']

    @action(detail=True, methods=['get'])
    @require_authenticated
    def detalle(self, request, pk=None):
        """Detalle completo de un envío masivo"""
        envio = self.get_object()
        
        # Contar notificaciones por estado
        notificaciones = Notificacion.objects.filter(envio_lote=envio)
        
        resumen = {
            'total': notificaciones.count(),
            'enviadas': notificaciones.filter(enviado=True).count(),
            'pendientes': notificaciones.filter(enviado=False).count(),
            'leidas': notificaciones.filter(leido=True).count(),
        }
        
        serializer = self.get_serializer(envio)
        
        return Response({
            'envio': serializer.data,
            'resumen': resumen
        })


class RenderCorreoViewSet(GIGABaseViewSet):
    """ViewSet   para renders de correo"""
    queryset = RenderCorreo.objects.all()
    serializer_class = RenderCorreoSerializer
    filterset_fields = ['plantilla', 'exitoso']
    ordering = ['-creado_en']


class VistaViewSet(GIGABaseViewSet):
    """ViewSet   para vistas del sistema"""
    queryset = Vista.objects.all()
    serializer_class = VistaSerializer
    search_fields = ['nombre']
    filterset_fields = ['activa']
    ordering = ['nombre']


class ReportesViewSet(GIGAViewSet):
    """
    ViewSet   para generación de reportes dinámicos del sistema GIGA
    """
    
    @action(detail=False, methods=['get'])
    @require_authenticated
    def asistencia_resumen(self, request):
        """Reporte resumen de asistencia por período y área"""
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        area_id = request.query_params.get('area')
        
        if not (fecha_desde and fecha_hasta):
            return create_error_response('Se requieren fechaDesde y fechaHasta')
        
        # Importar modelos necesarios
        from asistencia.models import Asistencia
        from personas.models import Agente, Area
        
        # Construir queryset base
        asistencias = Asistencia.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        ).select_related('agente__usuario')
        
        if area_id:
            # Filtrar por área específica
            asistencias = asistencias.filter(agente__areas__id=area_id)
        
        # Agrupar datos por agente
        datos_reporte = []
        agentes = asistencias.values('agente').distinct()
        
        for agente_data in agentes:
            agente_id = agente_data['agente']
            agente = Agente.objects.get(id=agente_id)
            
            asistencias_agente = asistencias.filter(agente=agente)
            
            # Calcular estadísticas
            total_dias = asistencias_agente.count()
            presentes = asistencias_agente.filter(estado='presente').count()
            ausentes = asistencias_agente.filter(estado='ausente').count()
            licencias = asistencias_agente.filter(estado='licencia').count()
            
            datos_reporte.append({
                'agente_id': agente.id,
                'nombre': agente.usuario.get_full_name(),
                'legajo': agente.legajo,
                'total_dias': total_dias,
                'presentes': presentes,
                'ausentes': ausentes,
                'licencias': licencias,
                'porcentaje_asistencia': round((presentes / total_dias * 100) if total_dias > 0 else 0, 2)
            })
        
        return Response({
            'periodo': {'desde': fecha_desde, 'hasta': fecha_hasta},
            'area': area_id,
            'total_agentes': len(datos_reporte),
            'datos': datos_reporte
        })

    @action(detail=False, methods=['get'])
    @require_authenticated
    def guardias_resumen(self, request):
        """Reporte resumen de guardias por período"""
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        
        if not (fecha_desde and fecha_hasta):
            return create_error_response('Se requieren fechaDesde y fechaHasta')
        
        # Importar modelos necesarios
        from guardias.models import AsignacionGuardia
        from personas.models import Agente
        
        asignaciones = AsignacionGuardia.objects.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        ).select_related('agente__usuario', 'guardia')
        
        # Agrupar por agente
        datos_reporte = []
        agentes = asignaciones.values('agente').distinct()
        
        for agente_data in agentes:
            agente_id = agente_data['agente']
            agente = Agente.objects.get(id=agente_id)
            
            asignaciones_agente = asignaciones.filter(agente=agente)
            
            datos_reporte.append({
                'agente_id': agente.id,
                'nombre': agente.usuario.get_full_name(),
                'legajo': agente.legajo,
                'total_guardias': asignaciones_agente.count(),
                'guardias_detalle': [{
                    'fecha': a.fecha,
                    'guardia': a.guardia.nombre,
                    'horario': f"{a.guardia.hora_inicio} - {a.guardia.hora_fin}"
                } for a in asignaciones_agente]
            })
        
        return Response({
            'periodo': {'desde': fecha_desde, 'hasta': fecha_hasta},
            'total_agentes': len(datos_reporte),
            'datos': datos_reporte
        })

    @action(detail=False, methods=['get'])
    @require_authenticated
    def exportar_csv(self, request):
        """Exportar cualquier reporte a CSV"""
        tipo_reporte = request.query_params.get('tipo')
        
        if tipo_reporte == 'asistencia':
            return self._exportar_asistencia_csv(request)
        elif tipo_reporte == 'guardias':
            return self._exportar_guardias_csv(request)
        else:
            return create_error_response('Tipo de reporte no válido')

    def _exportar_asistencia_csv(self, request):
        """Exportar reporte de asistencia a CSV"""
        import csv
        from django.http import HttpResponse
        
        # Obtener datos usando el método existente
        response_data = self.asistencia_resumen(request).data
        
        # Crear response CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_asistencia.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Legajo', 'Nombre', 'Total Días', 'Presentes', 'Ausentes', 'Licencias', '% Asistencia'])
        
        for dato in response_data.get('datos', []):
            writer.writerow([
                dato['legajo'], dato['nombre'], dato['total_dias'],
                dato['presentes'], dato['ausentes'], dato['licencias'],
                dato['porcentaje_asistencia']
            ])
        
        return response

    def _exportar_guardias_csv(self, request):
        """Exportar reporte de guardias a CSV"""
        import csv
        from django.http import HttpResponse
        
        # Obtener datos usando el método existente
        response_data = self.guardias_resumen(request).data
        
        # Crear response CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_guardias.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Legajo', 'Nombre', 'Total Guardias', 'Fecha', 'Guardia', 'Horario'])
        
        for dato in response_data.get('datos', []):
            for guardia_detalle in dato['guardias_detalle']:
                writer.writerow([
                    dato['legajo'], dato['nombre'], dato['total_guardias'],
                    guardia_detalle['fecha'], guardia_detalle['guardia'], 
                    guardia_detalle['horario']
                ])
        
        return response