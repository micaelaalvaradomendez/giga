<script>
  import { onMount } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { planificadorGuardiasController } from "$lib/paneladmin/controllers";

  // Obtener stores del controller
  const {
    loading,
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

  onMount(async () => {
    console.log(
      "🔄 Componente de planificador montado, iniciando controller...",
    );

    // Verificar si viene parámetro de edición
    const urlParams = new URLSearchParams(window.location.search);
    await planificadorGuardiasController.init(urlParams);

    console.log("✅ Controller de planificador inicializado");
  });

  // Handlers delegados al controller
  async function handleAreaChange() {
    await planificadorGuardiasController.handleAreaChange();
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
</script>

<section class="guardias-wrap">
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
    <div class="panel card">
      <h2>Datos de la Guardia</h2>

      <div class="form-grid">
        <div class="campo">
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
            <option value={null}>Seleccione un área</option>
            {#each $areas as area}
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
            bind:value={$fechaInicio}
            on:change={handleFechaHorarioChange}
            disabled={$loading}
          />
        </div>

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
          disabled={$loading}
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

      {#if $loading}
        <div class="placeholder">
          <div class="placeholder-icon">⏳</div>
          <div class="placeholder-title">Cargando agentes...</div>
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
        <div class="agentes-lista">
          <p class="info-text">
            <strong>{$agentesDisponibles.length}</strong> agente(s) activo(s) en
            esta área • <strong>{$agentesSeleccionados.size}</strong>
            seleccionado(s)
            {#if $agentesConConflicto.size > 0}
              <span class="advertencia-conflictos"
                >⚠️ {$agentesConConflicto.size} con guardias existentes</span
              >
            {/if}
          </p>
          {#each $agentesDisponibles as agente}
            {@const tieneConflicto = $agentesConConflicto.has(
              String(agente.id_agente),
            )}
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
  .guardias-wrap {
    max-width: 900px;
    margin: 0 auto;
    padding: 1.5rem;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .head {
    margin-bottom: 1.5rem;
  }

  .head h1 {
    font-size: 1.2rem;
    margin: 0 0 0.25rem 0;
    color: #1e40af;
    max-width: 100%;
    word-wrap: break-word;
  }

  @media (min-width: 480px) {
    .head h1 {
      font-size: 1.4rem;
    }
  }

  @media (min-width: 640px) {
    .head h1 {
      font-size: 1.6rem;
    }
  }

  @media (min-width: 768px) {
    .head h1 {
      font-size: 1.8rem;
    }
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
    transition:
      border-color 0.2s,
      background 0.2s;
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
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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
</style>
