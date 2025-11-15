"""
Autenticación personalizada para Django REST Framework.
Integra el sistema de sesiones personalizadas con Django REST Framework.
"""

from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.models import AnonymousUser
from .models import Agente


class CustomUser:
    """
    Wrapper personalizado que simula un objeto User de Django
    para compatibilidad con Django REST Framework.
    """
    def __init__(self, agente):
        self.agente = agente
        self.id = agente.id_agente
        self.pk = agente.id_agente
        self.username = agente.username
        self.email = agente.email
        self.first_name = agente.nombre
        self.last_name = agente.apellido
        self.is_active = agente.activo if agente.activo is not None else True
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False
        
    def __str__(self):
        return f"{self.agente.nombre} {self.agente.apellido}"
    
    def has_perm(self, perm, obj=None):
        """Método requerido por Django para verificar permisos"""
        return True  # Por ahora, todos los agentes autenticados tienen permisos
    
    def has_module_perms(self, app_label):
        """Método requerido por Django para verificar permisos de módulo"""
        return True


class CustomSessionAuthentication(SessionAuthentication):
    """
    Autenticación personalizada que integra el sistema de sesiones
    personalizadas con Django REST Framework.
    """
    
    def authenticate(self, request):
        """
        Autentica al usuario basándose en las sesiones personalizadas.
        """
        # Verificar si hay una sesión personalizada activa
        user_id = request.session.get('user_id')
        is_authenticated = request.session.get('is_authenticated', False)
        
        if not user_id or not is_authenticated:
            return None
            
        try:
            # Obtener el agente de la base de datos
            agente = Agente.objects.get(id_agente=user_id, activo=True)
            
            # Crear el wrapper de usuario personalizado
            custom_user = CustomUser(agente)
            
            # Retornar el usuario y None (no hay token)
            return (custom_user, None)
            
        except Agente.DoesNotExist:
            # Si el agente no existe o no está activo, limpiar sesión
            request.session.flush()
            return None
    
    def authenticate_header(self, request):
        """
        Retorna el header de autenticación esperado.
        """
        return 'Session'