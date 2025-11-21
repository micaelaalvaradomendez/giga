# Sistema de Aprobaciones Jerárquicas - Guardias

## 📋 Resumen del Sistema

Se ha implementado un sistema completo de aprobaciones jerárquicas para la gestión de guardias con los siguientes componentes:

### ✅ Características Implementadas

1. **Aprobación Jerárquica por Roles**
   - Jefatura crea → Director o Administrador aprueba
   - Director crea → Administrador aprueba
   - Administrador crea → Auto-aprobado (no requiere aprobación adicional)

2. **Estados de Cronograma**
   - `generada`: Estado inicial (legacy)
   - `pendiente`: Esperando aprobación
   - `aprobada`: Aprobada por rol superior
   - `publicada`: Visible para todos
   - `rechazada`: Rechazada con motivo

3. **Visualización Multi-día en Calendario**
   - Guardias que cruzan medianoche ahora se muestran en todos los días que abarcan
   - Ejemplo: Guardia 20:00-08:00 aparece tanto el día de inicio como el día siguiente

4. **Feedback en Planificador**
   - Mensaje detallado post-creación indicando estado de aprobación
   - Información sobre quién puede aprobar la guardia
   - Redirección automática después de 5 segundos

---

## 🗄️ Cambios en Base de Datos

### Nuevos Campos en Tabla `cronograma`

```sql
-- Campos agregados:
creado_por_rol VARCHAR(50)      -- Rol del creador: 'jefatura', 'director', 'administrador'
creado_por_id BIGINT             -- ID del agente creador (FK → agente)
aprobado_por_id BIGINT           -- ID del agente aprobador (FK → agente)

-- Índices para performance:
- idx_cronograma_estado
- idx_cronograma_creado_por_rol
- idx_cronograma_creado_por_id
- idx_cronograma_aprobado_por_id
```

### Script de Migración

Ubicación: `/home/micaela/giga/bd/init-scripts/06-add-approval-tracking.sql`

**Ejecutar migración:**
```bash
cd /home/micaela/giga/bd
docker-compose exec db psql -U giga -d giga -f /docker-entrypoint-initdb.d/06-add-approval-tracking.sql
```

O si la base de datos está corriendo localmente:
```bash
psql -U giga -d giga -f bd/init-scripts/06-add-approval-tracking.sql
```

---

## 🔧 Cambios en Backend

### 1. Modelo Actualizado (`back/guardias/models.py`)

**Nuevos campos en `Cronograma`:**
- `creado_por_rol`: Rol del creador
- `creado_por_id`: Foreign Key a Agente (creador)
- `aprobado_por_id`: Foreign Key a Agente (aprobador)

**Nuevas propiedades:**
- `requiere_aprobacion`: Verifica si necesita aprobación según rol
- `puede_aprobar_rol`: Lista de roles que pueden aprobar

### 2. Utilidades (`back/guardias/utils.py`)

**Funciones nuevas:**
- `get_approval_hierarchy(creado_por_rol)`: Retorna roles que pueden aprobar
- `puede_aprobar(cronograma, rol_aprobador)`: Valida permisos de aprobación
- `get_agente_rol(agente)`: Obtiene rol principal del agente
- `requiere_aprobacion_rol(creado_por_rol)`: Verifica si requiere aprobación

### 3. Serializers (`back/guardias/serializers.py`)

**`CronogramaExtendidoSerializer` actualizado:**
- Incluye: `creado_por_nombre`, `creado_por_apellido`
- Incluye: `aprobado_por_nombre`, `aprobado_por_apellido`
- Incluye: `requiere_aprobacion`, `puede_aprobar_rol`

### 4. Endpoints (`back/guardias/views.py`)

#### **GET** `/guardias/cronogramas/pendientes/`
Lista cronogramas pendientes que el usuario puede aprobar.

**Query params:**
- `agente_id`: ID del agente (opcional si hay auth)

**Response:**
```json
{
  "count": 2,
  "rol_agente": "director",
  "cronogramas": [
    {
      "id_cronograma": 123,
      "area_nombre": "Emergencias",
      "tipo": "regular",
      "estado": "pendiente",
      "creado_por_nombre": "Juan",
      "creado_por_rol": "jefatura",
      "puede_aprobar_rol": ["director", "administrador"],
      "total_guardias": 5
    }
  ]
}
```

#### **PATCH** `/guardias/cronogramas/{id}/aprobar/`
Aprueba un cronograma validando jerarquía de roles.

**Body:**
```json
{
  "agente_id": 1
}
```

**Response:**
```json
{
  "mensaje": "Cronograma aprobado exitosamente",
  "cronograma_id": 123,
  "aprobado_por": "María López",
  "fecha_aprobacion": "2025-11-21"
}
```

#### **POST** `/guardias/cronogramas/{id}/rechazar/`
Rechaza un cronograma con motivo.

**Body:**
```json
{
  "agente_id": 1,
  "motivo": "Falta coordinación con el área de soporte"
}
```

**Response:**
```json
{
  "mensaje": "Cronograma rechazado",
  "cronograma_id": 123,
  "rechazado_por": "Pedro García",
  "motivo": "Falta coordinación con el área de soporte"
}
```

#### **POST** `/guardias/cronogramas/crear_con_guardias/` (Modificado)
Ahora detecta automáticamente el rol del creador y establece el estado inicial:
- Admin → `estado='aprobada'` (auto-aprobado)
- Otros → `estado='pendiente'` (requiere aprobación)

**Body actualizado:**
```json
{
  "nombre": "Guardia Diciembre",
  "tipo": "regular",
  "id_area": 1,
  "fecha": "2025-12-01",
  "hora_inicio": "20:00:00",
  "hora_fin": "08:00:00",
  "agente_id": 1,
  "agentes": [2, 3, 4],
  "observaciones": "Guardia nocturna"
}
```

---

## 🎨 Cambios en Frontend

### 1. Services (`front/src/lib/services.js`)

**Nuevos métodos en `guardiasService`:**
```javascript
getPendientesAprobacion: (agenteId, token = null) => 
  createApiClient(token).get(`/guardias/cronogramas/pendientes/?agente_id=${agenteId}`)

rechazarCronograma: (id, data, token = null) => 
  createApiClient(token).post(`/guardias/cronogramas/${id}/rechazar/`, data)

// aprobarCronograma actualizado para recibir data:
aprobarCronograma: (id, data, token = null) => 
  createApiClient(token).patch(`/guardias/cronogramas/${id}/aprobar/`, data)
```

### 2. Página de Aprobaciones (`front/src/routes/paneladmin/guardias/aprobaciones/+page.svelte`)

**Funcionalidades:**
- **Tabs:** Pendientes / Aprobadas
- **Lista de cronogramas pendientes:** Filtrados por rol del usuario
- **Tarjetas informativas:** Muestran creador, área, horario, cantidad de guardias, roles que pueden aprobar
- **Acciones por cronograma:**
  - Ver Detalles (modal con lista de guardias)
  - Aprobar (validación de permisos en backend)
  - Rechazar (modal para ingresar motivo)
  - Publicar (solo para cronogramas aprobados)

**Estilo:** Consistente con el glassmorphism del resto del sistema

### 3. Calendario Multi-día (`front/src/routes/paneladmin/guardias/+page.svelte`)

**Nueva función:** `calcularFechasGuardia(fechaInicio, horaInicio, horaFin)`
- Detecta si una guardia cruza medianoche comparando horas
- Retorna array de fechas que abarca la guardia
- Ejemplo: Guardia 20:00-08:00 → retorna [fecha_inicio, fecha_inicio+1]

**Función modificada:** `agruparGuardias()`
- Ahora itera sobre todas las fechas que abarca cada guardia
- Evita duplicados al agrupar
- Guardias multi-día aparecen en todos los días correspondientes

**Función modificada:** `handleDayClick(event)`
- Filtra guardias usando `calcularFechasGuardia()`
- Muestra todas las guardias del día clickeado, incluyendo las que cruzan medianoche

### 4. Planificador con Feedback (`front/src/routes/paneladmin/guardias/planificador/+page.svelte`)

**Mejoras post-creación:**
- Consulta el estado del cronograma creado
- Muestra mensaje detallado según estado:
  - **Auto-aprobada (Admin):** "🎉 Como tienes rol de Administrador, la guardia fue auto-aprobada"
  - **Pendiente:** "⏳ Requiere aprobación de: director, administrador. Será visible en Aprobaciones"
  - **Generada:** "📋 La guardia ha sido creada y registrada"
- Redirección automática después de 5 segundos
- Soporte para saltos de línea en mensajes (`white-space: pre-line`)

---

## 🚀 Instrucciones de Despliegue

### 1. Aplicar Migración de Base de Datos

```bash
# Desde el directorio del proyecto
cd /home/micaela/giga

# Opción A: Dentro del contenedor de base de datos
docker-compose exec -w /docker-entrypoint-initdb.d db psql -U giga -d giga -f 06-add-approval-tracking.sql

# Opción B: Desde el host (si tienes psql instalado)
psql -U giga -h localhost -d giga -f bd/init-scripts/06-add-approval-tracking.sql
```

### 2. Reiniciar Backend

```bash
# Reiniciar contenedor de Django
cd back
docker-compose restart

# O si no usas Docker:
cd back
python manage.py runserver
```

### 3. Verificar Frontend

El frontend se actualizará automáticamente en desarrollo. En producción:

```bash
cd front
pnpm build
# O según tu configuración de build
```

### 4. Verificar Funcionamiento

1. **Crear guardia como Jefatura/Director:**
   - Ir a `/paneladmin/guardias/planificador`
   - Crear una guardia
   - Verificar mensaje de "Pendiente de aprobación"

2. **Aprobar como superior:**
   - Ir a `/paneladmin/guardias/aprobaciones`
   - Ver cronograma en tab "Pendientes"
   - Hacer clic en "Aprobar"

3. **Verificar calendario multi-día:**
   - Crear guardia con horario 20:00-08:00 (cruza medianoche)
   - Ir a `/paneladmin/guardias`
   - Verificar que aparece en ambos días del calendario

---

## 🧪 Testing

### Casos de Prueba

#### 1. Jerarquía de Aprobación
- [ ] Jefatura crea guardia → estado='pendiente'
- [ ] Director puede aprobar guardia de Jefatura
- [ ] Administrador puede aprobar cualquier guardia
- [ ] Director crea guardia → solo Admin puede aprobar
- [ ] Admin crea guardia → estado='aprobada' automáticamente

#### 2. Calendario Multi-día
- [ ] Guardia 20:00-08:00 aparece en día 1 y día 2
- [ ] Guardia 08:00-16:00 (mismo día) aparece solo en día 1
- [ ] Clic en día 2 muestra guardias que empezaron día 1 y cruzan medianoche

#### 3. Feedback en Planificador
- [ ] Admin ve mensaje de auto-aprobación
- [ ] Jefatura ve mensaje de pendiente con roles aprobadores
- [ ] Mensaje persiste 5 segundos antes de redirección

#### 4. Página de Aprobaciones
- [ ] Tab Pendientes muestra solo cronogramas que el usuario puede aprobar
- [ ] Tab Aprobadas muestra histórico
- [ ] Modal de rechazo requiere motivo
- [ ] Publicar solo disponible para cronogramas aprobados

---

## 📝 Notas Técnicas

### Auditoría
Todas las acciones de aprobación/rechazo se registran en `auditoria.RegistroAuditoria` con:
- `tipo_accion`: 'aprobacion_cronograma' o 'rechazo_cronograma'
- `detalle`: Incluye nombres, roles y motivos
- `modelo_afectado`: 'cronograma'
- `id_registro`: ID del cronograma afectado

### Permisos
El sistema actual simula roles mediante `agente_id` en el request. 
**TODO para producción:** Integrar con sistema de autenticación Django (`request.user.agente`).

### Performance
Se crearon índices en:
- `cronograma.estado`: Filtrado rápido por estado
- `cronograma.creado_por_rol`: Filtrado por rol creador
- `cronograma.creado_por_id`, `aprobado_por_id`: Joins rápidos con tabla agente

---

## 🔄 Flujo Completo

```
1. CREACIÓN
   Usuario (Jefatura) → Planificador → Crear Guardia
   ↓
   Backend detecta rol = "jefatura"
   ↓
   Cronograma.estado = "pendiente"
   Cronograma.creado_por_rol = "jefatura"
   Cronograma.puede_aprobar_rol = ["director", "administrador"]
   ↓
   Frontend muestra: "⏳ Pendiente de aprobación por director, administrador"

2. APROBACIÓN
   Usuario (Director) → Aprobaciones → Tab "Pendientes"
   ↓
   Ve cronogramas creados por Jefatura (filtro backend por rol)
   ↓
   Clic "Aprobar"
   ↓
   Backend valida: rol_director IN puede_aprobar_rol ✓
   ↓
   Cronograma.estado = "aprobada"
   Cronograma.aprobado_por_id = director.id
   Cronograma.fecha_aprobacion = hoy
   ↓
   Auditoría registra aprobación

3. PUBLICACIÓN
   Usuario (Admin) → Aprobaciones → Tab "Aprobadas"
   ↓
   Clic "Publicar"
   ↓
   Cronograma.estado = "publicada"
   ↓
   Visible para todos en calendario principal

4. VISUALIZACIÓN EN CALENDARIO
   Guardia: 2025-11-21 20:00 - 2025-11-22 08:00
   ↓
   calcularFechasGuardia() detecta cruce de medianoche
   ↓
   Retorna: ["2025-11-21", "2025-11-22"]
   ↓
   Calendario muestra la guardia en ambas fechas
```

---

## 📚 Referencias

### Archivos Modificados

**Backend:**
- `bd/init-scripts/06-add-approval-tracking.sql` (nuevo)
- `back/guardias/models.py` (Cronograma)
- `back/guardias/utils.py` (funciones de aprobación)
- `back/guardias/serializers.py` (CronogramaExtendidoSerializer)
- `back/guardias/views.py` (aprobar, rechazar, pendientes, crear_con_guardias)

**Frontend:**
- `front/src/lib/services.js` (guardiasService)
- `front/src/routes/paneladmin/guardias/aprobaciones/+page.svelte` (nuevo)
- `front/src/routes/paneladmin/guardias/+page.svelte` (calendario multi-día)
- `front/src/routes/paneladmin/guardias/planificador/+page.svelte` (feedback)

### Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/guardias/cronogramas/pendientes/` | Lista pendientes según rol |
| PATCH | `/guardias/cronogramas/{id}/aprobar/` | Aprueba con validación |
| POST | `/guardias/cronogramas/{id}/rechazar/` | Rechaza con motivo |
| PATCH | `/guardias/cronogramas/{id}/publicar/` | Publica cronograma |
| POST | `/guardias/cronogramas/crear_con_guardias/` | Crea con detección de rol |

---

## ✅ Checklist de Implementación

- [x] Migración SQL creada
- [x] Modelo Cronograma actualizado
- [x] Funciones de utilidad implementadas
- [x] Serializers actualizados
- [x] Endpoints de aprobación creados
- [x] Servicios frontend actualizados
- [x] Página de aprobaciones creada
- [x] Calendario multi-día implementado
- [x] Feedback en planificador agregado
- [ ] Migración SQL ejecutada en BD
- [ ] Backend reiniciado
- [ ] Tests de jerarquía validados
- [ ] Tests de calendario validados
- [ ] Integración con autenticación real

---

## 🐛 Troubleshooting

### Error: "Campo creado_por_rol no existe"
**Solución:** Ejecutar migración SQL en la base de datos.

### Guardias no aparecen en calendario
**Solución:** Verificar que `calcularFechasGuardia()` esté siendo llamado en `agruparGuardias()`.

### Usuario no puede aprobar
**Solución:** Verificar que:
1. El agente tenga un rol asignado en `AsignacionRol`
2. El rol del agente esté en `puede_aprobar_rol` del cronograma
3. El cronograma esté en estado='pendiente'

### Mensaje de feedback no muestra estado
**Solución:** Verificar que el endpoint `getCronograma()` retorne los campos `estado` y `puede_aprobar_rol`.

---

**Implementado por:** GitHub Copilot
**Fecha:** 21 de noviembre de 2025
**Versión:** 1.0
