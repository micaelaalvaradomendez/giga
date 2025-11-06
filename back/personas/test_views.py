"""
Vista temporal para testing de agentes sin autenticación
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Agente, AgenteRol
from .serializers import AgenteListSerializer


@api_view(['GET'])
def get_agentes_test(request):
    """
    Obtener lista de todos los agentes SIN autenticación (solo para testing).
    """
    try:
        # Obtener todos los agentes
        queryset = Agente.objects.all().select_related('id_area').prefetch_related(
            'agenterol_set__id_rol'
        ).order_by('apellido', 'nombre')
        
        # Serializar
        serializer = AgenteListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener agentes: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)