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
  // Datos para el formulario de nueva compensación
  let areas = [];
  let agentes = {};
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
  let filtrosBusqueda = {
    agenteId: 0,
    areaId: 0,
    estado: "",
  };
  onMount(async () => {
    // Obtener token de sesión
    token = localStorage.getItem("token");
    await cargarCompensaciones();
    await cargarAreas();
    await getAgentes();
  });
  async function cargarCompensaciones() {
    cargando = true;
    error = null;
    try {
      const response = await guardiasService.getCompensaciones("", token);
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
    } catch (err) {
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
      areas = datos;
    } catch (err) {
      areas = [];
    } finally {
      cargandoAreas = false;
    }
  }
  async function getAgentes() {
    const { data } = await personasService.getAgentes(token);
    agentes = data.results;
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
    let filtrosBusqueda = {
      agenteId: 0,
      areaId: 0,
      estado: "",
    };
    filtroEstadoLista = "";
  }
  function buildQuery() {
    const params = new URLSearchParams();
    if (filtrosBusqueda.agenteId && filtrosBusqueda.agenteId !== 0) {
      params.append("agente_id", filtrosBusqueda.agenteId);
    }
    if (filtrosBusqueda.areaId && filtrosBusqueda.areaId !== 0) {
      params.append("area_id", filtrosBusqueda.areaId);
    }
    if (filtrosBusqueda.estado && filtrosBusqueda.estado !== "") {
      params.append("estado", filtrosBusqueda.estado);
    }
    const query = params.toString();
    return query ? `?${query}` : "";
  }
  async function buscarCompensaciones() {
    const query = buildQuery();
    const { data } = await guardiasService.getCompensaciones(query, token);
    compensaciones = data.results;
  }
  function verDetalles(compensacion) {
    compensacionSeleccionada = compensacion;
    mostrandoDetalles = true;
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
      // Identificar el ID correcto de la compensación
      const compensacionId =
        compensacion.id_hora_compensacion ||
        compensacion.id_compensacion ||
        compensacion.id ||
        compensacion.pk;
      if (!compensacionId) {
        throw new Error("No se pudo identificar el ID de la compensación");
      }
      const response = await guardiasService.aprobarCompensacion(
        compensacionId,
        { aprobado_por: 1 }, // TODO: Obtener del agente actual
        token
      );
      await cargarCompensaciones();
      mostrarConfirmacion(
        "¡Aprobada!",
        "Compensación aprobada exitosamente",
        "success"
      );
    } catch (err) {
      const mensaje =
        err.response?.data?.message || err.message || "Error desconocido";
      error = "Error al aprobar compensación: " + mensaje;
      mostrarConfirmacion(
        "Error",
        "Error al aprobar compensación: " + mensaje,
        "error"
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
      true
    );
    if (!motivo || !motivo.trim()) {
      return;
    }
    try {
      cargando = true;
      error = null;
      // Identificar el ID correcto de la compensación
      const compensacionId =
        compensacion.id_hora_compensacion ||
        compensacion.id_compensacion ||
        compensacion.id ||
        compensacion.pk;
      if (!compensacionId) {
        throw new Error("No se pudo identificar el ID de la compensación");
      }
      const response = await guardiasService.rechazarCompensacion(
        compensacionId,
        {
          motivo_rechazo: motivo.trim(),
          rechazado_por: 1, // TODO: Obtener del agente actual
        },
        token
      );
      await cargarCompensaciones();
      mostrarConfirmacion(
        "Rechazada",
        "Compensación rechazada correctamente",
        "success"
      );
    } catch (err) {
      const mensaje =
        err.response?.data?.message || err.message || "Error desconocido";
      error = "Error al rechazar compensación: " + mensaje;
      mostrarConfirmacion(
        "Error",
        "Error al rechazar compensación: " + mensaje,
        "error"
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
  <div class="header-compensaciones">
    <div class="titulo-compensaciones">⏱️ Compensaciones por Horas Extra</div>
    <button class="btn-nueva-compensacion"> ➕ Nueva Compensación </button>
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
        <select id="filtro-agente-lista" bind:value={filtrosBusqueda.agenteId}>
          <option value="">Todos los agentes</option>
          {#each agentes as agente}
            <option value={agente.id_agente}
              >{agente.nombre} {agente.apellido}</option
            >
          {/each}
        </select>
      </div>
      <div class="filtro-group">
        <label for="filtro-area-lista">📍 Filtrar por Área:</label>
        <select id="filtro-area-lista" bind:value={filtrosBusqueda.areaId}>
          <option value="">Todas las áreas</option>
          {#each areas as area}
            <option value={area.id_area}>{area.nombre}</option>
          {/each}
        </select>
      </div>
      <div class="filtro-group">
        <label for="filtro-estado-lista">🚦Estado:</label>
        <select id="filtro-estado-lista" bind:value={filtrosBusqueda.estado}>
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
      <button
        class="btn-limpiar"
        on:click={buscarCompensaciones}
        title="Limpiar Filtros"
      >
        🔎 Buscar
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
                    {compensacion.horas_extra ? Math.floor(compensacion.horas_extra) : "N/A"}h
                  </span>
                  {#if compensacion.hora_fin_real}
                    <br /><small
                      >Finalizó: {formatearHora(
                        compensacion.hora_fin_real
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
.lista-compensaciones {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}
.header-compensaciones {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}
.titulo-compensaciones {
  position: relative;
  flex: 1;
  text-align: center;
  background: linear-gradient(135deg, #5a84e8, #5c8df0);
  color: #fff;
  padding: 18px 22px;
  border-radius: 24px;
  font-size: 1.1rem;
  font-weight: 800;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.12) inset,
    0 16px 50px rgba(30, 64, 175, 0.25);
}
.btn-nueva-compensacion {
  background: linear-gradient(135deg, #f5a43a, #f0932b);
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 14px 18px;
  font-size: 0.95rem;
  font-weight: 800;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 10px 25px rgba(240, 147, 43, 0.25);
}
.btn-nueva-compensacion:hover {
  transform: translateY(-1px);
  opacity: 0.95;
}
@media (max-width: 768px) {
  .header-compensaciones {
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
  }
  .btn-nueva-compensacion {
    width: 100%;
    text-align: center;
  }
}
.alert {
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-weight: 600;
}
.alert-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}
.filtros-lista {
  background: #fff;
  padding: 14px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  margin-bottom: 18px;
}
.filtro-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.filtro-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filtro-group label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #495057;
}
.filtro-group select {
  height: 44px;
  padding: 0 12px;
  font-size: 0.95rem;
  border-radius: 10px;
  border: 1px solid #dee2e6;
  background: #fff;
  width: 100%;
  box-sizing: border-box;
}
.filtro-group select:focus {
  outline: none;
  border-color: #407bff;
  box-shadow: 0 0 0 3px rgba(64, 123, 255, 0.15);
}
.btn-limpiar {
  height: 44px;
  padding: 0 14px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 800;
  white-space: nowrap;
}
.btn-limpiar:first-of-type {
  background: #e9ecef;
  color: #495057;
}
.btn-limpiar:last-of-type {
  background: #007bff;
  color: #fff;
}
.btn-limpiar:hover {
  opacity: 0.92;
}
@media (min-width: 900px) {
  .filtro-row {
    grid-template-columns: 1.6fr 1.2fr 1fr auto auto;
    align-items: end;
  }
}
@media (max-width: 900px) and (min-width: 601px) {
  .filtro-row {
    grid-template-columns: 1fr 1fr;
  }
  .filtro-group:first-child {
    grid-column: 1 / -1;
  }
  .btn-limpiar {
    grid-column: 1 / -1;
    justify-self: center;
    width: min(320px, 100%);
  }
}
@media (max-width: 600px) {
  .btn-limpiar {
    width: 100%;
    text-align: center;
  }
}
.lista-container {
  background: transparent;
  padding: 0;
}
.lista-header {
  margin-bottom: 18px;
}
.lista-header h2 {
  color: #1e293b;
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  display: inline-block;
  padding-bottom: 10px;
  position: relative;
}
.lista-header h2::after {
  content: "";
  position: absolute;
  left: -100%;
  bottom: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #000, transparent);
  animation: moveLine 2s linear infinite;
}
@keyframes moveLine {
  0% { left: -100%; }
  100% { left: 100%; }
}
.table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.compensaciones-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px; 
}
.compensaciones-table th {
  padding: 16px 18px;
  text-align: left;
  font-weight: 800;
  color: #1e293b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 3px solid #3b82f6;
}
.compensaciones-table td {
  padding: 16px 18px;
  font-size: 14px;
  color: #374151;
  vertical-align: middle;
}
.compensaciones-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}
.compensaciones-table tbody tr:hover {
  background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
}
.horas-badge {
  display: inline-block;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
  padding: 7px 12px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 12px;
}
.motivo-badge {
  display: inline-block;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  color: #374151;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #d1d5db;
}
.estado-badge {
  display: inline-block;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  text-transform: capitalize;
}
.estado-pendiente {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
  border: 1px solid #fcd34d;
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
.acciones-grupo {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.btn-small {
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-ver {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
}
.btn-aprobar {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
}
.btn-rechazar {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff;
}
.btn-small:hover {
  transform: translateY(-1px);
  opacity: 0.95;
}
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 16px;
  gap: 12px;
  background: #fff;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.empty-state {
  text-align: center;
  padding: 70px 30px;
  color: #6b7280;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 14px;
}
.empty-state h3 {
  margin: 0 0 10px 0;
  color: #374151;
  font-size: 20px;
  font-weight: 800;
}
.empty-state p {
  margin: 0;
  font-size: 14px;
}
.modal-confirmacion {
  position: fixed;
  inset: 0;
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
  padding: 28px;
  width: min(420px, 92vw);
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
}
.modal-confirmacion-titulo {
  font-size: 20px;
  font-weight: 900;
  color: #1e293b;
  margin: 8px 0;
}
.modal-confirmacion-mensaje {
  font-size: 14px;
  color: #475569;
  margin-bottom: 18px;
}
.modal-input {
  width: 100%;
  padding: 10px 14px;
  min-height: 90px;
  border-radius: 10px;
  border: 1px solid #cbd5e1;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 18px;
  outline: none;
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
  border-radius: 10px;
  font-size: 14px;
  font-weight: 800;
  color: #475569;
  cursor: pointer;
}
.modal-confirmacion-boton {
  padding: 10px 28px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}
@media (max-width: 768px) {
  .lista-compensaciones {
    padding: 0 10px;
  }
  .compensaciones-table {
    min-width: 780px;
  }
  .acciones-grupo {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-small {
    width: 100%;
    text-align: center;
  }
}
</style>
