<script>
  import { onMount } from 'svelte';
  import { API } from '$lib/api.js';

  // Estado del componente
  let compensaciones = [];
  let mostrandoFormulario = false;
  let cargando = false;
  let error = null;

  // Filtros
  let filtroEstado = '';
  let filtroMes = '';
  let filtroAnio = new Date().getFullYear();
  
  // Formulario nueva compensación
  let nuevaCompensacion = {
    id_agente: '',
    fecha_servicio: '',
    hora_fin_real: '',
    motivo: 'emergencia',
    descripcion_motivo: '',
    numero_acta: '',
    tipo_compensacion: 'plus',
    solicitado_por: ''
  };

  // Estados y opciones
  const estadosCompensacion = [
    { value: '', label: 'Todos los estados' },
    { value: 'pendiente', label: 'Pendientes' },
    { value: 'aprobada', label: 'Aprobadas' },
    { value: 'rechazada', label: 'Rechazadas' },
    { value: 'pagada', label: 'Pagadas' }
  ];

  const motivosCompensacion = [
    { value: 'siniestro', label: 'Siniestro/Accidente' },
    { value: 'emergencia', label: 'Emergencia Operativa' },
    { value: 'operativo', label: 'Operativo Especial' },
    { value: 'refuerzo', label: 'Refuerzo de Seguridad' },
    { value: 'otro', label: 'Otro Motivo' }
  ];

  const meses = [
    { value: '', label: 'Todos los meses' },
    { value: '1', label: 'Enero' },
    { value: '2', label: 'Febrero' },
    { value: '3', label: 'Marzo' },
    { value: '4', label: 'Abril' },
    { value: '5', label: 'Mayo' },
    { value: '6', label: 'Junio' },
    { value: '7', label: 'Julio' },
    { value: '8', label: 'Agosto' },
    { value: '9', label: 'Septiembre' },
    { value: '10', label: 'Octubre' },
    { value: '11', label: 'Noviembre' },
    { value: '12', label: 'Diciembre' }
  ];

  onMount(() => {
    cargarCompensaciones();
  });

  async function cargarCompensaciones() {
    cargando = true;
    error = null;
    try {
      let url = '/api/guardias/compensaciones/';
      const params = new URLSearchParams();
      
      if (filtroEstado) params.append('estado', filtroEstado);
      if (filtroMes) params.append('mes', filtroMes);
      if (filtroAnio) params.append('anio', filtroAnio);
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const response = await API.get(url);
      compensaciones = response.results || response;
    } catch (err) {
      error = 'Error al cargar compensaciones: ' + err.message;
    } finally {
      cargando = false;
    }
  }

  async function crearCompensacion() {
    cargando = true;
    error = null;
    
    try {
      await API.post('/api/guardias/compensaciones/crear-compensacion/', nuevaCompensacion);
      
      // Limpiar formulario y recargar lista
      nuevaCompensacion = {
        id_agente: '',
        fecha_servicio: '',
        hora_fin_real: '',
        motivo: 'emergencia',
        descripcion_motivo: '',
        numero_acta: '',
        tipo_compensacion: 'plus',
        solicitado_por: ''
      };
      
      mostrandoFormulario = false;
      await cargarCompensaciones();
      
      alert('Compensación creada exitosamente');
    } catch (err) {
      error = 'Error al crear compensación: ' + err.message;
    } finally {
      cargando = false;
    }
  }

  async function aprobarCompensaciones(ids, accion = 'aprobar') {
    if (!confirm(`¿Está seguro de ${accion} las compensaciones seleccionadas?`)) {
      return;
    }

    cargando = true;
    error = null;

    try {
      await API.post('/api/guardias/compensaciones/aprobar-lote/', {
        compensacion_ids: ids,
        accion: accion,
        observaciones: accion === 'rechazar' ? prompt('Motivo del rechazo:') : '',
        agente_id: 1 // TODO: Obtener del usuario logueado
      });

      await cargarCompensaciones();
      alert(`Compensaciones ${accion === 'aprobar' ? 'aprobadas' : 'rechazadas'} exitosamente`);
    } catch (err) {
      error = `Error al ${accion} compensaciones: ` + err.message;
    } finally {
      cargando = false;
    }
  }

  function formatearFecha(fecha) {
    return new Date(fecha).toLocaleDateString('es-AR');
  }

  function formatearHora(hora) {
    return hora.slice(0, 5); // HH:MM
  }

  function obtenerClaseEstado(estado) {
    const clases = {
      pendiente: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      aprobada: 'bg-green-100 text-green-800 border-green-300',
      rechazada: 'bg-red-100 text-red-800 border-red-300',
      pagada: 'bg-blue-100 text-blue-800 border-blue-300'
    };
    return clases[estado] || 'bg-gray-100 text-gray-800 border-gray-300';
  }

  // Aplicar filtros
  function aplicarFiltros() {
    cargarCompensaciones();
  }

  function limpiarFiltros() {
    filtroEstado = '';
    filtroMes = '';
    filtroAnio = new Date().getFullYear();
    cargarCompensaciones();
  }
</script>

<div class="compensaciones-container">
  <div class="header">
    <h1>Gestión de Horas de Compensación</h1>
    <p class="subtitle">
      Sistema para gestionar horas extras por emergencias que exceden el límite reglamentario de 10 horas
    </p>
  </div>

  <!-- Filtros -->
  <div class="filtros-section">
    <h3>Filtros</h3>
    <div class="filtros-grid">
      <div class="campo">
        <label for="filtroEstado">Estado</label>
        <select bind:value={filtroEstado} on:change={aplicarFiltros}>
          {#each estadosCompensacion as estado}
            <option value={estado.value}>{estado.label}</option>
          {/each}
        </select>
      </div>
      
      <div class="campo">
        <label for="filtroMes">Mes</label>
        <select bind:value={filtroMes} on:change={aplicarFiltros}>
          {#each meses as mes}
            <option value={mes.value}>{mes.label}</option>
          {/each}
        </select>
      </div>

      <div class="campo">
        <label for="filtroAnio">Año</label>
        <input type="number" bind:value={filtroAnio} min="2020" max="2030" on:change={aplicarFiltros} />
      </div>

      <div class="campo">
        <button class="btn-secondary" on:click={limpiarFiltros}>Limpiar</button>
        <button class="btn-primary" on:click={() => mostrandoFormulario = true}>Nueva Compensación</button>
      </div>
    </div>
  </div>

  <!-- Errores -->
  {#if error}
    <div class="alert alert-error">
      {error}
    </div>
  {/if}

  <!-- Formulario nueva compensación -->
  {#if mostrandoFormulario}
    <div class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Nueva Compensación por Horas Extra</h2>
          <button class="btn-close" on:click={() => mostrandoFormulario = false}>×</button>
        </div>

        <form on:submit|preventDefault={crearCompensacion} class="modal-body">
          <div class="form-grid">
            <div class="campo">
              <label for="id_agente">ID Agente *</label>
              <input 
                type="number" 
                bind:value={nuevaCompensacion.id_agente} 
                required 
                placeholder="ID del agente que trabajó las horas extra"
              />
            </div>

            <div class="campo">
              <label for="fecha_servicio">Fecha del Servicio *</label>
              <input 
                type="date" 
                bind:value={nuevaCompensacion.fecha_servicio} 
                required 
              />
            </div>

            <div class="campo">
              <label for="hora_fin_real">Hora Real de Finalización *</label>
              <input 
                type="time" 
                bind:value={nuevaCompensacion.hora_fin_real} 
                required 
                placeholder="HH:MM"
              />
            </div>

            <div class="campo">
              <label for="motivo">Motivo *</label>
              <select bind:value={nuevaCompensacion.motivo} required>
                {#each motivosCompensacion as motivo}
                  <option value={motivo.value}>{motivo.label}</option>
                {/each}
              </select>
            </div>

            <div class="campo campo-wide">
              <label for="descripcion_motivo">Descripción Detallada *</label>
              <textarea 
                bind:value={nuevaCompensacion.descripcion_motivo} 
                required 
                rows="3"
                placeholder="Describa detalladamente el motivo que causó la extensión del horario..."
              ></textarea>
            </div>

            <div class="campo">
              <label for="numero_acta">Número de Acta/Expediente</label>
              <input 
                type="text" 
                bind:value={nuevaCompensacion.numero_acta} 
                placeholder="Opcional"
              />
            </div>

            <div class="campo">
              <label for="solicitado_por">Solicitado por (ID Agente) *</label>
              <input 
                type="number" 
                bind:value={nuevaCompensacion.solicitado_por} 
                required 
                placeholder="ID del agente que solicita"
              />
            </div>

            <div class="campo">
              <label for="tipo_compensacion">Tipo de Compensación</label>
              <select bind:value={nuevaCompensacion.tipo_compensacion}>
                <option value="plus">Plus Adicional</option>
                <option value="pago">Pago Directo</option>
                <option value="franco">Franco Compensatorio</option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" on:click={() => mostrandoFormulario = false}>Cancelar</button>
            <button type="submit" class="btn-primary" disabled={cargando}>
              {cargando ? 'Creando...' : 'Crear Compensación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <!-- Lista de compensaciones -->
  <div class="compensaciones-lista">
    <h3>
      Compensaciones Registradas ({compensaciones.length})
    </h3>

    {#if cargando}
      <div class="loading">Cargando compensaciones...</div>
    {:else if compensaciones.length === 0}
      <div class="empty-state">
        No hay compensaciones registradas con los filtros aplicados
      </div>
    {:else}
      <div class="table-container">
        <table class="compensaciones-table">
          <thead>
            <tr>
              <th>Agente</th>
              <th>Fecha Servicio</th>
              <th>Horas Extra</th>
              <th>Motivo</th>
              <th>Estado</th>
              <th>Solicitado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each compensaciones as compensacion}
              <tr>
                <td>
                  <div class="agente-info">
                    <strong>{compensacion.agente_apellido}, {compensacion.agente_nombre}</strong>
                    <small>Leg: {compensacion.agente_legajo}</small>
                  </div>
                </td>
                <td>{formatearFecha(compensacion.fecha_servicio)}</td>
                <td class="horas-extra">
                  <span class="horas-badge">{compensacion.horas_extra}h</span>
                  <small>
                    {formatearHora(compensacion.hora_inicio_programada)} - 
                    {formatearHora(compensacion.hora_fin_programada)} → 
                    {formatearHora(compensacion.hora_fin_real)}
                  </small>
                </td>
                <td>
                  <span class="motivo-badge">{compensacion.motivo_display}</span>
                  {#if compensacion.numero_acta}
                    <small>Acta: {compensacion.numero_acta}</small>
                  {/if}
                </td>
                <td>
                  <span class="estado-badge {obtenerClaseEstado(compensacion.estado)}">
                    {compensacion.estado_display}
                  </span>
                </td>
                <td>
                  <small>{formatearFecha(compensacion.fecha_solicitud)}</small>
                  <br>
                  <small>{compensacion.solicitado_por_apellido}</small>
                </td>
                <td>
                  {#if compensacion.estado === 'pendiente'}
                    <div class="acciones">
                      <button 
                        class="btn-small btn-success" 
                        on:click={() => aprobarCompensaciones([compensacion.id_hora_compensacion], 'aprobar')}
                      >
                        Aprobar
                      </button>
                      <button 
                        class="btn-small btn-danger" 
                        on:click={() => aprobarCompensaciones([compensacion.id_hora_compensacion], 'rechazar')}
                      >
                        Rechazar
                      </button>
                    </div>
                  {:else}
                    <span class="text-muted">—</span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<style>
  .compensaciones-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .header h1 {
    color: #2d3748;
    margin-bottom: 8px;
    font-size: 24px;
  }

  .subtitle {
    color: #718096;
    margin-bottom: 24px;
    font-size: 14px;
  }

  .filtros-section {
    background: #f7fafc;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid #e2e8f0;
  }

  .filtros-section h3 {
    margin: 0 0 12px 0;
    color: #4a5568;
    font-size: 16px;
  }

  .filtros-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    align-items: end;
  }

  .campo label {
    display: block;
    margin-bottom: 4px;
    font-weight: 500;
    color: #4a5568;
    font-size: 14px;
  }

  .campo input, .campo select, .campo textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
  }

  .campo input:focus, .campo select:focus, .campo textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .btn-primary, .btn-secondary, .btn-small, .btn-success, .btn-danger {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-block;
  }

  .btn-primary {
    background: #3b82f6;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn-secondary {
    background: #6b7280;
    color: white;
  }

  .btn-secondary:hover {
    background: #4b5563;
  }

  .btn-small {
    padding: 4px 8px;
    font-size: 12px;
    margin: 2px;
  }

  .btn-success {
    background: #10b981;
    color: white;
  }

  .btn-success:hover {
    background: #059669;
  }

  .btn-danger {
    background: #ef4444;
    color: white;
  }

  .btn-danger:hover {
    background: #dc2626;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .alert {
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 16px;
  }

  .alert-error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 90%;
    overflow-y: auto;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    margin: 0;
    color: #1f2937;
  }

  .btn-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6b7280;
    padding: 4px;
  }

  .modal-body {
    padding: 20px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }

  .campo-wide {
    grid-column: 1 / -1;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
  }

  .compensaciones-lista h3 {
    color: #374151;
    margin-bottom: 16px;
  }

  .loading, .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #6b7280;
    font-style: italic;
  }

  .table-container {
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .compensaciones-table {
    width: 100%;
    border-collapse: collapse;
  }

  .compensaciones-table th {
    background: #f9fafb;
    padding: 12px;
    text-align: left;
    font-weight: 600;
    color: #374151;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }

  .compensaciones-table td {
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }

  .compensaciones-table tbody tr:hover {
    background: #f9fafb;
  }

  .agente-info strong {
    display: block;
    color: #374151;
  }

  .agente-info small {
    color: #6b7280;
    font-size: 12px;
  }

  .horas-extra {
    text-align: center;
  }

  .horas-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    padding: 4px 8px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 12px;
  }

  .horas-extra small {
    display: block;
    color: #6b7280;
    font-size: 11px;
    margin-top: 4px;
  }

  .motivo-badge {
    display: inline-block;
    background: #f3f4f6;
    color: #374151;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .estado-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid;
  }

  .acciones {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .text-muted {
    color: #9ca3af;
  }

  @media (max-width: 768px) {
    .filtros-grid {
      grid-template-columns: 1fr;
    }

    .form-grid {
      grid-template-columns: 1fr;
    }

    .modal {
      width: 95%;
      margin: 10px;
    }

    .compensaciones-table {
      font-size: 12px;
    }

    .compensaciones-table th,
    .compensaciones-table td {
      padding: 8px;
    }
  }
</style>