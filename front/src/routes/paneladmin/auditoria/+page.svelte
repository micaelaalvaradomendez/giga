<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { auditoriaController } from "$lib/paneladmin/controllers";

	// Stores del controlador
	const { registros, registrosFiltrados, loading, error, terminoBusqueda } =
		auditoriaController;

	// Inicializar el controlador
	onMount(async () => {
		console.log(
			"🔄 Componente montado, iniciando controlador de auditoría...",
		);
		try {
			await auditoriaController.init();
			console.log(
				"✅ Controlador de auditoría inicializado exitosamente",
			);

			// Recargar cuando la página vuelve a ser visible
			if (typeof window !== "undefined") {
				const handleVisibilityChange = () => {
					if (document.visibilityState === "visible") {
						auditoriaController.init();
					}
				};

				const handleFocus = () => {
					auditoriaController.init();
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
			console.error(
				"❌ Error inicializando controlador de auditoría:",
				err,
			);
			if (err.message === "Usuario no autenticado") {
				goto("/");
				return;
			}
		}
	});

	// Función para manejar cambios en el término de búsqueda
	function handleBusquedaChange(event) {
		auditoriaController.setBusqueda(event.target.value);
	}

	// Función para limpiar búsqueda
	function limpiarBusqueda() {
		auditoriaController.limpiarBusqueda();
	}

	// Función para recargar datos
	function recargarDatos() {
		auditoriaController.recargar();
	}

	// Mapeo de colores para badges
	const badgeColors = {
		CREAR: "bg-green-500 text-white",
		MODIFICAR: "bg-yellow-400 text-black",
		ELIMINAR: "bg-red-500 text-white",
		create: "bg-green-500 text-white",
		update: "bg-yellow-400 text-black",
		delete: "bg-red-500 text-white",
	};

	// Mapeo de traducciones de acciones
	const traduccionAccion = {
		CREAR: "Alta de registro",
		MODIFICAR: "Modificación",
		ELIMINAR: "Registro eliminado",
		ACTUALIZAR: "Modificación",
		create: "Alta de registro",
		update: "Modificación",
		delete: "Registro eliminado",
		CAMBIO_ROL_ATOMICO: "Cambio de rol",
		CAMBIO_PASSWORD_EXITOSO: "Cambio de contraseña",
		LOGIN_EXITOSO: "Inicio de sesión",
		LOGIN_FALLIDO: "Intento de inicio de sesión fallido",
		LOGOUT: "Cierre de sesión",
	};

	// Función para formatear la fecha
	function formatearFecha(fecha) {
		return new Date(fecha).toLocaleString("es-AR", {
			year: "numeric",
			month: "2-digit",
			day: "2-digit",
			hour: "2-digit",
			minute: "2-digit",
			hour12: false,
		});
	}

	// Función para obtener solo las diferencias entre dos objetos
	function obtenerDiferencias(previo, nuevo) {
		if (
			typeof previo !== "object" ||
			typeof nuevo !== "object" ||
			previo === null ||
			nuevo === null
		) {
			return { previo, nuevo };
		}

		const diffPrevio = {};
		const diffNuevo = {};
		const allKeys = new Set([
			...Object.keys(previo),
			...Object.keys(nuevo),
		]);

		allKeys.forEach((key) => {
			const valorPrevio = JSON.stringify(previo[key]);
			const valorNuevo = JSON.stringify(nuevo[key]);

			if (valorPrevio !== valorNuevo) {
				// Formatea la clave para que sea legible
				const claveFormateada = key
					.replace(/_/g, " ")
					.replace(/\b\w/g, (l) => l.toUpperCase());

				// Asigna los valores diferentes
				diffPrevio[claveFormateada] = previo[key] ?? "N/A";
				diffNuevo[claveFormateada] = nuevo[key] ?? "N/A";
			}
		});

		// Si no hay diferencias, devuelve los objetos originales para el formateo estándar
		if (Object.keys(diffPrevio).length === 0) {
			return { previo, nuevo };
		}

		return { previo: diffPrevio, nuevo: diffNuevo };
	}

	// Función para formatear valores JSON
	function formatearValor(valor, accion) {
		if (typeof valor !== "object" || valor === null) {
			return valor || "";
		}

		// Formato especial para la acción de cambio de rol
		if (accion === "CAMBIO_ROL_ATOMICO") {
			const agente = valor.agente || "";

			// Formato para el valor NUEVO
			if (valor.nuevo_rol) {
				return `Agente: ${agente}\nNuevo Rol: ${valor.nuevo_rol}`;
			}

			// Formato para el valor PREVIO
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
				if (valorItem === null || valorItem === undefined) return null; // Omitir nulos

				// La clave ya viene formateada desde obtenerDiferencias
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
			.filter(Boolean); // Eliminar los nulos

		return textoLimpio.join("\n");
	}
</script>

<div class="admin-page-container">
	<div class="page-header">
		<div>
			<h1 class="text-2xl font-bold text-gray-800">
				Auditoría de registros
			</h1>
		</div>
	</div>

	<!-- Bloque de búsqueda -->
	<div class="search-section">
		<label for="search-input" class="search-label">🔍 Buscar</label>
		<input
			id="search-input"
			type="text"
			value={$terminoBusqueda}
			on:input={handleBusquedaChange}
			placeholder="Escribe un usuario, acción o nombre de tabla..."
			class="search-input"
		/>
		{#if $terminoBusqueda}
			<button
				class="btn-clear"
				on:click={limpiarBusqueda}
				title="Limpiar búsqueda"
			>
				✖️ Limpiar
			</button>
		{/if}
	</div>

	{#if $loading}
		<div class="loading-container">
			<div class="loading-spinner"></div>
			<p>Cargando registros de auditoría...</p>
		</div>
	{:else if $error}
		<div class="error-message">
			<p><strong>Error:</strong> {$error}</p>
			<button class="btn-retry" on:click={recargarDatos}
				>🔄 Reintentar</button
			>
		</div>
	{:else if $registrosFiltrados.length === 0}
		<div
			class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4"
			role="alert"
		>
			<p class="font-bold">Sin datos</p>
			<p>
				{#if $terminoBusqueda}No se encontraron registros que coincidan
					con "{$terminoBusqueda}".{:else}No hay registros para
					mostrar.{/if}
			</p>
		</div>
	{:else}
		<div class="bg-white shadow-md rounded-lg overflow-x-auto">
			<table class="min-w-full leading-normal responsive-table">
				<thead class="bg-gray-100">
					<tr>
						<th
							class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
						>
							Fecha y Hora
						</th>
						<th
							class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
						>
							Usuario
						</th>
						<th
							class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
						>
							Acción
						</th>
						<th
							class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
						>
							Tabla
						</th>
						<th
							class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
						>
							Valor Anterior
						</th>
						<th
							class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
						>
							Valor Nuevo
						</th>
					</tr>
				</thead>
				<tbody>
					{#each $registrosFiltrados as registro}
						<tr>
							<td
								class="px-5 py-4 border-b border-gray-200 bg-white text-sm"
							>
								{formatearFecha(registro.creado_en)}
							</td>
							<td
								class="px-5 py-4 border-b border-gray-200 bg-white text-sm"
							>
								{registro.creado_por_nombre || "Sistema"}
							</td>
							<td
								class="px-5 py-4 border-b border-gray-200 bg-white text-sm"
							>
								<span
									class="px-2 py-1 font-semibold leading-tight rounded-full text-xs {badgeColors[
										registro.accion
									] || 'bg-gray-400 text-white'}"
								>
									{traduccionAccion[registro.accion] ||
										registro.accion}
								</span>
							</td>
							<td
								class="px-5 py-4 border-b border-gray-200 bg-white text-sm"
							>
								{registro.nombre_tabla}
							</td>
							<td
								class="px-5 py-4 border-b border-gray-200 bg-white text-sm font-mono text-gray-600 whitespace-pre-wrap break-all"
							>
								{#if registro.accion === "ACTUALIZAR"}
									{formatearValor(
										obtenerDiferencias(
											registro.valor_previo,
											registro.valor_nuevo,
										).previo,
										registro.accion,
									)}
								{:else}
									{formatearValor(
										registro.valor_previo,
										registro.accion,
									)}
								{/if}
							</td>
							<td
								class="px-5 py-4 border-b border-gray-200 bg-white text-sm font-mono text-gray-800 whitespace-pre-wrap break-all"
							>
								{#if registro.accion === "ACTUALIZAR"}
									{formatearValor(
										obtenerDiferencias(
											registro.valor_previo,
											registro.valor_nuevo,
										).nuevo,
										registro.accion,
									)}
								{:else}
									{formatearValor(
										registro.valor_nuevo,
										registro.accion,
									)}
								{/if}
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
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
		background-color: #f8f9fa;
		color: #212529;
	}
	.admin-page-container {
		width: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 1rem 0;
	}

	.page-header {
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		text-align: center;
		padding: 40px 20px;
		margin: 0 0 40px 0;
		border-radius: 28px;
		overflow: hidden;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
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
		margin: 0 0 0 20px;
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

	.search-section {
		margin-bottom: 1.5rem;
		background-color: #fff;
		padding: 1.5rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.search-label {
		font-weight: 600;
		color: #495057;
	}

	.search-input {
		flex: 1;
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
		border: 3px solid #e79043;
		box-shadow:
			0 4px 12px rgba(231, 144, 67, 0.15),
			0 0 0 1px rgba(231, 144, 67, 0.1) inset;
		overflow: hidden;
		border-radius: 10px;
	}

	.bg-white.shadow-md.rounded-lg.overflow-x-auto::before {
		content: "";
		position: relative;
		top: 0;
		left: 0;
		right: 0;
		height: 4px;
		background: linear-gradient(
			90deg,
			#ff9d5c,
			#e79043,
			#d67d35,
			#e79043,
			#ff9d5c
		);
		background-size: 200% 100%;
		animation: shimmer 3s linear infinite;
	}

	@keyframes shimmer {
		0% {
			background-position: -200% 0;
		}
		100% {
			background-position: 200% 0;
		}
	}

	.bg-gray-100 {
		background: linear-gradient(135deg, #fff5ec 0%, #ffe8d6 100%);
		position: relative;
	}

	.bg-gray-100::after {
		content: "";
		position: relative;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
	}

	th {
		padding: 1rem;
		font-weight: 700;
		color: #8b4513;
		border-bottom: 2px solid #ffd4a8;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		font-size: 0.85rem;
		position: relative;
	}

	td {
		padding: 1rem;
		font-size: 0.9rem;
		border-bottom: 1px solid #fff0e0;
		transition: all 0.2s ease;
	}

	tbody tr {
		transition: all 0.3s ease;
		border-left: 3px solid transparent;
	}

	tbody tr:hover {
		background: linear-gradient(90deg, #fff9f5 0%, #fff5ec 100%);
		border: 3px solid #e79043;
		transform: translateX(2px);
		box-shadow: 0 2px 8px rgba(231, 144, 67, 0.1);
	}

	tbody tr:nth-child(even) {
		background-color: #fffbf7;
	}

	tbody tr:nth-child(even):hover {
		background: linear-gradient(90deg, #fff9f5 0%, #fff5ec 100%);
	}

	.btn-icon {
		background: none;
		border: none;
		font-size: 1rem;
		cursor: pointer;
		padding: 0.5rem 0.75rem;
		border-radius: 6px;
		transition:
			background-color 0.2s,
			color 0.2s;
		color: #2c5282;
		font-weight: 500;
	}

	.btn-icon:hover {
		background-color: #e9ecef;
		color: #1a365d;
	}

	.btn-clear {
		margin-left: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: #dc3545;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: background-color 0.2s;
	}

	.btn-clear:hover {
		background-color: #c82333;
	}

	.btn-retry {
		margin-top: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: background-color 0.2s;
	}

	.btn-retry:hover {
		background-color: #0056b3;
	}

	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background-color: white;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #f3f3f3;
		border-top: 4px solid #e79043;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.error-message {
		background-color: #f8d7da;
		color: #721c24;
		padding: 1rem;
		border-radius: 8px;
		border: 1px solid #f5c6cb;
		margin-bottom: 1rem;
	}

	@media (max-width: 1200px) {
		.admin-page-container {
			width: 90%;
		}
	}

	@media (max-width: 768px) {
		.admin-page-container {
			width: 95%;
			padding: 1rem;
		}

		.page-header {
			padding: 20px 15px;
			margin-bottom: 20px;
		}

		.page-header h1 {
			font-size: 26px;
		}

		.search-section {
			padding: 1rem;
			display: flex;
			flex-direction: column;
			align-items: stretch;
		}

		.search-input {
			flex: none;
		}

		.btn-clear {
			margin-top: 0.5rem;
			margin-left: 0;
			width: 100%;
		}

		.table {
			table-layout: fixed;
		}

		th,
		td {
			padding: 0.75rem;
			font-size: 0.8rem;
		}

		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}
	}

	@media (max-width: 480px) {
		.page-header h1 {
			font-size: 22px;
		}

		th,
		td {
			padding: 0.5rem;
			font-size: 0.75rem;
		}

		.btn-clear,
		.btn-retry {
			padding: 0.75rem;
			font-size: 0.85rem;
		}
	}
</style>
