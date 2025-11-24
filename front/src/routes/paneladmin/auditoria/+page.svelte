<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { slide } from "svelte/transition";
	import { auditoriaController } from "$lib/paneladmin/controllers";
	import FiltrosAuditoria from './FiltrosAuditoria.svelte';
	import TablaAuditoria from './TablaAuditoria.svelte';
	import EstadisticasAuditoria from './EstadisticasAuditoria.svelte';

	// Estados reactivos
	let mostrarEstadisticas = false;
	let cargandoDatos = false;

	// Stores del controlador
	const { loading, error, registros, registrosFiltrados, terminoBusqueda, filtros } = auditoriaController;

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


</script>

<div class="auditoria-container">
	<!-- Header Principal -->
	<div class="auditoria-header">
		<div class="header-content">
			<div class="header-info">
				<h1>📊 Auditoría del Sistema</h1>
				<p>Sistema profesional de seguimiento y auditoría de actividades</p>
			</div>
			
			<div class="header-controls">
				<button 
					class="btn-estadisticas"
					class:activo={mostrarEstadisticas}
					on:click={() => mostrarEstadisticas = !mostrarEstadisticas}
				>
					📈 {mostrarEstadisticas ? 'Ocultar' : 'Ver'} Estadísticas
				</button>
				
				<button 
					class="btn-refresh"
					on:click={async () => {
						cargandoDatos = true;
						await auditoriaController.init();
						cargandoDatos = false;
					}}
					disabled={$loading || cargandoDatos}
				>
					{#if $loading || cargandoDatos}
						🔄 Actualizando...
					{:else}
						🔄 Actualizar Datos
					{/if}
				</button>
			</div>
		</div>

		<!-- Stats rápidas -->
		<div class="stats-rapidas">
			<div class="stat-item">
				<span class="stat-numero">{$registros.length.toLocaleString()}</span>
				<span class="stat-etiqueta">Total de Registros</span>
			</div>
			<div class="stat-item">
				<span class="stat-numero">{$registrosFiltrados.length.toLocaleString()}</span>
				<span class="stat-etiqueta">Registros Filtrados</span>
			</div>
			<div class="stat-item">
				<span class="stat-numero">
					{#if $registros.length > 0}
						{Math.round((($registrosFiltrados.length / $registros.length) * 100))}%
					{:else}
						0%
					{/if}
				</span>
				<span class="stat-etiqueta">Coincidencias</span>
			</div>
		</div>
	</div>

	<!-- Estadísticas (Opcional) -->
	{#if mostrarEstadisticas}
		<div class="seccion-estadisticas" transition:slide>
			<EstadisticasAuditoria registros={$registrosFiltrados} />
		</div>
	{/if}

	<!-- Sistema de Filtros Profesional -->
	<div class="seccion-filtros">
		<FiltrosAuditoria />
	</div>

	<!-- Manejo de Estados -->
	{#if $error}
		<div class="error-container">
			<div class="error-content">
				<span class="error-icon">⚠️</span>
				<div class="error-text">
					<h3>Error al cargar datos</h3>
					<p>{$error}</p>
				</div>
				<button 
					class="btn-retry"
					on:click={async () => {
						cargandoDatos = true;
						await auditoriaController.init();
						cargandoDatos = false;
					}}
				>
					🔄 Reintentar
				</button>
			</div>
		</div>
	{:else if $loading && !cargandoDatos}
		<div class="loading-container">
			<div class="loading-content">
				<div class="loading-spinner">
					<div class="spinner-ring"></div>
				</div>
				<h3>Cargando Registros de Auditoría</h3>
				<p>Obteniendo datos del servidor...</p>
			</div>
		</div>
	{:else if $registrosFiltrados.length === 0 && $registros.length > 0}
		<div class="sin-resultados-container">
			<div class="sin-resultados-content">
				<span class="sin-resultados-icon">🔍</span>
				<h3>Sin Resultados</h3>
				<p>No se encontraron registros que coincidan con los filtros actuales.</p>
				<p class="hint">Prueba ajustando los criterios de filtrado o limpia los filtros activos.</p>
			</div>
		</div>
	{:else if $registrosFiltrados.length === 0 && $registros.length === 0}
		<div class="sin-datos-container">
			<div class="sin-datos-content">
				<span class="sin-datos-icon">📝</span>
				<h3>Sin Datos de Auditoría</h3>
				<p>No hay registros de auditoría disponibles en el sistema.</p>
				<p class="hint">Los registros aparecerán aquí cuando se generen actividades en el sistema.</p>
			</div>
		</div>
	{:else}
		<!-- Tabla Principal de Auditoría -->
		<div class="seccion-tabla">
			<TablaAuditoria registros={$registrosFiltrados} />
		</div>
	{/if}
</div>

<style>
	.auditoria-container {
		max-width: 1600px;
		margin: 0 auto;
		padding: 20px;
		background: #f8fafc;
		min-height: 100vh;
	}

	/* Header Principal */
	.auditoria-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 16px;
		padding: 32px;
		margin-bottom: 24px;
		box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
		color: white;
		position: relative;
		overflow: hidden;
	}

	.auditoria-header::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: url('data:image/svg+xml,<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="smallGrid" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M 8 0 L 0 0 0 8" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23smallGrid)"/></svg>');
		opacity: 0.3;
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
		position: relative;
		z-index: 1;
	}

	.header-info h1 {
		font-size: 2.5rem;
		font-weight: 800;
		margin: 0 0 8px 0;
		background: linear-gradient(45deg, #ffffff, #e2e8f0);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		text-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.header-info p {
		font-size: 1.1rem;
		opacity: 0.9;
		margin: 0;
	}

	.header-controls {
		display: flex;
		gap: 12px;
	}

	.btn-estadisticas, .btn-refresh {
		padding: 12px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 0.9rem;
	}

	.btn-estadisticas {
		background: rgba(255, 255, 255, 0.15);
		color: white;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.btn-estadisticas:hover, .btn-estadisticas.activo {
		background: rgba(255, 255, 255, 0.25);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.btn-refresh {
		background: rgba(255, 255, 255, 0.9);
		color: #374151;
	}

	.btn-refresh:hover {
		background: white;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.btn-refresh:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	.stats-rapidas {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 20px;
		position: relative;
		z-index: 1;
	}

	.stat-item {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 12px;
		padding: 20px;
		text-align: center;
		transition: transform 0.3s ease;
	}

	.stat-item:hover {
		transform: translateY(-4px);
		background: rgba(255, 255, 255, 0.15);
	}

	.stat-numero {
		display: block;
		font-size: 2rem;
		font-weight: 800;
		margin-bottom: 4px;
	}

	.stat-etiqueta {
		font-size: 0.9rem;
		opacity: 0.9;
	}

	/* Secciones */
	.seccion-estadisticas, .seccion-filtros, .seccion-tabla {
		margin-bottom: 24px;
	}

	/* Estados de carga y error */
	.loading-container {
		background: white;
		border-radius: 16px;
		padding: 60px;
		text-align: center;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}

	.loading-content h3 {
		color: #374151;
		margin: 20px 0 8px 0;
		font-size: 1.5rem;
	}

	.loading-content p {
		color: #6b7280;
		margin: 0;
	}

	.spinner-ring {
		width: 60px;
		height: 60px;
		border: 4px solid #f3f4f6;
		border-top: 4px solid #667eea;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 20px;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.error-container, .sin-resultados-container, .sin-datos-container {
		background: white;
		border-radius: 16px;
		padding: 60px;
		text-align: center;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}

	.error-content, .sin-resultados-content, .sin-datos-content {
		max-width: 500px;
		margin: 0 auto;
	}

	.error-icon, .sin-resultados-icon, .sin-datos-icon {
		font-size: 4rem;
		margin-bottom: 20px;
		display: block;
	}

	.error-content h3, .sin-resultados-content h3, .sin-datos-content h3 {
		color: #374151;
		margin: 0 0 12px 0;
		font-size: 1.5rem;
	}

	.error-content p, .sin-resultados-content p, .sin-datos-content p {
		color: #6b7280;
		margin: 0 0 8px 0;
		line-height: 1.6;
	}

	.hint {
		font-size: 0.9rem;
		font-style: italic;
		opacity: 0.8;
	}

	.btn-retry {
		margin-top: 20px;
		padding: 12px 24px;
		background: #dc2626;
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.btn-retry:hover {
		background: #b91c1c;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
	}

	/* Responsive */
	@media (max-width: 768px) {
		.auditoria-container {
			padding: 16px;
		}

		.auditoria-header {
			padding: 24px 20px;
		}

		.header-content {
			flex-direction: column;
			gap: 16px;
			align-items: stretch;
		}

		.header-controls {
			justify-content: center;
		}

		.header-info h1 {
			font-size: 2rem;
			text-align: center;
		}

		.stats-rapidas {
			grid-template-columns: 1fr;
		}

		.loading-container, .error-container, .sin-resultados-container, .sin-datos-container {
			padding: 40px 20px;
		}
	}

	@media (max-width: 480px) {
		.header-info h1 {
			font-size: 1.7rem;
		}

		.btn-estadisticas, .btn-refresh {
			padding: 10px 16px;
			font-size: 0.85rem;
		}

		.stat-numero {
			font-size: 1.5rem;
		}

		.stat-etiqueta {
			font-size: 0.8rem;
		}
	}
</style>
