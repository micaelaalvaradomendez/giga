<script>
	/** @type {import('./$types').PageData} */
	export let data;

	// Los agentes vienen cargados desde +page.server.js
	const { agentes } = data;
</script>

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
