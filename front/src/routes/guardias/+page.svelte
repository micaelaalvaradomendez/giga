<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { guardiasService } from '$lib/services';
  import AuthService from '$lib/login/authService.js';
  
  let user = null;
  let token = null;
  let guardiasPorHacer = [];
  let guardiasRealizadas = [];
  let tabActual = 'porHacer';
  let cargando = true;
  let error = null;
  
  // Modal de notas
  let modalNotaAbierto = false;
  let guardiaSeleccionada = null;
  let notaTexto = '';
  let notaId = null;
  let guardandoNota = false;
  
  // Role-based permissions
  $: userRole = user?.roles?.[0]?.nombre;
  $: isAdmin = userRole === 'Administrador';
  $: isDirector = userRole === 'Director' || isAdmin;
  $: isJefatura = userRole === 'Jefatura' || isDirector;

  onMount(async () => {
    try {
      const sessionCheck = await AuthService.checkSession();
      
      if (!sessionCheck.authenticated) {
        goto('/');
        return;
      }
      
      user = sessionCheck.user;
      token = localStorage.getItem('token');
      
      await cargarGuardias();
    } catch (err) {
      console.error('Error verificando sesión:', err);
      goto('/');
    }
  });
  
  async function cargarGuardias() {
    if (!user || !user.id) return;
    
    try {
      cargando = true;
      error = null;
      
      // Obtener guardias del agente
      const response = await guardiasService.getGuardiasAgente(user.id, token);
      
      if (!response || !response.data) {
        throw new Error('Respuesta inválida del servidor');
      }
      
      const todasGuardias = response.data.guardias || [];
      
      // Filtrar solo guardias aprobadas (estado planificada, activa=true, cronograma aprobado/publicado)
      const guardiasAprobadas = todasGuardias.filter(g => 
        g.estado === 'planificada' && 
        g.activa === true &&
        (g.cronograma_estado === 'aprobada' || g.cronograma_estado === 'publicada')
      );
      
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      
      // Separar por hacer y realizadas
      guardiasPorHacer = guardiasAprobadas
        .filter(g => new Date(g.fecha) >= hoy)
        .sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
      
      guardiasRealizadas = guardiasAprobadas
        .filter(g => new Date(g.fecha) < hoy)
        .sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
      
    } catch (err) {
      console.error('Error cargando guardias:', err);
      error = err.message || 'Error al cargar guardias';
    } finally {
      cargando = false;
    }
  }
  
  function formatearFecha(fecha) {
    const f = new Date(fecha);
    const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return `${dias[f.getDay()]} ${f.getDate()} ${meses[f.getMonth()]} ${f.getFullYear()}`;
  }
  
  function abrirModalNota(guardia) {
    guardiaSeleccionada = guardia;
    
    // Si la guardia tiene nota, cargar su contenido
    if (guardia.notas && guardia.notas.length > 0) {
      const miNota = guardia.notas.find(n => n.id_agente === user.id);
      if (miNota) {
        notaTexto = miNota.nota || '';
        notaId = miNota.id_nota;
      } else {
        notaTexto = '';
        notaId = null;
      }
    } else {
      notaTexto = '';
      notaId = null;
    }
    
    modalNotaAbierto = true;
  }
  
  function cerrarModalNota() {
    modalNotaAbierto = false;
    guardiaSeleccionada = null;
    notaTexto = '';
    notaId = null;
  }
  
  async function guardarNota() {
    if (!guardiaSeleccionada || !notaTexto.trim()) {
      alert('Debe escribir una nota');
      return;
    }
    
    try {
      guardandoNota = true;
      
      const data = {
        agente_id: user.id,
        nota: notaTexto.trim()
      };
      
      if (notaId) {
        // Actualizar nota existente
        await guardiasService.updateNotaGuardia(notaId, data, token);
      } else {
        // Crear nueva nota
        await guardiasService.createNotaGuardia(guardiaSeleccionada.id_guardia, data, token);
      }
      
      // Recargar guardias para actualizar notas
      await cargarGuardias();
      
      cerrarModalNota();
      
    } catch (err) {
      console.error('Error guardando nota:', err);
      alert('Error al guardar la nota: ' + (err.message || 'Error desconocido'));
    } finally {
      guardandoNota = false;
    }
  }
  
  async function eliminarNota() {
    if (!notaId || !confirm('¿Está seguro de eliminar esta nota?')) {
      return;
    }
    
    try {
      guardandoNota = true;
      
      await guardiasService.deleteNotaGuardia(notaId, user.id, token);
      
      // Recargar guardias
      await cargarGuardias();
      
      cerrarModalNota();
      
    } catch (err) {
      console.error('Error eliminando nota:', err);
      alert('Error al eliminar la nota: ' + (err.message || 'Error desconocido'));
    } finally {
      guardandoNota = false;
    }
  }
</script>

<div class="container">
  <div class="header-glass">
    <h1>🛡️ Mis Guardias</h1>
    <p class="subtitle">Administra tus guardias y agrega notas personales</p>
  </div>

  {#if cargando}
    <div class="loading-glass">
      <div class="spinner"></div>
      <p>Cargando guardias...</p>
    </div>
  {:else if error}
    <div class="error-glass">
      <p>⚠️ {error}</p>
      <button class="btn-secondary" on:click={cargarGuardias}>Reintentar</button>
    </div>
  {:else}
    <!-- Tabs -->
    <div class="tabs">
      <button 
        class="tab {tabActual === 'porHacer' ? 'active' : ''}"
        on:click={() => tabActual = 'porHacer'}
      >
        📅 Por Hacer ({guardiasPorHacer.length})
      </button>
      <button 
        class="tab {tabActual === 'realizadas' ? 'active' : ''}"
        on:click={() => tabActual = 'realizadas'}
      >
        ✅ Realizadas ({guardiasRealizadas.length})
      </button>
    </div>

    <!-- Botón de gestión (solo para jefatura, director, admin) -->
    {#if isJefatura || isDirector || isAdmin}
      <div class="admin-actions">
        <button class="btn btn-gestionar" on:click={() => goto('/paneladmin/guardias')}>
          🛡️ Gestionar Guardias
        </button>
      </div>
    {/if}

    <!-- Contenido según tab -->
    {#if tabActual === 'porHacer'}
      {#if guardiasPorHacer.length === 0}
        <div class="empty-glass">
          <p>📭 No tienes guardias pendientes</p>
        </div>
      {:else}
        <div class="guardias-grid">
          {#each guardiasPorHacer as guardia}
            <div class="guardia-card">
              <div class="guardia-header">
                <div class="fecha">
                  <span class="fecha-label">{formatearFecha(guardia.fecha)}</span>
                  <span class="tipo-badge tipo-{guardia.tipo}">{guardia.tipo}</span>
                </div>
                <span class="horario">{guardia.hora_inicio} - {guardia.hora_fin}</span>
              </div>
              
              <div class="guardia-body">
                <div class="info-row">
                  <span class="label">Área:</span>
                  <span class="value">{guardia.area_nombre || 'N/A'}</span>
                </div>
                <div class="info-row">
                  <span class="label">Cronograma:</span>
                  <span class="value">{guardia.cronograma_tipo}</span>
                </div>
                {#if guardia.observaciones}
                  <div class="info-row observaciones">
                    <span class="label">Observaciones:</span>
                    <span class="value">{guardia.observaciones}</span>
                  </div>
                {/if}
              </div>
              
              <div class="guardia-footer">
                <button 
                  class="btn-nota {guardia.tiene_nota ? 'tiene-nota' : ''}"
                  on:click={() => abrirModalNota(guardia)}
                >
                  {guardia.tiene_nota ? '📝 Editar nota' : '➕ Agregar nota'}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {:else}
      {#if guardiasRealizadas.length === 0}
        <div class="empty-glass">
          <p>📭 No tienes guardias realizadas</p>
        </div>
      {:else}
        <div class="guardias-grid">
          {#each guardiasRealizadas as guardia}
            <div class="guardia-card realizada">
              <div class="guardia-header">
                <div class="fecha">
                  <span class="fecha-label">{formatearFecha(guardia.fecha)}</span>
                  <span class="tipo-badge tipo-{guardia.tipo}">{guardia.tipo}</span>
                </div>
                <span class="horario">{guardia.hora_inicio} - {guardia.hora_fin}</span>
              </div>
              
              <div class="guardia-body">
                <div class="info-row">
                  <span class="label">Área:</span>
                  <span class="value">{guardia.area_nombre || 'N/A'}</span>
                </div>
                <div class="info-row">
                  <span class="label">Cronograma:</span>
                  <span class="value">{guardia.cronograma_tipo}</span>
                </div>
                {#if guardia.observaciones}
                  <div class="info-row observaciones">
                    <span class="label">Observaciones:</span>
                    <span class="value">{guardia.observaciones}</span>
                  </div>
                {/if}
              </div>
              
              <div class="guardia-footer">
                <button 
                  class="btn-nota {guardia.tiene_nota ? 'tiene-nota' : ''}"
                  on:click={() => abrirModalNota(guardia)}
                >
                  {guardia.tiene_nota ? '📝 Ver/Editar nota' : '➕ Agregar nota'}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  {/if}
</div>

<!-- Modal de Nota -->
{#if modalNotaAbierto && guardiaSeleccionada}
  <div class="modal-overlay" on:click={cerrarModalNota}>
    <div class="modal-glass" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{notaId ? '📝 Editar nota' : '➕ Nueva nota'}</h2>
        <button class="btn-close" on:click={cerrarModalNota}>✕</button>
      </div>
      
      <div class="modal-body">
        <div class="guardia-info">
          <p><strong>Fecha:</strong> {formatearFecha(guardiaSeleccionada.fecha)}</p>
          <p><strong>Horario:</strong> {guardiaSeleccionada.hora_inicio} - {guardiaSeleccionada.hora_fin}</p>
          <p><strong>Tipo:</strong> {guardiaSeleccionada.tipo}</p>
        </div>
        
        <label for="nota-texto">Nota personal:</label>
        <textarea
          id="nota-texto"
          bind:value={notaTexto}
          placeholder="Escribe tus observaciones sobre esta guardia..."
          rows="6"
          disabled={guardandoNota}
        ></textarea>
      </div>
      
      <div class="modal-footer">
        {#if notaId}
          <button 
            class="btn-danger" 
            on:click={eliminarNota}
            disabled={guardandoNota}
          >
            🗑️ Eliminar
          </button>
        {/if}
        <button 
          class="btn-secondary" 
          on:click={cerrarModalNota}
          disabled={guardandoNota}
        >
          Cancelar
        </button>
        <button 
          class="btn-primary" 
          on:click={guardarNota}
          disabled={guardandoNota || !notaTexto.trim()}
        >
          {guardandoNota ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .header-glass {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  
  .header-glass h1 {
    margin: 0 0 0.5rem 0;
    color: #00C6FF;
    font-size: 2rem;
  }
  
  .subtitle {
    margin: 0;
    color: #1a1a1a;
    font-size: 1rem;
  }
  
  .tabs-glass {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 0.5rem;
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
  }
  
  .tab {
    flex: 1;
    padding: 1rem 2rem;
    background: transparent;
    border: none;
    border-radius: 10px;
    color: #1a1a1a;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .tab:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #000;
  }
  
  .tab.active {
    background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
    color: #fff;
    box-shadow: 0 4px 15px rgba(0, 198, 255, 0.3);
  }
  
  .guardias-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }
  
  .guardia-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }
  
  .guardia-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 198, 255, 0.2);
    border-color: rgba(0, 198, 255, 0.4);
  }
  
  .guardia-card.realizada {
    opacity: 0.8;
    border-color: rgba(76, 175, 80, 0.3);
  }
  
  .guardia-header {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .fecha {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .fecha-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
  }
  
  .tipo-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    text-transform: uppercase;
  }
  
  .tipo-badge.tipo-diurno {
    background: rgba(255, 193, 7, 0.2);
    color: #1a1a1a;
    border: 1px solid rgba(255, 193, 7, 0.3);
  }
  
  .tipo-badge.tipo-nocturno {
    background: rgba(63, 81, 181, 0.2);
    color: #1a1a1a;
    border: 1px solid rgba(63, 81, 181, 0.3);
  }
  
  .horario {
    color: #1a1a1a;
    font-size: 1.2rem;
    font-weight: 500;
  }
  
  .guardia-body {
    margin-bottom: 1rem;
  }
  
  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }
  
  .info-row .label {
    color: #666;
    font-size: 0.9rem;
  }
  
  .info-row .value {
    color: #1a1a1a;
    font-weight: 500;
  }
  
  .info-row.observaciones {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .guardia-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .btn-nota {
    padding: 0.6rem 1.2rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    color: #1a1a1a;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .btn-nota:hover {
    background: rgba(255, 255, 255, 0.15);
    color: #000;
    transform: scale(1.05);
  }
  
  .btn-nota.tiene-nota {
    background: rgba(255, 152, 0, 0.3);
    border-color: rgba(255, 152, 0, 0.4);
    color: #1a1a1a;
  }
  
  .btn-nota.tiene-nota:hover {
    background: rgba(255, 152, 0, 0.4);
  }
  
  .loading-glass,
  .error-glass,
  .empty-glass {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 3rem;
    text-align: center;
    color: #1a1a1a;
  }
  
  .spinner {
    width: 50px;
    height: 50px;
    margin: 0 auto 1rem;
    border: 4px solid rgba(0, 198, 255, 0.2);
    border-top-color: #00C6FF;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  /* Modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(5px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }
  
  .modal-glass {
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow: auto;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .modal-header h2 {
    margin: 0;
    color: #00C6FF;
    font-size: 1.5rem;
  }
  
  .btn-close {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    transition: color 0.3s ease;
  }
  
  .btn-close:hover {
    color: #fff;
  }
  
  .modal-body {
    padding: 2rem;
  }
  
  .guardia-info {
    background: rgba(255, 255, 255, 0.05);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
  }
  
  .guardia-info p {
    margin: 0.5rem 0;
    color: rgba(255, 255, 255, 0.9);
  }
  
  .guardia-info strong {
    color: #00C6FF;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
  }
  
  textarea {
    width: 100%;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    color: #fff;
    font-family: inherit;
    font-size: 1rem;
    resize: vertical;
  }
  
  textarea:focus {
    outline: none;
    border-color: #00C6FF;
    box-shadow: 0 0 0 3px rgba(0, 198, 255, 0.1);
  }
  
  textarea:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding: 1.5rem 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .btn-primary,
  .btn-secondary,
  .btn-danger {
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
    color: #fff;
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(0, 198, 255, 0.4);
  }
  
  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.8);
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
  }
  
  .btn-danger {
    background: rgba(244, 67, 54, 0.2);
    border: 1px solid rgba(244, 67, 54, 0.4);
    color: #F44336;
  }
  
  .btn-danger:hover:not(:disabled) {
    background: rgba(244, 67, 54, 0.3);
    transform: translateY(-2px);
  }
  
  /* Admin actions section */
  .admin-actions {
    margin: 2rem 0;
    padding: 1.5rem;
    background: linear-gradient(135deg, rgba(64, 123, 255, 0.1), rgba(64, 123, 255, 0.05));
    border-radius: 16px;
    border: 1px solid rgba(64, 123, 255, 0.2);
    text-align: center;
    backdrop-filter: blur(10px);
  }
  
  .btn-gestionar {
    padding: 0.875rem 2rem;
    border-radius: 12px;
    font-size: 1.05rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
    background: linear-gradient(135deg, #407BFF 0%, #0052CC 100%);
    color: #fff;
    box-shadow: 0 4px 15px rgba(64, 123, 255, 0.3);
  }
  
  .btn-gestionar:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 25px rgba(64, 123, 255, 0.5);
  }
  
  .btn-gestionar:active {
    transform: translateY(-1px);
  }
</style>