# App: Asistencia - Modelos de Base de Datos

## Descripción
Esta app gestiona todo lo relacionado con control de asistencia, marcas de entrada/salida, licencias, novedades y parámetros de control horario.

## Modelos Definidos

### 1. TipoLicencia
**Tabla:** `asistencia_tipolicencia`

```python
class TipoLicencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=255, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
```

**Ejemplos:** Vacaciones, Enfermedad, Personal, Estudio, Maternidad

### 2. Marca
**Tabla:** `asistencia_marca`

```python
class Marca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='marcas')
    fecha = models.DateField()
    hora = models.TimeField()
    tipo = models.CharField(max_length=10, choices=[('entrada', 'Entrada'), ('salida', 'Salida')])
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Registros individuales de entrada/salida
- Constraint: unique_together = ['agente', 'fecha', 'hora', 'tipo']
- Índices en: ['agente', 'fecha', 'hora']

### 3. ParteDiario
**Tabla:** `asistencia_partediario`

```python
class ParteDiario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha_parte = models.DateField()
    estado = models.CharField(max_length=20, default='borrador', 
                             choices=[('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('anulado', 'Anulado')])
    observaciones = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.CASCADE, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Consolidación diaria de asistencia
- Constraint: unique_together = ['fecha_parte', 'agente']
- Índices en: ['area', 'fecha_parte', 'agente']

### 4. Asistencia
**Tabla:** `asistencia_asistencia`

```python
class Asistencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    horario_entrada = models.TimeField(null=True, blank=True)
    horario_salida = models.TimeField(null=True, blank=True)
    minutos_tarde = models.IntegerField(default=0)
    minutos_extras = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, default='presente', 
                             choices=[('presente', 'Presente'), ('ausente', 'Ausente'), ('tardanza', 'Tardanza'), ('licencia', 'Licencia')])
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Registro diario consolidado por agente
- Constraint: unique_together = ['agente', 'fecha']
- Índices en: ['agente', 'fecha'], ['estado', 'fecha']

### 5. LicenciaONovedad (Clase Abstracta)
**Base para:** Licencia y Novedad

```python
class LicenciaONovedad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente', 
                             choices=[('pendiente', 'Pendiente'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('anulada', 'Anulada')])
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Constraint: fecha_fin >= fecha_inicio
- Método: `duracion_dias()`

### 6. Licencia
**Tabla:** `asistencia_licencia`  
**Hereda de:** LicenciaONovedad

```python
class Licencia(LicenciaONovedad):
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.CASCADE)
    con_goce_haberes = models.BooleanField(default=True)
```

**Características:**
- Licencias (vacaciones, enfermedad, personal, estudio)
- Índices en: ['agente', 'fecha_inicio', 'fecha_fin'], ['tipo_licencia', 'estado']

### 7. Novedad
**Tabla:** `asistencia_novedad`  
**Hereda de:** LicenciaONovedad

```python
class Novedad(LicenciaONovedad):
    TIPO_NOVEDAD_CHOICES = [('medica', 'Médica'), ('familiar', 'Familiar'), ('capacitacion', 'Capacitación'), ('otra', 'Otra')]
    tipo_novedad = models.CharField(max_length=20, choices=TIPO_NOVEDAD_CHOICES)
    requiere_justificativo = models.BooleanField(default=True)
```

**Características:**
- Novedades (médica, familiar, capacitación)
- Índices en: ['agente', 'fecha_inicio', 'fecha_fin'], ['tipo_novedad', 'estado']

### 8. Adjunto
**Tabla:** `asistencia_adjunto`

```python
class Adjunto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Relaciones polimórficas
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    archivo = models.FileField(upload_to='adjuntos/%Y/%m/', 
                              validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])])
    nombre_original = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tamaño = models.BigIntegerField()
    tipo_archivo = models.CharField(max_length=100)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Archivos adjuntos para licencias y novedades
- Relación polimórfica (puede asociarse a cualquier modelo)
- Validación de extensiones permitidas
- Índices en: ['content_type', 'object_id']

### 9. ParametrosControlHorario
**Tabla:** `asistencia_parametros_control_horario`

```python
class ParametrosControlHorario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='parametros_horario')
    
    # Ventanas de marcación
    ventana_entrada_inicio = models.TimeField(help_text="Hora más temprana permitida para marcar entrada")
    ventana_entrada_fin = models.TimeField(help_text="Hora más tardía permitida para marcar entrada")
    ventana_salida_inicio = models.TimeField(help_text="Hora más temprana permitida para marcar salida")
    ventana_salida_fin = models.TimeField(help_text="Hora más tardía permitida para marcar salida")
    
    # Tolerancias
    tolerancia_entrada_min = models.IntegerField(default=15, help_text="Tolerancia entrada en minutos")
    tolerancia_salida_min = models.IntegerField(default=15, help_text="Tolerancia salida en minutos")
    
    # Configuraciones adicionales
    requiere_justificacion_fuera_ventana = models.BooleanField(default=True)
    horas_trabajo_por_dia = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Configuración de ventanas de marcación y tolerancias por área
- Constraints: ventanas válidas, vigencia válida
- Índices en: ['area', 'vigente_desde', 'vigente_hasta']

## Relaciones Principales

1. **Agente ↔ Marca**: 1:N (Un agente tiene múltiples marcas)
2. **Agente ↔ Asistencia**: 1:N (Un agente tiene múltiples registros de asistencia)
3. **Agente ↔ ParteDiario**: 1:N (Un agente tiene múltiples partes diarios)
4. **Agente ↔ Licencia**: 1:N (Un agente puede tener múltiples licencias)
5. **Agente ↔ Novedad**: 1:N (Un agente puede tener múltiples novedades)
6. **TipoLicencia ↔ Licencia**: 1:N (Un tipo se usa en múltiples licencias)
7. **Area ↔ ParametrosControlHorario**: 1:N (Un área puede tener múltiples configuraciones de horario)
8. **Adjunto**: Relación polimórfica con Licencia/Novedad

## Constraints de Negocio

- Una marca por agente, fecha, hora y tipo
- Una asistencia por agente y fecha
- Un parte diario por agente y fecha
- Fecha fin >= fecha inicio en licencias y novedades
- Ventanas de marcación válidas (fin > inicio)
- Vigencia válida (hasta > desde)

## Funcionalidades Clave

- Control de marcas de entrada/salida
- Consolidación diaria de asistencia
- Gestión de licencias con tipos y estados
- Gestión de novedades con clasificación
- Adjuntos para documentación de respaldo
- Configuración flexible de horarios por área