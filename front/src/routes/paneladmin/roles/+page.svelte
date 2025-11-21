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
					if (document.visibilityState === 'visible') {
						rolesController.init();
					}
				};
				
				const handleFocus = () => {
					rolesController.init();
				};
				
				document.addEventListener('visibilitychange', handleVisibilityChange);
				window.addEventListener('focus', handleFocus);
				
				return () => {
					document.removeEventListener('visibilitychange', handleVisibilityChange);
					window.removeEventListener('focus', handleFocus);
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
		<div class="header-content">
			<div class="header-title">
				<h1>🛡️ Gestión de Roles y Permisos</h1>
			</div>
			<div class="header-actions">
				<button
					class="btn btn-secondary"
					on:click={() => rolesController.cargarDatos()}
					disabled={$loading}
				>
					{#if $loading}
						<span class="spinner"></span>
					{:else}
						🔄
					{/if}
					Actualizar
				</button>
			</div>
		</div>
	</div>

	<div class="page-content">
		{#if $error}
			<div class="alert alert-error">
				<strong>❌ Error:</strong>
				{$error}
				<button
					class="btn btn-sm btn-primary"
					on:click={() => rolesController.cargarDatos()}
				>
					Reintentar
				</button>
			</div>
		{/if}

		<!-- Filtros y búsqueda -->
		<div class="filters-section">
			<div class="filters-row">
				<div class="search-box">
					<input
						type="text"
						placeholder="🔍 Buscar por nombre, apellido, legajo, DNI, email o categoría..."
						value={$searchTerm}
						on:input={actualizarBusqueda}
						class="search-input"
					/>
				</div>
				<div class="filter-box">
					<label for="filtroArea">Filtrar por Área:</label>
					<select
						id="filtroArea"
						bind:value={$filtroArea}
						on:change={actualizarFiltroArea}
						class="filter-select"
					>
						<option value=""
							>Todas las áreas ({$areasDisponibles.length})</option
						>
						{#each $areasDisponibles as area}
							<option value={area.id_area}>{area.nombre}</option>
						{/each}
					</select>
					{#if $areasDisponibles.length === 0}
						<small style="color: red;"
							>❌ No se cargaron áreas</small
						>
					{/if}
				</div>
				<div class="filter-actions">
					<button
						class="btn btn-secondary btn-sm"
						on:click={limpiarFiltros}
					>
						🗑️ Limpiar
					</button>
				</div>
			</div>
			<div class="search-results">
				{$estadisticas.mostrados} de {$estadisticas.total} agentes
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
						class="btn btn-primary"
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
												value={rolActual?.id ||
													rolActual?.id_rol ||
													""}
												on:keydown={(e) =>
													rolesController.handleKeyPress(
														e,
														agente,
														e.target.value,
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
													class="btn btn-sm btn-success"
													on:click={(e) => {
														const select = e.target
															.closest(
																".rol-editor",
															)
															.querySelector(
																".rol-select",
															);
														rolesController.guardarCambioRol(
															agente,
															select.value,
														);
													}}
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
													class="btn btn-sm btn-secondary"
													on:click={rolesController.cancelarEdicionRol}
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
												class="btn btn-sm btn-primary"
												on:click={() =>
													rolesController.iniciarEdicionRol(
														agente.id_agente,
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
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
	}

	.page-header {
		margin-bottom: 2rem;
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 2rem;
	}

	.header-title h1 {
		margin: 0 0 0.5rem 0;
		color: #2c3e50;
		font-size: 2rem;
	}

	.header-actions {
		display: flex;
		gap: 1rem;
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

	.filters-section {
		background: white;
		padding: 1.5rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 2rem;
	}

	.filters-row {
		display: grid;
		grid-template-columns: 1fr auto auto;
		gap: 1.5rem;
		align-items: end;
		margin-bottom: 1rem;
	}

	.search-box {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.filter-box {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		min-width: 200px;
	}

	.filter-box label {
		font-size: 0.9rem;
		font-weight: 500;
		color: #495057;
	}

	.filter-actions {
		display: flex;
		align-items: end;
	}

	.search-input,
	.filter-select {
		padding: 0.75rem 1rem;
		border: 2px solid #e9ecef;
		border-radius: 8px;
		font-size: 1rem;
		transition: border-color 0.2s;
		background: white;
	}

	.search-input:focus,
	.filter-select:focus {
		outline: none;
		border-color: #e79043;
		box-shadow: 0 0 0 3px rgba(231, 144, 67, 0.1);
	}

	.search-results {
		color: #6c757d;
		font-size: 0.9rem;
		text-align: center;
		padding: 0.5rem;
		background: #f8f9fa;
		border-radius: 6px;
	}

	.loading-container {
		text-align: center;
		padding: 4rem 2rem;
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
		background: white;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		overflow: hidden;
	}

	.roles-table {
		width: 100%;
		border-collapse: collapse;
	}

	.roles-table th {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		border-bottom: none;
	}

	.roles-table td {
		padding: 1rem;
		border-bottom: 1px solid #e9ecef;
		vertical-align: middle;
	}

	.agente-row:hover {
		background: #f8f9fa;
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
		background: #6c757d;
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.85rem;
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

	.btn {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 500;
		transition: all 0.2s;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		text-decoration: none;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-sm {
		padding: 0.375rem 0.75rem;
		font-size: 0.8rem;
	}

	.btn-primary {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: linear-gradient(135deg, #d17d38, #e67e22);
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(231, 144, 67, 0.3);
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #545b62;
	}

	.btn-success {
		background: #28a745;
		color: white;
	}

	.btn-success:hover:not(:disabled) {
		background: #1e7e34;
	}

	.spinner,
	.spinner-sm {
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.spinner {
		width: 1rem;
		height: 1rem;
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

		.filters-row {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
	}

	@media (max-width: 768px) {
		.page-container {
			padding: 1rem;
		}

		.header-content {
			flex-direction: column;
			align-items: stretch;
		}

		.filters-row {
			grid-template-columns: 1fr;
			gap: 1rem;
		}

		.filter-box {
			min-width: auto;
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

		.header-title h1 {
			font-size: 1.5rem;
		}

		.roles-table {
			min-width: 1000px;
		}

		.filters-section {
			padding: 1rem;
		}
	}
</style>
