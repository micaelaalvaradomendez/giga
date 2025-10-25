"""
ViewSets  s para el módulo personas
Usando mixins base y eliminando código repetitivo
"""
from core.common import (
    GIGABaseViewSet, GIGAReadOnlyViewSet, action, Response, 
    status, require_authenticated, validate_required_params,
    create_success_response, create_error_response
)
from .models import Usuario, Agente, Area, Rol, Permiso, PermisoRol, AgenteRol
from .serializers import AgenteSerializer, AreaSerializer, RolSerializer, UsuarioSerializer, AsignacionRolSerializer


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