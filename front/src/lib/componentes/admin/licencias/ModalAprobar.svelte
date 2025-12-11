<script>
	import { createEventDispatcher } from "svelte";

	// Props
	export let show = false;
	export let licencia = null;

	const dispatch = createEventDispatcher();

	let formAprobacion = { observaciones: "" };

	// Reset al cerrar modal principal
	$: if (!show) {
		formAprobacion = { observaciones: "" };
	}

	function cerrarModal() {
		show = false;
		dispatch("close");
	}

	function handleAprobar() {
		if (!licencia?.id_licencia) {
			alert("Error: No se ha seleccionado una licencia válida");
			return;
		}

		dispatch("aprobar", { observaciones: formAprobacion.observaciones });
	}
</script>

{#if show && licencia}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Aprobar Licencia</h5>
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

				<form on:submit|preventDefault={handleAprobar}>
					<div class="form-group">
						<label for="observaciones_aprobar"
							>Observaciones de Aprobación</label
						>
						<textarea
							id="observaciones_aprobar"
							bind:value={formAprobacion.observaciones}
							placeholder="Ingrese observaciones sobre la aprobación (opcional)..."
							rows="3"
						></textarea>
					</div>

					<div class="modal-footer">
						<button
							type="button"
							class="btn-secondary"
							on:click={cerrarModal}
						>
							Cancelar
						</button>
						<button type="submit" class="btn-success">
							✅ Aprobar Licencia
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
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 4px;
		padding: 1rem;
		margin-bottom: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.licencia-info h6 {
		font-size: 16px;
		margin: 0 0 0.5rem 0;
		color: #495057;
	}

	.info-row {
		margin-bottom: 0.25rem;
		font-size: 0.9rem;
		width: 100%;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 10px;
		font-weight: 600;
		color: #313131;
	}

	.form-group textarea {
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 16px;
		transition: all 0.3s ease;
		font-family: inherit;
		width: 94%;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.btn-secondary,
	.btn-success {
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-success {
		background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
		color: white;
	}

	.btn-success:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-2px);
	}

	.btn-success:disabled,
	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}
</style>
