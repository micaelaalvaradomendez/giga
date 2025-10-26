from rest_framework import serializers
from .models import Agente, Area, Rol, AgenteRol


class AreaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Area
    """
    class Meta:
        model = Area
        fields = '__all__'


class AgenteSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Agente
    """
    class Meta:
        model = Agente
        fields = '__all__'


class RolSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Rol
    """
    class Meta:
        model = Rol
        fields = '__all__'


class SubordinadoSerializer(serializers.ModelSerializer):
    """
    Serializador simplificado para listar subordinados de un jefe.
    Incluye usuario_id, nombre completo y las áreas asignadas vía AgenteRol.
    """
    usuario_id = serializers.UUIDField(source='usuario.id', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    areas = serializers.SerializerMethodField()

    class Meta:
        model = Agente
        fields = [
            'id', 'usuario_id', 'apellido', 'nombre', 'nombre_completo',
            'dni', 'email', 'legajo', 'es_jefe', 'categoria_revista', 'areas'
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.apellido}, {obj.nombre}"

    def get_areas(self, obj):
        asignaciones = AgenteRol.objects.filter(usuario=obj.usuario).select_related('area')
        return [
            {
                'id': str(asig.area.id),
                'nombre': asig.area.nombre,
            }
            for asig in asignaciones if asig.area is not None
        ]


# FALTA MODELO CuentaAcceso
# class CuentaAccesoSerializer(serializers.ModelSerializer):
#     """
#     Serializador para el modelo CuentaAcceso
#     """
#     agente_nombre = serializers.CharField(source='agente.nombre_completo', read_only=True)
#     
#     class Meta:
#         model = CuentaAcceso
#         fields = '__all__'
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }
