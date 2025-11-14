"""
Vistas para el módulo personas - Sistema GIGA
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import Agente, Area, Rol, AgenteRol, Agrupacion, Organigrama
from auditoria.models import Auditoria
from .serializers import (
    AgenteListSerializer,
    AgenteDetailSerializer, 
    AgenteCreateUpdateSerializer,
    AreaSerializer,
    RolSerializer,
    AgrupacionSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para las vistas."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


def is_authenticated(request):
    """Verificar si el usuario está autenticado usando sesiones Django."""
    return hasattr(request, 'session') and 'agente_id' in request.session


def get_authenticated_agente(request):
    """Obtener el agente autenticado desde la sesión."""
    if not is_authenticated(request):
        return None
    
    try:
        agente_id = request.session.get('agente_id')
        return Agente.objects.get(id_agente=agente_id, activo=True)
    except Agente.DoesNotExist:
        return None


@api_view(['GET'])
@permission_classes([AllowAny])
def get_agentes(request):
    """
    Obtener lista de todos los agentes con paginación y filtros.
    """
    # Verificar autenticación (COMENTADO TEMPORALMENTE PARA TESTING)
    # if not is_authenticated(request):
    #     return Response({
    #         'success': False,
    #         'message': 'Autenticación requerida'
    #     }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Obtener parámetros de filtro
        search = request.GET.get('search', '').strip()
        agrupacion = request.GET.get('agrupacion', '').strip()
        rol = request.GET.get('rol', '').strip()
        area = request.GET.get('area', '').strip()
        activo = request.GET.get('activo', '').strip()
        
        # Consulta base
        queryset = Agente.objects.all().select_related('id_area').prefetch_related(
            'agenterol_set__id_rol'
        ).order_by('apellido', 'nombre')
        
        # Aplicar filtros
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(dni__icontains=search) |
                Q(legajo__icontains=search) |
                Q(email__icontains=search)
            )
        
        if agrupacion:
            queryset = queryset.filter(agrupacion__iexact=agrupacion)
        
        if area:
            queryset = queryset.filter(id_area__nombre__icontains=area)
        
        if activo:
            is_activo = activo.lower() in ['true', '1', 'yes', 'si']
            queryset = queryset.filter(activo=is_activo)
        
        if rol:
            # Filtrar por rol específico
            agentes_con_rol = AgenteRol.objects.filter(
                id_rol__nombre__icontains=rol
            ).values_list('id_agente', flat=True)
            queryset = queryset.filter(id_agente__in=agentes_con_rol)
        
        # Paginación
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = AgenteListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Sin paginación si no se puede paginar
        serializer = AgenteListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener agentes: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_agente(request, agente_id):
    """
    Obtener detalles completos de un agente específico.
    """
    # Verificar autenticación (COMENTADO TEMPORALMENTE PARA TESTING)
    # if not is_authenticated(request):
    #     return Response({
    #         'success': False,
    #         'message': 'Autenticación requerida'
    #     }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        agente = get_object_or_404(Agente, id_agente=agente_id)
        serializer = AgenteDetailSerializer(agente)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener agente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_agente(request):
    """
    Crear un nuevo agente.
    """
    # Verificar autenticación (COMENTADO TEMPORALMENTE PARA TESTING)
    # if not is_authenticated(request):
    #     return Response({
    #         'success': False,
    #         'message': 'Autenticación requerida'
    #     }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        with transaction.atomic():
            serializer = AgenteCreateUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                agente = serializer.save()
                
                # Crear auditoría de creación
                agente_data = AgenteDetailSerializer(agente).data
                crear_auditoria_agente(
                    accion='CREAR',
                    agente_id=agente.id_agente,
                    valor_previo=None,
                    valor_nuevo=agente_data,
                    usuario_logueado_id=None  # TODO: Obtener del usuario autenticado
                )
                
                # Retornar el agente creado con detalles completos
                detail_serializer = AgenteDetailSerializer(agente)
                
                return Response({
                    'success': True,
                    'message': 'Agente creado correctamente',
                    'data': detail_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear agente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_agente(request, agente_id):
    """
    Actualizar un agente existente.
    """
    try:
        with transaction.atomic():
            agente = get_object_or_404(Agente, id_agente=agente_id)
            
            # Capturar datos previos para auditoría
            agente_previo = AgenteDetailSerializer(agente).data
            
            # Usar PATCH para actualizaciones parciales
            partial = request.method == 'PATCH'
            
            serializer = AgenteCreateUpdateSerializer(
                agente, 
                data=request.data, 
                partial=partial
            )
            
            if serializer.is_valid():
                agente = serializer.save()
                
                # Capturar datos nuevos para auditoría
                agente_nuevo = AgenteDetailSerializer(agente).data
                
                # Crear auditoría de actualización
                crear_auditoria_agente(
                    accion='ACTUALIZAR',
                    agente_id=agente.id_agente,
                    valor_previo=agente_previo,
                    valor_nuevo=agente_nuevo,
                    usuario_logueado_id=None  # TODO: Obtener del usuario autenticado
                )
                
                # Retornar el agente actualizado con detalles completos
                detail_serializer = AgenteDetailSerializer(agente)
                
                return Response({
                    'success': True,
                    'message': 'Agente actualizado correctamente',
                    'data': detail_serializer.data
                })
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar agente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_agente(request, agente_id):
    """
    Eliminar un agente y todos los datos relacionados según reglas de negocio:
    - Campos que permiten NULL: se ponen en NULL
    - Campos que NO permiten NULL: se eliminan los registros completos
    """
    try:
        with transaction.atomic():
            agente = get_object_or_404(Agente, id_agente=agente_id)
            
            # Verificar que no sea el usuario actual
            if hasattr(request, 'agente') and request.agente.id_agente == agente.id_agente:
                return Response({
                    'success': False,
                    'message': 'No puedes eliminarte a ti mismo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Capturar datos para auditoría antes de eliminar
            agente_eliminado = AgenteDetailSerializer(agente).data
            
            # Ejecutar eliminación en cascada personalizada
            eliminados = eliminar_agente_con_cascada(agente_id)
            
            # Crear auditoría de eliminación completa
            crear_auditoria_agente(
                accion='ELIMINAR',
                agente_id=agente.id_agente,
                valor_previo=agente_eliminado,
                valor_nuevo=None,
                usuario_logueado_id=None  # TODO: Obtener del usuario autenticado
            )
            
            return Response({
                'success': True,
                'message': f'Agente eliminado correctamente junto con todos sus datos relacionados',
                'data': {
                    'agente_id': agente_id,
                    'eliminados': eliminados
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al eliminar agente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_areas(request):
    """
    Obtener lista de todas las áreas activas.
    """
    try:
        areas = Area.objects.filter(activo=True).order_by('nombre')
        serializer = AreaSerializer(areas, many=True)
        
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener áreas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_roles(request):
    """
    Obtener lista de todos los roles disponibles.
    """
    try:
        roles = Rol.objects.all().order_by('nombre')
        serializer = RolSerializer(roles, many=True)
        
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener roles: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_asignaciones(request):
    """
    Obtener todas las asignaciones de roles a agentes.
    """
    try:
        asignaciones = AgenteRol.objects.all().select_related(
            'id_agente', 'id_rol'
        ).order_by('id_agente__apellido', 'id_agente__nombre')
        
        data = []
        for asignacion in asignaciones:
            data.append({
                'id': asignacion.id_agente_rol,
                'usuario': asignacion.id_agente.id_agente,
                'agente_nombre': f"{asignacion.id_agente.nombre} {asignacion.id_agente.apellido}",
                'rol': asignacion.id_rol.id_rol,
                'rol_nombre': asignacion.id_rol.nombre,
                'asignado_en': asignacion.asignado_en,
                'area': asignacion.id_agente.id_area.id_area if asignacion.id_agente.id_area else None,
                'area_nombre': asignacion.id_agente.id_area.nombre if asignacion.id_agente.id_area else None
            })
        
        return Response({
            'success': True,
            'data': {
                'results': data,
                'count': len(data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener asignaciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_asignacion(request):
    """
    Crear nueva asignación de rol a agente.
    """
    try:
        with transaction.atomic():
            usuario_id = request.data.get('usuario')
            rol_id = request.data.get('rol')
            
            if not usuario_id or not rol_id:
                return Response({
                    'success': False,
                    'message': 'Usuario y rol son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que existan
            agente = get_object_or_404(Agente, id_agente=usuario_id)
            rol = get_object_or_404(Rol, id_rol=rol_id)
            
            # Crear asignación
            asignacion = AgenteRol.objects.create(
                id_agente=agente,
                id_rol=rol
            )
            
            return Response({
                'success': True,
                'message': 'Asignación creada correctamente',
                'data': {
                    'id': asignacion.id_agente_rol,
                    'usuario': asignacion.id_agente.id_agente,
                    'rol': asignacion.id_rol.id_rol,
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear asignación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_asignacion(request, asignacion_id):
    """
    Eliminar asignación de rol.
    """
    try:
        asignacion = get_object_or_404(AgenteRol, id_agente_rol=asignacion_id)
        asignacion.delete()
        
        return Response({
            'success': True,
            'message': 'Asignación eliminada correctamente'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al eliminar asignación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINTS PARA GESTIÓN DE PARÁMETROS DEL SISTEMA
# ============================================================================

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_area(request):
    """
    Crear nueva área.
    """
    try:
        with transaction.atomic():
            serializer = AreaSerializer(data=request.data)
            
            if serializer.is_valid():
                area = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Área creada correctamente',
                    'data': {
                        'id_area': area.id_area,
                        'nombre': area.nombre,
                        'activo': area.activo
                    }
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear área: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_area(request, area_id):
    """
    Actualizar área existente.
    """
    try:
        with transaction.atomic():
            area = get_object_or_404(Area, id_area=area_id)
            
            partial = request.method == 'PATCH'
            serializer = AreaSerializer(area, data=request.data, partial=partial)
            
            if serializer.is_valid():
                area = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Área actualizada correctamente',
                    'data': {
                        'id_area': area.id_area,
                        'nombre': area.nombre,
                        'activo': area.activo
                    }
                })
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar área: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_area(request, area_id):
    """
    Eliminar área (soft delete) y reasignar agentes a área por defecto.
    """
    try:
        with transaction.atomic():
            area = get_object_or_404(Area, id_area=area_id)
            
            # Verificar si hay agentes asignados
            agentes_asignados = Agente.objects.filter(id_area=area, activo=True).count()
            
            if agentes_asignados > 0:
                # Buscar área por defecto (primera activa)
                area_default = Area.objects.filter(activo=True).first()
                
                if area_default and area_default.id_area != area.id_area:
                    # Reasignar agentes al área por defecto
                    Agente.objects.filter(id_area=area, activo=True).update(id_area=area_default)
                    message = f'Área eliminada. {agentes_asignados} agente(s) reasignado(s) al área "{area_default.nombre}"'
                else:
                    # Si no hay área por defecto, desasignar agentes
                    Agente.objects.filter(id_area=area, activo=True).update(id_area=None)
                    message = f'Área eliminada. {agentes_asignados} agente(s) desasignado(s) de área'
            else:
                message = 'Área eliminada correctamente'
            
            # Marcar área como inactiva
            area.activo = False
            area.save()
            
            return Response({
                'success': True,
                'message': message
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al eliminar área: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def update_area_schedule(request, area_id):
    """
    Actualizar horarios de todos los agentes de un área.
    """
    try:
        with transaction.atomic():
            area = get_object_or_404(Area, id_area=area_id)
            
            horario_entrada = request.data.get('horario_entrada')
            horario_salida = request.data.get('horario_salida')
            
            if not horario_entrada or not horario_salida:
                return Response({
                    'success': False,
                    'message': 'Horario de entrada y salida son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar horarios de todos los agentes del área
            agentes_actualizados = Agente.objects.filter(
                id_area=area, 
                activo=True
            ).update(
                horario_entrada=horario_entrada,
                horario_salida=horario_salida
            )
            
            return Response({
                'success': True,
                'message': f'Horarios actualizados para {agentes_actualizados} agente(s) del área "{area.nombre}"',
                'data': {
                    'area': area.nombre,
                    'agentes_actualizados': agentes_actualizados,
                    'horario_entrada': horario_entrada,
                    'horario_salida': horario_salida
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar horarios: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_agrupaciones(request):
    """
    Obtener lista de todas las agrupaciones organizacionales.
    """
    try:
        # Obtener agrupaciones de la tabla agrupacion
        agrupaciones = Agrupacion.objects.filter(activo=True).order_by('nombre')
        serializer = AgrupacionSerializer(agrupaciones, many=True)
        
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': len(serializer.data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener agrupaciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_agrupacion(request):
    """
    Crear nueva agrupación organizacional.
    """
    try:
        with transaction.atomic():
            serializer = AgrupacionSerializer(data=request.data)
            
            if serializer.is_valid():
                agrupacion = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Agrupación creada correctamente',
                    'data': AgrupacionSerializer(agrupacion).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear agrupación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_agrupacion(request, agrupacion_id):
    """
    Actualizar agrupación existente.
    """
    try:
        with transaction.atomic():
            agrupacion = get_object_or_404(Agrupacion, id_agrupacion=agrupacion_id)
            
            partial = request.method == 'PATCH'
            serializer = AgrupacionSerializer(agrupacion, data=request.data, partial=partial)
            
            if serializer.is_valid():
                # Si se cambia el nombre, actualizar en tabla agente
                nombre_anterior = agrupacion.nombre
                agrupacion = serializer.save()
                
                if nombre_anterior != agrupacion.nombre:
                    # Actualizar campo agrupacion en tabla agente
                    Agente.objects.filter(
                        agrupacion=nombre_anterior,
                        activo=True
                    ).update(agrupacion=agrupacion.nombre)
                
                return Response({
                    'success': True,
                    'message': 'Agrupación actualizada correctamente',
                    'data': AgrupacionSerializer(agrupacion).data
                })
            
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar agrupación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def update_agrupacion_schedule(request):
    """
    Actualizar horarios de todos los agentes de una agrupación.
    """
    try:
        with transaction.atomic():
            agrupacion_nombre = request.data.get('agrupacion')
            horario_entrada = request.data.get('horario_entrada')
            horario_salida = request.data.get('horario_salida')
            
            if not agrupacion_nombre:
                return Response({
                    'success': False,
                    'message': 'Nombre de agrupación es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not horario_entrada or not horario_salida:
                return Response({
                    'success': False,
                    'message': 'Horario de entrada y salida son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar horarios de todos los agentes de la agrupación
            agentes_actualizados = Agente.objects.filter(
                agrupacion=agrupacion_nombre,
                activo=True
            ).update(
                horario_entrada=horario_entrada,
                horario_salida=horario_salida
            )
            
            return Response({
                'success': True,
                'message': f'Horarios actualizados para {agentes_actualizados} agente(s) de la agrupación "{agrupacion_nombre}"',
                'data': {
                    'agrupacion': agrupacion_nombre,
                    'agentes_actualizados': agentes_actualizados,
                    'horario_entrada': horario_entrada,
                    'horario_salida': horario_salida
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar horarios de agrupación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def rename_agrupacion(request):
    """
    Renombrar una agrupación organizacional.
    """
    try:
        with transaction.atomic():
            nombre_actual = request.data.get('nombre_actual')
            nombre_nuevo = request.data.get('nombre_nuevo')
            
            if not nombre_actual or not nombre_nuevo:
                return Response({
                    'success': False,
                    'message': 'Nombre actual y nuevo son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que el nuevo nombre no exista
            if Agente.objects.filter(
                agrupacion=nombre_nuevo,
                activo=True
            ).exists():
                return Response({
                    'success': False,
                    'message': f'Ya existe una agrupación con el nombre "{nombre_nuevo}"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar el nombre en todos los agentes
            agentes_actualizados = Agente.objects.filter(
                agrupacion=nombre_actual,
                activo=True
            ).update(agrupacion=nombre_nuevo)
            
            return Response({
                'success': True,
                'message': f'Agrupación renombrada correctamente. {agentes_actualizados} agente(s) actualizados',
                'data': {
                    'nombre_anterior': nombre_actual,
                    'nombre_nuevo': nombre_nuevo,
                    'agentes_actualizados': agentes_actualizados
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al renombrar agrupación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_agrupacion(request, agrupacion_id):
    """
    Eliminar una agrupación organizacional (reasignar agentes a otra agrupación o desasignar).
    """
    try:
        with transaction.atomic():
            agrupacion = get_object_or_404(Agrupacion, id_agrupacion=agrupacion_id)
            nueva_agrupacion = request.data.get('nueva_agrupacion', None)
            
            # Contar agentes en la agrupación
            agentes_count = Agente.objects.filter(
                agrupacion=agrupacion.nombre,
                activo=True
            ).count()
            
            if nueva_agrupacion:
                # Reasignar a nueva agrupación
                Agente.objects.filter(
                    agrupacion=agrupacion.nombre,
                    activo=True
                ).update(agrupacion=nueva_agrupacion)
                
                message = f'Agrupación "{agrupacion.nombre}" eliminada. {agentes_count} agente(s) reasignado(s) a "{nueva_agrupacion}"'
            else:
                # Desasignar agrupación (vacío)
                Agente.objects.filter(
                    agrupacion=agrupacion.nombre,
                    activo=True
                ).update(agrupacion=None)
                
                message = f'Agrupación "{agrupacion.nombre}" eliminada. {agentes_count} agente(s) sin agrupación asignada'
            
            # Marcar agrupación como inactiva
            agrupacion.activo = False
            agrupacion.save()
            
            return Response({
                'success': True,
                'message': message
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al eliminar agrupación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# FUNCIONES AUXILIARES PARA ELIMINACIÓN Y AUDITORÍA
# ============================================================================

def eliminar_agente_con_cascada(agente_id):
    """
    Eliminar un agente y todos sus datos relacionados según las reglas:
    - Si el campo FK permite NULL: poner en NULL
    - Si el campo FK NO permite NULL: eliminar el registro completo
    
    Retorna un resumen de las operaciones realizadas.
    """
    from django.db import connection
    
    eliminados = {}
    
    try:
        with connection.cursor() as cursor:
            # 1. AUDITORIA: id_agente permite NULL -> SET NULL
            cursor.execute(
                "UPDATE auditoria SET id_agente = NULL WHERE id_agente = %s",
                [agente_id]
            )
            eliminados['auditoria_actualizados'] = cursor.rowcount
            
            # 2. AGENTE_ROL: id_agente NO permite NULL -> DELETE
            cursor.execute(
                "DELETE FROM agente_rol WHERE id_agente = %s",
                [agente_id]
            )
            eliminados['agente_rol_eliminados'] = cursor.rowcount
            
            # 3. ASISTENCIA: tanto id_agente como creado_por NO permiten NULL -> DELETE
            cursor.execute(
                "DELETE FROM asistencia WHERE id_agente = %s OR creado_por = %s",
                [agente_id, agente_id]
            )
            eliminados['asistencia_eliminados'] = cursor.rowcount
            
            # 4. CRONOGRAMA: id_director y id_jefe NO permiten NULL -> DELETE
            cursor.execute(
                "DELETE FROM cronograma WHERE id_director = %s OR id_jefe = %s",
                [agente_id, agente_id]
            )
            eliminados['cronograma_eliminados'] = cursor.rowcount
            
            # 5. GUARDIA: id_agente NO permite NULL -> DELETE
            cursor.execute(
                "DELETE FROM guardia WHERE id_agente = %s",
                [agente_id]
            )
            eliminados['guardia_eliminados'] = cursor.rowcount
            
            # 6. LICENCIA: id_agente NO permite NULL -> DELETE
            cursor.execute(
                "DELETE FROM licencia WHERE id_agente = %s",
                [agente_id]
            )
            eliminados['licencia_eliminados'] = cursor.rowcount
            
            # 7. PARTE_DIARIO: id_agente, creado_por, actualizado_por NO permiten NULL -> DELETE
            cursor.execute(
                "DELETE FROM parte_diario WHERE id_agente = %s OR creado_por = %s OR actualizado_por = %s",
                [agente_id, agente_id, agente_id]
            )
            eliminados['parte_diario_eliminados'] = cursor.rowcount
            
            # 8. RESUMEN_GUARDIA_MES: id_agente NO permite NULL -> DELETE
            cursor.execute(
                "DELETE FROM resumen_guardia_mes WHERE id_agente = %s",
                [agente_id]
            )
            eliminados['resumen_guardia_mes_eliminados'] = cursor.rowcount
            
            # 9. Finalmente, eliminar el AGENTE
            cursor.execute(
                "DELETE FROM agente WHERE id_agente = %s",
                [agente_id]
            )
            eliminados['agente_eliminado'] = cursor.rowcount
            
    except Exception as e:
        raise Exception(f"Error en eliminación en cascada: {str(e)}")
    
    return eliminados


def crear_auditoria_agente(accion, agente_id, valor_previo=None, valor_nuevo=None, usuario_logueado_id=None):
    """
    Crear registro de auditoría para cambios en agentes.
    """
    try:
        from django.utils import timezone
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        # Convertir datos a JSON serializable
        valor_previo_json = None
        valor_nuevo_json = None
        
        if valor_previo:
            valor_previo_json = json.loads(json.dumps(valor_previo, cls=DjangoJSONEncoder))
        
        if valor_nuevo:
            valor_nuevo_json = json.loads(json.dumps(valor_nuevo, cls=DjangoJSONEncoder))
        
        Auditoria.objects.create(
            pk_afectada=agente_id,
            nombre_tabla='agente',
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=usuario_logueado_id  # FK al agente que hizo el cambio
        )
    except Exception as e:
        # No fallar si la auditoría falla, solo registrar
        print(f"Error al crear auditoría: {str(e)}")


def crear_auditoria_organigrama(accion, organigrama_id, valor_previo=None, valor_nuevo=None, agente_id=None):
    """
    Crear registro de auditoría para cambios en organigrama.
    """
    try:
        from django.utils import timezone
        
        Auditoria.objects.create(
            pk_afectada=organigrama_id,
            nombre_tabla='organigrama',
            creado_en=timezone.now(),
            valor_previo=valor_previo,
            valor_nuevo=valor_nuevo,
            accion=accion,
            id_agente_id=agente_id  # FK al agente que hizo el cambio
        )
    except Exception as e:
        # No fallar si la auditoría falla, solo registrar
        print(f"Error al crear auditoría: {str(e)}")


# ============================================================================
# ENDPOINTS PARA GESTIÓN DE ORGANIGRAMA
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_organigrama(request):
    """
    Obtener la estructura del organigrama activa.
    """
    try:
        # Obtener el organigrama activo más reciente
        organigrama = Organigrama.objects.filter(activo=True).first()
        
        if not organigrama:
            # Si no existe, devolver estructura por defecto
            return Response({
                'success': True,
                'data': {
                    'id': None,
                    'nombre': 'Sin organigrama configurado',
                    'version': '1.0.0',
                    'estructura': [],
                    'creado_por': 'Sistema',
                    'actualizado_en': None,
                    'es_nuevo': True
                }
            })
        
        return Response({
            'success': True,
            'data': {
                'id': organigrama.id_organigrama,
                'nombre': organigrama.nombre,
                'version': organigrama.version,
                'estructura': organigrama.estructura,
                'creado_por': organigrama.creado_por,
                'actualizado_en': organigrama.actualizado_en,
                'es_nuevo': False
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener organigrama: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST', 'PUT'])
@permission_classes([AllowAny])
def save_organigrama(request):
    """
    Guardar o actualizar la estructura del organigrama.
    """
    try:
        with transaction.atomic():
            estructura = request.data.get('estructura')
            nombre = request.data.get('nombre', 'Organigrama Principal')
            version = request.data.get('version', '1.0.0')
            creado_por = request.data.get('creado_por', 'Administrador')
            
            if not estructura:
                return Response({
                    'success': False,
                    'message': 'La estructura del organigrama es requerida'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener organigrama anterior para auditoría
            organigrama_anterior = Organigrama.objects.filter(activo=True).first()
            valor_previo = None
            
            if organigrama_anterior:
                valor_previo = {
                    'id': organigrama_anterior.id_organigrama,
                    'nombre': organigrama_anterior.nombre,
                    'version': organigrama_anterior.version,
                    'estructura': organigrama_anterior.estructura,
                    'creado_por': organigrama_anterior.creado_por
                }
            
            # Desactivar organigramas anteriores
            Organigrama.objects.filter(activo=True).update(activo=False)
            
            # Crear nuevo organigrama
            organigrama = Organigrama.objects.create(
                nombre=nombre,
                estructura=estructura,
                version=version,
                creado_por=creado_por,
                activo=True
            )
            
            # Crear auditoría
            valor_nuevo = {
                'id': organigrama.id_organigrama,
                'nombre': organigrama.nombre,
                'version': organigrama.version,
                'estructura': organigrama.estructura,
                'creado_por': organigrama.creado_por,
                'actualizado_en': organigrama.actualizado_en.isoformat()
            }
            
            accion = 'ACTUALIZAR' if organigrama_anterior else 'CREAR'
            crear_auditoria_organigrama(
                accion=accion,
                organigrama_id=organigrama.id_organigrama,
                valor_previo=valor_previo,
                valor_nuevo=valor_nuevo,
                agente_id=None  # TODO: Obtener del usuario autenticado
            )
            
            return Response({
                'success': True,
                'message': 'Organigrama guardado correctamente',
                'data': {
                    'id': organigrama.id_organigrama,
                    'nombre': organigrama.nombre,
                    'version': organigrama.version,
                    'estructura': organigrama.estructura,
                    'creado_por': organigrama.creado_por,
                    'actualizado_en': organigrama.actualizado_en
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al guardar organigrama: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_organigrama_historial(request):
    """
    Obtener historial de versiones del organigrama.
    """
    try:
        organigramas = Organigrama.objects.all().order_by('-actualizado_en')
        
        data = []
        for org in organigramas:
            data.append({
                'id': org.id_organigrama,
                'nombre': org.nombre,
                'version': org.version,
                'creado_por': org.creado_por,
                'activo': org.activo,
                'creado_en': org.creado_en,
                'actualizado_en': org.actualizado_en,
                'nodos_count': len(_contar_nodos_recursivo(org.estructura)) if isinstance(org.estructura, list) else len(_contar_nodos_recursivo([org.estructura]))
            })
        
        return Response({
            'success': True,
            'data': {
                'results': data,
                'count': len(data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener historial: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _contar_nodos_recursivo(nodos):
    """
    Función auxiliar para contar nodos en la estructura recursivamente.
    """
    count = 0
    if isinstance(nodos, list):
        for nodo in nodos:
            count += 1
            if isinstance(nodo, dict) and 'children' in nodo:
                count += _contar_nodos_recursivo(nodo['children'])
    elif isinstance(nodos, dict):
        count += 1
        if 'children' in nodos:
            count += _contar_nodos_recursivo(nodos['children'])
    
    return count


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def restore_organigrama(request, organigrama_id):
    """
    Restaurar una versión específica del organigrama.
    """
    try:
        with transaction.atomic():
            # Obtener el organigrama a restaurar
            organigrama_original = get_object_or_404(Organigrama, id_organigrama=organigrama_id)
            
            # Obtener organigrama actual para auditoría
            organigrama_actual = Organigrama.objects.filter(activo=True).first()
            valor_previo = None
            
            if organigrama_actual:
                valor_previo = {
                    'id': organigrama_actual.id_organigrama,
                    'nombre': organigrama_actual.nombre,
                    'version': organigrama_actual.version,
                    'estructura': organigrama_actual.estructura,
                    'creado_por': organigrama_actual.creado_por
                }
            
            # Desactivar organigramas actuales
            Organigrama.objects.filter(activo=True).update(activo=False)
            
            # Crear nueva versión basada en la original
            nuevo_organigrama = Organigrama.objects.create(
                nombre=f"{organigrama_original.nombre} (Restaurado)",
                estructura=organigrama_original.estructura,
                version=f"{organigrama_original.version}-restored",
                creado_por=request.data.get('creado_por', 'Administrador'),
                activo=True
            )
            
            # Crear auditoría de restauración
            valor_nuevo = {
                'id': nuevo_organigrama.id_organigrama,
                'nombre': nuevo_organigrama.nombre,
                'version': nuevo_organigrama.version,
                'estructura': nuevo_organigrama.estructura,
                'creado_por': nuevo_organigrama.creado_por,
                'actualizado_en': nuevo_organigrama.actualizado_en.isoformat(),
                'restaurado_desde': organigrama_original.id_organigrama
            }
            
            crear_auditoria_organigrama(
                accion='RESTAURAR',
                organigrama_id=nuevo_organigrama.id_organigrama,
                valor_previo=valor_previo,
                valor_nuevo=valor_nuevo,
                agente_id=None  # TODO: Obtener del usuario autenticado
            )
            
            return Response({
                'success': True,
                'message': f'Organigrama v{organigrama_original.version} restaurado correctamente',
                'data': {
                    'id': nuevo_organigrama.id_organigrama,
                    'nombre': nuevo_organigrama.nombre,
                    'version': nuevo_organigrama.version,
                    'estructura': nuevo_organigrama.estructura,
                    'creado_por': nuevo_organigrama.creado_por,
                    'actualizado_en': nuevo_organigrama.actualizado_en
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al restaurar organigrama: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
