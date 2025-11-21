<script>
  import { onMount } from 'svelte';
  import { goto, invalidateAll } from '$app/navigation';
  import { browser } from '$app/environment';
  import { guardiasService, personasService } from '$lib/services.js';
  import AuthService from '$lib/login/authService.js';

  let loading = false;
  let error = '';
  let cronogramasPendientes = [];
  let cronogramasAprobadas = [];
  let tabActiva = 'pendientes'; // 'pendientes' | 'aprobadas'
  let agenteActual = null;
  let rolAgente = '';
  let token = null;
  
  // Modal para ver detalles
  let mostrarModal = false;
  let cronogramaSeleccionado = null;
  let guardiasDelCronograma = [];
  
  // Modal de rechazo
  let mostrarModalRechazo = false;
  let motivoRechazo = '';
  let cronogramaARechazar = null;

  onMount(async () => {
    try {
      const sessionCheck = await AuthService.checkSession();
      
      if (!sessionCheck.authenticated) {
        goto('/');
        return;
      }
      
      token = localStorage.getItem('token');
      await cargarDatos();
      
      // Recargar cuando la página vuelve a ser visible
      if (browser) {
        const handleVisibilityChange = () => {
          if (document.visibilityState === 'visible') {
            cargarDatos();
          }
        };
        
        const handleFocus = () => {
          cargarDatos();
        };
        
        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('focus', handleFocus);
        
        return () => {
          document.removeEventListener('visibilitychange', handleVisibilityChange);
          window.removeEventListener('focus', handleFocus);
        };
      }
    } catch (err) {
      console.error('Error verificando sesión:', err);
      goto('/');
    }
  });

  async function cargarDatos() {
    try {
      const responseAgentes = await personasService.getAllAgentes(token);
      const agentes = responseAgentes.data?.results || responseAgentes.data || [];
      
      // Obtener agente de la sesión actual
      const user = JSON.parse(localStorage.getItem('agente') || '{}');
      agenteActual = agentes.find(a => a.id_agente === user.id_agente) || agentes[0];
      
      if (agenteActual) {
        await Promise.all([
          cargarPendientes(),
          cargarAprobadas()
        ]);
      }
    } catch (e) {
      error = 'Error cargando datos iniciales';
      console.error(e);
    }
  }

  async function cargarPendientes() {
    try {
      loading = true;
      error = '';
      
      const response = await guardiasService.getPendientesAprobacion(agenteActual.id_agente, token);
      cronogramasPendientes = response.data?.cronogramas || [];
      rolAgente = response.data?.rol_agente || '';
      
      console.log('Cronogramas pendientes:', cronogramasPendientes);
    } catch (e) {
      error = 'Error cargando cronogramas pendientes';
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function cargarAprobadas() {
    try {
      // Obtener cronogramas aprobadas/publicadas del mes actual y anteriores
      const response = await guardiasService.getCronogramas(token);
      const todas = response.data?.results || response.data || [];
      
      cronogramasAprobadas = todas.filter(c => 
        c.estado === 'aprobada' || c.estado === 'publicada'
      );
      
      console.log('Cronogramas aprobadas:', cronogramasAprobadas);
    } catch (e) {
      console.error('Error cargando cronogramas aprobadas:', e);
    }
  }

  async function verDetalles(cronograma) {
    cronogramaSeleccionado = cronograma;
    
    // Cargar guardias del cronograma
    try {
      const response = await guardiasService.getResumenGuardias(`id_cronograma=${cronograma.id_cronograma}`);
      guardiasDelCronograma = response.data?.guardias || [];
      mostrarModal = true;
    } catch (e) {
      console.error('Error cargando guardias:', e);
      guardiasDelCronograma = [];
      mostrarModal = true;
    }
  }

  async function aprobar(cronograma) {
    if (!confirm(`¿Confirmar aprobación del cronograma de ${cronograma.area_nombre}?`)) {
      return;
    }

    try {
      loading = true;
      await guardiasService.aprobarCronograma(cronograma.id_cronograma, {
        agente_id: agenteActual.id_agente
      }, token);
      
      alert('Cronograma aprobado exitosamente');
      await cargarDatos();
    } catch (e) {
      const errorMsg = e.response?.data?.error || e.response?.data?.detalle || 'Error al aprobar cronograma';
      alert(errorMsg);
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function iniciarRechazo(cronograma) {
    cronogramaARechazar = cronograma;
    motivoRechazo = '';
    mostrarModalRechazo = true;
  }

  async function confirmarRechazo() {
    if (!motivoRechazo.trim()) {
      alert('Debe ingresar un motivo de rechazo');
      return;
    }

    try {
      loading = true;
      await guardiasService.rechazarCronograma(cronogramaARechazar.id_cronograma, {
        agente_id: agenteActual.id_agente,
        motivo: motivoRechazo
      }, token);
      
      alert('Cronograma rechazado');
      mostrarModalRechazo = false;
      cronogramaARechazar = null;
      motivoRechazo = '';
      await cargarDatos();
    } catch (e) {
      const errorMsg = e.response?.data?.error || 'Error al rechazar cronograma';
      alert(errorMsg);
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function publicar(cronograma) {
    if (!confirm(`¿Publicar cronograma de ${cronograma.area_nombre}?`)) {
      return;
    }

    try {
      loading = true;
      await guardiasService.publicarCronograma(cronograma.id_cronograma, token);
      
      alert('Cronograma publicado exitosamente');
      await cargarDatos();
    } catch (e) {
      const errorMsg = e.response?.data?.error || 'Error al publicar cronograma';
      alert(errorMsg);
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function cerrarModal() {
    mostrarModal = false;
    cronogramaSeleccionado = null;
    guardiasDelCronograma = [];
  }
  
  async function editarCronograma(cronograma) {
    // Redirigir al planificador con el ID del cronograma para editar
    await invalidateAll();
    goto(`/paneladmin/guardias/planificador?editar=${cronograma.id_cronograma}`, { invalidateAll: true });
  }
  
  async function eliminarGuardia(guardia) {
    if (!confirm(`¿Eliminar guardia de ${guardia.agente_nombre} el ${formatearFecha(guardia.fecha)}?`)) {
      return;
    }
    
    try {
      loading = true;
      await guardiasService.deleteGuardia(guardia.id_guardia, token);
      
      alert('Guardia eliminada exitosamente');
      
      // Recargar detalles del cronograma
      if (cronogramaSeleccionado) {
        await verDetalles(cronogramaSeleccionado);
      }
      
      await cargarDatos();
    } catch (e) {
      const errorMsg = e.response?.data?.error || 'Error al eliminar guardia';
      alert(errorMsg);
      console.error(e);
    } finally {
      loading = false;
    }
  }
  
  async function eliminarCronograma(cronograma) {
    if (!confirm(`¿Está seguro de eliminar el cronograma de ${cronograma.area_nombre}?\n\nEsto eliminará todas las guardias asociadas.`)) {
      return;
    }
    
    try {
      loading = true;
      await guardiasService.deleteCronograma(cronograma.id_cronograma, token);
      
      alert('Cronograma eliminado exitosamente');
      cerrarModal();
      await cargarDatos();
    } catch (e) {
      const errorMsg = e.response?.data?.error || 'Error al eliminar cronograma';
      alert(errorMsg);
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function formatearFecha(fechaStr) {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr + 'T00:00:00');
    return fecha.toLocaleDateString('es-AR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  }

  function formatearHora(horaStr) {
    if (!horaStr) return '';
    return horaStr.substring(0, 5); // HH:MM
  }
</script>

<section class="aprobaciones-wrap">
  <header class="head">
    <h1>Aprobaciones de Guardias</h1>
    <p>Revisá y aprobá cronogramas pendientes</p>
    {#if rolAgente}
      <div class="rol-badge">
        Tu rol: <strong>{rolAgente}</strong>
      </div>
    {/if}
  </header>

  <!-- Tabs -->
  <div class="tabs">
    <button 
      class="tab" 
      class:active={tabActiva === 'pendientes'}
      on:click={() => tabActiva = 'pendientes'}
    >
      Pendientes ({cronogramasPendientes.length})
    </button>
    <button 
      class="tab" 
      class:active={tabActiva === 'aprobadas'}
      on:click={() => tabActiva = 'aprobadas'}
    >
      Aprobadas ({cronogramasAprobadas.length})
    </button>
  </div>

  {#if error}
    <div class="alert alert-error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Cargando...</p>
    </div>
  {:else if tabActiva === 'pendientes'}
    <!-- Lista de pendientes -->
    <div class="cronogramas-lista">
      {#if cronogramasPendientes.length === 0}
        <div class="empty-state">
          <p>✓ No hay cronogramas pendientes de aprobación</p>
        </div>
      {:else}
        {#each cronogramasPendientes as cronograma}
          <div class="cronograma-card pendiente">
            <div class="cronograma-header">
              <div class="cronograma-info">
                <h3>{cronograma.area_nombre || 'Sin área'}</h3>
                <p class="tipo">{cronograma.tipo}</p>
              </div>
              <div class="cronograma-estado">
                <span class="badge badge-pendiente">{cronograma.estado}</span>
              </div>
            </div>
            
            <div class="cronograma-body">
              <div class="info-row">
                <span class="label">Creado por:</span>
                <span class="value">
                  {cronograma.creado_por_nombre || ''} {cronograma.creado_por_apellido || ''}
                  {#if cronograma.creado_por_rol}
                    <span class="rol-mini">({cronograma.creado_por_rol})</span>
                  {/if}
                </span>
              </div>
              
              <div class="info-row">
                <span class="label">Fecha creación:</span>
                <span class="value">{formatearFecha(cronograma.fecha_creacion)}</span>
              </div>
              
              <div class="info-row">
                <span class="label">Horario:</span>
                <span class="value">
                  {formatearHora(cronograma.hora_inicio)} - {formatearHora(cronograma.hora_fin)}
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
                    {cronograma.puede_aprobar_rol.join(', ')}
                  </span>
                </div>
              {/if}
            </div>
            
            <div class="cronograma-actions">
              <button class="btn btn-secondary" on:click={() => verDetalles(cronograma)}>
                📋 Ver Detalles
              </button>
              <button class="btn btn-info" on:click={() => editarCronograma(cronograma)} disabled={loading}>
                ✏️ Editar
              </button>
              <button class="btn btn-success" on:click={() => aprobar(cronograma)} disabled={loading}>
                ✓ Aprobar
              </button>
              <button class="btn btn-danger" on:click={() => iniciarRechazo(cronograma)} disabled={loading}>
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
      {#if cronogramasAprobadas.length === 0}
        <div class="empty-state">
          <p>No hay cronogramas aprobadas</p>
        </div>
      {:else}
        {#each cronogramasAprobadas as cronograma}
          <div class="cronograma-card aprobada">
            <div class="cronograma-header">
              <div class="cronograma-info">
                <h3>{cronograma.area_nombre || 'Sin área'}</h3>
                <p class="tipo">{cronograma.tipo}</p>
              </div>
              <div class="cronograma-estado">
                <span class="badge badge-{cronograma.estado}">{cronograma.estado}</span>
              </div>
            </div>
            
            <div class="cronograma-body">
              <div class="info-row">
                <span class="label">Aprobado:</span>
                <span class="value">{formatearFecha(cronograma.fecha_aprobacion)}</span>
              </div>
              
              <div class="info-row">
                <span class="label">Guardias:</span>
                <span class="value">{cronograma.total_guardias || 0}</span>
              </div>
            </div>
            
            <div class="cronograma-actions">
              <button class="btn btn-secondary" on:click={() => verDetalles(cronograma)}>
                Ver Detalles
              </button>
              {#if cronograma.estado === 'aprobada'}
                <button class="btn btn-primary" on:click={() => publicar(cronograma)} disabled={loading}>
                  Publicar
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
{#if mostrarModal && cronogramaSeleccionado}
  <div class="modal-overlay" on:click={cerrarModal}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Detalles del Cronograma</h3>
        <button class="close-button" on:click={cerrarModal}>&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="detalle-seccion">
          <h4>Información General</h4>
          <div class="info-row">
            <span class="label">Área:</span>
            <span class="value">{cronogramaSeleccionado.area_nombre}</span>
          </div>
          <div class="info-row">
            <span class="label">Tipo:</span>
            <span class="value">{cronogramaSeleccionado.tipo}</span>
          </div>
          <div class="info-row">
            <span class="label">Estado:</span>
            <span class="value">
              <span class="badge badge-{cronogramaSeleccionado.estado}">
                {cronogramaSeleccionado.estado}
              </span>
            </span>
          </div>
        </div>
        
        <div class="detalle-seccion">
          <h4>Guardias Asignadas ({guardiasDelCronograma.length})</h4>
          {#if guardiasDelCronograma.length > 0}
            <div class="guardias-tabla">
              <table>
                <thead>
                  <tr>
                    <th>Agente</th>
                    <th>Fecha</th>
                    <th>Horario</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {#each guardiasDelCronograma as guardia}
                    <tr>
                      <td>{guardia.agente_nombre}</td>
                      <td>{formatearFecha(guardia.fecha)}</td>
                      <td>{formatearHora(guardia.hora_inicio)} - {formatearHora(guardia.hora_fin)}</td>
                      <td>
                        <span class="badge-mini badge-{guardia.estado}">{guardia.estado}</span>
                      </td>
                      <td>
                        <button 
                          class="btn-icon btn-danger-icon" 
                          on:click={() => eliminarGuardia(guardia)}
                          disabled={loading}
                          title="Eliminar guardia"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {:else}
            <p class="text-muted">No hay guardias asignadas</p>
          {/if}
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={cerrarModal}>Cerrar</button>
          {#if cronogramaSeleccionado && (cronogramaSeleccionado.estado === 'pendiente' || cronogramaSeleccionado.estado === 'aprobada')}
            <button 
              class="btn btn-danger" 
              on:click={() => eliminarCronograma(cronogramaSeleccionado)}
              disabled={loading}
            >
              🗑️ Eliminar Cronograma
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Modal de rechazo -->
{#if mostrarModalRechazo && cronogramaARechazar}
  <div class="modal-overlay" on:click={() => mostrarModalRechazo = false}>
    <div class="modal-content modal-rechazo" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Rechazar Cronograma</h3>
        <button class="close-button" on:click={() => mostrarModalRechazo = false}>&times;</button>
      </div>
      
      <div class="modal-body">
        <p><strong>Cronograma:</strong> {cronogramaARechazar.area_nombre} - {cronogramaARechazar.tipo}</p>
        
        <div class="form-group">
          <label for="motivo">Motivo del rechazo *</label>
          <textarea 
            id="motivo" 
            bind:value={motivoRechazo} 
            placeholder="Ingrese el motivo del rechazo..."
            rows="4"
          ></textarea>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={() => mostrarModalRechazo = false}>
          Cancelar
        </button>
        <button class="btn btn-danger" on:click={confirmarRechazo} disabled={loading || !motivoRechazo.trim()}>
          Confirmar Rechazo
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .aprobaciones-wrap {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
  }

  .head {
    text-align: center;
    margin-bottom: 2rem;
  }

  .head h1 {
    font-size: 1.8rem;
    margin: 0 0 0.5rem 0;
    color: #1e40af;
  }

  .head p {
    margin: 0 0 1rem 0;
    color: #64748b;
    font-size: 1rem;
  }

  .rol-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, rgba(142, 182, 228, 0.2) 0%, rgba(61, 151, 255, 0.2) 100%);
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
    text-transform: capitalize;
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

  .badge-rechazada {
    background: #fee2e2;
    color: #991b1b;
  }

  .cronograma-body {
    margin-bottom: 1rem;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .info-row:last-child {
    border-bottom: none;
  }

  .info-row .label {
    color: #64748b;
    font-size: 0.9rem;
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
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
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

  /* Modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  }

  .modal-rechazo {
    max-width: 500px;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h3 {
    margin: 0;
    color: #1e40af;
    font-size: 1.3rem;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #64748b;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
  }

  .close-button:hover {
    background: #f3f4f6;
  }

  .modal-body {
    padding: 1.5rem;
  }

  .detalle-seccion {
    margin-bottom: 1.5rem;
  }

  .detalle-seccion:last-child {
    margin-bottom: 0;
  }

  .detalle-seccion h4 {
    margin: 0 0 1rem 0;
    color: #374151;
    font-size: 1rem;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .guardias-tabla {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  thead {
    background: #f9fafb;
  }

  th, td {
    padding: 0.75rem;
    text-align: left;
    font-size: 0.9rem;
  }

  th {
    font-weight: 600;
    color: #374151;
    border-bottom: 2px solid #e5e7eb;
  }

  td {
    color: #111827;
    border-bottom: 1px solid #f3f4f6;
  }

  tbody tr:hover {
    background: #f9fafb;
  }

  .badge-mini {
    padding: 0.15rem 0.5rem;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .badge-mini.badge-planificada {
    background: #dbeafe;
    color: #1e40af;
  }

  .text-muted {
    color: #9ca3af;
    font-style: italic;
  }

  .form-group {
    margin-top: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-weight: 600;
    font-size: 0.9rem;
  }

  textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-family: inherit;
    font-size: 0.9rem;
    resize: vertical;
  }

  textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid #e5e7eb;
  }
</style>
