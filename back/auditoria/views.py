from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ParametrosControlHorario, RegistroAuditoria
from .serializers import ParametrosControlHorarioSerializer, RegistroAuditoriaSerializer


# ====== VIEWS PARA PARÁMETROS DE CONTROL HORARIO ======

class ParametrosControlHorarioListView(generics.ListCreateAPIView):
    """Vista para listar y crear parámetros de control horario"""
    queryset = ParametrosControlHorario.objects.all()
    serializer_class = ParametrosControlHorarioSerializer
    permission_classes = [IsAuthenticated]


class ParametrosControlHorarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar parámetros específicos"""
    queryset = ParametrosControlHorario.objects.all()
    serializer_class = ParametrosControlHorarioSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA REGISTROS DE AUDITORÍA ======

class RegistroAuditoriaListView(generics.ListAPIView):
    """Vista para listar registros de auditoría (solo lectura)"""
    queryset = RegistroAuditoria.objects.all()
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [IsAuthenticated]


class RegistroAuditoriaDetailView(generics.RetrieveAPIView):
    """Vista para obtener un registro de auditoría específico (solo lectura)"""
    queryset = RegistroAuditoria.objects.all()
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [IsAuthenticated]
