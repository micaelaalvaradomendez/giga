<script>
  import { onMount } from 'svelte';
  import CalendarioBase from '$lib/componentes/calendarioBase.svelte';
  import { guardiasService } from '$lib/services.js';

  const items = [
    { title: 'Planificador', desc: 'Crear nueva guardia', href: '/paneladmin/guardias/planificador', emoji: '➕' },
    { title: 'Aprobaciones  (falta)', desc: 'Revisar y publicar', href: '/paneladmin/guardias/aprobaciones', emoji: '📝' }
  ];

  let loading = false;
  let error = '';
  let guardias = [];
  let guardiasParaCalendario = [];
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
      
      // Agrupar guardias por fecha, área y hora para mostrar en calendario
      agruparGuardias();
      
      console.log('Guardias cargadas:', guardias);
      console.log('Guardias para calendario:', guardiasParaCalendario);
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

  function agruparGuardias() {
    // Estructura: { fecha: { 'area-hora': [guardias] } }
    const agrupadas = {};
    
    guardias.forEach(guardia => {
      const fecha = guardia.fecha;
      if (!agrupadas[fecha]) {
        agrupadas[fecha] = {};
      }
      
      // Agrupar por área y hora para separar guardias de diferentes áreas/horarios
      const clave = `${guardia.area_nombre || 'sin-area'}-${guardia.hora_inicio}-${guardia.hora_fin}`;
      
      if (!agrupadas[fecha][clave]) {
        agrupadas[fecha][clave] = {
          area_nombre: guardia.area_nombre || 'Sin área',
          hora_inicio: guardia.hora_inicio,
          hora_fin: guardia.hora_fin,
          tipo: guardia.tipo,
          agentes: []
        };
      }
      
      agrupadas[fecha][clave].agentes.push(guardia);
    });
    
    // Convertir a formato para el calendario
    guardiasParaCalendario = [];
    Object.keys(agrupadas).forEach(fecha => {
      Object.values(agrupadas[fecha]).forEach(grupo => {
        guardiasParaCalendario.push({
          fecha,
          tipo: grupo.tipo,
          estado: 'planificada',
          area_nombre: grupo.area_nombre,
          agente_nombre: `${grupo.area_nombre} (${grupo.agentes.length} agente${grupo.agentes.length > 1 ? 's' : ''})`,
          hora_inicio: grupo.hora_inicio || '08:00:00',
          hora_fin: grupo.hora_fin || '16:00:00',
          agentes: grupo.agentes,
          cantidad: grupo.agentes.length
        });
      });
    });
  }

  function handleDayClick(event) {
    const { date, guardias: guardiasDelDia } = event.detail;
    if (guardiasDelDia && guardiasDelDia.length > 0) {
      const fechaStr = date.toISOString().split('T')[0];
      fechaSeleccionada = fechaStr;
      
      // Buscar todas las guardias de esa fecha (sin agrupar)
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

  function formatearFecha(fechaStr) {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr + 'T00:00:00');
    return fecha.toLocaleDateString('es-AR', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  }
</script>

<section class="guardias-wrap">
  <header class="head">
    <h1>Planificación de Guardias</h1>
    <p>Elegí una opción para comenzar o revisá el calendario</p>
  </header>

  <div class="grid">
    {#each items as it}
      <a class="card" href={it.href}>
        <div class="icon">{it.emoji}</div>
        <div class="body">
          <h2>{it.title}</h2>
          <p>{it.desc}</p>
        </div>
        <div class="chev">→</div>
      </a>
    {/each}
  </div>

  <!-- Estadísticas de guardias -->
  {#if guardias.length > 0}
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
  {/if}

  <!-- Calendario de guardias -->
  <div class="calendario-section">
    <h2>Calendario de Guardias</h2>
    {#if error}
      <div class="alert alert-error">{error}</div>
    {/if}
    
    <div class="calendario-container">
      {#if loading}
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p>Cargando calendario...</p>
        </div>
      {:else}
        <CalendarioBase 
          {feriados} 
          guardias={guardiasParaCalendario} 
          on:dayclick={handleDayClick} 
        />
      {/if}
    </div>
  </div>
</section>

<!-- Modal para mostrar guardias de una fecha -->
{#if mostrarModal}
  <div class="modal-overlay" on:click={cerrarModal}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Guardias del {formatearFecha(fechaSeleccionada)}</h3>
        <button class="close-button" on:click={cerrarModal}>&times;</button>
      </div>
      <div class="modal-body">
        {#if guardiasDeFecha.length > 0}
          <!-- Agrupar por área y horario -->
          {@const guardiasPorAreaHora = guardiasDeFecha.reduce((acc, g) => {
            const clave = `${g.area_nombre || 'Sin área'} (${g.hora_inicio} - ${g.hora_fin})`;
            if (!acc[clave]) acc[clave] = [];
            acc[clave].push(g);
            return acc;
          }, {})}
          
          <div class="guardias-lista">
            {#each Object.entries(guardiasPorAreaHora) as [grupo, guardiasGrupo]}
              <div class="grupo-area">
                <h4 class="grupo-titulo">{grupo}</h4>
                <div class="agentes-grupo">
                  {#each guardiasGrupo as guardia}
                    <div class="guardia-card">
                      <div class="agente-info">
                        <strong>{guardia.agente_nombre}</strong>
                      </div>
                      <div class="guardia-detalles">
                        <span class="tipo tipo-{guardia.tipo}">{guardia.tipo}</span>
                        <span class="estado estado-{guardia.estado}">{guardia.estado}</span>
                      </div>
                    </div>
                  {/each}
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
  .guardias-wrap {
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
    margin: 0;
    color: #64748b;
    font-size: 1rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
    max-width: 800px;
    margin: 0 auto 2rem auto;
  }

  .card {
    display: grid;
    grid-template-columns: 56px 1fr 20px;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    text-decoration: none;
    background: #fff;
    color: #111827;
    transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.05s ease;
  }
  .card:hover {
    border-color: #bfdbfe;
    box-shadow: 0 8px 24px rgba(30, 64, 175, 0.15);
  }
  .card:active { transform: translateY(1px); }

  .icon { font-size: 28px; text-align: center; }

  .body h2 {
    margin: 0 0 4px 0;
    font-size: 1.05rem;
    line-height: 1.2;
  }
  .body p {
    margin: 0;
    font-size: 0.9rem;
    color: #64748b;
  }

  .chev { color: #94a3b8; font-weight: 700; }

  /* Estadísticas */
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

  /* Calendario */
  .calendario-section {
    margin-top: 3rem;
  }

  .calendario-section h2 {
    font-size: 1.5rem;
    color: #1e40af;
    margin-bottom: 1.5rem;
    text-align: center;
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
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    padding: 0;
    max-width: 700px;
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
    font-size: 1.1rem;
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
    gap: 1.5rem;
  }

  .grupo-area {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    background: #f8f9fa;
  }

  .grupo-titulo {
    font-size: 1rem;
    color: #1e40af;
    margin: 0 0 1rem 0;
    font-weight: 600;
  }

  .agentes-grupo {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .guardia-card {
    background: white;
    border-radius: 6px;
    padding: 0.75rem;
    border-left: 4px solid #1e40af;
  }

  .agente-info {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: #333;
  }

  .agente-info strong {
    color: #1e40af;
  }

  .guardia-detalles {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
  }

  .tipo, .estado {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .tipo-regular {
    background: #dbeafe;
    color: #1e40af;
  }

  .tipo-especial {
    background: #d1fae5;
    color: #065f46;
  }

  .tipo-feriado {
    background: #fee2e2;
    color: #991b1b;
  }

  .tipo-emergencia {
    background: #fed7aa;
    color: #9a3412;
  }

  .estado-planificada {
    background: #e5e7eb;
    color: #374151;
  }

  .estado-confirmada {
    background: #dbeafe;
    color: #1e40af;
  }

  .estado-completada {
    background: #d1fae5;
    color: #065f46;
  }

  .estado-cancelada {
    background: #fee2e2;
    color: #991b1b;
  }

  @media (max-width: 900px) {
    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .estadisticas {
      grid-template-columns: 1fr;
    }
  }
  @media (max-width: 640px) {
    .grid { grid-template-columns: 1fr; }
  }
</style>
