# Reportes de Guardias - API (Backend)

## Autenticación y headers
- Usa la sesión (cookie `sessionid`) y CSRF (`csrftoken`).
- Todos los endpoints son `POST` y esperan JSON en el body (`Content-Type: application/json`).

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

### General (por área/jerarquía)
- URL: `/api/guardias/guardias/reporte_general/`
- Body ejemplo:
```json
{
  "fecha_desde": "2025-11-01",
  "fecha_hasta": "2025-11-30",
  "area": 5
}
```
- Opcional: `"agente": <id>` para filtrar a un agente dentro del alcance.

## Endpoints de exportación (usa los mismos filtros)
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
- Para individual, usa `"tipo_reporte": "individual"` y pasa `"agente"`.

## Reglas de permisos (server-side)
- Agente: fuerza su propio `agente` (id), ignora `area`.
-,Jefatura: fija `area` = la suya; `agente` solo de su área.
-,Director: `area` debe estar en su jerarquía; `agente` de las areas; si viene `agente` sin `area`, se infiere.
- Admin: sin tope; valida existencia.

## Notas de datos
- Se usan horas efectivas (no las planificadas).
- En reporte general solo se muestran días que tienen guardias.
- Fechas obligatorias en formato `YYYY-MM-DD` (valida `desde <= hasta`).
