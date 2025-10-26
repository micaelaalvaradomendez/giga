from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Usuario, Agente, Area, Rol, Permiso, PermisoRol, AgenteRol
from .serializers import SubordinadoSerializer


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

    data = SubordinadoSerializer(qs, many=True).data
    return Response(data)
