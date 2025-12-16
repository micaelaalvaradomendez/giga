"""
Middleware personalizado para manejar cookies con atributo Partitioned
Necesario para compatibilidad con modo incógnito de Chrome
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PartitionedSessionCookieMiddleware:
    """
    Middleware que agrega el atributo Partitioned a las cookies de sesión
    para compatibilidad con Chrome en modo incógnito (CHIPS - Cookies Having Independent Partitioned State)
    
    Chrome en modo incógnito requiere cookies third-party con Partitioned para funcionar.
    Django no soporta este atributo nativamente, por lo que lo agregamos manualmente
    modificando los headers Set-Cookie después de que Django los genere.
    
    Más info: https://developer.chrome.com/docs/privacy-sandbox/chips/
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo procesar si:
        # 1. No estamos en DEBUG (producción)
        # 2. La response tiene cookies
        # 3. Existe la cookie de sesión
        if not settings.DEBUG and hasattr(response, 'cookies') and settings.SESSION_COOKIE_NAME in response.cookies:
            logger.info(f"🍪 Processing session cookie for path: {request.path}")
            
            # Obtener todos los headers Set-Cookie
            set_cookie_headers = response._headers.get('set-cookie')
            
            if set_cookie_headers:
                # set_cookie_headers es una tupla: ('Set-Cookie', 'valor')
                header_key, header_value = set_cookie_headers
                
                # Si es una lista de cookies (múltiples Set-Cookie headers)
                if isinstance(header_value, list):
                    updated_cookies = []
                    for cookie in header_value:
                        if settings.SESSION_COOKIE_NAME in cookie and 'Partitioned' not in cookie:
                            # Agregar Partitioned al final de la cookie de sesión
                            updated_cookie = cookie.rstrip(';') + '; Partitioned'
                            updated_cookies.append(updated_cookie)
                            logger.info(f"✅ Added Partitioned to session cookie")
                        else:
                            updated_cookies.append(cookie)
                    response._headers['set-cookie'] = (header_key, updated_cookies)
                
                # Si es un string simple (un solo Set-Cookie header)
                elif isinstance(header_value, str):
                    if settings.SESSION_COOKIE_NAME in header_value and 'Partitioned' not in header_value:
                        # Agregar Partitioned al final
                        updated_value = header_value.rstrip(';') + '; Partitioned'
                        response._headers['set-cookie'] = (header_key, updated_value)
                        logger.info(f"✅ Added Partitioned to session cookie")
        
        return response
