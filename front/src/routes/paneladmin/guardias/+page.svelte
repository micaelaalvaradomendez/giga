<script>
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import CalendarioBase from "$lib/componentes/calendarioBase.svelte";
  import { guardiasMainController } from "$lib/paneladmin/controllers/index.js";

  // Items de navegación
  const items = [
    {
      title: "Planificador",
      desc: "Crear nueva guardia",
      href: "/paneladmin/guardias/planificador",
      emoji: "➕",
    },
    {
      title: "Aprobaciones",
      desc: "Revisar y publicar",
      href: "/paneladmin/guardias/aprobaciones",
      emoji: "📝",
    },
    {
      title: "Compensaciones",
      desc: "Compensaciones horas guardias y extras",
      href: "/paneladmin/guardias/compensaciones",
      emoji: "📝",
    },
  ];

  // Obtener stores del controller
  const {
    loading,
    error,
    guardiasParaCalendario,
    feriados,
    fechaSeleccionada,
    guardiasDeFecha,
    mostrarModal,
    estadisticas,
  } = guardiasMainController;

  onMount(async () => {
    console.log("🔄 Componente de guardias montado, iniciando controller...");
    await guardiasMainController.init();
    console.log("✅ Controller de guardias inicializado");

    // Recargar cuando la página vuelve a ser visible
    if (browser) {
      const handleVisibilityChange = () => {
        if (document.visibilityState === "visible") {
          guardiasMainController.recargar();
        }
      };

      const handleFocus = () => {
        guardiasMainController.recargar();
      };

      document.addEventListener("visibilitychange", handleVisibilityChange);
      window.addEventListener("focus", handleFocus);

      return () => {
        document.removeEventListener(
          "visibilitychange",
          handleVisibilityChange,
        );
        window.removeEventListener("focus", handleFocus);
      };
    }
  });

  // Handlers delegados al controller
  function handleDayClick(event) {
    const { date, guardias: guardiasDelDia } = event.detail;
    guardiasMainController.handleDayClick(date, guardiasDelDia);
  }

  function handleCerrarModal() {
    guardiasMainController.cerrarModal();
  }
</script>

<section class="guardias-wrap">
  <header class="head">
    <h1>Planificación de Guardias</h1>
    <p>Elegí una opción para comenzar o revisá el calendario</p>
  </header>
  <div class="grid-general">
    <div class="left">
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

      <!-- Estadísticas de guardias -->
      {#if $estadisticas.total > 0}
        <div class="estadisticas">
          <div class="stat-card">
            <div class="stat-number">{$estadisticas.total}</div>
            <div class="stat-label">Guardias Total</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{$estadisticas.planificadas}</div>
            <div class="stat-label">Planificadas</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{$estadisticas.activas}</div>
            <div class="stat-label">Activas</div>
          </div>
        </div>
      {/if}
    </div>

    <!-- Calendario de guardias -->
    <div class="right">
      <div class="calendario-section">
        <div class="titulo-wrapper">
          <h2>Calendario de Guardias</h2>
        </div>
        {#if $error}
          <div class="alert alert-error">{$error}</div>
        {/if}

        <div class="calendario-container">
          {#if $loading}
            <div class="loading-container">
              <div class="loading-spinner"></div>
              <p>Cargando calendario...</p>
            </div>
          {:else}
            <CalendarioBase
              feriados={$feriados}
              guardias={$guardiasParaCalendario}
              on:dayclick={handleDayClick}
            />
          {/if}
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Modal para mostrar guardias de una fecha -->
{#if $mostrarModal}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal-overlay" on:click={handleCerrarModal}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3>
          Guardias del {guardiasMainController.formatearFecha(
            $fechaSeleccionada,
          )}
        </h3>
        <button class="close-button" on:click={handleCerrarModal}
          >&times;</button
        >
      </div>
      <div class="modal-body">
        {#if $guardiasDeFecha.length > 0}
          <!-- Agrupar por área y horario -->
          {@const guardiasPorAreaHora =
            guardiasMainController.agruparGuardiasPorAreaHora($guardiasDeFecha)}

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
                        <span class="tipo tipo-{guardia.tipo}"
                          >{guardia.tipo}</span
                        >
                        <span class="estado estado-{guardia.estado}"
                          >{guardia.estado}</span
                        >
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
    width: 100%;
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .head {
    position: relative;
    background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
    color: white;
    padding: 30px 40px;
    max-width: 1600px;
    border-radius: 28px;
    overflow: hidden;
    text-align: center;
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.1) inset,
      0 10px 30px rgba(30, 64, 175, 0.4);
    text-align: center;
    margin-bottom: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .head::before {
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

  .head h1 {
    margin: 10px;
    font-weight: 800;
    font-size: 30px;
    letter-spacing: 0.2px;
    position: relative;
    padding-bottom: 12px;
    overflow: hidden;
    display: inline-block;
  }

  .head h1::after {
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
  .head p {
    color: #0d47a1;
    font-weight: 600;
    font-size: 16px;
    margin-top: 0.5rem;
    margin-bottom: 10px;
    padding: 0.5rem 1rem;
    background: #e3f2fd;
    border-radius: 8px;
    display: inline-flex;
  }

  .grid-general {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 2rem;
    align-items: start;
  }

  .left {
    display: flex;
    gap: 1rem;
    flex-direction: column;
  }

  .card {
    display: grid;
    grid-template-columns: 64px 1fr 24px;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    border: 2px solid #9fb2d8;
    border-radius: 16px;
    text-decoration: none;
    background: #fff;
    color: #111827;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition:
      box-shadow 0.2s ease,
      border-color 0.2s ease,
      transform 0.05s ease;
  }
  .card:hover {
    border-color: #377dd3;
    box-shadow: 0 12px 232px rgba(30, 64, 175, 0.15);
  }
  .card:active {
    transform: translateY(1px);
  }

  .icon {
    font-size: 28px;
    text-align: center;
  }

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

  .chev {
    color: #001e4bb4;
    font-weight: 700;
    font-size: 2rem;
  }

  /* Estadísticas */
  .estadisticas {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .stat-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    border-top: 4px solid #2372a7;
    border-bottom: 2px solid #4949491e;
    transition: transform 0.3s ease;
  }

  .stat-card:hover {
    transform: translateY(-5px);
  }

  .stat-number {
    font-size: 2.2rem;
    font-weight: 700;
    color: #2372a7;
    margin: 0;
  }

  .stat-label {
    margin: 0 0 10px;
    color: #000000;
    font-size: 16px;
    font-weight: 600;
    text-transform: uppercase;
  }

  /* Calendario */
  .right {
    width: 100%;
  }

  .calendario-section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
  }

  .titulo-wrapper {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .calendario-section h2 {
    font-size: 30px;
    color: #1e40af;
    margin: 0;
    letter-spacing: 0.2px;
    position: relative;
    padding-bottom: 12px;
    display: inline-block;
    overflow: hidden;
  }

  .calendario-section h2::after {
    content: "";
    position: absolute;
    width: 40%;
    height: 3px;
    bottom: 0;
    left: 30%;
    right: 90%;
    background: linear-gradient(90deg, transparent, #1e40af, transparent);
    animation: moveLine 2s linear infinite;
  }

  .calendario-container {
    margin-bottom: 0;
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
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
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

  .tipo,
  .estado {
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
    .grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .estadisticas {
      grid-template-columns: 1fr;
    }
  }
  @media (max-width: 640px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>
