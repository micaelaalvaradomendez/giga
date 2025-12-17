<script>
	import { createEventDispatcher } from "svelte";
	export let agente = null;
	export let isOpen = false;
	const dispatch = createEventDispatcher();
	function cerrarModal() {
		isOpen = false;
		dispatch("cerrar");
	}
	function formatearFecha(fecha) {
		if (!fecha) return "N/A";
		return new Date(fecha).toLocaleDateString("es-AR");
	}
	function formatearHora(hora) {
		if (!hora) return "N/A";
		return hora;
	}
	function abrirGoogleMaps(direccion) {
		if (!direccion) return;
		const direccionCodificada = encodeURIComponent(direccion);
		const urlMaps = `https://www.google.com/maps/search/?api=1&query=${direccionCodificada}`;
		window.open(urlMaps, "_blank");
	}
</script>
{#if isOpen && agente}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={cerrarModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>Detalles del Agente</h2>
				<button class="btn-close" on:click={cerrarModal}>×</button>
			</div>
			<div class="modal-body">
				<div class="info-grid">
					<!-- Información Personal -->
					<div class="info-section">
						<h3>Información Personal</h3>
						<div class="info-row">
							<span class="label">Nombre Completo:</span>
							<span class="value"
								>{agente.nombre} {agente.apellido}</span
							>
						</div>
						<div class="info-row">
							<span class="label">DNI:</span>
							<span class="value">{agente.dni}</span>
						</div>
						<div class="info-row">
							<span class="label">CUIL:</span>
							<span class="value">{agente.cuil || "N/A"}</span>
						</div>
						<div class="info-row">
							<span class="label">Fecha de Nacimiento:</span>
							<span class="value"
								>{formatearFecha(agente.fecha_nacimiento)}</span
							>
						</div>
						<div class="info-row">
							<span class="label">Email:</span>
							<span class="value email-value" title={agente.email}
								>{agente.email}</span
							>
						</div>
						<div class="info-row">
							<span class="label">Teléfono:</span>
							<span class="value">{agente.telefono || "N/A"}</span
							>
						</div>
						<div class="info-row">
							<span class="label">Dirección:</span>
							<span class="value direccion-value">
								{#if agente.direccion_completa}
									<span
										class="direccion-text"
										title={agente.direccion_completa}
										>{agente.direccion_completa}</span
									>
									<button
										class="btn-maps"
										title="Ver en Google Maps"
										on:click={() =>
											abrirGoogleMaps(
												agente.direccion_completa,
											)}
									>
										🗺️
									</button>
								{:else}
									N/A
								{/if}
							</span>
						</div>
					</div>
					<!-- Información Laboral -->
					<div class="info-section">
						<h3>Información Laboral</h3>
						<div class="info-row">
							<span class="label">Legajo:</span>
							<span class="value">{agente.legajo || "N/A"}</span>
						</div>
						<div class="info-row">
							<span class="label">Roles:</span>
							{#if agente.roles && agente.roles.length > 0}
								<div class="roles-list">
									{#each agente.roles as rol}
										<div class="role-card">
											<span class="badge badge-role"
												>{rol.nombre}</span
											>
											{#if rol.descripcion}
												<small class="area-text"
													>{rol.descripcion}</small
												>
											{/if}
											{#if rol.asignado_en}
												<small class="fecha-text"
													>Desde: {formatearFecha(
														rol.asignado_en,
													)}</small
												>
											{/if}
										</div>
									{/each}
								</div>
							{:else}
								<p class="no-roles">Sin roles asignados</p>
							{/if}
						</div>
						<div class="info-row">
							<span class="label">Agrupación:</span>
							<span class="value">
								{#if agente.agrupacion_display}
									<span
										class="badge badge-{agente.agrupacion?.toLowerCase()}"
										>{agente.agrupacion_display}</span
									>
								{:else}
									N/A
								{/if}
							</span>
						</div>
						<div class="info-row">
							<span class="label">Área:</span>
							<span class="value">
								{#if agente.area_nombre}
									<span class="badge badge-area"
										>{agente.area_nombre}</span
									>
								{:else}
									Sin área asignada
								{/if}
							</span>
						</div>
						<div class="info-row">
							<span class="label">Categoría:</span>
							<span class="value"
								>{agente.categoria_revista || "N/A"}</span
							>
						</div>
						<div class="info-row">
							<span class="label">Horario Entrada:</span>
							<span class="value"
								>{formatearHora(agente.horario_entrada)}</span
							>
						</div>
						<div class="info-row">
							<span class="label">Horario Salida:</span>
							<span class="value"
								>{formatearHora(agente.horario_salida)}</span
							>
						</div>
						<div class="info-row">
							<span class="label">Estado:</span>
							<span class="value">
								{#if agente.activo}
									<span class="badge badge-activo"
										>✅ Activo</span
									>
								{:else}
									<span class="badge badge-inactivo"
										>❌ Inactivo</span
									>
								{/if}
							</span>
						</div>
					</div>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn btn-secondary" on:click={cerrarModal}
					>Cerrar</button
				>
			</div>
		</div>
	</div>
{/if}
<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
	}
	.modal-content {
		background: white;
		border-radius: 8px;
		max-width: 800px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		scrollbar-width: none;
		-ms-overflow-style: none;
	}
	.modal-content::-webkit-scrollbar {
		display: none;
	}
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e9ecef;
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		border-radius: 8px 8px 0 0;
	}
	.modal-header h2 {
		margin: 0;
		font-size: 1.5rem;
	}
	.btn-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		color: white;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 4px;
		transition: background-color 0.2s;
	}
	.btn-close:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}
	.modal-body {
		padding: 1.5rem;
	}
	.info-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
	}
	.info-section {
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1rem;
		background: #f8f9fa;
	}
	.info-section h3 {
		margin: 0 0 1rem 0;
		color: #2c3e50;
		font-size: 1.1rem;
		padding-bottom: 0.5rem;
		border-bottom: 2px solid #e79043;
	}
	.info-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 0.75rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid #e9ecef;
		gap: 0.5rem;
	}
	.info-row:last-child {
		border-bottom: none;
		margin-bottom: 0;
	}
	.label {
		font-weight: 500;
		color: #495057;
		flex-shrink: 0;
		margin-right: 1rem;
	}
	.value {
		text-align: right;
		color: #212529;
		word-break: break-word;
		overflow-wrap: break-word;
	}
	.email-value {
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.direccion-value {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	.direccion-text {
		max-width: 180px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		flex-shrink: 1;
	}
	.btn-maps {
		background: none;
		border: none;
		font-size: 1.2rem;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 4px;
		transition: all 0.2s;
		flex-shrink: 0;
	}
	.btn-maps:hover {
		background-color: #e9ecef;
		transform: scale(1.1);
	}
	.roles-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	.role-card {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem;
		background: white;
		border-radius: 4px;
		border: 1px solid #e9ecef;
	}
	.area-text {
		color: #6c757d;
		font-style: italic;
	}
	.no-roles {
		color: #6c757d;
		font-style: italic;
		margin: 0;
	}
	.modal-footer {
		padding: 1rem 1.5rem;
		border-top: 1px solid #e9ecef;
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
	}
	.btn {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s;
	}
	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}
	.btn-secondary:hover {
		background-color: #5a6268;
	}
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
	}
	.badge-area {
		background-color: #d1ecf1;
		color: #0c5460;
		border: 1px solid #bee5eb;
	}
	.badge-activo {
		background-color: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}
	.badge-inactivo {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}
	.fecha-text {
		color: #6c757d;
		font-style: italic;
		display: block;
		margin-top: 0.25rem;
	}
	@media (max-width: 768px) {
		.modal-overlay {
			align-items: flex-start;
			padding: 0.5rem;
		}
		.modal-content {
			width: 100%;
			margin: 0;
			max-height: 95vh;
			border-radius: 8px;
		}
		.modal-header {
			padding: 1rem;
		}
		.modal-header h2 {
			font-size: 1.1rem;
		}
		.modal-body {
			padding: 1rem;
		}
		.info-grid {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
		.info-section {
			padding: 0.75rem;
		}
		.info-row {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.25rem;
			margin-bottom: 0.5rem;
		}
		.label {
			margin-right: 0;
			font-size: 0.85rem;
			color: #6c757d;
		}
		.value {
			text-align: left;
			width: 100%;
			font-size: 0.95rem;
		}
		.email-value {
			max-width: none;
		}
		.direccion-text {
			max-width: none;
		}
		.direccion-value {
			justify-content: flex-start;
			width: 100%;
		}
	}
</style>
