"""
Views para la app guardias - Implementación de Fase 1 con lógica existente.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import datetime, date
import logging

from .models import Cronograma, Guardia, ResumenGuardiaMes, ReglaPlus, ParametrosArea, Feriado
from auditoria.models import Auditoria
from .serializers import (
    CronogramaExtendidoSerializer, GuardiaResumenSerializer, 
    ResumenGuardiaMesExtendidoSerializer, ReglaPlusSerializer,
    ParametrosAreaSerializer, FeriadoSerializer,
    PlanificacionCronogramaSerializer, CalculoPlusSerializer, AprobacionPlusSerializer
)
from .utils import CalculadoraPlus, PlanificadorCronograma, ValidadorHorarios

logger = logging.getLogger(__name__)


class ReglaPlusViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de reglas de plus salarial"""
    
    queryset = ReglaPlus.objects.all()
    serializer_class = ReglaPlusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        activa = self.request.query_params.get('activa')
        vigente = self.request.query_params.get('vigente')
        
        if activa is not None:
            queryset = queryset.filter(activa=activa.lower() == 'true')
        
        if vigente is not None and vigente.lower() == 'true':
            hoy = date.today()
            queryset = queryset.filter(
                activa=True,
                vigente_desde__lte=hoy
            ).filter(
                Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy)
            )
        
        return queryset.order_by('-porcentaje_plus', 'nombre')
    
    @action(detail=True, methods=['post'])
    def simular(self, request, pk=None):
        """Simula la aplicación de una regla de plus"""
        regla = self.get_object()
        
        horas_test = request.data.get('horas_efectivas', 160)
        
        resultado = {
            'regla': regla.nombre,
            'horas_minimas_requeridas': regla.horas_minimas_mensuales,
            'horas_testeo': horas_test,
            'plus_aplicable': float(regla.porcentaje_plus) if horas_test >= regla.horas_minimas_mensuales else 0,
            'aplica': horas_test >= regla.horas_minimas_mensuales
        }
        
        return Response(resultado)


class ParametrosAreaViewSet(viewsets.ModelViewSet):
    """ViewSet para parámetros de control horario por área"""
    
    queryset = ParametrosArea.objects.all()
    serializer_class = ParametrosAreaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por área
        area_id = self.request.query_params.get('area')
        if area_id:
            queryset = queryset.filter(id_area=area_id)
        
        # Filtrar solo vigentes
        vigentes = self.request.query_params.get('vigentes')
        if vigentes and vigentes.lower() == 'true':
            hoy = date.today()
            queryset = queryset.filter(
                activo=True,
                vigente_desde__lte=hoy
            ).filter(
                Q(vigente_hasta__isnull=True) | Q(vigente_hasta__gte=hoy)
            )
        
        return queryset.order_by('-vigente_desde')


class FeriadoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de feriados"""
    
    queryset = Feriado.objects.all()
    serializer_class = FeriadoSerializer
    permission_classes = []  # Temporalmente sin autenticación para debugging
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros por año
        anio = self.request.query_params.get('anio')
        if anio:
            queryset = queryset.filter(fecha__year=anio)
        
        # Filtros por tipo
        tipo = self.request.query_params.get('tipo')
        if tipo == 'nacional':
            queryset = queryset.filter(es_nacional=True)
        elif tipo == 'provincial':
            queryset = queryset.filter(es_provincial=True)
        elif tipo == 'local':
            queryset = queryset.filter(es_local=True)
        
        return queryset.filter(activo=True).order_by('fecha')
    
    @action(detail=False, methods=['post'])
    def verificar_fecha(self, request):
        """Verifica si una fecha específica es feriado"""
        fecha_str = request.data.get('fecha')
        if not fecha_str:
            return Response(
                {'error': 'Fecha requerida'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            es_feriado = ValidadorHorarios.es_feriado(fecha)
            
            feriado_info = None
            if es_feriado:
                feriado = Feriado.objects.filter(fecha=fecha, activo=True).first()
                if feriado:
                    feriado_info = FeriadoSerializer(feriado).data
            
            return Response({
                'fecha': fecha_str,
                'es_feriado': es_feriado,
                'feriado': feriado_info
            })
            
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Override para agregar auditoría en creación"""
        feriado = serializer.save()
        self._crear_auditoria_feriado('CREAR', feriado.id_feriado, None, serializer.data)
    
    def perform_update(self, serializer):
        """Override para agregar auditoría en actualización"""
        feriado_anterior = self.get_object()
        valor_previo = FeriadoSerializer(feriado_anterior).data
        
        feriado = serializer.save()
        self._crear_auditoria_feriado('MODIFICAR', feriado.id_feriado, valor_previo, serializer.data)
    
    def perform_destroy(self, instance):
        """Override para agregar auditoría en eliminación"""
        valor_previo = FeriadoSerializer(instance).data
        self._crear_auditoria_feriado('ELIMINAR', instance.id_feriado, valor_previo, None)
        instance.delete()
    
    def _crear_auditoria_feriado(self, accion, feriado_id, valor_previo=None, valor_nuevo=None):
        """Crear registro de auditoría para cambios en feriados"""
        try:
            # Obtener el agente del usuario autenticado
            agente_id = None
            if hasattr(self.request.user, 'agente'):
                agente_id = self.request.user.agente.id
            
            Auditoria.objects.create(
                pk_afectada=feriado_id,
                nombre_tabla='feriado',
                creado_en=timezone.now(),
                valor_previo=valor_previo,
                valor_nuevo=valor_nuevo,
                accion=accion,
                id_agente_id=agente_id
            )
        except Exception as e:
            logger.error(f"Error al crear auditoría de feriado: {str(e)}")


class CronogramaViewSet(viewsets.ModelViewSet):
    """ViewSet extendido para cronogramas con planificación automática"""
    
    queryset = Cronograma.objects.all()
    serializer_class = CronogramaExtendidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        area_id = self.request.query_params.get('area')
        estado = self.request.query_params.get('estado')
        tipo = self.request.query_params.get('tipo')
        
        if area_id:
            queryset = queryset.filter(id_area=area_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-creado_en')
    
    @action(detail=False, methods=['post'])
    def crear_con_guardias(self, request):
        """Crea un cronograma con múltiples guardias y registra en auditoría"""
        try:
            data = request.data
            
            # Validar datos requeridos
            required_fields = ['nombre', 'tipo', 'id_area', 'fecha', 'hora_inicio', 'hora_fin', 'agentes']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Campo requerido: {field}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validar que haya agentes
            if not data['agentes'] or len(data['agentes']) == 0:
                return Response(
                    {'error': 'Debe seleccionar al menos un agente'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener el agente del usuario autenticado
            agente_id = None
            if hasattr(request.user, 'agente'):
                agente_id = request.user.agente.id
            
            # Crear el cronograma
            cronograma = Cronograma.objects.create(
                id_area_id=data['id_area'],
                id_jefe_id=agente_id,  # El jefe es quien crea
                tipo=data['tipo'],
                hora_inicio=data['hora_inicio'],
                hora_fin=data['hora_fin'],
                estado='generada'
            )
            
            # Registrar auditoría del cronograma
            Auditoria.objects.create(
                pk_afectada=cronograma.id_cronograma,
                nombre_tabla='cronograma',
                creado_en=timezone.now(),
                valor_previo=None,
                valor_nuevo={
                    'nombre': data['nombre'],
                    'tipo': data['tipo'],
                    'id_area': data['id_area'],
                    'hora_inicio': data['hora_inicio'],
                    'hora_fin': data['hora_fin'],
                    'observaciones': data.get('observaciones', '')
                },
                accion='CREAR',
                id_agente_id=agente_id
            )
            
            # Crear las guardias para cada agente
            guardias_creadas = []
            for agente_data in data['agentes']:
                guardia = Guardia.objects.create(
                    id_cronograma=cronograma,
                    id_agente_id=agente_data['id_agente'],
                    fecha=data['fecha'],
                    hora_inicio=data['hora_inicio'],
                    hora_fin=data['hora_fin'],
                    tipo=data['tipo'],
                    estado='planificada',
                    activa=True,
                    observaciones=data.get('observaciones', '')
                )
                guardias_creadas.append(guardia)
                
                # Registrar auditoría de cada guardia
                Auditoria.objects.create(
                    pk_afectada=guardia.id_guardia,
                    nombre_tabla='guardia',
                    creado_en=timezone.now(),
                    valor_previo=None,
                    valor_nuevo={
                        'id_cronograma': cronograma.id_cronograma,
                        'id_agente': agente_data['id_agente'],
                        'fecha': data['fecha'],
                        'hora_inicio': data['hora_inicio'],
                        'hora_fin': data['hora_fin'],
                        'tipo': data['tipo'],
                        'estado': 'planificada'
                    },
                    accion='CREAR',
                    id_agente_id=agente_id
                )
            
            return Response({
                'mensaje': 'Guardia creada exitosamente',
                'cronograma_id': cronograma.id_cronograma,
                'guardias_creadas': len(guardias_creadas)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error al crear guardia con cronograma: {str(e)}")
            return Response(
                {'error': f'Error al crear guardia: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def planificar(self, request):
        """Planificación automática de guardias"""
        serializer = PlanificacionCronogramaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                resultado = PlanificadorCronograma.planificar_automatico(
                    area_id=serializer.validated_data['area_id'],
                    fecha_inicio=serializer.validated_data['fecha_inicio'],
                    fecha_fin=serializer.validated_data['fecha_fin'],
                    agentes_ids=serializer.validated_data.get('agentes_ids')
                )
                
                if resultado:
                    return Response(resultado, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {'error': 'Error en la planificación automática'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                logger.error(f"Error en planificación: {e}")
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def aprobar(self, request, pk=None):
        """Aprueba un cronograma"""
        cronograma = self.get_object()
        
        if cronograma.estado != 'generada':
            return Response(
                {'error': 'Solo se pueden aprobar cronogramas en estado "generada"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cronograma.estado = 'aprobada'
        cronograma.fecha_aprobacion = date.today()
        # cronograma.aprobado_por = request.user.agente  # Si tienes auth
        cronograma.save()
        
        return Response({'mensaje': 'Cronograma aprobado exitosamente'})
    
    @action(detail=True, methods=['patch'])
    def publicar(self, request, pk=None):
        """Publica un cronograma aprobado"""
        cronograma = self.get_object()
        
        if cronograma.estado != 'aprobada':
            return Response(
                {'error': 'Solo se pueden publicar cronogramas aprobados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cronograma.estado = 'publicada'
        cronograma.save()
        
        # Notificar publicación (implementar sistema de notificaciones)
        # NotificacionManager.notificar_cronograma_publicado(cronograma.id_cronograma)
        
        return Response({'mensaje': 'Cronograma publicado exitosamente'})


class GuardiaViewSet(viewsets.ModelViewSet):
    """ViewSet para guardias con reportes y exportación"""
    
    queryset = Guardia.objects.all()
    serializer_class = GuardiaResumenSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Resumen de guardias por período"""
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        agente_id = request.query_params.get('agente')
        area_id = request.query_params.get('area')
        
        queryset = self.get_queryset()
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        if agente_id:
            queryset = queryset.filter(id_agente=agente_id)
        if area_id:
            queryset = queryset.filter(id_cronograma__id_area=area_id)
        
        # Estadísticas
        estadisticas = queryset.aggregate(
            total_guardias=Count('id_guardia'),
            guardias_activas=Count('id_guardia', filter=Q(activa=True)),
            horas_planificadas=Sum('horas_planificadas'),
            horas_efectivas=Sum('horas_efectivas')
        )
        
        # Guardias del período
        guardias = queryset.order_by('-fecha')[:50]  # Limitar a 50 más recientes
        serializer = self.get_serializer(guardias, many=True)
        
        return Response({
            'estadisticas': estadisticas,
            'guardias': serializer.data,
            'filtros_aplicados': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'agente_id': agente_id,
                'area_id': area_id
            }
        })


class ResumenGuardiaMesViewSet(viewsets.ModelViewSet):
    """ViewSet para resumen mensual con cálculo automático de plus"""
    
    queryset = ResumenGuardiaMes.objects.all()
    serializer_class = ResumenGuardiaMesExtendidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        mes = self.request.query_params.get('mes')
        anio = self.request.query_params.get('anio')
        agente_id = self.request.query_params.get('agente')
        estado_plus = self.request.query_params.get('estado_plus')
        
        if mes:
            queryset = queryset.filter(mes=mes)
        if anio:
            queryset = queryset.filter(anio=anio)
        if agente_id:
            queryset = queryset.filter(id_agente=agente_id)
        if estado_plus:
            queryset = queryset.filter(estado_plus=estado_plus)
        
        return queryset.order_by('-anio', '-mes')
    
    @action(detail=False, methods=['post'])
    def calcular_mensual(self, request):
        """Dispara el cálculo automático de plus mensual"""
        serializer = CalculoPlusSerializer(data=request.data)
        if serializer.is_valid():
            try:
                resultado = CalculadoraPlus.generar_asignaciones_plus(
                    mes=serializer.validated_data['mes'],
                    anio=serializer.validated_data['anio']
                )
                
                return Response(resultado, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error en cálculo mensual: {e}")
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'])
    def aprobar_lote(self, request):
        """Aprueba un lote de asignaciones de plus"""
        serializer = AprobacionPlusSerializer(data=request.data)
        if serializer.is_valid():
            try:
                resumen_ids = serializer.validated_data['resumen_ids']
                
                # Actualizar los resúmenes
                resumenes = ResumenGuardiaMes.objects.filter(
                    id_resumen_guardia_mes__in=resumen_ids,
                    estado_plus='pendiente'
                )
                
                resumenes.update(
                    estado_plus='aprobado',
                    aprobado_en=timezone.now()
                )
                
                return Response({
                    'mensaje': f'{resumenes.count()} asignaciones de plus aprobadas',
                    'aprobados': resumen_ids
                })
                
            except Exception as e:
                logger.error(f"Error aprobando plus: {e}")
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
