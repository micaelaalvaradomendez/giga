<script>
	import { onMount } from 'svelte';
	import { personasService } from '$lib/services.js';
	import AuthService from '$lib/login/authService.js';
	import { goto } from '$app/navigation';

	let agentes = [];
	let rolesDisponibles = [];
	let loading = true;
	let error = null;
	let searchTerm = '';
	let filteredAgentes = [];
	let editingRoleId = null;
	let savingRoleId = null;
	let currentUser = null;

	// Verificar autenticación al montar
	onMount(async () => {
		if (!AuthService.isAuthenticated()) {
			goto('/');
			return;
		}
		currentUser = AuthService.getCurrentUser();
		await cargarDatos();
	});

	async function cargarDatos() {
		try {
			loading = true;
			error = null;
			
			// Cargar agentes y roles en paralelo
			const [agentesResponse, rolesResponse] = await Promise.all([
				personasService.getAgentes(),
				personasService.getRoles()
			]);

			agentes = agentesResponse.data.results || [];
			rolesDisponibles = rolesResponse.data.results || [];
			filteredAgentes = [...agentes];
		} catch (err) {
			console.error('Error cargando datos:', err);
			error = 'Error al cargar los datos. Por favor, intenta nuevamente.';
		} finally {
			loading = false;
		}
	}

	// Filtrar agentes por término de búsqueda
	$: {
		if (searchTerm.trim()) {
			const term = searchTerm.toLowerCase();
			filteredAgentes = agentes.filter(agente => 
				agente.nombre?.toLowerCase().includes(term) ||
				agente.apellido?.toLowerCase().includes(term) ||
				agente.legajo?.toLowerCase().includes(term) ||
				agente.usuario?.cuil?.includes(term) ||
				agente.categoria_revista?.toLowerCase().includes(term)
			);
		} else {
			filteredAgentes = [...agentes];
		}
	}

	function obtenerRolActual(agente) {
		if (agente.roles && agente.roles.length > 0) {
			return agente.roles[0];
		}
		return null;
	}

	function obtenerNombreRol(rolId) {
		if (!rolId) return 'Sin rol asignado';
		const rol = rolesDisponibles.find(r => r.id === rolId);
		return rol ? rol.nombre : 'Rol desconocido';
	}

	function iniciarEdicionRol(agenteId) {
		editingRoleId = agenteId;
	}

	function cancelarEdicionRol() {
		editingRoleId = null;
	}

	function puedeEditarRol(agente) {
		// No permitir que el usuario se cambie el rol a sí mismo
		if (!currentUser || !agente.usuario) return true;
		
		return currentUser.id !== agente.usuario.id && 
		       currentUser.email !== agente.email && 
		       currentUser.email !== agente.usuario.email;
	}

	async function guardarCambioRol(agente, nuevoRolId) {
		if (!nuevoRolId) {
			alert('Por favor, selecciona un rol válido.');
			return;
		}

		// Verificar que no se esté cambiando el rol a sí mismo
		if (!puedeEditarRol(agente)) {
			alert('⚠️ No puedes cambiar tu propio rol. Solicita a otro administrador que realice esta acción.');
			editingRoleId = null;
			return;
		}

		try {
			savingRoleId = agente.id;
			
			// Primero obtener asignaciones actuales
			const asignacionesResponse = await personasService.getAsignaciones();
			const asignaciones = asignacionesResponse.data.results || [];
			const asignacionActual = asignaciones.find(a => a.usuario === agente.usuario.id);
			
			// Si ya tiene una asignación, eliminarla primero
			if (asignacionActual) {
				await personasService.deleteAsignacion(asignacionActual.id);
			}
			
			// Crear nueva asignación de rol
			const asignacionData = {
				usuario: agente.usuario.id,
				rol: parseInt(nuevoRolId),
				area: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' // Área por defecto: Secretaría de Protección Civil
			};

			console.log('Datos de asignación a enviar:', asignacionData);
			await personasService.createAsignacion(asignacionData);
			
			// Recargar datos para mostrar el cambio
			await cargarDatos();
			editingRoleId = null;
			alert('✅ Rol actualizado correctamente');
		} catch (err) {
			console.error('Error al cambiar rol:', err);
			console.error('Respuesta del error:', err.response?.data);
			
			let errorMessage = 'Error al cambiar el rol: ';
			
			if (err.response?.status === 400) {
				const errorData = err.response.data;
				if (errorData) {
					console.error('Detalles del error 400:', errorData);
					// Mostrar errores específicos de campo
					if (errorData.usuario) errorMessage += `Usuario: ${errorData.usuario[0]}. `;
					if (errorData.rol) errorMessage += `Rol: ${errorData.rol[0]}. `;
					if (errorData.area) errorMessage += `Área: ${errorData.area[0]}. `;
					if (errorData.non_field_errors) errorMessage += `${errorData.non_field_errors[0]}. `;
				}
				if (errorMessage === 'Error al cambiar el rol: ') {
					errorMessage += 'Datos inválidos. Verifique la información.';
				}
			} else if (err.response?.status === 403) {
				errorMessage += 'No tienes permisos para realizar esta acción.';
			} else if (err.response?.status === 404) {
				errorMessage += 'Usuario o rol no encontrado.';
			} else {
				errorMessage += (err.response?.data?.message || err.message || 'Error desconocido.');
			}
			
			alert(errorMessage);
		} finally {
			savingRoleId = null;
		}
	}

	function handleKeyPress(event, agente, nuevoRolId) {
		if (event.key === 'Enter') {
			guardarCambioRol(agente, nuevoRolId);
		} else if (event.key === 'Escape') {
			cancelarEdicionRol();
		}
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
				<p>Administra los roles y permisos de los usuarios del sistema</p>
			</div>
			<div class="header-actions">
				<button class="btn btn-secondary" on:click={cargarDatos} disabled={loading}>
					{#if loading}
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
		{#if error}
			<div class="alert alert-error">
				<strong>❌ Error:</strong> {error}
				<button class="btn btn-sm btn-primary" on:click={cargarDatos}>
					Reintentar
				</button>
			</div>
		{/if}

		<!-- Filtros y búsqueda -->
		<div class="filters-section">
			<div class="search-box">
				<input
					type="text"
					placeholder="🔍 Buscar por nombre, apellido, legajo, CUIL o categoría..."
					bind:value={searchTerm}
					class="search-input"
				/>
				<span class="search-results">
					{filteredAgentes.length} de {agentes.length} agentes
				</span>
			</div>
		</div>

		{#if loading}
			<div class="loading-container">
				<div class="spinner-large"></div>
				<p>Cargando información de roles...</p>
			</div>
		{:else if filteredAgentes.length === 0 && !loading}
			<div class="empty-state">
				<div class="empty-icon">👥</div>
				<h3>No se encontraron agentes</h3>
				<p>
					{#if searchTerm}
						No hay agentes que coincidan con tu búsqueda "{searchTerm}".
					{:else}
						No hay agentes registrados en el sistema.
					{/if}
				</p>
				{#if searchTerm}
					<button class="btn btn-primary" on:click={() => searchTerm = ''}>
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
							<th>CUIL</th>
							<th>Categoría</th>
							<th>Rol Actual</th>
							<th>Acciones</th>
						</tr>
					</thead>
					<tbody>
						{#each filteredAgentes as agente (agente.id)}
							{@const rolActual = obtenerRolActual(agente)}
							<tr class="agente-row">
								<td class="legajo">
									<span class="legajo-badge">{agente.legajo || 'N/A'}</span>
								</td>
								<td class="nombre">
									<div class="nombre-info">
										<strong>{agente.nombre} {agente.apellido}</strong>
										<small>{agente.usuario?.email || 'Sin email'}</small>
									</div>
								</td>
								<td class="cuil">
									{agente.usuario?.cuil || 'No disponible'}
								</td>
								<td class="categoria">
									<span class="categoria-badge">
										{agente.categoria_revista || 'N/A'}
									</span>
								</td>
								<td class="rol">
									{#if editingRoleId === agente.id}
										<div class="rol-editor">
											<select 
												class="rol-select" 
												value={rolActual?.id || ''}
												on:keydown={(e) => handleKeyPress(e, agente, e.target.value)}
												disabled={savingRoleId === agente.id}
											>
												<option value="">Sin rol</option>
												{#each rolesDisponibles as rol}
													<option value={rol.id}>{rol.nombre}</option>
												{/each}
											</select>
											<div class="rol-actions">
												<button 
													class="btn btn-sm btn-success"
													on:click={(e) => {
														const select = e.target.closest('.rol-editor').querySelector('.rol-select');
														guardarCambioRol(agente, select.value);
													}}
													disabled={savingRoleId === agente.id}
												>
													{#if savingRoleId === agente.id}
														<span class="spinner-sm"></span>
													{:else}
														✓
													{/if}
												</button>
												<button 
													class="btn btn-sm btn-secondary"
													on:click={cancelarEdicionRol}
													disabled={savingRoleId === agente.id}
												>
													✕
												</button>
											</div>
										</div>
									{:else}
										<div class="rol-display">
											<span class="rol-badge {rolActual ? 'rol-asignado' : 'sin-rol'}">
												{obtenerNombreRol(rolActual?.id)}
											</span>
										</div>
									{/if}
								</td>
								<td class="acciones">
									{#if editingRoleId !== agente.id}
										{#if puedeEditarRol(agente)}
											<button 
												class="btn btn-sm btn-primary"
												on:click={() => iniciarEdicionRol(agente.id)}
												disabled={savingRoleId !== null}
											>
												✏️ Cambiar Rol
											</button>
										{:else}
											<span class="text-muted">Tu propio rol</span>
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

	.header-title p {
		margin: 0;
		color: #6c757d;
		font-size: 1.1rem;
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
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		margin-bottom: 2rem;
	}

	.search-box {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.search-input {
		flex: 1;
		padding: 0.75rem 1rem;
		border: 2px solid #e9ecef;
		border-radius: 8px;
		font-size: 1rem;
		transition: border-color 0.2s;
	}

	.search-input:focus {
		outline: none;
		border-color: #e79043;
		box-shadow: 0 0 0 3px rgba(231, 144, 67, 0.1);
	}

	.search-results {
		color: #6c757d;
		font-size: 0.9rem;
		white-space: nowrap;
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
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

	.categoria-badge {
		background: #6c757d;
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.85rem;
		font-weight: 500;
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

	.spinner, .spinner-sm {
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
	}

	@media (max-width: 768px) {
		.page-container {
			padding: 1rem;
		}
		
		.header-content {
			flex-direction: column;
			align-items: stretch;
		}
		
		.search-box {
			flex-direction: column;
			align-items: stretch;
			gap: 0.5rem;
		}
		
		.table-container {
			overflow-x: auto;
		}
		
		.roles-table {
			min-width: 800px;
		}
	}
</style>