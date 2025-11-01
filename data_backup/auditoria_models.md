# App: Auditoria - Modelos de Base de Datos

## Descripción
Esta app gestiona el registro de auditoría de todas las operaciones realizadas en el sistema, tracking de cambios y trazabilidad.

## Modelos Definidos

### 1. Auditoria
**Tabla:** `auditoria_auditoria`

```python
class Auditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_creadas')
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='auditorias_actualizadas')
    nombre_tabla = models.CharField(max_length=255)
    pk_afectada = models.CharField(max_length=255)
    accion = models.CharField(max_length=20, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    valor_previo = models.JSONField(null=True, blank=True)
    valor_nuevo = models.JSONField(null=True, blank=True)
```

**Características:**
- Registro automático de todas las operaciones CRUD
- Almacenamiento de valores antes y después del cambio
- Tracking del usuario responsable
- Índices en: ['nombre_tabla', 'pk_afectada', 'creado_en']

## Funcionalidades del Sistema de Auditoría

### Tipos de Operaciones Auditadas

#### 1. CREATE (Creación)
- **valor_previo**: `null`
- **valor_nuevo**: JSON con todos los campos del objeto creado
- **Ejemplo**:
```json
{
  "accion": "create",
  "nombre_tabla": "personas_agente",
  "pk_afectada": "550e8400-e29b-41d4-a716-446655440000",
  "valor_previo": null,
  "valor_nuevo": {
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "12345678",
    "email": "juan.perez@example.com",
    "creado_en": "2024-01-01T10:00:00Z"
  }
}
```

#### 2. UPDATE (Actualización)
- **valor_previo**: JSON con valores antes del cambio
- **valor_nuevo**: JSON con valores después del cambio
- **Ejemplo**:
```json
{
  "accion": "update",
  "nombre_tabla": "personas_agente",
  "pk_afectada": "550e8400-e29b-41d4-a716-446655440000",
  "valor_previo": {
    "telefono": "123456789",
    "actualizado_en": "2024-01-01T10:00:00Z"
  },
  "valor_nuevo": {
    "telefono": "987654321",
    "actualizado_en": "2024-01-02T15:30:00Z"
  }
}
```

#### 3. DELETE (Eliminación)
- **valor_previo**: JSON con todos los campos del objeto eliminado
- **valor_nuevo**: `null`
- **Ejemplo**:
```json
{
  "accion": "delete",
  "nombre_tabla": "personas_agente",
  "pk_afectada": "550e8400-e29b-41d4-a716-446655440000",
  "valor_previo": {
    "nombre": "Juan",
    "apellido": "Pérez",
    "dni": "12345678",
    "activo": true
  },
  "valor_nuevo": null
}
```

### Tablas Auditadas

El sistema de auditoría automáticamente registra cambios en las siguientes tablas:

#### Personas App
- `personas_usuario`
- `personas_area`
- `personas_agente`
- `personas_permiso`
- `personas_rol`
- `personas_permisorol`
- `personas_agenterol`

#### Asistencia App
- `asistencia_tipolicencia`
- `asistencia_marca`
- `asistencia_partediario`
- `asistencia_asistencia`
- `asistencia_licencia`
- `asistencia_novedad`
- `asistencia_parametroscontrolhorario`

#### Guardias App
- `guardias_feriado`
- `guardias_reglaplus`
- `guardias_cronogramaguardias`
- `guardias_guardia`
- `guardias_horasguardias`
- `guardias_asignacionplus`

#### Reportes App
- `reportes_reporte`
- `reportes_plantillacorreo`
- `reportes_notificacion`

#### Convenio IA App
- `convenio_ia_convenio`
- `convenio_ia_consultaconvenio`

### Casos de Uso de Auditoría

#### 1. Trazabilidad de Cambios
```sql
-- Ver historial de cambios de un agente específico
SELECT * FROM auditoria_auditoria 
WHERE nombre_tabla = 'personas_agente' 
  AND pk_afectada = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY creado_en DESC;
```

#### 2. Actividad por Usuario
```sql
-- Ver todas las acciones realizadas por un usuario
SELECT * FROM auditoria_auditoria 
WHERE creado_por_id = 'user-uuid'
ORDER BY creado_en DESC;
```

#### 3. Cambios en Período Específico
```sql
-- Ver cambios en las últimas 24 horas
SELECT * FROM auditoria_auditoria 
WHERE creado_en >= NOW() - INTERVAL '24 hours'
ORDER BY creado_en DESC;
```

#### 4. Análisis de Operaciones por Tabla
```sql
-- Estadísticas de operaciones por tabla
SELECT nombre_tabla, accion, COUNT(*) as cantidad
FROM auditoria_auditoria 
WHERE creado_en >= '2024-01-01'
GROUP BY nombre_tabla, accion
ORDER BY nombre_tabla, accion;
```

### Implementación Técnica

#### Signal Handlers
El sistema utiliza Django signals para capturar automáticamente los cambios:

```python
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    # Registra creaciones y actualizaciones
    pass

@receiver(post_delete) 
def audit_post_delete(sender, instance, **kwargs):
    # Registra eliminaciones
    pass

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    # Captura valores previos para actualizaciones
    pass
```

#### Middleware de Auditoría
```python
class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Captura contexto del usuario para auditoría
        response = self.get_response(request)
        return response
```

### Consideraciones de Rendimiento

#### Índices Optimizados
- **Primario**: ['nombre_tabla', 'pk_afectada', 'creado_en']
- **Secundarios**: ['creado_por', 'creado_en'], ['accion', 'creado_en']

#### Políticas de Retención
```python
# Configuración sugerida para retención de datos
AUDIT_RETENTION_DAYS = {
    'critical_tables': 2555,  # 7 años para tablas críticas
    'normal_tables': 1095,    # 3 años para tablas normales
    'temp_tables': 365        # 1 año para tablas temporales
}
```

#### Archivado Automático
```python
# Script de archivado automático
def archive_old_audit_records():
    cutoff_date = timezone.now() - timedelta(days=365)
    old_records = Auditoria.objects.filter(creado_en__lt=cutoff_date)
    # Mover a tabla de archivo o exportar
```

### Seguridad y Compliance

#### Integridad de Datos
- Los registros de auditoría son **inmutables** (no se pueden modificar)
- Eliminación solo mediante procesos automatizados de archivado
- Acceso restringido solo a administradores

#### Compliance Regulatorio
- **SOX**: Trazabilidad completa de cambios financieros
- **GDPR**: Registro de accesos y modificaciones de datos personales
- **ISO 27001**: Control de accesos y modificaciones

### Reportes y Analytics

#### Dashboard de Auditoría
- Resumen diario/semanal/mensual de operaciones
- Top usuarios más activos
- Tablas con más modificaciones
- Alertas de actividad sospechosa

#### Exportación de Datos
```python
def export_audit_report(start_date, end_date, table_name=None):
    queryset = Auditoria.objects.filter(
        creado_en__range=[start_date, end_date]
    )
    if table_name:
        queryset = queryset.filter(nombre_tabla=table_name)
    
    # Exportar a Excel, PDF, etc.
```

## Relaciones Principales

1. **Usuario ↔ Auditoria**: 1:N (Un usuario puede generar múltiples registros de auditoría)
2. **Auditoria**: Referencia polimórfica a cualquier tabla del sistema

## Constraints de Negocio

- Registros de auditoría son inmutables una vez creados
- Todos los campos de tracking son obligatorios
- JSON debe ser válido en campos valor_previo/valor_nuevo

## Beneficios del Sistema

### Para Administradores
- Trazabilidad completa de cambios
- Identificación de usuarios responsables
- Detección de actividad sospechosa
- Cumplimiento regulatorio

### Para Usuarios
- Transparencia en el sistema
- Capacidad de restaurar datos
- Auditoría de sus propias acciones

### Para la Organización
- Compliance automático
- Reducción de riesgos
- Facilita auditorías externas
- Mejora la seguridad de datos