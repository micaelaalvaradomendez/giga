<script>
  import { API } from '$lib/api.js';
  import { onMount } from 'svelte';

  // Estado del componente
  let compensaciones = [];
  let cargando = false;
  let error = null;
  let mostrandoFormulario = false;

  // Debug: verificar que el script se esté ejecutando
  console.log('Script de compensaciones inicializado');

  // Datos para nueva compensación
  let nuevaCompensacion = {
    id_guardia: '',
    hora_fin_real: '',
    motivo: 'emergencia',
    descripcion_motivo: '',
    numero_acta: '',
    solicitado_por: ''
  };

  // Datos para los filtros
  let areas = [];
  let agentes = [];
  let guardias = [];
  let areaSeleccionada = '';
  let agenteSeleccionado = '';
  let guardiaSeleccionada = '';
  let cargandoAreas = false;
  let cargandoAgentes = false;
  let cargandoGuardias = false;

  // Opciones para el formulario
  const motivosCompensacion = [
    { value: 'siniestro', label: 'Siniestro/Accidente' },
    { value: 'emergencia', label: 'Emergencia Operativa' },
    { value: 'operativo', label: 'Operativo Especial' },
    { value: 'refuerzo', label: 'Refuerzo de Seguridad' },
    { value: 'otro', label: 'Otro Motivo' }
  ];

  onMount(async () => {
    console.log('Componente compensaciones montado, iniciando carga...');
    try {
      await cargarCompensaciones();
      await cargarAreas();
      console.log('Carga inicial completada');
    } catch (err) {
      console.error('Error en carga inicial:', err);
    }
  });

  async function cargarCompensaciones() {
    cargando = true;
    error = null;
    try {
      const response = await API.get('/guardias/compensaciones/');
      compensaciones = response.results || response || [];
      console.log('Compensaciones cargadas:', compensaciones);
    } catch (err) {
      console.error('Error cargando compensaciones:', err);
      error = 'Error al cargar compensaciones: ' + (err.message || 'Error desconocido');
      compensaciones = [];
    } finally {
      cargando = false;
    }
  }

  async function cargarAreas() {
    cargandoAreas = true;
    try {
      const response = await API.get('/personas/catalogs/areas/');
      console.log('Respuesta completa de áreas:', response);
      
      // La API devuelve { success: true, data: { results: [...] } }
      if (response.success && response.data && response.data.results) {
        areas = response.data.results;
      } else if (response.results) {
        areas = response.results;
      } else if (Array.isArray(response)) {
        areas = response;
      } else {
        areas = [];
      }
      
      console.log('Áreas procesadas:', areas);
    } catch (err) {
      console.error('Error cargando áreas:', err);
      areas = [];
    } finally {
      cargandoAreas = false;
    }
  }

  async function cargarAgentes() {
    if (!areaSeleccionada) {
      agentes = [];
      return;
    }
    
    cargandoAgentes = true;
    try {
      const response = await API.get(`/personas/agentes/?area=${areaSeleccionada}`);
      console.log('Respuesta completa de agentes:', response);
      
      // Manejar diferentes estructuras de respuesta
      if (response.success && response.data && response.data.results) {
        agentes = response.data.results;
      } else if (response.results) {
        agentes = response.results;
      } else if (Array.isArray(response)) {
        agentes = response;
      } else {
        agentes = [];
      }
      
      console.log('Agentes procesados:', agentes);
      // Limpiar selección de agente cuando cambia el área
      agenteSeleccionado = '';
      guardias = [];
      guardiaSeleccionada = '';
    } catch (err) {
      console.error('Error cargando agentes:', err);
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
      // Cargar guardias del agente - últimas guardias realizadas
      const response = await API.get(`/guardias/guardias/resumen/?agente=${agenteSeleccionado}`);
      console.log('Respuesta completa de guardias:', response);
      
      // Manejar diferentes estructuras de respuesta
      if (response.success && response.data && response.data.results) {
        guardias = response.data.results;
      } else if (response.results) {
        guardias = response.results;
      } else if (Array.isArray(response)) {
        guardias = response;
      } else {
        guardias = [];
      }
      
      console.log('Guardias procesadas:', guardias);
      // Limpiar selección de guardia cuando cambia el agente
      guardiaSeleccionada = '';
    } catch (err) {
      console.error('Error cargando guardias:', err);
      guardias = [];
    } finally {
      cargandoGuardias = false;
    }
  }

  // Funciones reactivas para cargar datos cuando cambian las selecciones
  $: if (areaSeleccionada) cargarAgentes();
  $: if (agenteSeleccionado) cargarGuardias();

  async function crearCompensacion() {
    if (!guardiaSeleccionada || !nuevaCompensacion.hora_fin_real || !nuevaCompensacion.descripcion_motivo) {
      alert('Por favor complete todos los campos obligatorios');
      return;
    }

    cargando = true;
    error = null;
    
    try {
      const guardiaData = guardias.find(g => g.id_guardia == guardiaSeleccionada);
      
      const compensacionData = {
        id_guardia: guardiaSeleccionada,
        hora_fin_real: nuevaCompensacion.hora_fin_real,
        motivo: nuevaCompensacion.motivo,
        descripcion_motivo: nuevaCompensacion.descripcion_motivo,
        numero_acta: nuevaCompensacion.numero_acta,
        solicitado_por: nuevaCompensacion.solicitado_por || agenteSeleccionado
      };
      
      await API.post('/guardias/compensaciones/', compensacionData);
      
      // Limpiar formulario
      nuevaCompensacion = {
        id_guardia: '',
        hora_fin_real: '',
        motivo: 'emergencia',
        descripcion_motivo: '',
        numero_acta: '',
        solicitado_por: ''
      };
      areaSeleccionada = '';
      agenteSeleccionado = '';
      guardiaSeleccionada = '';
      agentes = [];
      guardias = [];
      
      mostrandoFormulario = false;
      await cargarCompensaciones();
      alert('Compensación creada exitosamente');
    } catch (err) {
      console.error('Error creando compensación:', err);
      error = 'Error al crear compensación: ' + (err.message || 'Error desconocido');
    } finally {
      cargando = false;
    }
  }

  function formatearFecha(fecha) {
    if (!fecha) return '-';
    return new Date(fecha).toLocaleDateString('es-AR');
  }

  function formatearHora(hora) {
    if (!hora) return '-';
    return hora.slice(0, 5); // HH:MM
  }
</script>

<svelte:head>
  <title>Compensaciones por Horas Extra - GIGA</title>
</svelte:head>

<div class="compensaciones-container">
  <div class="header">
    <h1>⏱️ Compensaciones por Horas Extra</h1>
    <p class="descripcion">
      Gestión de horas de compensación por emergencias que exceden el límite de 10 horas por guardia
    </p>
    <button class="btn-nuevo" on:click={() => mostrandoFormulario = true}>
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
    <div class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Nueva Compensación por Horas Extra</h2>
          <button class="btn-close" on:click={() => mostrandoFormulario = false}>×</button>
        </div>

        <form on:submit|preventDefault={crearCompensacion} class="modal-body">
          <div class="paso-selector">
            <h3>Paso 1: Seleccionar Área</h3>
            <div class="campo">
              <label for="area">Área *</label>
              <select bind:value={areaSeleccionada} required disabled={cargandoAreas}>
                <option value="">
                  {cargandoAreas ? 'Cargando áreas...' : 'Seleccione un área'}
                </option>
                {#each areas as area}
                  <option value={area.id_area}>{area.nombre}</option>
                {/each}
                <!-- Debug: Mostrar cantidad de áreas -->
                {#if areas.length === 0 && !cargandoAreas}
                  <option disabled>No hay áreas disponibles</option>
                {/if}
              </select>
            </div>
          </div>

          {#if areaSeleccionada}
            <div class="paso-selector">
              <h3>Paso 2: Seleccionar Agente</h3>
              <div class="campo">
                <label for="agente">Agente *</label>
                <select bind:value={agenteSeleccionado} required disabled={cargandoAgentes}>
                  <option value="">
                    {cargandoAgentes ? 'Cargando agentes...' : 'Seleccione un agente'}
                  </option>
                  {#each agentes as agente}
                    <option value={agente.id_agente}>
                      {agente.apellido}, {agente.nombre} (Leg: {agente.legajo})
                    </option>
                  {/each}
                </select>
              </div>
            </div>
          {/if}

          {#if agenteSeleccionado}
            <div class="paso-selector">
              <h3>Paso 3: Seleccionar Guardia</h3>
              <div class="campo">
                <label for="guardia">Guardia que Necesita Compensación *</label>
                <select bind:value={guardiaSeleccionada} required disabled={cargandoGuardias}>
                  <option value="">
                    {cargandoGuardias ? 'Cargando guardias...' : 'Seleccione una guardia'}
                  </option>
                  {#each guardias as guardia}
                    <option value={guardia.id_guardia}>
                      {formatearFecha(guardia.fecha)} - {formatearHora(guardia.hora_inicio)} a {formatearHora(guardia.hora_fin)}
                      {#if guardia.cronograma_nombre}
                        ({guardia.cronograma_nombre})
                      {/if}
                    </option>
                  {/each}
                </select>
                {#if guardias.length === 0 && !cargandoGuardias && agenteSeleccionado}
                  <small class="text-warning">Este agente no tiene guardias registradas recientes</small>
                {/if}
              </div>
            </div>
          {/if}

          {#if guardiaSeleccionada}

            <div class="paso-selector">
              <h3>Paso 4: Detalles de la Compensación</h3>
              
              <div class="campo">
                <label for="hora_fin_real">Hora Real de Finalización *</label>
                <input 
                  type="time" 
                  bind:value={nuevaCompensacion.hora_fin_real} 
                  required 
                />
                <small>Hora en que realmente terminó el servicio (debe exceder las 10 horas)</small>
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
                  required 
                  rows="3"
                  placeholder="Describa detalladamente qué situación causó que se extendiera el horario..."
                ></textarea>
              </div>

              <div class="campo">
                <label for="numero_acta">Número de Acta (Opcional)</label>
                <input 
                  type="text" 
                  bind:value={nuevaCompensacion.numero_acta} 
                  placeholder="Si existe un expediente o acta relacionada"
                />
              </div>

              <div class="campo">
                <label for="solicitado_por">Solicitado por</label>
                <input 
                  type="number" 
                  bind:value={nuevaCompensacion.solicitado_por} 
                  placeholder="Por defecto será el agente seleccionado"
                />
                <small>Si no se especifica, se usará el agente seleccionado</small>
              </div>
            </div>
          {/if}

          <div class="modal-footer">
            <button type="button" class="btn-cancelar" on:click={() => mostrandoFormulario = false}>
              Cancelar
            </button>
            <button type="submit" class="btn-guardar" disabled={cargando}>
              {cargando ? 'Guardando...' : 'Crear Compensación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <!-- Lista de compensaciones -->
  <div class="lista-compensaciones">
    <h2>Compensaciones Registradas ({compensaciones.length})</h2>

    {#if cargando}
      <div class="loading">
        <div class="spinner"></div>
        Cargando compensaciones...
      </div>
    {:else if compensaciones.length === 0}
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No hay compensaciones registradas</h3>
        <p>Cuando se registre una compensación por horas extra aparecerá aquí</p>
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
            {#each compensaciones as compensacion}
              <tr>
                <td>
                  <div class="agente-info">
                    <strong>ID: {compensacion.id_agente || compensacion.agente_id || 'N/A'}</strong>
                    {#if compensacion.agente_nombre}
                      <br><small>{compensacion.agente_apellido}, {compensacion.agente_nombre}</small>
                    {/if}
                  </div>
                </td>
                <td>{formatearFecha(compensacion.fecha_servicio)}</td>
                <td>
                  <span class="horas-badge">
                    {compensacion.horas_extra || 'N/A'}h
                  </span>
                  {#if compensacion.hora_fin_real}
                    <br><small>Finalizó: {formatearHora(compensacion.hora_fin_real)}</small>
                  {/if}
                </td>
                <td>
                  <span class="motivo-badge">{compensacion.motivo || 'N/A'}</span>
                  {#if compensacion.numero_acta}
                    <br><small>Acta: {compensacion.numero_acta}</small>
                  {/if}
                </td>
                <td>
                  <span class="estado-badge estado-{compensacion.estado || 'pendiente'}">
                    {compensacion.estado || 'Pendiente'}
                  </span>
                </td>
                <td>
                  <button class="btn-small btn-ver">Ver</button>
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

  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #e2e8f0;
  }

  .header h1 {
    color: #2d3748;
    margin: 0 0 10px 0;
    font-size: 28px;
  }

  .descripcion {
    color: #718096;
    font-size: 14px;
    margin: 0;
    max-width: 600px;
  }

  .btn-nuevo {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .btn-nuevo:hover {
    background: #2563eb;
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

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    margin: 0;
    color: #1f2937;
    font-size: 20px;
  }

  .btn-close {
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #6b7280;
    padding: 4px;
    border-radius: 4px;
  }

  .btn-close:hover {
    background: #f3f4f6;
  }

  .modal-body {
    padding: 24px;
  }

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

  .campo {
    margin-bottom: 20px;
  }

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
    transition: border-color 0.2s;
  }

  .campo input:focus, .campo select:focus, .campo textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .campo small {
    display: block;
    margin-top: 4px;
    color: #6b7280;
    font-size: 12px;
  }

  .text-warning {
    color: #d97706 !important;
    font-weight: 500;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 24px;
    border-top: 1px solid #e5e7eb;
  }

  .btn-cancelar, .btn-guardar, .btn-small, .btn-ver {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-cancelar {
    background: #6b7280;
    color: white;
  }

  .btn-cancelar:hover {
    background: #4b5563;
  }

  .btn-guardar {
    background: #10b981;
    color: white;
  }

  .btn-guardar:hover:not(:disabled) {
    background: #059669;
  }

  .btn-guardar:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .lista-compensaciones {
    margin-top: 40px;
  }

  .lista-compensaciones h2 {
    color: #374151;
    margin-bottom: 20px;
    font-size: 20px;
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: #6b7280;
    font-size: 16px;
    gap: 12px;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 3px solid #e5e7eb;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #6b7280;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .empty-state h3 {
    margin: 0 0 8px 0;
    color: #374151;
  }

  .empty-state p {
    margin: 0;
    font-size: 14px;
  }

  .table-container {
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: white;
  }

  .compensaciones-table {
    width: 100%;
    border-collapse: collapse;
  }

  .compensaciones-table th {
    background: #f9fafb;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #374151;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }

  .compensaciones-table td {
    padding: 16px;
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

  .horas-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 12px;
  }

  .motivo-badge {
    display: inline-block;
    background: #f3f4f6;
    color: #374151;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
    text-transform: capitalize;
  }

  .estado-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;
  }

  .estado-pendiente {
    background: #fef3c7;
    color: #92400e;
  }

  .estado-aprobada {
    background: #d1fae5;
    color: #065f46;
  }

  .estado-rechazada {
    background: #fee2e2;
    color: #991b1b;
  }

  .btn-small {
    padding: 6px 12px;
    font-size: 12px;
  }

  .btn-ver {
    background: #3b82f6;
    color: white;
  }

  .btn-ver:hover {
    background: #2563eb;
  }

  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
    }

    .btn-nuevo {
      align-self: flex-start;
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
      padding: 12px;
    }
  }
</style>