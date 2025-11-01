"""
Serializers  s para el módulo personas
Usando serializers base y eliminando duplicaciones
"""
from core.serializers import BaseSerializer, PersonaBaseSerializer, CatalogoSerializer
from rest_framework import serializers
from .models import Agente, Area, Rol, Usuario, AgenteRol


class UsuarioSerializer(BaseSerializer):
    """
    Serializador   para el modelo Usuario
    """
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'cuil', 
                 'is_active', 'date_joined', 'nombre_completo']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username


class AreaSerializer(BaseSerializer):
    """
    Serializador   para el modelo Area
    """
    area_padre_nombre = serializers.CharField(source='area_padre.nombre', read_only=True)
    hijas_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Area
        fields = '__all__'
    
    def get_hijas_count(self, obj):
        """Contar áreas hijas"""
        return obj.area_set.filter(activa=True).count()


class AgenteSerializer(PersonaBaseSerializer):
    """
    Serializador   para el modelo Agente
    """
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    categoria_display = serializers.CharField(source='get_categoria_revista_display', read_only=True)
    agrupacion_display = serializers.CharField(source='get_agrupacion_display', read_only=True)
    direccion = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = Agente
        fields = '__all__'
        read_only_fields = ['creado_en', 'actualizado_en', 'creado_por', 'actualizado_por']
    
    def get_direccion(self, obj):
        """Concatenar dirección completa"""
        if obj.calle and obj.numero:
            return f"{obj.calle} {obj.numero}, {obj.ciudad or 'N/A'}"
        elif obj.calle:
            return f"{obj.calle}, {obj.ciudad or 'N/A'}"
        else:
            return obj.ciudad or 'N/A'
    
    def get_roles(self, obj):
        """Obtener roles asignados al agente"""
        roles_asignados = AgenteRol.objects.filter(usuario=obj.usuario).select_related('rol', 'area')
        return [{
            'id': str(asignacion.rol.id),  # Convertir UUID a string
            'nombre': asignacion.rol.nombre,
            'area': asignacion.area.nombre if asignacion.area else None
        } for asignacion in roles_asignados]


class RolSerializer(BaseSerializer):
    """
    Serializador   para el modelo Rol
    """
    permisos_count = serializers.SerializerMethodField()
    usuarios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Rol
        fields = '__all__'
    
    def get_permisos_count(self, obj):
        """Contar permisos asociados"""
        return obj.permisos.count()
    
    def get_usuarios_count(self, obj):
        """Contar usuarios con este rol"""
        return obj.agenterol_set.count()


class AsignacionRolSerializer(BaseSerializer):
    """
    Serializador   para asignaciones de roles
    """
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)

    class Meta:
        model = AgenteRol
        fields = ['id', 'usuario', 'rol', 'area', 'asignado_en', 
                 'usuario_nombre', 'rol_nombre', 'area_nombre']
