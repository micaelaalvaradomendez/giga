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
		agentesFiltrados
	} = reporteController;
	
	// Inicialización
	onMount(async () => {
		console.log('🔄 ONMOUNT EJECUTÁNDOSE...');
		await reporteController.inicializar();
		console.log('✅ INICIALIZACIÓN COMPLETADA');
	});
	
	// Funciones del componente
	function handleTipoReporteChange(event) {
		reporteController.cambiarTipoReporte(event.target.value);
	}
	
	function handleFiltroChange(campo, valor) {
		reporteController.actualizarFiltro(campo, valor);
		
		// Si cambió el área, resetear la selección de agente
		if (campo === 'area_id') {
			reporteController.actualizarFiltro('agente_id', null);
		}
	}
	
	async function generarReporte() {
		const tipo = $tipoReporteActual;
		switch (tipo) {
			case 'individual':
				await reporteController.generarReporteIndividual();
				break;
			case 'general':
				await reporteController.generarReporteGeneral();
				break;
			case 'horas_trabajadas':
				await reporteController.generarReporteHorasTrabajadas();
				break;
			case 'parte_diario':
				await reporteController.generarReporteParteDiario();
				break;
			case 'resumen_licencias':
				await reporteController.generarReporteResumenLicencias();
				break;
			case 'calculo_plus':
				await reporteController.generarReporteCalculoPlus();
				break;
			case 'incumplimiento_normativo':
				await reporteController.generarReporteIncumplimientoNormativo();
				break;
			default:
				console.error('Tipo de reporte no soportado:', tipo);
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
	$: agenteDiasMap = $datosReporte?.agentes?.reduce((map, agente) => {
		const diasByFecha = new Map();
		agente.dias?.forEach(d => diasByFecha.set(d.fecha, d));
		map.set(agente, diasByFecha);
		return map;
	}, new Map()) || new Map();

	// Precompute totals per day to avoid reduce+find in template
	$: totalesPorDia = $datosReporte?.dias_columnas?.reduce((map, dia) => {
		const total = $datosReporte.agentes?.reduce((sum, agente) => {
			const diaData = agenteDiasMap.get(agente)?.get(dia.fecha);
			return sum + (diaData?.horas || 0);
		}, 0) || 0;
		map.set(dia.fecha, total);
		return map;
	}, new Map()) || new Map();

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
	<header class="header-reportes">
		<div class="titulo-section">
			<h1>📊 Gestión de Reportes</h1>
			<p>Genere y exporte reportes de guardias individuales y generales</p>
			{#if $loadingFiltros}
				<p class="estado-carga">🔄 Cargando opciones disponibles...</p>
			{:else if $filtrosDisponibles.agentes?.length === 0}
				<p class="estado-advertencia">⚠️ Sistema en modo fallback - Los reportes usarán datos simulados</p>
			{:else}
				<p class="estado-ok">✅ Sistema conectado - Reportes con datos reales disponibles</p>
			{/if}
		</div>
		
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
						<span>Horas de guardia programadas vs efectivas (fines de semana/feriados únicamente)</span>
					</div>
				</label>
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
						<span>Marcas de ingreso/egreso y novedades (llegadas tarde, retiros, comisiones)</span>
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
						<span>Área operativa + guardia = 40% | Otras áreas + 32h = 40% | Resto = 20%</span>
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
						<span>Alertas de violaciones a reglas de horas semanales y descansos</span>
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
						on:change={(e) => handleFiltroChange('fecha_desde', e.target.value)}
						disabled={$cargandoGeneral}
						class="input-fecha"
						aria-label="Fecha desde"
					/>
					<span class="rango-separador">hasta</span>
					<input 
						type="date" 
						bind:value={$filtrosSeleccionados.fecha_hasta}
						on:change={(e) => handleFiltroChange('fecha_hasta', e.target.value)}
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
					bind:value={$filtrosSeleccionados.area_id}
					on:change={(e) => handleFiltroChange('area_id', parseInt(e.target.value) || null)}
					disabled={$cargandoGeneral}
					class="select-filtro"
					class:requerido={$tipoReporteActual === 'general'}
				>
					<option value={null}>-- Seleccionar área --</option>
					{#each $filtrosDisponibles.areas as area}
						<option value={area.id}>
							{'  '.repeat(area.nivel)}{area.nombre}
						</option>
					{/each}
				</select>
			</div>

			<!-- Agente (para reporte individual) -->
			{#if $tipoReporteActual === 'individual'}
				<div class="filtro-grupo">
					<label class="filtro-label" for="agente-select">👤 Agente:</label>
					<select 
						id="agente-select"
						bind:value={$filtrosSeleccionados.agente_id}
						on:change={(e) => handleFiltroChange('agente_id', parseInt(e.target.value) || null)}
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
							<span>ℹ️ Seleccione un área primero para filtrar los agentes</span>
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
				<label class="filtro-label" for="tipo-guardia-select">⚙️ Tipo de guardia:</label>
				<select 
					id="tipo-guardia-select"
					bind:value={$filtrosSeleccionados.tipo_guardia}
					on:change={(e) => handleFiltroChange('tipo_guardia', e.target.value)}
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
					bind:checked={$filtrosSeleccionados.incluir_licencias}
					on:change={(e) => handleFiltroChange('incluir_licencias', e.target.checked)}
					disabled={$cargandoGeneral}
				/>
				<span class="checkmark"></span>
				Incluir días con licencias
			</label>
			
			<label class="checkbox-container">
				<input 
					type="checkbox" 
					bind:checked={$filtrosSeleccionados.incluir_feriados}
					on:change={(e) => handleFiltroChange('incluir_feriados', e.target.checked)}
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
				disabled={$cargandoGeneral || !$puedeGenerarReporte || !$validacionFechas.valido}
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
				</div>
			</div>

			<div class="vista-previa-container">
				{#if $tipoReporteActual === 'individual'}
					<!-- Vista previa reporte individual -->
					<div class="reporte-individual">
						<div class="reporte-header">
							<h3>Planilla Individual de Guardias</h3>
							<div class="datos-agente">
								<p><strong>Agente:</strong> {$datosReporte.agente.nombre_completo}</p>
								<p><strong>Legajo:</strong> {$datosReporte.agente.legajo}</p>
								<p><strong>Área:</strong> {$datosReporte.agente.area_nombre}</p>
								<p><strong>Período:</strong> {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo.fecha_hasta}</p>
							</div>
						</div>
					</div>
				{:else if $tipoReporteActual === 'horas_trabajadas'}
					<!-- Vista previa reporte de horas trabajadas -->
					<div class="reporte-horas-trabajadas">
						<div class="reporte-header">
							<h3>⏰ Reporte de Guardias y Compensaciones</h3>
							<div class="datos-area">
								<p><strong>Área:</strong> {$datosReporte.area_nombre || 'Todas las áreas'}</p>
								<p><strong>Período:</strong> {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo.fecha_hasta}</p>
								<p><strong>Generado:</strong> {new Date().toLocaleDateString()}</p>
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
							<p>📊 Este reporte discrimina las horas según cronograma (diurna 08:00-16:00, nocturna 22:00-06:00, feriados según calendario)</p>
						</div>
					</div>
				{:else if $tipoReporteActual === 'parte_diario'}
					<!-- Vista previa parte diario -->
					<div class="reporte-parte-diario">
						<div class="reporte-header">
							<h3>📅 Parte Diario/Mensual Consolidado</h3>
							<div class="datos-area">
								<p><strong>Área:</strong> {$datosReporte.area_nombre || 'Todas las áreas'}</p>
								<p><strong>Período:</strong> {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo.fecha_hasta}</p>
								<p><strong>Generado:</strong> {new Date().toLocaleDateString()}</p>
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
										<td><span class="novedad-normal">Jornada habitual</span></td>
									</tr>
									<tr>
										<td>22/11/2025</td>
										<td>Cristian Garcia</td>
										<td class="hora-ingreso tarde">08:15</td>
										<td class="hora-egreso">16:00</td>
										<td class="horas-trabajadas">7h 45m</td>
										<td><span class="novedad-advertencia">Llegada tarde</span></td>
									</tr>
									<tr>
										<td>22/11/2025</td>
										<td>Teresa Criniti</td>
										<td class="hora-ingreso">08:00</td>
										<td class="hora-egreso">14:30</td>
										<td class="horas-trabajadas">6h 30m</td>
										<td><span class="novedad-comision">Comisión oficial</span></td>
									</tr>
								</tbody>
							</table>
						</div>
						
						<div class="preview-note">
							<p>📋 Detalla ingresos, egresos y novedades registradas por el sistema de asistencias. Incluye alertas automáticas.</p>
						</div>
					</div>
				{:else if $tipoReporteActual === 'resumen_licencias'}
					<!-- Vista previa resumen licencias -->
					<div class="reporte-resumen-licencias">
						<div class="reporte-header">
							<h3>🏥 Resumen de Licencias</h3>
							<div class="datos-area">
								<p><strong>Período:</strong> Año {new Date().getFullYear()}</p>
								<p><strong>Área:</strong> {$datosReporte.area_nombre || 'Todas las áreas'}</p>
								<p><strong>Generado:</strong> {new Date().toLocaleDateString()}</p>
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
							<p>🏥 Control de consumo de licencias según articulado del Convenio Colectivo. Monitorea límites anuales.</p>
						</div>
					</div>
				{:else if $tipoReporteActual === 'calculo_plus'}
					<!-- Vista previa cálculo plus -->
					<div class="reporte-calculo-plus">
						<div class="reporte-header">
							<h3>💲 Cálculo Plus por Guardias</h3>
							<div class="datos-area">
								<p><strong>Período:</strong> Octubre 2025</p>
								<p><strong>Área:</strong> Todas las áreas</p>
								<p><strong>Generado:</strong> {new Date().toLocaleDateString()}</p>
							</div>
							<div class="reglas-plus">
								<h4>Reglas de Plus Aplicadas:</h4>
								<ul>
									<li><strong>40% Plus:</strong> Área operativa + guardia | Otras áreas + 32+ horas</li>
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
										<td class="area-operativa">Secretaría de Protección Civil</td>
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
										<td class="area-administrativa">División de Planificación</td>
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
							<p>💰 Cálculo automático según CCT. Áreas operativas tienen plus garantizado, otras dependen de horas acumuladas.</p>
						</div>
					</div>
				{:else if $tipoReporteActual === 'incumplimiento_normativo'}
					<!-- Vista previa incumplimiento normativo -->
					<div class="reporte-incumplimiento">
						<div class="reporte-header">
							<h3>⚠️ Reporte de Incumplimiento Normativo</h3>
							<div class="datos-area">
								<p><strong>Período:</strong> {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo.fecha_hasta}</p>
								<p><strong>Área:</strong> {$datosReporte.area_nombre || 'Todas las áreas'}</p>
								<p><strong>Generado:</strong> {new Date().toLocaleDateString()}</p>
							</div>
						</div>
						
						<div class="alertas-normativas">
							<div class="alerta-item alerta-critica">
								<div class="alerta-icono">🚨</div>
								<div class="alerta-contenido">
									<h4>Exceso de Horas Semanales</h4>
									<p><strong>Agente:</strong> Tayra Aguila</p>
									<p><strong>Semana:</strong> 18-24/11/2025</p>
									<p><strong>Problema:</strong> 52 horas trabajadas (máximo: 48h según CC)</p>
								</div>
							</div>
							
							<div class="alerta-item alerta-advertencia">
								<div class="alerta-icono">⚠️</div>
								<div class="alerta-contenido">
									<h4>Descanso Insuficiente</h4>
									<p><strong>Agente:</strong> Carlos Rodriguez</p>
									<p><strong>Fecha:</strong> 21-22/11/2025</p>
									<p><strong>Problema:</strong> 8 horas de descanso (mínimo: 12h entre guardias)</p>
								</div>
							</div>
							
							<div class="alerta-item alerta-info">
								<div class="alerta-icono">ℹ️</div>
								<div class="alerta-contenido">
									<h4>Próximo a Límite</h4>
									<p><strong>Agente:</strong> Sandra Lopez</p>
									<p><strong>Semana:</strong> 18-24/11/2025</p>
									<p><strong>Problema:</strong> 46 horas trabajadas (límite: 48h)</p>
								</div>
							</div>
						</div>
						
						<div class="preview-note">
							<p>⚖️ Monitorea automáticamente el cumplimiento de normas del Convenio Colectivo. Genera alertas preventivas.</p>
						</div>
					</div>
				{:else}
					<!-- Vista previa reporte general -->
					<div class="reporte-general">
						<div class="reporte-header">
							<h3>Planilla General/Preventiva</h3>
							<div class="datos-area">
								<p><strong>Dirección:</strong> {$datosReporte.area_nombre}</p>
								<p><strong>Mes:</strong> {$datosReporte.periodo.mes}</p>
								<p><strong>Período:</strong> {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo.fecha_hasta}</p>
							</div>
						</div>

						<div class="tabla-container">
							<table class="tabla-reporte tabla-individual">
								<thead>
									<tr>
										<th>Día</th>
										<th>Horario Habitual / Novedad</th>
										<th>Horario de Guardia</th>
										<th>Horas</th>
										<th>Motivo de la Guardia</th>
									</tr>
								</thead>
								<tbody>
									{#each $datosReporte.dias_mes.slice(0, 10) as dia}
										<tr class:dia-con-guardia={dia.tiene_guardia} class:fin-semana={!dia.horario_habitual_inicio}>
											<td class="dia-fecha">
												<div class="fecha-completa">
													<span class="numero-dia">{dia.dia_mes}</span>
													<span class="nombre-dia">{dia.dia_semana}</span>
												</div>
											</td>
											<td class="horario-novedad">
												{#if dia.novedad && dia.novedad !== "Jornada habitual"}
													<span class="novedad">{dia.novedad}</span>
												{:else if dia.horario_habitual_inicio}
													<span class="horario-habitual">{dia.horario_habitual_inicio} - {dia.horario_habitual_fin}</span>
												{:else}
													<span class="sin-jornada">-</span>
												{/if}
											</td>
											<td class="horario-guardia">
												{#if dia.guardia_inicio}
													<span class="horario-guardia-valor">{dia.guardia_inicio} - {dia.guardia_fin}</span>
													{#if dia.horas_efectivas > 0}
														<span class="presentismo-ok">✓</span>
													{:else}
														<span class="presentismo-pendiente">⚠</span>
													{/if}
												{:else}
													-
												{/if}
											</td>
											<td class="horas-columna text-center">
												{#if dia.horas_planificadas > 0}
													<div class="horas-planificadas">{dia.horas_planificadas}h</div>
													{#if dia.horas_efectivas > 0 && dia.horas_efectivas !== dia.horas_planificadas}
														<div class="horas-efectivas">({dia.horas_efectivas}h efec.)</div>
													{/if}
												{:else}
													-
												{/if}
											</td>
											<td class="motivo-guardia">
												{#if dia.motivo_guardia}
													<span class="motivo">{dia.motivo_guardia}</span>
												{:else}
													-
												{/if}
											</td>
										</tr>
									{/each}
								</tbody>
								<tfoot>
									<tr class="total-row">
										<td><strong>TOTAL</strong></td>
										<td colspan="3" class="text-center">
											<strong>Días con guardias: {$datosReporte.totales.total_dias_trabajados}</strong>
										</td>
										<td class="text-center">
											<strong>{$datosReporte.totales.total_horas_planificadas}h</strong>
										</td>
									</tr>
								</tfoot>
							</table>
						</div>

						{#if $datosReporte.dias_mes.length > 10}
							<div class="vista-limitada">
								<p>Mostrando 10 de {$datosReporte.dias_mes.length} días. Exporte para ver el reporte completo.</p>
							</div>
						{/if}

						<div class="totales-reporte">
							<div class="totales-row">
								<div class="total-item">
									<span class="total-label">Total días con guardias:</span>
									<span class="total-valor">{$datosReporte.totales.total_dias_trabajados}</span>
								</div>
								<div class="total-item">
									<span class="total-label">Horas planificadas:</span>
									<span class="total-valor">{$datosReporte.totales.total_horas_planificadas || $datosReporte.totales.total_horas_guardia}h</span>
								</div>
								<div class="total-item">
									<span class="total-label">Promedio horas/día:</span>
									<span class="total-valor">{$datosReporte.totales.promedio_horas_dia}h</span>
								</div>
							</div>
							
							<div class="presentismo-info">
								<h4>📊 Información de Presentismo</h4>
								<div class="totales-row">
									<div class="total-item success">
										<span class="total-label">Días con presentismo:</span>
										<span class="total-valor">{$datosReporte.totales.dias_con_presentismo || 0}</span>
									</div>
									<div class="total-item warning">
										<span class="total-label">Días sin registro:</span>
										<span class="total-valor">{$datosReporte.totales.dias_sin_presentismo || 0}</span>
									</div>
									<div class="total-item">
										<span class="total-label">Horas efectivas:</span>
										<span class="total-valor">{$datosReporte.totales.total_horas_efectivas || 0}h</span>
									</div>
									<div class="total-item">
										<span class="total-label">% Presentismo:</span>
										<span class="total-valor">{$datosReporte.totales.porcentaje_presentismo || 0}%</span>
									</div>
								</div>
								
								{#if ($datosReporte.totales.dias_sin_presentismo || 0) > 0}
									<div class="alerta-presentismo">
										<p>⚠️ <strong>Nota:</strong> Hay guardias sin registro de presentismo. Las horas efectivas se registran cuando el agente marca entrada y salida durante su guardia en el sistema de asistencias.</p>
									</div>
								{/if}
							</div>
						</div>
					</div>

						{#if $datosReporte.dias_columnas && $datosReporte.dias_columnas.length > 0}
							<div class="tabla-container tabla-grilla">
								<table class="tabla-reporte tabla-general">
									<thead>
										<tr>
											<th rowspan="2" class="agente-header">Agente y Legajo</th>
											<th colspan="{$datosReporte.dias_columnas.length}" class="dias-header">Días del mes</th>
											<th rowspan="2" class="total-header">Total</th>
										</tr>
										<tr class="dias-numeros">
											{#each $datosReporte.dias_columnas as dia}
												<th class="dia-numero" class:fin-semana={dia.dia_semana === 'Sáb' || dia.dia_semana === 'Dom'}>
													<div class="dia-info">
														<span class="numero">{dia.dia}</span>
														<span class="dia-sem">{dia.dia_semana}</span>
													</div>
												</th>
											{/each}
										</tr>
									</thead>
									<tbody>
										{#each $datosReporte.agentes.slice(0, 5) as agente}
											<tr>
												<td class="agente-info">
													<div class="nombre-legajo">
														<span class="nombre">{agente.nombre_completo}</span>
														<span class="legajo">Leg: {agente.legajo}</span>
													</div>
												</td>
												{#each $datosReporte.dias_columnas as dia}
													{@const diaData = getDiaData(agente, dia.fecha)}
													<td class="dia-celda" class:con-horas={diaData?.horas > 0} class:fin-semana={dia.dia_semana === 'Sáb' || dia.dia_semana === 'Dom'}>
														{#if diaData}
															{#if diaData.tipo === 'guardia'}
																<span class="horas-guardia">{diaData.valor}</span>
															{:else if diaData.valor === '-'}
																<span class="sin-actividad">-</span>
															{:else}
																<span class="novedad">{diaData.valor}</span>
															{/if}
														{:else}
															<span class="sin-datos">-</span>
														{/if}
													</td>
												{/each}
												<td class="total-agente">
													<strong>{agente.total_horas}h</strong>
												</td>
											</tr>
										{/each}
									</tbody>
									<tfoot>
										<tr class="total-direccion">
											<td><strong>TOTAL DIRECCIÓN</strong></td>
											{#each $datosReporte.dias_columnas as dia}
												{@const totalDia = getTotalDia(dia.fecha)}
												<td class="total-dia">
													{#if totalDia > 0}
														<strong>{totalDia.toFixed(1)}h</strong>
													{:else}
														-
													{/if}
												</td>
											{/each}
											<td class="total-general">
												<strong>{$datosReporte.totales.total_horas_direccion}h</strong>
											</td>
										</tr>
									</tfoot>
								</table>
							</div>
							
							{#if $datosReporte.agentes.length > 5}
								<div class="vista-limitada">
									<p>Mostrando 5 de {$datosReporte.agentes.length} agentes. Exporte para ver el reporte completo con todos los agentes.</p>
								</div>
							{/if}
						{:else}
							<!-- Fallback si no hay datos de días por columnas -->
							<div class="tabla-container">
								<table class="tabla-reporte">
									<thead>
										<tr>
											<th>Agente</th>
											<th>Legajo</th>
											<th>Total Horas</th>
											<th>Estado</th>
										</tr>
									</thead>
									<tbody>
										{#each $datosReporte.agentes as agente}
											<tr>
												<td>{agente.nombre_completo}</td>
												<td>{agente.legajo}</td>
												<td class="text-center">{agente.total_horas}h</td>
												<td>
													{#if agente.total_horas > 0}
														<span class="badge badge-activo">Activo</span>
													{:else}
														<span class="badge badge-inactivo">Sin guardias</span>
													{/if}
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						{/if}

						<div class="totales-reporte">
							<div class="totales-row">
								<div class="total-item">
									<span class="total-label">Total agentes:</span>
									<span class="total-valor">{$datosReporte.totales.total_agentes}</span>
								</div>
								<div class="total-item">
									<span class="total-label">Total horas dirección:</span>
									<span class="total-valor">{$datosReporte.totales.total_horas_direccion || $datosReporte.totales.total_horas_todas}h</span>
								</div>
								<div class="total-item">
									<span class="total-label">Promedio por agente:</span>
									<span class="total-valor">{$datosReporte.totales.promedio_horas_agente}h</span>
								</div>
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
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
		min-height: 100vh;
	}

	/* ===== ENCABEZADO ===== */
	.header-reportes {
		background: white;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		margin-bottom: 2rem;
	}

	.titulo-section h1 {
		margin: 0 0 0.5rem 0;
		color: #2c3e50;
		font-size: 1.3rem;
		font-weight: 700;
		max-width: 100%;
		word-wrap: break-word;
	}

	@media (min-width: 480px) {
		.titulo-section h1 {
			font-size: 1.5rem;
		}
	}

	@media (min-width: 640px) {
		.titulo-section h1 {
			font-size: 1.7rem;
		}
	}

	@media (min-width: 768px) {
		.titulo-section h1 {
			font-size: 2rem;
		}
	}

	.titulo-section p {
		margin: 0;
		color: #6c757d;
		font-size: 1.1rem;
	}

	.estado-carga {
		color: #007bff !important;
		font-weight: 500;
	}

	.estado-advertencia {
		color: #ffc107 !important;
		font-weight: 500;
	}

	.estado-ok {
		color: #28a745 !important;
		font-weight: 500;
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

	/* ===== SELECTOR DE TIPO ===== */
	.selector-tipo {
		background: white;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		margin-bottom: 2rem;
	}

	.tipos-categoria {
		margin-bottom: 2.5rem;
	}

	.tipos-categoria:last-child {
		margin-bottom: 0;
	}

	.categoria-titulo {
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e9ecef;
	}

	.categoria-titulo h3 {
		margin: 0 0 0.5rem 0;
		color: #2c3e50;
		font-size: 1.3rem;
		font-weight: 700;
	}

	.categoria-titulo p {
		margin: 0;
		color: #6c757d;
		font-size: 0.95rem;
	}

	.selector-tipo-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
	}

	.selector-opcion {
		display: flex;
		align-items: center;
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
		transform: scale(1.2);
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

	/* ===== PANEL DE FILTROS ===== */
	.panel-filtros {
		background: white;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
		flex-wrap: wrap;
	}

	.input-fecha {
		flex: 1;
		min-width: 150px;
		padding: 0.75rem;
		border: 1px solid #dee2e6;
		border-radius: 6px;
		font-size: 1rem;
		transition: border-color 0.2s;
	}

	.input-fecha:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
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
		box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
	}

	.select-filtro.requerido {
		border-color: #ffc107;
		background: #fff8e1;
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

	/* ===== BOTONES ===== */
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
		background: #007bff;
		color: white;
	}

	.btn-primario:hover:not(.disabled) {
		background: #0056b3;
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0,123,255,0.3);
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

	/* ===== PANEL DE RESULTADO ===== */
	.panel-resultado {
		background: white;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
	}

	.tabla-reporte {
		width: 100%;
		border-collapse: collapse;
		background: white;
		border-radius: 6px;
		overflow: hidden;
		box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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

	.tabla-reporte .text-center {
		text-align: center;
	}

	.badge {
		padding: 0.25rem 0.5rem;
		font-size: 0.8rem;
		border-radius: 4px;
		font-weight: 500;
	}

	.badge-activo {
		background: #d4edda;
		color: #155724;
	}

	.badge-inactivo {
		background: #f8d7da;
		color: #721c24;
	}

	.totales-reporte {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		padding: 1rem;
		background: white;
		border-radius: 6px;
		border: 1px solid #e9ecef;
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

	.vista-limitada {
		text-align: center;
		padding: 1rem;
		background: #fff3cd;
		color: #856404;
		border-radius: 4px;
		margin: 1rem 0;
		font-style: italic;
	}

	/* ===== SPINNERS ===== */
	.spinner {
		width: 20px;
		height: 20px;
		border: 2px solid rgba(255,255,255,0.3);
		border-top: 2px solid white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.spinner-pequeño {
		width: 14px;
		height: 14px;
		border: 2px solid rgba(255,255,255,0.3);
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
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.loading-inicial {
		text-align: center;
		padding: 4rem 2rem;
		color: #6c757d;
	}

	/* ===== ESTILOS ESPECÍFICOS REPORTES ===== */
	
	/* Tabla Individual */
	.tabla-individual .dia-fecha {
		text-align: center;
		min-width: 80px;
	}
	
	.fecha-completa {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
	}
	
	.numero-dia {
		font-size: 1.2rem;
		font-weight: 700;
		color: #2c3e50;
	}
	
	.nombre-dia {
		font-size: 0.8rem;
		color: #6c757d;
		text-transform: capitalize;
	}
	
	.horario-novedad {
		min-width: 150px;
	}
	
	.novedad {
		color: #ffc107;
		font-weight: 600;
		font-style: italic;
	}
	
	.horario-habitual {
		color: #28a745;
		font-weight: 500;
	}
	
	.sin-jornada {
		color: #6c757d;
		font-style: italic;
	}
	
	.horario-guardia {
		position: relative;
		min-width: 120px;
	}
	
	.horario-guardia-valor {
		color: #007bff;
		font-weight: 600;
	}
	
	.presentismo-ok {
		color: #28a745;
		font-weight: bold;
		margin-left: 0.5rem;
	}
	
	.presentismo-pendiente {
		color: #ffc107;
		font-weight: bold;
		margin-left: 0.5rem;
	}
	
	.horas-columna {
		min-width: 100px;
	}
	
	.horas-planificadas {
		font-weight: 600;
		color: #2c3e50;
	}
	
	.horas-efectivas {
		font-size: 0.8rem;
		color: #28a745;
		font-style: italic;
	}
	
	.motivo-guardia {
		min-width: 100px;
	}
	
	.motivo {
		background: #e3f2fd;
		color: #1976d2;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.85rem;
		font-weight: 500;
	}
	
	.dia-con-guardia {
		background: linear-gradient(135deg, #fff8e1 0%, #ffffff 100%);
		border-left: 4px solid #ffc107;
	}
	
	.fin-semana {
		background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
	}
	
	.total-row {
		background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
		border-top: 2px solid #28a745;
		font-weight: 600;
	}
	
	/* Tabla General/Grilla */
	.tabla-grilla {
		overflow-x: auto;
		border-radius: 8px;
		border: 1px solid #dee2e6;
	}
	
	.tabla-general {
		min-width: 800px;
		font-size: 0.85rem;
	}
	
	.agente-header,
	.total-header {
		background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
		color: white;
		text-align: center;
		font-weight: 600;
		min-width: 150px;
	}
	
	.dias-header {
		background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
		color: white;
		text-align: center;
		font-weight: 600;
	}
	
	.dias-numeros th {
		background: linear-gradient(135deg, #ecf0f1 0%, #bdc3c7 100%);
		color: #2c3e50;
		padding: 0.5rem 0.25rem;
		border-bottom: 1px solid #95a5a6;
		min-width: 45px;
		max-width: 45px;
	}
	
	.dias-numeros th.fin-semana {
		background: linear-gradient(135deg, #fadbd8 0%, #f1948a 100%);
		color: #922b21;
	}
	
	.dia-info {
		display: flex;
		flex-direction: column;
		align-items: center;
		line-height: 1.2;
	}
	
	.dia-info .numero {
		font-weight: 700;
		font-size: 0.9rem;
	}
	
	.dia-info .dia-sem {
		font-size: 0.7rem;
		text-transform: uppercase;
	}
	
	.agente-info {
		background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
		border-right: 2px solid #dee2e6;
		min-width: 150px;
		max-width: 150px;
		padding: 0.75rem 0.5rem;
	}
	
	.nombre-legajo {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	
	.nombre {
		font-weight: 600;
		color: #2c3e50;
		font-size: 0.9rem;
		line-height: 1.2;
	}
	
	.legajo {
		font-size: 0.75rem;
		color: #7f8c8d;
		font-style: italic;
	}
	
	.dia-celda {
		text-align: center;
		padding: 0.5rem 0.25rem;
		vertical-align: middle;
		min-width: 45px;
		max-width: 45px;
		border-right: 1px solid #ecf0f1;
	}
	
	.dia-celda.fin-semana {
		background: linear-gradient(135deg, #fdf2e9 0%, #fadbd8 100%);
	}
	
	.dia-celda.con-horas {
		background: linear-gradient(135deg, #d5f4e6 0%, #a9dfbf 100%);
		font-weight: 600;
	}
	
	.horas-guardia {
		color: #27ae60;
		font-weight: 700;
		font-size: 0.8rem;
	}
	
	.sin-actividad,
	.sin-datos {
		color: #bdc3c7;
		font-style: italic;
	}
	
	.novedad {
		background: #fff3cd;
		color: #856404;
		padding: 0.1rem 0.3rem;
		border-radius: 3px;
		font-size: 0.7rem;
		font-weight: 500;
		display: inline-block;
		transform: rotate(-45deg);
		font-style: normal;
	}
	
	.total-agente {
		background: linear-gradient(135deg, #e8f5e8 0%, #d5f4e6 100%);
		border-left: 2px solid #27ae60;
		text-align: center;
		font-weight: 600;
		color: #27ae60;
		min-width: 80px;
	}
	
	.total-direccion {
		background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
		color: white;
		font-weight: 700;
	}
	
	.total-direccion td {
		padding: 0.75rem 0.5rem;
		text-align: center;
		border-top: 3px solid #f39c12;
	}
	
	.total-dia {
		font-size: 0.8rem;
	}
	
	.total-general {
		background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
		font-size: 1.1rem;
	}

	/* ===== RESPONSIVE ===== */
	@media (max-width: 768px) {
		.container-reportes {
			padding: 1rem;
		}

		.selector-tipo-container {
			grid-template-columns: 1fr;
		}

		.tipos-categoria {
			margin-bottom: 2rem;
		}

		.categoria-titulo h3 {
			font-size: 1.1rem;
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

		.rango-separador {
			text-align: center;
			order: 1;
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

		.totales-reporte {
			grid-template-columns: 1fr;
		}

		.opciones-adicionales {
			flex-direction: column;
			gap: 1rem;
		}
		
		.presentismo-info {
			grid-column: 1 / -1;
		}
		
		.totales-row {
			display: grid;
			grid-template-columns: 1fr;
			gap: 0.5rem;
		}
	}
	
	/* ===== ESTILOS DE PRESENTISMO ===== */
	.horas-efectivas {
		color: #28a745;
		font-weight: 600;
	}
	
	.sin-registro {
		color: #ffc107;
		font-size: 0.8rem;
		font-weight: 500;
	}
	
	.badge-warning {
		background-color: #fff3cd;
		color: #856404;
		border: 1px solid #ffeaa7;
		font-size: 0.7rem;
		margin-left: 0.25rem;
	}
	
	.presentismo-info {
		background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
		padding: 1.5rem;
		border-radius: 12px;
		border: 1px solid #dee2e6;
		margin-top: 1rem;
	}
	
	.presentismo-info h4 {
		margin: 0 0 1rem 0;
		color: #495057;
		font-size: 1rem;
		font-weight: 600;
	}
	
	.totales-row {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 1rem;
	}
	
	.total-item.success {
		border-left: 4px solid #28a745;
	}
	
	.total-item.warning {
		border-left: 4px solid #ffc107;
	}
	
	.alerta-presentismo {
		background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
		border: 1px solid #ffc107;
		border-radius: 8px;
		padding: 1rem;
		margin-top: 1rem;
	}
	
	.alerta-presentismo p {
		margin: 0;
		color: #856404;
		font-size: 0.9rem;
		line-height: 1.4;
	}

	/* ===== ESTILOS ESPECÍFICOS NUEVOS REPORTES ===== */
	
	/* Reporte de Guardias y Compensaciones */
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
	
	/* Reporte de Plus */
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

	/* Reporte Parte Diario */
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

	/* Reporte Licencias */
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

	/* Reporte Plus */
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
	
	.tabla-plus .horas-normales {
		text-align: center;
		color: #2c3e50;
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
	
	.tabla-plus .total-liquidar {
		text-align: center;
		background: linear-gradient(135deg, #d4edda 0%, #a9dfbf 100%);
		color: #155724;
		font-size: 0.95rem;
	}

	/* Reporte Incumplimiento Normativo */
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

	/* Nota de vista previa */
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

	/* Filas de ejemplo */
	.ejemplo-fila {
		background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
		opacity: 0.8;
	}
	
	.ejemplo-fila:hover {
		opacity: 1;
		background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%);
	}
	
</style>
