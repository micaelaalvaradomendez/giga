"""
Servicios de reportes para la app guardias.

Expone la API principal: obtener_datos_reporte y ReporteError.
"""

from .reportes import obtener_datos_reporte, ReporteError

__all__ = ["obtener_datos_reporte", "ReporteError"]
