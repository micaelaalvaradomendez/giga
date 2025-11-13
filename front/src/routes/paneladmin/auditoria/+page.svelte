<script>
	/** @type {import('./$types').PageData} */
	export let data;

	$: registros = data.registros || [];

	// --- Lógica del Buscador ---
	let terminoBusqueda = '';

	$: registrosFiltrados = registros.filter((registro) => {
		const busqueda = terminoBusqueda.toLowerCase().trim();
		if (!busqueda) return true; // Si no hay búsqueda, mostrar todo

		const usuario = (registro.creado_por_nombre || 'sistema').toLowerCase();
		const accion = (traduccionAccion[registro.accion] || registro.accion).toLowerCase();
		const tabla = registro.nombre_tabla.toLowerCase();

		return usuario.includes(busqueda) || accion.includes(busqueda) || tabla.includes(busqueda);
	});

	/**
	 * Formatea una fecha en formato ISO a un string legible para Argentina.
	 * @param {string} fechaISO - La fecha en formato ISO.
	 * @returns {string} La fecha formateada.
	 */
	function formatarFecha(fechaISO) {
		if (!fechaISO) return 'N/A';
		const fecha = new Date(fechaISO);
		return fecha.toLocaleString('es-AR', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			hour12: false 
		});
	}

	/**
	 * Formatea un objeto JSON para mostrarlo de forma legible, sin llaves ni comillas.
	 * Si el valor es null, devuelve un guion.
	 * @param {object | null} valor - El objeto JSON a formatear.
	 * @returns {string} El valor formateado.
	 */
	function formatarValor(valor) {
		if (valor === null || typeof valor !== 'object' || Object.keys(valor).length === 0) {
			return '-';
		}
		return Object.entries(valor)
			.map(([key, val]) => `${key}: ${val}`)
			.join(', ');
	}

	const badgeColors = {
		create: 'bg-green-500 text-white',
		update: 'bg-yellow-400 text-black',
		delete: 'bg-red-500 text-white'
	};

	const traduccionAccion = {
		create: 'Alta de registro',
		update: 'Modificación',
		delete: 'Registro eliminado'
	};
</script>

<div class="admin-page-container">
	<div class="page-header">
		<div>
			<h1 class="text-2xl font-bold text-gray-800">Auditoría de registros</h1>
		</div>
	</div>

	<!-- Bloque de búsqueda -->
	<div class="search-section">
		<label for="search-input" class="search-label">🔍 Buscar</label>
		<input
			id="search-input"
			type="text"
			bind:value={terminoBusqueda}
			placeholder="Escribe un usuario, acción o nombre de tabla..."
			class="search-input"
		/>
	</div>

	{#if registrosFiltrados.length === 0}
		<div class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4" role="alert">
			<p class="font-bold">Sin datos</p>
			<p>
				{#if terminoBusqueda}No se encontraron registros que coincidan con "{terminoBusqueda}".{:else}No hay registros para mostrar.{/if}
			</p>
		</div>
	{:else}
		<div class="bg-white shadow-md rounded-lg overflow-x-auto">
			<table class="min-w-full leading-normal">
				<thead class="bg-gray-100">
					<tr>
						<th
							class="px-5 py-3 border-b-2 border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
						>
							Fecha y Hora
						</th>
						<th
							class="px-5 py-3 border-b-2 border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
						>
							Usuario
						</th>
						<th
							class="px-5 py-3 border-b-2 border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
						>
							Acción
						</th>
						<th
							class="px-5 py-3 border-b-2 border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
						>
							Tabla
						</th>
						<th
							class="px-5 py-3 border-b-2 border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
						>
							Valor Anterior
						</th>
						<th
							class="px-5 py-3 border-b-2 border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
						>
							Valor Nuevo
						</th>
					</tr>
				</thead>
				<tbody>
					{#each registrosFiltrados as registro}
						<tr>
							<td class="px-5 py-4 border-b border-gray-200 bg-white text-sm">
								{formatarFecha(registro.creado_en)}
							</td>
							<td class="px-5 py-4 border-b border-gray-200 bg-white text-sm">
								{registro.creado_por_nombre || 'Sistema'}
							</td>
							<td class="px-5 py-4 border-b border-gray-200 bg-white text-sm">
								<span
									class="px-2 py-1 font-semibold leading-tight rounded-full text-xs {badgeColors[registro.accion] ||
										'bg-gray-500 text-white'}"
								>
									{traduccionAccion[registro.accion] || registro.accion.toUpperCase()}
								</span>
							</td>
							<td class="px-5 py-4 border-b border-gray-200 bg-white text-sm">
								{registro.nombre_tabla}
							</td>
							<td class="px-5 py-4 border-b border-gray-200 bg-white text-sm font-mono text-gray-600">
								{formatarValor(registro.valor_previo)}
							</td>
							<td class="px-5 py-4 border-b border-gray-200 bg-white text-sm font-mono text-gray-800">
								{formatarValor(registro.valor_nuevo)}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
			'Open Sans', 'Helvetica Neue', sans-serif;
		background-color: #f8f9fa;
		color: #212529;
	}
	.admin-page-container {
		width: 80%;
		max-width: 1400px; 
		margin: 0 auto;
		padding: 1rem 0; 
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		margin-bottom: 1.5rem; 
		padding: 1.5rem;
		background: linear-gradient(135deg, #e79043, #d17a2e); 
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
	}

	.page-header h1 {
		margin: 0;
		color: #333; 
		font-size: 2rem;
		font-weight: 600;
	}

	.search-section {
		margin-bottom: 1.5rem;
		background-color: #fff;
		padding: 1.5rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}

	.search-label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #495057;
	}

	.search-input {
        width: 95%; 
		padding: 0.75rem 1rem;
		border-radius: 8px;
		border: 1px solid #ccc;
		font-size: 1rem;
		transition:
			border-color 0.2s,
			box-shadow 0.2s;
	}

	.search-input:focus {
		outline: none;
		border-color: #e79043;
		box-shadow: 0 0 0 3px rgba(231, 144, 67, 0.3);
	}

	.bg-white.shadow-md.rounded-lg.overflow-x-auto {
		border: 1px solid #e9ecef; 
	}

	.bg-gray-100 {
		background-color: #f8f9fa; 
	}

	th {
		padding: 1rem; 
		font-weight: 600;
		color: #495057; 
		border-bottom: 2px solid #e9ecef;
	}

	td {
		padding: 1rem; 
		font-size: 0.9rem;
		border-bottom: 1px solid #e9ecef;
	}

	tbody tr:hover {
		background-color: #f8f9fa; 
	}

	.btn-icon {
		background: none;
		border: none;
		font-size: 1rem; 
		cursor: pointer;
		padding: 0.5rem 0.75rem;
		border-radius: 6px;
		transition: background-color 0.2s, color 0.2s;
		color: #2c5282; 
		font-weight: 500;
	}

	.btn-icon:hover {
		background-color: #e9ecef; 
		color: #1a365d; 
	}

	@media (max-width: 768px) {
		.admin-page-container {
			width: 95%;
			padding: 0.5rem;
		}
		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}
	}
</style>
