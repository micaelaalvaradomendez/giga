<script>
  import { onMount } from "svelte";
  import { reporteController } from "$lib/paneladmin/controllers/reporteController.js";
  // Obtener referencias a los stores del controlador
  const {
    loading,
    loadingFiltros,
    exportando,
    error,
    mensaje,
    filtrosDisponibles,
    filtrosSeleccionados,
    datosReporte,
    tipoReporteActual,
    vistaPreviaVisible,
    opcionesExport,
    puedeGenerarReporte,
    hayDatos,
    cargandoGeneral,
    validacionFechas,
    agentesFiltrados,
  } = reporteController;
  // Inicialización
  onMount(async () => {
    await reporteController.inicializar();
  });
  // Funciones del componente
  function handleTipoReporteChange(event) {
    reporteController.cambiarTipoReporte(event.target.value);
  }
  function handleFiltroChange(campo, valor) {
    reporteController.actualizarFiltro(campo, valor);
    // Si cambió el área, resetear la selección de agente
    if (campo === "area_id") {
      reporteController.actualizarFiltro("agente_id", null);
    }
  }
  async function generarReporte() {
    const tipo = $tipoReporteActual;
    switch (tipo) {
      case "individual":
        await reporteController.generarReporteIndividual();
        break;
      case "general":
        await reporteController.generarReporteGeneral();
        break;
      case "horas_trabajadas":
        await reporteController.generarReporteHorasTrabajadas();
        break;
      case "parte_diario":
        await reporteController.generarReporteParteDiario();
        break;
      case "resumen_licencias":
        await reporteController.generarReporteResumenLicencias();
        break;
      case "calculo_plus":
        await reporteController.generarReporteCalculoPlus();
        break;
      case "incumplimiento_normativo":
        await reporteController.generarReporteIncumplimientoNormativo();
        break;
    }
  }
  // Funciones de exportación
  async function exportarPDF() {
    await reporteController.exportarPDF();
  }
  async function exportarExcel() {
    await reporteController.exportarExcel();
  }
  // Funciones de filtros rápidos
  function seleccionarMesActual() {
    reporteController.seleccionarMesActual();
  }
  function seleccionarMesAnterior() {
    reporteController.seleccionarMesAnterior();
  }
  function resetearFiltros() {
    reporteController.resetearFiltros();
  }
  // Precompute Maps for O(1) lookups in table rendering
  // This converts agente.dias arrays to Maps indexed by fecha for fast access
  $: agenteDiasMap =
    $datosReporte?.agentes?.reduce((map, agente) => {
      const diasByFecha = new Map();
      agente.dias?.forEach((d) => diasByFecha.set(d.fecha, d));
      map.set(agente, diasByFecha);
      return map;
    }, new Map()) || new Map();
  // Precompute totals per day to avoid reduce+find in template
  // Note: This depends on agenteDiasMap being computed first (Svelte handles this via reactive statement ordering)
  $: totalesPorDia = (() => {
    // Ensure agenteDiasMap is ready before computing totals
    if (!agenteDiasMap.size || !$datosReporte?.dias_columnas) {
      return new Map();
    }
    return $datosReporte.dias_columnas.reduce((map, dia) => {
      const total =
        $datosReporte.agentes?.reduce((sum, agente) => {
          const diaData = agenteDiasMap.get(agente)?.get(dia.fecha);
          return sum + (diaData?.horas || 0);
        }, 0) || 0;
      map.set(dia.fecha, total);
      return map;
    }, new Map());
  })();
  // Helper function to get day data for an agent (uses precomputed map)
  function getDiaData(agente, fecha) {
    return agenteDiasMap.get(agente)?.get(fecha);
  }
  // Helper function to get total for a day (uses precomputed map)
  function getTotalDia(fecha) {
    return totalesPorDia.get(fecha) || 0;
  }
</script>

<svelte:head>
  <title>Reportes - Panel Administrador | Sistema GIGA</title>
</svelte:head>
<div class="container-reportes">
  <!-- Encabezado -->
  <div class="page-header">
    <div class="header-title">
      <h1>Gestión de Reportes</h1>
    </div>
  </div>
  <header class="header-reportes-messages">
    {#if $mensaje}
      <div class="mensaje mensaje-exito">
        <span>✅ {$mensaje}</span>
      </div>
    {/if}
    {#if $error}
      <div class="mensaje mensaje-error">
        <span>❌ {$error}</span>
      </div>
    {/if}
  </header>
  <!-- Selector de tipo de reporte -->
  <section class="selector-tipo">
    <div class="selector-tipo-container">
      {#if false}
        <label class="selector-opcion">
          <input
            type="radio"
            bind:group={$tipoReporteActual}
            value="individual"
            on:change={handleTipoReporteChange}
            disabled={$cargandoGeneral}
          />
          <div class="opcion-contenido">
            <strong>📋 Reporte Individual</strong>
            <span>Planilla detallada de guardias por agente</span>
          </div>
        </label>
      {/if}
      <label class="selector-opcion">
        <input
          type="radio"
          bind:group={$tipoReporteActual}
          value="general"
          on:change={handleTipoReporteChange}
          disabled={$cargandoGeneral}
        />
        <div class="opcion-contenido">
          <strong>📊 Reporte General</strong>
          <span>Resumen de guardias por área/dirección</span>
        </div>
      </label>
      {#if false}
        <label class="selector-opcion">
          <input
            type="radio"
            bind:group={$tipoReporteActual}
            value="horas_trabajadas"
            on:change={handleTipoReporteChange}
            disabled={$cargandoGeneral}
          />
          <div class="opcion-contenido">
            <strong>⏰ Guardias y Compensaciones</strong>
            <span
              >Horas de guardia programadas vs efectivas (fines de
              semana/feriados únicamente)</span
            >
          </div>
        </label>
      {/if}
    </div>
    <div class="selector-tipo-container">
      <label class="selector-opcion">
        <input
          type="radio"
          bind:group={$tipoReporteActual}
          value="parte_diario"
          on:change={handleTipoReporteChange}
          disabled={$cargandoGeneral}
        />
        <div class="opcion-contenido">
          <strong>📅 Parte Diario/Mensual Consolidado</strong>
          <span
            >Marcas de ingreso/egreso y novedades (llegadas tarde, retiros,
            comisiones)</span
          >
        </div>
      </label>
      <label class="selector-opcion">
        <input
          type="radio"
          bind:group={$tipoReporteActual}
          value="resumen_licencias"
          on:change={handleTipoReporteChange}
          disabled={$cargandoGeneral}
        />
        <div class="opcion-contenido">
          <strong>🏥 Resumen de Licencias</strong>
          <span>Consumo de días por tipo de licencia y límites anuales</span>
        </div>
      </label>
    </div>
    <div class="selector-tipo-container">
      <label class="selector-opcion">
        <input
          type="radio"
          bind:group={$tipoReporteActual}
          value="calculo_plus"
          on:change={handleTipoReporteChange}
          disabled={$cargandoGeneral}
        />
        <div class="opcion-contenido">
          <strong>💲 Cálculo Plus por Guardias (20% / 40%)</strong>
          <span
            >Área operativa + guardia = 40% | Otras áreas + 32h = 40% | Resto =
            20%</span
          >
        </div>
      </label>
    </div>
    <div class="selector-tipo-container">
      <label class="selector-opcion">
        <input
          type="radio"
          bind:group={$tipoReporteActual}
          value="incumplimiento_normativo"
          on:change={handleTipoReporteChange}
          disabled={$cargandoGeneral}
        />
        <div class="opcion-contenido">
          <strong>⚠️ Reporte de Incumplimiento Normativo</strong>
          <span
            >Alertas de violaciones a reglas de horas semanales y descansos</span
          >
        </div>
      </label>
    </div>
  </section>
  <!-- Panel de filtros -->
  <section class="panel-filtros">
    <div class="panel-header">
      <h2>🎯 Filtros de Búsqueda</h2>
      <button
        class="btn btn-secundario btn-pequeño"
        on:click={resetearFiltros}
        disabled={$cargandoGeneral}
      >
        🔄 Resetear
      </button>
    </div>
    <div class="filtros-grid">
      <!-- Rango de fechas -->
      <div class="filtro-grupo">
        <span class="filtro-label">📅 Período:</span>
        <div class="rango-fechas">
          <input
            type="date"
            bind:value={$filtrosSeleccionados.fecha_desde}
            on:change={(e) => handleFiltroChange("fecha_desde", e.target.value)}
            disabled={$cargandoGeneral}
            class="input-fecha"
            aria-label="Fecha desde"
          />
          <span class="rango-separador">hasta</span>
          <input
            type="date"
            bind:value={$filtrosSeleccionados.fecha_hasta}
            on:change={(e) => handleFiltroChange("fecha_hasta", e.target.value)}
            disabled={$cargandoGeneral}
            class="input-fecha"
            aria-label="Fecha hasta"
          />
        </div>
        <!-- Botones de selección rápida -->
        <div class="botones-rapidos">
          <button
            class="btn-rapido"
            on:click={seleccionarMesActual}
            disabled={$cargandoGeneral}
          >
            Mes actual
          </button>
          <button
            class="btn-rapido"
            on:click={seleccionarMesAnterior}
            disabled={$cargandoGeneral}
          >
            Mes anterior
          </button>
        </div>
        {#if !$validacionFechas.valido}
          <div class="error-validacion">{$validacionFechas.mensaje}</div>
        {/if}
      </div>
      <!-- Área (para reporte general o todos) -->
      <div class="filtro-grupo">
        <label class="filtro-label" for="area-select">🏢 Área/Dirección:</label>
        <select
          id="area-select"
          on:change={(e) =>
            handleFiltroChange("area_id", parseInt(e.target.value) || null)}
          disabled={$cargandoGeneral}
          class="select-filtro"
          class:requerido={$tipoReporteActual === "general"}
        >
          <option value={null}>-- Seleccionar área --</option>
          {#each $filtrosDisponibles.areas as area}
            <option value={area.id}>
              {"  ".repeat(area.nivel)}{area.nombre}
            </option>
          {/each}
        </select>
      </div>
      <!-- Agente (para reporte individual) -->
      {#if $tipoReporteActual === "individual"}
        <div class="filtro-grupo">
          <label class="filtro-label" for="agente-select">👤 Agente:</label>
          <select
            id="agente-select"
            on:change={(e) =>
              handleFiltroChange("agente_id", parseInt(e.target.value) || null)}
            disabled={$cargandoGeneral}
            class="select-filtro requerido"
          >
            <option value={null}>-- Seleccionar agente --</option>
            {#each $agentesFiltrados as agente}
              <option value={agente.id}>
                {agente.nombre_completo} (Leg: {agente.legajo})
              </option>
            {/each}
          </select>
          {#if !$filtrosSeleccionados.area_id}
            <div class="info-filtro">
              <span>ℹ️ Seleccione un área primero para filtrar los agentes</span
              >
            </div>
          {:else if $agentesFiltrados.length === 0}
            <div class="info-filtro">
              <span>⚠️ No hay agentes disponibles en el área seleccionada</span>
            </div>
          {/if}
        </div>
      {/if}
      <!-- Tipo de guardia -->
      <div class="filtro-grupo">
        <label class="filtro-label" for="tipo-guardia-select"
          >⚙️ Tipo de guardia:</label
        >
        <select
          id="tipo-guardia-select"
          bind:value={$filtrosSeleccionados.tipo_guardia}
          on:change={(e) => handleFiltroChange("tipo_guardia", e.target.value)}
          disabled={$cargandoGeneral}
          class="select-filtro"
        >
          <option value="">Todos los tipos</option>
          {#each $filtrosDisponibles.tipos_guardia as tipo}
            <option value={tipo}>{tipo}</option>
          {/each}
        </select>
      </div>
    </div>
    <!-- Opciones adicionales -->
    <div class="opciones-adicionales">
      <label class="checkbox-container">
        <input
          type="checkbox"
          on:change={(e) =>
            handleFiltroChange("incluir_licencias", e.target.checked)}
          disabled={$cargandoGeneral}
        />
        <span class="checkmark"></span>
        Incluir días con licencias
      </label>
      <label class="checkbox-container">
        <input
          type="checkbox"
          on:change={(e) =>
            handleFiltroChange("incluir_feriados", e.target.checked)}
          disabled={$cargandoGeneral}
        />
        <span class="checkmark"></span>
        Incluir feriados
      </label>
    </div>
    <!-- Botón de generación -->
    <div class="accion-generar">
      <button
        class="btn btn-primario btn-generar"
        class:disabled={!$puedeGenerarReporte || !$validacionFechas.valido}
        disabled={$cargandoGeneral ||
          !$puedeGenerarReporte ||
          !$validacionFechas.valido}
        on:click={generarReporte}
      >
        {#if $loading}
          <div class="spinner"></div>
          Generando...
        {:else}
          📊 Generar Reporte
        {/if}
      </button>
    </div>
  </section>
  <!-- Vista previa y exportación -->
  {#if $vistaPreviaVisible && $hayDatos}
    <section class="panel-resultado">
      <div class="resultado-header">
        <h2>📋 Vista Previa del Reporte</h2>
        <div class="botones-exportacion">
          <button
            class="btn btn-exportar btn-pdf"
            disabled={$exportando}
            on:click={exportarPDF}
          >
            {#if $exportando}
              <div class="spinner-pequeño"></div>
            {:else}
              📄
            {/if}
            Exportar PDF
          </button>
          {#if false}
            <button
              class="btn btn-exportar btn-excel"
              disabled={$exportando}
              on:click={exportarExcel}
            >
              {#if $exportando}
                <div class="spinner-pequeño"></div>
              {:else}
                📊
              {/if}
              Exportar Excel
            </button>
          {/if}
        </div>
      </div>
      <div class="vista-previa-container">
        {#if $tipoReporteActual === "individual"}
          <!-- Vista previa reporte individual -->
          <div class="reporte-individual">
            <div class="reporte-header">
              <h3>Planilla Individual de Guardias</h3>
              <div class="datos-agente">
                <p>
                  <strong>Agente:</strong>
                  {$datosReporte.agente.nombre_completo}
                </p>
                <p><strong>Legajo:</strong> {$datosReporte.agente.legajo}</p>
                <p><strong>Área:</strong> {$datosReporte.agente.area_nombre}</p>
                <p>
                  <strong>Período:</strong>
                  {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo
                    .fecha_hasta}
                </p>
              </div>
            </div>
          </div>
        {:else if $tipoReporteActual === "horas_trabajadas"}
          <!-- Vista previa reporte de horas trabajadas -->
          <div class="reporte-horas-trabajadas">
            <div class="reporte-header">
              <h3>⏰ Reporte de Guardias y Compensaciones</h3>
              <div class="datos-area">
                <p>
                  <strong>Área:</strong>
                  {$datosReporte.area_nombre || "Todas las áreas"}
                </p>
                <p>
                  <strong>Período:</strong>
                  {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo
                    .fecha_hasta}
                </p>
                <p>
                  <strong>Generado:</strong>
                  {new Date().toLocaleDateString()}
                </p>
              </div>
            </div>
            <div class="tabla-container">
              <table class="tabla-reporte tabla-horas-trabajadas">
                <thead>
                  <tr>
                    <th>Agente</th>
                    <th>Legajo</th>
                    <th>Horas Programadas</th>
                    <th>Horas Efectivas</th>
                    <th>Guardias Fines/Feriados</th>
                    <th>Total Horas</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="ejemplo-fila">
                    <td>Tayra Aguila</td>
                    <td>001</td>
                    <td class="horas-programadas">160h</td>
                    <td class="horas-efectivas">176h</td>
                    <td class="guardias-feriados">12</td>
                    <td class="total-horas"><strong>176h</strong></td>
                  </tr>
                  <tr class="ejemplo-fila">
                    <td>Micaela Alvarado</td>
                    <td>002</td>
                    <td class="horas-programadas">144h</td>
                    <td class="horas-efectivas">168h</td>
                    <td class="guardias-feriados">8</td>
                    <td class="total-horas"><strong>168h</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="preview-note">
              <p>
                📊 Este reporte discrimina las horas según cronograma (diurna
                08:00-16:00, nocturna 22:00-06:00, feriados según calendario)
              </p>
            </div>
          </div>
        {:else if $tipoReporteActual === "parte_diario"}
          <!-- Vista previa parte diario -->
          <div class="reporte-parte-diario">
            <div class="reporte-header">
              <h3>📅 Parte Diario/Mensual Consolidado</h3>
              <div class="datos-area">
                <p>
                  <strong>Área:</strong>
                  {$datosReporte.area_nombre || "Todas las áreas"}
                </p>
                <p>
                  <strong>Período:</strong>
                  {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo
                    .fecha_hasta}
                </p>
                <p>
                  <strong>Generado:</strong>
                  {new Date().toLocaleDateString()}
                </p>
              </div>
            </div>
            <div class="tabla-container">
              <table class="tabla-reporte tabla-parte-diario">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Agente</th>
                    <th>Ingreso</th>
                    <th>Egreso</th>
                    <th>Horas Trabajadas</th>
                    <th>Novedades</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>22/11/2025</td>
                    <td>Tayra Aguila</td>
                    <td class="hora-ingreso">08:00</td>
                    <td class="hora-egreso">16:00</td>
                    <td class="horas-trabajadas">8h</td>
                    <td><span class="novedad-normal">Jornada habitual</span></td
                    >
                  </tr>
                  <tr>
                    <td>22/11/2025</td>
                    <td>Cristian Garcia</td>
                    <td class="hora-ingreso tarde">08:15</td>
                    <td class="hora-egreso">16:00</td>
                    <td class="horas-trabajadas">7h 45m</td>
                    <td
                      ><span class="novedad-advertencia">Llegada tarde</span
                      ></td
                    >
                  </tr>
                  <tr>
                    <td>22/11/2025</td>
                    <td>Teresa Criniti</td>
                    <td class="hora-ingreso">08:00</td>
                    <td class="hora-egreso">14:30</td>
                    <td class="horas-trabajadas">6h 30m</td>
                    <td
                      ><span class="novedad-comision">Comisión oficial</span
                      ></td
                    >
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="preview-note">
              <p>
                📋 Detalla ingresos, egresos y novedades registradas por el
                sistema de asistencias. Incluye alertas automáticas.
              </p>
            </div>
          </div>
        {:else if $tipoReporteActual === "resumen_licencias"}
          <!-- Vista previa resumen licencias -->
          <div class="reporte-resumen-licencias">
            <div class="reporte-header">
              <h3>🏥 Resumen de Licencias</h3>
              <div class="datos-area">
                <p><strong>Período:</strong> Año {new Date().getFullYear()}</p>
                <p>
                  <strong>Área:</strong>
                  {$datosReporte.area_nombre || "Todas las áreas"}
                </p>
                <p>
                  <strong>Generado:</strong>
                  {new Date().toLocaleDateString()}
                </p>
              </div>
            </div>
            <div class="tabla-container">
              <table class="tabla-reporte tabla-licencias">
                <thead>
                  <tr>
                    <th>Agente</th>
                    <th>Art. 32.1 (Anual)</th>
                    <th>Art. 32.2 (Enfermedad)</th>
                    <th>Art. 33 (Especiales)</th>
                    <th>Días Utilizados</th>
                    <th>Días Disponibles</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Tayra Aguila</td>
                    <td class="licencia-anual">15/21</td>
                    <td class="licencia-enfermedad">3/30</td>
                    <td class="licencia-especial">2/10</td>
                    <td class="dias-utilizados">20</td>
                    <td class="dias-disponibles">41</td>
                  </tr>
                  <tr>
                    <td>Micaela Alvarado</td>
                    <td class="licencia-anual">8/21</td>
                    <td class="licencia-enfermedad">0/30</td>
                    <td class="licencia-especial">1/10</td>
                    <td class="dias-utilizados">9</td>
                    <td class="dias-disponibles">52</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="preview-note">
              <p>
                🏥 Control de consumo de licencias según articulado del Convenio
                Colectivo. Monitorea límites anuales.
              </p>
            </div>
          </div>
        {:else if $tipoReporteActual === "calculo_plus"}
          <!-- Vista previa cálculo plus -->
          <div class="reporte-calculo-plus">
            <div class="reporte-header">
              <h3>💲 Cálculo Plus por Guardias</h3>
              <div class="datos-area">
                <p><strong>Período:</strong> Octubre 2025</p>
                <p><strong>Área:</strong> Todas las áreas</p>
                <p>
                  <strong>Generado:</strong>
                  {new Date().toLocaleDateString()}
                </p>
              </div>
              <div class="reglas-plus">
                <h4>Reglas de Plus Aplicadas:</h4>
                <ul>
                  <li>
                    <strong>40% Plus:</strong> Área operativa + guardia | Otras áreas
                    + 32+ horas
                  </li>
                  <li><strong>20% Plus:</strong> Resto con guardias</li>
                </ul>
              </div>
            </div>
            <div class="tabla-container">
              <table class="tabla-reporte tabla-plus">
                <thead>
                  <tr>
                    <th>Agente</th>
                    <th>Área</th>
                    <th>Horas de Guardia</th>
                    <th>Tipo Plus</th>
                    <th>Motivo</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="plus-40">
                    <td>Carlos Rodriguez</td>
                    <td class="area-operativa"
                      >Secretaría de Protección Civil</td
                    >
                    <td class="horas-guardia">48h</td>
                    <td class="plus-valor"><strong>40%</strong></td>
                    <td class="motivo-plus">Área operativa con guardias</td>
                  </tr>
                  <tr class="plus-40">
                    <td>Jorge Gutierrez</td>
                    <td class="area-administrativa">Depto. Administrativo</td>
                    <td class="horas-guardia">36h</td>
                    <td class="plus-valor"><strong>40%</strong></td>
                    <td class="motivo-plus">Otras áreas con 36h (≥32h)</td>
                  </tr>
                  <tr class="plus-20">
                    <td>Ana Torres</td>
                    <td class="area-administrativa"
                      >División de Planificación</td
                    >
                    <td class="horas-guardia">24h</td>
                    <td class="plus-valor">20%</td>
                    <td class="motivo-plus">Guardias con menos de 32h</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="totales-plus">
              <div class="total-item">
                <span class="total-label">Agentes con 40% Plus:</span>
                <span class="total-valor plus-40-count">2</span>
              </div>
              <div class="total-item">
                <span class="total-label">Agentes con 20% Plus:</span>
                <span class="total-valor plus-20-count">1</span>
              </div>
              <div class="total-item">
                <span class="total-label">Total agentes con Plus:</span>
                <span class="total-valor"><strong>3</strong></span>
              </div>
            </div>
            <div class="preview-note">
              <p>
                💰 Cálculo automático según CCT. Áreas operativas tienen plus
                garantizado, otras dependen de horas acumuladas.
              </p>
            </div>
          </div>
        {:else if $tipoReporteActual === "incumplimiento_normativo"}
          <!-- Vista previa incumplimiento normativo -->
          <div class="reporte-incumplimiento">
            <div class="reporte-header">
              <h3>⚠️ Reporte de Incumplimiento Normativo</h3>
              <div class="datos-area">
                <p>
                  <strong>Período:</strong>
                  {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo
                    .fecha_hasta}
                </p>
                <p>
                  <strong>Área:</strong>
                  {$datosReporte.area_nombre || "Todas las áreas"}
                </p>
                <p>
                  <strong>Generado:</strong>
                  {new Date().toLocaleDateString()}
                </p>
              </div>
            </div>
            <div class="alertas-normativas">
              <div class="alerta-item alerta-critica">
                <div class="alerta-icono">🚨</div>
                <div class="alerta-contenido">
                  <h4>Exceso de Horas Semanales</h4>
                  <p><strong>Agente:</strong> Tayra Aguila</p>
                  <p><strong>Semana:</strong> 18-24/11/2025</p>
                  <p>
                    <strong>Problema:</strong> 52 horas trabajadas (máximo: 48h según
                    CC)
                  </p>
                </div>
              </div>
              <div class="alerta-item alerta-advertencia">
                <div class="alerta-icono">⚠️</div>
                <div class="alerta-contenido">
                  <h4>Descanso Insuficiente</h4>
                  <p><strong>Agente:</strong> Carlos Rodriguez</p>
                  <p><strong>Fecha:</strong> 21-22/11/2025</p>
                  <p>
                    <strong>Problema:</strong> 8 horas de descanso (mínimo: 12h entre
                    guardias)
                  </p>
                </div>
              </div>
              <div class="alerta-item alerta-info">
                <div class="alerta-icono">ℹ️</div>
                <div class="alerta-contenido">
                  <h4>Próximo a Límite</h4>
                  <p><strong>Agente:</strong> Sandra Lopez</p>
                  <p><strong>Semana:</strong> 18-24/11/2025</p>
                  <p>
                    <strong>Problema:</strong> 46 horas trabajadas (límite: 48h)
                  </p>
                </div>
              </div>
            </div>
            <div class="preview-note">
              <p>
                ⚖️ Monitorea automáticamente el cumplimiento de normas del
                Convenio Colectivo. Genera alertas preventivas.
              </p>
            </div>
          </div>
        {:else}
          <!-- Vista previa simplificada reporte general -->
          <div class="reporte-general simple">
            <div class="summary-grid">
              <div class="summary-card">
                <p class="summary-label">Área/Dirección</p>
                <p class="summary-value">
                  {$datosReporte.area_nombre || "Según permisos"}
                </p>
              </div>
              <div class="summary-card">
                <p class="summary-label">Período</p>
                <p class="summary-value">
                  {$datosReporte.periodo?.fecha_desde} - {$datosReporte.periodo
                    ?.fecha_hasta}
                </p>
              </div>
              <div class="summary-card">
                <p class="summary-label">Agentes</p>
                <p class="summary-value">
                  {$datosReporte.totales?.total_agentes ||
                    $datosReporte.agentes?.length ||
                    0}
                </p>
              </div>
              <div class="summary-card">
                <p class="summary-label">Horas totales</p>
                <p class="summary-value">
                  {$datosReporte.totales?.total_horas_direccion ||
                    $datosReporte.totales?.horas ||
                    "-"}
                </p>
              </div>
            </div>
            <div class="list-preview">
              <p class="summary-label">Agentes (vista breve)</p>
              <ul>
                {#each ($datosReporte.agentes || []).slice(0, 8) as agente}
                  <li class="list-item">
                    <div>
                      <strong>{agente.nombre_completo}</strong>
                      <span class="muted">· Legajo {agente.legajo}</span>
                    </div>
                    <div class="muted">
                      {agente.area || "Sin área"} · {agente.total_horas || 0} h
                    </div>
                  </li>
                {/each}
                {#if ($datosReporte.agentes || []).length > 8}
                  <li class="muted">
                    ... y {($datosReporte.agentes || []).length - 8} más
                  </li>
                {/if}
              </ul>
            </div>
            <div class="preview-note">
              <p>
                🔎 Vista reducida para validación rápida. Usa Exportar para ver
                la grilla completa.
              </p>
            </div>
          </div>
        {/if}
      </div>
    </section>
  {/if}
  <!-- Estado de carga inicial -->
  {#if $loadingFiltros}
    <div class="loading-inicial">
      <div class="spinner-grande"></div>
      <p>Cargando opciones de filtros...</p>
    </div>
  {/if}
</div>

<style>
  .container-reportes {
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }
  .header-reportes-messages {
    margin-bottom: 1rem;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .header-title {
    position: relative;
    background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
    color: white;
    padding: 30px 40px;
    margin: 0;
    width: 100%;
    border-radius: 28px;
    overflow: hidden;
    text-align: center;
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.1) inset,
      0 20px 60px rgba(30, 64, 175, 0.4);
  }

  .header-title::before {
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

  .header-title h1 {
    margin: 10px;
    font-weight: 800;
    font-size: 18px;
    letter-spacing: 0.2px;
    position: relative;
    padding-bottom: 12px;
    overflow: hidden;
    display: block;
    max-width: 100%;
    word-wrap: break-word;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  @media (min-width: 480px) {
    .header-title h1 {
      font-size: 22px;
    }
  }

  @media (min-width: 640px) {
    .header-title h1 {
      font-size: 26px;
      display: inline-block;
    }
  }

  @media (min-width: 768px) {
    .header-title h1 {
      font-size: 30px;
    }
  }

  @media (max-width: 768px) {
    .header-title {
      padding: 15px 10px;
      border-radius: 14px;
    }
  }

  .header-title h1::after {
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

  @keyframes moveLines {
    0% {
      background-position: 0 0;
    }
    100% {
      background-position: 50px 50px;
    }
  }

  @media (min-width: 768px) {
    .container-reportes {
      padding: 24px;
    }
  }
  @media (min-width: 1280px) {
    .container-reportes {
      width: min(1800px, 96vw);
    }
  }
  @media (min-width: 1600px) {
    .container-reportes {
      width: min(2000px, 92vw);
    }
  }
  @media (max-width: 768px) {
    .botones-exportacion {
      flex-direction: column;
      width: 100%;
    }
    .botones-exportacion .btn {
      width: 100%;
      justify-content: center;
    }
    .rango-fechas {
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
    }
    .rango-separador {
      text-align: center;
    }
    .input-fecha {
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
    }
    .filtros-grid {
      grid-template-columns: 1fr;
    }
    .filtro-grupo {
      width: 100%;
      max-width: 100%;
      overflow: hidden;
    }
    .select-filtro {
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
    }
    .header-title {
      padding: 20px 20px;
      border-radius: 16px;
    }
    .panel-filtros {
      padding: 1rem;
      border-radius: 12px;
      margin-left: 0;
      margin-right: 0;
    }
  }
  .mensaje {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    font-weight: 500;
  }
  .mensaje-exito {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  .mensaje-error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  .selector-tipo {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    margin-bottom: 2rem;
  }

  .input-fecha,
  .select-filtro {
    width: 100%;
    min-width: 0;
  }
  .selector-tipo-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  .selector-opcion {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.5rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .selector-opcion:hover {
    border-color: #007bff;
    background: #f8f9ff;
  }
  .selector-opcion input[type="radio"] {
    margin: 0;
    margin-top: 2px;
    transform: scale(1.2);
  }
  .selector-tipo-container:nth-of-type(n + 2) {
    display: none;
  }
  .opcion-contenido {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  .opcion-contenido strong {
    color: #2c3e50;
    font-size: 1.1rem;
  }
  .opcion-contenido span {
    color: #6c757d;
    font-size: 0.9rem;
  }
  .panel-filtros {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    margin-bottom: 2rem;
  }
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e9ecef;
  }
  .panel-header h2 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5rem;
  }
  .filtros-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  .filtro-grupo {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .filtro-label {
    font-weight: 600;
    color: #495057;
    font-size: 0.95rem;
  }
  .rango-fechas {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: nowrap;
  }
  .input-fecha {
    flex: 1;
    min-width: 130px;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }
  .input-fecha:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
  .rango-separador {
    color: #6c757d;
    font-weight: 500;
    white-space: nowrap;
  }
  .botones-rapidos {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
  }
  .btn-rapido {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn-rapido:hover:not(:disabled) {
    background: #e9ecef;
    border-color: #adb5bd;
  }
  .select-filtro {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-size: 1rem;
    background: white;
    transition: border-color 0.2s;
  }
  .select-filtro:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
  .select-filtro.requerido {
    border-color: #dee2e6;
    background: white;
  }
  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }
  .summary-card {
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 12px;
    background: #f8fafc;
  }
  .summary-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6c757d;
    margin: 0 0 4px 0;
  }
  .summary-value {
    font-weight: 700;
    color: #2c3e50;
    margin: 0;
  }
  .list-preview ul {
    list-style: none;
    padding: 0;
    margin: 8px 0 0 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .list-item {
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 10px 12px;
    background: #fff;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .opciones-adicionales {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }
  .checkbox-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.95rem;
    color: #495057;
  }
  .checkbox-container input[type="checkbox"] {
    margin: 0;
    transform: scale(1.1);
  }
  .error-validacion {
    color: #dc3545;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.25rem;
  }
  .info-filtro {
    background: #d1ecf1;
    color: #0c5460;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    border: 1px solid #bee5eb;
  }
  .accion-generar {
    display: flex;
    justify-content: center;
    padding-top: 1rem;
    border-top: 1px solid #e9ecef;
  }
  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
  }
  .btn-primario {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  .btn-primario:hover:not(.disabled) {
    background: linear-gradient(135deg, #5468d4 0%, #653a8e 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
  .btn-secundario {
    background: #6c757d;
    color: white;
  }
  .btn-secundario:hover:not(:disabled) {
    background: #545b62;
  }
  .btn-pequeño {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  .btn-generar {
    padding: 1rem 2rem;
    font-size: 1.1rem;
  }
  .btn-exportar {
    background: #28a745;
    color: white;
    padding: 0.6rem 1.2rem;
  }
  .btn-exportar:hover:not(:disabled) {
    background: #1e7e34;
  }
  .btn-pdf {
    background: #dc3545;
  }
  .btn-pdf:hover:not(:disabled) {
    background: #c82333;
  }
  .btn-excel {
    background: #198754;
  }
  .btn-excel:hover:not(:disabled) {
    background: #146c43;
  }
  .btn.disabled,
  .btn:disabled {
    background: #6c757d !important;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none !important;
    box-shadow: none !important;
  }
  .panel-resultado {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    margin-bottom: 2rem;
  }
  .resultado-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e9ecef;
  }
  .resultado-header h2 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5rem;
  }
  .botones-exportacion {
    display: flex;
    gap: 1rem;
  }
  .vista-previa-container {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }
  .reporte-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #dee2e6;
  }
  .reporte-header h3 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 1.3rem;
  }
  .datos-agente,
  .datos-area {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 0.5rem;
  }
  .datos-agente p,
  .datos-area p {
    margin: 0;
    font-size: 0.95rem;
    color: #495057;
  }
  .tabla-container {
    overflow-x: auto;
    margin-bottom: 1.5rem;
    -webkit-overflow-scrolling: touch;
  }
  .tabla-reporte {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 6px;
    overflow: hidden;
    min-width: 720px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  .tabla-reporte th:first-child,
  .tabla-reporte td:first-child {
    position: sticky;
    left: 0;
    background: white;
    z-index: 2;
  }
  .tabla-reporte th:first-child {
    z-index: 3;
  }
  .tabla-reporte th,
  .tabla-reporte td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
  }
  .tabla-reporte th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
    font-size: 0.9rem;
  }
  .tabla-reporte td {
    font-size: 0.9rem;
    color: #6c757d;
  }

  .total-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
  }
  .total-label {
    font-weight: 500;
    color: #495057;
  }
  .total-valor {
    font-weight: 700;
    color: #007bff;
    font-size: 1.1rem;
  }
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  .spinner-pequeño {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  .spinner-grande {
    width: 40px;
    height: 40px;
    border: 3px solid #e9ecef;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  .loading-inicial {
    text-align: center;
    padding: 4rem 2rem;
    color: #6c757d;
  }
  .horas-efectivas {
    font-size: 0.8rem;
    color: #28a745;
    font-style: italic;
  }
  .horas-guardia {
    color: #27ae60;
    font-weight: 700;
    font-size: 0.8rem;
  }

  @media (max-width: 768px) {
    .rango-fechas {
      gap: 8px;
    }
    .container-reportes {
      padding: 0.75rem;
    }

    .selector-tipo,
    .panel-filtros,
    .panel-resultado {
      padding: 1.5rem 1rem;
      border-radius: 16px;
    }
  }
  @media (max-width: 768px) {
    .container-reportes {
      padding: 1rem;
    }
    .selector-tipo-container {
      grid-template-columns: 1fr;
    }
    .alertas-normativas {
      gap: 0.75rem;
    }
    .alerta-item {
      flex-direction: column;
      gap: 0.5rem;
      text-align: center;
    }
    .preview-note {
      margin-top: 0.75rem;
      padding: 0.75rem;
    }
    .filtros-grid {
      grid-template-columns: 1fr;
    }
    .rango-fechas {
      flex-direction: column;
      align-items: stretch;
    }
    .input-fecha:first-of-type {
      order: 1;
    }
    .rango-separador {
      text-align: center;
      order: 2;
    }
    .input-fecha:last-of-type {
      order: 3;
    }
    .resultado-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }
    .botones-exportacion {
      justify-content: center;
    }
    .datos-agente,
    .datos-area {
      grid-template-columns: 1fr;
    }
    .opciones-adicionales {
      flex-direction: column;
      gap: 1rem;
    }
  }
  .horas-efectivas {
    color: #28a745;
    font-weight: 600;
  }

  .tabla-horas-trabajadas .horas-programadas {
    color: #007bff;
    font-weight: 600;
  }
  .tabla-horas-trabajadas .horas-efectivas {
    color: #28a745;
    font-weight: 600;
  }
  .tabla-horas-trabajadas .guardias-feriados {
    color: #fd7e14;
    font-weight: 600;
    text-align: center;
  }
  .reglas-plus {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 6px;
    margin-top: 1rem;
  }
  .reglas-plus h4 {
    margin: 0 0 0.5rem 0;
    color: #495057;
  }
  .reglas-plus ul {
    margin: 0;
    padding-left: 1.5rem;
  }
  .tabla-plus .plus-40 {
    background-color: rgba(40, 167, 69, 0.1);
  }
  .tabla-plus .plus-20 {
    background-color: rgba(255, 193, 7, 0.1);
  }
  .tabla-plus .plus-valor {
    font-weight: 700;
    text-align: center;
  }
  .tabla-plus .area-operativa {
    color: #28a745;
    font-weight: 600;
  }
  .tabla-plus .area-administrativa {
    color: #6c757d;
  }
  .tabla-plus .horas-guardia {
    font-weight: 600;
    text-align: center;
    color: #007bff;
  }
  .totales-plus {
    display: flex;
    justify-content: space-around;
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 6px;
    margin-top: 1rem;
  }
  .totales-plus .total-item {
    text-align: center;
  }
  .totales-plus .plus-40-count {
    color: #28a745;
    font-weight: 700;
  }
  .totales-plus .plus-20-count {
    color: #ffc107;
    font-weight: 700;
  }
  .tabla-horas-trabajadas .total-horas {
    background: linear-gradient(135deg, #e8f5e8 0%, #d5f4e6 100%);
    text-align: center;
    color: #155724;
  }
  .tabla-parte-diario .hora-ingreso,
  .tabla-parte-diario .hora-egreso {
    font-family: monospace;
    font-weight: 600;
    text-align: center;
  }
  .tabla-parte-diario .hora-ingreso.tarde {
    color: #e74c3c;
    background: #fadbd8;
  }
  .tabla-parte-diario .horas-trabajadas {
    text-align: center;
    font-weight: 600;
    color: #2c3e50;
  }
  .novedad-normal {
    background: #d4edda;
    color: #155724;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  .novedad-advertencia {
    background: #fff3cd;
    color: #856404;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  .novedad-comision {
    background: #d1ecf1;
    color: #0c5460;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  .tabla-licencias .licencia-anual,
  .tabla-licencias .licencia-enfermedad,
  .tabla-licencias .licencia-especial {
    text-align: center;
    font-weight: 600;
  }
  .tabla-licencias .licencia-anual {
    color: #007bff;
  }
  .tabla-licencias .licencia-enfermedad {
    color: #e74c3c;
  }
  .tabla-licencias .licencia-especial {
    color: #f39c12;
  }
  .tabla-licencias .dias-utilizados {
    text-align: center;
    font-weight: 600;
    color: #6c757d;
  }
  .tabla-licencias .dias-disponibles {
    text-align: center;
    font-weight: 700;
    color: #28a745;
    background: #d4edda;
  }
  .tabla-plus .area-operativa {
    background: #fff3cd;
    color: #856404;
    font-weight: 600;
  }
  .tabla-plus .area-administrativa {
    background: #d1ecf1;
    color: #0c5460;
    font-weight: 600;
  }

  .tabla-plus .plus-20 {
    text-align: center;
    color: #f39c12;
    font-weight: 600;
    background: #fef9e7;
  }
  .tabla-plus .plus-40 {
    text-align: center;
    color: #e74c3c;
    font-weight: 600;
    background: #fdf2f2;
  }
  .alertas-normativas {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  .alerta-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid;
  }
  .alerta-critica {
    background: linear-gradient(135deg, #fdf2f2 0%, #fadbd8 100%);
    border-left-color: #e74c3c;
  }
  .alerta-advertencia {
    background: linear-gradient(135deg, #fef9e7 0%, #fff3cd 100%);
    border-left-color: #f39c12;
  }
  .alerta-info {
    background: linear-gradient(135deg, #e3f2fd 0%, #d1ecf1 100%);
    border-left-color: #17a2b8;
  }
  .alerta-icono {
    font-size: 1.5rem;
    line-height: 1;
    margin-top: 0.25rem;
  }
  .alerta-contenido h4 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 1rem;
    font-weight: 700;
  }
  .alerta-contenido p {
    margin: 0.25rem 0;
    font-size: 0.9rem;
    color: #495057;
  }
  .preview-note {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    border-left: 4px solid #007bff;
  }
  .preview-note p {
    margin: 0;
    color: #495057;
    font-size: 0.9rem;
    line-height: 1.4;
    font-style: italic;
  }
  .ejemplo-fila {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    opacity: 0.8;
  }
  .ejemplo-fila:hover {
    opacity: 1;
    background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%);
  }
  .selector-tipo-container:nth-of-type(n + 2) {
    display: none;
  }
  .selector-opcion input[value="horas_trabajadas"],
  .selector-opcion input[value="parte_diario"],
  .selector-opcion input[value="resumen_licencias"],
  .selector-opcion input[value="calculo_plus"],
  .selector-opcion input[value="incumplimiento_normativo"] {
    display: none;
  }
  .selector-opcion input[value="horas_trabajadas"] + .opcion-contenido,
  .selector-opcion input[value="parte_diario"] + .opcion-contenido,
  .selector-opcion input[value="resumen_licencias"] + .opcion-contenido,
  .selector-opcion input[value="calculo_plus"] + .opcion-contenido,
  .selector-opcion input[value="incumplimiento_normativo"] + .opcion-contenido {
    display: none;
  }
</style>
