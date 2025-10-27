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
	body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: #ffffff;
    color: #212529;
}

.admin-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    height: 60px;
    background: linear-gradient(135deg, #e79043, #f39c12);
    flex-shrink: 0;
}

.admin-header .logo a {
    font-weight: bold;
    font-size: 1.2rem;
    text-decoration: none;
    color: white;
}

.admin-main {
    display: flex;
    flex-grow: 1;
    overflow: hidden;
}

.admin-content-full {
    flex-grow: 1;
    padding: 2.5rem;
    overflow-y: auto;
    width: 100%;
    background-color: #ffffff;
}
</style>
