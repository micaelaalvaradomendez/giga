# Reportes de Guardias - API (Backend)

## Autenticacion y headers
- Usa la sesion (cookie `sessionid`) y CSRF (`csrftoken`).
- Endpoints aceptan POST (JSON) y GET; siempre enviar `Content-Type: application/json` + cookies de sesion/CSRF.

## Estado actual (08/12/2025)
- Servicio `obtener_datos_reporte` operativo (individual/general) con saneo por rol.
- Vistas: `/api/guardias/guardias/reporte_individual/` y `/api/guardias/guardias/reporte_general/` ya aceptan POST (se corrigio `data_in` en general).
- Exportes: CSV/PDF/Excel usan los filtros del request y validan permisos; generan con datos reales.
- Limpieza de caracteres corruptos en `views.py`; contenedores levantan health-check OK.

## Endpoints de vista previa
### Individual
- URL: `/api/guardias/guardias/reporte_individual/`
- Body ejemplo:
```json
{
  "fecha_desde": "2025-11-01",
  "fecha_hasta": "2025-11-30",
  "agente": 1
}
```

### General (por area/jerarquia)
- URL: `/api/guardias/guardias/reporte_general/`
- Body ejemplo:
```json
{
  "fecha_desde": "2025-11-01",
  "fecha_hasta": "2025-11-30",
  "area": 5
}
```
- Opcional: "agente": <id> para filtrar a un agente dentro del alcance.

## Endpoints de exportacion (mismos filtros)
- CSV: `/api/guardias/guardias/exportar_csv/`
- PDF: `/api/guardias/guardias/exportar_pdf/`
- Excel: `/api/guardias/guardias/exportar_excel/`
- Body ejemplo (general):
```json
{
  "tipo_reporte": "general",
  "fecha_desde": "2025-11-01",
  "fecha_hasta": "2025-11-30",
  "area": 5
}
```
- Para individual: "tipo_reporte": "individual" y pasar "agente".

## Reglas de permisos (server-side)
- Agente: fuerza su propio `agente` (id), ignora `area`.
- Jefatura: fija `area` = la suya; `agente` solo de su area.
- Director: `area` debe estar en su jerarquia; `agente` de sus areas; si viene `agente` sin `area`, se infiere.
- Admin: sin tope; valida existencia.

## Notas de datos
- Se usan horas efectivas (no las planificadas).
- En reporte general solo se muestran dias que tienen guardias.
- Fechas obligatorias `YYYY-MM-DD` (`desde <= hasta`).

## Front (resumen)
- Ruta `/paneladmin/reportes`: restaurada la vista original, se ocultan reportes no usados; CSRF automatico en axios; el controller calcula totales derivados y rellena periodo/area si el backend no los envia.
- Ruta `/reportes`: multiselects y validacion por rol; estilos a medio camino.

## Pendientes proximos
- Ajustar layout/estilos finales en ambas vistas de reportes.
- Completar totales visibles (horas/dias/presentismo) y revisar la vista previa para que muestre todos los campos esperados.
- Hacer coincidir el PDF con la plantilla institucional (logo/leyenda); agregar logos/plantilla a una carpeta de assets y usarlos en los exportes.
- Pruebas por rol (agente/jefatura/director/admin) en vista previa y exportes.
