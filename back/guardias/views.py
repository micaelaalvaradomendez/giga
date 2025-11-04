"""
ViewSets  s para el módulo guardias
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, transaction
)
from .models import (
    Guardia, CronogramaGuardias, HorasGuardias, Feriado, ReglaPlus, AsignacionPlus
)
from .serializers import (
    GuardiaSerializer, ModalidadSerializer, CuadroGuardiaSerializer, 
    AsignacionGuardiaSerializer, FeriadoSerializer
)

# Alias para compatibilidad con ViewSets existentes
Modalidad = CronogramaGuardias
CuadroGuardia = CronogramaGuardias  
AsignacionGuardia = Guardia


class FeriadoViewSet(GIGABaseViewSet):
    """ViewSet para el ABM de Feriados."""
    queryset = Feriado.objects.all().order_by('fecha')
    serializer_class = FeriadoSerializer
    ordering_fields = ['fecha', 'descripcion']


class ModalidadViewSet(GIGABaseViewSet):
    """ViewSet para modalidades"""
    queryset = CronogramaGuardias.objects.all()
    serializer_class = ModalidadSerializer
    ordering_fields = ['tipo']
    ordering = ['tipo']
    
    class Meta:
        model = CronogramaGuardias


class GuardiaViewSet(GIGABaseViewSet):
    """ViewSet para guardias"""
    queryset = Guardia.objects.all().select_related('cronograma')
    serializer_class = GuardiaSerializer
    search_fields = ['tipo']
    filterset_fields = ['cronograma', 'activa']
    ordering_fields = ['fecha', 'hora_inicio', 'hora_fin']
    ordering = ['fecha']

    @action(detail=False, methods=['get'])
    @validate_required_params('cronograma')
    def por_cronograma(self, request):
        """Obtener guardias agrupadas por cronograma"""
        cronograma_id = request.query_params.get('cronograma')
        guardias = self.queryset.filter(cronograma_id=cronograma_id, activa=True)
        serializer = self.get_serializer(guardias, many=True)
        return Response(serializer.data)


class CuadroGuardiaViewSet(GIGABaseViewSet):
    """ViewSet para cuadros"""
    queryset = CronogramaGuardias.objects.all()
    serializer_class = CuadroGuardiaSerializer
    filterset_fields = ['fecha', 'area', 'estado']
    ordering_fields = ['fecha', 'creado_en']
    ordering = ['-creado_en']
    basename = 'cuadro'

    @action(detail=True, methods=['post'])
    @require_authenticated
    def activar(self, request, pk=None):
        """Activar cuadro desactivando otros del mismo período"""
        cuadro = self.get_object()
        
        with transaction.atomic():
            # Actualizar estado a aprobada
            cuadro.estado = 'aprobada'
            cuadro.save()
        
        return create_success_response('Cuadro activado correctamente')

    @action(detail=False, methods=['get'])
    def vigente(self, request):
        """Obtener cuadro vigente"""
        from datetime import date
        fecha_actual = date.today()
        
        try:
            cuadro = CuadroGuardia.objects.get(
                fecha=fecha_actual,
                estado='aprobada'
            )
            serializer = self.get_serializer(cuadro)
            return Response(serializer.data)
        except CuadroGuardia.DoesNotExist:
            return create_error_response('No hay cuadro vigente', status.HTTP_404_NOT_FOUND)


class AsignacionGuardiaViewSet(GIGABaseViewSet):
    """ViewSet para asignaciones"""
    queryset = Guardia.objects.all().select_related('cronograma', 'usuario')
    serializer_class = AsignacionGuardiaSerializer
    filterset_fields = ['cronograma', 'usuario', 'fecha']
    ordering_fields = ['fecha', 'creado_en']
    ordering = ['fecha']
    basename = 'asignacion'

    @action(detail=False, methods=['get'])
    @validate_required_params('usuario')
    def por_usuario(self, request):
        """Obtener asignaciones de un usuario en un período"""
        usuario_id = request.query_params.get('usuario')
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        
        queryset = self.queryset.filter(usuario_id=usuario_id)
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def calendario(self, request):
        """Obtener calendario de guardias para un período"""
        fecha_desde = request.query_params.get('fechaDesde')
        fecha_hasta = request.query_params.get('fechaHasta')
        
        if not (fecha_desde and fecha_hasta):
            return create_error_response('Se requieren fechaDesde y fechaHasta')
        
        asignaciones = self.queryset.filter(
            fecha__range=[fecha_desde, fecha_hasta]
        )
        
        # Agrupar por fecha
        calendario = {}
        for asignacion in asignaciones:
            fecha_str = asignacion.fecha.strftime('%Y-%m-%d')
            if fecha_str not in calendario:
                calendario[fecha_str] = []
            calendario[fecha_str].append({
                'guardia': asignacion.tipo or 'Guardia',
                'usuario': asignacion.usuario.get_full_name(),
                'horario': f"{asignacion.hora_inicio} - {asignacion.hora_fin}" if asignacion.hora_inicio else "Sin horario"
            })
        
        return Response({
            'periodo': {'desde': fecha_desde, 'hasta': fecha_hasta},
            'calendario': calendario
        })

    @action(detail=False, methods=['post'])
    @require_authenticated
    def asignacion_masiva(self, request):
        """Crear múltiples asignaciones de guardia"""
        asignaciones_data = request.data.get('asignaciones', [])
        
        if not asignaciones_data:
            return create_error_response('Se requieren asignaciones')
        
        errores = []
        asignaciones_creadas = []
        
        with transaction.atomic():
            for i, data in enumerate(asignaciones_data):
                serializer = self.get_serializer(data=data)
                if serializer.is_valid():
                    # Validar duplicados
                    if AsignacionGuardia.objects.filter(
                        usuario=serializer.validated_data['usuario'],
                        fecha=serializer.validated_data['fecha'],
                        cronograma=serializer.validated_data['cronograma']
                    ).exists():
                        errores.append(f"Asignación {i}: El usuario ya tiene guardia ese día")
                    else:
                        asignacion = serializer.save()
                        asignaciones_creadas.append(serializer.data)
                else:
                    errores.append(f"Asignación {i}: {serializer.errors}")
        
        if errores:
            return Response({'validation_errors': errores}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': f'{len(asignaciones_creadas)} asignaciones creadas exitosamente',
            'asignaciones': asignaciones_creadas
        }, status=status.HTTP_201_CREATED)
