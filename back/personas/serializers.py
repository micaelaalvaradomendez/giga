"""
Serializadores para el módulo de personas - Sistema GIGA
"""

from rest_framework import serializers
from .models import Agente, Area, Rol, AgenteRol, Agrupacion
from django.contrib.auth.hashers import make_password


class AreaSerializer(serializers.ModelSerializer):
    """Serializador para áreas."""
    
    class Meta:
        model = Area
        fields = ['id_area', 'nombre', 'activo']


class AgrupacionSerializer(serializers.ModelSerializer):
    """Serializador para agrupaciones organizacionales."""
    total_agentes = serializers.SerializerMethodField()
    
    class Meta:
        model = Agrupacion
        fields = ['id_agrupacion', 'nombre', 'descripcion', 'color', 'activo', 'total_agentes']
        
    def get_total_agentes(self, obj):
        """Obtener el total de agentes activos en esta agrupación."""
        return Agente.objects.filter(agrupacion=obj.nombre, activo=True).count()


class RolSerializer(serializers.ModelSerializer):
    """Serializador para roles."""
    
    class Meta:
        model = Rol
        fields = ['id_rol', 'nombre', 'descripcion']


class AgenteRolSerializer(serializers.ModelSerializer):
    """Serializador para relación agente-rol."""
    rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)
    area_nombre = serializers.CharField(source='id_agente.id_area.nombre', read_only=True)
    
    class Meta:
        model = AgenteRol
        fields = ['id_agente_rol', 'id_agente', 'id_rol', 'rol_nombre', 'area_nombre', 'asignado_en']


class AgenteListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listado de agentes."""
    roles = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='id_area.nombre', read_only=True)
    area_id = serializers.IntegerField(source='id_area.id_area', read_only=True)
    agrupacion_display = serializers.SerializerMethodField()
    direccion_completa = serializers.SerializerMethodField()
    
    class Meta:
        model = Agente
        fields = [
            'id_agente', 'legajo', 'nombre', 'apellido', 'dni', 'email',
            'telefono', 'fecha_nacimiento', 'provincia', 'ciudad', 
            'direccion_completa', 'agrupacion', 'agrupacion_display',
            'categoria_revista', 'area_nombre', 'area_id', 'roles', 'activo'
        ]
    
    def get_roles(self, obj):
        """Obtener roles del agente."""
        agente_roles = AgenteRol.objects.filter(id_agente=obj).select_related('id_rol')
        return [{'id': ar.id_rol.id_rol, 'nombre': ar.id_rol.nombre} for ar in agente_roles]
    
    def get_agrupacion_display(self, obj):
        """Mostrar agrupación formateada."""
        if obj.agrupacion:
            return obj.agrupacion.upper()
        return None
    
    def get_direccion_completa(self, obj):
        """Dirección completa concatenada."""
        return obj.direccion


class AgenteDetailSerializer(serializers.ModelSerializer):
    """Serializador completo para detalles de agente."""
    roles = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='id_area.nombre', read_only=True)
    area_id = serializers.IntegerField(source='id_area.id_area', read_only=True)
    agrupacion_display = serializers.SerializerMethodField()
    direccion_completa = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    
    class Meta:
        model = Agente
        fields = [
            'id_agente', 'email', 'dni', 'cuil', 'legajo', 'nombre', 'apellido',
            'telefono', 'fecha_nacimiento', 'provincia', 'ciudad', 'calle', 'numero',
            'direccion_completa', 'horario_entrada', 'horario_salida', 'agrupacion',
            'agrupacion_display', 'categoria_revista', 'area_nombre', 'area_id',
            'roles', 'activo', 'creado_en', 'usuario'
        ]
    
    def get_roles(self, obj):
        """Obtener roles completos del agente."""
        agente_roles = AgenteRol.objects.filter(id_agente=obj).select_related('id_rol')
        return [{
            'id': ar.id_rol.id_rol,
            'nombre': ar.id_rol.nombre,
            'descripcion': ar.id_rol.descripcion,
            'asignado_en': ar.asignado_en
        } for ar in agente_roles]
    
    def get_agrupacion_display(self, obj):
        """Mostrar agrupación formateada."""
        if obj.agrupacion:
            return obj.agrupacion.upper()
        return None
    
    def get_direccion_completa(self, obj):
        """Dirección completa concatenada."""
        return obj.direccion
    
    def get_usuario(self, obj):
        """ID del usuario (para compatibilidad)."""
        return obj.id_agente


class AgenteCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para crear/actualizar agentes."""
    password = serializers.CharField(write_only=True, required=False)
    rol_id = serializers.IntegerField(write_only=True, required=False)
    area_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Agente
        fields = [
            'email', 'dni', 'cuil', 'legajo', 'nombre', 'apellido',
            'telefono', 'fecha_nacimiento', 'provincia', 'ciudad', 'calle', 'numero',
            'horario_entrada', 'horario_salida', 'agrupacion', 'area_id',
            'password', 'rol_id', 'activo'
        ]
    
    def validate_email(self, value):
        """Validar que el email sea único."""
        if self.instance:
            # Actualización: excluir el agente actual
            if Agente.objects.exclude(id_agente=self.instance.id_agente).filter(email=value).exists():
                raise serializers.ValidationError("Este email ya está registrado por otro agente.")
        else:
            # Creación: verificar que no exista
            if Agente.objects.filter(email=value).exists():
                raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_dni(self, value):
        """Validar que el DNI sea único."""
        if self.instance:
            # Actualización: excluir el agente actual
            if Agente.objects.exclude(id_agente=self.instance.id_agente).filter(dni=value).exists():
                raise serializers.ValidationError("Este DNI ya está registrado por otro agente.")
        else:
            # Creación: verificar que no exista
            if Agente.objects.filter(dni=value).exists():
                raise serializers.ValidationError("Este DNI ya está registrado.")
        return value
    
    def validate_cuil(self, value):
        """Validar que el CUIL sea único."""
        if self.instance:
            # Actualización: excluir el agente actual
            if Agente.objects.exclude(id_agente=self.instance.id_agente).filter(cuil=value).exists():
                raise serializers.ValidationError("Este CUIL ya está registrado por otro agente.")
        else:
            # Creación: verificar que no exista
            if Agente.objects.filter(cuil=value).exists():
                raise serializers.ValidationError("Este CUIL ya está registrado.")
        return value
    
    def validate_legajo(self, value):
        """Validar que el legajo sea único."""
        if self.instance:
            # Actualización: excluir el agente actual
            if Agente.objects.exclude(id_agente=self.instance.id_agente).filter(legajo=value).exists():
                raise serializers.ValidationError("Este legajo ya está registrado por otro agente.")
        else:
            # Creación: verificar que no exista
            if Agente.objects.filter(legajo=value).exists():
                raise serializers.ValidationError("Este legajo ya está registrado.")
        return value
    
    def create(self, validated_data):
        """Crear nuevo agente con contraseña hasheada."""
        password = validated_data.pop('password', None)
        rol_id = validated_data.pop('rol_id', None)
        area_id = validated_data.pop('area_id', None)
        
        # Asignar área si se proporciona
        if area_id:
            try:
                area = Area.objects.get(id_area=area_id)
                validated_data['id_area'] = area
            except Area.DoesNotExist:
                pass
        
        # Crear el agente
        if password:
            validated_data['password_hash'] = make_password(password)
        
        agente = Agente.objects.create(**validated_data)
        
        # Asignar rol si se proporciona
        if rol_id:
            try:
                rol = Rol.objects.get(id_rol=rol_id)
                AgenteRol.objects.create(id_agente=agente, id_rol=rol)
            except Rol.DoesNotExist:
                pass
        
        return agente
    
    def update(self, instance, validated_data):
        """Actualizar agente."""
        password = validated_data.pop('password', None)
        rol_id = validated_data.pop('rol_id', None)
        area_id = validated_data.pop('area_id', None)
        
        # Actualizar área si se proporciona
        if area_id is not None:
            if area_id:
                try:
                    area = Area.objects.get(id_area=area_id)
                    validated_data['id_area'] = area
                except Area.DoesNotExist:
                    validated_data['id_area'] = None
            else:
                validated_data['id_area'] = None
        
        # Actualizar contraseña si se proporciona
        if password:
            validated_data['password_hash'] = make_password(password)
        
        # Actualizar campos del agente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar rol si se proporciona
        if rol_id is not None:
            # Eliminar roles actuales
            AgenteRol.objects.filter(id_agente=instance).delete()
            
            # Asignar nuevo rol si se proporciona
            if rol_id:
                try:
                    rol = Rol.objects.get(id_rol=rol_id)
                    AgenteRol.objects.create(id_agente=instance, id_rol=rol)
                except Rol.DoesNotExist:
                    pass
        
        return instance
