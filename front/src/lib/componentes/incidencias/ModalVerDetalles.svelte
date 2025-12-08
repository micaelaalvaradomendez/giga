<script>
	import BaseModal from "./BaseModal.svelte";
	import { IncidenciasService } from "$lib/services/incidencias.js";

	export let show = false;
	export let incidenciaSeleccionada = null;
	export let cargandoDetalle = false;
	export let onClose = () => {};
	export let onCambiarEstado = () => {};
</script>

<BaseModal {show} title="Detalle de Incidencia" maxWidth="900px" onClose={onClose}>
	<div class="modal-detalle-body">
		<div class="detalle-header-badges">
			{#if incidenciaSeleccionada?.fecha_resolucion}
				<span class="badge badge-resuelto"> Resuelta </span>
			{:else}
				<span class="badge badge-pendiente"> Pendiente </span>
			{/if}
		</div>

		{#if cargandoDetalle}
			<div class="loading-container">
				<div class="spinner"></div>
				<p>Cargando detalles...</p>
			</div>
		{:else if incidenciaSeleccionada}
			<div class="detalle-content">
				<!-- Información principal -->
				<div class="detalle-section">
					<div class="detalle-numero">#{incidenciaSeleccionada.numero}</div>
					<h3 class="detalle-titulo">{incidenciaSeleccionada.titulo}</h3>
				</div>

				<!-- Descripción -->
				<div class="detalle-section">
					<h4>Descripción</h4>
					<div class="detalle-descripcion">
						{incidenciaSeleccionada.descripcion}
					</div>
				</div>

				<!-- Estado y prioridad -->
				{#if incidenciaSeleccionada.estado || incidenciaSeleccionada.prioridad}
					<div class="detalle-section">
						<h4>Estado y Prioridad</h4>
						<div class="estado-prioridad-container">
							{#if incidenciaSeleccionada.estado}
								<div class="estado-actual">
									<strong>Estado:</strong>
									<span class="badge badge-{incidenciaSeleccionada.estado}">
										{incidenciaSeleccionada.estado_display ||
											incidenciaSeleccionada.estado}
									</span>
								</div>
							{/if}
							{#if incidenciaSeleccionada.prioridad}
								<div class="prioridad-actual">
									<strong>Prioridad:</strong>
									<span
										class="badge badge-prioridad-{incidenciaSeleccionada.prioridad}"
									>
										{incidenciaSeleccionada.prioridad_display ||
											incidenciaSeleccionada.prioridad}
									</span>
								</div>
							{/if}
							{#if incidenciaSeleccionada.puede_cambiar_estado}
								<button class="btn-cambiar-estado" on:click={onCambiarEstado}>
									Cambiar Estado
								</button>
							{/if}
						</div>
					</div>
				{/if}

				<!-- Información de gestión -->
				<div class="detalle-grid">
					<div class="detalle-item">
						<strong>Creada por:</strong>
						<span>
							{incidenciaSeleccionada.creado_por_nombre || "No especificado"}
						</span>
					</div>

					<div class="detalle-item">
						<strong>Fecha de creación:</strong>
						<span>
							{IncidenciasService.formatearFecha(
								incidenciaSeleccionada.fecha_creacion
							)}
						</span>
					</div>

					{#if incidenciaSeleccionada.asignado_a_nombre}
						<div class="detalle-item">
							<strong>Asignada a:</strong>
							<span>{incidenciaSeleccionada.asignado_a_nombre}</span>
						</div>
					{/if}

					{#if incidenciaSeleccionada.fecha_asignacion}
						<div class="detalle-item">
							<strong>Fecha de asignación:</strong>
							<span>
								{IncidenciasService.formatearFecha(
									incidenciaSeleccionada.fecha_asignacion
								)}
							</span>
						</div>
					{/if}

					{#if incidenciaSeleccionada.area_nombre}
						<div class="detalle-item">
							<strong>Área involucrada:</strong>
							<span>{incidenciaSeleccionada.area_nombre}</span>
						</div>
					{/if}

					{#if incidenciaSeleccionada.fecha_resolucion}
						<div class="detalle-item">
							<strong>Fecha de resolución:</strong>
							<span>
								{IncidenciasService.formatearFecha(
									incidenciaSeleccionada.fecha_resolucion
								)}
							</span>
						</div>
					{/if}
				</div>

				<!-- Resolución (si existe) -->
				{#if incidenciaSeleccionada.resolucion}
					<div class="detalle-section">
						<h4>Resolución</h4>
						<div class="detalle-resolucion">
							{incidenciaSeleccionada.resolucion}
						</div>
					</div>
				{/if}

				<!-- Comentarios de seguimiento (si existen) -->
				{#if incidenciaSeleccionada.comentarios_seguimiento && incidenciaSeleccionada.comentarios_seguimiento.length > 0}
					<div class="detalle-section comentarios-section">
						<h4>Comentarios de Seguimiento</h4>
						<div class="comentarios-lista">
							{#each incidenciaSeleccionada.comentarios_seguimiento as comentario}
								<div class="comentario-item">
									<div class="comentario-meta">
										<strong>{comentario.autor || "Usuario"}</strong>
										<span class="comentario-fecha">
											{IncidenciasService.formatearFecha(comentario.fecha)}
										</span>
									</div>
									<div class="comentario-texto">{comentario.comentario}</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</BaseModal>

<style>
	.modal-detalle-body {
		max-height: 85vh;
		overflow-y: auto;
	}

	.detalle-header-badges {
		padding: 1rem 2rem 0;
		display: flex;
		gap: 0.5rem;
	}

	.detalle-content {
		padding: 2rem;
		overflow-y: auto;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
		gap: 1rem;
		padding: 2rem;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #f3f4f6;
		border-top: 4px solid #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.detalle-section {
		margin-bottom: 2rem;
	}

	.detalle-section:last-child {
		margin-bottom: 0;
	}

	.detalle-numero {
		font-size: 0.9rem;
		color: #6b7280;
		font-weight: 600;
		margin-bottom: 0.5rem;
		font-family: "Courier New", monospace;
		background: #f3f4f6;
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 6px;
	}

	.detalle-titulo {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0 0 1rem 0;
		line-height: 1.3;
	}

	.detalle-section h4 {
		font-size: 1.1rem;
		font-weight: 700;
		color: #374151;
		margin: 0 0 0.75rem 0;
		border-bottom: 2px solid #e5e7eb;
		padding-bottom: 0.5rem;
	}

	.detalle-descripcion,
	.detalle-resolucion {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 12px;
		padding: 1.25rem;
		line-height: 1.7;
		color: #374151;
		white-space: pre-wrap;
		word-wrap: break-word;
		min-height: 60px;
	}

	.detalle-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}

	.detalle-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		padding: 1rem;
		background: #f8fafc;
		border-radius: 8px;
		border-left: 4px solid #4c51bf;
		transition: all 0.2s ease;
	}

	.detalle-item:hover {
		transform: translateX(4px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.detalle-item strong {
		font-size: 0.75rem;
		font-weight: 700;
		color: #6b7280;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.detalle-item span {
		font-size: 1rem;
		color: #1f2937;
		font-weight: 600;
	}

	.comentarios-section {
		border-top: 2px solid #e5e7eb;
		padding-top: 2rem;
		margin-top: 2rem;
	}

	.comentarios-lista {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.comentario-item {
		background: #f8fafc;
		border: 1px solid #e5e7eb;
		border-left: 4px solid #4c51bf;
		border-radius: 12px;
		padding: 1.25rem;
		transition: all 0.2s ease;
	}

	.comentario-item:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		transform: translateY(-2px);
	}

	.comentario-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
	}

	.comentario-meta strong {
		color: #374151;
		font-weight: 600;
	}

	.comentario-fecha {
		font-size: 0.875rem;
		color: #6b7280;
		font-weight: 400;
	}

	.comentario-texto {
		color: #4b5563;
		line-height: 1.6;
		font-weight: 400;
	}

	.estado-prioridad-container {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: #f8fafc;
		border-radius: 12px;
		border: 1px solid #e5e7eb;
	}

	.estado-actual,
	.prioridad-actual {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.estado-actual strong,
	.prioridad-actual strong {
		font-size: 0.875rem;
		color: #374151;
		font-weight: 600;
	}

	.btn-cambiar-estado {
		background: linear-gradient(135deg, #4c51bf, #5b21b6);
		color: white;
		border: none;
		padding: 0.6rem 1.2rem;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		margin-left: auto;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		box-shadow: 0 2px 8px rgba(76, 81, 191, 0.3);
	}

	.btn-cambiar-estado:hover {
		background: linear-gradient(135deg, #5b21b6, #6d28d9);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(76, 81, 191, 0.4);
	}

	/* Badges */
	:global(.badge) {
		padding: 0.35rem 0.85rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	:global(.badge-resuelto),
	:global(.badge-resuelta) {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
	}

	:global(.badge-pendiente),
	:global(.badge-abierta) {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
	}

	:global(.badge-en_proceso) {
		background: linear-gradient(135deg, #3b82f6, #2563eb);
		color: white;
	}

	:global(.badge-pendiente_informacion) {
		background: linear-gradient(135deg, #eab308, #ca8a04);
		color: white;
	}

	:global(.badge-cerrada) {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
	}

	/* Prioridades */
	:global(.badge-prioridad-baja) {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
	}

	:global(.badge-prioridad-media) {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
	}

	:global(.badge-prioridad-alta) {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
	}

	:global(.badge-prioridad-critica) {
		background: linear-gradient(135deg, #991b1b, #7f1d1d);
		color: white;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.detalle-content {
			padding: 0.75rem;
		}

		.detalle-grid {
			grid-template-columns: 1fr;
		}

		.detalle-descripcion,
		.detalle-resolucion {
			padding: 1rem;
			font-size: 0.95rem;
		}
	}
</style>
