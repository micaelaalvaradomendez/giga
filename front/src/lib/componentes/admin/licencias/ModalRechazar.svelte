<script>
	import { createEventDispatcher } from "svelte";

	// Props
	export let show = false;
	export let licencia = null;

	const dispatch = createEventDispatcher();

	// Form data
	let formRechazo = { motivo: "" };

	// Reset al cerrar modal principal
	$: if (!show) {
		formRechazo = { motivo: "" };
	}

	function cerrarModal() {
		show = false;
		dispatch("close");
	}

	function handleRechazar() {
		if (!licencia?.id_licencia) {
			alert("Error: Licencia no válida");
			return;
		}

		if (!formRechazo.motivo.trim()) {
			alert("Debe proporcionar un motivo para rechazar la licencia.");
			return;
		}

		dispatch("rechazar", { motivo: formRechazo.motivo });
	}
</script>

{#if show && licencia}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Rechazar Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}
					>&times;</button
				>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<div class="info-row">
						<strong>Agente:</strong>
						{licencia.agente_nombre || "SIN AGENTE"}
					</div>
					<div class="info-row">
						<strong>Tipo:</strong>
						{licencia.tipo_licencia_descripcion || "N/A"}
					</div>
					<div class="info-row">
						<strong>Período:</strong>
						{licencia.fecha_desde} - {licencia.fecha_hasta}
					</div>
					<div class="info-row">
						<strong>Días:</strong>
						{licencia.dias_licencia}
					</div>
					{#if licencia.justificacion}
						<div class="info-row">
							<strong>Justificación:</strong>
							{licencia.justificacion}
						</div>
					{/if}
				</div>

				<form on:submit|preventDefault={handleRechazar}>
					<div class="form-group">
						<label for="motivo_rechazo">Motivo del Rechazo *</label>
						<textarea
							id="motivo_rechazo"
							bind:value={formRechazo.motivo}
							placeholder="Ingrese el motivo del rechazo (requerido)..."
							rows="4"
							required
						></textarea>
						<small class="form-text text-danger">
							⚠️ El motivo del rechazo es obligatorio y será
							notificado al solicitante.
						</small>
					</div>

					<div class="modal-footer">
						<button
							type="button"
							class="btn-secondary"
							on:click={cerrarModal}
						>
							Cancelar
						</button>
						<button
							type="submit"
							class="btn-danger"
							disabled={!formRechazo.motivo.trim()}
						>
							❌ Rechazar Licencia
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

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
	}

	.modal-contenido {
		background: white;
		border-radius: 16px;
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-contenido::-webkit-scrollbar {
		display: none;
	}

	.modal-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 1.5rem 2rem;
		border-radius: 16px 16px 0 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
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

	.modal-body {
		padding: 2rem;
	}

	.licencia-info {
		background: #f7f7f7;
		border: 1px solid #e1e1e1;
		border-radius: 10px;
		padding: 1.2rem;
		margin-bottom: 1.2rem;
	}

	.licencia-info h6 {
		font-size: 16px;
		margin: 0 0 0.5rem 0;
		color: #495057;
		font-weight: 600;
	}

	.info-row {
		margin-bottom: 0.3rem;
		font-size: 0.9rem;
		width: 100%;
	}

	.form-group {
		margin-bottom: 1.3rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 600;
		color: #313131;
	}

	.form-group textarea {
		width: 94%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 10px;
		font-size: 16px;
		transition: all 0.25s ease;
		font-family: inherit;
		resize: vertical;
		margin-bottom: 5px;
	}

	.form-group textarea:focus {
		border-color: #84a59d;
		box-shadow: 0 0 0 3px rgba(132, 165, 157, 0.25);
	}

	.text-danger {
		color: #dc3545;
		font-size: 16px;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.btn-danger,
	.btn-secondary {
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-danger {
		background: #c9302c;
		color: white;
	}

	.btn-danger:hover:not(:disabled) {
		background: #c9302c;
		transform: scale(1.04);
	}

	.btn-danger:disabled {
		background: #da4141;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #545b62;
		transform: scale(1.04);
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}
</style>
