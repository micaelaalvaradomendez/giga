<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { usuariosController } from "$lib/paneladmin/controllers";
	import ModalVerAgente from "$lib/componentes/ModalVerAgente.svelte";
	import ModalEditarAgente from "$lib/componentes/ModalEditarAgente.svelte";
	import ModalEliminarAgente from "$lib/componentes/ModalEliminarAgente.svelte";
	import ModalAgregarAgente from "$lib/componentes/ModalAgregarAgente.svelte";

	/** @type {import('./$types').PageData} */

	// Obtener referencias a los stores individuales
	const {
		agentes,
		agentesFiltrados,
		areasDisponibles,
		rolesDisponibles,
		loading,
		error,
		estadisticas,
		busqueda,
		filtroArea,
		modalVerAgente,
		modalEditarAgente,
		modalEliminarAgente,
		modalAgregarAgente,
	} = usuariosController;

	// Funciones para abrir modales (delegadas al controlador)
	function verAgente(agente) {
		usuariosController.verAgente(agente);
	}

	function editarAgente(agente) {
		usuariosController.editarAgente(agente);
	}

	function eliminarAgente(agente) {
		usuariosController.eliminarAgente(agente);
	}

	function agregarAgente() {
		usuariosController.agregarAgente();
	}

	// Función para limpiar filtros (delegada al controlador)
	function limpiarFiltros() {
		usuariosController.limpiarFiltros();
	}

	// Los filtros ahora usan bind:value directamente con los stores

	// Verificar autenticación y cargar datos al montar el componente
	onMount(async () => {
		console.log("🔄 Componente montado, iniciando controlador...");
		try {
			await usuariosController.init();
			console.log("✅ Controlador inicializado exitosamente");
		} catch (err) {
			console.error("❌ Error inicializando controlador:", err);
			if (err.message === "Usuario no autenticado") {
				goto("/");
				return;
			}
		}
	});

	// Función para cerrar modales (delegada al controlador)
	function cerrarModales() {
		usuariosController.cerrarModales();
	}

	// Función para guardar cambios del agente (delegada al controlador)
	async function guardarCambiosAgente(event) {
		const { agente, formData } = event.detail;

		try {
			const result = await usuariosController.guardarCambiosAgente(
				agente,
				formData,
			);
			if (result.success) {
				alert(result.message);
			}
		} catch (error) {
			alert(error.message);
		}
	}

	// Función para confirmar eliminación (delegada al controlador)
	async function confirmarEliminacionAgente(event) {
		const { agente } = event.detail;

		try {
			const result =
				await usuariosController.confirmarEliminacionAgente(agente);
			if (result.success) {
				alert(result.message);
			}
		} catch (error) {
			alert(error.message);
		}
	}

	// Función para crear nuevo agente (delegada al controlador)
	async function crearNuevoAgente(event) {
		const { formData } = event.detail;

		try {
			const result = await usuariosController.crearNuevoAgente(formData);
			if (result.success) {
				alert(result.message);
			}
		} catch (error) {
			alert(error.message);
		}
	}
</script>

<div class="logo">
	<a href="/paneladmin">Panel de Administración</a>
</div>

<div class="page-header">
	<div class="page-header-title">
		<h1>Gestión de Agentes</h1>
	</div>
	<button class="btn-primary" on:click={agregarAgente}>
		+ Añadir Agente
	</button>
</div>

<!-- Controles de filtrado -->
<div class="filtros-container">
	<div class="filtros-row">
		<div class="filtro-group">
			<label for="busqueda">🔍 Buscar agente</label>
			<input
				type="text"
				id="busqueda"
				bind:value={$busqueda}
				placeholder="Buscar por nombre, apellido, DNI, email o legajo..."
				class="input-busqueda"
			/>
		</div>
		<div class="filtro-group">
			<label for="filtroArea">📍 Filtrar por área</label>
			<select
				id="filtroArea"
				bind:value={$filtroArea}
				class="select-area"
			>
				<option value=""
					>Todas las áreas ({$areasDisponibles.length})</option
				>
				{#each $areasDisponibles as area}
					<option value={area.id_area}>{area.nombre}</option>
				{/each}
				{#if $areasDisponibles.length === 0}
					<option disabled>❌ No hay áreas cargadas</option>
				{/if}
			</select>
		</div>
		<div class="filtro-actions">
			<button
				class="btn-limpiar"
				on:click={limpiarFiltros}
				title="Limpiar filtros"
			>
				🗑️ Limpiar
			</button>
		</div>
	</div>
</div>

<div class="table-container">
	<table>
		<thead>
			<tr>
				<th>Legajo</th>
				<th>Nombre Completo</th>
				<th>DNI</th>
				<th>Categoría</th>
				<th>Área</th>
				<th>Rol</th>
				<th>Acciones</th>
			</tr>
		</thead>
		<tbody>
			{#if $agentesFiltrados && $agentesFiltrados.length > 0}
				{#each $agentesFiltrados as agente}
					{@const currentUser = usuariosController.getCurrentUser()}
					<tr
						class={usuariosController.isCurrentUser(agente)
							? "current-user"
							: ""}
					>
						<td><strong>{agente.legajo || "N/A"}</strong></td>
						<td>
							<strong>{agente.nombre} {agente.apellido}</strong>
							{#if usuariosController.isCurrentUser(agente)}
								<span class="badge badge-current-user">Tú</span>
							{/if}
						</td>
						<td>{agente.dni}</td>
						<td>{agente.categoria_revista || "N/A"}</td>
						<td>
							{#if agente.area_nombre}
								<span class="badge badge-area"
									>{agente.area_nombre}</span
								>
							{:else if agente.agrupacion_display}
								<span
									class="badge badge-{agente.agrupacion?.toLowerCase()}"
									>{agente.agrupacion_display}</span
								>
							{:else}
								<span class="badge badge-sin-area"
									>Sin área</span
								>
							{/if}
						</td>
						<td>
							{#if agente.roles && agente.roles.length > 0}
								<span class="badge badge-role"
									>{agente.roles[0].nombre}</span
								>
								{#if agente.roles.length > 1}
									<span class="badge badge-secondary"
										>+{agente.roles.length - 1}</span
									>
								{/if}
							{:else}
								<span class="badge badge-sin-rol">Sin rol</span>
							{/if}
						</td>
						<td class="actions">
							<button
								class="btn-icon"
								title="Editar"
								on:click={() => editarAgente(agente)}>✏️</button
							>
							<button
								class="btn-icon"
								title="Ver detalles"
								on:click={() => verAgente(agente)}>👁️</button
							>
							{#if usuariosController.isCurrentUser(agente)}
								<button
									class="btn-icon-disabled"
									title="No puedes eliminarte a ti mismo"
									disabled>🔒</button
								>
							{:else}
								<button
									class="btn-icon-danger"
									title="Eliminar"
									on:click={() => eliminarAgente(agente)}
									>🗑️</button
								>
							{/if}
						</td>
					</tr>
				{/each}
			{:else}
				<tr>
					<td colspan="7" style="text-align: center; padding: 2rem;">
						{#if $busqueda || $filtroArea}
							No se encontraron agentes que coincidan con los
							filtros aplicados.
							<br /><button
								class="btn-link"
								on:click={limpiarFiltros}
								>Limpiar filtros</button
							>
						{:else}
							No se encontraron agentes. Total: {$agentes
								? $agentes.length
								: "undefined"}
						{/if}
					</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>

<!-- Modales -->
<ModalVerAgente
	bind:isOpen={$modalVerAgente.isOpen}
	agente={$modalVerAgente.agente}
	on:cerrar={cerrarModales}
/>

<ModalEditarAgente
	bind:isOpen={$modalEditarAgente.isOpen}
	agente={$modalEditarAgente.agente}
	bind:isSaving={$modalEditarAgente.isSaving}
	areasDisponibles={$areasDisponibles}
	rolesDisponibles={$rolesDisponibles}
	on:cerrar={cerrarModales}
	on:guardar={guardarCambiosAgente}
/>

<ModalEliminarAgente
	bind:isOpen={$modalEliminarAgente.isOpen}
	agente={$modalEliminarAgente.agente}
	bind:isDeleting={$modalEliminarAgente.isDeleting}
	on:cerrar={cerrarModales}
	on:confirmar={confirmarEliminacionAgente}
/>

<ModalAgregarAgente
	bind:isOpen={$modalAgregarAgente.isOpen}
	bind:isSaving={$modalAgregarAgente.isSaving}
	areasDisponibles={$areasDisponibles}
	rolesDisponibles={$rolesDisponibles}
	on:cerrar={cerrarModales}
	on:guardar={crearNuevoAgente}
/>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
		background-color: #f8f9fa;
		color: #212529;
	}

	:global(.admin-layout) {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	:global(.admin-header) {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 1.5rem;
		height: 70px;
		background: linear-gradient(135deg, #e79043, #f39c12);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	:global(.admin-header .logo a) {
		font-weight: bold;
		font-size: 1.3rem;
		text-decoration: none;
		color: white;
		transition: opacity 0.2s;
	}

	:global(.admin-header .logo a:hover) {
		opacity: 0.9;
	}

	:global(.admin-main) {
		display: flex;
		flex-grow: 1;
		overflow: hidden;
	}

	:global(.admin-content-full) {
		flex-grow: 1;
		padding: 2rem;
		overflow-y: auto;
		width: 100%;
		background-color: #ffffff;
		margin: 1rem;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.logo {
		display: none; /* Ocultar porque ya está en el header */
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e9ecef;
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

	.page-header h1 {
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

	/* Estilos para filtros */
	.filtros-container {
		background: white;
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.filtros-row {
		display: grid;
		grid-template-columns: 1fr auto auto;
		gap: 1rem;
		align-items: end;
		margin-bottom: 1rem;
	}

	.filtro-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.filtro-group label {
		font-weight: 500;
		color: #495057;
		font-size: 0.9rem;
	}

	.input-busqueda,
	.select-area {
		padding: 0.75rem;
		border: 1px solid #ced4da;
		border-radius: 6px;
		font-size: 0.9rem;
		transition:
			border-color 0.2s,
			box-shadow 0.2s;
		min-width: 250px;
	}

	.input-busqueda:focus,
	.select-area:focus {
		outline: none;
		border-color: #e79043;
		box-shadow: 0 0 0 2px rgba(231, 144, 67, 0.25);
	}

	.filtro-actions {
		display: flex;
		gap: 10px;
		flex-shrink: 0;
	}

	.btn-limpiar {
		padding: 10px 25px;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.3s ease;
		white-space: nowrap;
		height: 42px;
	}

	.btn-limpiar:hover {
		background: #5a6268;
		transform: translateY(-1px);
	}

	.filtros-resumen {
		padding: 0.75rem 1rem;
		background: #f8f9fa;
		border-radius: 6px;
		border-left: 4px solid #e79043;
	}

	.filtros-activos {
		color: #e79043;
		font-weight: 500;
		font-size: 0.9rem;
	}

	.filtros-inactivos {
		color: #6c757d;
		font-size: 0.9rem;
	}

	.btn-link {
		background: none;
		border: none;
		color: #e79043;
		cursor: pointer;
		text-decoration: underline;
		font-size: inherit;
		padding: 0;
		margin-top: 0.5rem;
	}

	.btn-link:hover {
		color: #d68a3b;
	}

	.btn-primary {
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
		font-size: 18px;
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		box-shadow: 0 2px 4px rgba(237, 160, 93, 0.756);
	}

	.btn-primary:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(237, 160, 93, 0.756);
	}

	.table-container {
		overflow-x: auto;
		max-height: 600px;
		overflow-y: auto;
		position: relative;
		border-radius: 24px;
		box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
		background: white;
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
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	thead {
		background: linear-gradient(135deg, #4865e9 0%, #527ab6d0 100%);
		position: sticky;
		top: 0;
		z-index: 10;
		box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
	}

	th {
		padding: 15px 20px;
		text-align: left;
		font-weight: 600;
		color: white;
		border-bottom: none;
		font-size: 0.9rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		background: transparent;
	}

	td {
		padding: 15px 20px;
		border-bottom: 1px solid #f1f3f4;
		vertical-align: middle;
		font-size: 0.95rem;
	}

	tbody tr {
		transition: all 0.3s ease;
	}

	tbody tr:hover {
		background-color: #f8f9fa;
		transform: scale(1.01);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}

	.actions {
		display: flex;
		gap: 0.5rem;
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
		background: #75757528;
	}

	.btn-icon:hover {
		background: #61616134;
		transform: translateY(-3px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.btn-icon-danger {
		background: #e46570d8;
	}

	.btn-icon-danger:hover {
		background: #be3b48;
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(220, 53, 69, 0.2);
	}

	.btn-icon-disabled {
		padding: 8px 12px;
		border: none;
		border-radius: 6px;
		font-size: 14px;
		background: #f8f9fa;
		color: #6c757d;
		cursor: not-allowed;
		opacity: 0.5;
	}

	/* Estilos para badges */
	.badge {
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		white-space: nowrap;
		display: inline-block;
	}

	.badge-area {
		background: #d1ecf1;
		color: #0c5460;
		border: 1px solid #bee5eb;
	}

	.badge-sin-area {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.badge-role {
		background: #cff4fc;
		color: #055160;
		border: 1px solid #b6effb;
	}

	.badge-sin-rol {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.badge-secondary {
		background: #6c757d;
		color: white;
		border: none;
		margin-left: 0.25rem;
		padding: 4px 8px;
	}

	.badge-current-user {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		border: none;
		margin-left: 0.5rem;
		font-size: 0.7rem;
		padding: 4px 10px;
		box-shadow: 0 2px 4px rgba(231, 144, 67, 0.3);
	}

	.badge-epu {
		background-color: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.badge-pomys {
		background-color: #d1ecf1;
		color: #0c5460;
		border: 1px solid #bee5eb;
	}

	.badge-payt {
		background-color: #fff3cd;
		color: #856404;
		border: 1px solid #ffeaa7;
	}

	.badge-jefe {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.badge-agente {
		background-color: #e2e3e5;
		color: #383d41;
		border: 1px solid #d6d8db;
	}

	.current-user {
		background-color: #fff8e1 !important;
		border-left: 4px solid #e79043;
	}

	.current-user:hover {
		background-color: #ffecb3 !important;
	}
	.roles-container {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.role-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.area-text {
		color: #6c757d;
		font-style: italic;
	}

	/* Responsive Design */
	@media (max-width: 1200px) {
		.stats-container {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}

		.stats-container {
			grid-template-columns: repeat(2, 1fr);
		}

		.filtros-row {
			grid-template-columns: 1fr;
			gap: 1rem;
		}

		.filtros-container {
			padding: 1rem;
		}

		.input-busqueda,
		.select-area {
			min-width: auto;
			width: 100%;
		}

		.filtro-actions {
			justify-content: center;
		}

		.table-container {
			overflow-x: auto;
		}

		table {
			min-width: 800px; /* Reducir ancho mínimo para móviles */
		}

		th,
		td {
			padding: 0.5rem;
			font-size: 0.875rem;
		}

		.btn-icon,
		.btn-icon-danger {
			padding: 0.5rem;
		}
	}

	@media (max-width: 480px) {
		.stats-container {
			grid-template-columns: 1fr;
		}

		.stat-card {
			padding: 0.75rem;
		}

		.stat-number {
			font-size: 1.5rem;
		}
	}

	th:nth-child(4),
	td:nth-child(4) {
		/* Email */
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	th:nth-child(6),
	td:nth-child(6) {
		/* Dirección */
		max-width: 180px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	th:nth-child(7),
	td:nth-child(7) {
		/* Agrupación */
		text-align: center;
	}

	th:nth-child(9),
	td:nth-child(9) {
		/* Roles */
		max-width: 200px;
	}
</style>
