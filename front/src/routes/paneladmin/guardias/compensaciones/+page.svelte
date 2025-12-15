<script>
  import { guardiasService, personasService } from "$lib/services.js";
  import { onMount } from "svelte";
  import ModalDetalleCompensacion from "$lib/componentes/admin/compensaciones/ModalDetalleCompensacion.svelte";
  import ModalNuevaCompensacion from "$lib/componentes/admin/compensaciones/ModalNuevaCompensacion.svelte";

  // Estado del componente
  let compensaciones = [];
  let cargando = false;
  let error = null;
  let mostrandoFormulario = false;
  let token = null;

  // Debug: verificar que el script se esté ejecutando
  console.log("Script de compensaciones inicializado");

  // Datos para el formulario de nueva compensación
  let areas = [];
  let cargandoAreas = false;

  // Filtros para la lista de compensaciones
  let filtroAreaLista = "";
  let filtroEstadoLista = "";
  let busqueda = "";

  // Modal de detalles
  let mostrandoDetalles = false;
  let compensacionSeleccionada = null;

  // Variables para modal de confirmación
  let mostrandoConfirmacion = false;
  let tituloConfirmacion = "";
  let mensajeConfirmacion = "";
  let tipoConfirmacion = "success"; // 'success', 'error', 'warning'
  let resolverConfirmacion = null;
  let pedirInput = false;
  let valorInput = "";

  onMount(async () => {
    console.log("Componente compensaciones montado, iniciando carga...");
    // Obtener token de sesión
    token = localStorage.getItem("token");

    try {
      await cargarCompensaciones();
      await cargarAreas();
      console.log("Carga inicial completada");
    } catch (err) {
      console.error("Error en carga inicial:", err);
    }
  });

  async function cargarCompensaciones() {
    cargando = true;
    error = null;
    try {
      const response = await guardiasService.getCompensaciones("", token);
      console.log("Respuesta completa compensaciones:", response);

      // Manejar diferentes estructuras de respuesta (incluyendo response.data.data.results)
      let datos = [];
      if (response.data?.data?.results) {
        datos = response.data.data.results;
      } else if (response.data?.results) {
        datos = response.data.results;
      } else if (response.success && response.data && response.data.results) {
        datos = response.data.results;
      } else if (response.results) {
        datos = response.results;
      } else if (Array.isArray(response.data)) {
        datos = response.data;
      } else if (Array.isArray(response)) {
        datos = response;
      } else {
        datos = [];
      }

      compensaciones = datos;
      console.log("Compensaciones cargadas:", compensaciones);
    } catch (err) {
      console.error("Error cargando compensaciones:", err);
      error =
        "Error al cargar compensaciones: " +
        (err.response?.data?.message || err.message || "Error desconocido");
      compensaciones = [];
    } finally {
      cargando = false;
    }
  }

  async function cargarAreas() {
    cargandoAreas = true;
    try {
      const response = await personasService.getAreas(token);
      console.log("Respuesta completa de áreas:", response);

      // Manejar diferentes estructuras de respuesta (incluyendo response.data.data.results)
      let datos = [];
      if (response.data?.data?.results) {
        datos = response.data.data.results;
      } else if (response.data?.results) {
        datos = response.data.results;
      } else if (response.success && response.data && response.data.results) {
        datos = response.data.results;
      } else if (response.results) {
        datos = response.results;
      } else if (Array.isArray(response.data)) {
        datos = response.data;
      } else if (Array.isArray(response)) {
        datos = response;
      } else {
        console.log(
          "📊 Estructura inesperada de respuesta áreas compensaciones:",
          response,
        );
        datos = [];
      }

      areas = datos;
      console.log("✅ Áreas procesadas en compensaciones:", areas.length);
      console.log("📋 Primeras 3 áreas:", areas.slice(0, 3));

      console.log("Áreas procesadas:", areas);
    } catch (err) {
      console.error("Error cargando áreas:", err);
      areas = [];
    } finally {
      cargandoAreas = false;
    }
  }

  // Compensaciones filtradas
  $: compensacionesFiltradas = compensaciones.filter((comp) => {
    // Filtro por búsqueda
    if (busqueda.trim()) {
      const searchTerm = busqueda.toLowerCase();
      const matchesSearch =
        comp.agente_nombre?.toLowerCase().includes(searchTerm) ||
        comp.agente_apellido?.toLowerCase().includes(searchTerm) ||
        comp.id_agente?.toString().includes(searchTerm) ||
        comp.agente_dni?.toString().includes(searchTerm) ||
        comp.agente_email?.toLowerCase().includes(searchTerm) ||
        comp.agente_legajo?.toString().includes(searchTerm) ||
        comp.descripcion_motivo?.toLowerCase().includes(searchTerm);

      if (!matchesSearch) return false;
    }

    // Filtro por área - necesitamos buscar el área de la guardia
    if (filtroAreaLista && comp.id_area !== parseInt(filtroAreaLista)) {
      return false;
    }
    // Filtro por estado
    if (filtroEstadoLista && comp.estado !== filtroEstadoLista) {
      return false;
    }
    return true;
  });


  function formatearFecha(fecha) {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-AR");
  }

  function formatearHora(hora) {
    if (!hora) return "-";
    return hora.slice(0, 5); // HH:MM
  }

  function limpiarFiltros() {
    busqueda = "";
    filtroAreaLista = "";
    filtroEstadoLista = "";
  }

  function verDetalles(compensacion) {
    compensacionSeleccionada = compensacion;
    mostrandoDetalles = true;
    console.log("Ver detalles de compensación:", compensacion);
  }

  function cerrarDetalles() {
    mostrandoDetalles = false;
    compensacionSeleccionada = null;
  }

  async function aprobarCompensacion(compensacion) {
    if (!(await confirmar("¿Está seguro de aprobar esta compensación?"))) {
      return;
    }

    try {
      cargando = true;
      error = null;

      console.log("Compensación a aprobar:", compensacion);

      // Identificar el ID correcto de la compensación
      const compensacionId =
        compensacion.id_hora_compensacion ||
        compensacion.id_compensacion ||
        compensacion.id ||
        compensacion.pk;
      console.log("ID de compensación:", compensacionId);

      if (!compensacionId) {
        throw new Error("No se pudo identificar el ID de la compensación");
      }

      const response = await guardiasService.aprobarCompensacion(
        compensacionId,
        { aprobado_por: 1 }, // TODO: Obtener del agente actual
        token,
      );

      await cargarCompensaciones();
      mostrarConfirmacion(
        "¡Aprobada!",
        "Compensación aprobada exitosamente",
        "success",
      );
      console.log("Compensación aprobada:", response);
    } catch (err) {
      console.error("Error aprobando compensación:", err);
      const mensaje =
        err.response?.data?.message || err.message || "Error desconocido";
      error = "Error al aprobar compensación: " + mensaje;
      mostrarConfirmacion(
        "Error",
        "Error al aprobar compensación: " + mensaje,
        "error",
      );
    } finally {
      cargando = false;
    }
  }

  async function rechazarCompensacion(compensacion) {
    const motivo = await confirmar(
      "¿Seguro de rechazar?",
      "Debe indicar un motivo",
      "warning",
      true,
    );
    if (!motivo || !motivo.trim()) {
      return;
    }

    try {
      cargando = true;
      error = null;

      console.log("Compensación a rechazar:", compensacion);

      // Identificar el ID correcto de la compensación
      const compensacionId =
        compensacion.id_hora_compensacion ||
        compensacion.id_compensacion ||
        compensacion.id ||
        compensacion.pk;
      console.log("ID de compensación:", compensacionId);

      if (!compensacionId) {
        throw new Error("No se pudo identificar el ID de la compensación");
      }

      const response = await guardiasService.rechazarCompensacion(
        compensacionId,
        {
          motivo_rechazo: motivo.trim(),
          rechazado_por: 1, // TODO: Obtener del agente actual
        },
        token,
      );

      await cargarCompensaciones();
      mostrarConfirmacion(
        "Rechazada",
        "Compensación rechazada correctamente",
        "success",
      );
      console.log("Compensación rechazada:", response);
    } catch (err) {
      console.error("Error rechazando compensación:", err);
      const mensaje =
        err.response?.data?.message || err.message || "Error desconocido";
      error = "Error al rechazar compensación: " + mensaje;
      mostrarConfirmacion(
        "Error",
        "Error al rechazar compensación: " + mensaje,
        "error",
      );
    } finally {
      cargando = false;
    }
  }

  function mostrarConfirmacion(titulo, mensaje, tipo = "success") {
    tituloConfirmacion = titulo;
    mensajeConfirmacion = mensaje;
    const tiposValidos = ["success", "error", "warning"];
    tipoConfirmacion = tiposValidos.includes(tipo) ? tipo : "success";
    mostrandoConfirmacion = true;
  }

  function cerrarConfirmacion() {
    mostrandoConfirmacion = false;
  }

  function confirmar(titulo, mensaje = "", tipo = "success", conInput = false) {
    tituloConfirmacion = titulo;
    mensajeConfirmacion = mensaje;

    const tiposValidos = ["success", "error", "warning"];
    tipoConfirmacion = tiposValidos.includes(tipo) ? tipo : "success";

    pedirInput = conInput;
    valorInput = "";

    mostrandoConfirmacion = true;

    return new Promise((resolve) => {
      resolverConfirmacion = resolve;
    });
  }

  function aceptarConfirmacion() {
    mostrandoConfirmacion = false;

    if (resolverConfirmacion) {
      if (pedirInput) {
        resolverConfirmacion(valorInput.trim());
      } else {
        resolverConfirmacion(true);
      }
    }

    // Reset state
    pedirInput = false;
    valorInput = "";
    resolverConfirmacion = null;
  }

  function cancelarConfirmacion() {
    mostrandoConfirmacion = false;

    if (resolverConfirmacion) {
      resolverConfirmacion(null);
    }

    // Reset state
    pedirInput = false;
    valorInput = "";
    resolverConfirmacion = null;
  }
</script>

<svelte:head>
  <title>Compensaciones por Horas Extra - GIGA</title>
</svelte:head>

<div class="compensaciones-container">
  <div class="header">
    <div class="header-title">
      <h1>⏱️ Compensaciones por Horas Extra</h1>
    </div>
    <button class="btn-nuevo" on:click={() => (mostrandoFormulario = true)}>
      ➕ Nueva Compensación
    </button>
  </div>

  <!-- Errores -->
  {#if error}
    <div class="alert alert-error">
      ⚠️ {error}
    </div>
  {/if}

  <!-- Formulario nueva compensación -->
  {#if mostrandoFormulario}
    <ModalNuevaCompensacion
      {token}
      {areas}
      on:close={() => (mostrandoFormulario = false)}
      on:success={() => {
        mostrandoFormulario = false;
        cargarCompensaciones();
      }}
    />
  {/if}

  <!-- Filtros para la lista -->
  <div class="filtros-lista">
    <div class="filtro-row">
      <div class="filtro-group">
        <label for="busqueda">🔍 Buscar agente</label>
        <input
          type="text"
          id="busqueda"
          bind:value={busqueda}
          placeholder="Buscar por nombre, apellido, DNI, email o legajo..."
          class="input-busqueda"
        />
      </div>
      <div class="filtro-group">
        <label for="filtro-area-lista">📍 Filtrar por Área:</label>
        <select id="filtro-area-lista" bind:value={filtroAreaLista}>
          <option value="">Todas las áreas</option>
          {#each areas as area}
            <option value={area.id_area}>{area.nombre}</option>
          {/each}
        </select>
      </div>

      <div class="filtro-group">
        <label for="filtro-estado-lista">🚦Estado:</label>
        <select id="filtro-estado-lista" bind:value={filtroEstadoLista}>
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendiente</option>
          <option value="aprobada">Aprobada</option>
          <option value="rechazada">Rechazada</option>
        </select>
      </div>

      <button
        class="btn-limpiar"
        on:click={limpiarFiltros}
        title="Limpiar Filtros"
      >
        🗑️ Limpiar filtros
      </button>
    </div>
  </div>
</div>

<!-- Lista de compensaciones -->
<div class="lista-compensaciones">
  <div class="lista-container">
    <div class="lista-header">
      <h2>Compensaciones Registradas ({compensaciones.length})</h2>
    </div>
    {#if cargando}
      <div class="loading">
        <div class="spinner"></div>
        Cargando compensaciones...
      </div>
    {:else if compensacionesFiltradas.length === 0}
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>
          {#if compensaciones.length === 0}
            No hay compensaciones registradas
          {:else}
            No hay compensaciones que coincidan con los filtros
          {/if}
        </h3>
        <p>
          {#if compensaciones.length === 0}
            Cuando se registre una compensación por horas extra aparecerá aquí
          {:else}
            Intente cambiar los filtros para ver más resultados
          {/if}
        </p>
      </div>
    {:else}
      <div class="table-container">
        <table class="compensaciones-table">
          <thead>
            <tr>
              <th>Agente</th>
              <th>Fecha</th>
              <th>Horas Extra</th>
              <th>Motivo</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each compensacionesFiltradas as compensacion}
              <tr>
                <td>
                  <div class="agente-info">
                    <strong
                      >ID: {compensacion.id_agente ||
                        compensacion.agente_id ||
                        "N/A"}</strong
                    >
                    {#if compensacion.agente_nombre}
                      <br /><small
                        >{compensacion.agente_apellido}, {compensacion.agente_nombre}</small
                      >
                    {/if}
                  </div>
                </td>
                <td>{formatearFecha(compensacion.fecha_servicio)}</td>
                <td>
                  <span class="horas-badge">
                    {compensacion.horas_extra || "N/A"}h
                  </span>
                  {#if compensacion.hora_fin_real}
                    <br /><small
                      >Finalizó: {formatearHora(
                        compensacion.hora_fin_real,
                      )}</small
                    >
                  {/if}
                </td>
                <td>
                  <span class="motivo-badge"
                    >{compensacion.motivo || "N/A"}</span
                  >
                  {#if compensacion.numero_acta}
                    <br /><small>Acta: {compensacion.numero_acta}</small>
                  {/if}
                </td>
                <td>
                  <span
                    class="estado-badge estado-{compensacion.estado ||
                      'pendiente'}"
                  >
                    {compensacion.estado || "Pendiente"}
                  </span>
                </td>
                <td>
                  <div class="acciones-grupo">
                    <button
                      class="btn-small btn-ver"
                      on:click={() => verDetalles(compensacion)}
                    >
                      👁️ Ver
                    </button>
                    {#if compensacion.estado === "pendiente"}
                      <button
                        class="btn-small btn-aprobar"
                        on:click={() => aprobarCompensacion(compensacion)}
                      >
                        ✅ Aprobar
                      </button>
                      <button
                        class="btn-small btn-rechazar"
                        on:click={() => rechazarCompensacion(compensacion)}
                      >
                        ❌ Rechazar
                      </button>
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<!-- Modal de detalles de compensación -->
{#if mostrandoDetalles && compensacionSeleccionada}
  <ModalDetalleCompensacion
    compensacion={compensacionSeleccionada}
    loading={cargando}
    on:close={cerrarDetalles}
    on:aprobar={({ detail }) => aprobarCompensacion(detail)}
    on:rechazar={({ detail }) => rechazarCompensacion(detail)}
  />
{/if}

{#if mostrandoConfirmacion}
  <div class="modal-confirmacion">
    <div class="modal-confirmacion-contenido {tipoConfirmacion}">
      <div class="modal-confirmacion-icono">
        {#if tipoConfirmacion === "success"}
          ✓
        {:else if tipoConfirmacion === "error"}
          ✕
        {:else if tipoConfirmacion === "warning"}
          ⚠
        {:else}
          ✓
        {/if}
      </div>
      <h3 class="modal-confirmacion-titulo">{tituloConfirmacion}</h3>
      <p class="modal-confirmacion-mensaje">{mensajeConfirmacion}</p>
      {#if pedirInput && tipoConfirmacion !== "success"}
        <textarea
          class="modal-input"
          bind:value={valorInput}
          placeholder="Ingrese el motivo del rechazo..."
          rows="4"
        ></textarea>
      {/if}
      <div class="modal-confirmacion-botones">
        <button class="btn-cancelar" on:click={cancelarConfirmacion}>
          Cancelar
        </button>
        <button class="modal-confirmacion-boton" on:click={aceptarConfirmacion}>
          Aceptar
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .compensaciones-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
  }

  .header-title {
    position: relative;
    background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
    color: white;
    padding: 30px 20px;
    margin: 0;
    margin-right: 10px;
    max-width: 1000px;
    border-radius: 28px;
    overflow: hidden;
    text-align: center;
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.1) inset,
      0 20px 60px rgba(30, 64, 175, 0.4);
  }

  .header-title::before {
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

  .header-title h1 {
    margin: 10px;
    font-weight: 800;
    font-size: 18px;
    letter-spacing: 0.2px;
    position: relative;
    padding-bottom: 12px;
    overflow: hidden;
    display: block;
    max-width: 100%;
    word-wrap: break-word;
  }

  @media (min-width: 480px) {
    .header-title h1 {
      font-size: 22px;
    }
  }

  @media (min-width: 640px) {
    .header-title h1 {
      font-size: 26px;
      display: inline-block;
    }
  }

  @media (min-width: 768px) {
    .header-title h1 {
      font-size: 30px;
    }
  }

  .header-title h1::after {
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

  .btn-nuevo {
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    background: #f68f3b;
    color: white;
    border: none;
    padding: 15px 25px;
    border-radius: 10px;
    font-size: 17px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #e79043, #f39c12);
    box-shadow: 0 2px 4px rgba(237, 160, 93, 0.756);
  }

  .btn-nuevo:hover {
    box-shadow: 0 4px 8px rgba(237, 160, 93, 0.756);
    transform: translateY(-1px);
  }

  .alert {
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-weight: 500;
  }

  .alert-error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }


  .btn-small,
  .btn-ver {
    padding: 8px 14px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .lista-compensaciones {
    margin-top: 0;
    max-width: 1400px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 20px;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .lista-container {
    background: transparent;
    padding: 0;
  }

  .lista-header {
    margin-bottom: 24px;
  }

  .lista-header h2 {
    color: #1e293b;
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    position: relative;
    display: inline-block;
    padding-bottom: 12px;
    overflow: hidden;
  }

  .lista-header h2::after {
    content: "";
    position: absolute;
    width: 100%;
    height: 3px;
    bottom: 0;
    left: -100%;
    background: linear-gradient(90deg, transparent, #000000, transparent);
    animation: moveLine 2s linear infinite;
  }

  .filtros-lista {
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .filtro-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 1.2rem;
    align-items: end;
    width: 100%;
  }

  .filtro-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .filtro-group label {
    font-size: 16px;
    font-weight: 600;
    color: #4b5563;
  }

  .filtro-group select,
  .filtro-group input,
  .input-busqueda {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 0.9rem;
    box-sizing: border-box;
  }

  .filtro-group select:focus,
  .filtro-group input:focus,
  .input-busqueda:focus {
    outline: none;
    border-color: #407bff;
    box-shadow: 0 0 0 3px rgba(64, 123, 255, 0.15);
  }

  .input-busqueda::placeholder {
    color: #9ca3af;
    font-size: 0.85rem;
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
    width: fit-content;
  }

  .btn-limpiar:hover {
    background: #5a6268;
    transform: translateY(-1px);
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    color: #6b7280;
    font-size: 16px;
    gap: 12px;
    background: white;
    border-radius: 12px;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 4px solid #e5e7eb;
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

  /* Modal de confirmación/alerta */
  .modal-confirmacion {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999;
    backdrop-filter: blur(4px);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .modal-confirmacion-contenido {
    background: #ffffff;
    padding: 32px;
    width: 380px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  }

  .modal-confirmacion-contenido.success {
    background: #d4edda;
    border: 4px solid #28a745;
  }

  .modal-confirmacion-contenido.error {
    background: #f8d7da;
    border: 4px solid #dc3545;
  }

  .modal-confirmacion-contenido.warning {
    background: #fff3cd;
    border: 4px solid #ffc107;
  }

  .modal-confirmacion-icono {
    font-size: 3rem;
    font-weight: bold;
    color: inherit;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-confirmacion-titulo {
    font-size: 20px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 8px;
  }

  .modal-confirmacion-mensaje {
    font-size: 15px;
    color: #475569;
    margin-bottom: 20px;
  }

  .modal-input {
    width: 93%;
    padding: 10px 14px;
    min-height: 80px;
    border-radius: 10px;
    border: 1px solid #cbd5e1;
    font-size: 14px;
    resize: vertical;
    margin-bottom: 20px;
    outline: none;
    transition: border 0.2s ease;
  }

  .modal-input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 4px rgba(59, 130, 246, 0.35);
  }

  .modal-confirmacion-botones {
    display: flex;
    justify-content: center;
    gap: 10px;
  }

  .btn-cancelar {
    padding: 10px 22px;
    background: #e2e8f0;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    color: #475569;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-cancelar:hover {
    background: #cbd5e1;
    transform: translateY(-2px);
  }

  .modal-confirmacion-boton {
    padding: 10px 28px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 3px 6px rgba(59, 130, 246, 0.3);
  }

  .modal-confirmacion-boton:hover {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
  }

  .empty-state {
    text-align: center;
    padding: 80px 40px;
    color: #6b7280;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  .empty-icon {
    font-size: 64px;
    margin-bottom: 20px;
  }

  .empty-state h3 {
    margin: 0 0 12px 0;
    color: #374151;
    font-size: 20px;
    font-weight: 600;
  }

  .empty-state p {
    margin: 0;
    font-size: 15px;
    color: #6b7280;
  }

  .table-container {
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
 scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .table-container::-webkit-scrollbar { display: none; }

  .table-container::-webkit-scrollbar {
    height: 8px;
    width: 8px;
  }

  .table-container::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 10px;
  }

  .table-container::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 10px;
  }

  .table-container::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  .compensaciones-table {
    width: 100%;
    border-collapse: collapse;
  }

  .compensaciones-table th {
    padding: 18px 20px;
    text-align: left;
    font-weight: 700;
    color: #1e293b;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 3px solid #3b82f6;
  }

  .compensaciones-table tbody tr {
    border-bottom: 1px solid #e5e7eb;
    transition: all 0.2s ease;
  }

  .compensaciones-table tbody tr:hover {
    background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
    transform: scale(1.005);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
  }

  .compensaciones-table td {
    padding: 18px 20px;
    font-size: 14px;
    color: #374151;
    vertical-align: middle;
  }

  .compensaciones-table tbody tr:hover {
    background: #f9fafb;
  }

  .agente-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .agente-info strong {
    display: block;
    color: #1e293b;
    font-size: 14px;
    font-weight: 600;
  }

  .agente-info small {
    color: #64748b;
    font-size: 13px;
  }

  .horas-badge {
    display: inline-block;
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
    color: #1e40af;
    padding: 8px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  }

  .motivo-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
    color: #374151;
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;
    border: 1px solid #d1d5db;
  }

  .estado-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    text-transform: capitalize;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    letter-spacing: 0.3px;
  }

  .estado-pendiente {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    color: #92400e;
    border: 1px solid #fcd34d;
    animation: pulse 2s infinite;
  }

  .estado-aprobada {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    color: #065f46;
    border: 1px solid #6ee7b7;
  }

  .estado-rechazada {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    color: #991b1b;
    border: 1px solid #fca5a5;
  }

  @keyframes pulse {
    0%,
    100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }

  .btn-small {
    padding: 8px 14px;
    font-size: 13px;
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;
  }

  .btn-ver {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  }

  .btn-ver:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
  }

  .btn-aprobar {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
  }

  .btn-aprobar:hover {
    background: linear-gradient(135deg, #059669, #047857);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
  }

  .btn-rechazar {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
    box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
  }

  .btn-rechazar:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
  }

  .acciones-grupo {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }
  /* Modal de detalles */
  .modal-detalles {
    background: white;
    border-radius: 16px;
    max-width: 900px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    border: none;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .modal-detalles::-webkit-scrollbar {
    display: none;
  }

  .detalle-seccion {
    margin-bottom: 24px;
    padding: 20px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
  }

  .detalle-seccion h3 {
    margin: 0 0 16px 0;
    color: #1e40af;
    font-size: 18px;
    font-weight: 700;
  }

  .detalle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }

  .detalle-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .detalle-item.detalle-full {
    grid-column: 1 / -1;
  }

  .descripcion-texto {
    padding: 12px;
    background: white;
    border-radius: 6px;
    border: 1px solid #d1d5db;
    color: #374151;
    font-size: 14px;
    line-height: 1.5;
    white-space: pre-wrap;
  }

  .descripcion-texto.rechazo {
    background: #fef2f2;
    border-color: #fecaca;
    color: #991b1b;
  }

  .monto-badge {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
  }

  @media (max-width: 1024px) {
    .lista-header h2 {
      font-size: 24px;
    }

    .compensaciones-table th,
    .compensaciones-table td {
      padding: 14px 16px;
      font-size: 13px;
    }

    .filtro-row {
      grid-template-columns: 2fr 1fr 1fr;
      gap: 1rem;
    }

    .btn-limpiar {
      grid-column: 1 / -1;
      justify-self: center;
      max-width: 200px;
    }
  }

  @media (max-width: 768px) {
    .lista-compensaciones {
      padding: 0 10px;
    }

    .lista-header h2 {
      font-size: 20px;
    }

    .compensaciones-table th,
    .compensaciones-table td {
      padding: 12px;
      font-size: 12px;
    }

    .btn-small {
      padding: 6px 10px;
      font-size: 11px;
    }

    .acciones-grupo {
      flex-direction: column;
      gap: 6px;
    }

    .filtro-row {
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }

    .filtro-group:first-child {
      grid-column: 1 / -1;
    }

    .btn-limpiar {
      grid-column: 1 / -1;
      justify-self: center;
      max-width: 200px;
    }
  }
</style>
