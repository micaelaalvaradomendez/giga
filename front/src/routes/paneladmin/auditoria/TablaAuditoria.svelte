<script>
	import { auditoriaController } from "$lib/paneladmin/controllers";

	export let registros = [];

	// Paginación
	let paginaActual = 1;
	let registrosPorPagina = 25;

	// Ordenamiento
	let ordenarPor = "creado_en";
	let ordenAsc = false;

	// Funciones para formatear datos
	function formatearFecha(fecha) {
		return auditoriaController.formatearFecha(fecha);
	}

	function traducirAccion(accion) {
		return auditoriaController.traducirAccion(accion);
	}

	function formatearNombreModulo(tabla) {
		return auditoriaController.formatearNombreModulo(tabla);
	}

	function getBadgeColor(accion) {
		return auditoriaController.getBadgeColor(accion);
	}

	// Cache for computed differences to avoid recomputation (keyed by audit record ID)
	const diffCache = new Map();

	// Fast equality check: true shallow for primitives, deep only when needed for objects
	function valuesEqual(a, b) {
		// Handle primitives and null/undefined - fast path
		if (a === b) return true;
		if (a === null || b === null || a === undefined || b === undefined)
			return false;
		if (typeof a !== typeof b) return false;

		// For primitives, direct comparison is enough
		if (typeof a !== "object") return a === b;

		// For arrays, compare length first
		if (Array.isArray(a) && Array.isArray(b)) {
			if (a.length !== b.length) return false;
			// Compare elements recursively for small arrays
			if (a.length <= 10) {
				for (let i = 0; i < a.length; i++) {
					if (!valuesEqual(a[i], b[i])) return false;
				}
				return true;
			}
		}

		// For objects, compare keys count first
		const keysA = Object.keys(a);
		const keysB = Object.keys(b);
		if (keysA.length !== keysB.length) return false;

		// For small objects, compare recursively without JSON.stringify
		if (keysA.length <= 10) {
			for (const key of keysA) {
				if (!(key in b) || !valuesEqual(a[key], b[key])) return false;
			}
			return true;
		}

		// Only fall back to JSON.stringify for complex nested objects
		return JSON.stringify(a) === JSON.stringify(b);
	}

	// Función para obtener solo las diferencias entre dos objetos
	// Uses audit record ID for caching when available
	function obtenerDiferencias(previo, nuevo, recordId = null) {
		if (
			typeof previo !== "object" ||
			typeof nuevo !== "object" ||
			previo === null ||
			nuevo === null
		) {
			return { previo, nuevo };
		}

		// Use record ID for cache key if available (most efficient)
		// Only create string cache key for records without ID
		const cacheKey =
			recordId ??
			`${Object.keys(previo).length}_${Object.keys(nuevo).length}`;
		if (recordId && diffCache.has(cacheKey)) {
			return diffCache.get(cacheKey);
		}

		const diffPrevio = {};
		const diffNuevo = {};
		const allKeys = new Set([
			...Object.keys(previo),
			...Object.keys(nuevo),
		]);

		allKeys.forEach((key) => {
			const valorPrevio = previo[key];
			const valorNuevo = nuevo[key];

			// Use optimized equality check
			if (!valuesEqual(valorPrevio, valorNuevo)) {
				const claveFormateada = key
					.replace(/_/g, " ")
					.replace(/\b\w/g, (l) => l.toUpperCase());
				diffPrevio[claveFormateada] = valorPrevio ?? "N/A";
				diffNuevo[claveFormateada] = valorNuevo ?? "N/A";
			}
		});

		const result =
			Object.keys(diffPrevio).length === 0
				? { previo, nuevo }
				: { previo: diffPrevio, nuevo: diffNuevo };

		// Only cache if we have a record ID (stable key)
		if (recordId) {
			// Cache result (limit cache size to avoid memory issues)
			if (diffCache.size > 100) {
				const firstKey = diffCache.keys().next().value;
				diffCache.delete(firstKey);
			}
			diffCache.set(cacheKey, result);
		}

		return result;
	}

	// Función para formatear valores JSON de forma inteligente
	function formatearValor(valor, accion) {
		if (typeof valor !== "object" || valor === null) {
			return valor || "";
		}

		// Formato especial para cambios de rol
		if (accion === "CAMBIO_ROL_ATOMICO") {
			const agente = valor.agente || "";

			if (valor.nuevo_rol) {
				return `Agente: ${agente}\nNuevo Rol: ${valor.nuevo_rol}`;
			}

			if (valor.roles_previos && valor.roles_previos.length > 0) {
				const rolesNombres = valor.roles_previos
					.map((r) => r.rol_nombre)
					.join(", ");
				return `Agente: ${agente}\nRoles Previos: ${rolesNombres}`;
			}

			return `Agente: ${agente}\nRoles Previos: Ninguno`;
		}

		// Formato genérico para otros objetos
		const textoLimpio = Object.entries(valor)
			.map(([clave, valorItem]) => {
				if (valorItem === null || valorItem === undefined) return null;

				if (
					typeof valorItem === "object" &&
					!Array.isArray(valorItem)
				) {
					const subItems = Object.entries(valorItem)
						.map(([subKey, subValue]) => `${subKey}: ${subValue}`)
						.join(", ");
					return `${clave}: { ${subItems} }`;
				}
				return `${clave}: ${valorItem}`;
			})
			.filter(Boolean);

		return textoLimpio.join("\n");
	}

	// Funciones de ordenamiento
	function ordenar(columna) {
		if (ordenarPor === columna) {
			ordenAsc = !ordenAsc;
		} else {
			ordenarPor = columna;
			ordenAsc = false;
		}
		paginaActual = 1;
	}

	// Computed properties - Use spread copy to avoid mutating the original array
	// Optimize: avoid creating new Date() in sort, use precomputed _ts_creado_en timestamp
	$: registrosOrdenados = [...registros].sort((a, b) => {
		let valorA = a[ordenarPor];
		let valorB = b[ordenarPor];

		// Tratamiento especial para fechas - use precomputed timestamp if available
		if (ordenarPor === "creado_en") {
			// Use precomputed timestamp from controller, fallback to Date parsing
			valorA = a._ts_creado_en ?? new Date(valorA).getTime();
			valorB = b._ts_creado_en ?? new Date(valorB).getTime();
		}

		// Tratamiento especial para nombres
		if (ordenarPor === "creado_por_nombre") {
			valorA = valorA || "Sistema";
			valorB = valorB || "Sistema";
		}

		if (valorA < valorB) return ordenAsc ? -1 : 1;
		if (valorA > valorB) return ordenAsc ? 1 : -1;
		return 0;
	});

	$: totalPaginas = Math.ceil(registrosOrdenados.length / registrosPorPagina);
	$: inicio = (paginaActual - 1) * registrosPorPagina;
	$: fin = Math.min(inicio + registrosPorPagina, registrosOrdenados.length);
	$: registrosPagina = registrosOrdenados.slice(inicio, fin);

	// Funciones de paginación
	function irAPagina(pagina) {
		if (pagina >= 1 && pagina <= totalPaginas) {
			paginaActual = pagina;
		}
	}

	function cambiarRegistrosPorPagina(cantidad) {
		registrosPorPagina = cantidad;
		paginaActual = 1;
	}

	// Función para expandir/colapsar detalles
	let registrosExpandidos = new Set();

	function toggleExpansion(id) {
		if (registrosExpandidos.has(id)) {
			registrosExpandidos.delete(id);
		} else {
			registrosExpandidos.add(id);
		}
		registrosExpandidos = registrosExpandidos;
	}
</script>

<div class="tabla-container">
	<!-- Controles de tabla -->
	<div class="tabla-controles">
		<div class="controles-izquierda">
			<span class="info-registros">
				Mostrando {inicio + 1}-{fin} de {registrosOrdenados.length} registros
			</span>
		</div>

		<div class="controles-derecha">
			<label class="registros-por-pagina">
				Mostrar:
				<select
					bind:value={registrosPorPagina}
					on:change={() =>
						cambiarRegistrosPorPagina(registrosPorPagina)}
				>
					<option value={10}>10</option>
					<option value={25}>25</option>
					<option value={50}>50</option>
					<option value={100}>100</option>
				</select>
			</label>
		</div>
	</div>

	<!-- Tabla principal -->
	<div class="tabla-wrapper">
		<table class="tabla-auditoria">
			<thead>
				<tr>
					<th>
						<!-- Columna de expansión -->
					</th>
					<th class="sorteable" on:click={() => ordenar("creado_en")}>
						📅 Fecha y Hora
						{#if ordenarPor === "creado_en"}
							<span class="sort-indicator"
								>{ordenAsc ? "▲" : "▼"}</span
							>
						{/if}
					</th>
					<th
						class="sorteable"
						on:click={() => ordenar("creado_por_nombre")}
					>
						👤 Usuario
						{#if ordenarPor === "creado_por_nombre"}
							<span class="sort-indicator"
								>{ordenAsc ? "▲" : "▼"}</span
							>
						{/if}
					</th>
					<th class="sorteable" on:click={() => ordenar("accion")}>
						⚡ Acción
						{#if ordenarPor === "accion"}
							<span class="sort-indicator"
								>{ordenAsc ? "▲" : "▼"}</span
							>
						{/if}
					</th>
					<th
						class="sorteable"
						on:click={() => ordenar("nombre_tabla")}
					>
						📦 Módulo
						{#if ordenarPor === "nombre_tabla"}
							<span class="sort-indicator"
								>{ordenAsc ? "▲" : "▼"}</span
							>
						{/if}
					</th>
					<th>🔍 ID</th>
				</tr>
			</thead>
			<tbody>
				{#each registrosPagina as registro (registro.id_auditoria)}
					<tr
						class="fila-principal"
						class:expandida={registrosExpandidos.has(
							registro.id_auditoria,
						)}
					>
						<td>
							<button
								class="btn-expandir"
								on:click={() =>
									toggleExpansion(registro.id_auditoria)}
								title="Ver detalles"
							>
								{registrosExpandidos.has(registro.id_auditoria)
									? "▼"
									: "▶"}
							</button>
						</td>
						<td class="fecha">
							<div class="fecha-content">
								<span class="fecha-principal"
									>{formatearFecha(registro.creado_en)}</span
								>
								<span class="fecha-relativa"
									>{new Date(
										registro.creado_en,
									).toLocaleDateString("es-AR")}</span
								>
							</div>
						</td>
						<td class="usuario">
							<div class="usuario-content">
								<span class="usuario-nombre"
									>{registro.creado_por_nombre ||
										"Sistema"}</span
								>
								{#if registro.id_agente}
									<span class="usuario-id"
										>ID: {registro.id_agente}</span
									>
								{/if}
							</div>
						</td>
						<td class="accion">
							<span
								class="badge {getBadgeColor(registro.accion)}"
							>
								{traducirAccion(registro.accion)}
							</span>
						</td>
						<td class="modulo">
							<span class="modulo-badge">
								{formatearNombreModulo(registro.nombre_tabla)}
							</span>
						</td>
						<td class="id-registro">
							{registro.pk_afectada || "N/A"}
						</td>
					</tr>

					{#if registrosExpandidos.has(registro.id_auditoria)}
						<tr class="fila-detalles">
							<td colspan="6">
								<div class="detalles-container">
									<div class="detalles-grid">
										{#if registro.valor_previo}
											<div class="detalle-seccion">
												<h4>📋 Valor Anterior</h4>
												<pre
													class="valor-json">{#if registro.accion === "ACTUALIZAR"}{formatearValor(
															obtenerDiferencias(
																registro.valor_previo,
																registro.valor_nuevo,
																registro.id_auditoria,
															).previo,
															registro.accion,
														)}{:else}{formatearValor(
															registro.valor_previo,
															registro.accion,
														)}{/if}</pre>
											</div>
										{/if}

										{#if registro.valor_nuevo}
											<div class="detalle-seccion">
												<h4>📝 Valor Nuevo</h4>
												<pre
													class="valor-json">{#if registro.accion === "ACTUALIZAR"}{formatearValor(
															obtenerDiferencias(
																registro.valor_previo,
																registro.valor_nuevo,
																registro.id_auditoria,
															).nuevo,
															registro.accion,
														)}{:else}{formatearValor(
															registro.valor_nuevo,
															registro.accion,
														)}{/if}</pre>
											</div>
										{/if}
									</div>

									<div class="detalles-meta">
										<span class="meta-item"
											>🔢 ID Auditoría: {registro.id_auditoria}</span
										>
										<span class="meta-item"
											>🕐 Timestamp: {registro.creado_en}</span
										>
									</div>
								</div>
							</td>
						</tr>
					{/if}
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Paginación -->
	{#if totalPaginas > 1}
		<div class="paginacion">
			<div class="paginacion-info">
				Página {paginaActual} de {totalPaginas}
			</div>

			<div class="paginacion-controles">
				<button
					class="btn-pagina"
					disabled={paginaActual === 1}
					on:click={() => irAPagina(1)}
				>
					⏪ Primera
				</button>

				<button
					class="btn-pagina"
					disabled={paginaActual === 1}
					on:click={() => irAPagina(paginaActual - 1)}
				>
					◀ Anterior
				</button>

				<!-- Números de página -->
				{#each Array(Math.min(5, totalPaginas)) as _, i}
					{@const pagina =
						Math.max(
							1,
							Math.min(totalPaginas - 4, paginaActual - 2),
						) + i}
					{#if pagina <= totalPaginas}
						<button
							class="btn-pagina-num"
							class:activa={pagina === paginaActual}
							on:click={() => irAPagina(pagina)}
						>
							{pagina}
						</button>
					{/if}
				{/each}

				<button
					class="btn-pagina"
					disabled={paginaActual === totalPaginas}
					on:click={() => irAPagina(paginaActual + 1)}
				>
					Siguiente ▶
				</button>

				<button
					class="btn-pagina"
					disabled={paginaActual === totalPaginas}
					on:click={() => irAPagina(totalPaginas)}
				>
					Última ⏩
				</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.tabla-container {
		background: white;
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
	}

	.tabla-controles {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 25px;
		background: #f8fafc;
		border-bottom: 1px solid #e5e7eb;
	}

	.info-registros {
		color: #6b7280;
		font-size: 0.9rem;
		font-weight: 500;
	}

	.registros-por-pagina {
		display: flex;
		align-items: center;
		gap: 8px;
		color: #374151;
		font-size: 0.9rem;
		font-weight: 500;
	}

	.registros-por-pagina select {
		padding: 4px 8px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.tabla-wrapper {
		overflow-x: auto;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.tabla-wrapper::-webkit-scrollbar {
		display: none;
	}

	.tabla-auditoria {
		width: 100%;
		border-collapse: collapse;
	}

	.tabla-auditoria th {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		font-weight: 600;
		padding: 16px 12px;
		text-align: left;
		font-size: 0.9rem;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.tabla-auditoria th.sorteable {
		cursor: pointer;
		user-select: none;
		transition: background 0.2s ease;
		position: relative;
	}

	.tabla-auditoria th.sorteable:hover {
		background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
	}

	.sort-indicator {
		font-size: 0.8rem;
		margin-left: 4px;
	}

	.fila-principal {
		border-bottom: 1px solid #f3f4f6;
		transition: all 0.2s ease;
	}

	.fila-principal:hover {
		background: #f8fafc;
	}

	.fila-principal.expandida {
		background: #eff6ff;
		border-bottom-color: #dbeafe;
	}

	.tabla-auditoria td {
		padding: 12px;
		vertical-align: top;
	}

	.btn-expandir {
		background: #e5e7eb;
		border: none;
		width: 24px;
		height: 24px;
		border-radius: 4px;
		cursor: pointer;
		color: #374151;
		font-size: 0.8rem;
		transition: all 0.2s ease;
	}

	.btn-expandir:hover {
		background: #d1d5db;
	}

	.fecha-content {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.fecha-principal {
		font-weight: 500;
		color: #374151;
		font-size: 0.9rem;
	}

	.fecha-relativa {
		font-size: 0.8rem;
		color: #6b7280;
	}

	.usuario-content {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.usuario-nombre {
		font-weight: 500;
		color: #374151;
	}

	.usuario-id {
		font-size: 0.8rem;
		color: #6b7280;
	}

	.badge {
		padding: 4px 8px;
		border-radius: 12px;
		font-size: 0.8rem;
		font-weight: 600;
		text-align: center;
		min-width: 80px;
		display: inline-block;
	}

	.modulo-badge {
		background: #f3f4f6;
		color: #374151;
		padding: 4px 8px;
		border-radius: 6px;
		font-size: 0.85rem;
		font-weight: 500;
	}

	.id-registro {
		font-family: "Courier New", monospace;
		color: #6b7280;
		font-size: 0.9rem;
	}

	.fila-detalles {
		background: #f8fafc !important;
	}

	.detalles-container {
		padding: 20px;
		border-left: 4px solid #667eea;
		background: white;
		border-radius: 8px;
		margin: 8px;
	}

	.detalles-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
		margin-bottom: 15px;
	}

	.detalle-seccion h4 {
		margin: 0 0 8px 0;
		color: #374151;
		font-size: 0.9rem;
		font-weight: 600;
	}

	.valor-json {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		padding: 12px;
		font-family: "Courier New", monospace;
		font-size: 0.8rem;
		color: #374151;
		white-space: pre-wrap;
		word-break: break-all;
		max-height: 200px;
		overflow-y: auto;
		margin: 0;
	}

	.detalles-meta {
		display: flex;
		gap: 20px;
		padding-top: 12px;
		border-top: 1px solid #e5e7eb;
		font-size: 0.8rem;
		color: #6b7280;
	}

	.paginacion {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 25px;
		background: #f8fafc;
		border-top: 1px solid #e5e7eb;
	}

	.paginacion-controles {
		display: flex;
		gap: 8px;
		align-items: center;
	}

	.btn-pagina,
	.btn-pagina-num {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		background: white;
		color: #374151;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.85rem;
		transition: all 0.2s ease;
	}

	.btn-pagina:hover,
	.btn-pagina-num:hover {
		background: #f3f4f6;
		border-color: #9ca3af;
	}

	.btn-pagina:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-pagina-num.activa {
		background: #667eea;
		border-color: #667eea;
		color: white;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.tabla-controles {
			flex-direction: column;
			gap: 12px;
			align-items: stretch;
		}

		.detalles-grid {
			grid-template-columns: 1fr;
		}

		.paginacion {
			flex-direction: column;
			gap: 12px;
		}

		.paginacion-controles {
			flex-wrap: wrap;
			justify-content: center;
		}

		.detalles-meta {
			flex-direction: column;
			gap: 8px;
		}
	}

	@media (max-width: 640px) {
		.tabla-auditoria th,
		.tabla-auditoria td {
			padding: 8px 6px;
		}

		.fecha-content,
		.usuario-content {
			font-size: 0.85rem;
		}

		.badge {
			min-width: 60px;
			font-size: 0.75rem;
		}
	}
</style>
