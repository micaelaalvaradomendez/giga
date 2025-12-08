<script>
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import { rolesController } from "$lib/paneladmin/controllers";
	import { goto } from "$app/navigation";

	// Obtener referencias a los stores individuales para usar con $
	const {
		agentes,
		rolesDisponibles,
		areasDisponibles,
		loading,
		error,
		filteredAgentes,
		estadisticas,
		searchTerm,
		filtroArea,
		editingRoleId,
		selectedRoleId,
		savingRoleId,
		currentUser,
	} = rolesController;

	// Verificar autenticación al montar
	onMount(async () => {
		try {
			console.log("🚀 Iniciando controlador de roles...");
			await rolesController.init();
			console.log("✅ Controlador de roles inicializado");

			// Recargar cuando la página vuelve a ser visible
			if (browser) {
				const handleVisibilityChange = () => {
					if (document.visibilityState === "visible") {
						rolesController.init();
					}
				};

				const handleFocus = () => {
					rolesController.init();
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

	// Funciones reactivas para actualizar filtros en el controlador
	function actualizarBusqueda(event) {
		rolesController.actualizarBusqueda(event.target.value);
	}

	function actualizarFiltroArea(event) {
		rolesController.actualizarFiltroArea(event.target.value);
	}

	function limpiarFiltros() {
		rolesController.limpiarFiltros();
	}
</script>

<svelte:head>
	<title>Roles y Permisos - GIGA</title>
</svelte:head>

<div class="page-container">
	<div class="page-header">
		<h1>Gestión de Roles y Permisos</h1>
	</div>

	<div class="page-content">
		{#if $error}
			<div class="alert alert-error">
				<strong>❌ Error:</strong>
				{$error}
				<button
					class="btn-primary"
					on:click={() => rolesController.cargarDatos()}
				>
					Reintentar
				</button>
			</div>
		{/if}

		<!-- Controles de filtrado -->
		<div class="filtros-container">
			<div class="filtros-row">
				<div class="filtro-group">
					<label for="busqueda">🔍 Buscar agente</label>
					<input
						type="text"
						id="busqueda"
						bind:value={$searchTerm}
						on:input={actualizarBusqueda}
						placeholder="Buscar por nombre, apellido, DNI, email o legajo..."
						class="input-busqueda"
					/>
				</div>
				<div class="filtro-group">
					<label for="filtroArea">📍 Filtrar por área</label>
					<select
						id="filtroArea"
						bind:value={$filtroArea}
						on:change={actualizarFiltroArea}
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

		{#if $loading}
			<div class="loading-container">
				<div class="spinner-large"></div>
				<p>Cargando información de roles...</p>
			</div>
		{:else if $filteredAgentes.length === 0 && !$loading}
			<div class="empty-state">
				<div class="empty-icon">👥</div>
				<h3>No se encontraron agentes</h3>
				<p>
					{#if $searchTerm}
						No hay agentes que coincidan con tu búsqueda "{$searchTerm}".
					{:else}
						No hay agentes registrados en el sistema.
					{/if}
				</p>
				{#if $searchTerm}
					<button
						class="btn-primary"
						on:click={() => rolesController.limpiarBusqueda()}
					>
						Limpiar búsqueda
					</button>
				{/if}
			</div>
		{:else}
			<!-- Tabla de roles -->
			<div class="table-container">
				<table class="roles-table">
					<thead>
						<tr>
							<th>Legajo</th>
							<th>Nombre Completo</th>
							<th>DNI</th>
							<th>Categoría</th>
							<th>Área</th>
							<th>Rol Actual</th>
							<th>Acciones</th>
						</tr>
					</thead>
					<tbody>
						{#each $filteredAgentes as agente (agente.id_agente)}
							{@const rolActual =
								rolesController.obtenerRolActual(agente)}
							<tr class="agente-row">
								<td class="legajo">
									<span class="legajo-badge"
										>{agente.legajo || "N/A"}</span
									>
								</td>
								<td class="nombre">
									<div class="nombre-info">
										<strong
											>{agente.nombre}
											{agente.apellido}</strong
										>
										<small
											>{agente.email ||
												"Sin email"}</small
										>
									</div>
								</td>
								<td class="dni">
									<span class="dni-text"
										>{agente.dni || "No disponible"}</span
									>
								</td>
								<td class="categoria">
									<span class="categoria-badge">
										{agente.categoria_revista || "N/A"}
									</span>
								</td>
								<td class="area">
									<span class="area-badge">
										{agente.area_nombre ||
											rolesController.obtenerNombreArea(
												agente.area_id,
											) ||
											"Sin área"}
									</span>
								</td>
								<td class="rol">
									{#if $editingRoleId === agente.id_agente}
										<div class="rol-editor">
											<select
												class="rol-select"
												bind:value={$selectedRoleId}
												on:keydown={(e) =>
													rolesController.handleKeyPress(
														e,
														agente,
														$selectedRoleId,
													)}
												disabled={$savingRoleId ===
													agente.id_agente}
											>
												<option value=""
													>🚫 Sin rol asignado</option
												>
												{#each $rolesDisponibles as rol}
													<option value={rol.id_rol}
														>{rol.nombre}</option
													>
												{/each}
												{#if $rolesDisponibles.length === 0}
													<option disabled
														>❌ No hay roles
														cargados</option
													>
												{/if}
											</select>
											<div class="rol-actions">
												<button
													class="btn-success"
													on:click={() =>
														rolesController.guardarCambioRol(
															agente,
														)}
													disabled={$savingRoleId ===
														agente.id_agente}
												>
													{#if $savingRoleId === agente.id_agente}
														<span class="spinner-sm"
														></span>
													{:else}
														✓
													{/if}
												</button>
												<button
													class="btn-secondary"
													type="button"
													on:click={() =>
														rolesController.cancelarEdicionRol()}
													disabled={$savingRoleId ===
														agente.id_agente}
												>
													✕
												</button>
											</div>
										</div>
									{:else}
										<div class="rol-display">
											<span
												class="rol-badge {rolActual
													? 'rol-asignado'
													: 'sin-rol'}"
											>
												{rolActual
													? rolActual.nombre
													: "Sin rol asignado"}
											</span>
										</div>
									{/if}
								</td>
								<td class="acciones">
									{#if $editingRoleId !== agente.id_agente}
										{#if rolesController.puedeEditarRol(agente, $currentUser)}
											<button
												class="btn-primary"
												on:click={() =>
													rolesController.iniciarEdicionRol(
														agente.id_agente,
														rolActual?.id ||
															rolActual?.id_rol,
													)}
												disabled={$savingRoleId !==
													null}
											>
												✏️ Cambiar Rol
											</button>
										{:else}
											<span class="text-muted"
												>Tu propio rol</span
											>
										{/if}
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<style>
	.page-container {
		width: 1600px;
		margin: 0 auto;
		padding: 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.page-header {
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 40px;
		max-width: 1600px;
		border-radius: 28px;
		overflow: hidden;
		text-align: center;
		margin-bottom: 30px;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 10px 30px rgba(30, 64, 175, 0.4);
	}

	.page-header::before {
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
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: inline-block;
	}

	.page-header h1::after {
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

	.alert {
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.alert-error {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.filtros-container {
		background: white;
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		font-size: 12px;
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
		align-items: end;
	}

	.loading-container {
		text-align: center;
		padding: 4rem 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.spinner-large {
		width: 3rem;
		height: 3rem;
		border: 4px solid #e9ecef;
		border-top: 4px solid #e79043;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
		background: white;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.empty-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.empty-state h3 {
		margin: 0 0 0.5rem 0;
		color: #495057;
	}

	.empty-state p {
		color: #6c757d;
		margin-bottom: 2rem;
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

	.legajo-badge {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-weight: 600;
		font-size: 0.9rem;
	}

	.nombre-info strong {
		display: block;
		color: #2c3e50;
		margin-bottom: 0.25rem;
	}

	.nombre-info small {
		color: #6c757d;
		font-size: 0.8rem;
	}

	.dni-text {
		font-weight: 500;
		color: #495057;
		font-family: monospace;
	}

	.categoria-badge {
		color: black;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 15px;
		font-weight: 500;
	}

	.area-badge {
		background: #17a2b8;
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.85rem;
		font-weight: 500;
		display: inline-block;
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.rol-display {
		display: flex;
		align-items: center;
	}

	.rol-badge {
		padding: 0.5rem 0.75rem;
		border-radius: 6px;
		font-size: 0.85rem;
		font-weight: 500;
	}

	.rol-badge.rol-asignado {
		background: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.rol-badge.sin-rol {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.rol-editor {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.rol-select {
		padding: 0.5rem;
		border: 2px solid #e79043;
		border-radius: 4px;
		font-size: 0.85rem;
		min-width: 150px;
	}

	.rol-select:focus {
		outline: none;
		box-shadow: 0 0 0 2px rgba(231, 144, 67, 0.25);
	}

	.rol-actions {
		display: flex;
		gap: 0.25rem;
	}

	.text-muted {
		color: #6c757d;
		font-size: 0.85rem;
		font-style: italic;
	}

	.btn-primary {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		padding: 8px 12px;
		border: none;
		border-radius: 6px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 14px;
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
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

	.btn-success {
		border: none;
		border-radius: 4px;
		background: #28a745;
		color: white;
		padding: 3px 5px 3px 5px;
	}

	.btn-success:hover:not(:disabled) {
		background: #1e7e34;
	}

	.btn-secondary {
		border: none;
		border-radius: 4px;
		background: #4b4b4baf;
		color: white;
		padding: 5px 5px 5px 5px;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #3d3c3cc2;
	}

	.spinner-sm {
		width: 0.8rem;
		height: 0.8rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	/* Responsive */
	@media (max-width: 1200px) {
		.roles-table {
			font-size: 0.85rem;
		}

		.roles-table th,
		.roles-table td {
			padding: 0.75rem 0.5rem;
		}
	}

	@media (max-width: 768px) {
		.page-container {
			padding: 1rem;
		}

		.table-container {
			overflow-x: auto;
		}

		.roles-table {
			min-width: 900px;
		}

		.area-badge {
			max-width: 120px;
		}
	}

	@media (max-width: 480px) {
		.page-container {
			padding: 0.5rem;
		}
		.roles-table {
			min-width: 1000px;
		}
	}
</style>
