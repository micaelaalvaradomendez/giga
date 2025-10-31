"""
Vistas de autenticación adaptadas para funcionar con CUIL como espera el frontend
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view
from personas.models import Agente
import json
import re

def generar_cuil_desde_dni(dni):
    """Generar CUIL en formato 27{dni}4 para compatibilidad"""
    dni_str = str(dni).zfill(8)
    return f"27{dni_str}4"

@csrf_exempt
@api_view(['POST'])
def login_view(request):
    """
    Autenticación usando CUIL + password como espera el frontend
    """
    try:
        data = json.loads(request.body)
        cuil = data.get('cuil', '').replace('-', '').replace(' ', '')
        password = data.get('password', '')
        
        if not cuil or not password:
            return JsonResponse({
                'success': False, 
                'message': 'CUIL y contraseña son requeridos'
            }, status=400)
        
        # Limpiar CUIL y validar formato
        if len(cuil) != 11 or not cuil.isdigit():
            return JsonResponse({
                'success': False, 
                'message': 'CUIL debe tener 11 dígitos'
            }, status=400)
        
        # Extraer DNI del CUIL (quitar primeros 2 y último dígito)
        dni = cuil[2:10]
        
        # Buscar agente por DNI
        try:
            agente = Agente.objects.select_related('usuario').get(dni=dni)
        except Agente.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Usuario no encontrado'
            }, status=401)
        
        # Verificar que el usuario Django existe
        if not agente.usuario:
            return JsonResponse({
                'success': False, 
                'message': 'Usuario no configurado correctamente'
            }, status=401)
        
        # Verificar contraseña
        user = authenticate(username=agente.usuario.username, password=password)
        if not user:
            return JsonResponse({
                'success': False, 
                'message': 'CUIL o contraseña incorrectos'
            }, status=401)
        
        # Crear sesión
        login(request, user)
        
        # Obtener roles del agente
        roles = []
        for asignacion in agente.asignaciones_agente.select_related('rol'):
            roles.append({
                'id': str(asignacion.rol.id),
                'nombre': asignacion.rol.nombre,
                'area': asignacion.area.nombre if asignacion.area else None
            })
        
        # Preparar datos del usuario
        user_data = {
            'id': str(agente.id),
            'usuario': str(agente.usuario.id),
            'username': agente.usuario.username,
            'email': agente.usuario.email,
            'nombre': agente.nombre,
            'apellido': agente.apellido,
            'dni': agente.dni,
            'cuil': generar_cuil_desde_dni(agente.dni),
            'legajo': agente.legajo,
            'roles': roles,
            'agrupacion': agente.agrupacion,
            'categoria_revista': agente.categoria_revista,
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Login exitoso',
            'user': user_data,
            'requires_password_change': False
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error interno: {str(e)}'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
def check_session(request):
    """
    Verificar si hay una sesión activa
    """
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    
    try:
        # Buscar agente asociado al usuario
        agente = Agente.objects.select_related('usuario').get(usuario=request.user)
        
        # Obtener roles
        roles = []
        for asignacion in agente.asignaciones_agente.select_related('rol'):
            roles.append({
                'id': str(asignacion.rol.id),
                'nombre': asignacion.rol.nombre,
                'area': asignacion.area.nombre if asignacion.area else None
            })
        
        user_data = {
            'id': str(agente.id),
            'usuario': str(agente.usuario.id),
            'username': agente.usuario.username,
            'email': agente.usuario.email,
            'nombre': agente.nombre,
            'apellido': agente.apellido,
            'dni': agente.dni,
            'cuil': generar_cuil_desde_dni(agente.dni),
            'legajo': agente.legajo,
            'roles': roles,
            'agrupacion': agente.agrupacion,
            'categoria_revista': agente.categoria_revista,
        }
        
        return JsonResponse({
            'authenticated': True,
            'user': user_data,
            'requires_password_change': False
        })
        
    except Agente.DoesNotExist:
        return JsonResponse({'authenticated': False})
    except Exception as e:
        return JsonResponse({
            'authenticated': False,
            'error': str(e)
        })

@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    """
    Cerrar sesión
    """
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Sesión cerrada correctamente'
    })

@csrf_exempt
@api_view(['POST'])
def update_profile(request):
    """
    Actualizar perfil del usuario
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'No autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        agente = Agente.objects.get(usuario=request.user)
        
        # Actualizar campos permitidos
        if 'email' in data:
            agente.usuario.email = data['email']
            agente.usuario.save()
        
        if 'telefono' in data:
            agente.telefono = data['telefono']
        
        if 'direccion' in data:
            agente.direccion = data['direccion']
        
        agente.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Perfil actualizado correctamente'
        })
        
    except Agente.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Agente no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)