<script>
	/** @type {import('./$types').PageData} */
	export let data;
	// Los agentes vienen cargados desde +page.server.js
	const { agentes } = data;
</script>

<div class="logo">
    <a href="/admin">Panel de Administración</a>
</div>

<div class="page-header">
	<h1>Gestión de Agentes</h1>
	<button class="btn-primary">
		+ Añadir Agente
	</button>
</div>

<!-- Resumen de estadísticas -->
{#if agentes && agentes.length > 0}
<div class="stats-container">
	<div class="stat-card">
		<h3>Total Agentes</h3>
		<p class="stat-number">{agentes.length}</p>
	</div>
	<div class="stat-card">
		<h3>EPU</h3>
		<p class="stat-number">{agentes.filter(a => a.agrupacion === 'EPU').length}</p>
	</div>
	<div class="stat-card">
		<h3>POMyS</h3>
		<p class="stat-number">{agentes.filter(a => a.agrupacion === 'POMYS').length}</p>
	</div>
	<div class="stat-card">
		<h3>PAyT</h3>
		<p class="stat-number">{agentes.filter(a => a.agrupacion === 'PAYT').length}</p>
	</div>
	<div class="stat-card">
		<h3>Con Roles</h3>
		<p class="stat-number">{agentes.filter(a => a.roles && a.roles.length > 0).length}</p>
	</div>
	<div class="stat-card">
		<h3>Administradores</h3>
		<p class="stat-number">{agentes.filter(a => a.roles && a.roles.some(r => r.nombre === 'Administrador')).length}</p>
	</div>
</div>
{/if}

<div class="table-container">
	<table>
		<thead>
			<tr>
				<th>Legajo</th>
				<th>Nombre Completo</th>
				<th>DNI</th>
				<th>Roles</th>
				<th>Categoría</th>
				<th>Fecha Nac.</th>
				<th>Email</th>
				<th>Teléfono</th>
				<th>Dirección</th>
				<th>Agrupación</th>
				<th>Acciones</th>
			</tr>
		</thead>
		<tbody>
			{#if agentes && agentes.length > 0}
				{#each agentes as agente}
					<tr>
						<td><strong>{agente.legajo || 'N/A'}</strong></td>
						<td><strong>{agente.nombre} {agente.apellido}</strong></td>
						<td>{agente.dni}</td>
						<td>
							{#if agente.roles && agente.roles.length > 0}
								<div class="roles-container">
									{#each agente.roles as rol}
										<div class="role-item">
											<span class="badge badge-role">{rol.nombre}</span>
										</div>
									{/each}
								</div>
							{:else}
								<span class="badge badge-sin-rol">Sin roles</span>
							{/if}
						</td>
						<td>{agente.categoria_revista}</td>
						<td><small>{agente.fecha_nac ? new Date(agente.fecha_nac).toLocaleDateString('es-AR') : 'N/A'}</small></td>
						<td><small>{agente.email}</small></td>
						<td>{agente.telefono}</td>
						<td><small>{agente.direccion || 'N/A'}</small></td>
						<td><span class="badge badge-{agente.agrupacion?.toLowerCase()}">{agente.agrupacion_display || 'Sin agrupación'}</span></td>
						<td class="actions">
							<button class="btn-icon" title="Editar">✏️</button>
							<button class="btn-icon" title="Ver detalles">👁️</button>
							<button class="btn-icon-danger" title="Eliminar">🗑️</button>
						</td>
					</tr>
				{/each}
			{:else}
				<tr>
					<td colspan="11" style="text-align: center; padding: 2rem;">
						No se encontraron agentes. Total: {agentes ? agentes.length : 'undefined'}
					</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
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
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

	.page-header h1 {
		margin: 0;
		color: #2c3e50;
		font-size: 2rem;
		font-weight: 600;
	}

	/* Estilos para estadísticas */
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.stat-card {
		background: white;
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1rem;
		text-align: center;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.stat-card h3 {
		margin: 0 0 0.5rem 0;
		font-size: 0.875rem;
		color: #6c757d;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.stat-number {
		margin: 0;
		font-size: 1.75rem;
		font-weight: 700;
		color: #e79043;
	}

	.btn-primary {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.btn-primary:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0,0,0,0.15);
	}

	.table-container {
		overflow-x: auto;
		border-radius: 8px;
		border: 1px solid #e9ecef;
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
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #495057;
		border-bottom: 2px solid #e9ecef;
	}

	td {
		padding: 1rem;
		border-bottom: 1px solid #e9ecef;
	}

	tbody tr:hover {
		background-color: #f8f9fa;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn-icon, .btn-icon-danger {
		background: none;
		border: none;
		font-size: 1.2rem;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 4px;
		transition: background-color 0.2s;
	}

	.btn-icon:hover {
		background-color: #e9ecef;
	}

	.btn-icon-danger:hover {
		background-color: #f8d7da;
	}

	/* Estilos para badges */
	.badge {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		border-radius: 4px;
		text-align: center;
		white-space: nowrap;
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

	.badge-role {
		background-color: #cff4fc;
		color: #055160;
		border: 1px solid #b6effb;
		margin-right: 0.25rem;
	}

	.badge-sin-rol {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
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

	/* Ajustes de columnas */
	table {
		min-width: 1600px; /* Para que sea scrolleable horizontalmente */
	}

	th:nth-child(4), td:nth-child(4) { /* Email */
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	th:nth-child(6), td:nth-child(6) { /* Dirección */
		max-width: 180px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	th:nth-child(7), td:nth-child(7) { /* Agrupación */
		text-align: center;
	}

	th:nth-child(9), td:nth-child(9) { /* Roles */
		max-width: 200px;
	}
</style>
