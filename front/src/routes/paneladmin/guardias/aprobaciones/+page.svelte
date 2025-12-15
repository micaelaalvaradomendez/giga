<script>
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import { aprobacionesGuardiasController } from "$lib/paneladmin/controllers";
  import ModalDetalleGuardia from "$lib/componentes/admin/guardias/ModalDetalleGuardia.svelte";
  import ModalRechazoCronograma from "$lib/componentes/admin/guardias/ModalRechazoCronograma.svelte";

  // Obtener stores del controller
  const {
    loading,
    error,
    cronogramasPendientes,
    cronogramasAprobadas,
    tabActiva,
    agenteActual,
    rolAgente,
    mostrarModal,
    cronogramaSeleccionado,
    guardiasDelCronograma,
    mostrarModalRechazo,
    motivoRechazo,
    cronogramaARechazar,
    // Filtros
    areas,
    filtroArea,
    filtroTipo,
    filtroEstado,
    busqueda,
    cronogramasPendientesFiltrados,
    cronogramasAprobadasFiltradas,
  } = aprobacionesGuardiasController;

  onMount(async () => {
    console.log(
      "🔄 Componente de aprobaciones montado, iniciando controller...",
    );
    await aprobacionesGuardiasController.init();
    console.log("✅ Controller de aprobaciones inicializado");

    // Recargar cuando la página vuelve a ser visible
    if (browser) {
      const handleVisibilityChange = () => {
        if (document.visibilityState === "visible") {
          aprobacionesGuardiasController.cargarDatos();
        }
      };

      const handleFocus = () => {
        aprobacionesGuardiasController.cargarDatos();
      };

      document.addEventListener("visibilitychange", handleVisibilityChange);
      window.addEventListener("focus", handleFocus);

      return () => {
        document.removeEventListener(
          "visibilitychange",
          handleVisibilityChange,
        );
        window.removeEventListener("focus", handleFocus);
      };
    }
  });

  // Handlers delegados al controller
  async function handleVerDetalles(cronograma) {
    await aprobacionesGuardiasController.verDetalles(cronograma);
  }

  async function handleAprobar(cronograma) {
    await aprobacionesGuardiasController.aprobar(cronograma);
  }

  function handleIniciarRechazo(cronograma) {
    aprobacionesGuardiasController.iniciarRechazo(cronograma);
  }

  async function handleConfirmarRechazo() {
    await aprobacionesGuardiasController.confirmarRechazo();
  }

  async function handlePublicar(cronograma) {
    await aprobacionesGuardiasController.publicar(cronograma);
  }

  function handleCerrarModal() {
    aprobacionesGuardiasController.cerrarModal();
  }

  async function handleEditarCronograma(cronograma) {
    await aprobacionesGuardiasController.editarCronograma(cronograma);
  }

  async function handleEliminarGuardia(guardia) {
    await aprobacionesGuardiasController.eliminarGuardia(guardia);
  }

  async function handleEliminarCronograma(cronograma) {
    await aprobacionesGuardiasController.eliminarCronograma(cronograma);
  }

  function handleCambiarTab(tab) {
    aprobacionesGuardiasController.cambiarTab(tab);
  }

  async function handleDespublicar(cronograma) {
    await aprobacionesGuardiasController.despublicar(cronograma);
  }

  async function handleEliminar(cronograma) {
    await aprobacionesGuardiasController.eliminar(cronograma);
  }
</script>

<section class="aprobaciones-wrap">
  <header class="head">
    <h1>Aprobaciones de Guardias</h1>
    <p>Revisá y aprobá cronogramas pendientes</p>
    {#if $rolAgente}
      <div class="rol-badge">
        Tu rol: <strong>{$rolAgente}</strong>
      </div>
    {/if}
  </header>

  <!-- Filtros -->
  <div class="filtros-section">
    <div class="filtros-grid">
      <div class="filtro-item">
        <label for="filtro-area">Área:</label>
        <select id="filtro-area" bind:value={$filtroArea}>
          <option value="">Todas las áreas</option>
          {#each $areas as area}
            <option value={area.id_area}>{area.nombre}</option>
          {/each}
        </select>
      </div>

      <div class="filtro-item">
        <label for="filtro-tipo">Tipo:</label>
        <select id="filtro-tipo" bind:value={$filtroTipo}>
          <option value="">Todos los tipos</option>
          <option value="regular">Regular</option>
          <option value="especial">Especial</option>
          <option value="feriado">Feriado</option>
          <option value="emergencia">Emergencia</option>
        </select>
      </div>

      <div class="filtro-item">
        <label for="filtro-estado">Estado:</label>
        <select id="filtro-estado" bind:value={$filtroEstado}>
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendiente</option>
          <option value="aprobada">Aprobada</option>
          <option value="publicada">Publicada</option>
          <option value="rechazada">Rechazada</option>
        </select>
      </div>

      <div class="filtro-item">
        <label for="filtro-busqueda">Buscar:</label>
        <input
          id="filtro-busqueda"
          type="text"
          placeholder="Nombre o área..."
          bind:value={$busqueda}
        />
      </div>

      <div class="filtro-item filtro-actions">
        <button
          class="btn-limpiar"
          on:click={() => aprobacionesGuardiasController.limpiarFiltros()}
        >
          🗑️ Limpiar
        </button>
      </div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button
      class="tab"
      class:active={$tabActiva === "pendientes"}
      on:click={() => handleCambiarTab("pendientes")}
    >
      Pendientes ({$cronogramasPendientesFiltrados.length})
    </button>
    <button
      class="tab"
      class:active={$tabActiva === "aprobadas"}
      on:click={() => handleCambiarTab("aprobadas")}
    >
      Publicadas ({$cronogramasAprobadasFiltradas.length})
    </button>
  </div>

  {#if $error}
    <div class="alert alert-error">{$error}</div>
  {/if}

  {#if $loading}
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando...</p>
    </div>
  {:else if $tabActiva === "pendientes"}
    <!-- Lista de pendientes -->
    <div class="cronogramas-lista">
      {#if $cronogramasPendientesFiltrados.length === 0}
        <div class="empty-state">
          <p>
            {#if $cronogramasPendientes.length > 0}
              📋 No hay cronogramas que coincidan con los filtros aplicados
            {:else}
              ✓ No hay cronogramas pendientes de aprobación
            {/if}
          </p>
        </div>
      {:else}
        {#each $cronogramasPendientesFiltrados as cronograma}
          <div class="cronograma-card pendiente">
            <div class="cronograma-header">
              <div class="cronograma-info">
                <h3>{cronograma.area_nombre || "Sin área"}</h3>
                <p class="tipo">{cronograma.tipo}</p>
              </div>
              <div class="cronograma-estado">
                <span class="badge badge-pendiente">{cronograma.estado}</span>
              </div>
            </div>

            <div class="cronograma-body">
              <div class="info-row">
                <span class="label">Creado por:</span>
                <span class="valor">
                  {#if cronograma.creado_por_nombre || cronograma.creado_por_apellido}
                    {cronograma.creado_por_nombre || ""}
                    {cronograma.creado_por_apellido || ""}
                    {#if cronograma.creado_por_rol}
                      <span class="rol-mini">({cronograma.creado_por_rol})</span
                      >
                    {/if}
                  {:else}
                    <span class="sin-creador">Sistema (histórico)</span>
                  {/if}
                </span>
              </div>

              <div class="info-row">
                <span class="label">Fecha creación:</span>
                <span class="value"
                  >{aprobacionesGuardiasController.formatearFecha(
                    cronograma.fecha_creacion,
                  )}</span
                >
              </div>

              <div class="info-row">
                <span class="label">Horario:</span>
                <span class="value">
                  {aprobacionesGuardiasController.formatearHora(
                    cronograma.hora_inicio,
                  )} - {aprobacionesGuardiasController.formatearHora(
                    cronograma.hora_fin,
                  )}
                </span>
              </div>

              <div class="info-row">
                <span class="label">Guardias:</span>
                <span class="value">{cronograma.total_guardias || 0}</span>
              </div>

              {#if cronograma.puede_aprobar_rol && cronograma.puede_aprobar_rol.length > 0}
                <div class="info-row">
                  <span class="label">Puede aprobar:</span>
                  <span class="value roles-permitidos">
                    {cronograma.puede_aprobar_rol.join(", ")}
                  </span>
                </div>
              {/if}
            </div>

            <div class="cronograma-actions">
              <button
                class="btn btn-secondary"
                on:click={() => handleVerDetalles(cronograma)}
              >
                📋 Ver Detalles
              </button>
              <button
                class="btn btn-info"
                on:click={() => handleEditarCronograma(cronograma)}
                disabled={$loading}
              >
                ✏️ Editar
              </button>
              <button
                class="btn btn-success"
                on:click={() => handleAprobar(cronograma)}
                disabled={$loading}
              >
                ✓ Aprobar y Publicar
              </button>
              <button
                class="btn btn-danger"
                on:click={() => handleIniciarRechazo(cronograma)}
                disabled={$loading}
              >
                ✗ Rechazar
              </button>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  {:else}
    <!-- Lista de aprobadas -->
    <div class="cronogramas-lista">
      {#if $cronogramasAprobadasFiltradas.length === 0}
        <div class="empty-state">
          <p>
            {#if $cronogramasAprobadas.length > 0}
              📋 No hay cronogramas que coincidan con los filtros aplicados
            {:else}
              ✓ No hay cronogramas publicados
            {/if}
          </p>
        </div>
      {:else}
        {#each $cronogramasAprobadasFiltradas as cronograma}
          <div class="cronograma-card aprobada">
            <div class="cronograma-header">
              <div class="cronograma-info">
                <h3>{cronograma.area_nombre || "Sin área"}</h3>
                <p class="tipo">{cronograma.tipo}</p>
              </div>
              <div class="cronograma-estado">
                <span class="badge badge-{cronograma.estado}"
                  >{cronograma.estado}</span
                >
              </div>
            </div>

            <div class="cronograma-body">
              <div class="info-row">
                <span class="label">Creado:</span>
                <span class="value"
                  >{aprobacionesGuardiasController.formatearFecha(
                    cronograma.fecha_creacion,
                  )}</span
                >
              </div>

              {#if cronograma.fecha_aprobacion}
                <div class="info-row">
                  <span class="label">Publicado:</span>
                  <span class="value"
                    >{aprobacionesGuardiasController.formatearFecha(
                      cronograma.fecha_aprobacion,
                    )}</span
                  >
                </div>
              {/if}

              <div class="info-row">
                <span class="label">Guardias:</span>
                <span class="value">{cronograma.total_guardias || 0}</span>
              </div>
            </div>

            <div class="cronograma-actions">
              <button
                class="btn btn-secondary"
                on:click={() => handleVerDetalles(cronograma)}
              >
                📋 Ver Detalles
              </button>
              {#if cronograma.estado === "publicada" && cronograma.puedeDespublicar}
                <button
                  class="btn btn-warning"
                  on:click={() => handleDespublicar(cronograma)}
                  disabled={$loading}
                  title="Despublicar cronograma"
                >
                  📤 Despublicar
                </button>
              {/if}
              {#if cronograma.estado === "pendiente"}
                <button
                  class="btn btn-danger"
                  on:click={() => handleEliminar(cronograma)}
                >
                  🗑️ Eliminar
                </button>
              {/if}
            </div>
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</section>

<!-- Modal de detalles -->
{#if $mostrarModal && $cronogramaSeleccionado}
  <ModalDetalleGuardia
    cronograma={$cronogramaSeleccionado}
    guardias={$guardiasDelCronograma}
    loading={$loading}
    on:close={handleCerrarModal}
    on:eliminarGuardia={({ detail }) => handleEliminarGuardia(detail)}
    on:eliminarCronograma={({ detail }) => handleEliminarCronograma(detail)}
  />
{/if}

<!-- Modal de rechazo -->
{#if $mostrarModalRechazo && $cronogramaARechazar}
  <ModalRechazoCronograma
    cronograma={$cronogramaARechazar}
    loading={$loading}
    bind:motivoRechazo={$motivoRechazo}
    on:close={() => aprobacionesGuardiasController.cerrarModalRechazo()}
    on:confirmar={handleConfirmarRechazo}
  />
{/if}

<style>
  .aprobaciones-wrap {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .head {
    text-align: center;
    margin-bottom: 2rem;
  }

  .head h1 {
    font-size: 1.2rem;
    margin: 0 0 0.5rem 0;
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

  .head p {
    margin: 0 0 1rem 0;
    color: #64748b;
    font-size: 1rem;
  }

  .search-section {
    margin-bottom: 1.5rem;
    background-color: #fff;
    padding: 1.5rem;
    border: 1px solid #4950574b;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    display: flex;
    gap: 1rem;
  }

  .search-label {
    font-weight: 600;
    color: #495057;
  }

  .search-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 1rem;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
  }

  .search-input:focus {
    outline: none;
    border-color: #e79043;
    box-shadow: 0 0 0 3px rgba(231, 144, 67, 0.3);
  }

  .rol-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: linear-gradient(
      135deg,
      rgba(142, 182, 228, 0.2) 0%,
      rgba(61, 151, 255, 0.2) 100%
    );
    border-radius: 8px;
    color: #1e40af;
    font-size: 0.9rem;
  }

  .tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e5e7eb;
  }

  .tab {
    padding: 0.75rem 1.5rem;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    color: #64748b;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .tab:hover {
    color: #1e40af;
    background: rgba(142, 182, 228, 0.1);
  }

  .tab.active {
    color: #1e40af;
    border-bottom-color: #1e40af;
  }

  .cronogramas-lista {
    display: grid;
    gap: 1rem;
  }

  .cronograma-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    transition: box-shadow 0.2s ease;
  }

  .cronograma-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .cronograma-card.pendiente {
    border-left: 4px solid #f59e0b;
  }

  .cronograma-card.aprobada {
    border-left: 4px solid #10b981;
  }

  .cronograma-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }

  .cronograma-info h3 {
    margin: 0 0 0.25rem 0;
    color: #1e40af;
    font-size: 1.2rem;
  }

  .cronograma-info .tipo {
    margin: 0;
    color: #64748b;
    font-size: 0.9rem;
    text-transform: uppercase;
  }

  .badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .badge-pendiente {
    background: #fef3c7;
    color: #92400e;
  }

  .badge-aprobada {
    background: #d1fae5;
    color: #065f46;
  }

  .badge-publicada {
    background: #dbeafe;
    color: #1e40af;
  }

  .badge-generada {
    background: #fef3c7;
    color: #92400e;
  }

  .badge-rechazada {
    background: #fee2e2;
    color: #991b1b;
  }

  .cronograma-body {
    margin-bottom: 1rem;
  }

  .info-row {
    display: flex;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .info-row:last-child {
    border-bottom: none;
  }

  .info-row .label {
    color: #64748b;
    font-size: 0.9rem;
    margin-right: 10px;
    font-weight: 600;
  }

  .info-row .value {
    color: #111827;
    font-size: 0.9rem;
  }

  .rol-mini {
    color: #64748b;
    font-size: 0.85rem;
    font-style: italic;
  }

  .sin-creador {
    color: #94a3b8;
    font-style: italic;
    font-size: 0.9rem;
  }

  .roles-permitidos {
    text-transform: capitalize;
    color: #059669;
    font-weight: 600;
  }

  .cronograma-actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: #3b82f6;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn-secondary {
    background: #e5e7eb;
    color: #374151;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #d1d5db;
  }

  .btn-info {
    background: #3b82f6;
    color: white;
  }

  .btn-info:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn-success {
    background: #10b981;
    color: white;
  }

  .btn-success:hover:not(:disabled) {
    background: #059669;
  }

  .btn-danger {
    background: #ef4444;
    color: white;
  }

  .btn-danger:hover:not(:disabled) {
    background: #dc2626;
  }

  .btn-icon {
    padding: 0.4rem 0.6rem;
    font-size: 1rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: transparent;
  }

  .btn-icon:hover:not(:disabled) {
    transform: scale(1.1);
  }

  .btn-danger-icon {
    color: #ef4444;
  }

  .btn-danger-icon:hover:not(:disabled) {
    background: #fee2e2;
  }

  .btn-icon:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #64748b;
  }

  .empty-state p {
    font-size: 1.1rem;
    margin: 0;
  }

  .loading-container {
    text-align: center;
    padding: 3rem 1rem;
  }

  .loading-spinner {
    border: 4px solid #f3f4f6;
    border-top: 4px solid #3b82f6;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .alert {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .alert-error {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  /* Estilos para filtros */
  .filtros-section {
    background: #f1f4f8;
    border: 1px solid #e5e9eeb2;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .filtros-grid {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 1rem;
    align-items: end;
    margin-bottom: 1rem;
  }

  .filtro-item {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .filtro-item label {
    font-weight: 600;
    color: #374151;
    font-size: 0.9rem;
  }

  .filtro-item select,
  .filtro-item input {
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 0.9rem;
    background: white;
  }

  .filtro-item select:focus,
  .filtro-item input:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  .btn-limpiar {
    padding: 10px 25px;
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;
    height: 42px;
  }

  .btn-limpiar:hover {
    background: #5a6268;
    transform: translateY(-1px);
  }

  .btn-warning {
    background: #f59e0b;
    color: white;
    border: 1px solid #d97706;
  }

  .btn-warning:hover:not(:disabled) {
    background: #d97706;
    border-color: #b45309;
  }

  .btn-warning:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
