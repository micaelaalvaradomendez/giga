# App: Guardias - Modelos de Base de Datos

## Descripción
Esta app gestiona cronogramas de guardias, asignaciones, control de horas trabajadas, cálculo de plus salariales y feriados.

## Modelos Definidos

### 1. Feriado
**Tabla:** `guardias_feriado`

```python
class Feriado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=255)
    es_nacional = models.BooleanField(default=True)
    es_provincial = models.BooleanField(default=False)
    es_local = models.BooleanField(default=False)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Días feriados que afectan el cálculo de guardias
- Clasificación por ámbito (nacional, provincial, local)
- Índices en: ['fecha'], ['es_nacional', 'es_provincial', 'es_local']

### 2. ReglaPlus
**Tabla:** `guardias_regla_plus`

```python
class ReglaPlus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    
    # Condiciones
    horas_minimas_diarias = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    horas_minimas_mensuales = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Tipos de área aplicables
    aplica_areas_operativas = models.BooleanField(default=True)
    aplica_areas_administrativas = models.BooleanField(default=True)
    
    # Plus a aplicar
    porcentaje_plus = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ej: 20.00 para 20%, 40.00 para 40%")
    
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Define reglas para cálculo de plus salarial
- Condiciones por horas mínimas diarias/mensuales
- Aplicabilidad por tipo de área
- Constraints: vigencia válida, porcentaje entre 0-100%
- Índices en: ['vigente_desde', 'vigente_hasta', 'activa']

### 3. CronogramaGuardias
**Tabla:** `guardias_cronogramaguardias`

```python
class CronogramaGuardias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=40, blank=True, null=True)
    estado = models.CharField(max_length=30, default='generada', 
                             choices=[('generada', 'Generada'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('publicada', 'Publicada')])
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    aprobado_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
```

**Características:**
- Define cronogramas de guardias por área y fecha
- Flujo de estados: generada → aprobada → publicada
- Constraint: hora_fin > hora_inicio
- Índices en: ['area', 'fecha', 'hora_inicio', 'hora_fin']

### 4. Guardia
**Tabla:** `guardias_guardia`

```python
class Guardia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(CronogramaGuardias, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardias_asignadas')
    fecha = models.DateField()
    
    # Asistencia real (NULL si no asistió)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    
    tipo = models.CharField(max_length=40, blank=True, null=True)
    activa = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, default='borrador', 
                             choices=[('borrador', 'Borrador'), ('aprobada', 'Aprobada'), ('publicada', 'Publicada'), ('anulada', 'Anulada')])
    
    # Control de horas
    horas_planificadas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horas_efectivas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
```

**Características:**
- Asignaciones individuales de guardias
- Control de horas planificadas vs efectivas
- Constraint: horas consistentes (ambas NULL o ambas con valor y hora_fin > hora_inicio)
- Unique constraint: ['cronograma', 'usuario', 'fecha']

### 5. HorasGuardias
**Tabla:** `guardias_horas_guardias`

```python
class HorasGuardias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumen_horas_guardias')
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    
    # Período
    año = models.IntegerField()
    mes = models.IntegerField()  # 1-12
    
    # Totales
    horas_planificadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    horas_efectivas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    guardias_totales = models.IntegerField(default=0)
    guardias_cumplidas = models.IntegerField(default=0)
    
    # Plus calculado
    plus_aplicable = models.BooleanField(default=False)
    porcentaje_plus = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    regla_plus_aplicada = models.ForeignKey(ReglaPlus, on_delete=models.SET_NULL, null=True, blank=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Resumen mensual de horas por agente y área
- Cálculo automático de plus aplicable
- Constraints: mes válido (1-12), año válido (>=2020), guardias_cumplidas <= guardias_totales
- Unique constraint: ['agente', 'area', 'año', 'mes']
- Índices en: ['agente', 'año', 'mes'], ['area', 'año', 'mes']

### 6. AsignacionPlus
**Tabla:** `guardias_asignacion_plus`

```python
class AsignacionPlus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asignaciones_plus')
    resumen_horas = models.ForeignKey(HorasGuardias, on_delete=models.CASCADE, related_name='asignaciones_plus')
    regla_plus = models.ForeignKey(ReglaPlus, on_delete=models.CASCADE)
    
    # Cálculo
    porcentaje_aplicado = models.DecimalField(max_digits=5, decimal_places=2)
    monto_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_plus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, default='calculado', 
                             choices=[('calculado', 'Calculado'), ('aprobado', 'Aprobado'), ('pagado', 'Pagado'), ('anulado', 'Anulado')])
    
    observaciones = models.TextField(blank=True, null=True)
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Asignaciones calculadas de plus salarial
- Flujo de estados: calculado → aprobado → pagado
- Unique constraint: ['agente', 'resumen_horas', 'regla_plus']
- Índices en: ['agente', 'estado'], ['resumen_horas', 'estado']

## Relaciones Principales

1. **Area ↔ CronogramaGuardias**: 1:N (Un área tiene múltiples cronogramas)
2. **CronogramaGuardias ↔ Guardia**: 1:N (Un cronograma tiene múltiples guardias)
3. **Usuario ↔ Guardia**: 1:N (Un usuario tiene múltiples guardias asignadas)
4. **Usuario ↔ HorasGuardias**: 1:N (Un usuario tiene múltiples resúmenes mensuales)
5. **Area ↔ HorasGuardias**: 1:N (Un área tiene múltiples resúmenes)
6. **ReglaPlus ↔ HorasGuardias**: 1:N (Una regla se aplica a múltiples resúmenes)
7. **HorasGuardias ↔ AsignacionPlus**: 1:N (Un resumen puede tener múltiples asignaciones de plus)
8. **ReglaPlus ↔ AsignacionPlus**: 1:N (Una regla se usa en múltiples asignaciones)

## Flujo de Trabajo

### Gestión de Cronogramas
1. **Generación**: Se crea cronograma con estado "generada"
2. **Aprobación**: Se cambia a "aprobada" por supervisor
3. **Publicación**: Se cambia a "publicada" y se notifica a usuarios

### Gestión de Guardias
1. **Asignación**: Se crean guardias individuales asociadas al cronograma
2. **Control**: Se registran horas reales de cumplimiento
3. **Cálculo**: Se consolidan horas en HorasGuardias mensualmente

### Cálculo de Plus
1. **Evaluación**: Se evalúan reglas de plus contra HorasGuardias
2. **Cálculo**: Se crean AsignacionPlus cuando se cumplen condiciones
3. **Aprobación**: Se aprueban para pago

## Constraints de Negocio

- Fechas de feriados únicas
- Vigencia válida en ReglaPlus
- Porcentajes de plus entre 0-100%
- Horas fin > horas inicio en cronogramas y guardias
- Guardias cumplidas ≤ guardias totales
- Un solo resumen mensual por agente/área/período
- Una sola asignación de plus por combinación única

## Funcionalidades Clave

- Gestión de feriados con clasificación
- Definición flexible de reglas de plus
- Cronogramas con flujo de aprobación
- Control de asistencia a guardias
- Consolidación mensual automática
- Cálculo automático de plus salariales