<script>
  import { createEventDispatcher, onMount } from "svelte";
  import { fade, scale } from "svelte/transition";
  import { guardiasService, personasService } from "$lib/services.js";

  export let token;
  export let areas = []; // Passed from parent if available, or empty
  
  const dispatch = createEventDispatcher();
  
  // Local state
  let cargando = false;
  let error = null;
  let successMessage = null;

  // Form selections
  let areaSeleccionada = "";
  let agenteSeleccionado = "";
  let guardiaSeleccionada = "";
  
  // Data lists
  let agentes = [];
  let guardias = [];
  
  let cargandoAgentes = false;
  let cargandoGuardias = false;

  // New Compensation Data
  let nuevaCompensacion = {
    id_guardia: "",
    hora_fin_real: "",
    motivo: "emergencia",
    descripcion_motivo: "",
    numero_acta: "",
    solicitado_por: "",
  };

  const motivosCompensacion = [
    { value: "siniestro", label: "Siniestro/Accidente" },
    { value: "emergencia", label: "Emergencia Operativa" },
    { value: "operativo", label: "Operativo Especial" },
    { value: "refuerzo", label: "Refuerzo de Seguridad" },
    { value: "otro", label: "Otro Motivo" },
  ];

  // Helper functions
  function formatearFecha(fecha) {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-AR");
  }

  function formatearHora(hora) {
    if (!hora) return "-";
    return hora.slice(0, 5); // HH:MM
  }

  function cerrar() {
    dispatch("close");
  }

  // Loaders
  async function cargarAgentes() {
    if (!areaSeleccionada) {
      agentes = [];
      return;
    }

    cargandoAgentes = true;
    try {
      const response = await personasService.getAgentesByArea(
        areaSeleccionada,
        token,
      );
      
      let datos = [];
      if (response.data?.data?.results) datos = response.data.data.results;
      else if (response.data?.results) datos = response.data.results;
      else if (response.success && response.data?.results) datos = response.data.results;
      else if (response.results) datos = response.results;
      else if (Array.isArray(response.data)) datos = response.data;
      else if (Array.isArray(response)) datos = response;
      
      agentes = datos;
      agenteSeleccionado = "";
      guardias = [];
      guardiaSeleccionada = "";
    } catch (err) {
      console.error("Error cargando agentes:", err);
      agentes = [];
    } finally {
      cargandoAgentes = false;
    }
  }

  async function cargarGuardias() {
    if (!agenteSeleccionado) {
      guardias = [];
      return;
    }

    cargandoGuardias = true;
    try {
      const response = await guardiasService.getGuardiasAgente(
        agenteSeleccionado,
        token,
      );
      
      let datos = [];
      if (response.guardias && Array.isArray(response.guardias)) datos = response.guardias;
      else if (response.data?.data?.guardias) datos = response.data.data.guardias;
      else if (response.data?.data?.results) datos = response.data.data.results;
      else if (response.data?.guardias) datos = response.data.guardias;
      else if (response.data?.results) datos = response.data.results;
      else if (response.success && response.data?.guardias) datos = response.data.guardias;
      else if (response.success && response.data?.results) datos = response.data.results;
      else if (response.results) datos = response.results;
      else if (Array.isArray(response.data)) datos = response.data;
      else if (Array.isArray(response)) datos = response;

      guardias = datos;
      await filtrarGuardiasConCompensacion();
      guardiaSeleccionada = "";
    } catch (err) {
      console.error("Error cargando guardias:", err);
      guardias = [];
    } finally {
      cargandoGuardias = false;
    }
  }

  async function filtrarGuardiasConCompensacion() {
    if (guardias.length === 0) return;

    try {
      const compensacionesResponse = await guardiasService.getCompensaciones("", token);
      
      let todasCompensaciones = [];
      if (compensacionesResponse.data?.data?.results) todasCompensaciones = compensacionesResponse.data.data.results;
      else if (compensacionesResponse.data?.results) todasCompensaciones = compensacionesResponse.data.results;
      else if (Array.isArray(compensacionesResponse.data)) todasCompensaciones = compensacionesResponse.data;

      if (!Array.isArray(todasCompensaciones)) return;

      const guardiasConCompensacion = todasCompensaciones
        .map((comp) => comp.id_guardia?.id_guardia || comp.id_guardia)
        .filter(Boolean);

      guardias = guardias.filter(
        (guardia) => !guardiasConCompensacion.includes(guardia.id_guardia)
      );
    } catch (err) {
      console.error("Error verificando compensaciones existentes:", err);
    }
  }

  // Reactive loaders
  $: if (areaSeleccionada) cargarAgentes();
  $: if (agenteSeleccionado) cargarGuardias();

  // Create action
  async function crearCompensacion() {
    if (!guardiaSeleccionada || !nuevaCompensacion.hora_fin_real || !nuevaCompensacion.descripcion_motivo) {
      error = "Por favor complete todos los campos obligatorios";
      return;
    }

    // Validate times
    const guardiaData = guardias.find((g) => g.id_guardia == guardiaSeleccionada);
    if (guardiaData && guardiaData.hora_fin) {
      const horaFinProgramada = guardiaData.hora_fin.slice(0, 5);
      const horaFinReal = nuevaCompensacion.hora_fin_real.slice(0, 5);

      if (horaFinProgramada === horaFinReal) {
        error = "La hora de finalización real no puede ser igual a la hora programada. Debe haber horas extra.";
        return;
      }
    }

    cargando = true;
    error = null;

    try {
      const compensacionData = {
        hora_fin_real: nuevaCompensacion.hora_fin_real,
        motivo: nuevaCompensacion.motivo,
        descripcion_motivo: nuevaCompensacion.descripcion_motivo,
        numero_acta: nuevaCompensacion.numero_acta || "",
        solicitado_por: parseInt(nuevaCompensacion.solicitado_por || agenteSeleccionado),
      };

      await guardiasService.createCompensacionFromGuardia(
        guardiaSeleccionada,
        compensacionData,
        token,
      );

      successMessage = "Compensación creada exitosamente";
      setTimeout(() => {
          dispatch("success");
          cerrar();
      }, 1500);

    } catch (err) {
      console.error("Error creating compensation:", err);
      error = err.response?.data?.message || err.message || "Error al crear compensación";
    } finally {
      cargando = false;
    }
  }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="modal-overlay" on:click={cerrar} transition:fade={{ duration: 200 }}>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div
    class="modal-content"
    on:click|stopPropagation
    transition:scale={{ duration: 200, start: 0.95 }}
  >
    <div class="modal-header">
      <h3>Nueva Compensación por Horas Extra</h3>
      <button class="btn-close" on:click={cerrar}>&times;</button>
    </div>

    <!-- Scrollable Body for the form -->
    <div class="modal-body-scroll">
        <form on:submit|preventDefault={crearCompensacion}>
            {#if error}
                <div class="alert alert-error">⚠️ {error}</div>
            {/if}
            {#if successMessage}
                <div class="alert alert-success">✅ {successMessage}</div>
            {/if}

            <div class="paso-selector">
                <h3>Paso 1: Seleccionar Área</h3>
                <div class="campo">
                    <label for="area">Área *</label>
                    <select bind:value={areaSeleccionada} required>
                        <option value="">Seleccione un área</option>
                        {#each areas as area}
                            <option value={area.id_area}>{area.nombre}</option>
                        {/each}
                    </select>
                </div>
            </div>

            {#if areaSeleccionada}
                <div class="paso-selector" transition:fade>
                    <h3>Paso 2: Seleccionar Agente</h3>
                    <div class="campo">
                        <label for="agente">Agente *</label>
                        <select bind:value={agenteSeleccionado} required disabled={cargandoAgentes}>
                            <option value="">{cargandoAgentes ? "Cargando..." : "Seleccione un agente"}</option>
                            {#each agentes as agente}
                                <option value={agente.id_agente}>{agente.apellido}, {agente.nombre} (Leg: {agente.legajo})</option>
                            {/each}
                        </select>
                    </div>
                </div>
            {/if}

            {#if agenteSeleccionado}
                <div class="paso-selector" transition:fade>
                    <h3>Paso 3: Seleccionar Guardia</h3>
                    <div class="campo">
                        <label for="guardia">Guardia que Necesita Compensación *</label>
                        <select bind:value={guardiaSeleccionada} required disabled={cargandoGuardias}>
                            <option value="">{cargandoGuardias ? "Cargando..." : "Seleccione una guardia"}</option>
                            {#each guardias as guardia}
                                <option value={guardia.id_guardia}>
                                    {formatearFecha(guardia.fecha)} - {formatearHora(guardia.hora_inicio)} a {formatearHora(guardia.hora_fin)}
                                    {#if guardia.cronograma_nombre}({guardia.cronograma_nombre}){/if}
                                </option>
                            {/each}
                        </select>
                        {#if guardias.length === 0 && !cargandoGuardias}
                            <small class="text-warning">Este agente no tiene guardias registradas recientes sin compensar</small>
                        {/if}
                    </div>
                </div>
            {/if}

            {#if guardiaSeleccionada}
                <div class="paso-selector" transition:fade>
                    <h3>Paso 4: Detalles de la Compensación</h3>
                    
                    <div class="campo">
                        <label for="hora_fin_real">Hora Real de Finalización *</label>
                        <input type="time" bind:value={nuevaCompensacion.hora_fin_real} required />
                        <small>Hora en que realmente terminó el servicio (debe exceder el horario)</small>
                    </div>

                    <div class="campo">
                        <label for="motivo">Motivo de la Emergencia *</label>
                        <select bind:value={nuevaCompensacion.motivo} required>
                            {#each motivosCompensacion as motivo}
                                <option value={motivo.value}>{motivo.label}</option>
                            {/each}
                        </select>
                    </div>

                    <div class="campo">
                        <label for="descripcion_motivo">Descripción del Motivo *</label>
                        <textarea 
                            bind:value={nuevaCompensacion.descripcion_motivo} 
                            required rows="3" 
                            placeholder="Describa detalladamente la situación...">
                        </textarea>
                    </div>

                    <div class="campo">
                        <label for="numero_acta">Número de Acta (Opcional)</label>
                        <input type="text" bind:value={nuevaCompensacion.numero_acta} placeholder="Si existe un expediente" />
                    </div>

                    <div class="campo">
                        <label for="solicitado_por">Solicitado por *</label>
                        <select bind:value={nuevaCompensacion.solicitado_por} required>
                            <option value="">Seleccione quién solicita</option>
                            {#if agenteSeleccionado}
                                <option value={agenteSeleccionado} selected>
                                    {agentes.find(a => a.id_agente == agenteSeleccionado)?.apellido}, 
                                    {agentes.find(a => a.id_agente == agenteSeleccionado)?.nombre} (El mismo agente)
                                </option>
                            {/if}
                            {#each agentes.filter(a => a.id_agente != agenteSeleccionado) as agente}
                                <option value={agente.id_agente}>{agente.apellido}, {agente.nombre}</option>
                            {/each}
                        </select>
                    </div>
                </div>
            {/if}
            
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" on:click={cerrar}>Cancelar</button>
                <button type="submit" class="btn btn-success" disabled={cargando}>
                    {cargando ? "Guardando..." : "Crear Compensación"}
                </button>
            </div>
        </form>
    </div>
  </div>
</div>

<style>
  /* Modal Overlay & Content */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal-content {
    background: white;
    border-radius: 16px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    border: none;
  }

  /* Header */
  .modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px 16px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
  }

  .modal-header h3 {
    margin: 0;
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
  }

  .btn-close {
    background: none;
    border: none;
    color: white;
    font-size: 25px;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.3s ease;
  }
  .btn-close:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
  }

  /* Scrollable container for body */
  .modal-body-scroll {
    overflow-y: auto;
    padding: 2rem;
    flex-grow: 1;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .modal-body-scroll::-webkit-scrollbar { display: none; }

  /* Form Elements */
  .paso-selector {
    margin-bottom: 24px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
  }
  .paso-selector h3 {
    margin: 0 0 12px 0;
    color: #1e40af;
    font-size: 16px;
    font-weight: 600;
  }

  .campo { margin-bottom: 20px; }
  
  .campo label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    color: #374151;
    font-size: 14px;
  }

  .campo input, .campo select, .campo textarea {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.2s;
    font-family: inherit;
    box-sizing: border-box;
  }

  .campo input:focus, .campo select:focus, .campo textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .text-warning { color: #d97706; font-size: 0.85rem; padding-top: 4px; display: block; }
  small { color: #6b7280; font-size: 12px; margin-top: 4px; display: block; }

  /* Alerts */
  .alert {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-weight: 500;
  }
  .alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
  .alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }

  /* Footer */
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }

  /* Buttons */
  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }
  .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

  .btn-secondary { background: #6c757d; color: white; }
  .btn-secondary:hover:not(:disabled) { background: #5a6268; transform: translateY(-2px); }

  .btn-success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; }
  .btn-success:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4); }
</style>
