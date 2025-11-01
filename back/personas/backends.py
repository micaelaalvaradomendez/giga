from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned

Usuario = get_user_model()

def clean_cuil(cuil_input):
    """
    Limpia un CUIL removiendo guiones, espacios y caracteres no numéricos
    """
    if not cuil_input:
        return ''
    return ''.join(filter(str.isdigit, str(cuil_input).strip()))

class CUILAuthenticationBackend(BaseBackend):
    """
    Backend de autenticación personalizado que permite login con CUIL
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica usando CUIL como username
        """
        if username is None or password is None:
            return None
        
        # Limpiar CUIL
        cuil_limpio = clean_cuil(username)
        
        try:
            # Buscar usuario por CUIL
            usuario = Usuario.objects.get(cuil=cuil_limpio)
            
            # Verificar contraseña
            if usuario.check_password(password):
                return usuario
            
        except Usuario.DoesNotExist:
            # Usuario no encontrado
            return None
        except MultipleObjectsReturned:
            # Múltiples usuarios con el mismo CUIL (no debería pasar)
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Obtiene un usuario por ID (requerido por Django)
        """
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None