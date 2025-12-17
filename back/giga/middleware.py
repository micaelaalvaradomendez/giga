"""
Middleware para agregar atributo Partitioned a cookies de sesión
Necesario para Chrome incógnito y navegadores móviles (CHIPS)
"""
from django.conf import settings

class PartitionedSessionCookieMiddleware:
    """
    Agrega Partitioned a la cookie de sesión en producción.
    https://developer.chrome.com/docs/privacy-sandbox/chips/
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Debug temporal
        print(f"[MIDDLEWARE] Path: {request.path}, DEBUG={settings.DEBUG}")
        print(f"[MIDDLEWARE] Response tiene cookies: {hasattr(response, 'cookies')}")
        if hasattr(response, 'cookies'):
            print(f"[MIDDLEWARE] Cookies en response: {list(response.cookies.keys())}")
        print(f"[MIDDLEWARE] SESSION_COOKIE_NAME: {settings.SESSION_COOKIE_NAME}")
        print(f"[MIDDLEWARE] SESSION_COOKIE_DOMAIN: {getattr(settings, 'SESSION_COOKIE_DOMAIN', 'None')}")
        print(f"[MIDDLEWARE] Set-Cookie header: {response._headers.get('set-cookie', 'None')}")
        
        # Solo en producción (DEBUG=False) y si hay cookie de sesión
        if not settings.DEBUG and hasattr(response, 'cookies') and settings.SESSION_COOKIE_NAME in response.cookies:
            print(f"[MIDDLEWARE] ✅ Agregando Partitioned a cookie de sesión")
            set_cookie_headers = response._headers.get('set-cookie')
            
            if set_cookie_headers:
                header_key, header_value = set_cookie_headers
                
                # Manejar lista de cookies
                if isinstance(header_value, list):
                    updated_cookies = []
                    for cookie in header_value:
                        if settings.SESSION_COOKIE_NAME in cookie and 'Partitioned' not in cookie:
                            updated_cookies.append(cookie.rstrip(';') + '; Partitioned')
                        else:
                            updated_cookies.append(cookie)
                    response._headers['set-cookie'] = (header_key, updated_cookies)
                
                # Manejar string simple
                elif isinstance(header_value, str):
                    if settings.SESSION_COOKIE_NAME in header_value and 'Partitioned' not in header_value:
                        response._headers['set-cookie'] = (header_key, header_value.rstrip(';') + '; Partitioned')

        return response
