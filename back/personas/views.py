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

# RBAC Permissions
from common.permissions import (
    IsAuthenticatedGIGA, IsAdministrador, IsJefaturaOrAbove,
    obtener_agente_sesion, obtener_rol_agente, obtener_areas_jerarquia
)



class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para las vistas."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


def is_authenticated(request):
    """Verificar si el usuario está autenticado usando sesiones Django."""
    return hasattr(request, 'session') and 'user_id' in request.session


def get_authenticated_agente(request):
    """Obtener el agente autenticado desde la sesión."""
    if not is_authenticated(request):
        return None
    
    try:
        agente_id = request.session.get('user_id')
        return Agente.objects.get(id_agente=agente_id, activo=True)
    except Agente.DoesNotExist:
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def get_agentes(request):
    """
    Obtener lista de todos los agentes con paginación y filtros.
    
    RBAC - Lógica Correcta:
    - Administrador: Todos los agentes de todas las áreas
    - Director: Agentes, agente_avanzado, jefatura de su área + sub-áreas
    - Jefatura: Agentes y agentes_avanzados de su área (sin sub-áreas)
    - Agente Avanzado: Su info + otros agentes (NO jefatura/director) de su área
    - Agente: Solo su propia información
    """
    # Verificar autenticación (COMENTADO TEMPORALMENTE PARA TESTING)
    # if not is_authenticated(request):
    #     return Response({
    #         'success': False,
    #         'message': 'Autenticación requerida'
    #     }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # RBAC: Obtener agente y rol de sesión
        agente_sesion = obtener_agente_sesion(request)
        if not agente_sesion:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        rol_sesion = obtener_rol_agente(agente_sesion)
        
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
        
        # RBAC: Filtrar por rol del usuario
        if rol_sesion == 'administrador':
            # Admin ve todos
            pass
        
        elif rol_sesion == 'director':
            # Director ve agentes, agente_avanzado, jefatura de su área + sub-áreas
            areas_permitidas = obtener_areas_jerarquia(agente_sesion)
            area_ids = [a.id_area for a in areas_permitidas]
            queryset = queryset.filter(id_area__id_area__in=area_ids)
        
        elif rol_sesion == 'jefatura':
            # Jefatura ve agentes y agentes_avanzados de su área (sin sub-áreas)
            areas_permitidas = obtener_areas_jerarquia(agente_sesion)
            area_ids = [a.id_area for a in areas_permitidas]
            queryset = queryset.filter(id_area__id_area__in=area_ids)
        
        elif rol_sesion == 'agente_avanzado':
            # Agente Avanzado: su info + otros agentes (no jefatura/director) de su área
            areas_permitidas = obtener_areas_jerarquia(agente_sesion)
            area_ids = [a.id_area for a in areas_permitidas]
            
            # Filtrar por área Y excluir roles superiores
            from personas.models import Rol
            queryset = queryset.filter(id_area__id_area__in=area_ids)
            
            # Excluir Jefatura, Director, Administrador (solo ve agentes y agentes_avanzados)
            roles_excluir = Rol.objects.filter(
                nombre__in=['Jefatura', 'Director', 'Administrador']
            ).values_list('id_rol', flat=True)
            
            queryset = queryset.exclude(
                agenterol__id_rol__in=roles_excluir
            ).distinct()
        
        else:  # agente
            # Agente: solo ve su propia información
            queryset = queryset.filter(id_agente=agente_sesion.id_agente)
        
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
            # Intentar filtrar por ID de área si es numérico, sino por nombre
            if area.isdigit():
                queryset = queryset.filter(id_area__id_area=int(area))
            else:
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAdministrador])  # CRÍTICO: Solo admin puede crear agentes
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
@api_view(['PATCH'])
@permission_classes([IsAdministrador])  #CRÍTICO: Solo admin puede editar agentes
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
@permission_classes([IsAdministrador])  # CRÍTICO: Solo admin puede eliminar agentes
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def get_areas(request):
    """
    Obtener todas las áreas del sistema con información jerárquica
    """
    try:
        incluir_jerarquia = request.GET.get('jerarquia', 'false').lower() == 'true'
        
        if incluir_jerarquia:
            # Obtener estructura jerárquica
            areas_raiz = Area.objects.filter(id_area_padre__isnull=True, activo=True).order_by('nombre')
            
            def construir_arbol(areas):
                resultado = []
                for area in areas:
                    area_data = {
                        'id_area': area.id_area,
                        'nombre': area.nombre,
                        'descripcion': area.descripcion,
                        'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                        'jefe_area': {
                            'id_agente': area.jefe_area.id_agente,
                            'nombre_completo': f"{area.jefe_area.nombre} {area.jefe_area.apellido}"
                        } if area.jefe_area else None,
                        'nivel': area.nivel,

                        'activo': area.activo,
                        'nombre_completo': area.nombre_completo,
                        'es_raiz': area.es_raiz,
                        'total_agentes': area.total_agentes,
                        'total_agentes_jerarquico': area.total_agentes_jerarquico,
                        'children': construir_arbol(area.hijos)
                    }
                    resultado.append(area_data)
                return resultado
            
            areas_data = construir_arbol(areas_raiz)
        else:
            # Lista plana como antes
            areas = Area.objects.filter(activo=True).order_by('nombre')
            areas_data = []
            for area in areas:
                areas_data.append({
                    'id_area': area.id_area,
                    'nombre': area.nombre,
                    'descripcion': area.descripcion if hasattr(area, 'descripcion') else None,
                    'id_area_padre': area.id_area_padre.id_area if hasattr(area, 'id_area_padre') and area.id_area_padre else None,
                    'jefe_area': {
                        'id_agente': area.jefe_area.id_agente,
                        'nombre_completo': f"{area.jefe_area.nombre} {area.jefe_area.apellido}"
                    } if hasattr(area, 'jefe_area') and area.jefe_area else None,
                    'nivel': getattr(area, 'nivel', 0),
                    'activo': area.activo,
                    'nombre_completo': getattr(area, 'nombre_completo', area.nombre),
                    'total_agentes': getattr(area, 'total_agentes', 0)
                })
        
        return Response({
            'success': True,
            'data': {
                'results': areas_data,
                'count': len(areas_data),
                'jerarquia': incluir_jerarquia
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener áreas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedGIGA])
def get_subareas(request, area_id):
    """
    Obtener todas las sub-áreas (recursivamente) de un área dada.
    
    Útil para Director que debe ver usuarios de su área + sub-áreas.
    Retorna un array plano de todas las sub-áreas en cualquier nivel de profundidad.
    
    Ejemplo:
        Área A (nivel 0)
          └─ Área B (nivel 1)
              └─ Área C (nivel 2)
        
        GET /areas/A/subareas/ → [B, C]
    """
    try:
        # Verificar que el área existe
        try:
            area_padre = Area.objects.get(id_area=area_id, activo=True)
        except Area.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Área con ID {area_id} no encontrada o inactiva'
            }, status=status.HTTP_404_NOT_FOUND)
        
        def get_all_subareas_recursive(parent_id):
            """
            Función recursiva para obtener todas las sub-áreas
            """
            # Obtener sub-áreas directas
            subareas_directas = list(Area.objects.filter(
                id_area_padre=parent_id,
                activo=True
            ))
            
            # Inicializar con sub-áreas directas
            todas_subareas = subareas_directas.copy()
            
            # Para cada sub-área, obtener sus sub-áreas recursivamente
            for subarea in subareas_directas:
                todas_subareas.extend(get_all_subareas_recursive(subarea.id_area))
            
            return todas_subareas
        
        # Obtener todas las sub-áreas recursivamente
        subareas = get_all_subareas_recursive(area_id)
        
        # Serializar datos
        subareas_data = []
        for subarea in subareas:
            subareas_data.append({
                'id_area': subarea.id_area,
                'nombre': subarea.nombre,
                'descripcion': subarea.descripcion if subarea.descripcion else None,
                'nivel': subarea.nivel,
                'id_area_padre': subarea.id_area_padre.id_area if subarea.id_area_padre else None,
                'activo': subarea.activo
            })
        
        return Response({
            'success': True,
            'data': {
                'area_padre': {
                    'id_area': area_padre.id_area,
                    'nombre': area_padre.nombre
                },
                'subareas': subareas_data,
                'count': len(subareas_data)
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener sub-áreas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
            
            # Crear auditoría para cambio de rol
            crear_auditoria_rol(
                accion='ASIGNAR_ROL',
                agente_id=agente.id_agente,
                rol_id=rol.id_rol,
                valor_previo=None,
                valor_nuevo={
                    'agente': f"{agente.nombre} {agente.apellido}",
                    'rol': rol.nombre,
                    'asignacion_id': asignacion.id_agente_rol
                },
                usuario_logueado_id=None  # TODO: Obtener del usuario autenticado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def delete_asignacion(request, asignacion_id):
    """
    Eliminar asignación de rol.
    """
    try:
        asignacion = get_object_or_404(AgenteRol, id_agente_rol=asignacion_id)
        
        # Obtener datos para auditoría antes de eliminar
        agente = asignacion.id_agente
        rol = asignacion.id_rol
        
        # Eliminar asignación
        asignacion.delete()
        
        # Crear auditoría para eliminación de rol
        crear_auditoria_rol(
            accion='QUITAR_ROL',
            agente_id=agente.id_agente,
            rol_id=rol.id_rol,
            valor_previo={
                'agente': f"{agente.nombre} {agente.apellido}",
                'rol': rol.nombre,
                'asignacion_id': asignacion_id
            },
            valor_nuevo=None,
            usuario_logueado_id=None  # TODO: Obtener del usuario autenticado
        )
        
        return Response({
            'success': True,
            'message': 'Asignación eliminada correctamente'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al eliminar asignación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def cambiar_rol_agente(request):
    """
    Cambia el rol de un agente eliminando todos los roles previos y asignando uno nuevo.
    Operación atómica para garantizar un solo rol por agente.
    """
    try:
        with transaction.atomic():
            agente_id = request.data.get('agente_id')
            nuevo_rol_id = request.data.get('rol_id')  # Puede ser None para "sin rol"
            
            if not agente_id:
                return Response({
                    'success': False,
                    'message': 'ID del agente es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que el agente existe
            agente = get_object_or_404(Agente, id_agente=agente_id)
            
            # Obtener roles actuales para auditoría
            roles_actuales = AgenteRol.objects.filter(id_agente=agente_id)
            roles_previos = []
            
            for rol_actual in roles_actuales:
                roles_previos.append({
                    'rol_id': rol_actual.id_rol.id_rol,
                    'rol_nombre': rol_actual.id_rol.nombre,
                    'asignacion_id': rol_actual.id_agente_rol
                })
            
            # PASO 1: Eliminar TODOS los roles actuales del agente
            count_eliminados = roles_actuales.delete()[0]
            
            # PASO 2: Si se especifica un nuevo rol, asignarlo
            nueva_asignacion = None
            if nuevo_rol_id and str(nuevo_rol_id).strip():
                nuevo_rol = get_object_or_404(Rol, id_rol=nuevo_rol_id)
                nueva_asignacion = AgenteRol.objects.create(
                    id_agente=agente,
                    id_rol=nuevo_rol
                )
            
            # PASO 3: Crear auditoría del cambio
            valor_previo = {
                'agente': f"{agente.nombre} {agente.apellido}",
                'roles_previos': roles_previos,
                'cantidad_eliminados': count_eliminados
            } if roles_previos else None
            
            valor_nuevo = {
                'agente': f"{agente.nombre} {agente.apellido}",
                'nuevo_rol': nuevo_rol.nombre if nueva_asignacion else None,
                'asignacion_id': nueva_asignacion.id_agente_rol if nueva_asignacion else None
            }
            
            crear_auditoria_rol(
                accion='CAMBIO_ROL_ATOMICO',
                agente_id=agente.id_agente,
                rol_id=nuevo_rol_id,
                valor_previo=valor_previo,
                valor_nuevo=valor_nuevo,
                usuario_logueado_id=None  # TODO: Obtener del usuario autenticado
            )
            
            return Response({
                'success': True,
                'message': f'Rol actualizado correctamente. Eliminados: {count_eliminados} roles previos.',
                'data': {
                    'agente_id': agente.id_agente,
                    'roles_eliminados': count_eliminados,
                    'nuevo_rol': nuevo_rol.nombre if nueva_asignacion else None,
                    'asignacion_id': nueva_asignacion.id_agente_rol if nueva_asignacion else None
                }
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al cambiar rol: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def limpiar_roles_duplicados(request):
    """
    Limpia roles duplicados dejando solo el más reciente por agente.
    """
    try:
        from django.db.models import Count
        
        # Encontrar agentes con múltiples roles
        agentes_multiples = AgenteRol.objects.values('id_agente').annotate(
            count=Count('id_agente')
        ).filter(count__gt=1)
        
        resultados = {
            'agentes_procesados': 0,
            'roles_eliminados': 0,
            'detalles': []
        }
        
        for agente_data in agentes_multiples:
            agente_id = agente_data['id_agente']
            count = agente_data['count']
            
            try:
                # Obtener información del agente
                agente = Agente.objects.get(id_agente=agente_id)
                
                # Obtener todos los roles de este agente ordenados por ID
                roles = AgenteRol.objects.filter(id_agente=agente_id).order_by('id_agente_rol')
                
                # Mantener solo el último rol (más reciente)
                ultimo_rol = roles.last()
                roles_a_eliminar = roles.exclude(id_agente_rol=ultimo_rol.id_agente_rol)
                
                detalle = {
                    'agente_id': agente_id,
                    'nombre': f"{agente.nombre} {agente.apellido}",
                    'roles_totales': count,
                    'rol_mantenido': ultimo_rol.id_rol.nombre,
                    'roles_eliminados': []
                }
                
                with transaction.atomic():
                    for rol_eliminar in roles_a_eliminar:
                        detalle['roles_eliminados'].append(rol_eliminar.id_rol.nombre)
                        rol_eliminar.delete()
                        resultados['roles_eliminados'] += 1
                
                resultados['detalles'].append(detalle)
                resultados['agentes_procesados'] += 1
                    
            except Exception as e:
                resultados['detalles'].append({
                    'agente_id': agente_id,
                    'error': str(e)
                })
        
        # Verificar que no queden roles duplicados
        agentes_multiples_post = AgenteRol.objects.values('id_agente').annotate(
            count=Count('id_agente')
        ).filter(count__gt=1)
        
        resultados['exito'] = len(agentes_multiples_post) == 0
        resultados['agentes_restantes_con_multiples_roles'] = len(agentes_multiples_post)
        
        return Response({
            'success': True,
            'message': 'Limpieza completada',
            'data': resultados
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error en la limpieza: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINTS PARA GESTIÓN DE PARÁMETROS DEL SISTEMA
# ============================================================================

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def create_area(request):
    """
    Crear nueva área con soporte para jerarquía, descripción y jefe.
    """
    try:
        with transaction.atomic():
            # Extraer datos del request
            nombre = request.data.get('nombre', '').strip()
            descripcion = request.data.get('descripcion', '').strip()
            id_area_padre = request.data.get('id_area_padre')
            jefe_area_id = request.data.get('jefe_area')
            agentes_asignados = request.data.get('agentes_asignados', [])
            activo = request.data.get('activo', True)
            
            # Validaciones
            if not nombre:
                return Response({
                    'success': False,
                    'message': 'El nombre del área es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar área padre si se especifica
            area_padre = None
            nivel = 0
            if id_area_padre:
                try:
                    area_padre = Area.objects.get(id_area=id_area_padre, activo=True)
                    nivel = area_padre.nivel + 1
                except Area.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'El área padre especificada no existe'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar jefe del área si se especifica
            jefe_area = None
            if jefe_area_id:
                try:
                    jefe_area = Agente.objects.get(id_agente=jefe_area_id, activo=True)
                except Agente.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'El jefe especificado no existe'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar unicidad del nombre en el mismo nivel
            if Area.objects.filter(
                nombre__iexact=nombre,
                id_area_padre=area_padre,
                activo=True
            ).exists():
                return Response({
                    'success': False,
                    'message': 'Ya existe un área con ese nombre en el mismo nivel jerárquico'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear área
            area = Area.objects.create(
                nombre=nombre,
                descripcion=descripcion or None,
                id_area_padre=area_padre,
                jefe_area=jefe_area,
                nivel=nivel,
                activo=activo
            )
            
            # Asignar agentes al área si se especificaron
            agentes_asignados_exitosos = []
            if agentes_asignados:
                for agente_id in agentes_asignados:
                    try:
                        agente = Agente.objects.get(id_agente=agente_id, activo=True)
                        agente.id_area = area
                        agente.save()
                        agentes_asignados_exitosos.append({
                            'id_agente': agente.id_agente,
                            'nombre_completo': f"{agente.nombre} {agente.apellido}"
                        })
                    except Agente.DoesNotExist:
                        continue
            
            # Registrar en auditoría
            crear_auditoria_area(
                accion='CREAR',
                area_id=area.id_area,
                valor_nuevo={
                    'nombre': area.nombre,
                    'descripcion': area.descripcion,
                    'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                    'nombre_area_padre': area.id_area_padre.nombre if area.id_area_padre else None,
                    'jefe_area': area.jefe_area.id_agente if area.jefe_area else None,
                    'nombre_jefe': f"{area.jefe_area.nombre} {area.jefe_area.apellido}" if area.jefe_area else None,
                    'nivel': area.nivel,
                    'agentes_asignados': agentes_asignados_exitosos,
                    'total_agentes': len(agentes_asignados_exitosos)
                },
                usuario_logueado_id=1  # TODO: obtener del usuario autenticado
            )
            
            # Sincronizar organigrama automáticamente
            resultado_sincronizacion = sincronizar_organigrama_areas(usuario_logueado_id=1)
            print(f"Sincronización organigrama: {resultado_sincronizacion}")
            
            return Response({
                'success': True,
                'message': 'Área creada correctamente',
                'data': {
                    'id_area': area.id_area,
                    'nombre': area.nombre,
                    'descripcion': area.descripcion,
                    'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                    'nombre_padre': area.id_area_padre.nombre if area.id_area_padre else None,
                    'jefe_area': {
                        'id_agente': area.jefe_area.id_agente,
                        'nombre_completo': f"{area.jefe_area.nombre} {area.jefe_area.apellido}"
                    } if area.jefe_area else None,
                    'nivel': area.nivel,
                    'activo': area.activo,
                    'nombre_completo': area.nombre_completo,
                    'agentes_asignados': agentes_asignados_exitosos,
                    'total_agentes': len(agentes_asignados_exitosos)
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear área: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def update_area(request, area_id):
    """
    Actualizar área existente con soporte para jerarquía, descripción y jefe.
    """
    try:
        with transaction.atomic():
            area = get_object_or_404(Area, id_area=area_id)
            
            # Capturar valores previos para auditoría
            valor_previo = {
                'nombre': area.nombre,
                'descripcion': area.descripcion,
                'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                'nombre_area_padre': area.id_area_padre.nombre if area.id_area_padre else None,
                'jefe_area': area.jefe_area.id_agente if area.jefe_area else None,
                'nombre_jefe': f"{area.jefe_area.nombre} {area.jefe_area.apellido}" if area.jefe_area else None,
                'nivel': area.nivel,
                'activo': area.activo
            }
            
            # Extraer datos del request
            nombre = request.data.get('nombre', area.nombre).strip()
            descripcion = request.data.get('descripcion', area.descripcion)
            id_area_padre = request.data.get('id_area_padre')
            jefe_area_id = request.data.get('jefe_area')
            agentes_asignados = request.data.get('agentes_asignados', [])
            activo = request.data.get('activo', area.activo)
            
            # Validaciones
            if not nombre:
                return Response({
                    'success': False,
                    'message': 'El nombre del área es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Evitar que el área sea su propio padre
            if id_area_padre and int(id_area_padre) == area.id_area:
                return Response({
                    'success': False,
                    'message': 'Un área no puede ser su propio padre'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar área padre si se especifica
            area_padre = None
            nivel = 1  # Nivel por defecto para áreas raíz
            if id_area_padre:
                try:
                    area_padre = Area.objects.get(id_area=id_area_padre, activo=True)
                    nivel = area_padre.nivel + 1
                    
                    # Verificar que no se cree un ciclo jerárquico
                    def verificar_ciclo(area_objetivo, area_candidata_padre):
                        if not area_candidata_padre:
                            return False
                        if area_candidata_padre.id_area == area_objetivo.id_area:
                            return True
                        return verificar_ciclo(area_objetivo, area_candidata_padre.id_area_padre)
                    
                    if verificar_ciclo(area, area_padre):
                        return Response({
                            'success': False,
                            'message': 'No se puede crear un ciclo jerárquico'
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                except Area.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'El área padre especificada no existe'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar jefe del área si se especifica
            jefe_area = None
            if jefe_area_id:
                try:
                    jefe_area = Agente.objects.get(id_agente=jefe_area_id, activo=True)
                except Agente.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'El jefe especificado no existe'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar unicidad del nombre en el mismo nivel (excluyendo el área actual)
            if Area.objects.filter(
                nombre__iexact=nombre,
                id_area_padre=area_padre,
                activo=True
            ).exclude(id_area=area.id_area).exists():
                return Response({
                    'success': False,
                    'message': 'Ya existe un área con ese nombre en el mismo nivel jerárquico'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar área
            area.nombre = nombre
            area.descripcion = descripcion.strip() if descripcion else None
            area.id_area_padre = area_padre
            area.jefe_area = jefe_area
            area.nivel = nivel
            area.activo = activo
            area.save()
            
            # Actualizar nivel de áreas descendientes si cambió la jerarquía
            def actualizar_niveles_descendientes(area_base):
                hijos = Area.objects.filter(id_area_padre=area_base.id_area, activo=True)
                for hijo in hijos:
                    hijo.nivel = area_base.nivel + 1
                    hijo.save()
                    actualizar_niveles_descendientes(hijo)
            
            actualizar_niveles_descendientes(area)
            
            # Gestionar asignaciones de agentes
            agentes_asignados_exitosos = []
            if agentes_asignados:
                # Primero, desasignar todos los agentes actuales del área
                Agente.objects.filter(id_area=area, activo=True).update(id_area=None)
                
                # Luego, asignar los nuevos agentes
                for agente_id in agentes_asignados:
                    try:
                        agente = Agente.objects.get(id_agente=agente_id, activo=True)
                        agente.id_area = area
                        agente.save()
                        agentes_asignados_exitosos.append({
                            'id_agente': agente.id_agente,
                            'nombre_completo': f"{agente.nombre} {agente.apellido}"
                        })
                    except Agente.DoesNotExist:
                        continue
            
            # Preparar valor nuevo para auditoría
            valor_nuevo = {
                'nombre': area.nombre,
                'descripcion': area.descripcion,
                'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                'nombre_area_padre': area.id_area_padre.nombre if area.id_area_padre else None,
                'jefe_area': area.jefe_area.id_agente if area.jefe_area else None,
                'nombre_jefe': f"{area.jefe_area.nombre} {area.jefe_area.apellido}" if area.jefe_area else None,
                'nivel': area.nivel,
                'activo': area.activo,
                'agentes_asignados': agentes_asignados_exitosos,
                'total_agentes': len(agentes_asignados_exitosos)
            }
            
            # Registrar en auditoría
            crear_auditoria_area(
                accion='MODIFICAR',
                area_id=area.id_area,
                valor_previo=valor_previo,
                valor_nuevo=valor_nuevo,
                usuario_logueado_id=1  # TODO: obtener del usuario autenticado
            )
            
            # Sincronizar organigrama automáticamente
            resultado_sincronizacion = sincronizar_organigrama_areas(usuario_logueado_id=1)
            print(f"Sincronización organigrama: {resultado_sincronizacion}")
            
            return Response({
                'success': True,
                'message': 'Área actualizada correctamente',
                'data': {
                    'id_area': area.id_area,
                    'nombre': area.nombre,
                    'descripcion': area.descripcion,
                    'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                    'nombre_padre': area.id_area_padre.nombre if area.id_area_padre else None,
                    'jefe_area': {
                        'id_agente': area.jefe_area.id_agente,
                        'nombre_completo': f"{area.jefe_area.nombre} {area.jefe_area.apellido}"
                    } if area.jefe_area else None,
                    'nivel': area.nivel,
                    'activo': area.activo,
                    'nombre_completo': area.nombre_completo,
                    'agentes_asignados': agentes_asignados_exitosos,
                    'total_agentes': len(agentes_asignados_exitosos)
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar área: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def delete_area(request, area_id):
    """
    Eliminar área (soft delete) y reasignar agentes a área por defecto.
    """
    try:
        with transaction.atomic():
            area = get_object_or_404(Area, id_area=area_id)
            
            # Capturar información para auditoría antes de eliminar
            valor_previo = {
                'nombre': area.nombre,
                'descripcion': area.descripcion,
                'id_area_padre': area.id_area_padre.id_area if area.id_area_padre else None,
                'nombre_area_padre': area.id_area_padre.nombre if area.id_area_padre else None,
                'jefe_area': area.jefe_area.id_agente if area.jefe_area else None,
                'nombre_jefe': f"{area.jefe_area.nombre} {area.jefe_area.apellido}" if area.jefe_area else None,
                'nivel': area.nivel,
                'activo': area.activo
            }
            
            # Verificar si hay áreas hijas
            areas_hijas = Area.objects.filter(id_area_padre=area, activo=True).count()
            if areas_hijas > 0:
                return Response({
                    'success': False,
                    'message': f'No se puede eliminar el área porque tiene {areas_hijas} sub-área(s) asignada(s). Elimine primero las sub-áreas.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si hay agentes asignados
            agentes_asignados = Agente.objects.filter(id_area=area, activo=True)
            agentes_info = []
            
            if agentes_asignados.exists():
                # Obtener información de agentes para auditoría
                for agente in agentes_asignados:
                    agentes_info.append({
                        'id_agente': agente.id_agente,
                        'nombre_completo': f"{agente.nombre} {agente.apellido}"
                    })
                
                # Buscar área por defecto (primera activa, excluyendo la que se va a eliminar)
                area_default = Area.objects.filter(activo=True).exclude(id_area=area.id_area).first()
                
                if area_default:
                    # Reasignar agentes al área por defecto
                    agentes_asignados.update(id_area=area_default)
                    message = f'Área eliminada. {len(agentes_info)} agente(s) reasignado(s) al área "{area_default.nombre}"'
                    area_reasignacion = area_default.nombre
                else:
                    # Si no hay área por defecto, desasignar agentes
                    agentes_asignados.update(id_area=None)
                    message = f'Área eliminada. {len(agentes_info)} agente(s) desasignado(s) de área'
                    area_reasignacion = None
            else:
                message = 'Área eliminada correctamente'
                area_reasignacion = None
            
            # Marcar área como inactiva
            area.activo = False
            area.save()
            
            # Registrar en auditoría
            valor_nuevo = {
                'activo': False,
                'agentes_reasignados': agentes_info,
                'area_reasignacion': area_reasignacion,
                'total_agentes_afectados': len(agentes_info)
            }
            
            crear_auditoria_area(
                accion='ELIMINAR',
                area_id=area.id_area,
                valor_previo=valor_previo,
                valor_nuevo=valor_nuevo,
                usuario_logueado_id=1  # TODO: obtener del usuario autenticado
            )
            
            # Sincronizar organigrama automáticamente
            resultado_sincronizacion = sincronizar_organigrama_areas(usuario_logueado_id=1)
            print(f"Sincronización organigrama: {resultado_sincronizacion}")
            
            return Response({
                'success': True,
                'message': message,
                'data': {
                    'agentes_reasignados': len(agentes_info),
                    'area_reasignacion': area_reasignacion
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al eliminar área: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def update_global_schedule(request):
    """
    Actualizar horarios de TODOS los agentes activos del sistema.
    Solo accesible por administradores.
    """
    try:
        # Verificar autenticación
        agente_id = request.session.get('user_id')
        if not agente_id:
            return Response({
                'success': False,
                'message': 'No hay sesión activa'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        agente = Agente.objects.get(id_agente=agente_id)
        rol = agente.agenterol_set.first()
        
        if not rol or rol.id_rol.nombre not in ['Administrador', 'Director']:
            return Response({
                'success': False,
                'message': 'No tiene permisos para establecer horario global'
            }, status=status.HTTP_403_FORBIDDEN)
        
        with transaction.atomic():
            horario_entrada = request.data.get('horario_entrada')
            horario_salida = request.data.get('horario_salida')
            
            if not horario_entrada or not horario_salida:
                return Response({
                    'success': False,
                    'message': 'Horario de entrada y salida son requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar horarios de TODOS los agentes activos
            agentes_actualizados = Agente.objects.filter(
                activo=True
            ).update(
                horario_entrada=horario_entrada,
                horario_salida=horario_salida
            )
            
            return Response({
                'success': True,
                'message': f'Horario global aplicado a {agentes_actualizados} agente(s) activo(s)',
                'data': {
                    'agentes_actualizados': agentes_actualizados,
                    'horario_entrada': horario_entrada,
                    'horario_salida': horario_salida
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al actualizar horario global: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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


def crear_auditoria(agente_id, accion, tabla, pk_afectada, valor_previo=None, valor_nuevo=None, usuario_logueado_id=None):
    """
    Crear registro de auditoría genérico.
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
            pk_afectada=pk_afectada,
            nombre_tabla=tabla,
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=usuario_logueado_id or agente_id
        )
    except Exception as e:
        print(f"Error al crear auditoría: {str(e)}")

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


def crear_auditoria_rol(accion, agente_id, rol_id, valor_previo=None, valor_nuevo=None, usuario_logueado_id=None):
    """
    Crear registro de auditoría para cambios de roles.
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
            nombre_tabla='agente_rol',
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=usuario_logueado_id  # FK al agente que hizo el cambio
        )
    except Exception as e:
        # No fallar si la auditoría falla, solo registrar
        print(f"Error al crear auditoría de rol: {str(e)}")


def crear_auditoria_area(accion, area_id, valor_previo=None, valor_nuevo=None, usuario_logueado_id=None):
    """
    Crear registro de auditoría para cambios en áreas.
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
            pk_afectada=area_id,
            nombre_tabla='area',
            creado_en=timezone.now(),
            valor_previo=valor_previo_json,
            valor_nuevo=valor_nuevo_json,
            accion=accion,
            id_agente_id=usuario_logueado_id  # FK al agente que hizo el cambio
        )
    except Exception as e:
        # No fallar si la auditoría falla, solo registrar
        print(f"Error al crear auditoría de área: {str(e)}")


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


def sincronizar_organigrama_areas(usuario_logueado_id=None):
    """
    Sincronizar automáticamente el organigrama con la estructura jerárquica de áreas.
    """
    try:
        # Obtener la estructura jerárquica actual de áreas
        areas_raiz = Area.objects.filter(id_area_padre__isnull=True, activo=True).order_by('nombre')
        
        def construir_nodo_organigrama(area):
            """Construir un nodo del organigrama basado en un área."""
            nodo = {
                'id': f'area_{area.id_area}',
                'nombre': area.nombre,
                'tipo': 'area',
                'id_area': area.id_area,
                'descripcion': area.descripcion or '',
                'nivel': area.nivel,
                'jefe': {
                    'id_agente': area.jefe_area.id_agente,
                    'nombre': f"{area.jefe_area.nombre} {area.jefe_area.apellido}",
                    'email': area.jefe_area.email
                } if area.jefe_area else None,
                'total_agentes': area.total_agentes,
                'children': []
            }
            
            # Agregar áreas hijas recursivamente
            areas_hijas = Area.objects.filter(id_area_padre=area, activo=True).order_by('nombre')
            for area_hija in areas_hijas:
                nodo['children'].append(construir_nodo_organigrama(area_hija))
            
            return nodo
        
        # Construir la estructura completa
        estructura_organigrama = []
        for area_raiz in areas_raiz:
            estructura_organigrama.append(construir_nodo_organigrama(area_raiz))
        
        # Obtener organigrama anterior para auditoría
        organigrama_anterior = Organigrama.objects.filter(activo=True).first()
        valor_previo = None
        
        if organigrama_anterior:
            valor_previo = {
                'id': organigrama_anterior.id_organigrama,
                'nombre': organigrama_anterior.nombre,
                'version': organigrama_anterior.version,
                'estructura': organigrama_anterior.estructura
            }
        
        # Desactivar organigramas anteriores
        Organigrama.objects.filter(activo=True).update(activo=False)
        
        # Crear nuevo organigrama sincronizado
        from django.utils import timezone
        nueva_version = f"v{timezone.now().strftime('%m%d-%H%M')}"
        
        organigrama_nuevo = Organigrama.objects.create(
            nombre='Organigrama Sincronizado con Áreas',
            estructura=estructura_organigrama,
            version=nueva_version,
            creado_por='Sistema - Sincronización Automática',
            activo=True
        )
        
        # Registrar auditoría de sincronización
        valor_nuevo = {
            'id': organigrama_nuevo.id_organigrama,
            'nombre': organigrama_nuevo.nombre,
            'version': organigrama_nuevo.version,
            'estructura': organigrama_nuevo.estructura,
            'motivo': 'Sincronización automática con cambios en áreas'
        }
        
        crear_auditoria_organigrama(
            accion='SINCRONIZACION_AUTOMATICA',
            organigrama_id=organigrama_nuevo.id_organigrama,
            valor_previo=valor_previo,
            valor_nuevo=valor_nuevo,
            agente_id=usuario_logueado_id
        )
        
        return {
            'success': True,
            'organigrama_id': organigrama_nuevo.id_organigrama,
            'version': nueva_version,
            'nodos_totales': len(estructura_organigrama)
        }
        
    except Exception as e:
        print(f"Error al sincronizar organigrama: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# ENDPOINTS PARA GESTIÓN DE ORGANIGRAMA
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
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


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticatedGIGA])  # RBAC actualizado
def sincronizar_organigrama_manual(request):
    """
    Sincronizar manualmente el organigrama con la estructura de áreas.
    """
    try:
        resultado = sincronizar_organigrama_areas(usuario_logueado_id=1)  # TODO: obtener del usuario autenticado
        
        if resultado['success']:
            return Response({
                'success': True,
                'message': 'Organigrama sincronizado correctamente',
                'data': resultado
            })
        else:
            return Response({
                'success': False,
                'message': f'Error en la sincronización: {resultado.get("error", "Error desconocido")}',
                'data': resultado
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al sincronizar organigrama: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
