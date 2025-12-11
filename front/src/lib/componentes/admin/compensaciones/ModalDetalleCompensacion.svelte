<script>
  import { createEventDispatcher } from "svelte";
  import { fade, scale } from "svelte/transition";

  export let compensacion;
  export let loading = false;

  const dispatch = createEventDispatcher();

  function cerrar() {
    dispatch("close");
  }

  function aprobar() {
    dispatch("aprobar", compensacion);
  }

  function rechazar() {
    dispatch("rechazar", compensacion);
  }

  function formatearFecha(fecha) {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-AR");
  }

  function formatearHora(hora) {
    if (!hora) return "-";
    return hora.slice(0, 5); // HH:MM
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
      <h3>Detalles de Compensación</h3>
      <button class="close-button" on:click={cerrar}>&times;</button>
    </div>

    <div class="modal-body">
      <div class="detalle-seccion">
        <h4>Información General</h4>
        <div class="detalle-grid">
          <div class="detalle-item">
            <label for="ID-compensacion">ID Compensación:</label>
            <span>
              {compensacion.id_hora_compensacion ||
                compensacion.id_compensacion ||
                compensacion.id ||
                "N/A"}
            </span>
          </div>
          <div class="detalle-item">
            <label for="estado">Estado:</label>
            <span
              class="estado-badge estado-{compensacion.estado || 'pendiente'}"
            >
              {compensacion.estado || "Pendiente"}
            </span>
          </div>
          <div class="detalle-item">
            <label for="fecha">Fecha de Solicitud:</label>
            <span>
              {formatearFecha(
                compensacion.fecha_solicitud || compensacion.created_at,
              )}
            </span>
          </div>
          <div class="detalle-item">
            <label for="solicita">Solicitado por:</label>
            <span>ID: {compensacion.solicitado_por || "N/A"}</span>
          </div>
        </div>
      </div>

      <div class="detalle-seccion">
        <h4>Detalles de la Guardia</h4>
        <div class="detalle-grid">
          <div class="detalle-item">
            <label for="guardia">ID Guardia:</label>
            <span>{compensacion.id_guardia || "N/A"}</span>
          </div>
          <div class="detalle-item">
            <label for="agente">Agente:</label>
            <span>
              {#if compensacion.agente_nombre}
                {compensacion.agente_apellido}, {compensacion.agente_nombre}
              {:else}
                ID: {compensacion.id_agente ||
                  compensacion.agente_id ||
                  "N/A"}
              {/if}
            </span>
          </div>
          <div class="detalle-item">
            <label for="fechaser">Fecha de Servicio:</label>
            <span>{formatearFecha(compensacion.fecha_servicio)}</span>
          </div>
          <div class="detalle-item">
            <label for="hora">Hora Real de Fin:</label>
            <span>{formatearHora(compensacion.hora_fin_real)}</span>
          </div>
        </div>
      </div>

      <div class="detalle-seccion">
        <h4>Motivo y Justificación</h4>
        <div class="detalle-grid">
          <div class="detalle-item detalle-full">
            <label for="tipo">Tipo de Motivo:</label>
            <span class="motivo-badge">{compensacion.motivo || "N/A"}</span>
          </div>
          <div class="detalle-item detalle-full">
            <label for="descr">Descripción del Motivo:</label>
            <div class="descripcion-texto">
              {compensacion.descripcion_motivo || "Sin descripción"}
            </div>
          </div>
          {#if compensacion.numero_acta}
            <div class="detalle-item detalle-full">
              <label for="numacta">Número de Acta:</label>
              <span>{compensacion.numero_acta}</span>
            </div>
          {/if}
        </div>
      </div>

      <div class="detalle-seccion">
        <h4>Cálculo de Horas</h4>
        <div class="detalle-grid">
          <div class="detalle-item">
            <label for="horasextra">Horas Extra Calculadas:</label>
            <span class="horas-badge">
              {compensacion.horas_extra || "Pendiente de cálculo"}h
            </span>
          </div>
          {#if compensacion.monto_compensacion}
            <div class="detalle-item">
              <label for="monto">Monto de Compensación:</label>
              <span class="monto-badge">
                ${compensacion.monto_compensacion}
              </span>
            </div>
          {/if}
        </div>
      </div>

      {#if compensacion.estado !== "pendiente"}
        <div class="detalle-seccion">
          <h4>Estado de Aprobación</h4>
          <div class="detalle-grid">
            {#if compensacion.aprobado_por}
              <div class="detalle-item">
                <label for="aprobado">Aprobado por:</label>
                <span>ID: {compensacion.aprobado_por}</span>
              </div>
            {/if}
            {#if compensacion.fecha_aprobacion}
              <div class="detalle-item">
                <label for="date-aprobacion">Fecha de Aprobación:</label>
                <span>
                  {formatearFecha(compensacion.fecha_aprobacion)}
                </span>
              </div>
            {/if}
            {#if compensacion.motivo_rechazo}
              <div class="detalle-item detalle-full">
                <label for="rechazo">Motivo de Rechazo:</label>
                <div class="descripcion-texto rechazo">
                  {compensacion.motivo_rechazo}
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/if}

      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={cerrar}>Cerrar</button>

        {#if compensacion.estado === "pendiente"}
          <button
            class="btn btn-danger"
            on:click={rechazar}
            disabled={loading}
          >
            ❌ Rechazar
          </button>
          <button
            class="btn btn-success"
            on:click={aprobar}
            disabled={loading}
          >
            ✅ Aprobar
          </button>
        {/if}
      </div>
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
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    border: none;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .modal-content::-webkit-scrollbar {
    display: none;
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
    border-bottom: none;
  }

  .modal-header h3 {
    margin: 0;
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
  }

  .close-button {
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

  .close-button:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
  }

  /* Body */
  .modal-body {
    padding: 2rem;
  }

  .detalle-seccion {
    margin-bottom: 2rem;
    padding: 1.25rem;
    background: #f9fafb;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
  }

  .detalle-seccion h4 {
    margin: 0 0 1rem 0;
    color: #374151;
    font-size: 1rem;
    font-weight: 700;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .detalle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .detalle-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .detalle-full {
    grid-column: 1 / -1;
  }

  .detalle-item label {
    font-size: 0.85rem;
    color: #64748b;
    font-weight: 600;
  }

  .detalle-item span {
    font-size: 1rem;
    color: #1e293b;
    font-weight: 500;
  }

  .descripcion-texto {
    background: white;
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.5;
    color: #334155;
  }

  .descripcion-texto.rechazo {
    background: #fef2f2;
    border-color: #fecaca;
    color: #991b1b;
  }

  /* Badges */
  .estado-badge {
    display: inline-flex;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: capitalize;
    width: fit-content;
  }

  .estado-pendiente {
    background-color: #fef3c7;
    color: #92400e;
  }

  .estado-aprobada {
    background-color: #d1fae5;
    color: #065f46;
  }

  .estado-rechazada {
    background-color: #fee2e2;
    color: #991b1b;
  }

  .motivo-badge {
    background-color: #e0f2fe;
    color: #0369a1;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 600;
    width: fit-content;
  }

  .horas-badge {
    background-color: #f3e8ff;
    color: #7e22ce;
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 700;
    width: fit-content;
  }

  .monto-badge {
    background-color: #dcfce7;
    color: #15803d;
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-family: monospace;
    font-size: 1.1rem;
    width: fit-content;
  }

  /* Footer & Buttons */
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }

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

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .btn-secondary {
    background: #6c757d;
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #5a6268;
    transform: translateY(-2px);
  }

  .btn-success {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
  }

  .btn-success:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
  }

  .btn-danger {
    background: #ef4444;
    color: white;
  }

  .btn-danger:hover:not(:disabled) {
    background: #dc2626;
    transform: translateY(-2px);
  }
</style>
