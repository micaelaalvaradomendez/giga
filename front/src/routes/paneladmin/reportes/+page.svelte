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
		await reporteController.inicializar();
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
		if (tipo === 'individual') {
			await reporteController.generarReporteIndividual();
		} else {
			await reporteController.generarReporteGeneral();
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

						<div class="tabla-container">
							<table class="tabla-reporte">
								<thead>
									<tr>
										<th>Fecha</th>
										<th>Día</th>
										<th>Horario Habitual</th>
										<th>Horario Guardia</th>
										<th>Horas Plan.</th>
										<th>Horas Efect.</th>
										<th>Estado</th>
									</tr>
								</thead>
								<tbody>
									{#each $datosReporte.dias_mes.slice(0, 10) as dia}
										<tr>
											<td>{dia.fecha}</td>
											<td>{dia.dia_semana}</td>
											<td>
												{#if dia.horario_habitual_inicio}
													{dia.horario_habitual_inicio} - {dia.horario_habitual_fin}
												{:else}
													-
												{/if}
											</td>
											<td>
												{#if dia.guardia_inicio}
													{dia.guardia_inicio} - {dia.guardia_fin}
												{:else}
													-
												{/if}
											</td>
											<td class="text-center">
												{#if dia.horas_planificadas > 0}
													{dia.horas_planificadas}h
												{:else}
													-
												{/if}
											</td>
											<td class="text-center">
												{#if dia.horas_efectivas > 0}
													<span class="horas-efectivas">{dia.horas_efectivas}h</span>
												{:else if dia.tiene_guardia}
													<span class="sin-registro">⚠️ Pendiente</span>
												{:else}
													-
												{/if}
											</td>
											<td>
												{#if dia.tiene_guardia}
													<span class="badge badge-activo">Guardia</span>
													{#if !dia.horas_efectivas}
														<span class="badge badge-warning">Sin presentismo</span>
													{/if}
												{:else}
													<span class="badge badge-inactivo">Normal</span>
												{/if}
											</td>
										</tr>
									{/each}
								</tbody>
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
				{:else}
					<!-- Vista previa reporte general -->
					<div class="reporte-general">
						<div class="reporte-header">
							<h3>Planilla General/Preventiva</h3>
							<div class="datos-area">
								<p><strong>Área:</strong> {$datosReporte.area_nombre}</p>
								<p><strong>Período:</strong> {$datosReporte.periodo.fecha_desde} - {$datosReporte.periodo.fecha_hasta}</p>
							</div>
						</div>

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

						<div class="totales-reporte">
							<div class="total-item">
								<span class="total-label">Total agentes:</span>
								<span class="total-valor">{$datosReporte.totales.total_agentes}</span>
							</div>
							<div class="total-item">
								<span class="total-label">Total horas área:</span>
								<span class="total-valor">{$datosReporte.totales.total_horas_todas}h</span>
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
		font-size: 2rem;
		font-weight: 700;
	}

	.titulo-section p {
		margin: 0;
		color: #6c757d;
		font-size: 1.1rem;
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

	.selector-tipo-container {
		display: grid;
		grid-template-columns: 1fr 1fr;
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

	/* ===== RESPONSIVE ===== */
	@media (max-width: 768px) {
		.container-reportes {
			padding: 1rem;
		}

		.selector-tipo-container {
			grid-template-columns: 1fr;
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
	
</style>
