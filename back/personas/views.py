from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Usuario, Agente, Area, Rol, Permiso, PermisoRol, AgenteRol

# Views sin hacer porque hay que hacer el serializers
