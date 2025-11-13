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
  let fecha = '';
  let horaInicio = '08:00';
  let horaFin = '16:00';
  let observaciones = '';

  let areas = [];
  let agentesDisponibles = [];
  let agentesSeleccionados = new Set();

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
      areas = Array.isArray(response.data) ? response.data : [];
    } catch (e) {
      error = 'Error al cargar las áreas';
      console.error(e);
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
      const todosAgentes = Array.isArray(response.data) ? response.data : [];

      agentesDisponibles = todosAgentes.filter(agente => {
        if (agente.areas && Array.isArray(agente.areas)) {
          return agente.areas.some(a => a.id === areaSeleccionada);
        }
        return false;
      });

      if (agentesDisponibles.length === 0) {
        error = 'No hay agentes en esta área';
      }
    } catch (e) {
      error = 'Error al cargar los agentes';
      console.error(e);
    } finally {
      loading = false;
    }
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

  function toggleAgente(agenteId) {
    const id = String(agenteId);
    if (agentesSeleccionados.has(id)) {
      agentesSeleccionados.delete(id);
    } else {
      agentesSeleccionados.add(id);
    }
    agentesSeleccionados = new Set(agentesSeleccionados);
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
    if (!fecha) {
      error = 'La fecha es obligatoria';
      return false;
    }
    if (!horaInicio || !horaFin) {
      error = 'Las horas de inicio y fin son obligatorias';
      return false;
    }
    if (horaInicio >= horaFin) {
      error = 'La hora de inicio debe ser anterior a la hora de fin';
      return false;
    }
    return true;
  }

  function avanzarPaso2() {
    if (!validarPaso1()) return;
    error = '';
    paso = 2;
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

    try {
      loading = true;
      error = '';

      const payload = {
        nombre: nombre,
        tipo: tipo,
        id_area: areaSeleccionada,
        fecha: fecha,
        hora_inicio: horaInicio,
        hora_fin: horaFin,
        observaciones: observaciones || '',
        agentes: Array.from(agentesSeleccionados).map(id => {
          const agente = agentesDisponibles.find(a => String(a.id) === id);
          return {
            id_agente: agente.id,
            usuario_id: agente.usuario_id
          };
        })
      };

      const response = await guardiasService.crearGuardia(payload);

      success = 'Guardia creada exitosamente';
      mostrarToast('Guardia creada exitosamente', 'success');

      setTimeout(() => {
        goto('/paneladmin/guardias');
      }, 2000);

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
    const area = areas.find(a => a.id === areaId);
    return area ? area.nombre : '';
  };
</script>

<section class="guardias-wrap">
  <header class="head">
    <h1>Crear Nueva Guardia</h1>
    <p>Paso {paso} de 2</p>
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
              <option value={area.id}>{area.nombre}</option>
            {/each}
          </select>
        </div>

        <div class="campo">
          <label for="fecha">Fecha *</label>
          <input 
            class="input"
            id="fecha" 
            type="date"
            bind:value={fecha}
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
          <label for="horaFin">Hora Fin *</label>
          <input 
            class="input"
            id="horaFin" 
            type="time"
            bind:value={horaFin}
            disabled={loading}
          />
        </div>

        <div class="campo campo-full">
          <label for="observaciones">Observaciones</label>
          <textarea 
            class="input textarea"
            id="observaciones" 
            bind:value={observaciones}
            placeholder="Información adicional sobre la guardia..."
            rows="3"
            disabled={loading}
          ></textarea>
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
      
      <div class="resumen-guardia">
        <div><strong>Guardia:</strong> {nombre}</div>
        <div><strong>Área:</strong> {nombreArea(areaSeleccionada)}</div>
        <div><strong>Fecha:</strong> {fecha}</div>
        <div><strong>Horario:</strong> {horaInicio} - {horaFin}</div>
      </div>

      {#if loading}
        <div class="placeholder">Cargando agentes...</div>
      {:else if agentesDisponibles.length === 0}
        <div class="placeholder">No hay agentes disponibles en esta área</div>
      {:else}
        <div class="agentes-lista">
          <p class="info-text">
            Seleccioná los agentes que participarán en esta guardia ({agentesSeleccionados.size} seleccionados)
          </p>
          {#each agentesDisponibles as agente}
            <label class="agente-item">
              <input 
                type="checkbox" 
                checked={agentesSeleccionados.has(String(agente.id))}
                on:change={() => toggleAgente(agente.id)}
                disabled={loading}
              />
              <div class="agente-info">
                <div class="agente-nombre">{agente.apellido}, {agente.nombre}</div>
                <div class="agente-datos">
                  <span>Legajo: {agente.legajo}</span>
                  {#if agente.areas?.length}
                    <span>• {agente.areas.map(a => a.nombre).join(', ')}</span>
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

.head p {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
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
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
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
}

.alert-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.placeholder {
  text-align: center;
  color: #64748b;
  padding: 2rem;
  font-style: italic;
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
