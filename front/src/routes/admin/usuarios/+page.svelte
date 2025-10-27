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

<div class="table-container">
	<table>
		<thead>
			<tr>
				<th>Legajo</th>
				<th>Nombre Completo</th>
				<th>CUIL</th>
				<th>Área</th>
				<th>Acciones</th>
			</tr>
		</thead>
		<tbody>
			{#if agentes && agentes.length > 0}
				{#each agentes as agente}
					<tr>
						<td>{agente.legajo || 'N/A'}</td>
						<td>{agente.nombre} {agente.apellido}</td>
						<td>{agente.usuario.cuil}</td>
						<td>{agente.area?.nombre || 'Sin área'}</td>
						<td class="actions">
							<button class="btn-icon" title="Editar">✏️</button>
							<button class="btn-icon" title="Ver detalles">👁️</button>
							<button class="btn-icon-danger" title="Eliminar">🗑️</button>
						</td>
					</tr>
				{/each}
			{:else}
				<tr>
					<td colspan="5" style="text-align: center; padding: 2rem;">
						No se encontraron agentes.
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
</style>
