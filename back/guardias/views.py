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
    
    def create(self, request, *args, **kwargs):
        """Override del método create para manejar repetición anual"""
        repetir_anualmente = request.data.get('repetir_anualmente', False)
        
        if not repetir_anualmente:
            # Comportamiento normal
            return super().create(request, *args, **kwargs)
        
        # Crear feriado con repetición anual (10 años hacia adelante)
        fecha_original = request.data.get('fecha')
        descripcion = request.data.get('descripcion')
        es_nacional = request.data.get('es_nacional', False)
        es_provincial = request.data.get('es_provincial', False)
        es_local = request.data.get('es_local', False)
        
        try:
            from datetime import datetime, timedelta
            from django.db import transaction
            
            fecha_base = datetime.strptime(fecha_original, '%Y-%m-%d').date()
            feriados_creados = []
            
            with transaction.atomic():
                # Crear feriado para los próximos 10 años
                for i in range(10):
                    fecha_año = fecha_base.replace(year=fecha_base.year + i)
                    
                    # Verificar si ya existe para evitar duplicados
                    if not Feriado.objects.filter(fecha=fecha_año).exists():
                        feriado = Feriado.objects.create(
                            fecha=fecha_año,
                            descripcion=descripcion,
                            es_nacional=es_nacional,
                            es_provincial=es_provincial,
                            es_local=es_local,
                            activo=True,
                            creado_en=timezone.now()
                        )
                        feriados_creados.append(FeriadoSerializer(feriado).data)
            
            return Response({
                'success': True,
                'message': f'Se crearon {len(feriados_creados)} feriados para los próximos 10 años',
                'data': {
                    'feriados_creados': len(feriados_creados),
                    'años': [f['fecha'][:4] for f in feriados_creados],
                    'feriados': feriados_creados
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error creando feriados anuales: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

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
            from .utils import get_agente_rol, requiere_aprobacion_rol
            
            agente_id = data.get('agente_id')  # Por ahora recibir del request
            if not agente_id and hasattr(request.user, 'agente'):
                agente_id = request.user.agente.id_agente
            
            if not agente_id:
                return Response(
                    {'error': 'No se pudo determinar el agente creador'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener agente completo
            try:
                from personas.models import Agente
                agente_creador = Agente.objects.get(id_agente=agente_id)
            except Agente.DoesNotExist:
                return Response(
                    {'error': 'Agente no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Determinar rol del creador
            rol_creador = get_agente_rol(agente_creador)
            if not rol_creador:
                rol_creador = 'jefatura'  # Por defecto
            
            # Determinar estado inicial según rol
            if rol_creador.lower() == 'administrador':
                estado_inicial = 'aprobada'  # Auto-aprobado
                fecha_aprobacion = timezone.now().date()
                aprobado_por_id = agente_id  # Se aprueba a sí mismo
            else:
                estado_inicial = 'pendiente'  # Requiere aprobación
                fecha_aprobacion = None
                aprobado_por_id = None
            
            # Crear el cronograma
            cronograma = Cronograma.objects.create(
                id_area_id=data['id_area'],
                id_jefe_id=agente_id,  # El jefe es quien crea
                id_director_id=agente_id,  # Por ahora, el mismo agente es jefe y director
                tipo=data['tipo'],
                hora_inicio=data['hora_inicio'],
                hora_fin=data['hora_fin'],
                estado=estado_inicial,
                fecha_creacion=timezone.now().date(),
                fecha_aprobacion=fecha_aprobacion,
                creado_por_rol=rol_creador,
                creado_por_id_id=agente_id,
                aprobado_por_id_id=aprobado_por_id
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
                # Manejar tanto el formato de entero como de objeto
                if isinstance(agente_data, dict):
                    agente_id_guardia = agente_data['id_agente']
                else:
                    agente_id_guardia = agente_data
                    
                guardia = Guardia.objects.create(
                    id_cronograma=cronograma,
                    id_agente_id=agente_id_guardia,
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
                        'id_agente': agente_id_guardia,
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
        """Aprueba un cronograma con validación de jerarquía de roles"""
        from .utils import get_agente_rol, puede_aprobar
        
        cronograma = self.get_object()
        
        # Validar estado actual
        if cronograma.estado not in ['generada', 'pendiente']:
            return Response(
                {'error': f'Solo se pueden aprobar cronogramas en estado "generada" o "pendiente". Estado actual: {cronograma.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener agente que aprueba (simular con agente_id del request por ahora)
        # En producción usar: agente_aprobador = request.user.agente
        agente_id = request.data.get('agente_id')
        if not agente_id:
            return Response(
                {'error': 'Se requiere agente_id para aprobar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from personas.models import Agente
            agente_aprobador = Agente.objects.get(id_agente=agente_id)
        except Agente.DoesNotExist:
            return Response(
                {'error': 'Agente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener rol del aprobador
        rol_aprobador = get_agente_rol(agente_aprobador)
        if not rol_aprobador:
            return Response(
                {'error': 'El agente no tiene un rol asignado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar si puede aprobar según jerarquía
        if not puede_aprobar(cronograma, rol_aprobador):
            roles_permitidos = cronograma.puede_aprobar_rol
            return Response(
                {
                    'error': f'No tiene permisos para aprobar este cronograma',
                    'detalle': f'Roles permitidos: {", ".join(roles_permitidos)}. Su rol: {rol_aprobador}'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Aprobar cronograma
        cronograma.estado = 'aprobada'
        cronograma.fecha_aprobacion = date.today()
        cronograma.aprobado_por_id = agente_aprobador
        cronograma.save()
        
        # Registrar en auditoría
        from auditoria.models import RegistroAuditoria
        RegistroAuditoria.objects.create(
            tipo_accion='aprobacion_cronograma',
            detalle=f'Cronograma {cronograma.id_cronograma} aprobado por {agente_aprobador.nombre} {agente_aprobador.apellido} (rol: {rol_aprobador})',
            modelo_afectado='cronograma',
            id_registro=cronograma.id_cronograma
        )
        
        return Response({
            'mensaje': 'Cronograma aprobado exitosamente',
            'cronograma_id': cronograma.id_cronograma,
            'aprobado_por': f'{agente_aprobador.nombre} {agente_aprobador.apellido}',
            'fecha_aprobacion': cronograma.fecha_aprobacion
        })
    
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
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Lista cronogramas pendientes de aprobación según rol del usuario"""
        from .utils import get_agente_rol, get_approval_hierarchy
        
        # Obtener agente del usuario (por ahora via query param)
        agente_id = request.query_params.get('agente_id')
        if not agente_id:
            if hasattr(request.user, 'agente'):
                agente_id = request.user.agente.id_agente
            else:
                return Response(
                    {'error': 'No se pudo determinar el agente'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            from personas.models import Agente
            agente = Agente.objects.get(id_agente=agente_id)
        except Agente.DoesNotExist:
            return Response(
                {'error': 'Agente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener rol del agente
        rol_agente = get_agente_rol(agente)
        if not rol_agente:
            return Response(
                {'error': 'El agente no tiene un rol asignado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtrar cronogramas pendientes que el agente puede aprobar
        cronogramas_pendientes = []
        queryset = Cronograma.objects.filter(estado='pendiente').select_related(
            'id_area', 'id_jefe', 'creado_por_id'
        ).prefetch_related('guardia_set')
        
        for cronograma in queryset:
            # Verificar si el rol del agente puede aprobar este cronograma
            if cronograma.creado_por_rol:
                roles_permitidos = get_approval_hierarchy(cronograma.creado_por_rol)
                if rol_agente.lower() in roles_permitidos:
                    cronogramas_pendientes.append(cronograma)
            elif rol_agente.lower() == 'administrador':
                # Si no tiene creado_por_rol, solo admin puede aprobar
                cronogramas_pendientes.append(cronograma)
        
        # Serializar resultados
        serializer = CronogramaExtendidoSerializer(cronogramas_pendientes, many=True)
        
        return Response({
            'count': len(cronogramas_pendientes),
            'rol_agente': rol_agente,
            'cronogramas': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechaza un cronograma con motivo"""
        from .utils import get_agente_rol, puede_aprobar
        
        cronograma = self.get_object()
        
        # Validar estado actual
        if cronograma.estado not in ['generada', 'pendiente']:
            return Response(
                {'error': f'Solo se pueden rechazar cronogramas pendientes. Estado actual: {cronograma.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener motivo de rechazo
        motivo = request.data.get('motivo')
        if not motivo:
            return Response(
                {'error': 'Se requiere un motivo de rechazo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener agente que rechaza
        agente_id = request.data.get('agente_id')
        if not agente_id:
            return Response(
                {'error': 'Se requiere agente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from personas.models import Agente
            agente_rechazador = Agente.objects.get(id_agente=agente_id)
        except Agente.DoesNotExist:
            return Response(
                {'error': 'Agente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar permisos
        rol_rechazador = get_agente_rol(agente_rechazador)
        if not rol_rechazador:
            return Response(
                {'error': 'El agente no tiene un rol asignado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not puede_aprobar(cronograma, rol_rechazador):
            return Response(
                {'error': 'No tiene permisos para rechazar este cronograma'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Rechazar cronograma
        cronograma.estado = 'rechazada'
        cronograma.save()
        
        # Registrar en auditoría
        from auditoria.models import RegistroAuditoria
        RegistroAuditoria.objects.create(
            tipo_accion='rechazo_cronograma',
            detalle=f'Cronograma {cronograma.id_cronograma} rechazado por {agente_rechazador.nombre} {agente_rechazador.apellido}. Motivo: {motivo}',
            modelo_afectado='cronograma',
            id_registro=cronograma.id_cronograma
        )
        
        return Response({
            'mensaje': 'Cronograma rechazado',
            'cronograma_id': cronograma.id_cronograma,
            'rechazado_por': f'{agente_rechazador.nombre} {agente_rechazador.apellido}',
            'motivo': motivo
        })


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
