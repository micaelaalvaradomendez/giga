"""
Middleware personalizado para el proyecto
"""

class DisableCSRFForAPIMiddleware:
    """
    Middleware que deshabilita CSRF para rutas que empiecen con /api/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si la URL comienza con /api/, marcamos la petición como exenta de CSRF
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        response = self.get_response(request)
        return response