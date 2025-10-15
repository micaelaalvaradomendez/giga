from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Asistencia, Marca, Licencia, Novedad
from .serializers import AsistenciaSerializer, MarcaSerializer, LicenciaSerializer, NovedadSerializer


# ====== VIEWS PARA ASISTENCIAS ======

class AsistenciaListView(generics.ListCreateAPIView):
    """Vista para listar y crear asistencias"""
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer
    permission_classes = [IsAuthenticated]


class AsistenciaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una asistencia específica"""
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA MARCAS ======

class MarcaListView(generics.ListCreateAPIView):
    """Vista para listar y crear marcas"""
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]


class MarcaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una marca específica"""
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA LICENCIAS ======

class LicenciaListView(generics.ListCreateAPIView):
    """Vista para listar y crear licencias"""
    queryset = Licencia.objects.all()
    serializer_class = LicenciaSerializer
    permission_classes = [IsAuthenticated]


class LicenciaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una licencia específica"""
    queryset = Licencia.objects.all()
    serializer_class = LicenciaSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA NOVEDADES ======

class NovedadListView(generics.ListCreateAPIView):
    """Vista para listar y crear novedades"""
    queryset = Novedad.objects.all()
    serializer_class = NovedadSerializer
    permission_classes = [IsAuthenticated]


class NovedadDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una novedad específica"""
    queryset = Novedad.objects.all()
    serializer_class = NovedadSerializer
    permission_classes = [IsAuthenticated]
