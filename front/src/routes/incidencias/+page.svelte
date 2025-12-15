<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import AuthService from "$lib/login/authService.js";
  import { IncidenciasService } from "$lib/services/incidencias.js";
  import BaseModal from "$lib/componentes/incidencias/BaseModal.svelte";
  import MessageModal from "$lib/componentes/incidencias/MessageModal.svelte";
  import FormModal from "$lib/componentes/incidencias/FormModal.svelte";
  import ModalNuevaIncidencia from "$lib/componentes/incidencias/ModalNuevaIncidencia.svelte";
  import ModalCambiarEstado from "$lib/componentes/incidencias/ModalCambiarEstado.svelte";
  import ModalVerDetalles from "$lib/componentes/incidencias/ModalVerDetalles.svelte";
  import ModalAlert from "$lib/componentes/ModalAlert.svelte";
  import { modalAlert, showAlert } from "$lib/stores/modalAlertStore.js";

  let loading = true;
  let currentUser = null;
  let userRole = null;
  let incidencias = [];
  let misIncidencias = [];
  let incidenciasAsignadas = [];
  let error = null;
  let tabActiva = "todas";
  let busqueda = "";
  let incluirCerradas = false;
  let incidenciasFiltradas = [];

  // Modal para ver detalles
  let showDetalleModal = false;
  let incidenciaSeleccionada = null;
  let cargandoDetalle = false;

  // Modal para cambiar estado
  let showCambiarEstadoModal = false;
  let cambiandoEstado = false;
  let nuevoEstado = "";
  let comentarioEstado = "";
  let estadosDisponibles = [
    { value: "abierta", label: "Abierta" },
    { value: "en_proceso", label: "En Proceso" },
    { value: "pendiente_informacion", label: "Información Pendiente" },
    { value: "resuelta", label: "Resuelta" },
    { value: "cerrada", label: "Cerrada" },
  ];

  // Modal para crear incidencia
  let showModal = false;
  let creandoIncidencia = false;

  // Modal para mensajes
  let showMensajeModal = false;
  let mensajeModal = { titulo: "", mensaje: "", tipo: "success" };
  let jefesArea = [];
  let cargandoJefes = false;
  let nuevaIncidencia = {
    titulo: "",
    descripcion: "",
    prioridad: "media",
    asignado_a_id: null,
  };

  const incidenciasService = new IncidenciasService();

  onMount(async () => {
    try {
      // Use getCurrentUser from localStorage (checkSession already called in +layout.svelte)
      currentUser = AuthService.getCurrentUser();
      if (!currentUser) {
        goto("/");
        return;
      }

      // Determinar si es agente (para simplicar lógica de UI)
      const esAgente = !currentUser?.roles?.some((r) =>
        ["Administrador", "Director", "Jefe de Área", "Jefatura"].includes(
          r.nombre,
        ),
      );
      userRole = esAgente ? "Agente" : "Supervisor";

      // Para agentes, mostrar primero sus incidencias
      if (esAgente) {
        tabActiva = "mias";
      }

      await cargarDatos();
    } catch (error) {
      console.error("Error inicializando página:", error);
      error = error.message;
    } finally {
      loading = false;
    }
  });

  async function cargarDatos() {
    try {
      // Cargar datos en paralelo
      const promesas = [
        incidenciasService.obtenerIncidencias(),
        incidenciasService.obtenerMisIncidencias(),
        incidenciasService.obtenerIncidenciasAsignadas(),
      ];

      const [todasIncidencias, misIncidenciasData, asignadasData] =
        await Promise.all(promesas);

      // Asignar datos recibidos
      incidencias = Array.isArray(todasIncidencias) ? todasIncidencias : [];
      misIncidencias = Array.isArray(misIncidenciasData)
        ? misIncidenciasData
        : [];
      incidenciasAsignadas = Array.isArray(asignadasData) ? asignadasData : [];
    } catch (err) {
      console.error("Error al cargar datos:", err);
      error = err.message;
    }
  }

  function cambiarTab(nuevaTab) {
    tabActiva = nuevaTab;
  }

  // Contadores reactivos que respetan el filtro de cerradas
  $: todasCount = incluirCerradas
    ? incidencias.length
    : incidencias.filter((inc) => inc.estado !== "cerrada").length;
  $: miasCount = incluirCerradas
    ? misIncidencias.length
    : misIncidencias.filter((inc) => inc.estado !== "cerrada").length;
  $: asignadasCount = incluirCerradas
    ? incidenciasAsignadas.length
    : incidenciasAsignadas.filter((inc) => inc.estado !== "cerrada").length;

  // Función reactiva para obtener incidencias según tab activa, búsqueda y filtro de cerradas
  $: incidenciasFiltradas = (() => {
    let incidenciasBase = [];

    switch (tabActiva) {
      case "mias":
        incidenciasBase = misIncidencias || [];
        break;
      case "asignadas":
        incidenciasBase = incidenciasAsignadas || [];
        break;
      default: // 'todas'
        incidenciasBase = incidencias || [];
    }

    // Filtrar incidencias cerradas si no están incluidas
    if (!incluirCerradas) {
      incidenciasBase = incidenciasBase.filter(
        (incidencia) => incidencia && incidencia.estado !== "cerrada",
      );
    }

    // Si no hay búsqueda, devolver incidencias base filtradas
    if (!busqueda || !busqueda.trim()) {
      return incidenciasBase;
    }

    // Aplicar filtro de búsqueda
    const busquedaLower = busqueda.toLowerCase().trim();
    return incidenciasBase.filter((incidencia) => {
      if (!incidencia) return false;

      return (
        (incidencia.titulo &&
          incidencia.titulo.toLowerCase().includes(busquedaLower)) ||
        (incidencia.descripcion &&
          incidencia.descripcion.toLowerCase().includes(busquedaLower)) ||
        (incidencia.numero &&
          incidencia.numero.toLowerCase().includes(busquedaLower)) ||
        (incidencia.creado_por_nombre &&
          incidencia.creado_por_nombre.toLowerCase().includes(busquedaLower)) ||
        (incidencia.asignado_a_nombre &&
          incidencia.asignado_a_nombre.toLowerCase().includes(busquedaLower))
      );
    });
  })();

  async function crearNuevaIncidencia() {
    showModal = true;
    await cargarJefesArea();
  }

  async function cargarJefesArea() {
    cargandoJefes = true;
    try {
      // Si es agente, buscar jefes de área. Si es jefe/director/admin, buscar agentes
      if (userRole === "Agente") {
        const response = await incidenciasService.obtenerJefesArea();
        jefesArea = response.jefes || [];
      } else {
        // Para jefes, directores y admins: obtener agentes
        const response = await incidenciasService.obtenerAgentesArea();
        jefesArea = response.agentes || [];
      }
    } catch (error) {
      console.error("Error cargando destinatarios:", error);
      jefesArea = [];
    } finally {
      cargandoJefes = false;
    }
  }

  function cerrarModal() {
    showModal = false;
    nuevaIncidencia = {
      titulo: "",
      descripcion: "",
      prioridad: "media",
      asignado_a_id: null,
    };
    jefesArea = [];
  }

  async function guardarIncidencia() {
    if (!nuevaIncidencia.titulo.trim() || !nuevaIncidencia.descripcion.trim()) {
      await showAlert("Por favor complete todos los campos obligatorios", "warning", "Advertencia");
      return;
    }

    if (!nuevaIncidencia.asignado_a_id) {
      await showAlert("Debe seleccionar un destinatario para asignar la incidencia", "warning", "Advertencia");
      return;
    }

    creandoIncidencia = true;
    try {
      await incidenciasService.crearIncidencia(nuevaIncidencia);

      // Recargar datos
      await cargarDatos();

      // Cerrar modal y mostrar mensaje
      cerrarModal();
      mostrarMensaje("¡Éxito!", "Incidencia creada exitosamente", "success");

      // Cambiar a la tab de "mis incidencias" para mostrar la nueva
      tabActiva = "mias";
    } catch (err) {
      console.error("Error al crear incidencia:", err);
      mostrarMensaje(
        "Error",
        `No se pudo crear la incidencia: ${err.message}`,
        "error",
      );
    } finally {
      creandoIncidencia = false;
    }
  }

  // Funciones para modal de detalles
  async function verDetalles(incidencia) {
    cargandoDetalle = true;
    showDetalleModal = true;

    try {
      // Obtener detalles completos de la incidencia
      const detallesCompletos = await incidenciasService.obtenerIncidencia(
        incidencia.id,
      );
      incidenciaSeleccionada = detallesCompletos;
    } catch (error) {
      console.error("Error cargando detalles:", error);
      incidenciaSeleccionada = incidencia; // Usar los datos que ya tenemos
    } finally {
      cargandoDetalle = false;
    }
  }

  function cerrarDetalleModal() {
    showDetalleModal = false;
    incidenciaSeleccionada = null;
  }

  function mostrarMensaje(titulo, mensaje, tipo = "success") {
    mensajeModal = { titulo, mensaje, tipo };
    showMensajeModal = true;
  }

  function cerrarMensajeModal() {
    showMensajeModal = false;
  }

  function abrirCambiarEstadoModal() {
    showCambiarEstadoModal = true;
    nuevoEstado = incidenciaSeleccionada.estado || "abierta";
    comentarioEstado = "";
  }

  function cerrarCambiarEstadoModal() {
    showCambiarEstadoModal = false;
    nuevoEstado = "";
    comentarioEstado = "";
  }

  async function guardarCambioEstado() {
    if (!nuevoEstado) {
      await showAlert("Debe seleccionar un nuevo estado", "warning", "Advertencia");
      return;
    }

    if (nuevoEstado === incidenciaSeleccionada.estado) {
      await showAlert("Debe seleccionar un estado diferente al actual", "warning", "Advertencia");
      return;
    }

    cambiandoEstado = true;
    try {
      // Cambiar estado
      const incidenciaActualizada = await incidenciasService.cambiarEstado(
        incidenciaSeleccionada.id,
        nuevoEstado,
        comentarioEstado,
      );

      // Actualizar la incidencia seleccionada
      incidenciaSeleccionada = incidenciaActualizada;

      // Recargar datos
      await cargarDatos();

      // Cerrar modal y mostrar mensaje
      cerrarCambiarEstadoModal();
      mostrarMensaje(
        "¡Estado actualizado!",
        `El estado de la incidencia ha sido cambiado exitosamente.`,
        "success",
      );
    } catch (err) {
      console.error("Error al cambiar estado:", err);
      mostrarMensaje(
        "Error",
        `No se pudo cambiar el estado: ${err.message}`,
        "error",
      );
    } finally {
      cambiandoEstado = false;
    }
  }
</script>

<svelte:head>
  <title>Incidencias - GIGA</title>
</svelte:head>

<div class="incidencias-container">
  {#if loading}
    <div class="loading-container">
      <div class="spinner"></div>
      <p>Cargando incidencias...</p>
    </div>
  {:else}
    <!-- Header elegante -->
    <div class="header">
      <h1>Incidencias</h1>
    </div>

    <!-- Contenido principal -->
    <div class="content">
      {#if error}
        <div class="error-banner">
          <p><strong>Error:</strong> {error}</p>
          <button on:click={() => window.location.reload()}>Reintentar</button>
        </div>
      {:else}
        <!-- Navegación por tabs y búsqueda -->
        <div class="tabs-container">
          <div class="tabs-row">
            <div class="tabs">
              <button
                class="tab {tabActiva === 'todas' ? 'active' : ''}"
                on:click={() => cambiarTab("todas")}
              >
                Todas las Incidencias ({todasCount})
              </button>
              <button
                class="tab {tabActiva === 'mias' ? 'active' : ''}"
                on:click={() => cambiarTab("mias")}
              >
                Mis Incidencias ({miasCount})
              </button>
              <button
                class="tab {tabActiva === 'asignadas' ? 'active' : ''}"
                on:click={() => cambiarTab("asignadas")}
              >
                Asignadas a Mí ({asignadasCount})
              </button>
            </div>

            <button class="btn-crear" on:click={crearNuevaIncidencia}>
              + {userRole === "Agente"
                ? "Contactar Jefatura"
                : "Contactar Agente"}
            </button>
          </div>

          <div class="controls">
            <div class="search-container">
              <input
                type="text"
                placeholder="Buscar incidencias..."
                bind:value={busqueda}
                class="search-input"
              />
              <svg
                class="search-icon"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path
                  d="M21.71 20.29l-3.4-3.4A9 9 0 1 0 16 18l3.4 3.4a1 1 0 0 0 1.42 0 1 1 0 0 0-.11-1.41zM11 18a7 7 0 1 1 7-7 7 7 0 0 1-7 7z"
                />
              </svg>
            </div>

            <div class="filter-container">
              <label class="checkbox-container">
                <input
                  type="checkbox"
                  bind:checked={incluirCerradas}
                  class="checkbox-input"
                />
                <span class="checkbox-label">Incluir cerradas</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Lista de incidencias -->
        <div class="incidencias-list">
          {#each incidenciasFiltradas as incidencia (incidencia?.id || incidencia?.numero || Math.random())}
            <div class="incidencia-card">
              <div class="incidencia-header">
                <div class="incidencia-numero">{incidencia.numero}</div>
                <div class="incidencia-badges">
                  {#if incidencia.estado}
                    <span class="badge badge-{incidencia.estado}">
                      {incidencia.estado_display || incidencia.estado}
                    </span>
                  {:else if incidencia.fecha_resolucion}
                    <span class="badge badge-resuelto"> Resuelta </span>
                  {:else}
                    <span class="badge badge-pendiente"> Pendiente </span>
                  {/if}
                  {#if incidencia.prioridad}
                    <span class="badge badge-prioridad-{incidencia.prioridad}">
                      {incidencia.prioridad_display || incidencia.prioridad}
                    </span>
                  {/if}
                </div>
              </div>

              <h3 class="incidencia-titulo">{incidencia.titulo}</h3>
              <p class="incidencia-descripcion">{incidencia.descripcion}</p>

              <div class="incidencia-footer">
                <div class="incidencia-meta">
                  <div class="meta-item">
                    <strong>Creada por:</strong>
                    {incidencia.creado_por_nombre}
                  </div>
                  <div class="meta-item">
                    <strong>Fecha:</strong>
                    {IncidenciasService.formatearFecha(
                      incidencia.fecha_creacion,
                    )}
                  </div>
                  {#if incidencia.asignado_a_nombre}
                    <div class="meta-item">
                      <strong>Asignada a:</strong>
                      {incidencia.asignado_a_nombre}
                    </div>
                  {/if}
                  {#if incidencia.area_nombre}
                    <div class="meta-item">
                      <strong>Área:</strong>
                      {incidencia.area_nombre}
                    </div>
                  {/if}
                </div>

                <div class="incidencia-actions">
                  <button
                    class="btn-secondary"
                    on:click={() => verDetalles(incidencia)}
                  >
                    Ver Detalles
                  </button>
                </div>
              </div>
            </div>
          {:else}
            <div class="empty-state">
              <h3>No hay incidencias</h3>
              <p>
                {#if busqueda.trim()}
                  No se encontraron incidencias que coincidan con "{busqueda}".
                {:else}
                  No se encontraron incidencias en esta categoría.
                {/if}
              </p>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<!-- Modal para crear nueva incidencia -->
<ModalNuevaIncidencia
  show={showModal}
  {userRole}
  bind:nuevaIncidencia
  {jefesArea}
  {cargandoJefes}
  {creandoIncidencia}
  onClose={cerrarModal}
  onSubmit={guardarIncidencia}
/>

<!-- Modal para ver detalles de incidencia -->
<ModalVerDetalles
  show={showDetalleModal && incidenciaSeleccionada}
  {incidenciaSeleccionada}
  {cargandoDetalle}
  onClose={cerrarDetalleModal}
  onCambiarEstado={abrirCambiarEstadoModal}
/>

<!-- Modal de Mensajes -->
<MessageModal
  show={showMensajeModal}
  type={mensajeModal.tipo}
  title={mensajeModal.titulo}
  message={mensajeModal.mensaje}
  onClose={cerrarMensajeModal}
/>

<!-- Modal para cambiar estado -->
<ModalCambiarEstado
  show={showCambiarEstadoModal && incidenciaSeleccionada}
  {incidenciaSeleccionada}
  {estadosDisponibles}
  bind:nuevoEstado
  bind:comentarioEstado
  {cambiandoEstado}
  onClose={cerrarCambiarEstadoModal}
  onSubmit={guardarCambioEstado}
/>

<!-- Modal de alertas -->
<ModalAlert
  bind:show={$modalAlert.show}
  type={$modalAlert.type}
  title={$modalAlert.title}
  message={$modalAlert.message}
  showConfirmButton={$modalAlert.showConfirmButton}
  confirmText={$modalAlert.confirmText}
  showCancelButton={$modalAlert.showCancelButton}
  cancelText={$modalAlert.cancelText}
  on:confirm={() => $modalAlert.onConfirm && $modalAlert.onConfirm()}
  on:cancel={() => $modalAlert.onCancel && $modalAlert.onCancel()}
/>

<style>
  .incidencias-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem 1rem 1.5rem;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  @media (max-width: 640px) {
    .incidencias-container {
      padding: 1rem 0.75rem 1.5rem;
      width: 100%;
      box-sizing: border-box;
      overflow-x: hidden;
    }
  }

  :global(html),
  :global(body) {
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  :global(html::-webkit-scrollbar),
  :global(body::-webkit-scrollbar) {
    display: none;
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f4f6;
    border-top: 4px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .header {
    position: relative;
    background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
    color: white;
    padding: 16px 12px;
    max-width: 100%;
    border-radius: 12px;
    overflow: hidden;
    text-align: center;
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.1) inset,
      0 20px 60px rgba(30, 64, 175, 0.4);
    margin-bottom: 1.5rem;
    box-sizing: border-box;
    height: auto;
    width: 100%;
  }

  @media (max-width: 640px) {
    .header {
      padding: 12px 8px;
      margin-bottom: 1rem;
    }
  }

  @media (min-width: 640px) {
    .header {
      padding: 18px 20px;
      border-radius: 14px;
    }
  }

  @media (min-width: 768px) {
    .header {
      padding: 20px 30px;
      border-radius: 16px;
      margin-bottom: 2rem;
    }
  }

  .header::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.03) 1px,
        transparent 1px
      ),
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: moveLines 20s linear infinite;
  }

  @keyframes moveLines {
    0% {
      transform: translateX(0) translateY(0);
    }
    100% {
      transform: translateX(50px) translateY(50px);
    }
  }

  .header h1 {
    margin: 10px;
    font-weight: 800;
    font-size: 20px;
    letter-spacing: 0.2px;
    position: relative;
    padding-bottom: 12px;
    overflow: hidden;
    display: block;
    max-width: 100%;
    word-wrap: break-word;
    word-break: break-word; /* Ensure long words break */
    white-space: normal;
    height: auto;
    line-height: 1.3;
  }

  @media (min-width: 480px) {
    .header h1 {
      font-size: 24px;
    }
  }

  @media (min-width: 640px) {
    .header h1 {
      font-size: 28px;
      display: inline-block;
    }
  }

  @media (min-width: 768px) {
    .header h1 {
      font-size: 32px;
    }
  }

  .header h1::after {
    content: "";
    position: absolute;
    width: 40%;
    height: 3px;
    bottom: 0;
    left: 0;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.9),
      transparent
    );
    animation: moveLine 2s linear infinite;
  }

  @keyframes moveLine {
    0% {
      left: -40%;
    }
    100% {
      left: 100%;
    }
  }

  .content {
    padding: 0;
  }

  .error-banner {
    background: #fee2e2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #fecaca;
  }

  .error-banner button {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);
  }

  .error-banner button:hover {
    background: linear-gradient(135deg, #b91c1c, #991b1b);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(220, 38, 38, 0.4);
  }

  .tabs-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 1rem;
    flex-wrap: wrap;
    min-width: 0;
  }

  @media (max-width: 768px) {
    .tabs-header {
      flex-direction: column;
      align-items: stretch;
    }
  }

  .tabs-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .tabs-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .tabs {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: nowrap;
  }

  .controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-shrink: 0;
    flex-wrap: wrap;
  }

  @media (max-width: 768px) {
    .tabs-row {
      flex-direction: column;
      align-items: stretch;
      overflow-x: hidden;
      white-space: normal;
    }

    .tabs {
      flex-direction: column;
      align-items: stretch;
      width: 100%;
      overflow-x: hidden;
      padding-bottom: 0;
      height: auto;
    }

    .tab {
      width: 100%;
      text-align: center;
      margin-bottom: 0.5rem;
    }

    .controls {
      width: 100%;
      flex-direction: column;
    }
  }

  .tab {
    background: none;
    border: none;
    font-size: 14px;
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    border-radius: 10px;
    color: #6b7280;
    font-weight: 600;
    transition: all 0.3s ease;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .tab:hover {
    background: #f3f4f6;
    color: #374151;
    transform: translateY(-2px);
  }

  .tab.active {
    background: linear-gradient(135deg, #4c51bf 0%, #5b21b6 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(76, 81, 191, 0.3);
  }

  .search-container {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-input {
    padding: 0.75rem 2.5rem 0.75rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    font-size: 0.875rem;
    width: 250px;
    max-width: 100%;
    transition: all 0.3s ease;
    background: white;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  @media (max-width: 768px) {
    .search-input {
      width: 100%;
    }
  }

  .search-input:focus {
    outline: none;
    border-color: #4c51bf;
    box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
  }

  .search-input::placeholder {
    color: #9ca3af;
  }

  .search-icon {
    position: absolute;
    right: 0.75rem;
    width: 18px;
    height: 18px;
    fill: #9ca3af;
    pointer-events: none;
  }

  .filter-container {
    display: flex;
    align-items: center;
    margin-left: 1rem;
  }

  .checkbox-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    user-select: none;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .checkbox-input {
    appearance: none;
    width: 18px;
    height: 18px;
    border: 2px solid #d1d5db;
    border-radius: 4px;
    background: white;
    margin-right: 0.5rem;
    cursor: pointer;
    position: relative;
    transition: all 0.2s;
  }

  .checkbox-input:checked {
    background: #4c51bf;
    border-color: #4c51bf;
  }

  .checkbox-input:checked::before {
    content: "✓";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
  }

  .checkbox-input:hover {
    border-color: #9ca3af;
  }

  .checkbox-input:checked:hover {
    background: #5b21b6;
    border-color: #5b21b6;
  }

  .checkbox-label {
    font-size: 0.875rem;
    color: #374151;
    font-weight: 600;
  }

  .btn-crear {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    font-size: 0.875rem;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  }

  .btn-crear:hover {
    background: linear-gradient(135deg, #059669, #047857);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
  }

  /* Lista de incidencias */
  .incidencias-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-height: 600px;
    overflow-y: auto;
    padding-right: 0.5rem;
  }

  .incidencia-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
  }

  .incidencia-card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-4px);
    border-color: #cbd5e1;
  }

  @media (max-width: 640px) {
    .incidencia-card {
      padding: 1rem;
    }
  }

  .incidencia-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .incidencia-numero {
    font-family: "Courier New", monospace;
    font-weight: bold;
    color: #6b7280;
    font-size: 0.875rem;
    background: #f3f4f6;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
  }

  .incidencia-badges {
    display: flex;
    gap: 0.5rem;
  }

  .badge {
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .badge-resuelto {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
  }

  .badge-pendiente {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
  }

  /* Estados específicos */
  .badge-abierta {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
  }

  .badge-en_proceso {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
  }

  .badge-pendiente_informacion {
    background: linear-gradient(135deg, #eab308, #ca8a04);
    color: white;
  }

  .badge-resuelta {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
  }

  .badge-cerrada {
    background: linear-gradient(135deg, #6b7280, #4b5563);
    color: white;
  }

  /* Prioridades */
  .badge-prioridad-baja {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
  }

  .badge-prioridad-media {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
  }

  .badge-prioridad-alta {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
  }

  .badge-prioridad-critica {
    background: linear-gradient(135deg, #991b1b, #7f1d1d);
    color: white;
  }

  .incidencia-titulo {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    font-weight: 700;
    color: #1f2937;
    word-wrap: break-word;
    word-break: break-word;
  }

  .incidencia-descripcion {
    color: #6b7280;
    margin-bottom: 1rem;
    line-height: 1.6;
  }

  .incidencia-footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
    flex-wrap: wrap;
  }

  @media (max-width: 768px) {
    .incidencia-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.75rem;
    }
    
    .incidencia-badges {
      flex-wrap: wrap;
    }

    .incidencia-footer {
      flex-direction: column;
      align-items: stretch;
      gap: 1.5rem;
    }

    .incidencia-meta {
      width: 100%;
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .incidencia-actions {
      width: 100%;
    }
    
    .btn-secondary {
      width: 100%;
    }
  }

  .incidencia-meta {
    display: flex;
    flex-wrap: wrap;
    flex-wrap: wrap;
    gap: 1rem;
    flex: 1;
    width: 100%;
  }

  .meta-item {
    font-size: 0.875rem;
    color: #6b7280;
  }

  .meta-item strong {
    color: #374151;
    font-weight: 600;
  }

  .incidencia-actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-secondary {
    background: linear-gradient(135deg, #4c51bf, #5b21b6);
    color: #ffffff;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    box-shadow: 0 2px 8px rgba(76, 81, 191, 0.3);
  }

  .btn-secondary:hover {
    background: linear-gradient(135deg, #5b21b6, #6d28d9);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(76, 81, 191, 0.4);
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #6b7280;
  }

  .empty-state h3 {
    margin-bottom: 0.5rem;
    color: #374151;
    font-size: 1.5rem;
    font-weight: 700;
  }

  .empty-state p {
    font-size: 1rem;
    margin-bottom: 1rem;
  }

  /* Solo ajustes mínimos para evitar overflow */
  @media (max-width: 1024px) {
    .incidencias-container {
      max-width: 100%;
    }
  }
</style>
