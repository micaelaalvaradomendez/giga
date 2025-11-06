<script>
	import { onMount } from 'svelte';
	import { parametrosController } from '$lib/paneladmin/controllers';
	import { goto } from '$app/navigation';
	
	// Importar componentes modales
	import ModalArea from '$lib/componentes/ModalArea.svelte';
	import ModalAgrupacion from '$lib/componentes/ModalAgrupacion.svelte';
	import ModalHorarios from '$lib/componentes/ModalHorarios.svelte';
	import ModalEliminar from '$lib/componentes/ModalEliminar.svelte';

	// Obtener referencias a los stores individuales
	const { 
		areas, agrupaciones, loading, error, busquedaAreas, busquedaAgrupaciones,
		areasFiltradas, agrupacionesFiltradas, modalArea, modalAgrupacion, modalSchedule,
		modalDelete, areaForm, agrupacionForm, scheduleForm
	} = parametrosController;

	// Validación de autenticación e inicialización
	onMount(async () => {
		try {
			console.log('🚀 Iniciando controlador de parámetros...');
			await parametrosController.init();
			console.log('✅ Controlador de parámetros inicializado');
		} catch (err) {
			console.error('❌ Error inicializando controlador:', err);
			if (err.message === 'Usuario no autenticado' || err.message === 'Sesión expirada') {
				goto('/');
				return;
			}
			// El controlador maneja el error automáticamente
		}
	});

	// Event handlers para filtros de búsqueda
	function actualizarBusquedaAreas(event) {
		parametrosController.actualizarBusquedaAreas(event.target.value);
	}

	function actualizarBusquedaAgrupaciones(event) {
		parametrosController.actualizarBusquedaAgrupaciones(event.target.value);
	}

	// Event handlers para modales
	async function actualizarHorarios() {
		try {
			const formData = $scheduleForm;
			const modalData = $modalSchedule;
			
			await parametrosController.actualizarHorarios(formData, modalData.tipo, modalData.target);
		} catch (error) {
			console.error('Error actualizando horarios:', error);
			// Manejar error - podríamos mostrar una notificación
		}
	}

	async function confirmarEliminar() {
		try {
			const modalData = $modalDelete;
			
			if (modalData.tipo === 'area') {
				await parametrosController.confirmarEliminarArea(modalData.item.id_area);
			} else if (modalData.tipo === 'agrupacion') {
				await parametrosController.confirmarEliminarAgrupacion(
					modalData.item.id_agrupacion, 
					modalData.nuevaAsignacion
				);
			}
		} catch (error) {
			console.error('Error eliminando elemento:', error);
			// Manejar error - podríamos mostrar una notificación
		}
	}

	async function guardarArea() {
		try {
			await parametrosController.guardarArea($areaForm);
		} catch (error) {
			console.error('Error guardando área:', error);
			parametrosController.error.set(error.message);
		}
	}

	async function guardarAgrupacion() {
		try {
			await parametrosController.guardarAgrupacion($agrupacionForm);
		} catch (error) {
			console.error('Error guardando agrupación:', error);
			parametrosController.error.set(error.message);
		}
	}
</script><svelte:head>
	<title>Parámetros del Sistema - GIGA</title>
</svelte:head>

<div class="page-header">
	<h1>Gestión de Parámetros del Sistema</h1>
	<div class="header-actions">
		<button class="btn-primary" on:click={() => parametrosController.agregarArea()}>
			+ Añadir Área
		</button>
		<button class="btn-secondary" on:click={() => parametrosController.agregarAgrupacion()}>
			+ Añadir Agrupación
		</button>
	</div>
</div>

<!-- Mensajes de error -->
{#if $error}
	<div class="alert alert-error">
		❌ {$error}
		<button class="btn-close" on:click={() => parametrosController.error.set(null)}>×</button>
	</div>
{/if}

<!-- Loading indicator -->
{#if $loading}
	<div class="loading-container">
		<div class="loading-spinner"></div>
		<p>Cargando parámetros del sistema...</p>
	</div>
{:else}

<!-- Resumen de estadísticas -->
{#if ($areasFiltradas && $areasFiltradas.length > 0) || ($agrupacionesFiltradas && $agrupacionesFiltradas.length > 0)}
<div class="stats-container">
	<div class="stat-card">
		<h3>Total Áreas</h3>
		<p class="stat-number">{$areas ? $areas.length : 0}</p>
	</div>
	<div class="stat-card">
		<h3>Áreas Activas</h3>
		<p class="stat-number">{$areas ? $areas.filter(a => a.activo).length : 0}</p>
	</div>
	<div class="stat-card">
		<h3>Total Agrupaciones</h3>
		<p class="stat-number">{$agrupaciones ? $agrupaciones.length : 0}</p>
	</div>
	<div class="stat-card">
		<h3>Agentes en Agrupaciones</h3>
		<p class="stat-number">{$agrupaciones ? $agrupaciones.reduce((sum, a) => sum + (a.total_agentes || 0), 0) : 0}</p>
	</div>
</div>
{/if}

<div class="content-grid">
	<!-- Panel de Áreas -->
	<div class="panel-areas">
		<div class="panel-header">
			<h2>📍 Gestión de Áreas</h2>
		</div>
		
		<!-- Filtros de áreas -->
		<div class="filtros-container">
			<div class="filtro-group">
				<label for="busquedaAreas">🔍 Buscar áreas</label>
				<input 
					type="text" 
					id="busquedaAreas"
					bind:value={$busquedaAreas}
					placeholder="Buscar por nombre..."
					class="input-busqueda"
				>
			</div>
			<div class="filtro-actions">
				<button class="btn-limpiar" on:click={() => parametrosController.limpiarFiltrosAreas()} title="Limpiar filtros">
					🗑️ Limpiar
				</button>
			</div>
		</div>

		<div class="table-container">
			<table>
				<thead>
					<tr>
						<th>Área</th>
						<th>Estado</th>
						<th>Acciones</th>
					</tr>
				</thead>
				<tbody>
				{#if $areasFiltradas && $areasFiltradas.length > 0}
					{#each $areasFiltradas as area}
						<tr>
							<td>
								<strong>{area.nombre}</strong>
							</td>
							<td>
								<span class="badge badge-{area.activo ? 'success' : 'inactive'}">
									{area.activo ? 'Activa' : 'Inactiva'}
								</span>
							</td>
							<td class="actions">
								<button class="btn-icon" title="Editar" on:click={() => parametrosController.editarArea(area)}>✏️</button>
								<button class="btn-icon" title="Horarios" on:click={() => parametrosController.gestionarHorarios('area', area)}>🕒</button>
								<button class="btn-icon-danger" title="Eliminar" on:click={() => parametrosController.eliminarArea(area)}>🗑️</button>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="3" style="text-align: center; padding: 2rem;">
							{#if busquedaAreas}
								No se encontraron áreas que coincidan con la búsqueda.
								<br><button class="btn-link" on:click={() => parametrosController.limpiarFiltrosAreas()}>Limpiar filtros</button>
							{:else}
								No hay áreas registradas.
								<br><button class="btn-link" on:click={() => parametrosController.agregarArea()}>Crear primera área</button>
							{/if}
						</td>
					</tr>
				{/if}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Panel de Agrupaciones -->
	<div class="panel-agrupaciones">
		<div class="panel-header">
			<h2>👥 Gestión de Agrupaciones</h2>
		</div>
		
		<!-- Filtros de agrupaciones -->
		<div class="filtros-container">
			<div class="filtro-group">
				<label for="busquedaAgrupaciones">🔍 Buscar agrupaciones</label>
				<input 
					type="text" 
					id="busquedaAgrupaciones"
					bind:value={$busquedaAgrupaciones}
					placeholder="Buscar por nombre..."
					class="input-busqueda"
				>
			</div>
			<div class="filtro-actions">
				<button class="btn-limpiar" on:click={() => parametrosController.limpiarFiltrosAgrupaciones()} title="Limpiar filtros">
					🗑️ Limpiar
				</button>
			</div>
		</div>

		<div class="table-container">
			<table>
				<thead>
					<tr>
						<th>Agrupación</th>
						<th>Descripción</th>
						<th>Agentes</th>
						<th>Estado</th>
						<th>Acciones</th>
					</tr>
				</thead>
				<tbody>
				{#if $agrupacionesFiltradas && $agrupacionesFiltradas.length > 0}
					{#each $agrupacionesFiltradas as agrupacion}
						<tr>
							<td>
								<div class="agrupacion-info">
									<div 
										class="color-indicator" 
										style="background-color: {agrupacion.color}"
									></div>
									<strong>{agrupacion.nombre}</strong>
								</div>
							</td>
							<td>{agrupacion.descripcion || 'Sin descripción'}</td>
							<td>
								<span class="badge badge-info">
									{agrupacion.total_agentes} agentes
								</span>
							</td>
							<td>
								<span class="badge badge-{agrupacion.activo ? 'success' : 'inactive'}">
									{agrupacion.activo ? 'Activa' : 'Inactiva'}
								</span>
							</td>
							<td class="actions">
								<button class="btn-icon" title="Editar" on:click={() => parametrosController.editarAgrupacion(agrupacion)}>✏️</button>
								<button class="btn-icon" title="Horarios" on:click={() => parametrosController.gestionarHorarios('agrupacion', agrupacion)}>🕒</button>
								<button class="btn-icon-danger" title="Eliminar" on:click={() => parametrosController.eliminarAgrupacion(agrupacion)}>🗑️</button>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="5" style="text-align: center; padding: 2rem;">
							{#if busquedaAgrupaciones}
								No se encontraron agrupaciones que coincidan con la búsqueda.
								<br><button class="btn-link" on:click={() => parametrosController.limpiarFiltrosAgrupaciones()}>Limpiar filtros</button>
							{:else}
								No hay agrupaciones registradas.
																<br><button class="btn-link" on:click={() => parametrosController.agregarAgrupacion()}>Crear primera agrupación</button>
							{/if}
						</td>
					</tr>
				{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>

{/if}

<!-- Componentes Modales -->
<ModalArea 
	isOpen={$modalArea.isOpen}
	isSaving={$modalArea.isSaving}
	formData={$areaForm}
	on:guardar={guardarArea}
	on:cerrar={() => parametrosController.modalArea.update(m => ({...m, isOpen: false}))}
/>

<ModalAgrupacion 
	isOpen={$modalAgrupacion.isOpen}
	isSaving={$modalAgrupacion.isSaving}
	formData={$agrupacionForm}
	on:guardar={guardarAgrupacion}
	on:cerrar={() => parametrosController.modalAgrupacion.update(m => ({...m, isOpen: false}))}
/>

<ModalHorarios 
	isOpen={$modalSchedule.isOpen}
	isSaving={$modalSchedule.isSaving}
	tipoHorarios={$modalSchedule.tipo}
	selectedItem={$modalSchedule.target}
	formData={$scheduleForm}
	on:guardar={(event) => {
		const { horario_entrada, horario_salida, tipo, target } = event.detail;
		parametrosController.actualizarHorarios({ horario_entrada, horario_salida }, tipo, target);
	}}
	on:cerrar={() => parametrosController.modalSchedule.update(m => ({...m, isOpen: false}))}
/>

<ModalEliminar 
	isOpen={$modalDelete.isOpen}
	isDeleting={$modalDelete.isDeleting}
	itemToDelete={$modalDelete.item}
	type={$modalDelete.tipo}
	on:confirmar={confirmarEliminar}
	on:cerrar={() => parametrosController.modalDelete.update(m => ({...m, isOpen: false}))}
/>



<style>
	/* Container principal */
	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 20px;
	}

	/* Logo y navegación */
	.logo {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 15px 20px;
		margin-bottom: 0;
		box-shadow: 0 2px 10px rgba(0,0,0,0.1);
	}

	.logo a {
		color: white;
		text-decoration: none;
		font-weight: 600;
		font-size: 18px;
		transition: opacity 0.3s ease;
	}

	.logo a:hover {
		opacity: 0.8;
	}

	/* Header de página */
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin: 30px 0;
		padding-bottom: 20px;
		border-bottom: 3px solid #f8f9fa;
	}

	.page-header h1 {
		color: #2c3e50;
		font-size: 2.2rem;
		font-weight: 700;
		margin: 0;
	}

	.header-actions {
		display: flex;
		gap: 10px;
	}

	/* Botones principales */
	.btn-primary, .btn-secondary {
		padding: 12px 24px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 8px;
	}

	.btn-primary {
		background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
		color: white;
	}

	.btn-primary:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
	}

	.btn-secondary {
		background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
		color: white;
	}

	.btn-secondary:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
	}

	/* Alertas */
	.alert {
		padding: 15px 20px;
		border-radius: 8px;
		margin: 20px 0;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.alert-error {
		background: #ffebee;
		color: #c62828;
		border-left: 4px solid #f44336;
	}

	.alert-info {
		background: #e3f2fd;
		color: #1565c0;
		border-left: 4px solid #2196f3;
		margin: 15px 0;
	}

	.btn-close {
		background: none;
		border: none;
		font-size: 18px;
		cursor: pointer;
		opacity: 0.6;
		transition: opacity 0.3s ease;
	}

	.btn-close:hover {
		opacity: 1;
	}

	/* Loading */
	.loading-container {
		text-align: center;
		padding: 60px 20px;
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #f3f3f3;
		border-top: 4px solid #3498db;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 20px;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	/* Grid de contenido */
	.content-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 30px;
		margin: 30px 0;
	}

	@media (max-width: 1024px) {
		.content-grid {
			grid-template-columns: 1fr;
		}
	}

	/* Estadísticas */
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 20px;
		margin: 30px 0;
	}

	.stat-card {
		background: white;
		padding: 25px;
		border-radius: 12px;
		box-shadow: 0 2px 10px rgba(0,0,0,0.1);
		text-align: center;
		border-top: 4px solid #3498db;
		transition: transform 0.3s ease;
	}

	.stat-card:hover {
		transform: translateY(-5px);
	}

	.stat-card h3 {
		margin: 0 0 10px;
		color: #555;
		font-size: 0.9rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.stat-number {
		font-size: 2.5rem;
		font-weight: 700;
		color: #3498db;
		margin: 0;
	}

	/* Paneles */
	.panel-areas, .panel-agrupaciones {
		background: white;
		border-radius: 12px;
		box-shadow: 0 2px 15px rgba(0,0,0,0.1);
		overflow: hidden;
	}

	.panel-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 20px 25px;
		text-align: center;
	}

	.panel-header h2 {
		margin: 0;
		font-size: 1.4rem;
		font-weight: 600;
	}

	/* Filtros */
	.filtros-container {
		padding: 20px 25px;
		background: #f8f9fa;
		border-bottom: 1px solid #dee2e6;
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 15px;
	}

	.filtro-group {
		flex: 1;
		min-width: 250px;
	}

	.filtro-group label {
		display: block;
		font-weight: 600;
		margin-bottom: 5px;
		color: #555;
		font-size: 0.9rem;
	}

	.input-busqueda {
		width: 100%;
		padding: 10px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.3s ease;
	}

	.input-busqueda:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.filtro-actions {
		display: flex;
		gap: 10px;
	}

	.btn-limpiar {
		padding: 10px 20px;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.3s ease;
	}

	.btn-limpiar:hover {
		background: #5a6268;
		transform: translateY(-1px);
	}

	/* Tablas */
	.table-container {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		background: white;
	}

	thead {
		background: #f8f9fa;
	}

	th {
		padding: 15px 20px;
		text-align: left;
		font-weight: 600;
		color: #495057;
		border-bottom: 2px solid #dee2e6;
		font-size: 0.9rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	td {
		padding: 15px 20px;
		border-bottom: 1px solid #f1f3f4;
		vertical-align: middle;
	}

	tbody tr {
		transition: all 0.3s ease;
	}

	tbody tr:hover {
		background-color: #f8f9fa;
		transform: scale(1.01);
	}

	/* Badges */
	.badge {
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.badge-success {
		background: #d4edda;
		color: #155724;
	}

	.badge-inactive {
		background: #f8d7da;
		color: #721c24;
	}

	.badge-info {
		background: #d1ecf1;
		color: #0c5460;
	}

	/* Acciones en tabla */
	.actions {
		display: flex;
		gap: 8px;
		align-items: center;
	}

	.btn-icon, .btn-icon-danger {
		padding: 8px 12px;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 14px;
		transition: all 0.3s ease;
		background: #f8f9fa;
		color: #495057;
	}

	.btn-icon:hover {
		background: #e9ecef;
		transform: translateY(-2px);
	}

	.btn-icon-danger {
		background: #f8d7da;
		color: #721c24;
	}

	.btn-icon-danger:hover {
		background: #f5c6cb;
		transform: translateY(-2px);
	}

	/* Información de agrupación */
	.agrupacion-info {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.color-indicator {
		width: 20px;
		height: 20px;
		border-radius: 50%;
		border: 2px solid white;
		box-shadow: 0 0 0 1px #ddd;
	}

	/* Enlaces */
	.btn-link {
		background: none;
		border: none;
		color: #3498db;
		cursor: pointer;
		text-decoration: underline;
		font-size: 0.9rem;
	}

	.btn-link:hover {
		color: #2980b9;
	}

	/* Los estilos de modales se han movido a componentes individuales */

	/* Responsividad para nueva estructura */
	._modal-placeholder {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(5px);
	}

	.modal-content {
		background: white;
		border-radius: 12px;
		width: 90%;
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: modalSlide 0.3s ease-out;
	}

	.delete-modal {
		max-width: 450px;
	}

	@keyframes modalSlide {
		from {
			opacity: 0;
			transform: translateY(-50px) scale(0.9);
		}
		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	.modal-header {
		padding: 20px 25px;
		border-bottom: 1px solid #e9ecef;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.delete-header {
		background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
	}

	.modal-header h2 {
		margin: 0;
		font-size: 1.3rem;
		font-weight: 600;
	}

	.modal-close {
		background: none;
		border: none;
		color: white;
		font-size: 24px;
		cursor: pointer;
		padding: 0;
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		transition: all 0.3s ease;
	}

	.modal-close:hover {
		background: rgba(255, 255, 255, 0.2);
	}

	.modal-body {
		padding: 25px;
	}

	.modal-footer {
		padding: 20px 25px;
		border-top: 1px solid #e9ecef;
		display: flex;
		justify-content: flex-end;
		gap: 10px;
		background: #f8f9fa;
	}

	/* Formularios en modales */
	.form-group {
		margin-bottom: 20px;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 600;
		color: #495057;
	}

	.form-group input,
	.form-group textarea {
		width: 100%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.form-group input:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
		align-items: end;
	}

	.color-picker {
		height: 45px;
		cursor: pointer;
		border-radius: 8px !important;
	}

	.checkbox-group {
		display: flex;
		align-items: center;
		margin: 15px 0;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		cursor: pointer;
		font-weight: 600;
		color: #495057;
	}

	.checkbox-label input[type="checkbox"] {
		display: none;
	}

	.checkbox-custom {
		width: 20px;
		height: 20px;
		border: 2px solid #ddd;
		border-radius: 4px;
		margin-right: 10px;
		position: relative;
		transition: all 0.3s ease;
	}

	.checkbox-label input:checked + .checkbox-custom {
		background: #3498db;
		border-color: #3498db;
	}

	.checkbox-label input:checked + .checkbox-custom::after {
		content: '✓';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: white;
		font-weight: bold;
		font-size: 12px;
	}

	/* Botones de modal */
	.btn-cancel, .btn-save, .btn-delete {
		padding: 12px 24px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 14px;
	}

	.btn-cancel {
		background: #6c757d;
		color: white;
	}

	.btn-cancel:hover {
		background: #5a6268;
		transform: translateY(-2px);
	}

	.btn-save {
		background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
		color: white;
	}

	.btn-save:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
	}

	.btn-delete {
		background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
		color: white;
	}

	.btn-delete:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
	}

	.btn-save:disabled,
	.btn-delete:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	/* Alerta de eliminación */
	.delete-warning {
		display: flex;
		align-items: flex-start;
		gap: 15px;
	}

	.warning-icon {
		font-size: 2rem;
		color: #f39c12;
	}

	.warning-text {
		flex: 1;
	}

	.item-info {
		background: #f8f9fa;
		padding: 10px 15px;
		border-radius: 6px;
		margin: 10px 0;
		border-left: 4px solid #3498db;
	}

	.agents-warning {
		background: #fff3cd;
		color: #856404;
		padding: 8px 12px;
		border-radius: 4px;
		margin-top: 5px;
		font-size: 0.9rem;
	}

	.action-warning {
		color: #e74c3c;
		font-weight: 600;
		margin: 10px 0 0 0;
		font-size: 0.9rem;
	}

	/* Responsividad */
	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			gap: 20px;
			text-align: center;
		}

		.header-actions {
			justify-content: center;
		}

		.stats-container {
			grid-template-columns: repeat(2, 1fr);
		}

		.filtros-container {
			flex-direction: column;
			align-items: stretch;
		}

		.filtro-group {
			min-width: auto;
		}

		.modal-content {
			width: 95%;
			margin: 20px;
		}

		.form-row {
			grid-template-columns: 1fr;
		}

		.actions {
			flex-direction: column;
		}
	}

	@media (max-width: 480px) {
		.stats-container {
			grid-template-columns: 1fr;
		}

		.page-header h1 {
			font-size: 1.8rem;
		}

		.header-actions {
			flex-direction: column;
		}
	}
</style>
