from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .models import Usuario, Agente, AgenteRol
import json

@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint para login con CUIL y contraseña
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        data = json.loads(request.body)
        cuil = data.get('cuil', '').replace('-', '')  # Remover guiones del CUIL
        password = data.get('password', '')
        
        if not cuil or not password:
            return Response({
                'success': False,
                'message': 'CUIL y contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario por CUIL
        try:
            usuario = Usuario.objects.get(cuil=cuil)
        except Usuario.DoesNotExist:
            return Response({
                'success': False,
                'message': 'CUIL no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar contraseña
        if not usuario.check_password(password):
            return Response({
                'success': False,
                'message': 'Contraseña incorrecta'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que el usuario esté activo
        if not usuario.is_active:
            return Response({
                'success': False,
                'message': 'Usuario inactivo'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Obtener información del agente y sus roles
        try:
            agente = Agente.objects.get(usuario=usuario)
            agente_roles = AgenteRol.objects.filter(usuario=usuario).select_related('rol')
            
            roles = [agente_rol.rol.nombre for agente_rol in agente_roles]
            rol_principal = roles[0] if roles else 'Sin rol'
            
        except Agente.DoesNotExist:
            rol_principal = 'Sin rol'
            roles = []
        
        # Login exitoso - crear sesión
        login(request, usuario)
        
        return Response({
            'success': True,
            'message': 'Login exitoso',
            'user': {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'cuil': usuario.cuil,
                'rol_principal': rol_principal,
                'roles': roles,
                'nombre_completo': f"{usuario.first_name} {usuario.last_name}"
            }
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Formato JSON inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    API endpoint para logout
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    try:
        from django.contrib.auth import logout
        logout(request)
        return Response({
            'success': True,
            'message': 'Logout exitoso'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al cerrar sesión: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'OPTIONS'])
def check_session(request):
    """
    Verificar si el usuario tiene una sesión activa
    """
    # Manejar preflight requests
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    if request.user.is_authenticated:
        try:
            agente = Agente.objects.get(usuario=request.user)
            agente_roles = AgenteRol.objects.filter(usuario=request.user).select_related('rol')
            
            roles = [agente_rol.rol.nombre for agente_rol in agente_roles]
            rol_principal = roles[0] if roles else 'Sin rol'
            
        except Agente.DoesNotExist:
            rol_principal = 'Sin rol'
            roles = []
        
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'cuil': request.user.cuil,
                'rol_principal': rol_principal,
                'roles': roles,
                'nombre_completo': f"{request.user.first_name} {request.user.last_name}"
            }
        })
    else:
        return Response({
            'authenticated': False
        })