"""
ViewSets  s para el módulo guardias
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, transaction
)
from .models import Guardia, CronogramaGuardias, HorasGuardias, Feriado, ReglaPlus, AsignacionPlus
from .serializers import GuardiaSerializer, ModalidadSerializer, CuadroGuardiaSerializer, AsignacionGuardiaSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from datetime import datetime, time
from personas.models import Agente, AgenteRol, Area

# Alias para compatibilidad con ViewSets existentes
Modalidad = CronogramaGuardias
CuadroGuardia = CronogramaGuardias  
AsignacionGuardia = Guardia


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
    

class PlanificarCronogramaView(GIGABaseViewSet):
    @extend_schema(
        description='Crea un cronograma y guardias en estado borrador para aprobación posterior.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'desde': {'type': 'string', 'format': 'date'},
                    'hasta': {'type': 'string', 'format': 'date'},
                    'horas_totales': {'type': 'number'},
                    'area_id': {'type': 'string', 'format': 'uuid', 'nullable': True},
                    'asignaciones': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'fecha': {'type': 'string', 'format': 'date'},
                                'usuario_id': {'type': 'string', 'format': 'uuid'},
                                'horas': {'type': 'number'}
                            },
                            'required': ['fecha', 'usuario_id', 'horas']
                        }
                    }
                },
                'required': ['desde', 'hasta', 'horas_totales', 'asignaciones']
            }
        },
        responses={200: {'type': 'object', 'properties': {
            'cronograma_id': {'type': 'string', 'format': 'uuid'},
            'guardias_creadas': {'type': 'integer'},
            'mensaje': {'type': 'string'}
        }},
        400: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}},
        tags=['guardias']
    )
    def post(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        desde = data.get('desde')
        hasta = data.get('hasta')
        horas_totales = data.get('horas_totales')
        asignaciones = data.get('asignaciones', [])
        area_id = data.get('area_id')

        if not desde or not hasta:
            return Response({'detail': 'desde y hasta son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        if not horas_totales or float(horas_totales) <= 0:
            return Response({'detail': 'horas_totales debe ser > 0'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            d_desde = datetime.strptime(desde, '%Y-%m-%d').date()
            d_hasta = datetime.strptime(hasta, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': 'Formato de fecha inválido (usar YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)
        if d_desde > d_hasta:
            return Response({'detail': 'desde no puede ser mayor a hasta'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            jefe_agente = Agente.objects.get(usuario=request.user)
        except Agente.DoesNotExist:
            return Response({'detail': 'El usuario no está vinculado a un agente'}, status=status.HTTP_403_FORBIDDEN)

        # Validar que las asignaciones correspondan a subordinados del jefe
        subordinados_ids = set(Agente.objects.filter(id_jefe=jefe_agente).values_list('usuario_id', flat=True))
        for it in asignaciones:
            if it.get('usuario_id') not in [str(u) for u in subordinados_ids]:
                return Response({'detail': 'Asignaciones incluyen usuarios que no son subordinados'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar horas totales
        horas_sum = sum(float(it.get('horas') or 0) for it in asignaciones)
        if horas_sum > float(horas_totales):
            return Response({'detail': f'Las horas asignadas ({horas_sum}) exceden las horas_totales ({horas_totales})'}, status=status.HTTP_400_BAD_REQUEST)

        # Resolver área
        area = None
        if area_id:
            try:
                area = Area.objects.get(id=area_id)
            except Area.DoesNotExist:
                return Response({'detail': 'area_id no existe'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ag_rol = AgenteRol.objects.filter(usuario=request.user, area__isnull=False).select_related('area').first()
            area = ag_rol.area if ag_rol else Area.objects.order_by('nombre').first()
            if not area:
                return Response({'detail': 'No hay un área disponible para el cronograma'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            cronograma = CronogramaGuardias.objects.create(
                area=area,
                fecha=d_desde,
                hora_inicio=time(0, 0),
                hora_fin=time(23, 59),
                tipo='mensual',
                estado='generada',
                creado_por=request.user,
                actualizado_por=request.user,
            )

            creadas = 0
            for it in asignaciones:
                try:
                    f = datetime.strptime(it['fecha'], '%Y-%m-%d').date()
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'detail': f"Fecha inválida en asignación: {it.get('fecha')}"}, status=status.HTTP_400_BAD_REQUEST)
                g, _created = Guardia.objects.get_or_create(
                    cronograma=cronograma,
                    usuario_id=it['usuario_id'],
                    fecha=f,
                    defaults={
                        'estado': 'borrador',
                        'activa': False,
                        'creado_por': request.user,
                        'actualizado_por': request.user,
                    }
                )
                # Actualizar horas planificadas
                g.horas_planificadas = float(it['horas'])
                g.estado = 'borrador'
                g.activa = False
                g.actualizado_por = request.user
                g.save()
                creadas += 1

        return Response({
            'cronograma_id': str(cronograma.id),
            'guardias_creadas': creadas,
            'mensaje': 'Cronograma generado en estado generada y guardias en borrador'
        }, status=status.HTTP_200_OK)
