# Guía de Integración: Implementación Actual vs Diseño de Base de Datos

## 📋 Resumen Ejecutivo

Este documento analiza las diferencias entre la implementación actual del backend Django y el diseño de base de datos en `db.puml`, proporcionando una guía detallada para la integración y migración necesaria.

## 🔍 Análisis Comparativo

### Estado Actual vs Diseño Objetivo

| Aspecto | Implementación Actual | Diseño db.puml | Estado |
|---------|---------------------|----------------|---------|
| **Sistema de Usuarios** | Django Auth (User) | Tabla `usuarios` personalizada | ⚠️ **Divergente** |
| **Áreas** | Modelo básico sin jerarquía | Jerarquía con `area_padre_id` | ⚠️ **Incompleto** |
| **Agentes** | Modelo básico | Modelo extendido con más campos | ⚠️ **Incompleto** |
| **Roles/Permisos** | Sistema básico con JSON | Sistema relacional completo | ⚠️ **Simplificado** |
| **Guardias** | Modelos adicionales no contemplados | Modelo base contemplado | ⚠️ **Extendido** |
| **Auditoría** | Implementación básica | Modelo estándar de auditoría | ✅ **Compatible** |
| **Asistencia** | Sistema básico | Sistema con `parte_diario` | ⚠️ **Diferente** |

## 🔧 Modificaciones Requeridas

### 1. **Sistema de Usuarios y Autenticación**

#### 🚨 **Problema Principal**
- **Actual**: Usa `django.contrib.auth.User` 
- **Diseño**: Tabla `usuarios` personalizada con campos específicos

#### 🛠️ **Solución Recomendada**

**Opción A: Migrar a Usuario Personalizado (Recomendado)**
```python
# back/personas/models.py
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

# settings.py
AUTH_USER_MODEL = 'personas.Usuario'
```

**Opción B: Mantener Django Auth + Perfil**
```python
# Mantener actual y agregar relación
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    # ... otros campos específicos
```

#### 📋 **Tareas de Migración**
1. **Crear nuevo modelo Usuario**
2. **Actualizar `AUTH_USER_MODEL` en settings**
3. **Migrar datos existentes**
4. **Actualizar todas las relaciones FK**

---

### 2. **Modelo de Áreas - Jerarquía**

#### 🚨 **Problema**
- **Actual**: Sin jerarquía
- **Diseño**: Estructura jerárquica con `area_padre_id`

#### 🛠️ **Solución**
```python
# back/personas/models.py
class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='areas_hijas')
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='areas_creadas')
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='areas_actualizadas')
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(area_padre=models.F('id')),
                name='area_no_padre_si_mismo'
            )
        ]
        indexes = [
            models.Index(fields=['nombre', 'area_padre'], name='idx_area_nombre_padre')
        ]

    def get_jerarquia_completa(self):
        """Retorna la jerarquía completa del área"""
        pass
        
    def get_areas_descendientes(self):
        """Retorna todas las áreas descendientes"""
        pass
```

#### 📋 **Tareas**
1. **Agregar campo `area_padre`**
2. **Implementar métodos de jerarquía**
3. **Crear constraint de auto-referencia**
4. **Migrar datos existentes**

---

### 3. **Modelo de Agentes - Campos Extendidos**

#### 🚨 **Problema**
- **Actual**: Campos básicos
- **Diseño**: Modelo completo con datos personales y laborales

#### 🛠️ **Solución**
```python
# back/personas/models.py
class Agente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='agente')
    
    # Datos de identificación
    dni = models.CharField(max_length=8, unique=True)
    legajo = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Datos personales
    apellido = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    fecha_nac = models.DateField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    
    # Dirección
    provincia = models.CharField(max_length=50, default='Tierra del Fuego')
    ciudad = models.CharField(max_length=50, blank=True, null=True)
    calle = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    
    # Datos laborales
    horario_entrada = models.TimeField(null=True, blank=True)
    horario_salida = models.TimeField(null=True, blank=True)
    categoria_revista = models.CharField(max_length=5)
    agrupacion = models.CharField(max_length=5, choices=[
        ('EPU', 'EPU'), ('POMYS', 'POMyS'), ('PAYT', 'PAyT')
    ])
    
    # Jerarquía
    es_jefe = models.BooleanField(default=False)
    jefe = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinados')
    categoria_usuf = models.CharField(max_length=5, blank=True, null=True)
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='agentes_creados')
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='agentes_actualizados')
```

#### 📋 **Tareas**
1. **Agregar campos faltantes**
2. **Migrar datos existentes**
3. **Actualizar serializers y forms**
4. **Validar restricciones de negocio**

---

### 4. **Sistema de Roles y Permisos - Normalización**

#### 🚨 **Problema**
- **Actual**: Sistema simplificado con JSON
- **Diseño**: Sistema normalizado con tablas relacionales

#### 🛠️ **Solución**
```python
# back/personas/models.py

class Permiso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

class Rol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    permisos = models.ManyToManyField(Permiso, through='PermisoRol')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

class PermisoRol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['rol', 'permiso']

class AgenteRol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    asignado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='asignaciones_creadas')
    
    class Meta:
        unique_together = ['usuario', 'rol', 'area']
```

#### 📋 **Tareas**
1. **Crear modelos de permisos normalizados**
2. **Migrar datos del JSON actual**
3. **Implementar lógica de permisos**
4. **Actualizar sistema de autenticación**

---

### 5. **Sistema de Guardias - Ajustes al Diseño**

#### 🚨 **Problema**
- **Actual**: Modelos adicionales no contemplados en diseño
- **Diseño**: Modelo base más simple

#### 🛠️ **Solución**
```python
# back/guardias/models.py

class CronogramaGuardias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=40, blank=True, null=True)
    estado = models.CharField(max_length=30, default='generada', choices=[
        ('generada', 'Generada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('publicada', 'Publicada')
    ])
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    aprobado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='cronogramas_aprobados')
    aprobado_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F('hora_inicio')),
                name='hora_fin_mayor_inicio'
            )
        ]
        indexes = [
            models.Index(fields=['area', 'fecha', 'hora_inicio', 'hora_fin'])
        ]

class Guardia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(CronogramaGuardias, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateField()
    
    # Asistencia real (NULL si no asistió)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    
    tipo = models.CharField(max_length=40, blank=True, null=True)
    activa = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, default='borrador', choices=[
        ('borrador', 'Borrador'),
        ('aprobada', 'Aprobada'),
        ('publicada', 'Publicada'),
        ('anulada', 'Anulada')
    ])
    
    # Control de horas
    horas_planificadas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horas_efectivas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_inicio__isnull=True, hora_fin__isnull=True) |
                         models.Q(hora_inicio__isnull=False, hora_fin__isnull=False, hora_fin__gt=models.F('hora_inicio')),
                name='horas_consistentes'
            )
        ]
        unique_together = ['cronograma', 'usuario', 'fecha']
```

#### 📋 **Tareas**
1. **Ajustar modelos existentes al diseño**
2. **Mantener funcionalidad adicional en modelos separados**
3. **Validar constraints de negocio**

---

### 6. **Sistema de Asistencia - Integración con Parte Diario**

#### 🚨 **Problema**
- **Actual**: Sistema independiente de asistencia
- **Diseño**: Sistema integrado con `parte_diario` y `tipo_licencia`

#### 🛠️ **Solución**
```python
# back/asistencia/models.py

class TipoLicencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=255, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

class ParteDiario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    fecha_parte = models.DateField()
    estado = models.CharField(max_length=20, default='borrador', choices=[
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('anulado', 'Anulado')
    ])
    observaciones = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.CASCADE)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['area', 'fecha_parte', 'agente'])
        ]
```

#### 📋 **Tareas**
1. **Integrar sistema actual con parte diario**
2. **Normalizar tipos de licencia**
3. **Migrar datos existentes**

---

### 7. **Sistema de Auditoría - Estandarización**

#### ✅ **Estado Actual**
El sistema de auditoría actual es compatible, solo necesita ajustes menores:

```python
# back/auditoria/models.py
class Auditoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    nombre_tabla = models.CharField(max_length=255)
    pk_afectada = models.CharField(max_length=255)
    accion = models.CharField(max_length=20, choices=[
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete')
    ])
    valor_previo = models.JSONField(null=True, blank=True)
    valor_nuevo = models.JSONField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['nombre_tabla', 'pk_afectada', 'creado_en'])
        ]
```

---

## 📋 Plan de Migración Completo

### Fase 1: Preparación (1-2 días)
1. **Backup completo** de la base de datos actual
2. **Análisis de dependencias** entre modelos
3. **Preparación de scripts** de migración

### Fase 2: Sistema de Usuarios (2-3 días)
1. **Crear modelo Usuario personalizado**
2. **Migrar datos de auth_user**
3. **Actualizar configuración AUTH_USER_MODEL**
4. **Probar autenticación**

### Fase 3: Modelos Base (3-4 días)
1. **Actualizar modelo Area con jerarquía**
2. **Extender modelo Agente**
3. **Normalizar sistema de roles y permisos**
4. **Migrar datos existentes**

### Fase 4: Modelos Específicos (2-3 días)
1. **Ajustar modelos de Guardias**
2. **Integrar sistema de Asistencia con ParteDiario**
3. **Estandarizar modelo de Auditoría**

### Fase 5: Pruebas y Validación (2-3 días)
1. **Pruebas unitarias** de nuevos modelos
2. **Pruebas de integración** API
3. **Validación de constraints** de base de datos
4. **Pruebas de rendimiento**

### Fase 6: Actualización Frontend (1-2 días)
1. **Actualizar servicios** de API
2. **Ajustar formularios** y validaciones
3. **Probar integración** completa

---

## 🚨 Consideraciones Críticas

### 1. **Compatibilidad con Django Auth**
- La migración a usuario personalizado es **irreversible**
- Requiere **recrear migraciones** desde cero
- **Impacto alto** en desarrollo actual

### 2. **Integridad de Datos**
- **Validar constraints** antes de implementar
- **Migrar datos** preservando relaciones
- **Backup y rollback** strategy

### 3. **Rendimiento**
- **Índices optimizados** para consultas frecuentes
- **Consultas complejas** con joins múltiples
- **Caching strategy** para jerarquías

### 4. **Testing**
- **Cobertura completa** de nuevos modelos
- **Pruebas de migración** en entorno staging
- **Validación de API** endpoints

---

## 🎯 Recomendaciones Finales

### **Estrategia Recomendada: Migración Incremental**

1. **Mantener sistema actual** funcionando
2. **Implementar cambios** por módulos
3. **Migrar datos** progresivamente
4. **Validar** cada etapa antes de continuar

### **Prioridades de Implementación**

1. 🔴 **Alta**: Sistema de usuarios y autenticación
2. 🟡 **Media**: Jerarquía de áreas y roles normalizados
3. 🟢 **Baja**: Integración parte diario y ajustes menores

### **Monitoreo Post-Migración**

1. **Performance** de consultas complejas
2. **Integridad** de datos relacionales
3. **Funcionamiento** de constraints
4. **Experiencia** de usuario en frontend

---

## 📞 Próximos Pasos

1. **Revisar** este análisis con el equipo
2. **Priorizar** modificaciones según impacto
3. **Planificar** timeline de implementación
4. **Preparar** entorno de testing
5. **Ejecutar** migración por fases

---

*Documento generado el 15 de octubre de 2025*  
*Basado en análisis de implementación actual vs diseño db.puml*