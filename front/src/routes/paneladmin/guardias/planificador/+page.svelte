<script>
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { planificadorGuardiasController } from "$lib/paneladmin/controllers";

  // Obtener stores del controller
  const {
    loading,
    loadingAgentes, 
    error,
    success,
    paso,
    nombre,
    tipo,
    areaSeleccionada,
    fechaInicio,
    horaInicio,
    fechaFin,
    horaFin,
    observaciones,
    areas,
    agentesDisponibles,
    agentesSeleccionados,
    agentesConConflicto,
    toastVisible,
    toastMensaje,
    toastTipo,
    modoEdicion,
    cronogramaId,
  } = planificadorGuardiasController;

  let ready = false;

  onMount(async () => {
    // Verificar si viene parámetro de edición
    const urlParams = new URLSearchParams(window.location.search);
    await planificadorGuardiasController.init(urlParams);
    ready = true;
  });

  // ... (rest of script)

  // Fecha mínima: hoy
  const hoy = new Date().toISOString().split('T')[0];

  // Handlers delegados al controller
  async function handleAreaChange() {
    await planificadorGuardiasController.handleAreaChange();
  }

  async function handleFechaInicioChange(fechaInicio) {
    this.fechaFin.set(fechaInicio); 
    await planificadorGuardiasController.handleFechaHorarioChange();
  }

  async function handleFechaHorarioChange() {
    await planificadorGuardiasController.handleFechaHorarioChange();
  }

  async function handleToggleAgente(agenteId) {
    await planificadorGuardiasController.toggleAgente(agenteId);
  }

  async function handleAvanzarPaso2() {
    await planificadorGuardiasController.avanzarPaso2();
  }

  function handleVolverPaso1() {
    planificadorGuardiasController.volverPaso1();
  }

  async function handleGuardarGuardia() {
    await planificadorGuardiasController.guardarGuardia();
  }

  function handleCancelar() {
    planificadorGuardiasController.cancelar();
  }

  const nombreArea = (areaId) => {
    const area = $areas.find((a) => a.id_area === areaId);
    return area ? area.nombre : "";
  };

  // Calcular la duración de la guardia en días y horas
  $: duracionGuardia = (() => {
    if (!$fechaInicio || !$fechaFin || !$horaInicio || !$horaFin) return "";

    try {
      // Crear objetos Date completos con fecha y hora
      const [horaI, minI] = $horaInicio.split(":").map(Number);
      const [horaF, minF] = $horaFin.split(":").map(Number);

      const inicio = new Date($fechaInicio);
      inicio.setHours(horaI, minI, 0, 0);

      const fin = new Date($fechaFin);
      fin.setHours(horaF, minF, 0, 0);

      // Calcular diferencia en minutos
      const diffMs = fin - inicio;
      if (diffMs <= 0) return "Inválido";

      const totalMinutos = Math.floor(diffMs / (1000 * 60));
      const dias = Math.floor(totalMinutos / (24 * 60));
      const horas = Math.floor((totalMinutos % (24 * 60)) / 60);
      const minutos = totalMinutos % 60;

      let resultado = "";
      if (dias > 0) resultado += `${dias}d `;
      if (horas > 0) resultado += `${horas}h `;
      if (minutos > 0) resultado += `${minutos}min`;

      return resultado.trim() || "0min";
    } catch (e) {
      return "";
    }
  })();

  // Verificar si la guardia es de múltiples días
  $: esGuardiaMultiDia =
    $fechaInicio && $fechaFin && $fechaInicio !== $fechaFin;

  // Calcular cuántos días abarca la guardia
  $: diasGuardia = (() => {
    if (!$fechaInicio || !$fechaFin) return 0;
    const inicio = new Date($fechaInicio);
    const fin = new Date($fechaFin);
    const diffTime = fin - inicio;
    return Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1;
  })();

  // Validar fechas y horarios
  $: errorFechaHora = (() => {
    if (!$fechaInicio || !$fechaFin || !$horaInicio || !$horaFin) return null;

    // Si fecha inicio es posterior a fecha fin
    if ($fechaInicio > $fechaFin) {
      return '⚠️ La fecha de inicio no puede ser posterior a la fecha de fin';
    }

    // Si es el mismo día, verificar que hora inicio no sea mayor que hora fin
    if ($fechaInicio === $fechaFin) {
      const [horaI, minI] = $horaInicio.split(':').map(Number);
      const [horaF, minF] = $horaFin.split(':').map(Number);
      const minutosInicio = horaI * 60 + minI;
      const minutosFin = horaF * 60 + minF;
      
      if (minutosInicio >= minutosFin) {
        return '⚠️ En el mismo día, la hora de inicio debe ser anterior a la hora de fin';
      }
    }

    return null;
  })();

  // Validar que todos los campos obligatorios estén completos
  $: puedeAvanzar = $nombre && $areaSeleccionada && $fechaInicio && $horaInicio && $horaFin && !errorFechaHora;
</script>

<section class="guardias-wrap">
  {#if ready}
    <!-- Content logic -->
    <header class="head">
      <h1>{$modoEdicion ? "✏️ Editar Guardia" : "➕ Crear Nueva Guardia"}</h1>
      <p class="subtitle">
        {#if $modoEdicion}
          Editando cronograma #{$cronogramaId} •
        {/if}
        Paso {$paso} de 2 • Los cambios se aplicarán al hacer clic en "{$modoEdicion
          ? "Actualizar"
          : "Guardar"} Guardia"
      </p>
    </header>

    {#if $error}
      <div class="alert alert-error" transition:fade>{$error}</div>
    {/if}

    {#if $success}
      <div class="alert alert-success" transition:fade>{$success}</div>
    {/if}

    {#if $paso === 1}
      <div class="panel card" class:loading={$loading}>
        {#if $loading}
          <div class="loading-overlay" transition:fade={{ duration: 200 }}>
            <div class="spinner"></div>
            <p style="margin-top: 1rem; color: #64748b; font-weight: 500;">Cargando...</p>
          </div>
        {/if}

         <h2>Datos de la Guardia</h2>

         <div class="form-grid" class:disabled={$loading}>
            <div class="campo campo-nombre">
              <label for="nombre">Nombre de la Guardia *</label>
              <input
                class="input"
                id="nombre"
                type="text"
                bind:value={$nombre}
                placeholder="Ej: Guardia de Emergencias Diciembre"
                disabled={$loading}
              />
            </div>

            <div class="campo">
              <label for="tipo">Tipo</label>
              <select
                class="input"
                id="tipo"
                bind:value={$tipo}
                disabled={$loading}
              >
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
                bind:value={$areaSeleccionada}
                on:change={handleAreaChange}
                disabled={$loading}
              >
                <option value="">Seleccione un área</option>
                {#each $areas as area}
                  <option value={area.id_area}>{area.nombre}</option>
                {/each}
              </select>
            </div>

        <div class="campo campo-full">
          <label for="fechaInicio">Fecha Guardia *</label>
          <input
            class="input"
            id="fechaInicio"
            type="date"
            bind:value={$fechaInicio}
            on:change={handleFechaInicioChange($fechaInicio)}
            min={hoy}
            disabled={$loading}
          />
        </div>

        <!-- <div class="campo">
          <label for="fechaFin">Fecha Fin *</label>
          <input
            class="input"
            id="fechaFin"
            type="date"
            bind:value={$fechaFin}
            on:change={handleFechaHorarioChange}
            disabled={$loading}
            min={$fechaInicio}
          />
        </div> -->

        <div class="campo">
          <label for="horaInicio">Hora Inicio *</label>
          <input
            class="input"
            id="horaInicio"
            type="time"
            bind:value={$horaInicio}
            on:change={handleFechaHorarioChange}
            disabled={$loading}
          />
        </div>

        <div class="campo">
          <label for="horaFin">Hora Fin *</label>
          <input
            class="input"
            id="horaFin"
            type="time"
            bind:value={$horaFin}
            on:change={handleFechaHorarioChange}
            disabled={$loading}
          />
        </div>

             {#if $fechaInicio && $fechaFin && $horaInicio && $horaFin && duracionGuardia}
              <div class="campo campo-full">
                <div class="info-duracion">
                  <strong>Duración de la guardia:</strong>
                  {duracionGuardia}
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
                bind:value={$observaciones}
                placeholder="Información adicional sobre la guardia... (Ej: turnos especiales, instrucciones, etc.)"
                rows="3"
                disabled={$loading}
              ></textarea>
              {#if esGuardiaMultiDia}
                <span class="campo-ayuda" style="color: #64748b;">
                  💡 Tip: Esta guardia abarca múltiples días. Podés agregar detalles
                  relevantes aquí.
                </span>
              {/if}
            </div>
         </div>
         
         {#if errorFechaHora}
            <div class="error-mensaje">
              {errorFechaHora}
            </div>
          {/if}

         <div class="acciones">
            <button
              class="btn btn-secondary"
              on:click={handleCancelar}
              disabled={$loading}
            >
              Cancelar
            </button>
            <button
              class="btn btn-primary"
              on:click={handleAvanzarPaso2}
              disabled={$loading || !puedeAvanzar}
            >
              Siguiente →
            </button>
          </div>
      </div>
    {:else if $paso === 2}
      <div class="panel card">
        <h2>Seleccionar Agentes</h2>
        <p class="card-description">
          Seleccioná los agentes del área que participarán en esta guardia.
        </p>

        <div class="resumen-guardia">
          <div><strong>Guardia:</strong> {$nombre}</div>
          <div><strong>Área:</strong> {nombreArea($areaSeleccionada)}</div>
          <div><strong>Inicio:</strong> {$fechaInicio} a las {$horaInicio}</div>
          <div>
            <strong>Fin:</strong>
            {$fechaFin} a las {$horaFin}
            {#if esGuardiaMultiDia}
              <span class="badge-nocturna-small">📅 {diasGuardia} día(s)</span>
            {/if}
          </div>
          {#if duracionGuardia}
            <div class="resumen-duracion">
              <strong>Duración total:</strong>
              {duracionGuardia}
            </div>
          {/if}
        </div>

        {#if $loading || $loadingAgentes}
          <div class="placeholder">
             <div class="spinner"></div>
             <p>Cargando agentes...</p>
          </div>
        {:else if $agentesDisponibles.length === 0}
          <div class="placeholder">
            <div class="placeholder-icon">👥</div>
            <div class="placeholder-title">
              No hay agentes activos en esta área
            </div>
            <div class="placeholder-text">
              Verificá que el área tenga agentes asignados y que estén activos en
              el sistema.
            </div>
          </div>
        {:else}
           <!-- Nuevo Header de Resumen Full Width -->
           <div class="resumen-agentes">
             <p class="info-text-full">
                <strong>{$agentesDisponibles.length}</strong> agente(s) activo(s) en esta área • 
                <strong>{$agentesSeleccionados.size}</strong> seleccionado(s)
                {#if $agentesConConflicto.size > 0}
                  <span class="advertencia-conflictos">⚠️ {$agentesConConflicto.size} con guardias existentes</span>
                {/if}
             </p>
           </div>

           <!-- Grid de Agentes -->
           <div class="agentes-lista">
            {#each $agentesDisponibles as agente}
              {@const tieneConflicto = $agentesConConflicto.has(String(agente.id_agente))}
              <label class="agente-item" class:tiene-conflicto={tieneConflicto}>
                <input
                  type="checkbox"
                  checked={$agentesSeleccionados.has(String(agente.id_agente))}
                  on:change={() => handleToggleAgente(agente.id_agente)}
                  disabled={$loading}
                />
                <div class="agente-info">
                  <div class="agente-nombre">
                    {agente.apellido}, {agente.nombre}
                    {#if tieneConflicto}
                      <span
                        class="badge-conflicto"
                        title="Este agente ya tiene una guardia asignada en estas fechas"
                      >
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
          <button
            class="btn btn-secondary"
            on:click={handleVolverPaso1}
            disabled={$loading}
          >
            ← Volver
          </button>
          <button
            class="btn btn-primary"
            on:click={handleGuardarGuardia}
            disabled={$loading || $agentesSeleccionados.size === 0}
          >
            {#if $loading}
              {$modoEdicion ? "Actualizando..." : "Guardando..."}
            {:else}
              {$modoEdicion ? "✏️ Actualizar Guardia" : "💾 Guardar Guardia"}
            {/if}
          </button>
        </div>
      </div>
    {/if}

  {:else}
    <div class="loading-container">
      <div class="spinner"></div>
    </div>
  {/if}
</section>

{#if $toastVisible}
  <div
    class="toast toast-{$toastTipo}"
    in:fly={{ y: -20, duration: 200 }}
    out:fade={{ duration: 300 }}
  >
    {#if $toastTipo === "success"}
      ✅ {$toastMensaje}
    {:else}
      ❌ {$toastMensaje}
    {/if}
  </div>
{/if}

<style>
  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 50vh;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f3f4f6;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Styles specific for Planner responsiveness */
  @media (max-width: 640px) {
    .guardias-wrap {
      padding: 1rem;
      padding-top: 1rem; /* Reduce top padding */
    }

    .panel {
      padding: 1.25rem; /* Reduce panel padding on mobile */
      min-height: auto !important; /* Allow panel to shrink if needed */
    }

    .head h1 {
      font-size: 1.3rem;
    }

    .head .subtitle {
      font-size: 0.85rem;
    }

    .acciones {
      flex-direction: column-reverse; /* Stack buttons on mobile */
      gap: 0.75rem;
    }
    
    .acciones button {
      width: 100%;
    }
  }

  .guardias-wrap {
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    min-height: 80vh;
    box-sizing: border-box; /* Ensure padding doesn't overflow width */
  }

  .resumen-agentes {
    background-color: white;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin-bottom: 1.5rem;
    border: 1px solid #e2e8f0;
  }

  .info-text-full {
    margin: 0;
    color: #475569;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .advertencia-conflictos {
    color: #b91c1c;
    background: #fef2f2;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .head {
    margin-bottom: 1rem;
  }

  .head h1 {
    font-size: 1.2rem;
    margin: 0 0 0.25rem 0;
    color: #1e40af;
    max-width: 100%;
    word-wrap: break-word;
  }
  
  @media (min-width: 480px) { .head h1 { font-size: 1.4rem; } }
  @media (min-width: 640px) { .head h1 { font-size: 1.6rem; } }
  @media (min-width: 768px) { .head h1 { font-size: 1.8rem; } }

  .head .subtitle {
    margin: 0;
    color: #64748b;
    font-size: 0.9rem;
  }


.panel {
  position: relative; 
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  min-height: 750px; 
  display: flex;
  flex-direction: column;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 50; 
  border-radius: 16px;
  transition: opacity 0.2s ease;
}

.form-grid {
  transition: opacity 0.3s ease;
}

.form-grid.disabled {
  opacity: 0.5;
  pointer-events: none;
}
  .card h2 {
    font-size: 1.5rem;
    color: #0f172a;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.025em;
  }

  .card-description {
    color: #64748b;
    font-size: 1rem;
    margin: 0 0 2rem 0;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f1f5f9;
    line-height: 1.6;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  @media (min-width: 768px) {
    .form-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (min-width: 1024px) {
    .form-grid {
      grid-template-columns: repeat(4, 1fr);
    }

    .campo-nombre {
      grid-column: span 3;
    }
  }

  .campo {
    display: flex;
    flex-direction: column;
    width: 100%; /* Ensure full width in grid cell */
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
      margin-top: 0.5rem;
      display: block;
  }

  .input {
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-family: inherit;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    width: 100%; /* Ensure full width */
    box-sizing: border-box; /* Include padding in width */
  }

  .input:hover:not(:disabled) {
      background: #fff;
      border-color: #94a3b8;
  }

  .input:focus {
    outline: none;
    border-color: #3b82f6;
    background: #fff;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  }

  .input:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    background: #f1f5f9;
  }

  .textarea {
    resize: vertical;
    min-height: 100px;
  }

  /* Resumen Styling */
  .resumen-guardia {
    background: #eff6ff;
    border: 1px solid #dbeafe;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 2rem;
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
  }
  
  @media (min-width: 768px) {
      .resumen-guardia {
          grid-template-columns: repeat(4, 1fr);
          align-items: center;
      }
  }

  /* ... badges styles (retained) ... */
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
  
  .info-duracion {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 1rem;
    font-size: 0.95rem;
    color: #0369a1;
    display: flex;
    align-items: center;
    gap: 1rem;
   }


  .info-text {
    color: #475569;
    font-size: 0.95rem;
    margin: 0 0 1.5rem 0;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  /* Agentes Grid Layout */
  .agentes-lista {
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #e2e8f0;
    border-radius: 12px; /* Increased radius */
    padding: 1rem;
    margin-bottom: 2rem;
    background: #f8fafc;
    
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  @media (min-width: 640px) {
    .agentes-lista {
        grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (min-width: 1024px) {
    .agentes-lista {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .agentes-lista:has(.agente-item:nth-child(4n)) {
        /* Optional: 4 columns on very wide screens if desired, stick to 3 for readability */
        grid-template-columns: repeat(3, 1fr);
    }
  }

  .agente-item {
    display: flex; /* Changed from grid to flex for cleaner layout */
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-radius: 12px;
    background: white;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  }

  .agente-item:hover {
    background: #fff;
    border-color: #94a3b8;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  .agente-item:has(input:checked) {
    background: #eff6ff;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px #3b82f6 inset;
  }

  .agente-item.tiene-conflicto {
    background: #fff1f2;
    border-color: #fecaca;
  }

  .agente-item input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
    flex-shrink: 0;
    accent-color: #2563eb;
  }

  .agente-info {
    flex: 1;
    min-width: 0; /* Prevent text overflow */
  }

  .agente-nombre {
    font-weight: 600;
    color: #1e293b;
    font-size: 1rem;
    margin-bottom: 0.15rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .agente-datos {
    color: #64748b;
    font-size: 0.85rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* ... badges ... */
  .badge-conflicto {
     background: #fee2e2;
     color: #991b1b;
     padding: 0.15rem 0.5rem;
     border-radius: 8px;
     font-size: 0.7rem;
     font-weight: 700;
  }

  .acciones {
    display: flex;
    justify-content: flex-end; /* Right align buttons */
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #f1f5f9;
  }

  .btn {
    padding: 0.875rem 2rem;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    font-family: inherit;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  }

  .btn-primary {
    background: #2563eb;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #1d4ed8;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
  }

  .btn-secondary {
    background: white;
    color: #64748b;
    border: 1px solid #e2e8f0;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #f8fafc;
    color: #334155;
    border-color: #cbd5e1;
  }

  .btn:disabled {
    opacity: 0.6;
    transform: none !important;
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

  .error-mensaje {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
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
    flex: 1; 
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 400px;
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
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    font-size: 16px;
    font-weight: 600;
    z-index: 9999;
    min-width: 260px;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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

  @media (max-width: 480px) {
    .guardias-wrap {
      padding: 1rem;
    }

    .panel {
      padding: 1.25rem;
    }

    .card h2 {
      font-size: 1.2rem;
    }
  }
</style>
