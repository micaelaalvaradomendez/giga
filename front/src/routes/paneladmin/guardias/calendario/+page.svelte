<script>
  import { onMount } from 'svelte';
  import CalendarioBase from '$lib/componentes/calendarioBase.svelte';
  import { guardiasService } from '$lib/services.js';

  let loading = false;
  let error = '';
  let guardias = [];
  let guardiasAgrupadas = [];
  let feriados = [];
  let fechaSeleccionada = null;
  let guardiasDeFecha = [];
  let mostrarModal = false;

  onMount(async () => {
    await cargarDatos();
  });

  async function cargarDatos() {
    await Promise.all([
      cargarGuardias(),
      cargarFeriados()
    ]);
  }

  async function cargarGuardias() {
    try {
      loading = true;
      error = '';
      const response = await guardiasService.getResumenGuardias('');
      guardias = response.data?.guardias || [];
      
      // Agrupar guardias por fecha
      agruparGuardiasPorFecha();
      
      console.log('Guardias cargadas:', guardias);
      console.log('Guardias agrupadas:', guardiasAgrupadas);
    } catch (e) {
      error = 'Error al cargar las guardias';
      console.error('Error cargando guardias:', e);
    } finally {
      loading = false;
    }
  }

  async function cargarFeriados() {
    try {
      const response = await guardiasService.getFeriados();
      feriados = response.data?.results || response.data || [];
      console.log('Feriados cargados:', feriados);
    } catch (e) {
      console.error('Error cargando feriados:', e);
      feriados = [];
    }
  }

  function agruparGuardiasPorFecha() {
    const agrupadas = {};
    
    guardias.forEach(guardia => {
      const fecha = guardia.fecha;
      if (!agrupadas[fecha]) {
        agrupadas[fecha] = [];
      }
      agrupadas[fecha].push(guardia);
    });
    
    // Convertir a array para usar en el calendario
    guardiasAgrupadas = Object.keys(agrupadas).map(fecha => ({
      fecha,
      tipo: 'regular',
      estado: 'planificada',
      agentes: agrupadas[fecha],
      cantidad: agrupadas[fecha].length,
      // Para mostrar en el calendario, usamos el primer agente como referencia
      agente_nombre: `${agrupadas[fecha].length} agente${agrupadas[fecha].length > 1 ? 's' : ''}`,
      hora_inicio: agrupadas[fecha][0]?.hora_inicio || '08:00:00',
      hora_fin: agrupadas[fecha][0]?.hora_fin || '16:00:00'
    }));
  }

  function handleDayClick(event) {
    const { date, guardias: guardiasDelDia } = event.detail;
    if (guardiasDelDia && guardiasDelDia.length > 0) {
      const fechaStr = date.toISOString().split('T')[0];
      fechaSeleccionada = fechaStr;
      
      // Buscar todas las guardias de esa fecha
      guardiasDeFecha = guardias.filter(g => g.fecha === fechaStr);
      mostrarModal = true;
      
      console.log('Guardias del día seleccionado:', guardiasDeFecha);
    }
  }

  function cerrarModal() {
    mostrarModal = false;
    fechaSeleccionada = null;
    guardiasDeFecha = [];
  }
</script>

<section class="calendario-guardias-wrap">
  <header class="head">
    <h1>Calendario de Guardias</h1>
    <p class="subtitle">Vista general de todas las guardias programadas</p>
  </header>

  {#if error}
    <div class="alert alert-error">{error}</div>
  {/if}

  <div class="estadisticas">
    <div class="stat-card">
      <div class="stat-number">{guardias.length}</div>
      <div class="stat-label">Guardias Total</div>
    </div>
    <div class="stat-card">
      <div class="stat-number">{guardias.filter(g => g.estado === 'planificada').length}</div>
      <div class="stat-label">Planificadas</div>
    </div>
    <div class="stat-card">
      <div class="stat-number">{guardias.filter(g => g.activa).length}</div>
      <div class="stat-label">Activas</div>
    </div>
  </div>

  <div class="calendario-container">
    {#if loading}
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>Cargando calendario...</p>
      </div>
    {:else}
      <CalendarioBase 
        {feriados} 
        guardias={guardiasAgrupadas} 
        on:dayclick={handleDayClick} 
      />
    {/if}
  </div>
</section>

<!-- Modal para mostrar guardias de una fecha -->
{#if mostrarModal}
  <div class="modal-overlay" on:click={cerrarModal}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Guardias del {new Date(fechaSeleccionada + 'T00:00:00').toLocaleDateString('es-AR', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        })}</h3>
        <button class="close-button" on:click={cerrarModal}>&times;</button>
      </div>
      <div class="modal-body">
        {#if guardiasDeFecha.length > 0}
          <div class="guardias-lista">
            {#each guardiasDeFecha as guardia}
              <div class="guardia-card">
                <div class="agente-info">
                  <strong>{guardia.agente_nombre}</strong>
                </div>
                <div class="guardia-detalles">
                  <span class="horario">{guardia.hora_inicio} - {guardia.hora_fin}</span>
                  <span class="tipo tipo-{guardia.tipo}">{guardia.tipo}</span>
                  <span class="estado estado-{guardia.estado}">{guardia.estado}</span>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p>No hay guardias para esta fecha.</p>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
.calendario-guardias-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: Verdana, Geneva, Tahoma, sans-serif;
}

.head {
  margin-bottom: 2rem;
  text-align: center;
}

.head h1 {
  font-size: 1.8rem;
  margin: 0 0 0.5rem 0;
  color: #1e40af;
}

.head .subtitle {
  margin: 0;
  color: #64748b;
  font-size: 1rem;
}

.estadisticas {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1e40af;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.calendario-container {
  margin-bottom: 2rem;
}

.loading-container {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.loading-spinner {
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
}

@media (max-width: 768px) {
  .estadisticas {
    grid-template-columns: 1fr;
  }
}

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
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  text-transform: capitalize;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-button:hover {
  background: #e9ecef;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.guardias-lista {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.guardia-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #1e40af;
}

.agente-info {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.guardia-detalles {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.horario {
  background: #e9ecef;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #495057;
  font-weight: 500;
}

.tipo, .estado {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.tipo-regular {
  background: #d1ecf1;
  color: #0c5460;
}

.tipo-especial {
  background: #fff3cd;
  color: #856404;
}

.estado-planificada {
  background: #d4edda;
  color: #155724;
}

.estado-confirmada {
  background: #cce5ff;
  color: #004085;
}

.estado-cancelada {
  background: #f8d7da;
  color: #721c24;
}
</style>