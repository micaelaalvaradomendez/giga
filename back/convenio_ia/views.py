"""
ViewSets  s para el módulo convenio_ia
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, timezone
)
from datetime import timedelta
from .models import Convenio, ConsultaConvenio, IndiceConvenio
from .serializers import ConvenioSerializer, ConsultaConvenioSerializer, IndiceConvenioSerializer


class ConvenioViewSet(GIGABaseViewSet):
    """
    ViewSet   para gestión de convenios
    """
    queryset = Convenio.objects.all()
    serializer_class = ConvenioSerializer
    search_fields = ['titulo', 'contenido']
    filterset_fields = ['activo', 'tipo_documento']
    ordering_fields = ['titulo', 'fecha_creacion', 'fecha_actualizacion']
    ordering = ['-fecha_actualizacion']

    @action(detail=True, methods=['post'])
    @require_authenticated
    def indexar(self, request, pk=None):
        """
        Indexar contenido del convenio para búsquedas con IA
        """
        convenio = self.get_object()
        
        # Crear o actualizar índice
        indice, created = IndiceConvenio.objects.get_or_create(
            convenio=convenio,
            defaults={
                'activo': True,
                'fecha_indexacion': timezone.now()
            }
        )
        
        if not created:
            indice.fecha_indexacion = timezone.now()
            indice.activo = True
            indice.save()
        
        # Aquí iría la lógica de indexación con IA/vectores
        # Por ahora simulamos el proceso
        
        action_text = 'creado' if created else 'actualizado'
        return create_success_response(f'Índice {action_text} correctamente para {convenio.titulo}')

    @action(detail=True, methods=['get'])
    @require_authenticated
    def buscar_contenido(self, request, pk=None):
        """
        Buscar contenido específico dentro del convenio
        """
        convenio = self.get_object()
        consulta = request.query_params.get('q', '')
        
        if not consulta:
            return create_error_response('Se requiere parámetro de búsqueda "q"')
        
        # Simulación de búsqueda en contenido
        # En implementación real usaríamos IA/vectores
        resultados = []
        
        if consulta.lower() in convenio.contenido.lower():
            # Encontrar contexto alrededor de la consulta
            contenido_lower = convenio.contenido.lower()
            posicion = contenido_lower.find(consulta.lower())
            
            inicio = max(0, posicion - 100)
            fin = min(len(convenio.contenido), posicion + len(consulta) + 100)
            
            contexto = convenio.contenido[inicio:fin]
            
            resultados.append({
                'snippet': contexto,
                'posicion': posicion,
                'relevancia': 0.95  # Simulado
            })
        
        return Response({
            'convenio': convenio.titulo,
            'consulta': consulta,
            'total_resultados': len(resultados),
            'resultados': resultados
        })

    @action(detail=False, methods=['get'])
    @require_authenticated
    def busqueda_global(self, request):
        """
        Búsqueda global en todos los convenios activos
        """
        consulta = request.query_params.get('q', '')
        
        if not consulta:
            return create_error_response('Se requiere parámetro de búsqueda "q"')
        
        # Buscar en todos los convenios activos
        convenios = self.queryset.filter(activo=True)
        resultados = []
        
        for convenio in convenios:
            if consulta.lower() in convenio.contenido.lower():
                # Calcular relevancia simulada
                ocurrencias = convenio.contenido.lower().count(consulta.lower())
                relevancia = min(1.0, ocurrencias / 10)  # Máximo 1.0
                
                resultados.append({
                    'convenio_id': convenio.id,
                    'titulo': convenio.titulo,
                    'tipo': convenio.tipo_documento,
                    'relevancia': relevancia,
                    'ocurrencias': ocurrencias
                })
        
        # Ordenar por relevancia
        resultados.sort(key=lambda x: x['relevancia'], reverse=True)
        
        return Response({
            'consulta': consulta,
            'total_convenios_revisados': convenios.count(),
            'total_resultados': len(resultados),
            'resultados': resultados[:20]  # Limitar a 20 resultados
        })


class ConsultaConvenioViewSet(GIGABaseViewSet):
    """
    ViewSet   para consultas sobre convenios con IA
    """
    queryset = ConsultaConvenio.objects.all().select_related('usuario')
    serializer_class = ConsultaConvenioSerializer
    search_fields = ['consulta', 'respuesta']
    filterset_fields = ['usuario', 'resuelto']
    ordering_fields = ['fecha_consulta']
    ordering = ['-fecha_consulta']

    @action(detail=False, methods=['post'])
    @require_authenticated
    def nueva_consulta(self, request):
        """
        Crear nueva consulta con procesamiento automático
        """
        consulta_texto = request.data.get('consulta', '')
        
        if not consulta_texto:
            return create_error_response('Se requiere texto de consulta')
        
        # Crear registro de consulta
        consulta = ConsultaConvenio.objects.create(
            usuario=request.user,
            consulta=consulta_texto,
            resuelto=False
        )
        
        # Procesar consulta automáticamente
        respuesta_automatica = self._procesar_consulta_ia(consulta_texto)
        
        if respuesta_automatica:
            consulta.respuesta = respuesta_automatica
            consulta.resuelto = True
            consulta.save()
        
        serializer = self.get_serializer(consulta)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _procesar_consulta_ia(self, consulta_texto):
        """
        Procesar consulta usando IA/búsqueda inteligente
        Simulación de procesamiento - en implementación real usaríamos LLM
        """
        # Palabras clave comunes en convenios
        keywords_responses = {
            'licencia': 'Las licencias se rigen según el artículo X del convenio...',
            'vacaciones': 'El período de vacaciones se establece en...',
            'salario': 'La escala salarial está definida en...',
            'horario': 'Los horarios de trabajo se especifican en...',
            'plus': 'Los adicionales y plus se calculan según...',
        }
        
        consulta_lower = consulta_texto.lower()
        
        for keyword, response in keywords_responses.items():
            if keyword in consulta_lower:
                return response
        
        # Si no encuentra palabras clave específicas
        if len(consulta_texto.split()) > 3:
            return "Su consulta ha sido registrada y será procesada por el sistema de IA. Recibirá una respuesta detallada pronto."
        
        return None

    @action(detail=False, methods=['get'])
    @require_authenticated
    def mis_consultas(self, request):
        """
        Obtener consultas del usuario actual
        """
        consultas = self.queryset.filter(usuario=request.user)
        serializer = self.get_serializer(consultas, many=True)
        
        # Estadísticas
        total = consultas.count()
        resueltas = consultas.filter(resuelto=True).count()
        pendientes = total - resueltas
        
        return Response({
            'estadisticas': {
                'total': total,
                'resueltas': resueltas,
                'pendientes': pendientes
            },
            'consultas': serializer.data
        })

    @action(detail=False, methods=['get'])
    @require_authenticated
    def frecuentes(self, request):
        """
        Obtener consultas frecuentes y sus respuestas
        """
        # Obtener consultas más comunes (simulado)
        consultas_frecuentes = [
            {
                'consulta': '¿Cuántos días de licencia por enfermedad tengo?',
                'respuesta': 'Según el convenio, tienes derecho a X días de licencia por enfermedad al año.',
                'frecuencia': 25
            },
            {
                'consulta': '¿Cómo se calculan las vacaciones?',
                'respuesta': 'Las vacaciones se calculan según la antigüedad establecida en el artículo Y.',
                'frecuencia': 18
            },
            {
                'consulta': '¿Qué plus me corresponden?',
                'respuesta': 'Los plus se asignan según tu categoría y función específica.',
                'frecuencia': 15
            }
        ]
        
        return Response({
            'total_frecuentes': len(consultas_frecuentes),
            'consultas': consultas_frecuentes
        })


class IndiceConvenioViewSet(GIGAReadOnlyViewSet):
    """
    ViewSet   para índices de convenios
    """
    queryset = IndiceConvenio.objects.all().select_related('convenio')
    serializer_class = IndiceConvenioSerializer
    filterset_fields = ['convenio', 'activo']
    ordering = ['-fecha_indexacion']

    @action(detail=False, methods=['get'])
    @validate_required_params('convenioId')
    def por_convenio(self, request):
        """
        Obtener índices de un convenio específico
        """
        convenio_id = request.query_params.get('convenioId')
        
        indices = self.queryset.filter(convenio_id=convenio_id, activo=True)
        serializer = self.get_serializer(indices, many=True)
        
        return Response({
            'convenio_id': convenio_id,
            'total_indices': indices.count(),
            'indices': serializer.data
        })

    @action(detail=False, methods=['get'])
    @require_authenticated
    def resumen(self, request):
        """
        Resumen del sistema de indexación
        """
        total_indices = self.queryset.count()
        activos = self.queryset.filter(activo=True).count()
        
        # Últimas indexaciones
        recientes = self.queryset.filter(
            fecha_indexacion__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return Response({
            'total_indices': total_indices,
            'indices_activos': activos,
            'indices_inactivos': total_indices - activos,
            'indexaciones_semana': recientes,
            'estado_sistema': 'operativo' if activos > 0 else 'sin_indices'
        })

    @action(detail=False, methods=['post'])
    @require_authenticated
    def reindexar_todo(self, request):
        """
        Reindexar todos los convenios activos
        """
        convenios_activos = Convenio.objects.filter(activo=True)
        
        indices_creados = 0
        indices_actualizados = 0
        
        for convenio in convenios_activos:
            indice, created = IndiceConvenio.objects.get_or_create(
                convenio=convenio,
                defaults={
                    'activo': True,
                    'fecha_indexacion': timezone.now()
                }
            )
            
            if created:
                indices_creados += 1
            else:
                indice.fecha_indexacion = timezone.now()
                indice.activo = True
                indice.save()
                indices_actualizados += 1
        
        return Response({
            'mensaje': 'Reindexación completada',
            'convenios_procesados': convenios_activos.count(),
            'indices_creados': indices_creados,
            'indices_actualizados': indices_actualizados
        })