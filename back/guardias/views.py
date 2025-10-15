from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CronogramaGuardias, Guardia, HorasGuardias, Feriado
from .serializers import CronogramaGuardiasSerializer, GuardiaSerializer, HorasGuardiasSerializer, FeriadoSerializer


# ====== VIEWS PARA CRONOGRAMAS ======

class CronogramaGuardiasListView(generics.ListCreateAPIView):
    """Vista para listar y crear cronogramas de guardias"""
    queryset = CronogramaGuardias.objects.all()
    serializer_class = CronogramaGuardiasSerializer
    permission_classes = [IsAuthenticated]


class CronogramaGuardiasDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un cronograma específico"""
    queryset = CronogramaGuardias.objects.all()
    serializer_class = CronogramaGuardiasSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA GUARDIAS ======

class GuardiaListView(generics.ListCreateAPIView):
    """Vista para listar y crear guardias"""
    queryset = Guardia.objects.all()
    serializer_class = GuardiaSerializer
    permission_classes = [IsAuthenticated]


class GuardiaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una guardia específica"""
    queryset = Guardia.objects.all()
    serializer_class = GuardiaSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA HORAS DE GUARDIAS ======

class HorasGuardiasListView(generics.ListCreateAPIView):
    """Vista para listar y crear horas de guardias"""
    queryset = HorasGuardias.objects.all()
    serializer_class = HorasGuardiasSerializer
    permission_classes = [IsAuthenticated]


class HorasGuardiasDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar horas de guardias específicas"""
    queryset = HorasGuardias.objects.all()
    serializer_class = HorasGuardiasSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA FERIADOS ======

class FeriadoListView(generics.ListCreateAPIView):
    """Vista para listar y crear feriados"""
    queryset = Feriado.objects.all()
    serializer_class = FeriadoSerializer
    permission_classes = [IsAuthenticated]


class FeriadoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un feriado específico"""
    queryset = Feriado.objects.all()
    serializer_class = FeriadoSerializer
    permission_classes = [IsAuthenticated]
