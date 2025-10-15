from rest_framework import serializers
from .models import Convenio, IndiceConvenio, ConsultaConvenio, ResultadoBusqueda, RespuestaConCitas, Archivo


class ConvenioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Convenio"""
    
    class Meta:
        model = Convenio
        fields = '__all__'


class IndiceConvenioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo IndiceConvenio"""
    convenio_version = serializers.CharField(source='convenio.version', read_only=True)
    
    class Meta:
        model = IndiceConvenio
        fields = '__all__'


class ConsultaConvenioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ConsultaConvenio"""
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = ConsultaConvenio
        fields = '__all__'


class ResultadoBusquedaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo ResultadoBusqueda"""
    
    class Meta:
        model = ResultadoBusqueda
        fields = '__all__'


class RespuestaConCitasSerializer(serializers.ModelSerializer):
    """Serializador para el modelo RespuestaConCitas"""
    
    class Meta:
        model = RespuestaConCitas
        fields = '__all__'


class ArchivoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Archivo"""
    
    class Meta:
        model = Archivo
        fields = '__all__'
        extra_kwargs = {
            'contenido': {'write_only': True}  # No exponer el contenido binario en la API
        }