# App: Reportes - Modelos de Base de Datos

## Descripción
Esta app gestiona la generación de reportes del sistema, notificaciones por email, plantillas de correo y envíos masivos de notificaciones.

## Enums Definidos

### TipoReporte
```python
class TipoReporte(models.TextChoices):
    INDIVIDUAL = 'INDIVIDUAL', _('Individual')
    AREA = 'AREA', _('Área')
    DIRECCION = 'DIRECCION', _('Dirección')
    CONSOLIDADO = 'CONSOLIDADO', _('Consolidado')
```

### FormatoReporte
```python
class FormatoReporte(models.TextChoices):
    PDF = 'PDF', _('PDF')
    XLSX = 'XLSX', _('Excel')
```

### EstadoReporte
```python
class EstadoReporte(models.TextChoices):
    LISTO = 'LISTO', _('Listo')
    ERROR = 'ERROR', _('Error')
```

### EstadoLote
```python
class EstadoLote(models.TextChoices):
    PENDIENTE = 'PENDIENTE', _('Pendiente')
    PARCIAL = 'PARCIAL', _('Parcial')
    COMPLETO = 'COMPLETO', _('Completo')
```

### MedioNotificacion
```python
class MedioNotificacion(models.TextChoices):
    EMAIL = 'EMAIL', _('Email')
```

### OrigenNotificacion
```python
class OrigenNotificacion(models.TextChoices):
    SISTEMA = 'SISTEMA', _('Sistema')
    USUARIO = 'USUARIO', _('Usuario')
```

### EstadoEnvio
```python
class EstadoEnvio(models.TextChoices):
    PENDIENTE = 'PENDIENTE', _('Pendiente')
    ENVIADO = 'ENVIADO', _('Enviado')
    ERROR = 'ERROR', _('Error')
```

## Modelos Definidos

### 1. Reporte
**Tabla:** `reportes_reporte`

```python
class Reporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TipoReporte.choices)
    filtros = models.JSONField()
    formato = models.CharField(max_length=10, choices=FormatoReporte.choices)
    generado_por = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='reportes_generados')
    generado_en = models.DateTimeField(auto_now_add=True)
    ruta_archivo = models.FileField(upload_to='reportes/', blank=True, null=True)
    estado = models.CharField(max_length=10, choices=EstadoReporte.choices, default=EstadoReporte.LISTO)
    error = models.TextField(blank=True, null=True)
```

**Características:**
- Generación de reportes en diferentes formatos (PDF, Excel)
- Filtros flexibles almacenados en JSON
- Tipos: Individual, por Área, por Dirección, Consolidado
- Archivos generados se almacenan en filesystem

**Métodos definidos:**
- `previsualizar(filtros)`: Genera vista previa del reporte
- `exportar(filtros, formato)`: Exporta en formato especificado
- `validar_filtros(filtros)`: Valida estructura de filtros

### 2. PlantillaCorreo
**Tabla:** `reportes_plantillacorreo`

```python
class PlantillaCorreo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, unique=True)
    asunto_tpl = models.CharField(max_length=500)
    cuerpo_tpl = models.TextField()
    variables = models.JSONField()
    version = models.IntegerField(default=1)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
```

**Características:**
- Plantillas reutilizables para correos electrónicos
- Sistema de versionado
- Variables dinámicas en formato JSON
- Vigencia temporal para activar/desactivar plantillas

**Ejemplo de variables JSON:**
```json
{
  "variables": [
    {
      "nombre": "{{nombre_agente}}",
      "descripcion": "Nombre completo del agente",
      "tipo": "string"
    },
    {
      "nombre": "{{fecha_guardia}}",
      "descripcion": "Fecha de la guardia asignada",
      "tipo": "date"
    },
    {
      "nombre": "{{area_nombre}}",
      "descripcion": "Nombre del área",
      "tipo": "string"
    }
  ]
}
```

**Métodos definidos:**
- `render(variables)`: Renderiza plantilla con variables

### 3. Notificacion
**Tabla:** `reportes_notificacion`

```python
class Notificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    remitente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='notificaciones_enviadas')
    destinatario = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='notificaciones_recibidas')
    asunto = models.CharField(max_length=500)
    cuerpo = models.TextField()
    medio = models.CharField(max_length=10, choices=MedioNotificacion.choices, default=MedioNotificacion.EMAIL)
    origen = models.CharField(max_length=10, choices=OrigenNotificacion.choices)
    estado_envio = models.CharField(max_length=10, choices=EstadoEnvio.choices, default=EstadoEnvio.PENDIENTE)
    intentos = models.IntegerField(default=0)
    ultimo_intento_en = models.DateTimeField(blank=True, null=True)
    error_mensaje = models.TextField(blank=True, null=True)
    plantilla = models.ForeignKey(PlantillaCorreo, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Sistema de notificaciones por email
- Control de intentos de envío y errores
- Origen automático (sistema) o manual (usuario)
- Integración con plantillas de correo

**Métodos definidos:**
- `redactar(remitente, destinatario, asunto, cuerpo, origen)`: Crea nueva notificación
- `enviar()`: Envía la notificación
- `reintentar()`: Reintenta envío fallido
- `marcar_error(mensaje)`: Marca notificación con error

### 4. EnvioLoteNotificaciones
**Tabla:** `reportes_enviolotenotificaciones`

```python
class EnvioLoteNotificaciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(CronogramaGuardias, on_delete=models.CASCADE, related_name='envios_notificaciones')
    creado_en = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    enviados = models.IntegerField(default=0)
    fallidos = models.IntegerField(default=0)
    estado = models.CharField(max_length=10, choices=EstadoLote.choices, default=EstadoLote.PENDIENTE)
```

**Características:**
- Envíos masivos de notificaciones para cronogramas de guardias
- Seguimiento de progreso (total, enviados, fallidos)
- Estados: PENDIENTE → PARCIAL → COMPLETO

**Métodos definidos:**
- `iniciar_para_publicacion(cronograma)`: Inicia envío masivo
- `registrar_resultado(notificacion, ok)`: Registra resultado individual
- `resumen()`: Retorna resumen del envío

## Modelos Auxiliares

### 5. RenderCorreo
**Tabla:** `reportes_rendercorreo`

```python
class RenderCorreo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asunto = models.CharField(max_length=500)
    cuerpo = models.TextField()
    variables = models.JSONField()
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Almacena correos renderizados para auditoría
- Preserva variables utilizadas en renderizado

### 6. Vista
**Tabla:** `reportes_vista`

```python
class Vista(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datos = models.JSONField()
    formato = models.CharField(max_length=50)
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Almacena vistas de datos para reportes
- Formatos flexibles (tabular, gráfico, etc.)

## Flujos de Trabajo

### Generación de Reportes
1. **Solicitud**: Usuario solicita reporte con filtros específicos
2. **Validación**: Se validan filtros y permisos
3. **Generación**: Se procesa el reporte en formato solicitado
4. **Almacenamiento**: Se guarda archivo generado
5. **Notificación**: Se notifica al usuario (opcional)

### Sistema de Notificaciones
1. **Creación**: Se crea notificación (manual o automática)
2. **Cola**: Se agrega a cola de envío
3. **Procesamiento**: Worker procesa notificaciones pendientes
4. **Envío**: Se intenta enviar por email
5. **Resultado**: Se actualiza estado según resultado

### Envíos Masivos
1. **Trigger**: Cronograma se publica
2. **Preparación**: Se crea lote de notificaciones
3. **Procesamiento**: Se envía a cada usuario asignado
4. **Seguimiento**: Se actualiza progreso en tiempo real
5. **Finalización**: Se marca como completo

## Casos de Uso

### Reportes de Asistencia
```json
{
  "tipo": "AREA",
  "filtros": {
    "area_id": "uuid-area",
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-01-31",
    "incluir_licencias": true,
    "formato_horas": "decimal"
  },
  "formato": "PDF"
}
```

### Notificación de Guardia Asignada
```json
{
  "plantilla": "guardia_asignada",
  "variables": {
    "nombre_agente": "Juan Pérez",
    "fecha_guardia": "2024-01-15",
    "hora_inicio": "08:00",
    "hora_fin": "16:00",
    "area_nombre": "Emergencias"
  }
}
```

### Reporte Consolidado Mensual
```json
{
  "tipo": "CONSOLIDADO",
  "filtros": {
    "año": 2024,
    "mes": 1,
    "incluir_guardias": true,
    "incluir_licencias": true,
    "incluir_plus": true,
    "agrupar_por": "area"
  },
  "formato": "XLSX"
}
```

## Relaciones Principales

1. **Agente ↔ Reporte**: 1:N (Un agente genera múltiples reportes)
2. **Agente ↔ Notificacion**: N:M (Remitente/Destinatario)
3. **PlantillaCorreo ↔ Notificacion**: 1:N (Una plantilla para múltiples notificaciones)
4. **CronogramaGuardias ↔ EnvioLoteNotificaciones**: 1:N (Un cronograma puede tener múltiples envíos)

## Integraciones

### Sistema de Email
- Configuración SMTP para envíos
- Plantillas HTML y texto plano
- Manejo de adjuntos en reportes

### Generadores de Reportes
- **PDF**: ReportLab, WeasyPrint
- **Excel**: openpyxl, xlswriter
- **CSV**: Exportación nativa Django

### Cola de Procesamiento
- **Celery**: Para procesamiento asíncrono
- **Redis/RabbitMQ**: Como broker de mensajes
- **Cron Jobs**: Para envíos programados

## Configuraciones

### Plantillas de Email Predefinidas
- **guardia_asignada**: Notifica asignación de guardia
- **cronograma_publicado**: Notifica publicación de cronograma
- **licencia_aprobada**: Notifica aprobación de licencia
- **reporte_generado**: Notifica reporte listo para descarga

### Tipos de Filtros por Reporte
- **Individual**: agente_id, fecha_inicio, fecha_fin
- **Área**: area_id, fecha_inicio, fecha_fin, incluir_subáreas
- **Dirección**: direccion_id, fecha_inicio, fecha_fin
- **Consolidado**: año, mes, tipo_consolidado

## Consideraciones Técnicas

### Rendimiento
- Reportes grandes se procesan asíncronamente
- Cache de reportes frecuentes
- Compresión de archivos grandes

### Seguridad
- Validación de permisos por tipo de reporte
- Sanitización de filtros de entrada
- Acceso seguro a archivos generados

### Escalabilidad
- Workers separados para reportes y notificaciones
- Particionado de tablas de notificaciones por fecha
- Archivado automático de reportes antiguos