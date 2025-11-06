# GIGA Backend - Database First

## Resumen de Implementación Completada
El Backend del sistema GIGA, permite que Django opere sobre la base de datos existente **sin modificar su estructura inicial**.

### 🔧 Configuración Database First

**Todos los modelos tienen `managed = False`:**
```python
class Meta:
    managed = False  # Django NO modifica la estructura de la tabla
    db_table = 'nombre_tabla_existente'
```

**Beneficios:**
- Django puede hacer **CRUD** sobre datos existentes
- Django **NO puede** modificar estructura de tablas
- Estructura definida en scripts SQL (`bd/init-scripts/`)
- Base de datos existente **preservada intacta**

## Arquitectura Implementada

### Apps Django

1. **`personas/`** - Gestión de agentes y áreas
   - `Area` - Áreas de trabajo en Protección Civil
   - `Rol` - Roles/cargos de los agentes  
   - `Agente` - Agentes de Protección Civil (modelo simple, no hereda de User)
   - `AgenteRol` - Relación N:N entre agentes y roles

2. **`auditoria/`** - Logging de cambios
   - `Auditoria` - Registro de cambios en el sistema

3. **`guardias/`** - Gestión de guardias
   - `Cronograma` - Programación de guardias
   - `Guardia` - Guardias asignadas
   - `ResumenGuardiaMes` - Resúmenes mensuales

4. **`asistencia/`** - Control de asistencias
   - `TipoLicencia` - Tipos de licencias
   - `ParteDiario` - Partes diarios de trabajo
   - `Licencia` - Licencias solicitadas
   - `Asistencia` - Registro de asistencias

## Verificación de Funcionamiento

### Conexión a BD Exitosa
```bash
# Django se conecta y consulta datos existentes
Total agentes: 6
Total áreas: 1
Primer agente: Tayra Aguila
```

### Operaciones CRUD Funcionando
```python
# CREATE - Django puede insertar datos
nueva_area = Area.objects.create(nombre='Test', activo=True)

# READ - Django puede consultar con JOINs
agentes_con_area = Agente.objects.select_related('id_area')

# UPDATE & DELETE - Django puede modificar/eliminar datos
area_test.delete()
```

## Estructura Final del Proyecto

```
back/
├── giga/                  
│   ├── settings.py         # Database First configurado
│   ├── urls.py
│   └── wsgi.py
├── personas/       
│   ├── models.py   
│   ├── admin.py
│   └── views.py
├── auditoria/      
├── guardias/       
├── asistencia/     
└── manage.py
```

## Comandos de Verificación

```bash
# Verificar que Django no tenga errores
docker-compose exec backend python manage.py check

# Probar consultas ORM
docker-compose exec backend python manage.py shell -c "
from personas.models import Agente, Area
print('Total agentes:', Agente.objects.count())
print('Total áreas:', Area.objects.count())
"
```
---

## ⚠️ Recordatorio Importante

**El backend NO PUEDE modificar la estructura de la base de datos existente.**
- ✅ Operaciones CRUD en datos: **Permitido**
- ❌ Modificar tablas existentes: **Prohibido** 
- ❌ Crear/eliminar columnas: **Prohibido**
- ❌ Cambiar tipos de datos: **Prohibido**

La estructura de BD se mantiene en `bd/init-scripts/` 
