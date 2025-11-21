<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { personasService, guardiasService } from '$lib/services.js';

  let loading = false;
  let error = '';
  let success = '';
  let paso = 1;

  let nombre = '';
  let tipo = 'regular';
  let areaSeleccionada = null;
  let fechaInicio = '';
  let horaInicio = '08:00';
  let fechaFin = '';
  let horaFin = '16:00';
  let observaciones = '';

  let areas = [];
  let agentesDisponibles = [];
  let agentesSeleccionados = new Set();
  let agentesConConflicto = new Set();

  let toastVisible = false;
  let toastMensaje = '';
  let toastTipo = 'success';

  onMount(async () => {
    await cargarAreas();
  });

  async function cargarAreas() {
    try {
      loading = true;
      error = '';
      const response = await personasService.getAreas();
      // La API devuelve { data: { results: [...] } }
      areas = response.data?.results || response.data?.data?.results || [];
      console.log('Áreas cargadas:', areas);
    } catch (e) {
      error = 'Error al cargar las áreas';
      console.error('Error cargando áreas:', e);
    } finally {
      loading = false;
    }
  }

  async function cargarAgentesDeArea() {
    if (!areaSeleccionada) return;

    try {
      loading = true;
      error = '';
      const response = await personasService.getAgentes();
      // La API puede devolver { results: [...] } (paginado) o { data: { results: [...] } }
      const todosAgentes = response.data?.results || response.data?.data?.results || response.data || [];
      console.log('Agentes cargados:', todosAgentes);

      // Filtrar agentes que pertenecen al área seleccionada y están activos
      // Los agentes tienen area_id que debe coincidir con areaSeleccionada
      agentesDisponibles = todosAgentes.filter(agente => {
        return agente.area_id === areaSeleccionada && agente.activo !== false;
      });
      console.log('Agentes disponibles para área', areaSeleccionada, ':', agentesDisponibles);

      if (agentesDisponibles.length === 0) {
        error = 'No hay agentes en esta área';
      }
      
      // Verificar conflictos cuando se avanza al paso 2 y hay fechas seleccionadas
      if (fechaInicio && fechaFin && paso === 2) {
        await verificarConflictosAgentes();
      }
    } catch (e) {
      error = 'Error al cargar los agentes';
      console.error('Error cargando agentes:', e);
    } finally {
      loading = false;
    }
  }
  
  async function verificarConflictosAgentes() {
    agentesConConflicto.clear();
    for (const agente of agentesDisponibles) {
      const tieneConflicto = await verificarDisponibilidadAgente(agente.id_agente);
      if (tieneConflicto) {
        agentesConConflicto.add(String(agente.id_agente));
      }
    }
    agentesConConflicto = new Set(agentesConConflicto);
  }

  function handleAreaChange() {
    agentesSeleccionados.clear();
    agentesSeleccionados = agentesSeleccionados;
    if (areaSeleccionada) {
      cargarAgentesDeArea();
    } else {
      agentesDisponibles = [];
    }
  }

  async function toggleAgente(agenteId) {
    const id = String(agenteId);
    
    // Si ya está seleccionado, simplemente lo deseleccionamos
    if (agentesSeleccionados.has(id)) {
      agentesSeleccionados.delete(id);
      agentesSeleccionados = new Set(agentesSeleccionados);
      return;
    }
    
    // Si no está seleccionado, verificamos que no tenga guardias en las fechas seleccionadas
    if (fechaInicio && fechaFin) {
      const tieneConflicto = await verificarDisponibilidadAgente(agenteId);
      if (tieneConflicto) {
        const agente = agentesDisponibles.find(a => String(a.id_agente) === id);
        const nombreAgente = agente ? `${agente.nombre} ${agente.apellido}` : 'Este agente';
        error = `${nombreAgente} ya tiene una guardia asignada que se superpone con las fechas seleccionadas (${fechaInicio} - ${fechaFin})`;
        mostrarToast(`⚠️ ${error}`, 'error');
        return;
      }
    }
    
    // Si no hay conflicto, lo agregamos
    agentesSeleccionados.add(id);
    agentesSeleccionados = new Set(agentesSeleccionados);
  }

  async function verificarDisponibilidadAgente(agenteId) {
    try {
      // Obtener todas las guardias del agente
      const response = await guardiasService.getGuardiasAgente(agenteId);
      const guardiasAgente = response.data?.guardias || [];
      
      // Verificar si alguna guardia se superpone con las fechas seleccionadas
      const fechaInicioSeleccionada = new Date(fechaInicio);
      const fechaFinSeleccionada = new Date(fechaFin);
      
      for (const guardia of guardiasAgente) {
        // Solo verificamos guardias activas y no canceladas
        if (guardia.activa === false || guardia.estado === 'cancelada') {
          continue;
        }
        
        const fechaGuardia = new Date(guardia.fecha);
        
        // Verificar si la fecha de la guardia existente está dentro del rango seleccionado
        if (fechaGuardia >= fechaInicioSeleccionada && fechaGuardia <= fechaFinSeleccionada) {
          console.log('Conflicto encontrado:', guardia);
          return true;
        }
      }
      
      return false;
    } catch (e) {
      console.error('Error verificando disponibilidad:', e);
      // En caso de error, permitimos la selección pero mostramos advertencia
      return false;
    }
  }

  function validarPaso1() {
    if (!nombre.trim()) {
      error = 'El nombre de la guardia es obligatorio';
      return false;
    }
    if (!areaSeleccionada) {
      error = 'Debe seleccionar un área';
      return false;
    }
    if (!fechaInicio) {
      error = 'La fecha de inicio es obligatoria';
      return false;
    }
    if (!fechaFin) {
      error = 'La fecha de fin es obligatoria';
      return false;
    }
    
    // Validar que la fecha de inicio no sea anterior a hoy
    const fechaInicioDate = new Date(fechaInicio);
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    
    if (fechaInicioDate < hoy) {
      error = 'La fecha de inicio no puede ser anterior a hoy';
      return false;
    }
    
    if (!horaInicio || !horaFin) {
      error = 'Las horas de inicio y fin son obligatorias';
      return false;
    }
    
    // Validar que fecha fin no sea anterior a fecha inicio
    const fechaFinDate = new Date(fechaFin);
    if (fechaFinDate < fechaInicioDate) {
      error = 'La fecha de fin no puede ser anterior a la fecha de inicio';
      return false;
    }
    
    // Validar que si es el mismo día, la hora fin sea diferente a la hora inicio
    if (fechaInicio === fechaFin && horaInicio === horaFin) {
      error = 'Si la guardia es en el mismo día, las horas de inicio y fin no pueden ser iguales';
      return false;
    }
    
    // Si es el mismo día, validar que hora fin sea posterior a hora inicio
    if (fechaInicio === fechaFin && horaInicio >= horaFin) {
      error = 'Si la guardia es en el mismo día, la hora de fin debe ser posterior a la hora de inicio';
      return false;
    }
    
    return true;
  }

  async function avanzarPaso2() {
    if (!validarPaso1()) return;
    error = '';
    paso = 2;
    // Verificar conflictos de los agentes con las fechas seleccionadas
    await verificarConflictosAgentes();
  }

  function volverPaso1() {
    paso = 1;
    error = '';
  }

  async function guardarGuardia() {
    if (agentesSeleccionados.size === 0) {
      error = 'Debe seleccionar al menos un agente';
      return;
    }

    // Verificar disponibilidad de todos los agentes seleccionados antes de guardar
    const agentesConConflicto = [];
    for (const agenteId of agentesSeleccionados) {
      const tieneConflicto = await verificarDisponibilidadAgente(agenteId);
      if (tieneConflicto) {
        const agente = agentesDisponibles.find(a => String(a.id_agente) === agenteId);
        if (agente) {
          agentesConConflicto.push(`${agente.nombre} ${agente.apellido}`);
        }
      }
    }
    
    if (agentesConConflicto.length > 0) {
      error = `Los siguientes agentes ya tienen guardias asignadas en estas fechas: ${agentesConConflicto.join(', ')}`;
      mostrarToast('⚠️ Algunos agentes tienen conflictos de horarios', 'error');
      return;
    }

    // Confirmación antes de guardar
    const infoMultiDia = esGuardiaMultiDia ? ` (${diasGuardia} días)` : '';
    const confirmar = confirm(
      `¿Confirmar la creación de la guardia?\n\n` +
      `Guardia: ${nombre}\n` +
      `Área: ${nombreArea(areaSeleccionada)}\n` +
      `Inicio: ${fechaInicio} a las ${horaInicio}\n` +
      `Fin: ${fechaFin} a las ${horaFin}\n` +
      `Duración: ${duracionGuardia}${infoMultiDia}\n` +
      `Agentes: ${agentesSeleccionados.size}\n\n` +
      `Se creará el cronograma y se asignará la guardia a los agentes seleccionados. Esta acción quedará registrada en auditoría.`
    );
    
    if (!confirmar) return;

    try {
      loading = true;
      error = '';

      // Preparar observaciones con información de fecha fin si es multi-día
      let observacionesCompletas = observaciones || '';
      if (esGuardiaMultiDia) {
        const infoMultiDia = `\n[Guardia de ${diasGuardia} días: Inicio ${fechaInicio} ${horaInicio} - Fin ${fechaFin} ${horaFin}]`;
        observacionesCompletas = observacionesCompletas ? observacionesCompletas + infoMultiDia : infoMultiDia.trim();
      }

      const payload = {
        nombre: nombre,
        tipo: tipo,
        id_area: areaSeleccionada,
        fecha: fechaInicio, // Fecha de inicio de la guardia
        hora_inicio: horaInicio,
        hora_fin: horaFin,
        observaciones: observacionesCompletas,
        agentes: Array.from(agentesSeleccionados).map(id => {
          const agente = agentesDisponibles.find(a => String(a.id_agente) === id);
          return {
            id_agente: agente.id_agente
          };
        })
      };

      const response = await guardiasService.crearGuardia(payload);

      const mensaje = response.data?.mensaje || 'Guardia creada exitosamente';
      const guardiasCreadas = response.data?.guardias_creadas || agentesSeleccionados.size;
      const cronogramaId = response.data?.cronograma_id;
      
      // Obtener información del cronograma creado para saber el estado
      let estadoMensaje = '';
      let estadoIcono = '';
      try {
        if (cronogramaId) {
          const cronogramaResponse = await guardiasService.getCronograma(cronogramaId);
          const cronograma = cronogramaResponse.data;
          
          if (cronograma.estado === 'aprobada') {
            estadoIcono = '🎉';
            estadoMensaje = '\n\nEstado: Auto-aprobada\nComo tienes rol de Administrador, la guardia fue aprobada automáticamente y está lista para ser publicada.';
          } else if (cronograma.estado === 'pendiente') {
            estadoIcono = '⏳';
            const rolesAprobadores = cronograma.puede_aprobar_rol?.join(', ') || 'superior';
            estadoMensaje = `\n\nEstado: Pendiente de aprobación\nRequiere aprobación de: ${rolesAprobadores}\nPodrá ser aprobada desde la página de Aprobaciones.`;
          } else if (cronograma.estado === 'generada') {
            estadoIcono = '📋';
            estadoMensaje = '\n\nEstado: Generada\nLa guardia ha sido creada y registrada exitosamente.';
          }
        }
      } catch (e) {
        console.log('No se pudo obtener estado del cronograma:', e);
        estadoIcono = '✅';
      }
      
      success = `${estadoIcono} ${mensaje}\n\nAgentes asignados: ${guardiasCreadas}${estadoMensaje}\n\nLos cambios han sido registrados en auditoría.`;
      mostrarToast('✅ Guardia creada y registrada exitosamente', 'success');

      setTimeout(() => {
        goto('/paneladmin/guardias');
      }, 5000);

    } catch (e) {
      const mensaje = e?.response?.data?.detail || e?.response?.data?.error || 'Error al crear la guardia';
      error = mensaje;
      mostrarToast(mensaje, 'error');
      console.error('Error completo:', e.response || e);
    } finally {
      loading = false;
    }
  }

  function mostrarToast(mensaje, tipo = 'success') {
    toastMensaje = mensaje;
    toastTipo = tipo;
    toastVisible = true;
    setTimeout(() => {
      toastVisible = false;
    }, 3000);
  }

  function cancelar() {
    goto('/paneladmin/guardias');
  }

  const nombreArea = (areaId) => {
    const area = areas.find(a => a.id_area === areaId);
    return area ? area.nombre : '';
  };

  // Calcular la duración de la guardia en días y horas
  $: duracionGuardia = (() => {
    if (!fechaInicio || !fechaFin || !horaInicio || !horaFin) return '';
    
    try {
      // Crear objetos Date completos con fecha y hora
      const [horaI, minI] = horaInicio.split(':').map(Number);
      const [horaF, minF] = horaFin.split(':').map(Number);
      
      const inicio = new Date(fechaInicio);
      inicio.setHours(horaI, minI, 0, 0);
      
      const fin = new Date(fechaFin);
      fin.setHours(horaF, minF, 0, 0);
      
      // Calcular diferencia en minutos
      const diffMs = fin - inicio;
      if (diffMs <= 0) return 'Inválido';
      
      const totalMinutos = Math.floor(diffMs / (1000 * 60));
      const dias = Math.floor(totalMinutos / (24 * 60));
      const horas = Math.floor((totalMinutos % (24 * 60)) / 60);
      const minutos = totalMinutos % 60;
      
      let resultado = '';
      if (dias > 0) resultado += `${dias}d `;
      if (horas > 0) resultado += `${horas}h `;
      if (minutos > 0) resultado += `${minutos}min`;
      
      return resultado.trim() || '0min';
    } catch (e) {
      return '';
    }
  })();
  
  // Verificar si la guardia es de múltiples días
  $: esGuardiaMultiDia = fechaInicio && fechaFin && fechaInicio !== fechaFin;
  
  // Calcular cuántos días abarca la guardia
  $: diasGuardia = (() => {
    if (!fechaInicio || !fechaFin) return 0;
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    const diffTime = fin - inicio;
    return Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1;
  })();
</script>

<section class="guardias-wrap">
  <header class="head">
    <h1>Crear Nueva Guardia</h1>
    <p class="subtitle">Paso {paso} de 2 • Los cambios se aplicarán al hacer clic en "Guardar Guardia"</p>
  </header>

  {#if error}
    <div class="alert alert-error" transition:fade>{error}</div>
  {/if}

  {#if success}
    <div class="alert alert-success" transition:fade>{success}</div>
  {/if}

  {#if paso === 1}
    <div class="panel card">
      <h2>Datos de la Guardia</h2>
      
      <div class="form-grid">
        <div class="campo">
          <label for="nombre">Nombre de la Guardia *</label>
          <input 
            class="input"
            id="nombre" 
            type="text"
            bind:value={nombre}
            placeholder="Ej: Guardia de Emergencias Diciembre"
            disabled={loading}
          />
        </div>

        <div class="campo">
          <label for="tipo">Tipo</label>
          <select class="input" id="tipo" bind:value={tipo} disabled={loading}>
            <option value="regular">Regular</option>
            <option value="especial">Especial</option>
            <option value="feriado">Feriado</option>
            <option value="emergencia">Emergencia</option>
          </select>
        </div>

        <div class="campo campo-full">
          <label for="area">Área / Dirección *</label>
          <select 
            class="input"
            id="area"
            bind:value={areaSeleccionada}
            on:change={handleAreaChange}
            disabled={loading}
          >
            <option value={null}>Seleccione un área</option>
            {#each areas as area}
              <option value={area.id_area}>{area.nombre}</option>
            {/each}
          </select>
        </div>

        <div class="campo">
          <label for="fechaInicio">Fecha Inicio *</label>
          <input 
            class="input"
            id="fechaInicio" 
            type="date"
            bind:value={fechaInicio}
            disabled={loading}
          />
        </div>

        <div class="campo">
          <label for="horaInicio">Hora Inicio *</label>
          <input 
            class="input"
            id="horaInicio" 
            type="time"
            bind:value={horaInicio}
            disabled={loading}
          />
        </div>

        <div class="campo">
          <label for="fechaFin">Fecha Fin *</label>
          <input 
            class="input"
            id="fechaFin" 
            type="date"
            bind:value={fechaFin}
            disabled={loading}
            min={fechaInicio}
          />
        </div>

        <div class="campo">
          <label for="horaFin">Hora Fin *</label>
          <input 
            class="input"
            id="horaFin" 
            type="time"
            bind:value={horaFin}
            disabled={loading}
          />
        </div>

        {#if fechaInicio && fechaFin && horaInicio && horaFin && duracionGuardia}
          <div class="campo campo-full">
            <div class="info-duracion">
              <strong>Duración de la guardia:</strong> {duracionGuardia}
              {#if esGuardiaMultiDia}
                <span class="badge-multidia">📅 {diasGuardia} día(s)</span>
              {/if}
            </div>
          </div>
        {/if}

        <div class="campo campo-full">
          <label for="observaciones">Observaciones</label>
          <textarea 
            class="input textarea"
            id="observaciones" 
            bind:value={observaciones}
            placeholder="Información adicional sobre la guardia... (Ej: turnos especiales, instrucciones, etc.)"
            rows="3"
            disabled={loading}
          ></textarea>
          {#if esGuardiaMultiDia}
            <span class="campo-ayuda" style="color: #64748b;">
              💡 Tip: Esta guardia abarca múltiples días. Podés agregar detalles relevantes aquí.
            </span>
          {/if}
        </div>
      </div>

      <div class="acciones">
        <button class="btn btn-secondary" on:click={cancelar} disabled={loading}>
          Cancelar
        </button>
        <button class="btn btn-primary" on:click={avanzarPaso2} disabled={loading}>
          Siguiente →
        </button>
      </div>
    </div>

  {:else if paso === 2}
    <div class="panel card">
      <h2>Seleccionar Agentes</h2>
      <p class="card-description">
        Seleccioná los agentes del área que participarán en esta guardia. 
      </p>
      
      <div class="resumen-guardia">
        <div><strong>Guardia:</strong> {nombre}</div>
        <div><strong>Área:</strong> {nombreArea(areaSeleccionada)}</div>
        <div><strong>Inicio:</strong> {fechaInicio} a las {horaInicio}</div>
        <div>
          <strong>Fin:</strong> {fechaFin} a las {horaFin}
          {#if esGuardiaMultiDia}
            <span class="badge-nocturna-small">📅 {diasGuardia} día(s)</span>
          {/if}
        </div>
        {#if duracionGuardia}
          <div class="resumen-duracion"><strong>Duración total:</strong> {duracionGuardia}</div>
        {/if}
      </div>

      {#if loading}
        <div class="placeholder">
          <div class="placeholder-icon">⏳</div>
          <div class="placeholder-title">Cargando agentes...</div>
        </div>
      {:else if agentesDisponibles.length === 0}
        <div class="placeholder">
          <div class="placeholder-icon">👥</div>
          <div class="placeholder-title">No hay agentes activos en esta área</div>
          <div class="placeholder-text">Verificá que el área tenga agentes asignados y que estén activos en el sistema.</div>
        </div>
      {:else}
        <div class="agentes-lista">
          <p class="info-text">
            <strong>{agentesDisponibles.length}</strong> agente(s) activo(s) en esta área • <strong>{agentesSeleccionados.size}</strong> seleccionado(s)
            {#if agentesConConflicto.size > 0}
              <span class="advertencia-conflictos">⚠️ {agentesConConflicto.size} con guardias existentes</span>
            {/if}
          </p>
          {#each agentesDisponibles as agente}
            {@const tieneConflicto = agentesConConflicto.has(String(agente.id_agente))}
            <label class="agente-item" class:tiene-conflicto={tieneConflicto}>
              <input 
                type="checkbox" 
                checked={agentesSeleccionados.has(String(agente.id_agente))}
                on:change={() => toggleAgente(agente.id_agente)}
                disabled={loading}
              />
              <div class="agente-info">
                <div class="agente-nombre">
                  {agente.apellido}, {agente.nombre}
                  {#if tieneConflicto}
                    <span class="badge-conflicto" title="Este agente ya tiene una guardia asignada en estas fechas">
                      ⚠️ Con guardia
                    </span>
                  {/if}
                </div>
                <div class="agente-datos">
                  <span>Legajo: {agente.legajo}</span>
                  {#if agente.area_nombre}
                    <span>• {agente.area_nombre}</span>
                  {/if}
                </div>
              </div>
            </label>
          {/each}
        </div>
      {/if}

      <div class="acciones">
        <button class="btn btn-secondary" on:click={volverPaso1} disabled={loading}>
          ← Volver
        </button>
        <button 
          class="btn btn-primary" 
          on:click={guardarGuardia} 
          disabled={loading || agentesSeleccionados.size === 0}
        >
          {loading ? 'Guardando...' : 'Guardar Guardia'}
        </button>
      </div>
    </div>
  {/if}
</section>

{#if toastVisible}
  <div 
    class="toast toast-{toastTipo}" 
    in:fly={{ y: -20, duration: 200 }} 
    out:fade={{ duration: 300 }}
  >
    {#if toastTipo === 'success'}
      ✅ {toastMensaje}
    {:else}
      ❌ {toastMensaje}
    {/if}
  </div>
{/if}

<style>
.guardias-wrap {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: Verdana, Geneva, Tahoma, sans-serif;
}

.head {
  margin-bottom: 1.5rem;
}

.head h1 {
  font-size: 1.8rem;
  margin: 0 0 0.25rem 0;
  color: #1e40af;
}

.head .subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
}

.card h2 {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.card-description {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
  line-height: 1.5;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.campo {
  display: flex;
  flex-direction: column;
}

.campo-full {
  grid-column: 1 / -1;
}

.campo label {
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.campo-ayuda {
  font-size: 0.85rem;
  margin-top: 0.35rem;
  display: block;
}

.campo-info {
  color: #1e40af;
  font-weight: 500;
}

.input {
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s, background 0.2s;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  background: #fff;
}

.input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.textarea {
  resize: vertical;
  min-height: 80px;
}

select.input {
  cursor: pointer;
}

.resumen-guardia {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.resumen-guardia div {
  color: #1e293b;
  font-size: 0.9rem;
}

.resumen-duracion {
  grid-column: 1 / -1;
  padding-top: 0.5rem;
  border-top: 1px solid #bfdbfe;
}

.info-duracion {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.badge-nocturna {
  background: #312e81;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-nocturna-small {
  background: #312e81;
  color: white;
  padding: 0.15rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  margin-left: 0.5rem;
  display: inline-block;
}

.badge-multidia {
  background: #0891b2;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-text {
  color: #475569;
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
  padding: 0.75rem;
  background: #f1f5f9;
  border-radius: 6px;
}

.agentes-lista {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.5rem;
  margin-bottom: 1.5rem;
}

.agente-item {
  display: grid;
  grid-template-columns: 24px 1fr;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  align-items: start;
}

.agente-item:hover {
  background: #f8fafc;
}

.agente-item:has(input:checked) {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  margin: -1px;
}

.agente-item.tiene-conflicto {
  background: #fef2f2;
  border: 1px solid #fecaca;
  opacity: 0.8;
}

.agente-item.tiene-conflicto:hover {
  background: #fee2e2;
}

.agente-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  margin-top: 2px;
}

.agente-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.agente-nombre {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge-conflicto {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.advertencia-conflictos {
  color: #d97706;
  font-weight: 600;
  font-size: 0.85rem;
  margin-left: 1rem;
}

.agente-datos {
  color: #64748b;
  font-size: 0.85rem;
}

.agente-datos span {
  margin-right: 0.5rem;
}

.acciones {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1e40af;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1e3a8a;
}

.btn-secondary {
  background: #e5e7eb;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background: #d1d5db;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert {
  padding: 1rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.alert-error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
  white-space: pre-line;
  line-height: 1.6;
}

.alert-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
  line-height: 1.6;
  white-space: pre-line;
  font-size: 0.95rem;
}

.placeholder {
  text-align: center;
  color: #64748b;
  padding: 3rem 2rem;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.placeholder-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.5rem;
}

.placeholder-text {
  font-size: 0.9rem;
  color: #64748b;
  max-width: 400px;
  margin: 0 auto;
}

.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  font-size: 0.95rem;
  font-weight: 500;
  z-index: 9999;
  min-width: 260px;
}

.toast-success {
  background: #22c55e;
  color: white;
}

.toast-error {
  background: #ef4444;
  color: white;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .resumen-guardia {
    grid-template-columns: 1fr;
  }
  
  .acciones {
    flex-direction: column;
  }
}
</style>
