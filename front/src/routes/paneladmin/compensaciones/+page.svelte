<script>
  import GestionCompensaciones from '$lib/componentes/GestionCompensaciones.svelte';
  import { onMount } from 'svelte';

  let paginaActiva = 'compensaciones';

  // Navegación entre secciones
  const secciones = [
    { id: 'compensaciones', titulo: 'Gestión de Compensaciones', icono: '⏱️' },
    { id: 'reportes', titulo: 'Reportes de Compensaciones', icono: '📊' },
    { id: 'configuracion', titulo: 'Configuración', icono: '⚙️' }
  ];

  function cambiarSeccion(seccionId) {
    paginaActiva = seccionId;
  }
</script>

<svelte:head>
  <title>Sistema de Compensaciones - GIGA</title>
</svelte:head>

<div class="compensaciones-layout">
  <!-- Navegación lateral -->
  <nav class="sidebar">
    <div class="sidebar-header">
      <h2>💼 Sistema de Compensaciones</h2>
      <p class="version">v2.0 - Horas de Emergencia</p>
    </div>

    <ul class="nav-menu">
      {#each secciones as seccion}
        <li>
          <button 
            class="nav-item {paginaActiva === seccion.id ? 'active' : ''}"
            on:click={() => cambiarSeccion(seccion.id)}
          >
            <span class="nav-icono">{seccion.icono}</span>
            <span class="nav-texto">{seccion.titulo}</span>
          </button>
        </li>
      {/each}
    </ul>

    <div class="sidebar-footer">
      <div class="info-sistema">
        <h4>ℹ️ Información del Sistema</h4>
        <ul>
          <li><strong>Límite reglamentario:</strong> 10 horas por guardia</li>
          <li><strong>Máximo horas extra:</strong> 8 horas por servicio</li>
          <li><strong>Plazo solicitud:</strong> 30 días desde el servicio</li>
          <li><strong>Plus con compensaciones:</strong> Se incluyen en cálculo mensual</li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Contenido principal -->
  <main class="main-content">
    {#if paginaActiva === 'compensaciones'}
      <GestionCompensaciones />
    
    {:else if paginaActiva === 'reportes'}
      <div class="seccion-reportes">
        <h1>📊 Reportes de Compensaciones</h1>
        <p class="descripcion">
          Genere reportes detallados sobre las horas de compensación por emergencias
        </p>

        <div class="reportes-grid">
          <div class="reporte-card">
            <h3>📋 Reporte Mensual por Agente</h3>
            <p>Compensaciones individuales de un agente en un período específico</p>
            <button class="btn-report">Generar Reporte</button>
          </div>

          <div class="reporte-card">
            <h3>🏢 Reporte General por Área</h3>
            <p>Resumen de compensaciones por área organizacional</p>
            <button class="btn-report">Generar Reporte</button>
          </div>

          <div class="reporte-card">
            <h3>💰 Impacto en Plus Salarial</h3>
            <p>Análisis del efecto de compensaciones en cálculo de plus</p>
            <button class="btn-report">Generar Reporte</button>
          </div>

          <div class="reporte-card">
            <h3>📈 Estadísticas por Motivo</h3>
            <p>Análisis de compensaciones agrupadas por tipo de emergencia</p>
            <button class="btn-report">Generar Reporte</button>
          </div>
        </div>

        <div class="reporte-explicacion">
          <h4>💡 Cómo funciona el sistema</h4>
          <div class="explicacion-grid">
            <div class="explicacion-item">
              <h5>1. Registro de Emergencia</h5>
              <p>Cuando un servicio se extiende más allá de las 10 horas reglamentarias por una emergencia, se registra la compensación correspondiente.</p>
            </div>
            <div class="explicacion-item">
              <h5>2. Aprobación Jerárquica</h5>
              <p>Las compensaciones deben ser aprobadas por superiores según la jerarquía organizacional establecida.</p>
            </div>
            <div class="explicacion-item">
              <h5>3. Inclusión en Plus</h5>
              <p>Las horas de compensación aprobadas se suman automáticamente al cálculo mensual de plus salarial.</p>
            </div>
            <div class="explicacion-item">
              <h5>4. Control y Auditoría</h5>
              <p>Todos los movimientos quedan registrados en el sistema de auditoría para control y seguimiento.</p>
            </div>
          </div>
        </div>
      </div>

    {:else if paginaActiva === 'configuracion'}
      <div class="seccion-configuracion">
        <h1>⚙️ Configuración del Sistema</h1>
        <p class="descripcion">
          Configurar parámetros del sistema de compensaciones
        </p>

        <div class="config-sections">
          <div class="config-card">
            <h3>⏱️ Límites Horarios</h3>
            <div class="config-items">
              <div class="config-item">
                <label>Límite reglamentario por guardia</label>
                <input type="number" value="10" readonly /> <span>horas</span>
              </div>
              <div class="config-item">
                <label>Máximo horas extra por servicio</label>
                <input type="number" value="8" readonly /> <span>horas</span>
              </div>
              <div class="config-item">
                <label>Máximo servicio total</label>
                <input type="number" value="18" readonly /> <span>horas</span>
              </div>
            </div>
            <p class="config-note">⚠️ Estos valores están definidos por normativa y no pueden modificarse</p>
          </div>

          <div class="config-card">
            <h3>📅 Plazos y Validaciones</h3>
            <div class="config-items">
              <div class="config-item">
                <label>Plazo máximo para solicitar compensación</label>
                <input type="number" value="30" readonly /> <span>días</span>
              </div>
              <div class="config-item">
                <label>Validación automática de fechas</label>
                <select disabled>
                  <option>Activada - Solo fines de semana y feriados</option>
                </select>
              </div>
            </div>
          </div>

          <div class="config-card">
            <h3>💰 Cálculo de Plus</h3>
            <div class="config-items">
              <div class="config-item">
                <label>Inclusión en cálculo mensual</label>
                <select disabled>
                  <option>Activada - Horas aprobadas se suman</option>
                </select>
              </div>
              <div class="config-item">
                <label>Reglas de plus vigentes</label>
                <div class="reglas-plus">
                  <ul>
                    <li>🟢 Área operativa + guardias/compensaciones = 40%</li>
                    <li>🟡 Otras áreas + 32+ horas = 40%</li>
                    <li>🔵 Resto con actividad = 20%</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="config-card">
            <h3>🔧 Funciones del Sistema</h3>
            <div class="funciones-lista">
              <div class="funcion-item">
                <span class="funcion-status activa">✅</span>
                <span>Validación automática de horas</span>
              </div>
              <div class="funcion-item">
                <span class="funcion-status activa">✅</span>
                <span>Cálculo automático de horas extra</span>
              </div>
              <div class="funcion-item">
                <span class="funcion-status activa">✅</span>
                <span>Integración con sistema de guardias</span>
              </div>
              <div class="funcion-item">
                <span class="funcion-status activa">✅</span>
                <span>Auditoría completa de cambios</span>
              </div>
              <div class="funcion-item">
                <span class="funcion-status activa">✅</span>
                <span>Cálculo de plus actualizado</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </main>
</div>

<style>
  .compensaciones-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    min-height: 100vh;
    background: #f8fafc;
  }

  .sidebar {
    background: #1e293b;
    color: white;
    padding: 0;
    overflow-y: auto;
  }

  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid #334155;
  }

  .sidebar-header h2 {
    margin: 0 0 8px 0;
    font-size: 18px;
    color: #f1f5f9;
  }

  .version {
    margin: 0;
    color: #94a3b8;
    font-size: 12px;
  }

  .nav-menu {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .nav-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 12px 20px;
    background: none;
    border: none;
    color: #cbd5e1;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 14px;
  }

  .nav-item:hover {
    background: #334155;
    color: #f1f5f9;
  }

  .nav-item.active {
    background: #3b82f6;
    color: white;
  }

  .nav-icono {
    margin-right: 12px;
    font-size: 16px;
  }

  .sidebar-footer {
    margin-top: auto;
    padding: 20px;
    border-top: 1px solid #334155;
  }

  .info-sistema h4 {
    margin: 0 0 12px 0;
    color: #f1f5f9;
    font-size: 14px;
  }

  .info-sistema ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .info-sistema li {
    padding: 4px 0;
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.4;
  }

  .main-content {
    padding: 0;
    overflow-y: auto;
  }

  .seccion-reportes, .seccion-configuracion {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  .seccion-reportes h1, .seccion-configuracion h1 {
    color: #1e293b;
    margin-bottom: 8px;
  }

  .descripcion {
    color: #64748b;
    margin-bottom: 32px;
  }

  .reportes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
  }

  .reporte-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .reporte-card h3 {
    margin: 0 0 12px 0;
    color: #1e293b;
    font-size: 16px;
  }

  .reporte-card p {
    margin: 0 0 16px 0;
    color: #64748b;
    font-size: 14px;
    line-height: 1.5;
  }

  .btn-report {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-report:hover {
    background: #2563eb;
  }

  .reporte-explicacion {
    background: white;
    padding: 24px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .reporte-explicacion h4 {
    margin: 0 0 20px 0;
    color: #1e293b;
  }

  .explicacion-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
  }

  .explicacion-item h5 {
    margin: 0 0 8px 0;
    color: #3b82f6;
    font-size: 14px;
  }

  .explicacion-item p {
    margin: 0;
    color: #64748b;
    font-size: 13px;
    line-height: 1.5;
  }

  .config-sections {
    display: grid;
    gap: 20px;
  }

  .config-card {
    background: white;
    padding: 24px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .config-card h3 {
    margin: 0 0 16px 0;
    color: #1e293b;
    font-size: 16px;
  }

  .config-items {
    display: grid;
    gap: 16px;
  }

  .config-item {
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 12px;
  }

  .config-item label {
    color: #374151;
    font-size: 14px;
    font-weight: 500;
  }

  .config-item input, .config-item select {
    padding: 6px 10px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 14px;
    width: 80px;
  }

  .config-item span {
    color: #6b7280;
    font-size: 13px;
  }

  .config-note {
    margin: 16px 0 0 0;
    color: #d97706;
    font-size: 12px;
    font-style: italic;
  }

  .reglas-plus ul {
    list-style: none;
    padding: 0;
    margin: 8px 0 0 0;
  }

  .reglas-plus li {
    padding: 4px 0;
    font-size: 13px;
    color: #374151;
  }

  .funciones-lista {
    display: grid;
    gap: 8px;
  }

  .funcion-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
  }

  .funcion-status.activa {
    color: #10b981;
    font-weight: bold;
  }

  .funcion-item span:last-child {
    color: #374151;
    font-size: 14px;
  }

  @media (max-width: 768px) {
    .compensaciones-layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }

    .sidebar {
      position: relative;
      height: auto;
    }

    .sidebar-footer {
      display: none;
    }

    .nav-menu {
      display: flex;
      overflow-x: auto;
    }

    .nav-item {
      white-space: nowrap;
      min-width: 150px;
    }

    .reportes-grid {
      grid-template-columns: 1fr;
    }

    .explicacion-grid {
      grid-template-columns: 1fr;
    }

    .config-item {
      grid-template-columns: 1fr;
      text-align: left;
      gap: 8px;
    }
  }
</style>