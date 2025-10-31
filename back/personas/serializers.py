from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Agente, Area, Rol, AgenteRol


class AreaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_area')
    
    class Meta:
        model = Area
        fields = ['id', 'nombre']


class RolSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_rol')
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre']


class AgenteRolSerializer(serializers.ModelSerializer):
    rol = RolSerializer(source='id_rol', read_only=True)
    
    class Meta:
        model = AgenteRol
        fields = ['id', 'agente', 'rol', 'activo']


class AgenteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_agente', read_only=True)
    area = AreaSerializer(source='id_area', read_only=True)
    roles = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Agente
        fields = [
            'id', 'legajo', 'nombre', 'apellido', 'dni', 'cuil',
            'email', 'username', 'telefono', 'direccion', 'fecha_nacimiento',
            'categoria_revista', 'agrupacion', 'is_active', 'fecha_ingreso',
            'area', 'roles', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_roles(self, obj):
        agente_roles = AgenteRol.objects.filter(id_agente=obj)
        return [RolSerializer(ar.id_rol).data for ar in agente_roles]
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        agente = Agente.objects.create(**validated_data)
        if password:
            agente.set_password(password)
            agente.save()
        return agente
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Buscar agente por email
            try:
                agente = Agente.objects.get(email=email)
                # Verificar contraseña
                if not agente.check_password(password):
                    raise serializers.ValidationError('Credenciales inválidas')
                if not agente.is_active:
                    raise serializers.ValidationError('Usuario inactivo')
                attrs['agente'] = agente
            except Agente.DoesNotExist:
                raise serializers.ValidationError('No existe agente con ese email')
        else:
            raise serializers.ValidationError('Email y contraseña requeridos')
        
        return attrs


class AgenteCreateRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenteRol
        fields = ['agente', 'rol', 'activo']
