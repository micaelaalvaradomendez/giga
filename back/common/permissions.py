"""
Sistema de Permisos RBAC para GIGA
Basado en análisis completo de funcionalidades.md, analisisRBAC.md y planroles.md

Jerarquía de Roles:
    Administrador (Máximo acceso)
        ↓
    Director (División completa)
        ↓
    Jefatura (Área + sub-áreas)
        ↓
    Agente Avanzado (Área extendida)
        ↓
    Agente (Solo datos propios)
"""

from rest_framework import permissions
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# FUNCIONES HELPER PARA RBAC
# ============================================================================

def obtener_agente_sesion(request):
    """
    Obtiene el agente asociado a la sesión actual
    
    Returns:
        Agente: Instancia del agente autenticado
        None: Si no hay sesión válida
    """
    agente_id = request.session.get('user_id')
    if not agente_id:
        return None
    
    from personas.models import Agente
    try:
        return Agente.objects.get(id_agente=agente_id, activo=True)
    except Agente.DoesNotExist:
        return None


def obtener_rol_agente(agente):
    """
    Obtiene el rol del agente (primer rol asignado)
    
    Args:
        agente: Instancia de Agente
        
    Returns:
        str: Nombre del rol en minúsculas ('administrador', 'director', etc.)
        None: Si no tiene rol asignado
    """
    if not agente:
        return None
    
    rol_asignacion = agente.agenterol_set.first()
    if not rol_asignacion or not rol_asignacion.id_rol:
        return None
    
    return rol_asignacion.id_rol.nombre.lower()


def obtener_area_y_subareas(area):
    """
    Obtiene un área y todas sus sub-áreas recursivamente
    
    Args:
        area: Instancia de Area
        
    Returns:
        list: Lista de áreas (incluyendo la original y todas sus descendientes)
    """
    if not area:
        return []
    
    from personas.models import Area
    areas = [area]
    
    # Buscar sub-áreas (donde id_area_padre = area)
    subareas = Area.objects.filter(id_area_padre=area)
    for subarea in subareas:
        areas.extend(obtener_area_y_subareas(subarea))
    
    return areas


def obtener_areas_jerarquia(agente):
    """
    Obtiene las áreas que un agente puede ver/gestionar según su rol
    
    LÓGICA CORRECTA:
    - Administrador: Todas las áreas
    - Director: Su área + sub-áreas (división completa)
    - Jefatura: Solo su área (SIN sub-áreas)
    - Agente Avanzado: Solo su área
    - Agente: Solo su área (pero solo ve su propia info)
    
    Args:
        agente: Instancia de Agente
        
    Returns:
        list: Lista de áreas accesibles según rol
    """
    if not agente or not agente.id_area:
        return []
    
    rol = obtener_rol_agente(agente)
    
    if rol == 'administrador':
        # Admin ve todas las áreas
        from personas.models import Area
        return list(Area.objects.all())
    
    elif rol == 'director':
        # Director ve su área + sub-áreas (división completa)
        return obtener_area_y_subareas(agente.id_area)
    
    elif rol in ['jefatura', 'agente_avanzado', 'agente']:
        # Jefatura, Agente Avanzado y Agente: solo su área (sin sub-áreas)
        return [agente.id_area]
    
    else:
        # Por defecto: solo su área
        return [agente.id_area]


# ============================================================================
# PERMISOS BÁSICOS
# ============================================================================

class IsAuthenticatedGIGA(permissions.BasePermission):
    """
    Usuario autenticado en GIGA (sesión válida)
    
    Reemplaza AllowAny en todos los endpoints excepto login/logout.
    Verifica que existe una sesión válida con un agente activo.
    """
    
    def has_permission(self, request, view):
        agente = obtener_agente_sesion(request)
        
        if not agente:
            logger.warning(f"Acceso denegado: No hay sesión válida")
            return False
        
        return True


class IsAdministrador(permissions.BasePermission):
    """
    Solo Administrador puede acceder
    
    Usado para:
    - ABM de agentes
    - Parámetros globales del sistema
    - Gestión de áreas y agrupaciones
    - Tipos de licencia
    - Organigrama (edición)
    """
    
    def has_permission(self, request, view):
        agente = obtener_agente_sesion(request)
        if not agente:
            return False
        
        rol = obtener_rol_agente(agente)
        
        if rol != 'administrador':
            logger.warning(
                f"Acceso denegado: Agente {agente.id_agente} ({rol}) "
                f"intentó acción de administrador"
            )
            return False
        
        return True


class IsDirectorOrAdmin(permissions.BasePermission):
    """
    Director o Admin pueden acceder
    
    Usado para:
    - Aprobación de cronogramas de jefatura
    - Reportes de división
    - Gestión de compensaciones (aprobación)
    """
    
    def has_permission(self, request, view):
        agente = obtener_agente_sesion(request)
        if not agente:
            return False
        
        rol = obtener_rol_agente(agente)
        return rol in ['administrador', 'director']


class IsJefaturaOrAbove(permissions.BasePermission):
    """
    Jefatura, Director o Admin pueden acceder
    
    Usado para:
    - Gestión de guardias (creación, planificación)
    - Corrección de asistencias
    - Aprobación de licencias de agentes
    - Reportes de área
    """
    
    def has_permission(self, request, view):
        agente = obtener_agente_sesion(request)
        if not agente:
            return False
        
        rol = obtener_rol_agente(agente)
        return rol in ['administrador', 'director', 'jefatura']


# ============================================================================
# PERMISOS CON VALIDACIÓN DE JERARQUÍA
# ============================================================================

class CanApprove(permissions.BasePermission):
    """
    Validación jerárquica para aprobaciones (licencias, compensaciones)
    
    Reglas:
    - Admin: aprueba todo
    - Director: aprueba solicitudes de jefaturas de su división
    - Jefatura: aprueba solicitudes de agentes/agentes avanzados de su área
    """
    
    def has_permission(self, request, view):
        """Verifica que el usuario tenga un rol con capacidad de aprobar"""
        agente = obtener_agente_sesion(request)
        if not agente:
            return False
        
        rol = obtener_rol_agente(agente)
        return rol in ['administrador', 'director', 'jefatura']
    
    def has_object_permission(self, request, view, obj):
        """Valida que pueda aprobar este objeto específico según jerarquía"""
        agente_aprobador = obtener_agente_sesion(request)
        rol_aprobador = obtener_rol_agente(agente_aprobador)
        
        # Admin aprueba todo
        if rol_aprobador == 'administrador':
            return True
        
        # Obtener agente solicitante del objeto
        agente_solicitante = getattr(obj, 'id_agente', None) or getattr(obj, 'solicitada_por', None)
        if not agente_solicitante:
            logger.error(f"No se pudo obtener agente solicitante del objeto {obj}")
            return False
        
        rol_solicitante = obtener_rol_agente(agente_solicitante)
        
        # Director aprueba jefaturas de su división
        if rol_aprobador == 'director':
            if rol_solicitante == 'jefatura':
                # Verificar que sea de su división
                areas_director = obtener_areas_jerarquia(agente_aprobador)
                area_ids = [a.id_area for a in areas_director]
                
                if agente_solicitante.id_area.id_area in area_ids:
                    return True
                
                logger.warning(
                    f"Director {agente_aprobador.id_agente} intentó aprobar "
                    f"de jefatura {agente_solicitante.id_agente} fuera de su división"
                )
            return False
        
        # Jefatura aprueba agentes de su área
        if rol_aprobador == 'jefatura':
            if rol_solicitante in ['agente', 'agente_avanzado']:
                # Verificar que sea de su área o sub-áreas
                areas_jefatura = obtener_areas_jerarquia(agente_aprobador)
                area_ids = [a.id_area for a in areas_jefatura]
                
                if agente_solicitante.id_area.id_area in area_ids:
                    return True
                
                logger.warning(
                    f"Jefatura {agente_aprobador.id_agente} intentó aprobar "
                    f"de agente {agente_solicitante.id_agente} fuera de su área"
                )
            return False
        
        return False


class CanCreateCronograma(permissions.BasePermission):
    """
    Validación para creación de cronogramas
    
    Reglas:
    - Admin: puede crear para cualquier área
    - Director: puede crear para áreas bajo su dirección
    - Jefatura: puede crear solo para su área
    """
    
    def has_permission(self, request, view):
        agente = obtener_agente_sesion(request)
        if not agente:
            return False
        
        rol = obtener_rol_agente(agente)
        return rol in ['administrador', 'director', 'jefatura']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Dueño del recurso o Admin
    
    Usado para:
    - Ver/editar perfil propio
    - Ver asistencias propias
    - Ver guardias propias
    - Ver licencias propias
    """
    
    def has_permission(self, request, view):
        return obtener_agente_sesion(request) is not None
    
    def has_object_permission(self, request, view, obj):
        agente = obtener_agente_sesion(request)
        if not agente:
            return False
        
        rol = obtener_rol_agente(agente)
        
        # Admin tiene acceso a todo
        if rol == 'administrador':
            return True
        
        # Verificar si es dueño del recurso
        if hasattr(obj, 'id_agente'):
            return obj.id_agente.id_agente == agente.id_agente
        
        return False


# ============================================================================
# MIXINS PARA FILTRADO AUTOMÁTICO EN VIEWSETS
# ============================================================================

class RBACFilterMixin:
    """
    Mixin para filtrar automáticamente querysets según rol del usuario
    
    Usar en ViewSets para aplicar filtros RBAC de forma consistente.
    Sobrescribe get_queryset() para filtrar por rol.
    """
    
    def get_queryset_filtered_by_role(self, base_queryset, agente_field='id_agente'):
        """
        Filtra queryset según rol del usuario autenticado
        
        Args:
            base_queryset: QuerySet base sin filtrar
            agente_field: Nombre del campo que referencia al agente
            
        Returns:
            QuerySet filtrado según rol
        """
        agente = obtener_agente_sesion(self.request)
        if not agente:
            return base_queryset.none()
        
        rol = obtener_rol_agente(agente)
        
        # Admin ve todo
        if rol == 'administrador':
            return base_queryset
        
        # Obtener áreas permitidas según rol
        areas_permitidas = obtener_areas_jerarquia(agente)
        area_ids = [a.id_area for a in areas_permitidas]
        
        # Filtrar según tipo de acceso
        if rol == 'agente':
            # Solo sus propios registros
            filter_kwargs = {agente_field: agente}
            return base_queryset.filter(**filter_kwargs)
        
        # Director, Jefatura, Agente Avanzado: filtrar por áreas
        # Intentar filtrar por área del agente
        try:
            filter_kwargs = {f'{agente_field}__id_area__id_area__in': area_ids}
            return base_queryset.filter(**filter_kwargs)
        except:
            # Si el modelo no tiene relación con agente, intentar directamente por área
            try:
                filter_kwargs = {'id_area__id_area__in': area_ids}
                return base_queryset.filter(**filter_kwargs)
            except:
                # Si tampoco tiene id_area, retornar el queryset base
                logger.warning(
                    f"No se pudo aplicar filtro RBAC a {base_queryset.model.__name__}"
                )
                return base_queryset
