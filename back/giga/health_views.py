"""
Health check views para el sistema GIGA
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint para nginx
    """
    try:
        # Verificar conexión a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy', 
            'error': str(e)
        }, status=500)

@csrf_exempt  
@require_http_methods(["GET"])
def simple_health(request):
    """
    Health check muy simple sin BD - solo para nginx
    """
    return JsonResponse({'status': 'ok'})