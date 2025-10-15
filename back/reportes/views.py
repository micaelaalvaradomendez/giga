from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Reporte, Notificacion, PlantillaCorreo, EnvioLoteNotificaciones
from .serializers import ReporteSerializer, NotificacionSerializer, PlantillaCorreoSerializer, EnvioLoteNotificacionesSerializer


# ====== VIEWS PARA REPORTES ======

class ReporteListView(generics.ListCreateAPIView):
    """Vista para listar y crear reportes"""
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]


class ReporteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un reporte específico"""
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA NOTIFICACIONES ======

class NotificacionListView(generics.ListCreateAPIView):
    """Vista para listar y crear notificaciones"""
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]


class NotificacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una notificación específica"""
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA PLANTILLAS DE CORREO ======

class PlantillaCorreoListView(generics.ListCreateAPIView):
    """Vista para listar y crear plantillas de correo"""
    queryset = PlantillaCorreo.objects.all()
    serializer_class = PlantillaCorreoSerializer
    permission_classes = [IsAuthenticated]


class PlantillaCorreoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar una plantilla específica"""
    queryset = PlantillaCorreo.objects.all()
    serializer_class = PlantillaCorreoSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA ENVÍOS LOTE ======

class EnvioLoteNotificacionesListView(generics.ListCreateAPIView):
    """Vista para listar y crear envíos masivos"""
    queryset = EnvioLoteNotificaciones.objects.all()
    serializer_class = EnvioLoteNotificacionesSerializer
    permission_classes = [IsAuthenticated]


class EnvioLoteNotificacionesDetailView(generics.RetrieveAPIView):
    """Vista para obtener un envío masivo específico (solo lectura)"""
    queryset = EnvioLoteNotificaciones.objects.all()
    serializer_class = EnvioLoteNotificacionesSerializer
    permission_classes = [IsAuthenticated]
