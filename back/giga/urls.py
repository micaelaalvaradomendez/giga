"""
URL configuration for giga project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import json
from personas.models import Agente, Area, Rol, AgenteRol

def test_db_view(request):
    """Vista de prueba para verificar la conexión a la BD"""
    try:
        agentes_count = Agente.objects.count()
        areas_count = Area.objects.count() 
        roles_count = Rol.objects.count()
        
        # Obtener algunos agentes de ejemplo
        agentes_sample = []
        for agente in Agente.objects.all()[:3]:
            agentes_sample.append({
                'id': agente.id_agente,
                'nombre': agente.nombre,
                'apellido': agente.apellido,
                'email': agente.email,
                'activo': agente.activo
            })
        
        return JsonResponse({
            'success': True,
            'message': 'Conexión a BD exitosa',
            'database_first_strategy': 'Funcionando correctamente',
            'counts': {
                'agentes': agentes_count,
                'areas': areas_count,
                'roles': roles_count
            },
            'sample_agentes': agentes_sample
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error de conexión a BD'
        }, status=500)

# ===== FUNCIONES DE AUTENTICACIÓN =====

def generar_cuil_desde_dni(dni):
    """Generar CUIL en formato 27{dni}4 para compatibilidad"""
    dni_str = str(dni).zfill(8)
    return f"27{dni_str}4"

@csrf_exempt
def login_view(request):
    """Autenticación usando CUIL + password como espera el frontend"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo se permite POST'}, status=405)
    
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
            agente = Agente.objects.get(dni=dni)
        except Agente.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Usuario no encontrado'
            }, status=401)
        
        # Crear o obtener usuario Django temporal para la sesión
        username = f"agente_{agente.id_agente}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': agente.email,
                'first_name': agente.nombre,
                'last_name': agente.apellido,
            }
        )
        if created:
            user.set_password(agente.dni)  # Contraseña por defecto es el DNI
            user.save()
        
        # Verificar contraseña (por ahora usar DNI como password)
        if password == agente.dni:
            # Iniciar sesión
            login(request, user)
            
            # Obtener roles del agente
            roles = []
            for asignacion in AgenteRol.objects.filter(id_agente=agente).select_related('id_rol'):
                roles.append(asignacion.id_rol.nombre)  # Solo el nombre como string
            
            # Preparar datos del usuario
            user_data = {
                'id': str(agente.id_agente),
                'usuario': str(user.id),
                'username': user.username,
                'email': agente.email,
                'nombre': agente.nombre,
                'apellido': agente.apellido,
                'first_name': agente.nombre,  # Para compatibilidad con frontend
                'last_name': agente.apellido,  # Para compatibilidad con frontend  
                'nombre_completo': f"{agente.nombre} {agente.apellido}",
                'dni': agente.dni,
                'cuil': generar_cuil_desde_dni(agente.dni),
                'legajo': agente.legajo,
                'telefono': agente.telefono or '',
                'fecha_nacimiento': agente.fecha_nacimiento,
                'direccion': f"{agente.calle or ''} {agente.numero or ''}, {agente.ciudad or ''}, {agente.provincia or ''}".strip(', '),
                'roles': roles,
                'rol_principal': roles[0] if roles else None,  # El primer rol como principal
                'agrupacion': agente.agrupacion,
                'categoria_revista': agente.categoria_revista or "N/A",
                'activo': agente.activo if agente.activo is not None else True,
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Login exitoso',
                'user': user_data,
                'requires_password_change': False
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'CUIL o contraseña incorrectos'
            }, status=401)
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'Error interno'
        }, status=500)

def check_session(request):
    """Verificar si hay una sesión activa"""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    
    try:
        # Encontrar agente por username
        username = request.user.username
        if username.startswith('agente_'):
            agente_id = username.replace('agente_', '')
            agente = Agente.objects.get(id_agente=agente_id)
            
            # Obtener roles
            roles = []
            for asignacion in AgenteRol.objects.filter(id_agente=agente).select_related('id_rol'):
                roles.append(asignacion.id_rol.nombre)  # Solo el nombre como string
            
            user_data = {
                'id': str(agente.id_agente),
                'usuario': str(request.user.id),
                'username': request.user.username,
                'email': agente.email,
                'nombre': agente.nombre,
                'apellido': agente.apellido,
                'first_name': agente.nombre,  # Para compatibilidad con frontend
                'last_name': agente.apellido,  # Para compatibilidad con frontend
                'nombre_completo': f"{agente.nombre} {agente.apellido}",
                'dni': agente.dni,
                'cuil': generar_cuil_desde_dni(agente.dni),
                'legajo': agente.legajo,
                'telefono': agente.telefono or '',
                'fecha_nacimiento': agente.fecha_nacimiento,
                'direccion': f"{agente.calle or ''} {agente.numero or ''}, {agente.ciudad or ''}, {agente.provincia or ''}".strip(', '),
                'roles': roles,
                'rol_principal': roles[0] if roles else None,  # El primer rol como principal
                'agrupacion': agente.agrupacion,
                'categoria_revista': agente.categoria_revista or "N/A",
                'activo': agente.activo if agente.activo is not None else True,
            }
            
            return JsonResponse({
                'authenticated': True,
                'user': user_data,
                'requires_password_change': False
            })
            
    except Agente.DoesNotExist:
        pass
    except Exception as e:
        return JsonResponse({
            'authenticated': False,
            'error': str(e)
        })
    
    return JsonResponse({'authenticated': False})

@csrf_exempt
def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Sesión cerrada correctamente'
    })

def update_profile(request):
    """Actualizar perfil del usuario"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'No autenticado'}, status=401)
    
    return JsonResponse({
        'success': True,
        'message': 'Función no implementada aún'
    })

def agentes_list_view(request):
    """Listar todos los agentes"""
    try:
        agentes = []
        for agente in Agente.objects.all().select_related('id_area'):
            # Obtener roles
            roles = []
            agente_roles = AgenteRol.objects.filter(id_agente=agente).select_related('id_rol')
            for ar in agente_roles:
                roles.append({
                    'id': ar.id_rol.id_rol,
                    'nombre': ar.id_rol.nombre
                })
            
            agentes.append({
                'id': agente.id_agente,
                'legajo': agente.legajo,
                'nombre': agente.nombre,
                'apellido': agente.apellido,
                'dni': agente.dni,
                'email': agente.email,
                'telefono': agente.telefono,
                'direccion': f"{agente.calle} {agente.numero}, {agente.ciudad}, {agente.provincia}".strip(', '),
                'fecha_nacimiento': agente.fecha_nacimiento,
                'agrupacion': agente.agrupacion,
                'is_active': agente.activo if agente.activo is not None else True,
                'area': {
                    'id': agente.id_area.id_area if agente.id_area else None,
                    'nombre': agente.id_area.nombre if agente.id_area else None
                } if agente.id_area else None,
                'roles': roles
            })
        
        return JsonResponse({
            'count': len(agentes),
            'results': agentes
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Error al obtener agentes'
        }, status=500)

def areas_list_view(request):
    """Listar todas las áreas"""
    try:
        areas = []
        for area in Area.objects.all():
            areas.append({
                'id': area.id_area,
                'nombre': area.nombre
            })
        
        return JsonResponse(areas, safe=False)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Error al obtener áreas'
        }, status=500)

def roles_list_view(request):
    """Listar todos los roles"""
    try:
        roles = []
        for rol in Rol.objects.all():
            roles.append({
                'id': rol.id_rol,
                'nombre': rol.nombre,
                'descripcion': rol.descripcion
            })
        
        return JsonResponse(roles, safe=False)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Error al obtener roles'
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test-db/', test_db_view, name='test_db'),
    
    # Autenticación
    path('api/auth/login/', login_view, name='auth_login'),
    path('api/auth/check-session/', check_session, name='auth_check_session'),
    path('api/auth/logout/', logout_view, name='auth_logout'),
    path('api/auth/update-profile/', update_profile, name='auth_update_profile'),
    
    # Apps URLs
    path('api/personas/', include('personas.urls')),
    path('api/asistencia/', include('asistencia.urls')),
    path('api/guardias/', include('guardias.urls')),
    path('api/auditoria/', include('auditoria.urls')),
]
