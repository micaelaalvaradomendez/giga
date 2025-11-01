"""
ViewSets  s para el módulo asistencia
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, transaction, timezone
)
from .models import Asistencia, Marca, Licencia, Novedad, Adjunto, TipoLicencia, ParteDiario
from .serializers import AsistenciaSerializer, MarcaSerializer, LicenciaSerializer, NovedadSerializer, AdjuntoSerializer, TipoLicenciaSerializer, ParteDiarioSerializer


class MarcaViewSet(GIGABaseViewSet):
    """ViewSet   para marcas de asistencia"""
    queryset = Marca.objects.all().select_related('agente__usuario')
    serializer_class = MarcaSerializer
    filterset_fields = ['tipo', 'agente']
    ordering_fields = ['fecha', 'hora']
    ordering = ['-fecha', '-hora']

    @action(detail=False, methods=['post'])
    @require_authenticated
    def registrar_marca(self, request):
        """Endpoint específico para registrar marcas con validaciones adicionales"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validaciones de negocio simplificadas
            fecha_hora = serializer.validated_data['fecha_hora']
            
            # Crear marca
            marca = serializer.save()
            
            # Crear o actualizar asistencia del día
            self._actualizar_asistencia_diaria(marca)
            
            return create_success_response('Marca registrada correctamente', serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _actualizar_asistencia_diaria(self, marca):
        """Actualizar el registro diario de asistencia"""
        from datetime import date
        fecha = marca.fecha
        
        asistencia, created = Asistencia.objects.get_or_create(
            agente=marca.agente,
            fecha=fecha,
            defaults={'estado': 'presente'}
        )
        
        # Lógica simplificada para calcular estado según marcas
        marcas_del_dia = Marca.objects.filter(
            agente=asistencia.agente,
            fecha=fecha
        ).order_by('hora')
        
        if marcas_del_dia.count() >= 2:
            asistencia.estado = 'presente'
        else:
            asistencia.estado = 'presente_parcial'
        
        asistencia.save()


class AsistenciaViewSet(GIGABaseViewSet):
    """ViewSet   para registros de asistencia diaria"""
    queryset = Asistencia.objects.all().select_related('agente')
    serializer_class = AsistenciaSerializer
    filterset_fields = ['estado', 'agente', 'fecha']
    ordering_fields = ['fecha', 'creado_en']
    ordering = ['-fecha']

    @action(detail=False, methods=['get'])
    @validate_required_params('agente')
    def por_agente(self, request):
        """Obtener asistencias de un agente en un período"""
        agente_id = request.query_params.get('agente')
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        
        queryset = self.queryset.filter(agente_id=agente_id)
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumen_diario(self, request):
        """Resumen de asistencias por día"""
        fecha = request.query_params.get('fecha', timezone.now().date())
        
        asistencias_dia = self.queryset.filter(fecha=fecha)
        
        resumen = {
            'fecha': fecha,
            'total': asistencias_dia.count(),
            'presentes': asistencias_dia.filter(estado='presente').count(),
            'ausentes': asistencias_dia.filter(estado='ausente').count(),
            'licencias': asistencias_dia.filter(estado='licencia').count(),
            'tardanzas': asistencias_dia.filter(estado='tardanza').count()
        }
        
        return Response(resumen)


class LicenciaViewSet(GIGABaseViewSet):
    """ViewSet   para licencias"""
    queryset = Licencia.objects.all().select_related('agente')
    serializer_class = LicenciaSerializer
    search_fields = ['observaciones']
    filterset_fields = ['estado', 'agente', 'tipo_licencia']
    ordering_fields = ['fecha_desde', 'fecha_hasta', 'creado_en']
    ordering = ['-creado_en']

    @action(detail=True, methods=['patch'])
    @require_authenticated
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de una licencia (aprobar/rechazar)"""
        licencia = self.get_object()
        nuevo_estado = request.data.get('estado')
        observaciones = request.data.get('observaciones', '')
        
        estados_validos = ['pendiente', 'aprobada', 'rechazada']
        if nuevo_estado not in estados_validos:
            return create_error_response('Estado inválido')
        
        licencia.estado = nuevo_estado
        licencia.observaciones_revision = observaciones
        licencia.revisado_por = request.user
        licencia.save()
        
        return create_success_response(f'Licencia {nuevo_estado} correctamente')

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtener licencias pendientes de revisión"""
        licencias = self.queryset.filter(estado='pendiente')
        serializer = self.get_serializer(licencias, many=True)
        return Response(serializer.data)


class NovedadViewSet(GIGABaseViewSet):
    """ViewSet   para novedades"""
    queryset = Novedad.objects.all().select_related('agente')
    serializer_class = NovedadSerializer
    search_fields = ['descripcion']
    filterset_fields = ['tipo', 'agente', 'fecha']
    ordering_fields = ['fecha', 'creado_en']
    ordering = ['-fecha']


class AdjuntoViewSet(GIGABaseViewSet):
    """ViewSet   para archivos adjuntos"""
    queryset = Adjunto.objects.all()
    serializer_class = AdjuntoSerializer
    filterset_fields = ['licencia', 'novedad']
    ordering = ['-subido_en']


class TipoLicenciaViewSet(GIGAReadOnlyViewSet):
    """ViewSet   para tipos de licencia (catálogo)"""
    queryset = TipoLicencia.objects.all()
    ordering = ['codigo']
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class TipoLicenciaSerializer(serializers.ModelSerializer):
            class Meta:
                model = TipoLicencia
                fields = ['id', 'codigo', 'descripcion', 'requiere_adjunto', 'dias_maximo']
        
        return TipoLicenciaSerializer