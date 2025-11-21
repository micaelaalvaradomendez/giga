# Resumen de Cambios - Módulo de Guardias
**Fecha:** 20 de noviembre de 2025

## 📋 Cambios Implementados

### 1. ✅ Integración de Calendario en Página Principal de Guardias

**Archivo modificado:** `/front/src/routes/paneladmin/guardias/+page.svelte`

**Cambios realizados:**
- ✅ Se integró el componente `CalendarioBase` directamente en la página principal
- ✅ Se mantuvieron las opciones de "Planificador" y "Aprobaciones"
- ✅ Se agregaron estadísticas de guardias (Total, Planificadas, Activas)
- ✅ Las guardias se agrupan por **área y horario** para mostrar correctamente cuando hay múltiples guardias en el mismo día
- ✅ Modal mejorado que muestra guardias agrupadas por "Área (hora_inicio - hora_fin)"
- ✅ Cada grupo muestra todos los agentes asignados a esa guardia específica

**Funcionalidades:**
```javascript
// Agrupación por área y horario
const clave = `${guardia.area_nombre || 'sin-area'}-${guardia.hora_inicio}-${guardia.hora_fin}`;

// Esto permite separar:
// - Área A (08:00 - 16:00) → Grupo 1
// - Área B (08:00 - 16:00) → Grupo 2 (diferente área, mismo horario)
// - Área A (18:00 - 02:00) → Grupo 3 (misma área, diferente horario)
```

**Vista del Modal:**
```
📅 Guardias del lunes, 25 de noviembre de 2025

┌─────────────────────────────────────────┐
│ Área Norte (08:00:00 - 16:00:00)       │
│ ├─ Juan Pérez      [regular] [planif.] │
│ └─ María García    [regular] [planif.] │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Área Sur (18:00:00 - 02:00:00)         │
│ └─ Carlos López    [especial] [confirm.]│
└─────────────────────────────────────────┘
```

---

### 2. ✅ Validación de Disponibilidad de Agentes en Planificador

**Archivo modificado:** `/front/src/routes/paneladmin/guardias/planificador/+page.svelte`

**Cambios realizados:**

#### A. Nueva función `verificarDisponibilidadAgente(agenteId)`
```javascript
async function verificarDisponibilidadAgente(agenteId) {
  // Obtiene todas las guardias del agente
  const response = await guardiasService.getGuardiasAgente(agenteId);
  const guardiasAgente = response.data?.guardias || [];
  
  // Verifica si alguna guardia se superpone con las fechas seleccionadas
  // Solo considera guardias activas y no canceladas
  for (const guardia of guardiasAgente) {
    if (guardia.activa === false || guardia.estado === 'cancelada') {
      continue;
    }
    
    const fechaGuardia = new Date(guardia.fecha);
    if (fechaGuardia >= fechaInicioSeleccionada && fechaGuardia <= fechaFinSeleccionada) {
      return true; // ⚠️ Conflicto detectado
    }
  }
  
  return false; // ✅ Sin conflictos
}
```

#### B. Validación en tiempo real al seleccionar agentes
```javascript
async function toggleAgente(agenteId) {
  // Si ya está seleccionado, simplemente lo deseleccionamos
  if (agentesSeleccionados.has(id)) {
    agentesSeleccionados.delete(id);
    return;
  }
  
  // ⚠️ NUEVA VALIDACIÓN: Verificar disponibilidad antes de seleccionar
  if (fechaInicio && fechaFin) {
    const tieneConflicto = await verificarDisponibilidadAgente(agenteId);
    if (tieneConflicto) {
      error = `${nombreAgente} ya tiene una guardia asignada que se superpone...`;
      mostrarToast(`⚠️ ${error}`, 'error');
      return; // ❌ No permite seleccionar
    }
  }
  
  agentesSeleccionados.add(id); // ✅ Permite seleccionar
}
```

#### C. Verificación múltiple antes de guardar
```javascript
async function guardarGuardia() {
  // Verificar disponibilidad de TODOS los agentes seleccionados
  const agentesConConflicto = [];
  for (const agenteId of agentesSeleccionados) {
    const tieneConflicto = await verificarDisponibilidadAgente(agenteId);
    if (tieneConflicto) {
      agentesConConflicto.push(nombreAgente);
    }
  }
  
  if (agentesConConflicto.length > 0) {
    error = `Los siguientes agentes ya tienen guardias asignadas: ...`;
    return; // ❌ No permite guardar
  }
  
  // ✅ Procede a guardar
}
```

---

### 3. ✅ Indicadores Visuales de Conflictos

**Cambios realizados:**

#### A. Variable de estado para conflictos
```javascript
let agentesConConflicto = new Set();
```

#### B. Verificación automática al avanzar al Paso 2
```javascript
async function avanzarPaso2() {
  if (!validarPaso1()) return;
  error = '';
  paso = 2;
  await verificarConflictosAgentes(); // 🔍 Verifica todos los agentes
}

async function verificarConflictosAgentes() {
  agentesConConflicto.clear();
  for (const agente of agentesDisponibles) {
    const tieneConflicto = await verificarDisponibilidadAgente(agente.id_agente);
    if (tieneConflicto) {
      agentesConConflicto.add(String(agente.id_agente));
    }
  }
}
```

#### C. Indicador visual en lista de agentes
```svelte
<!-- Contador de conflictos -->
{#if agentesConConflicto.size > 0}
  <span class="advertencia-conflictos">
    ⚠️ {agentesConConflicto.size} con guardias existentes
  </span>
{/if}

<!-- Badge individual por agente -->
{#each agentesDisponibles as agente}
  {@const tieneConflicto = agentesConConflicto.has(String(agente.id_agente))}
  <label class="agente-item" class:tiene-conflicto={tieneConflicto}>
    <!-- ... -->
    {#if tieneConflicto}
      <span class="badge-conflicto" title="Este agente ya tiene una guardia asignada">
        ⚠️ Con guardia
      </span>
    {/if}
  </label>
{/each}
```

#### D. Estilos CSS para indicadores
```css
.agente-item.tiene-conflicto {
  background: #fef2f2;      /* Fondo rojo claro */
  border: 1px solid #fecaca;
  opacity: 0.8;
}

.badge-conflicto {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.advertencia-conflictos {
  color: #d97706;          /* Naranja */
  font-weight: 600;
  font-size: 0.85rem;
}
```

---

## 🎯 Flujo Completo de Validación

### Paso 1: Ingresar datos de guardia
```
Usuario completa:
- Nombre de guardia
- Área
- Fecha inicio / Fecha fin
- Hora inicio / Hora fin
```

### Paso 2: Click en "Siguiente →"
```
✅ Validaciones de fechas
✅ Avanza a Paso 2
✅ Carga agentes del área
🔍 NUEVO: Verifica conflictos para TODOS los agentes
```

### Paso 3: Ver lista de agentes
```
📋 Lista de agentes con indicadores:
   - Agentes sin conflictos: Normal
   - Agentes con conflictos: ⚠️ Fondo rojo + Badge "Con guardia"
```

### Paso 4: Intentar seleccionar agente con conflicto
```
❌ No permite seleccionar
⚠️ Toast: "Juan Pérez ya tiene una guardia asignada..."
```

### Paso 5: Seleccionar agentes disponibles
```
✅ Checkbox se marca
✅ Fondo azul claro
```

### Paso 6: Click en "Guardar Guardia"
```
🔍 Verificación final de TODOS los seleccionados
   ├─ Si hay conflictos: ❌ Error y no guarda
   └─ Si no hay conflictos: ✅ Guarda y registra en auditoría
```

---

## 📊 Ejemplo Visual del Planificador

```
┌─────────────────────────────────────────────────────────────┐
│ PASO 2: Seleccionar Agentes                                 │
├─────────────────────────────────────────────────────────────┤
│ Resumen:                                                     │
│ Guardia: Turno Noche                                        │
│ Área: Seguridad Norte                                       │
│ Inicio: 2025-11-25 a las 18:00                             │
│ Fin: 2025-11-26 a las 02:00  📅 2 día(s)                   │
├─────────────────────────────────────────────────────────────┤
│ 5 agente(s) activo(s) • 2 seleccionado(s)                  │
│ ⚠️ 2 con guardias existentes                                │
├─────────────────────────────────────────────────────────────┤
│ ☑ Pérez, Juan                                               │
│   Legajo: 001 • Seguridad Norte                             │
├─────────────────────────────────────────────────────────────┤
│ ☐ García, María ⚠️ CON GUARDIA                              │
│   Legajo: 002 • Seguridad Norte                             │
│   [Fondo rojo - no permite seleccionar]                     │
├─────────────────────────────────────────────────────────────┤
│ ☑ López, Carlos                                             │
│   Legajo: 003 • Seguridad Norte                             │
├─────────────────────────────────────────────────────────────┤
│ ☐ Fernández, Ana ⚠️ CON GUARDIA                             │
│   Legajo: 004 • Seguridad Norte                             │
│   [Fondo rojo - no permite seleccionar]                     │
├─────────────────────────────────────────────────────────────┤
│ ☐ Rodríguez, Pedro                                          │
│   Legajo: 005 • Seguridad Norte                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Archivos Modificados

### 1. `/front/src/routes/paneladmin/guardias/+page.svelte`
- **Líneas agregadas:** ~200
- **Funciones nuevas:**
  - `cargarDatos()`
  - `cargarGuardias()`
  - `cargarFeriados()`
  - `agruparGuardias()`
  - `handleDayClick()`
  - `cerrarModal()`
  - `formatearFecha()`

### 2. `/front/src/routes/paneladmin/guardias/planificador/+page.svelte`
- **Líneas agregadas:** ~80
- **Funciones nuevas:**
  - `verificarDisponibilidadAgente(agenteId)`
  - `verificarConflictosAgentes()`
- **Funciones modificadas:**
  - `toggleAgente()` - Ahora valida disponibilidad
  - `guardarGuardia()` - Validación múltiple antes de guardar
  - `avanzarPaso2()` - Verifica conflictos al avanzar
  - `cargarAgentesDeArea()` - Llama verificación de conflictos

---

## ✅ Resultados Obtenidos

### 1. Calendario Mejorado
- ✅ Vista integrada en página principal
- ✅ Guardias agrupadas correctamente por área y horario
- ✅ Modal detallado con información completa
- ✅ Estadísticas en tiempo real

### 2. Validación de Disponibilidad
- ✅ Previene asignación de guardias a agentes ocupados
- ✅ Validación en tiempo real al seleccionar
- ✅ Verificación final antes de guardar
- ✅ Mensajes de error claros y específicos

### 3. Indicadores Visuales
- ✅ Fondo rojo para agentes con conflictos
- ✅ Badge "⚠️ Con guardia" visible
- ✅ Contador de agentes con conflictos
- ✅ Tooltips informativos

---

## 🧪 Casos de Prueba

### Caso 1: Guardia sin conflictos
```
✅ Fecha: 2025-11-25
✅ Agente: Juan Pérez (sin guardias previas)
✅ Resultado: Se permite seleccionar y guardar
```

### Caso 2: Guardia con conflicto
```
❌ Fecha: 2025-11-25
❌ Agente: María García (ya tiene guardia el 25/11)
❌ Resultado: Aparece con badge rojo, no permite seleccionar
⚠️ Toast: "María García ya tiene una guardia asignada..."
```

### Caso 3: Guardia multi-día con conflicto parcial
```
📅 Fecha inicio: 2025-11-25
📅 Fecha fin: 2025-11-27
❌ Agente: Carlos López (tiene guardia el 26/11)
❌ Resultado: Detecta conflicto el 26, no permite seleccionar
```

### Caso 4: Múltiples áreas, mismo horario
```
✅ Área A - 08:00 a 16:00 → Juan, María
✅ Área B - 08:00 a 16:00 → Carlos, Ana
✅ Calendario: Muestra 2 grupos separados
✅ Modal: Lista ambos grupos claramente
```

---

## 📝 Notas Técnicas

### Optimizaciones Futuras
1. **Cache de guardias:** Evitar consultas repetidas para el mismo agente
2. **Validación en backend:** Duplicar validación en el servidor
3. **WebSockets:** Actualización en tiempo real del calendario
4. **Filtros avanzados:** Por área, tipo de guardia, estado

### Limitaciones Actuales
- La validación solo considera guardias "activas" y no "canceladas"
- No valida superposición de horarios dentro del mismo día
- Requiere conexión al backend para cada verificación

---

## 🎓 Lecciones Aprendidas

1. **Validación multi-capa:** Validar en selección Y al guardar previene errores
2. **Indicadores visuales:** Los badges y colores mejoran UX significativamente
3. **Agrupación inteligente:** Agrupar por área+horario resuelve el problema de guardias múltiples
4. **Async/await:** Necesario para validaciones que requieren llamadas a API

---

*Documento generado automáticamente el 20 de noviembre de 2025*
