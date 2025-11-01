"""
ViewSets  s para el módulo personas
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response, transaction
)
from .models import Usuario, Agente, Area, Rol, Permiso, PermisoRol, AgenteRol
from .serializers import AgenteSerializer, AreaSerializer, RolSerializer, UsuarioSerializer, AsignacionRolSerializer
from auditoria.utils import registrar_creacion, registrar_actualizacion, registrar_eliminacion
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class UsuarioViewSet(GIGABaseViewSet):
    """
    ViewSet   para CRUD de usuarios
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    search_fields = ['username', 'email', 'first_name', 'last_name', 'cuil']
    filterset_fields = ['is_active', 'is_staff']
    ordering_fields = ['date_joined', 'username', 'email']
    ordering = ['-date_joined']


class AgenteViewSet(GIGABaseViewSet):
    """
    ViewSet para CRUD de agentes
    """
    queryset = Agente.objects.all().select_related('usuario')
    serializer_class = AgenteSerializer
    search_fields = ['usuario__first_name', 'usuario__last_name', 'dni', 'legajo', 'email']
    filterset_fields = ['categoria_revista', 'agrupacion', 'es_jefe']
    ordering_fields = ['usuario__first_name', 'usuario__last_name', 'fecha_nac']
    ordering = ['usuario__last_name', 'usuario__first_name']

    def create(self, request, *args, **kwargs):
        """
        Crear agente y usuario asociado en una transacción
        """
        try:
            with transaction.atomic():
                # Generar username automáticamente
                nombre = request.data.get('nombre', '').lower()
                apellido = request.data.get('apellido', '').lower()
                dni = request.data.get('dni', '')
                
                # Crear username único: nombre.apellido.dni
                username_base = f"{nombre}.{apellido}.{dni}".replace(' ', '').replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                username = username_base[:150]  # Limitamos a 150 caracteres
                
                # Verificar que el username sea único
                counter = 1
                original_username = username
                while Usuario.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Datos del usuario desde la request
                usuario_data = {
                    'username': username,
                    'email': request.data.get('email'),
                    'cuil': request.data.get('cuil'),
                    'password': request.data.get('password', request.data.get('dni', '12345678')),  # Default password es DNI
                    'first_name': request.data.get('nombre', ''),
                    'last_name': request.data.get('apellido', ''),
                    'is_active': True
                }

                # Crear usuario
                print(f"Creando usuario con datos: {usuario_data}")
                usuario = Usuario.objects.create_user(**usuario_data)

                # Generar legajo automáticamente
                def generar_proximo_legajo():
                    # Obtener todos los legajos existentes que sean numéricos
                    legajos_existentes = set()
                    for agente in Agente.objects.filter(legajo__isnull=False).only('legajo'):
                        try:
                            legajo_num = int(agente.legajo)
                            legajos_existentes.add(legajo_num)
                        except (ValueError, TypeError):
                            continue
                    
                    # Buscar el primer número disponible desde 10001
                    numero_legajo = 10001
                    while numero_legajo in legajos_existentes:
                        numero_legajo += 1
                    
                    return str(numero_legajo).zfill(5)
                
                nuevo_legajo = generar_proximo_legajo()

                # Datos del agente
                agente_data = request.data.copy()
                agente_data['usuario'] = usuario.id
                agente_data['legajo'] = nuevo_legajo
                
                # Agregar fecha_nac si no está presente
                if not agente_data.get('fecha_nac'):
                    agente_data['fecha_nac'] = '1990-01-01'  # Fecha por defecto
                
                # Agregar provincia por defecto si no está presente
                if not agente_data.get('provincia'):
                    agente_data['provincia'] = 'Por definir'
                
                # Agregar horarios predefinidos si no están presentes
                if not agente_data.get('horario_entrada'):
                    agente_data['horario_entrada'] = '08:00:00'
                if not agente_data.get('horario_salida'):
                    agente_data['horario_salida'] = '16:00:00'

                # Crear agente usando el serializer
                serializer = self.get_serializer(data=agente_data)
                if not serializer.is_valid():
                    print(f"Errores de validación del agente: {serializer.errors}")
                    print(f"Datos recibidos: {agente_data}")
                serializer.is_valid(raise_exception=True)
                agente = serializer.save(creado_por=request.user, actualizado_por=request.user)

                # Registrar en auditoría
                registrar_creacion(request.user, usuario, ['username', 'email', 'cuil', 'first_name', 'last_name'])
                registrar_creacion(request.user, agente, ['dni', 'legajo', 'email', 'nombre', 'apellido'])

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error al crear agente: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """
        Actualizar agente con auditoría
        """
        instance = self.get_object()
        
        # Guardar valores anteriores para auditoría
        valores_anteriores_usuario = {}
        if instance.usuario:
            for field in ['username', 'email', 'cuil', 'first_name', 'last_name']:
                valores_anteriores_usuario[field] = getattr(instance.usuario, field, '')
        
        valores_anteriores_agente = {}
        for field in ['dni', 'legajo', 'email', 'nombre', 'apellido', 'telefono', 'domicilio']:
            valores_anteriores_agente[field] = getattr(instance, field, '')
        
        # Actualizar el agente
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        agente_actualizado = serializer.save(actualizado_por=request.user)
        
        # Actualizar usuario si es necesario
        if instance.usuario and any(campo in request.data for campo in ['email', 'nombre', 'apellido', 'cuil']):
            usuario = instance.usuario
            if 'email' in request.data:
                usuario.email = request.data['email']
            if 'nombre' in request.data:
                usuario.first_name = request.data['nombre']
            if 'apellido' in request.data:
                usuario.last_name = request.data['apellido']
            if 'cuil' in request.data:
                usuario.cuil = request.data['cuil']
            usuario.save()
            
            # Registrar auditoría del usuario
            registrar_actualizacion(request.user, usuario, valores_anteriores_usuario, ['username', 'email', 'cuil', 'first_name', 'last_name'])
        
        # Registrar auditoría del agente
        registrar_actualizacion(request.user, agente_actualizado, valores_anteriores_agente, ['dni', 'legajo', 'email', 'nombre', 'apellido', 'telefono', 'domicilio'])
        
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    @require_authenticated
    def roles(self, request, pk=None):
        """
        Obtener roles asignados a un agente específico
        """
        agente = self.get_object()
        agente_roles = AgenteRol.objects.filter(
            usuario=agente.usuario
        ).select_related('rol', 'area')
        
        roles_data = [{
            'rol': agente_rol.rol.nombre,
            'area': agente_rol.area.nombre if agente_rol.area else None,
            'asignado_en': agente_rol.asignado_en
        } for agente_rol in agente_roles]
        
        return Response({
            'agente_id': agente.id,
            'roles': roles_data
        })


class AreaViewSet(GIGABaseViewSet):
    """
    ViewSet   para CRUD de áreas
    """
    queryset = Area.objects.all().select_related('area_padre')
    serializer_class = AreaSerializer
    search_fields = ['nombre']
    filterset_fields = ['activa', 'area_padre']
    ordering_fields = ['nombre']
    ordering = ['nombre']

    @action(detail=True, methods=['get'])
    @require_authenticated
    def hijas(self, request, pk=None):
        """
        Obtener áreas hijas de un área específica
        """
        area = self.get_object()
        areas_hijas = Area.objects.filter(area_padre=area)
        serializer = self.get_serializer(areas_hijas, many=True)
        return Response(serializer.data)


# Endpoint extra: subordinados del usuario autenticado
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subordinados(request):
    """
    Retorna los agentes subordinados del usuario autenticado (por id_jefe).
    Opcionalmente filtra por área asignada (query param `area_id`).
    """
    try:
        jefe_agente = Agente.objects.select_related('usuario').get(usuario=request.user)
    except Agente.DoesNotExist:
        return Response({'detail': 'El usuario autenticado no está vinculado a un agente.'}, status=status.HTTP_403_FORBIDDEN)

    qs = Agente.objects.select_related('usuario').filter(id_jefe=jefe_agente)

    area_id = request.query_params.get('area_id')
    if area_id:
        qs = qs.filter(usuario__agenterol__area_id=area_id).distinct()

    from .serializers import SubordinadoSerializer
    data = SubordinadoSerializer(qs, many=True).data
    return Response(data)


class RolViewSet(GIGABaseViewSet):
    """
    ViewSet   para CRUD de roles
    """
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    ordering = ['nombre']

    @action(detail=True, methods=['get'])
    @require_authenticated
    def permisos(self, request, pk=None):
        """
        Obtener permisos asociados a un rol específico
        """
        rol = self.get_object()
        permisos = rol.permisos.all()
        
        permisos_data = [{
            'id': permiso.id,
            'codigo': permiso.codigo,
            'descripcion': permiso.descripcion
        } for permiso in permisos]
        
        return Response({
            'rol_id': rol.id,
            'rol_nombre': rol.nombre,
            'permisos': permisos_data
        })


class AsignacionRolViewSet(GIGABaseViewSet):
    """
    ViewSet   para gestionar asignaciones de roles a usuarios por área
    """
    queryset = AgenteRol.objects.all().select_related('usuario', 'rol', 'area')
    serializer_class = AsignacionRolSerializer
    filterset_fields = ['usuario', 'rol', 'area']

    def create(self, request, *args, **kwargs):
        """
        Crear asignación de rol con auditoría
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asignacion = serializer.save()
        
        # Registrar en auditoría
        registrar_creacion(
            request.user, 
            asignacion, 
            ['usuario_id', 'rol_id', 'area_id', 'activo']
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar asignación de rol con auditoría
        """
        instance = self.get_object()
        
        # Registrar en auditoría antes de eliminar
        registrar_eliminacion(
            request.user,
            instance,
            ['usuario_id', 'rol_id', 'area_id', 'activo']
        )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
