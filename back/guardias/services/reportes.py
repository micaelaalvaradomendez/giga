"""
Servicio unificado de reportes de guardias.

Responsabilidades:
- Normalizar filtros de entrada.
- Validar permisos segun rol (agente, jefatura, director, admin).
- Armar datos para vista previa y export (individual y general).
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.db.models import F, Q
from guardias.models import Guardia, Feriado
from personas.models import Agente, Area
from asistencia.models import Asistencia, Licencia, TipoLicencia
from common.permissions import obtener_area_y_subareas, obtener_rol_agente

DATE_FMT = "%Y-%m-%d"
ESTADO_LICENCIA = "aprobada"


class ReporteError(Exception):
    """Errores de negocio para reportes."""


def obtener_datos_reporte(filtros: Dict, tipo_reporte: str, user_ctx: Dict):
    """
    Entrada unica para reportes de guardias (individual y general).

    Args:
        filtros: diccionario con posibles claves agente, area, fecha_desde, fecha_hasta, tipo_guardia
        tipo_reporte: 'individual' o 'general'
        user_ctx: {'agente': Agente, 'rol': str}
    """
    filtros_norm = _normalizar_filtros(filtros)
    agente_ctx = user_ctx.get("agente")
    rol_ctx = (user_ctx.get("rol") or obtener_rol_agente(agente_ctx) or "").lower()

    if not agente_ctx or not rol_ctx:
        raise ReporteError("Sesion invalida")

    permisos = _aplicar_reglas_por_rol(filtros_norm, rol_ctx, agente_ctx)
    _validar_rango_fechas(filtros_norm)

    if tipo_reporte == "individual":
        if not filtros_norm.get("agente"):
            raise ReporteError("Debe indicar un agente para el reporte individual")
        if len(filtros_norm["agente"]) != 1:
            raise ReporteError("Reporte individual solo admite un agente")
        return _armar_reporte_individual(filtros_norm, permisos)

    if tipo_reporte == "general":
        return _armar_reporte_general(filtros_norm, permisos)

    raise ReporteError("Tipo de reporte invalido")


# ---------------------------------------------------------------------------
# Normalizacion y validaciones
# ---------------------------------------------------------------------------


from datetime import datetime

def _to_bool(v):
    # acepta True/False, "true"/"false", 1/0, "1"/"0"
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "t", "yes", "y", "si", "sí", "on")
    return False

def _normalizar_filtros(filtros: Dict) -> Dict:
    def clean(v):
        if v in ("", "null", "None", None):
            return None
        return v

    out = {}

    # listas
    out["agente"] = filtros.get("agente")
    if out["agente"] is not None:
        out["agente"] = out["agente"] if isinstance(out["agente"], list) else [out["agente"]]

    out["area"] = filtros.get("area")
    if out["area"] is not None:
        out["area"] = out["area"] if isinstance(out["area"], list) else [out["area"]]

    out["tipo_guardia"] = clean(filtros.get("tipo_guardia"))

    # fechas
    fd = clean(filtros.get("fecha_desde"))
    fh = clean(filtros.get("fecha_hasta"))

    out["fecha_desde"] = datetime.strptime(fd, "%Y-%m-%d").date() if fd else None
    out["fecha_hasta"] = datetime.strptime(fh, "%Y-%m-%d").date() if fh else None

    # flags feriados y licencias
    out["incluir_feriados"] = _to_bool(filtros.get("incluir_feriados"))
    out["incluir_licencias"] = _to_bool(filtros.get("incluir_licencias"))

    return out



def _to_int_or_none(valor) -> Optional[int]:
    try:
        return int(valor) if valor not in [None, ""] else None
    except (TypeError, ValueError):
        return None


def _parse_fecha(valor, requerido=False):
    if not valor:
        if requerido:
            raise ReporteError("Las fechas son obligatorias (YYYY-MM-DD)")
        return None
    try:
        return datetime.strptime(valor, DATE_FMT).date()
    except ValueError:
        raise ReporteError("Formato de fecha invalido. Use YYYY-MM-DD")


def _validar_rango_fechas(filtros: Dict):
    fd = filtros.get("fecha_desde")
    fh = filtros.get("fecha_hasta")

    if fd and fh:
        if isinstance(fd, str):
            fd = datetime.strptime(fd, "%Y-%m-%d").date()
            filtros["fecha_desde"] = fd
        if isinstance(fh, str):
            fh = datetime.strptime(fh, "%Y-%m-%d").date()
            filtros["fecha_hasta"] = fh

        if fd > fh:
            raise ReporteError("Fecha desde no puede ser mayor que fecha hasta")


def _aplicar_reglas_por_rol(filtros: Dict, rol: str, agente_ctx: Agente) -> Dict:
    """
    Ajusta filtros segun rol y devuelve informacion de alcance (areas/agents permitidos).
    Admite listas en area/agente.
    """
    area_scope: List[int] = []

    if rol == "agente":
        filtros["agente"] = [agente_ctx.id_agente]
        if filtros.get("area"):
            raise ReporteError("El rol agente no puede filtrar por area")
        area_scope = [agente_ctx.id_area] if agente_ctx.id_area else []

    elif rol == "jefatura":
        if not agente_ctx.id_area:
            raise ReporteError("La jefatura no tiene un area asignada")
        area_scope = [agente_ctx.id_area]
        filtros["area"] = [agente_ctx.id_area]
        if filtros.get("agente"):
            for agente_id in filtros["agente"]:
                agente_filtro = _obtener_agente(agente_id)
                if agente_filtro.id_area != agente_ctx.id_area:
                    raise ReporteError("El agente indicado no pertenece a su area")

    elif rol == "director":
        if not agente_ctx.id_area:
            raise ReporteError("El director no tiene un area asignada")
        areas_permitidas = obtener_area_y_subareas(agente_ctx.id_area)
        area_ids_permitidas = [a.id_area for a in areas_permitidas]

        if filtros.get("area"):
            # validar que todas las areas esten en su jerarquia
            for area_id in filtros["area"]:
                if area_id not in area_ids_permitidas:
                    raise ReporteError("Alguna de las áreas indicadas no pertenece a su jerarquía")
            area_scope = []
            for area_id in filtros["area"]:
                area_scope.extend([a.id_area for a in obtener_area_y_subareas(_obtener_area(area_id))])
        else:
            area_scope = area_ids_permitidas
            # Inferir area si viene agente
            if filtros.get("agente"):
                for agente_id in filtros["agente"]:
                    agente_filtro = _obtener_agente(agente_id)
                    if agente_filtro.id_area not in area_ids_permitidas:
                        raise ReporteError("Algún agente indicado no pertenece a su jerarquía")
                # opcional: no forzar area si no viene; se usa scope

    elif rol == "administrador":
        area_scope = []  # sin limite
        if filtros.get("area"):
            area_scope = []
            for area_id in filtros["area"]:
                _ = _obtener_area(area_id)
                area_scope.extend([a.id_area for a in obtener_area_y_subareas(_obtener_area(area_id))])
        if filtros.get("agente"):
            for agente_id in filtros["agente"]:
                _obtener_agente(agente_id)

    else:
        raise ReporteError("Rol sin permisos para reportes")

    return {
        "rol": rol,
        "area_scope": list(set(area_scope)) if area_scope is not None else None,
        "agente_ctx": agente_ctx,
    }


def _obtener_agente(agente_id: int) -> Agente:
    try:
        return Agente.objects.get(id_agente=agente_id, activo=True)
    except Agente.DoesNotExist:
        raise ReporteError("Agente no encontrado")


def _obtener_area(area_id: int) -> Area:
    try:
        return Area.objects.get(id_area=area_id, activo=True)
    except Area.DoesNotExist:
        raise ReporteError("Area no encontrada")


# ---------------------------------------------------------------------------
# Construccion de datos
# ---------------------------------------------------------------------------


def _armar_reporte_individual(filtros: Dict, permisos: Dict) -> Dict:
    agente_id = filtros["agente"][0]
    agente = _obtener_agente(agente_id)
    if permisos.get("area_scope") is not None and agente.id_area not in permisos["area_scope"]:
        raise ReporteError("El agente indicado esta fuera de su alcance")

    guardias_qs = _query_guardias(filtros, permisos)
    guardias_qs = guardias_qs.filter(id_agente=agente.id_agente)

    dias_data = []
    for guardia in guardias_qs.order_by("fecha", "hora_inicio"):
        asistencia = _buscar_asistencia(guardia.id_agente, guardia.fecha)
        dias_data.append({
            "fecha": guardia.fecha.strftime(DATE_FMT),
            "dia_semana": guardia.fecha.strftime("%A"),
            "horario_guardia_inicio": guardia.hora_inicio.strftime("%H:%M") if guardia.hora_inicio else "",
            "horario_guardia_fin": guardia.hora_fin.strftime("%H:%M") if guardia.hora_fin else "",
            "horas_planificadas": guardia.horas_planificadas or 0,
            "horas_efectivas": guardia.horas_efectivas or guardia.horas_planificadas or 0,
            "motivo_guardia": guardia.tipo or "",
            "novedad": guardia.observaciones or "",
            "estado_asistencia": asistencia.estado if asistencia else "",
        })

    total_horas = sum(d.get("horas_efectivas") or 0 for d in dias_data)

    return {
        "tipo": "individual",
        "agente": {
            "id": agente.id_agente,
            "nombre": f"{agente.nombre} {agente.apellido}",
            "legajo": agente.legajo,
            "area": agente.id_area,
        },
        "filtros": _filtros_serializables(filtros),
        "dias": dias_data,
        "totales": {"horas_efectivas": total_horas},
    }


def _armar_reporte_general(filtros: Dict, permisos: Dict) -> Dict:
    area_scope = permisos.get("area_scope", [])

    agentes_qs = Agente.objects.filter(activo=True)

    # Filtro por agente puntual
    if filtros.get("agente"):
        agentes_qs = agentes_qs.filter(id_agente__in=filtros["agente"])

    # Filtro por área
    area_filtro = filtros.get("area")

    if area_filtro:
        # Normalizamos a lista
        if not isinstance(area_filtro, (list, tuple, set)):
            area_filtro = [area_filtro]

        agentes_qs = agentes_qs.filter(
            id_area_id__in=set(area_scope) & set(area_filtro)
        )
    else:
        # No eligió área → solo lo que puede ver
        agentes_qs = agentes_qs.filter(id_area_id__in=area_scope)

    agentes_qs = agentes_qs.select_related("id_area").order_by("apellido", "nombre")

    fecha_desde = filtros["fecha_desde"]
    fecha_hasta = filtros["fecha_hasta"]

    incluir_licencias = filtros.get("incluir_licencias", False)
    incluir_feriados = filtros.get("incluir_feriados", False)

    # =========================
    # LICENCIAS
    # =========================
    licencias_map = {}  # { agente_id: { 'YYYY-MM-DD': 'VAC' } }

    if incluir_licencias:
        licencias_qs = (
            Licencia.objects
            .filter(
                id_agente_id__in=agentes_qs.values_list("id_agente", flat=True),
                estado=ESTADO_LICENCIA,  # ej: "aprobada"
                fecha_desde__lte=fecha_hasta,
                fecha_hasta__gte=fecha_desde,
            )
            .select_related("id_tipo_licencia")
        )

        for lic in licencias_qs:
            codigo = lic.id_tipo_licencia.codigo or "LIC"
            d = lic.fecha_desde
            while d <= lic.fecha_hasta:
                if fecha_desde <= d <= fecha_hasta:
                    licencias_map.setdefault(lic.id_agente_id, {})[d.strftime(DATE_FMT)] = codigo
                d += timedelta(days=1)

    # =========================
    # FERIADOS
    # =========================
    feriados_set = set()  # { 'YYYY-MM-DD' }

    if incluir_feriados:
        feriados_qs = Feriado.feriados_en_rango(fecha_desde, fecha_hasta)
        for fer in feriados_qs:
            for f in fer.get_fechas_incluidas():
                if fecha_desde <= f <= fecha_hasta:
                    feriados_set.add(f.strftime(DATE_FMT))

    # =========================
    # GUARDIAS
    # =========================
    guardias_qs = list(
        _query_guardias(filtros, permisos).filter(
            id_agente_id__in=agentes_qs.values_list("id_agente", flat=True)
        )
    )

    # ✅ días = guardias + licencias + feriados
    dias_set = {g.fecha.strftime(DATE_FMT) for g in guardias_qs}
    if incluir_licencias:
        for per_agente in licencias_map.values():
            dias_set.update(per_agente.keys())
    if incluir_feriados:
        dias_set.update(feriados_set)

    dias_fechas = sorted(dias_set)
    dias_columnas = [
        {"fecha": f, "dia_semana": datetime.strptime(f, DATE_FMT).strftime("%A")}
        for f in dias_fechas
    ]

    agentes_data = []
    for agente in agentes_qs:
        dias_valores = []
        total_horas_agente = 0

        guardias_agente = [g for g in guardias_qs if g.id_agente_id == agente.id_agente]
        guardias_por_fecha = {g.fecha.strftime(DATE_FMT): g for g in guardias_agente}

        for fecha_str in dias_fechas:
            # 1) LICENCIA
            lic_code = licencias_map.get(agente.id_agente, {}).get(fecha_str)
            if lic_code:
                valor = lic_code

            # 2) FERIADO
            elif fecha_str in feriados_set:
                valor = "FER"

            # 3) GUARDIA
            else:
                guardia = guardias_por_fecha.get(fecha_str)
                if guardia:
                    valor = guardia.horas_efectivas
                    if valor is None:
                        valor = guardia.horas_planificadas or 0
                    total_horas_agente += (valor or 0)
                else:
                    valor = 0

            dias_valores.append({"fecha": fecha_str, "valor": valor})

        agentes_data.append({
            "id": agente.id_agente,
            "nombre_completo": f"{agente.nombre} {agente.apellido}",
            "legajo": agente.legajo,
            "cuil": getattr(agente, "cuil", "") or "",
            "area": agente.id_area.nombre if agente.id_area else "",
            "dias": dias_valores,
            "total_horas": total_horas_agente,
        })

    total_horas = sum(a["total_horas"] for a in agentes_data)

    return {
        "tipo": filtros.get("tipo_guardia") or "regular",
        "filtros": _filtros_serializables(filtros),
        "dias_columnas": dias_columnas,
        "agentes": agentes_data,
        "totales": {"horas": total_horas, "agentes": len(agentes_data)},
    }


def _query_guardias(filtros: Dict, permisos: Dict):
    fecha_desde = filtros["fecha_desde"]
    fecha_hasta = filtros["fecha_hasta"]

    base_q = Q(
        fecha__gte=fecha_desde,
        fecha__lte=fecha_hasta,
        activa=True,
    )

    cruza_medianoche_q = Q(
        fecha=fecha_desde - timedelta(days=1),
        hora_inicio__gt=F("hora_fin"),
        activa=True,
    )

    qs = Guardia.objects.filter(base_q | cruza_medianoche_q).select_related(
        "id_agente", "id_cronograma"
    )

    if filtros.get("tipo_guardia"):
        qs = qs.filter(tipo=filtros["tipo_guardia"])

    if filtros.get("agente"):
        qs = qs.filter(id_agente_id__in=filtros["agente"])

    if permisos.get("area_scope") is not None:
        qs = qs.filter(id_agente__id_area_id__in=permisos["area_scope"])
    elif filtros.get("area"):
        qs = qs.filter(id_agente__id_area_id__in=filtros["area"])

    return qs



def _generar_rango_dias(desde, hasta):
    dias = []
    fecha = desde
    while fecha <= hasta:
        dias.append({
            "fecha": fecha.strftime(DATE_FMT),
            "dia_semana": fecha.strftime("%A"),
        })
        fecha += timedelta(days=1)
    return dias


def _buscar_asistencia(agente_id: int, fecha):
    try:
        return Asistencia.objects.get(id_agente=agente_id, fecha=fecha)
    except Asistencia.DoesNotExist:
        return None


def _filtros_serializables(filtros: Dict):
    fecha_desde = filtros.get("fecha_desde")
    fecha_hasta = filtros.get("fecha_hasta")
    return {
        "agente": filtros.get("agente"),
        "area": filtros.get("area"),
        "fecha_desde": fecha_desde.strftime(DATE_FMT) if fecha_desde else None,
        "fecha_hasta": fecha_hasta.strftime(DATE_FMT) if fecha_hasta else None,
        "tipo_guardia": filtros.get("tipo_guardia"),
    }
