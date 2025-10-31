"""
ViewSets para el módulo de personas que funciona con el frontend SvelteKit
"""
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import Agente, Area, Rol, AgenteRol
import json


@csrf_exempt
def agentes_list_create(request):
    """Listar y crear agentes"""
    if request.method == 'GET':
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
                    'usuario': f"user_{agente.id_agente}",  # Compatibilidad con frontend
                    'legajo': agente.legajo,
                    'nombre': agente.nombre,
                    'apellido': agente.apellido,
                    'dni': agente.dni,
                    'email': agente.email,
                    'telefono': agente.telefono,
                    'direccion': f"{agente.calle or ''} {agente.numero or ''}, {agente.ciudad or ''}, {agente.provincia or ''}".strip(', '),
                    'fecha_nac': agente.fecha_nacimiento,
                    'categoria_revista': agente.categoria_revista or "N/A",
                    'agrupacion': agente.agrupacion,
                    'agrupacion_display': agente.agrupacion,
                    'activo': agente.activo if agente.activo is not None else True,
                    'area': {
                        'id': agente.id_area.id_area if agente.id_area else None,
                        'nombre': agente.id_area.nombre if agente.id_area else None
                    } if agente.id_area else None,
                    'roles': roles
                })
            
            return JsonResponse(agentes, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al obtener agentes'
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Crear agente
            with transaction.atomic():
                agente = Agente.objects.create(
                    legajo=data.get('legajo'),
                    nombre=data.get('nombre'),
                    apellido=data.get('apellido'),
                    dni=data.get('dni'),
                    email=data.get('email'),
                    telefono=data.get('telefono'),
                    calle=data.get('calle', ''),
                    numero=data.get('numero', ''),
                    ciudad=data.get('ciudad', ''),
                    provincia=data.get('provincia', ''),
                    fecha_nacimiento=data.get('fecha_nac'),
                    agrupacion=data.get('agrupacion'),
                    categoria_revista=data.get('categoria_revista', 'N/A'),
                    activo=True
                )
                
                # Crear usuario Django si no existe
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
                
                return JsonResponse({
                    'id': agente.id_agente,
                    'usuario': user.id,
                    'message': 'Agente creado exitosamente'
                }, status=201)
                
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al crear agente'
            }, status=400)


@csrf_exempt
def agente_detail(request, agente_id):
    """Detalle, actualizar y eliminar agente"""
    try:
        agente = Agente.objects.get(id_agente=agente_id)
    except Agente.DoesNotExist:
        return JsonResponse({'error': 'Agente no encontrado'}, status=404)
    
    if request.method == 'GET':
        # Obtener roles
        roles = []
        agente_roles = AgenteRol.objects.filter(id_agente=agente).select_related('id_rol')
        for ar in agente_roles:
            roles.append({
                'id': ar.id_rol.id_rol,
                'nombre': ar.id_rol.nombre
            })
        
        return JsonResponse({
            'id': agente.id_agente,
            'usuario': f"user_{agente.id_agente}",
            'legajo': agente.legajo,
            'nombre': agente.nombre,
            'apellido': agente.apellido,
            'dni': agente.dni,
            'email': agente.email,
            'telefono': agente.telefono,
            'direccion': f"{agente.calle or ''} {agente.numero or ''}, {agente.ciudad or ''}, {agente.provincia or ''}".strip(', '),
            'fecha_nac': agente.fecha_nacimiento,
            'categoria_revista': agente.categoria_revista or "N/A",
            'agrupacion': agente.agrupacion,
            'activo': agente.activo if agente.activo is not None else True,
            'roles': roles
        })
    
    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            
            # Actualizar campos
            for field, value in data.items():
                if hasattr(agente, field):
                    setattr(agente, field, value)
            
            agente.save()
            
            return JsonResponse({
                'id': agente.id_agente,
                'message': 'Agente actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al actualizar agente'
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            agente.delete()
            return JsonResponse({'message': 'Agente eliminado exitosamente'})
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al eliminar agente'
            }, status=400)


def areas_list_create(request):
    """Listar y crear áreas"""
    if request.method == 'GET':
        try:
            areas = []
            for area in Area.objects.all():
                areas.append({
                    'id': area.id_area,
                    'nombre': area.nombre,
                    'descripcion': getattr(area, 'descripcion', '')
                })
            
            return JsonResponse(areas, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al obtener áreas'
            }, status=500)


def roles_list_create(request):
    """Listar y crear roles"""
    if request.method == 'GET':
        try:
            roles = []
            for rol in Rol.objects.all():
                roles.append({
                    'id': rol.id_rol,
                    'nombre': rol.nombre,
                    'descripcion': rol.descripcion or ''
                })
            
            return JsonResponse(roles, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al obtener roles'
            }, status=500)


@csrf_exempt
def asignaciones_list_create(request):
    """Listar y crear asignaciones de roles"""
    if request.method == 'GET':
        try:
            asignaciones = []
            for ar in AgenteRol.objects.all().select_related('id_agente', 'id_rol'):
                asignaciones.append({
                    'id': ar.id_agente_rol,
                    'usuario': f"user_{ar.id_agente.id_agente}",
                    'agente': ar.id_agente.id_agente,
                    'rol': ar.id_rol.id_rol,
                    'area': None,  # No hay campo area en AgenteRol según nuestro modelo
                    'agente_nombre': f"{ar.id_agente.nombre} {ar.id_agente.apellido}",
                    'rol_nombre': ar.id_rol.nombre,
                    'area_nombre': None  # No hay campo area en AgenteRol según nuestro modelo
                })
            
            return JsonResponse(asignaciones, safe=False)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al obtener asignaciones'
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Buscar agente por usuario_id 
            usuario_ref = data.get('usuario', '').replace('user_', '')
            agente = Agente.objects.get(id_agente=usuario_ref)
            rol = Rol.objects.get(id_rol=data.get('rol'))
            
            # Crear asignación (sin area ya que nuestro modelo no lo tiene)
            ar = AgenteRol.objects.create(
                id_agente=agente,
                id_rol=rol
            )
            
            return JsonResponse({
                'id': ar.id_agente_rol,
                'message': 'Asignación creada exitosamente'
            }, status=201)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al crear asignación'
            }, status=400)


@csrf_exempt
def asignacion_delete(request, asignacion_id):
    """Eliminar asignación"""
    if request.method == 'DELETE':
        try:
            ar = AgenteRol.objects.get(id_agente_rol=asignacion_id)
            ar.delete()
            return JsonResponse({'message': 'Asignación eliminada exitosamente'})
        except AgenteRol.DoesNotExist:
            return JsonResponse({'error': 'Asignación no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al eliminar asignación'
            }, status=400)


@csrf_exempt
def area_detail(request, pk):
    """Detalle, actualizar y eliminar área"""
    try:
        area = Area.objects.get(id_area=pk)
    except Area.DoesNotExist:
        return JsonResponse({'error': 'Área no encontrada'}, status=404)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': area.id_area,
            'nombre': area.nombre,
            'descripcion': getattr(area, 'descripcion', '')
        })
    
    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            
            # Actualizar campos
            if 'nombre' in data:
                area.nombre = data['nombre']
            if 'descripcion' in data:
                if hasattr(area, 'descripcion'):
                    area.descripcion = data['descripcion']
            
            area.save()
            
            return JsonResponse({
                'id': area.id_area,
                'message': 'Área actualizada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al actualizar área'
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            area.delete()
            return JsonResponse({'message': 'Área eliminada exitosamente'})
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al eliminar área'
            }, status=400)


@csrf_exempt
def rol_detail(request, pk):
    """Detalle, actualizar y eliminar rol"""
    try:
        rol = Rol.objects.get(id_rol=pk)
    except Rol.DoesNotExist:
        return JsonResponse({'error': 'Rol no encontrado'}, status=404)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': rol.id_rol,
            'nombre': rol.nombre,
            'descripcion': rol.descripcion or ''
        })
    
    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            
            # Actualizar campos
            if 'nombre' in data:
                rol.nombre = data['nombre']
            if 'descripcion' in data:
                rol.descripcion = data['descripcion']
            
            rol.save()
            
            return JsonResponse({
                'id': rol.id_rol,
                'message': 'Rol actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al actualizar rol'
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            rol.delete()
            return JsonResponse({'message': 'Rol eliminado exitosamente'})
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error al eliminar rol'
            }, status=400)
