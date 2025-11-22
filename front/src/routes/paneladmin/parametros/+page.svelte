<script>
	import { onMount } from "svelte";
	import { parametrosController } from "$lib/paneladmin/controllers";
	import { goto } from "$app/navigation";

	// Importar componentes modales
	import ModalArea from "$lib/componentes/ModalArea.svelte";
	import ModalAgrupacion from "$lib/componentes/ModalAgrupacion.svelte";
	import ModalHorarios from "$lib/componentes/ModalHorarios.svelte";
	import ModalEliminar from "$lib/componentes/ModalEliminar.svelte";
	import ModalHorarioGlobal from "$lib/componentes/ModalHorarioGlobal.svelte";

	// Obtener referencias a los stores individuales
	const {
		areas,
		agrupaciones,
		loading,
		error,
		busquedaAreas,
		busquedaAgrupaciones,
		areasFiltradas,
		agrupacionesFiltradas,
		modalArea,
		modalAgrupacion,
		modalSchedule,
		modalDelete,
		areaForm,
		agrupacionForm,
		scheduleForm,
	} = parametrosController;

	// Validación de autenticación e inicialización
	onMount(async () => {
		try {
			console.log("🚀 Iniciando controlador de parámetros...");
			await parametrosController.init();
			console.log("✅ Controlador de parámetros inicializado");

			// Recargar cuando la página vuelve a ser visible
			if (typeof window !== "undefined") {
				const handleVisibilityChange = () => {
					if (document.visibilityState === "visible") {
						parametrosController.init();
					}
				};

				const handleFocus = () => {
					parametrosController.init();
				};

				document.addEventListener(
					"visibilitychange",
					handleVisibilityChange,
				);
				window.addEventListener("focus", handleFocus);

				return () => {
					document.removeEventListener(
						"visibilitychange",
						handleVisibilityChange,
					);
					window.removeEventListener("focus", handleFocus);
				};
			}
		} catch (err) {
			console.error("❌ Error inicializando controlador:", err);
			if (
				err.message === "Usuario no autenticado" ||
				err.message === "Sesión expirada"
			) {
				goto("/");
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

	let mensajeExito = "";
	let mensajeError = "";

	// Estado para modal de horario global
	let modalHorarioGlobal = false;
	let guardandoHorarioGlobal = false;

	function mostrarExito(mensaje) {
		mensajeExito = mensaje;
		setTimeout(() => {
			mensajeExito = "";
		}, 5000);
	}

	function mostrarError(mensaje) {
		mensajeError = mensaje;
		setTimeout(() => {
			mensajeError = "";
		}, 5000);
	}

	function abrirModalHorarioGlobal() {
		modalHorarioGlobal = true;
	}

	function cerrarModalHorarioGlobal() {
		modalHorarioGlobal = false;
		guardandoHorarioGlobal = false;
	}

	async function guardarHorarioGlobal(event) {
		const { horario_entrada, horario_salida } = event.detail;

		guardandoHorarioGlobal = true;
		try {
			const response = await fetch(
				"/api/personas/parametros/horario-global/",
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					credentials: "include",
					body: JSON.stringify({
						horario_entrada,
						horario_salida,
					}),
				},
			);

			const data = await response.json();

			if (response.ok && data.success) {
				mostrarExito(`✅ ${data.message}`);
				cerrarModalHorarioGlobal();
				await parametrosController.init(); // Recargar datos
			} else {
				mostrarError(data.message || "Error al aplicar horario global");
			}
		} catch (error) {
			console.error("Error aplicando horario global:", error);
			mostrarError("Error de conexión al aplicar horario global");
		} finally {
			guardandoHorarioGlobal = false;
		}
	}

	// Event handlers para modales
	async function actualizarHorarios() {
		try {
			const formData = $scheduleForm;
			const modalData = $modalSchedule;

			const result = await parametrosController.actualizarHorarios(
				formData,
				modalData.tipo,
				modalData.target,
			);

			if (result.success) {
				mostrarExito("✅ Horarios actualizados correctamente");
			}
		} catch (error) {
			console.error("Error actualizando horarios:", error);
			mostrarError(error.message || "Error al actualizar horarios");
		}
	}

	async function confirmarEliminar() {
		try {
			const modalData = $modalDelete;

			if (modalData.tipo === "area") {
				await parametrosController.confirmarEliminarArea(
					modalData.item.id_area,
				);
			} else if (modalData.tipo === "agrupacion") {
				await parametrosController.confirmarEliminarAgrupacion(
					modalData.item.id_agrupacion,
					modalData.nuevaAsignacion,
				);
			}
		} catch (error) {
			console.error("Error eliminando elemento:", error);
			// Manejar error - podríamos mostrar una notificación
		}
	}

	async function guardarArea() {
		try {
			await parametrosController.guardarArea($areaForm);
		} catch (error) {
			console.error("Error guardando área:", error);
			parametrosController.error.set(error.message);
		}
	}

	async function guardarAgrupacion() {
		try {
			await parametrosController.guardarAgrupacion($agrupacionForm);
		} catch (error) {
			console.error("Error guardando agrupación:", error);
			parametrosController.error.set(error.message);
		}
	}
</script>

<svelte:head>
	<title>Parámetros del Sistema - GIGA</title>
</svelte:head>

<div class="page-header">
	<div class="page-header-title">
		<h1>Parámetros del Sistema</h1>
	</div>
	<div class="header-actions">
		<button class="btn-horario-global" on:click={abrirModalHorarioGlobal}>
			🕐 Horario Global
		</button>
		<button
			class="btn-primary"
			on:click={() => parametrosController.agregarArea()}
		>
			+ Añadir Área
		</button>
		<button
			class="btn-secondary"
			on:click={() => parametrosController.agregarAgrupacion()}
		>
			+ Añadir Agrupación
		</button>
	</div>
</div>

<!-- Mensajes de éxito -->
{#if mensajeExito}
	<div class="alert alert-success">
		{mensajeExito}
		<button class="btn-close" on:click={() => (mensajeExito = "")}>×</button
		>
	</div>
{/if}

<!-- Mensajes de error -->
{#if mensajeError}
	<div class="alert alert-error">
		❌ {mensajeError}
		<button class="btn-close" on:click={() => (mensajeError = "")}>×</button
		>
	</div>
{/if}

{#if $error}
	<div class="alert alert-error">
		❌ {$error}
		<button
			class="btn-close"
			on:click={() => parametrosController.error.set(null)}>×</button
		>
	</div>
{/if}

<!-- Loading indicator -->
{#if $loading}
	<div class="loading-container">
		<div class="loading-spinner"></div>
		<p>Cargando parámetros del sistema...</p>
	</div>
{:else}
	<!-- Sección de Horario Global -->
	<div class="content-grid">
		<!-- Panel de Áreas -->
		<div class="panel-areas">
			<div class="panel-header">
				<h2>📍 Gestión de Áreas</h2>
			</div>
			<!-- Estadísticas de Áreas -->
			{#if $areasFiltradas && $areasFiltradas.length > 0}
				<div class="panel-stats">
					<div class="stat-card">
						<h3>Total Áreas</h3>
						<p class="stat-number">{$areas ? $areas.length : 0}</p>
					</div>
					<div class="stat-card">
						<h3>Áreas Activas</h3>
						<p class="stat-number">
							{$areas ? $areas.filter((a) => a.activo).length : 0}
						</p>
					</div>
				</div>
			{/if}
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
					/>
				</div>
				<div class="filtro-actions">
					<button
						class="btn-limpiar"
						on:click={() =>
							parametrosController.limpiarFiltrosAreas()}
						title="Limpiar filtros"
					>
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
										<span
											class="badge badge-{area.activo
												? 'success'
												: 'inactive'}"
										>
											{area.activo
												? "Activa"
												: "Inactiva"}
										</span>
									</td>
									<td class="actions">
										<button
											class="btn-icon"
											title="Editar"
											on:click={() =>
												parametrosController.editarArea(
													area,
												)}>✏️</button
										>
										<button
											class="btn-icon"
											title="Horarios"
											on:click={() =>
												parametrosController.gestionarHorarios(
													"area",
													area,
												)}>🕒</button
										>
										<button
											class="btn-icon-danger"
											title="Eliminar"
											on:click={() =>
												parametrosController.eliminarArea(
													area,
												)}>🗑️</button
										>
									</td>
								</tr>
							{/each}
						{:else}
							<tr>
								<td
									colspan="3"
									style="text-align: center; padding: 2rem;"
								>
									{#if busquedaAreas}
										No se encontraron áreas que coincidan
										con la búsqueda.
										<br /><button
											class="btn-link"
											on:click={() =>
												parametrosController.limpiarFiltrosAreas()}
											>Limpiar filtros</button
										>
									{:else}
										No hay áreas registradas.
										<br /><button
											class="btn-link"
											on:click={() =>
												parametrosController.agregarArea()}
											>Crear primera área</button
										>
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

			<!-- Estadísticas de Agrupaciones -->
			{#if $agrupacionesFiltradas && $agrupacionesFiltradas.length > 0}
				<div class="panel-stats">
					<div class="stat-card">
						<h3>Total Agrupaciones</h3>
						<p class="stat-number">
							{$agrupaciones ? $agrupaciones.length : 0}
						</p>
					</div>
					<div class="stat-card">
						<h3>Agentes en Agrupaciones</h3>
						<p class="stat-number">
							{$agrupaciones
								? $agrupaciones.reduce(
										(sum, a) =>
											sum + (a.total_agentes || 0),
										0,
									)
								: 0}
						</p>
					</div>
				</div>
			{/if}

			<!-- Filtros de agrupaciones -->
			<div class="filtros-container">
				<div class="filtro-group">
					<label for="busquedaAgrupaciones"
						>🔍 Buscar agrupaciones</label
					>
					<input
						type="text"
						id="busquedaAgrupaciones"
						bind:value={$busquedaAgrupaciones}
						placeholder="Buscar por nombre..."
						class="input-busqueda"
					/>
				</div>
				<div class="filtro-actions">
					<button
						class="btn-limpiar"
						on:click={() =>
							parametrosController.limpiarFiltrosAgrupaciones()}
						title="Limpiar filtros"
					>
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
									<td
										>{agrupacion.descripcion ||
											"Sin descripción"}</td
									>
									<td>
										<span class="badge badge-info">
											{agrupacion.total_agentes} agentes
										</span>
									</td>
									<td>
										<span
											class="badge badge-{agrupacion.activo
												? 'success'
												: 'inactive'}"
										>
											{agrupacion.activo
												? "Activa"
												: "Inactiva"}
										</span>
									</td>
									<td class="actions">
										<button
											class="btn-icon"
											title="Editar"
											on:click={() =>
												parametrosController.editarAgrupacion(
													agrupacion,
												)}>✏️</button
										>
										<button
											class="btn-icon"
											title="Horarios"
											on:click={() =>
												parametrosController.gestionarHorarios(
													"agrupacion",
													agrupacion,
												)}>🕒</button
										>
										<button
											class="btn-icon-danger"
											title="Eliminar"
											on:click={() =>
												parametrosController.eliminarAgrupacion(
													agrupacion,
												)}>🗑️</button
										>
									</td>
								</tr>
							{/each}
						{:else}
							<tr>
								<td
									colspan="5"
									style="text-align: center; padding: 2rem;"
								>
									{#if busquedaAgrupaciones}
										No se encontraron agrupaciones que
										coincidan con la búsqueda.
										<br /><button
											class="btn-link"
											on:click={() =>
												parametrosController.limpiarFiltrosAgrupaciones()}
											>Limpiar filtros</button
										>
									{:else}
										No hay agrupaciones registradas.
										<br /><button
											class="btn-link"
											on:click={() =>
												parametrosController.agregarAgrupacion()}
											>Crear primera agrupación</button
										>
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
	on:cerrar={() =>
		parametrosController.modalArea.update((m) => ({ ...m, isOpen: false }))}
/>

<ModalAgrupacion
	isOpen={$modalAgrupacion.isOpen}
	isSaving={$modalAgrupacion.isSaving}
	formData={$agrupacionForm}
	on:guardar={guardarAgrupacion}
	on:cerrar={() =>
		parametrosController.modalAgrupacion.update((m) => ({
			...m,
			isOpen: false,
		}))}
/>

<ModalHorarios
	isOpen={$modalSchedule.isOpen}
	isSaving={$modalSchedule.isSaving}
	tipoHorarios={$modalSchedule.tipo}
	selectedItem={$modalSchedule.target}
	formData={$scheduleForm}
	on:guardar={(event) => {
		const { horario_entrada, horario_salida, tipo, target } = event.detail;
		parametrosController.actualizarHorarios(
			{ horario_entrada, horario_salida },
			tipo,
			target,
		);
	}}
	on:cerrar={() =>
		parametrosController.modalSchedule.update((m) => ({
			...m,
			isOpen: false,
		}))}
/>

<ModalEliminar
	isOpen={$modalDelete.isOpen}
	isDeleting={$modalDelete.isDeleting}
	itemToDelete={$modalDelete.item}
	type={$modalDelete.tipo}
	on:confirmar={confirmarEliminar}
	on:cerrar={() =>
		parametrosController.modalDelete.update((m) => ({
			...m,
			isOpen: false,
		}))}
/>

<ModalHorarioGlobal
	isOpen={modalHorarioGlobal}
	isSaving={guardandoHorarioGlobal}
	on:guardar={guardarHorarioGlobal}
	on:cerrar={cerrarModalHorarioGlobal}
/>

<style>
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
		padding-bottom: 20px;
	}

	.page-header-title {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 40px;
		margin: 0;
		max-width: 1000px;
		border-radius: 28px;
		overflow: hidden;
		text-align: center;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
	}

	.page-header-title::before {
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

	.page-header-title h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 30px;
		letter-spacing: 0.2px;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: inline-block;
	}

	.page-header-title h1::after {
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

	.header-actions {
		display: flex;
		gap: 10px;
	}

	.btn-primary,
	.btn-secondary,
	.btn-horario-global {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		padding: 16px 32px;
		border: none;
		border-radius: 10px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 10px;
		font-size: 16px;
	}

	.btn-horario-global {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
		margin-left: 10px;
	}

	.btn-horario-global:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
	}

	.btn-primary {
		background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
		color: white;
	}

	.btn-primary:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
	}

	.btn-secondary {
		background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
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
		animation: slideIn 0.3s ease-out;
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(-20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.alert-success {
		background: #e8f5e9;
		color: #2e7d32;
		border-left: 4px solid #4caf50;
	}

	.alert-error {
		background: #ffebee;
		color: #c62828;
		border-left: 4px solid #f44336;
	}

	.btn-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		opacity: 0.6;
		transition: opacity 0.2s;
	}

	.btn-close:hover {
		opacity: 1;
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
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
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

	.panel-stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 20px;
		padding: 20px 25px;
		background: #f8f9fa;
		border-bottom: 1px solid #dee2e6;
	}

	.stat-card {
		background: white;
		padding: 20px;
		border-radius: 16px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
		font-size: 2.2rem;
		font-weight: 700;
		color: #3498db;
		margin: 0;
	}

	/* Paneles */
	.panel-areas,
	.panel-agrupaciones {
		background: white;
		border-radius: 24px;
		box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
		overflow: hidden;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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
		align-items: flex-end;
		flex-wrap: wrap;
		gap: 15px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.filtro-group {
		flex: 1 1 250px;
		min-width: 200px;
		max-width: 100%;
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
		box-sizing: border-box;
	}

	.input-busqueda:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.filtro-actions {
		display: flex;
		gap: 10px;
		flex-shrink: 0;
		align-self: flex-end;
	}

	.btn-limpiar {
		padding: 10px 25px;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.3s ease;
		white-space: nowrap;
		height: 42px;
	}

	.btn-limpiar:hover {
		background: #5a6268;
		transform: translateY(-1px);
	}

	/* Tablas */
	.table-container {
		overflow-x: auto;
		max-height: 500px;
		overflow-y: auto;
		position: relative;
		border-radius: 0 0 24px 24px;
	}

	.table-container::-webkit-scrollbar {
		width: 8px;
		height: 8px;
	}

	.table-container::-webkit-scrollbar-track {
		background: #f1f3f4;
		border-radius: 10px;
	}

	.table-container::-webkit-scrollbar-thumb {
		background: #c1c7cd;
		border-radius: 10px;
		transition: background 0.3s ease;
	}

	.table-container::-webkit-scrollbar-thumb:hover {
		background: #a8aeb4;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		background: white;
	}

	thead {
		background: #f8f9fa;
		position: sticky;
		top: 0;
		z-index: 10;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
		background: #f8f9fa;
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

	.panel-areas .table-container {
		max-height: 450px;
	}

	.panel-agrupaciones .table-container {
		max-height: 450px;
	}

	/* Badges */
	.badge {
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		white-space: nowrap;
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

	.btn-icon,
	.btn-icon-danger {
		padding: 8px 12px;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 14px;
		transition: all 0.3s ease;
		background: #68686836;
	}

	.btn-icon:hover {
		background: #68686836;
		transform: translateY(-3px);
	}

	.btn-icon-danger {
		background: #da414eb7;
	}

	.btn-icon-danger:hover {
		background: #ff001994;
		transform: translateY(-3px);
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

	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			gap: 20px;
			text-align: center;
		}

		.header-actions {
			justify-content: center;
		}

		.filtros-container {
			flex-direction: column;
			align-items: stretch;
		}

		.filtro-group {
			min-width: auto;
			flex: 1 1 auto;
		}

		.filtro-actions {
			width: 100%;
			justify-content: stretch;
		}

		.btn-limpiar {
			flex: 1;
		}

		.actions {
			flex-direction: column;
		}

		.table-container {
			max-height: 400px;
		}
	}

	@media (max-width: 480px) {
		.page-header h1 {
			font-size: 1.8rem;
		}

		.header-actions {
			flex-direction: column;
		}

		.filtros-container {
			padding: 15px;
		}
	}
</style>
