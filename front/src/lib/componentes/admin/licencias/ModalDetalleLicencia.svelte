<script>
	import { createEventDispatcher, onMount } from "svelte";
	import { formatearFecha, calcularDiasLicencia } from "$lib/paneladmin/controllers/licenciasController.js";

	export let licencia;

	const dispatch = createEventDispatcher();

	// Bloquear scroll del body cuando el modal está abierto
	onMount(() => {
		// Guardar el scroll actual
		const scrollY = window.scrollY;
		
		// Bloquear scroll del body
		document.body.style.overflow = 'hidden';
		document.body.style.position = 'fixed';
		document.body.style.top = `-${scrollY}px`;
		document.body.style.width = '100%';

		// Restaurar scroll cuando se desmonte el componente
		return () => {
			document.body.style.overflow = '';
			document.body.style.position = '';
			document.body.style.top = '';
			document.body.style.width = '';
			window.scrollTo(0, scrollY);
		};
	});

	function cerrar() {
		dispatch("close");
	}

	function getEstadoColor(estado) {
		const colores = {
			pendiente: "#ed8936",
			aprobada: "#38a169",
			rechazada: "#e53e3e"
		};
		return colores[estado] || "#4c51bf";
	}
</script>

<div class="modal-backdrop" on:click={cerrar}>
	<div class="modal-contenido" on:click|stopPropagation>
		<div class="modal-header">
			<h5>📋 Detalles de Licencia</h5>
			<button type="button" class="btn-close" on:click={cerrar}>&times;</button>
		</div>

		<div class="modal-body">
			<div class="licencia-info">
				<h6>Información General</h6>
				<div class="info-row">
					<strong>👤 Agente:</strong>
					{licencia.agente_nombre || "N/A"}
				</div>

				<div class="info-row">
					<strong>🏢 Área:</strong>
					{licencia.area_nombre || "N/A"}
				</div>

				<div class="info-row">
					<strong>📝 Tipo:</strong>
					<span class="tipo-badge">{licencia.tipo_licencia_descripcion || "N/A"}</span>
				</div>

				<div class="info-row">
					<strong>📅 Período:</strong>
					{formatearFecha(licencia.fecha_desde)} - {formatearFecha(licencia.fecha_hasta)}
				</div>

				<div class="info-row">
					<strong>⏱️ Duración:</strong>
					<span class="dias-badge">{calcularDiasLicencia(licencia.fecha_desde, licencia.fecha_hasta)} días</span>
				</div>

				<div class="info-row">
					<strong>✨ Estado:</strong>
					<span class="estado-badge estado-{licencia.estado}">
						{licencia.estado.toUpperCase()}
					</span>
				</div>

				<div class="info-row">
					<strong>📨 Solicitado:</strong>
					{formatearFecha(licencia.creado_en)}
				</div>
			</div>

			{#if licencia.observaciones}
				<div class="section-box">
					<strong>💬 Observaciones:</strong>
					<div class="text-content">{licencia.observaciones}</div>
				</div>
			{/if}

			{#if licencia.justificacion}
				<div class="section-box">
					<strong>📄 Justificación:</strong>
					<div class="text-content">{licencia.justificacion}</div>
				</div>
			{/if}

			{#if licencia.estado === "aprobada"}
				<div class="section-box success-box">
					<h6>✅ Información de Aprobación</h6>
					{#if licencia.motivo_aprobacion || licencia.observaciones_aprobacion || licencia.observaciones}
						<div class="info-row">
							<strong>Motivo/Observaciones:</strong>
							<div class="text-content">
								{licencia.motivo_aprobacion || licencia.observaciones_aprobacion || licencia.observaciones}
							</div>
						</div>
					{/if}
					{#if licencia.aprobado_por_nombre}
						<div class="info-row">
							<strong>Aprobado por:</strong>
							{licencia.aprobado_por_nombre}
						</div>
					{/if}
					{#if licencia.fecha_aprobacion}
						<div class="info-row">
							<strong>Fecha:</strong>
							{formatearFecha(licencia.fecha_aprobacion)}
						</div>
					{/if}
				</div>
			{/if}

			{#if licencia.estado === "rechazada"}
				<div class="section-box error-box">
					<h6>❌ Información de Rechazo</h6>
					{#if licencia.motivo_rechazo}
						<div class="info-row">
							<strong>Motivo:</strong>
							<div class="text-content">{licencia.motivo_rechazo}</div>
						</div>
					{/if}
					{#if licencia.rechazado_por_nombre}
						<div class="info-row">
							<strong>Rechazado por:</strong>
							{licencia.rechazado_por_nombre}
						</div>
					{/if}
					{#if licencia.fecha_rechazo}
						<div class="info-row">
							<strong>Fecha:</strong>
							{formatearFecha(licencia.fecha_rechazo)}
						</div>
					{/if}
				</div>
			{/if}

			<div class="modal-footer">
				<button type="button" class="btn-secondary" on:click={cerrar}>
					Cerrar
				</button>
			</div>
		</div>
	</div>
</div>

<style>
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
		overflow-y: auto;
		padding: 20px 0;
	}

	.modal-contenido {
		background: white;
		border-radius: 16px;
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		display: flex;
		flex-direction: column;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		margin: auto;
		position: relative;
	}

	.modal-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 1.5rem 2rem;
		border-radius: 16px 16px 0 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-shrink: 0;
	}

	.modal-body {
		padding: 2rem;
		overflow-y: auto;
		flex: 1;
		-webkit-overflow-scrolling: touch;
		scrollbar-width: thin;
		scrollbar-color: #c1c7cd #f1f3f4;
	}

	.modal-body::-webkit-scrollbar {
		width: 8px;
	}

	.modal-body::-webkit-scrollbar-track {
		background: #f1f3f4;
		border-radius: 10px;
	}

	.modal-body::-webkit-scrollbar-thumb {
		background: #c1c7cd;
		border-radius: 10px;
	}

	.modal-body::-webkit-scrollbar-thumb:hover {
		background: #a8aeb4;
	}

	.modal-header h5 {
		margin: 0;
		font-size: 1.5rem;
	}

	.btn-close {
		background: none;
		border: none;
		color: white;
		font-size: 25px;
		cursor: pointer;
		padding: 0;
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		transition: all 0.3s ease;
	}

	.btn-close:hover {
		background: rgba(255, 255, 255, 0.2);
		transform: rotate(90deg);
	}

	.licencia-info {
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.licencia-info h6 {
		font-size: 16px;
		margin: 0 0 0.75rem 0;
		color: #495057;
		font-weight: 600;
	}

	.info-row {
		margin-bottom: 0.5rem;
		font-size: 0.9rem;
		display: flex;
		gap: 8px;
		align-items: baseline;
	}

	.info-row strong {
		color: #495057;
		min-width: 120px;
	}

	.section-box {
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.section-box h6 {
		font-size: 15px;
		margin: 0 0 0.75rem 0;
		color: #495057;
		font-weight: 600;
	}

	.section-box strong {
		color: #495057;
		font-size: 0.9rem;
		display: block;
		margin-bottom: 0.5rem;
	}

	.text-content {
		background: white;
		padding: 0.75rem;
		border-radius: 6px;
		border: 1px solid #e9ecef;
		font-size: 0.9rem;
		line-height: 1.5;
		color: #212529;
		margin-top: 0.5rem;
	}

	.success-box {
		background: #d4edda;
		border-color: #c3e6cb;
	}

	.success-box h6 {
		color: #155724;
	}

	.error-box {
		background: #f8d7da;
		border-color: #f5c6cb;
	}

	.error-box h6 {
		color: #721c24;
	}

	.tipo-badge {
		background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
		color: #3730a3;
		padding: 4px 10px;
		border-radius: 12px;
		font-size: 0.85rem;
		font-weight: 600;
		border: 1px solid #a5b4fc;
	}

	.dias-badge {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		color: white;
		padding: 4px 10px;
		border-radius: 12px;
		font-size: 0.85rem;
		font-weight: 700;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
	}

	.estado-badge {
		padding: 4px 10px;
		border-radius: 12px;
		font-size: 0.85rem;
		font-weight: 700;
	}

	.estado-pendiente {
		background: linear-gradient(135deg, #fef3c7, #fde68a);
		color: #92400e;
		border: 1px solid #fcd34d;
	}

	.estado-aprobada {
		background: linear-gradient(135deg, #d1fae5, #a7f3d0);
		color: #065f46;
		border: 1px solid #6ee7b7;
	}

	.estado-rechazada {
		background: linear-gradient(135deg, #fee2e2, #fecaca);
		color: #991b1b;
		border: 1px solid #fca5a5;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.btn-secondary {
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		background: #6c757d;
		color: white;
	}

	.btn-secondary:hover {
		background: #5a6268;
		transform: translateY(-2px);
	}

	@media (max-width: 768px) {
		.modal-contenido {
			width: 95%;
			max-height: 95vh;
		}

		.info-row {
			flex-direction: column;
			gap: 4px;
		}

		.info-row strong {
			min-width: auto;
		}
	}
</style>
