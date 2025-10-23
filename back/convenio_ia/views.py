from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Convenio, ConsultaConvenio, IndiceConvenio
from .serializers import ConvenioSerializer, ConsultaConvenioSerializer, IndiceConvenioSerializer


# VIEWS PARA CONVENIOS

class ConvenioListView(generics.ListCreateAPIView):
    """Vista para listar y crear convenios"""
    queryset = Convenio.objects.all()
    serializer_class = ConvenioSerializer
    permission_classes = [IsAuthenticated]


class ConvenioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un convenio específico"""
    queryset = Convenio.objects.all()
    serializer_class = ConvenioSerializer
    permission_classes = [IsAuthenticated]


# VIEWS PARA CONSULTAS DE CONVENIO

class ConsultaConvenioListView(generics.ListCreateAPIView):
    """Vista para listar y crear consultas de convenio"""
    queryset = ConsultaConvenio.objects.all()
    serializer_class = ConsultaConvenioSerializer
    permission_classes = [IsAuthenticated]


class ConsultaConvenioDetailView(generics.RetrieveAPIView):
    """Vista para obtener una consulta específica (solo lectura)"""
    queryset = ConsultaConvenio.objects.all()
    serializer_class = ConsultaConvenioSerializer
    permission_classes = [IsAuthenticated]


# VIEW PARA CONSULTAR CONVENIO

class ConsultarConvenioView(generics.CreateAPIView):
    """Vista para realizar consultas sobre convenios usando IA"""
    serializer_class = ConsultaConvenioSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Procesa una consulta sobre el convenio y retorna la respuesta
        """
        pregunta = request.data.get('pregunta', '')
        
        if not pregunta:
            return Response(
                {'error': 'La pregunta es requerida'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Aquí iría la lógica de IA para procesar la consulta
            # Por ahora, retornamos una respuesta de ejemplo
            consulta = ConsultaConvenio.objects.create(
                usuario=request.user.agente,  # Asumiendo relación con Agente
                pregunta=pregunta,
                respuesta="Esta funcionalidad será implementada con IA",
                citas=[]
            )
            
            serializer = self.get_serializer(consulta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error al procesar la consulta: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
