from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from personas.views import get_authenticated_agente
from common.permissions import obtener_areas_jerarquia

from .models import Incidencia
from .serializers import (
    IncidenciaSerializer,
    IncidenciaCreateSerializer,
    IncidenciaListSerializer,
    ComentarioSerializer,
    ResolucionSerializer,
    CambiarEstadoSerializer
)


class IncidenciaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de incidencias"""
    permission_classes = [IsAuthenticated]
    
    def _get_agente(self, request):
        """Obtiene el agente autenticado del request"""
        return get_authenticated_agente(request)
    
    def get_queryset(self):
        """Filtra incidencias según el rol del usuario"""
        agente = get_authenticated_agente(self.request)
        if not agente:
            return Incidencia.objects.none()
        queryset = Incidencia.objects.select_related(
            'creado_por', 'asignado_a', 'area_involucrada'
        )
        
        # Obtener rol del agente
        agente_rol = agente.agenterol_set.first()
        rol_nombre = agente_rol.id_rol.nombre if agente_rol else 'Agente'
        
        # Administrador ve todas las incidencias del sistema
        if rol_nombre == 'Administrador':
            return queryset.all()
        
        # Director ve incidencias de su área + sub-áreas (jerárquico)
        if rol_nombre == 'Director':
            areas_permitidas = obtener_areas_jerarquia(agente)
            area_ids_permitidas = [a.id_area for a in areas_permitidas]
            return queryset.filter(area_involucrada__id_area__in=area_ids_permitidas)
        
        # Jefatura ve todas las incidencias de su área
        if rol_nombre == 'Jefatura':
            return queryset.filter(area_involucrada=agente.id_area)
        
        # Agente Avanzado ve las incidencias de los agentes de su área y las propias
        if rol_nombre == 'Agente Avanzado':
            return queryset.filter(
                Q(area_involucrada=agente.id_area) &
                (Q(creado_por__agenterol__id_rol__nombre='Agente') | Q(creado_por=agente))
            )
        
        # Agente ve solo las suyas (creadas por él o asignadas a él)
        return queryset.filter(
            Q(creado_por=agente) | Q(asignado_a=agente)
        )
    
    def get_serializer_class(self):
        """Usa diferentes serializers según la acción"""
        if self.action == 'list':
            return IncidenciaListSerializer
        elif self.action == 'create':
            return IncidenciaCreateSerializer
        return IncidenciaSerializer
    
    def perform_create(self, serializer):
        """Asigna automáticamente el área y creador"""
        serializer.save()
    
    @action(detail=False, methods=['get'], url_path='mias')
    def mis_incidencias(self, request):
        """Obtiene las incidencias creadas por el usuario"""
        agente = self._get_agente(request)
        if not agente:
            return Response({'detail': 'Usuario no autenticado'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        incidencias = self.get_queryset().filter(creado_por=agente)
        serializer = IncidenciaListSerializer(incidencias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='asignadas')
    def asignadas(self, request):
        """Obtiene las incidencias asignadas al usuario"""
        agente = self._get_agente(request)
        if not agente:
            return Response({'detail': 'Usuario no autenticado'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        incidencias = self.get_queryset().filter(asignado_a=agente)
        serializer = IncidenciaListSerializer(incidencias, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='agregar-comentario')
    def agregar_comentario(self, request, pk=None):
        """Agrega un comentario de seguimiento a la incidencia"""
        incidencia = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ComentarioSerializer(data=request.data)
        
        if serializer.is_valid():
            comentario = serializer.validated_data['comentario']
            agente = self._get_agente(request)
            incidencia.agregar_comentario(agente, comentario)
            return Response({
                'mensaje': 'Comentario agregado exitosamente',
                'comentarios': incidencia.comentarios_seguimiento
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de una incidencia"""
        incidencia = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CambiarEstadoSerializer(data=request.data)
        
        if serializer.is_valid():
            nuevo_estado = serializer.validated_data['estado']
            comentario_adicional = serializer.validated_data.get('comentario', '')
            
            # Verificar permisos
            agente = self._get_agente(request)
            if not agente or not incidencia.puede_cambiar_estado(agente):
                return Response(
                    {'detail': 'No tienes permisos para cambiar el estado de esta incidencia. Solo el asignado, jefatura, directores o administradores pueden hacerlo.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Verificar que no esté cerrada
            if incidencia.estado == 'cerrada':
                return Response(
                    {'detail': 'No se puede cambiar el estado de una incidencia cerrada'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar estado
            estado_anterior = incidencia.cambiar_estado(nuevo_estado, agente, comentario_adicional)
            
            # Enviar notificación por email
            self._enviar_notificacion_cambio_estado(incidencia, estado_anterior, nuevo_estado)
            
            serializer_response = IncidenciaSerializer(incidencia, context={'request': request})
            return Response(serializer_response.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='resolver')
    def resolver_incidencia(self, request, pk=None):
        """Marca una incidencia como resuelta"""
        incidencia = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ResolucionSerializer(data=request.data)
        
        if serializer.is_valid():
            resolucion = serializer.validated_data['resolucion']
            
            # Validaciones
            if incidencia.fecha_resolucion:
                return Response(
                    {'detail': 'La incidencia ya está resuelta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Solo el asignado o jefatura pueden resolver
            agente = self._get_agente(request)
            agente_rol = agente.agenterol_set.first()
            rol_nombre = agente_rol.id_rol.nombre if agente_rol else 'Agente'
            es_jefatura_o_admin = rol_nombre in ['Administrador', 'Director', 'Jefatura', 'Agente Avanzado']
            es_asignado = incidencia.asignado_a_id == agente.id_agente
            
            if not (es_jefatura_o_admin or es_asignado):
                return Response(
                    {'detail': 'Solo el asignado o jefatura pueden resolver incidencias'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Resolver incidencia
            incidencia.resolver_incidencia(resolucion, agente)
            
            serializer = IncidenciaSerializer(incidencia, context={'request': request})
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='asignar')
    def asignar(self, request, pk=None):
        """Asigna una incidencia a un agente"""
        incidencia = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Solo jefatura/admin pueden asignar
        agente = self._get_agente(request)
        agente_rol = agente.agenterol_set.first()
        rol_nombre = agente_rol.id_rol.nombre if agente_rol else 'Agente'
        es_jefatura_o_admin = rol_nombre in ['Administrador', 'Director', 'Jefatura', 'Agente Avanzado']
        
        if not es_jefatura_o_admin:
            return Response(
                {'detail': 'Solo jefatura puede asignar incidencias'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        agente_id = request.data.get('agente_id')
        if not agente_id:
            return Response(
                {'detail': 'Debe especificar el agente_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from personas.models import Agente
        try:
            agente = Agente.objects.get(id=agente_id)
            incidencia.asignado_a = agente
            incidencia.estado = 'ASIGNADA'
            incidencia.fecha_asignacion = timezone.now()
            incidencia.save()
            
            # Agregar comentario de asignación
            comentario = f"Incidencia asignada a {agente.nombre} {agente.apellido}"
            agente_actual = self._get_agente(request)
            incidencia.agregar_comentario(agente_actual, comentario)
            
            serializer = IncidenciaSerializer(incidencia, context={'request': request})
            return Response(serializer.data)
            
        except Agente.DoesNotExist:
            return Response(
                {'detail': 'Agente no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='jefes-area')
    def jefes_area(self, request):
        """Obtiene los jefes del área del usuario para asignación"""
        agente = self._get_agente(request)
        if not agente:
            return Response({'detail': 'Usuario no autenticado'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        from personas.models import Agente
        
        # Obtener jefes del área del usuario
        area_usuario = agente.id_area
        if not area_usuario:
            return Response({'jefes': []})
        
        jefes = Agente.objects.filter(
            id_area=area_usuario,
            agenterol__id_rol__nombre='Jefatura',
            activo=True
        ).prefetch_related('agenterol_set__id_rol').distinct()
        
        jefes_data = []
        for jefe in jefes:
            rol = jefe.agenterol_set.first()
            jefes_data.append({
                'id': jefe.id_agente,
                'nombre': f"{jefe.nombre} {jefe.apellido}",
                'rol': rol.id_rol.nombre if rol else 'Sin rol'
            })
        
        return Response({'jefes': jefes_data})

    @action(detail=False, methods=['get'], url_path='agentes-area')
    def agentes_area(self, request):
        """Obtiene los agentes del área del usuario para asignación (para jefes/directores/admins)"""
        agente = self._get_agente(request)
        if not agente:
            return Response({'detail': 'Usuario no autenticado'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        from personas.models import Agente
        
        # Obtener agentes del área del usuario
        area_usuario = agente.id_area
        if not area_usuario:
            return Response({'agentes': []})
        
        # Obtener agentes (no jefaturas) del área
        agentes = Agente.objects.filter(
            id_area=area_usuario,
            agenterol__id_rol__nombre='Agente',  # Solo rol 'Agente'
            activo=True
        ).prefetch_related('agenterol_set__id_rol').distinct()
        
        agentes_data = []
        for agente in agentes:
            rol = agente.agenterol_set.first()
            agentes_data.append({
                'id': agente.id_agente,
                'nombre': f"{agente.nombre} {agente.apellido}",
                'rol': rol.id_rol.nombre if rol else 'Sin rol'
            })
        
        return Response({'agentes': agentes_data})

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """Estadísticas de incidencias según el rol"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'por_estado': {},
            'por_prioridad': {},
            'vencidas': queryset.filter(
                estado__in=['ABIERTA', 'EN_PROGRESO'],
                fecha_creacion__lt=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }
        
        # Estadísticas por estado
        for estado, _ in Incidencia.ESTADOS:
            stats['por_estado'][estado] = queryset.filter(estado=estado).count()
        
        # Estadísticas por prioridad
        for prioridad, _ in Incidencia.PRIORIDADES:
            stats['por_prioridad'][prioridad] = queryset.filter(prioridad=prioridad).count()
        
        return Response(stats)
    
    def _enviar_notificacion_cambio_estado(self, incidencia, estado_anterior, nuevo_estado):
        """Envía notificación por email cuando cambia el estado de una incidencia"""
        try:
            from .email_service import IncidenciaEmailService
            
            # Determinar destinatarios
            destinatarios = []
            
            # Siempre notificar al creador (si no es quien hizo el cambio)
            agente_actual = self._get_agente(self.request)
            if incidencia.creado_por and incidencia.creado_por != agente_actual:
                destinatarios.append(incidencia.creado_por)
            
            # Notificar al asignado (si no es quien hizo el cambio)
            if incidencia.asignado_a and incidencia.asignado_a != agente_actual:
                destinatarios.append(incidencia.asignado_a)
            
            # Enviar emails
            for agente in destinatarios:
                email = self._obtener_email_agente(agente)
                if email:
                    IncidenciaEmailService.enviar_notificacion_cambio_estado(
                        incidencia, estado_anterior, nuevo_estado, email, agente
                    )
        except Exception as e:
            # Log del error pero no fallar la operación principal
            print(f"Error enviando notificación de cambio de estado: {str(e)}")
    
    def _obtener_email_agente(self, agente):
        """Obtiene el email de un agente"""
        try:
            # Primero intentar obtener email desde el User
            if hasattr(agente, 'user') and agente.user:
                return agente.user.email
            
            # Si no tiene user asociado, buscar por DNI
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username=str(agente.dni))
                return user.email
            except User.DoesNotExist:
                pass
            
            # Como fallback, usar un email basado en el nombre
            email_domain = "giga.gob.ar"  # Dominio por defecto
            nombre_email = f"{agente.nombre.lower()}.{agente.apellido.lower()}".replace(" ", ".")
            return f"{nombre_email}@{email_domain}"
            
        except Exception:
            return None

    @action(detail=False, methods=['get'], url_path='debug')
    def debug(self, request):
        """Debug endpoint para verificar qué está pasando"""
        debug_info = {
            'has_user_agente': hasattr(request, 'user_agente'),
            'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
        }
        
        agente = self._get_agente(request)
        if agente:
            debug_info.update({
                'agente_dni': agente.dni,
                'agente_nombre': f"{agente.nombre} {agente.apellido}",
                'agente_area': agente.area.nombre if agente.area else None,
                'total_incidencias_db': Incidencia.objects.count(),
                'queryset_count': self.get_queryset().count(),
                'todas_incidencias': list(Incidencia.objects.values('id', 'titulo', 'estado', 'creado_por_id'))
            })
        
        return Response(debug_info)
    
    @action(detail=False, methods=['post'], url_path='test-email')
    def test_email(self, request):
        """Endpoint para probar el envío de emails"""
        from .email_service import IncidenciaEmailService
        
        email_destino = request.data.get('email', 'test@ejemplo.com')
        
        try:
            resultado = IncidenciaEmailService.test_envio_email(email_destino)
            if resultado:
                return Response({'message': f'Email de prueba enviado correctamente a {email_destino}'})
            else:
                return Response({'error': 'Error al enviar email de prueba'}, status=400)
        except Exception as e:
            return Response({'error': f'Error en test de email: {str(e)}'}, status=500)
    
    @action(detail=False, methods=['post'], url_path='crear-prueba', permission_classes=[])
    def crear_prueba(self, request):
        """Endpoint sin autenticación para crear incidencia de prueba y activar signals"""
        from personas.models import Agente, Area
        from .models import Incidencia
        from django.utils import timezone
        
        try:
            # Obtener agentes de prueba
            lucía = Agente.objects.get(id_agente=14)  # Lucía Morales
            area = Area.objects.get(id_area=21)
            
            # Crear incidencia que activará signals
            incidencia = Incidencia.objects.create(
                numero=f"PB-{timezone.now().strftime('%H%M%S')}",
                titulo="Prueba Automática de Sistema Email",
                descripcion="Esta incidencia fue creada automáticamente para probar el sistema de notificaciones por email mediante Django signals.",
                prioridad="alta",
                estado="ABIERTA",
                fecha_creacion=timezone.now(),
                fecha_asignacion=timezone.now(),
                area_involucrada=area,
                asignado_a=lucía,
                creado_por=lucía,
                comentarios_seguimiento=[]
            )
            
            return Response({
                'message': 'Incidencia de prueba creada exitosamente',
                'incidencia_id': incidencia.id,
                'numero': incidencia.numero,
                'asignado_a': f"{lucía.nombre} {lucía.apellido}",
                'email_agente': 'lgantonaz@gmail.com'
            })
            
        except Exception as e:
            return Response({'error': f'Error creando incidencia de prueba: {str(e)}'}, status=500)