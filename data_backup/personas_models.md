# App: Personas - Modelos de Base de Datos

## Descripción
Esta app gestiona usuarios, agentes, áreas organizacionales, roles y permisos del sistema GIGA.

## Modelos Definidos

### 1. Usuario (AbstractUser)
**Tabla:** `personas_usuario`  
**Hereda de:** `django.contrib.auth.models.AbstractUser`

```python
class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    cuil = models.CharField(max_length=11, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    password_reset = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
```

**Funcionalidades:**
- Autenticación por CUIL y email
- Control de contraseñas reseteadas
- Auditoría de creación y actualización

### 2. Area
**Tabla:** `personas_area`

```python
class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
```

**Características:**
- Jerarquía de áreas (área padre/hijas)
- Constraint: un área no puede ser padre de sí misma
- Unique constraint: nombre + área_padre
- Métodos: `get_jerarquia_completa()`, `get_areas_descendientes()`

### 3. Agente
**Tabla:** `personas_agente`

```python
class Agente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    
    # Identificación
    dni = models.CharField(max_length=8, unique=True)
    legajo = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Datos personales
    apellido = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    fecha_nac = models.DateField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    
    # Dirección
    provincia = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=50, blank=True, null=True)
    calle = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    
    # Datos laborales
    horario_entrada = models.TimeField(null=True, blank=True)
    horario_salida = models.TimeField(null=True, blank=True)
    categoria_revista = models.CharField(max_length=5)
    agrupacion = models.CharField(max_length=5, choices=[('EPU', 'EPU'), ('POMYS', 'POMyS'), ('PAYT', 'PAyT')])
    
    # Jerarquía
    es_jefe = models.BooleanField(default=False)
    id_jefe = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    categoria_usuf = models.CharField(max_length=5, blank=True, null=True)
```

### 4. Permiso
**Tabla:** `personas_permiso`

```python
class Permiso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
```

### 5. Rol
**Tabla:** `personas_rol`

```python
class Rol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    permisos = models.ManyToManyField(Permiso, through='PermisoRol')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
```

### 6. PermisoRol (Tabla Intermedia)
**Tabla:** `personas_permisorol`

```python
class PermisoRol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
```

**Constraints:** unique_together = ['rol', 'permiso']

### 7. AgenteRol (Asignaciones)
**Tabla:** `personas_agenterol`

```python
class AgenteRol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    asignado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
```

**Constraints:** unique_together = ['usuario', 'rol', 'area']

## Relaciones Principales

1. **Usuario ↔ Agente**: Relación 1:1
2. **Area**: Autorreferencia para jerarquía
3. **Agente**: Autorreferencia para jerarquía de jefes
4. **Rol ↔ Permiso**: Relación M:M a través de PermisoRol
5. **Usuario ↔ Rol**: Relación M:M a través de AgenteRol con contexto de Area

## Índices Definidos

- `idx_area_nombre_padre` en Area (nombre, area_padre)
- Todos los campos de auditoría están indexados implícitamente

## Constraints de Negocio

- Area no puede ser padre de sí misma
- Nombres de área únicos por nivel jerárquico
- CUIL y email únicos en Usuario
- DNI y legajo únicos en Agente