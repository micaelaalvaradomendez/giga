<script>
  const items = [
    { title: 'Planificador', desc: 'Crear nueva guardia', href: '/paneladmin/guardias/planificador', emoji: '➕' },
    { title: 'Calendario', desc: 'Ver guardias en calendario', href: '/paneladmin/guardias/calendario', emoji: '📅' },
    { title: 'Aprobaciones  (falta)', desc: 'Revisar y publicar', href: '/paneladmin/guardias/aprobaciones', emoji: '📝' }
  ];
</script>

<section class="guardias-wrap">
  <header class="head">
    <h1>Planificación de Guardias</h1>
    <p>Elegí una opción para comenzar</p>
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

  <h3> en planificador ocnsiderar que no puedo asignarle una guardia a un agente si ya tiene una guardia asignada para esa fecha</h3>
  <h3> en el calendario hay que mostrar los agentes en funcion de la guardia creada, separarlos y si hay dos guardias de diferentes areas para le mismo dia y la misma hora, entonces deberia separarse</h3>
</section>

<style>
  .guardias-wrap {
    max-width: 1100px;
    margin: 0 auto;
    padding: 1.5rem;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
  }

  .head h1 {
    font-size: 1.6rem;
    margin: 0 0 0.25rem 0;
    color: #1e40af;
  }
  .head p {
    margin: 0 0 1rem 0;
    color: #475569;
    font-size: 0.95rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    max-width: 1000px;
    margin: 0 auto;
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

  @media (max-width: 900px) {
    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
  @media (max-width: 640px) {
    .grid { grid-template-columns: 1fr; }
  }
</style>
