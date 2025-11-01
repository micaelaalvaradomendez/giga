"""
Imports comunes para views del sistema GIGA
Centraliza las importaciones que se repiten en todos los módulos
"""

# Imports centralizados - se importan cuando Django está disponible
try:
    # Django REST Framework
    from rest_framework import viewsets, status, filters
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework.permissions import IsAuthenticated
    
    # Filtros y paginación
    from django_filters.rest_framework import DjangoFilterBackend
    
    # Django core
    from django.db import transaction
    from django.utils import timezone
    from django.shortcuts import get_object_or_404
    
    # Auditoría
    from auditoria.models import Auditoria
    
    # Core components
    from core.mixins import GIGABaseViewSet, GIGAReadOnlyViewSet, GIGAViewSet
    
    DJANGO_AVAILABLE = True
    
except ImportError:
    # Fallback para entornos sin Django (testing, desarrollo)
    DJANGO_AVAILABLE = False
    
    # Stubs para mantener compatibilidad
    class MockClass:
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_200_OK = 200
    
    class MockStatus:
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_204_NO_CONTENT = 204
        HTTP_404_NOT_FOUND = 404
    
    viewsets = filters = action = Response = IsAuthenticated = MockClass
    DjangoFilterBackend = transaction = timezone = get_object_or_404 = MockClass
    Auditoria = GIGABaseViewSet = GIGAReadOnlyViewSet = GIGAViewSet = MockClass
    status = MockStatus()

from datetime import datetime, date, timedelta


# Excepciones comunes
class ValidationError(Exception):
    """Excepción para errores de validación personalizada"""
    pass


# Decoradores útiles
import functools

def require_authenticated(view_func):
    """Decorador que asegura que el usuario esté autenticado"""
    @functools.wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Autenticación requerida'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return view_func(self, request, *args, **kwargs)
    return wrapper


def validate_required_params(*param_names):
    """Decorador que valida parámetros requeridos"""
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            missing_params = []
            for param in param_names:
                if not request.query_params.get(param):
                    missing_params.append(param)
            
            if missing_params:
                return Response(
                    {'error': f'Parámetros requeridos: {", ".join(missing_params)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# Funciones de utilidad
def create_success_response(message, data=None):
    """Crear respuesta de éxito estándar"""
    response_data = {'message': message}
    if data is not None:
        response_data['data'] = data
    return Response(response_data, status=status.HTTP_200_OK)


def create_error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """Crear respuesta de error estándar"""
    return Response({'error': message}, status=status_code)


def create_validation_error_response(errors):
    """Crear respuesta de error de validación estándar"""
    return Response({'validation_errors': errors}, status=status.HTTP_400_BAD_REQUEST)