from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Agente, Area, Rol, CuentaAcceso
from .serializers import AgenteSerializer, AreaSerializer, RolSerializer, CuentaAccesoSerializer


# ====== VIEWS PARA AGENTES ======

class AgenteListView(generics.ListCreateAPIView):
    """
    Vista para listar y crear agentes
    """
    queryset = Agente.objects.all()
    serializer_class = AgenteSerializer
    permission_classes = [IsAuthenticated]


class AgenteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un agente específico
    """
    queryset = Agente.objects.all()
    serializer_class = AgenteSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA ÁREAS ======

class AreaListView(generics.ListCreateAPIView):
    """
    Vista para listar y crear áreas
    """
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]


class AreaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un área específica
    """
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA ROLES ======

class RolListView(generics.ListCreateAPIView):
    """
    Vista para listar y crear roles
    """
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]


class RolDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un rol específico
    """
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]


# ====== VIEWS PARA CUENTAS DE ACCESO ======

class CuentaAccesoListView(generics.ListCreateAPIView):
    """
    Vista para listar y crear cuentas de acceso
    """
    queryset = CuentaAcceso.objects.all()
    serializer_class = CuentaAccesoSerializer
    permission_classes = [IsAuthenticated]


class CuentaAccesoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar una cuenta de acceso específica
    """
    queryset = CuentaAcceso.objects.all()
    serializer_class = CuentaAccesoSerializer
    permission_classes = [IsAuthenticated]
