<script>
  import { createEventDispatcher } from "svelte";
  import { guardiasMainController } from "$lib/paneladmin/controllers/index.js";
  import { slide } from "svelte/transition";

  export let fecha;
  export let guardias = [];

  const dispatch = createEventDispatcher();

  // Estado para controlar qué grupos están expandidos
  let expandedGroups = {};

  function cerrar() {
    dispatch("close");
  }

  function toggleGroup(grupoKey) {
    expandedGroups[grupoKey] = !expandedGroups[grupoKey];
  }

  // Agrupar guardias si hay datos
  $: guardiasPorAreaHora =
    guardias.length > 0
      ? guardiasMainController.agruparGuardiasPorAreaHora(guardias)
      : {};

  // Inicializar todos los grupos como "cerrados" o "abiertos" según preferencia.
  // Aquí los dejamos cerrados por defecto, o podríamos abrirlos al cambiar guardias.
  $: {
    if (guardias && Object.keys(expandedGroups).length === 0) {
      // Opcional: abrir el primer grupo por defecto
      // const primerGrupo = Object.keys(guardiasPorAreaHora)[0];
      // if (primerGrupo) expandedGroups[primerGrupo] = true;
    }
  }

  // Helper para extraer datos limpios del primer elemento del grupo
  function getGroupInfo(guardiasGrupo) {
    if (!guardiasGrupo || guardiasGrupo.length === 0) return { area: "", start: "", end: "" };
    const g = guardiasGrupo[0];
    return {
      area: g.area_nombre || "Sin Área",
      start: g.hora_inicio?.substring(0, 5), // 'HH:MM:SS' -> 'HH:MM'
      end: g.hora_fin?.substring(0, 5)
    };
  }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="modal-overlay" on:click={cerrar}>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h3>
        Guardias del {guardiasMainController.formatearFecha(fecha)}
      </h3>
      <button class="close-button" on:click={cerrar}>&times;</button>
    </div>
    
    <div class="modal-body">
      {#if guardias.length > 0}
        <div class="guardias-lista">
          {#each Object.entries(guardiasPorAreaHora) as [grupoKey, guardiasGrupo]}
            {@const info = getGroupInfo(guardiasGrupo)}
            {@const isExpanded = expandedGroups[grupoKey]}
            
            <div class="grupo-container">
              <!-- Encabezado del Grupo (Click para toggle) -->
              <!-- svelte-ignore a11y-click-events-have-key-events -->
              <!-- svelte-ignore a11y-no-static-element-interactions -->
              <div 
                class="grupo-header {isExpanded ? 'expanded' : ''}" 
                on:click={() => toggleGroup(grupoKey)}
              >
                <div class="grupo-info">
                  <div class="grupo-area">
                    <span class="icon-area">🏢</span>
                    <span class="area-nombre">{info.area}</span>
                  </div>
                  <div class="grupo-horario">
                    <span class="icon-time">🕒</span>
                    <span class="horario-texto">{info.start} - {info.end} hs</span>
                  </div>
                </div>
                
                <button class="btn-toggle">
                  <span class="chevron {isExpanded ? 'rotated' : ''}">▼</span>
                </button>
              </div>

              <!-- Lista de Agentes (Colapsable) -->
              {#if isExpanded}
                <div class="agentes-wrapper" transition:slide|local={{ duration: 300 }}>
                  <div class="agentes-grupo">
                    {#each guardiasGrupo as guardia}
                      <div class="guardia-card">
                        <div class="agente-info">
                          <span class="avatar-placeholder">
                            {guardia.agente_nombre.charAt(0)}
                          </span>
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
              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <div class="empty-state">
          <p>No hay guardias registradas para esta fecha.</p>
        </div>
      {/if}
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
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 16px;
    padding: 0;
    max-width: 600px; /* Un poco más angosto para parecer lista moderna */
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .modal-content::-webkit-scrollbar { display: none; }

  /* Header */
  .modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px 16px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
  }

  .close-button {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    font-size: 1.5rem;
    line-height: 1;
    color: white;
    cursor: pointer;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
  }
  .close-button:hover { background: rgba(255, 255, 255, 0.4); }

  /* Body */
  .modal-body {
    padding: 1.5rem;
    background: #f8f9fa;
    min-height: 200px;
  }

  .guardias-lista {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* Grupo Accordion */
  .grupo-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    overflow: hidden;
    border: 1px solid #eee;
    transition: box-shadow 0.2s;
  }
  .grupo-container:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
  }

  .grupo-header {
    padding: 1rem 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background: white;
    transition: background 0.2s;
    user-select: none;
  }
  .grupo-header:hover {
    background: #f1f5f9;
  }
  .grupo-header.expanded {
    background: #eef2ff;
    border-bottom: 1px solid #e2e8f0;
  }

  .grupo-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .grupo-area {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .area-nombre {
    font-weight: 700;
    color: #1e40af;
    font-size: 1.05rem;
  }
  .icon-area { font-size: 1.1rem; }

  .grupo-horario {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    font-size: 0.9rem;
    margin-left: 2px;
  }
  .icon-time { font-size: 0.9rem; }
  .horario-texto { font-weight: 500; }

  /* Toggle Button */
  .btn-toggle {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
  }
  .chevron {
    transition: transform 0.3s ease;
    font-size: 0.8rem;
  }
  .chevron.rotated {
    transform: rotate(180deg);
  }

  /* Agentes List */
  .agentes-wrapper {
    background: #f8fafc;
  }
  .agentes-grupo {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .guardia-card {
    background: white;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    border: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .agente-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .avatar-placeholder {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 2px 4px rgba(118, 75, 162, 0.3);
    flex-shrink: 0;
  }

  .agente-info strong {
    color: #334155;
    font-weight: 600;
  }

  .guardia-detalles {
    display: flex;
    gap: 0.5rem;
  }

  /* Badges */
  .tipo, .estado {
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .tipo-regular { background: #dbeafe; color: #1e40af; }
  .tipo-especial { background: #d1fae5; color: #065f46; }
  .tipo-feriado { background: #fee2e2; color: #991b1b; }
  .tipo-emergencia { background: #fed7aa; color: #9a3412; }

  .estado-planificada { background: #f1f5f9; color: #475569; }
  .estado-confirmada { background: #e0f2fe; color: #0284c7; }
  .estado-completada { background: #dcfce7; color: #16a34a; }
  .estado-cancelada { background: #fee2e2; color: #dc2626; }

  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #64748b;
  }
</style>
