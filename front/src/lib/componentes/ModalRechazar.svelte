<script>
	import { rechazarLicencia } from '$lib/paneladmin/controllers/licenciasController.js';
	
	// Props
	export let show = false;
	export let licencia = null;

	// Events
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

	// Form data
	let formRechazo = {
		motivo: ''
	};

	let enviando = false;

	// Limpiar form cuando se cierra el modal
	$: if (!show) {
		formRechazo = { motivo: '' };
		enviando = false;
	}

	function cerrarModal() {
		show = false;
		dispatch('close');
	}

	async function handleRechazar() {
		if (!licencia?.id_licencia) {
			alert('Error: No se ha seleccionado una licencia válida');
			return;
		}

		if (!formRechazo.motivo.trim()) {
			alert('Error: Debe proporcionar un motivo para rechazar la licencia');
			return;
		}

		try {
			enviando = true;
			
			console.log('❌ Rechazando licencia:', licencia.id_licencia, formRechazo);
			
			const resultado = await rechazarLicencia(licencia.id_licencia, formRechazo);
			
			if (resultado.success) {
				alert('❌ Licencia rechazada correctamente');
				cerrarModal();
				dispatch('rejected', resultado.data);
			} else {
				throw new Error(resultado.message || 'Error al rechazar la licencia');
			}
		} catch (err) {
			console.error('❌ Error rechazando licencia:', err);
			alert(`Error: ${err.message}`);
		} finally {
			enviando = false;
		}
	}
</script>

{#if show && licencia}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Rechazar Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<div class="info-row">
						<strong>Agente:</strong> {licencia.agente?.nombre} {licencia.agente?.apellido}
					</div>
					<div class="info-row">
						<strong>Tipo:</strong> {licencia.tipo_licencia?.nombre || 'N/A'}
					</div>
					<div class="info-row">
						<strong>Período:</strong> {licencia.fecha_desde} - {licencia.fecha_hasta}
					</div>
					<div class="info-row">
						<strong>Días:</strong> {licencia.dias_solicitados}
					</div>
					{#if licencia.justificacion}
						<div class="info-row">
							<strong>Justificación:</strong> {licencia.justificacion}
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
							⚠️ El motivo del rechazo es obligatorio y será notificado al solicitante.
						</small>
					</div>

					<div class="modal-footer">
						<button type="button" class="btn-secondary" on:click={cerrarModal} disabled={enviando}>
							Cancelar
						</button>
						<button type="submit" class="btn-danger" disabled={enviando || !formRechazo.motivo.trim()}>
							{enviando ? '⏳ Rechazando...' : '❌ Rechazar Licencia'}
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
	}

	.modal-contenido {
		background: white;
		border-radius: 8px;
		width: 90%;
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		border-bottom: 1px solid #eee;
	}

	.modal-header h5 {
		margin: 0;
		font-size: 1.2rem;
		color: #333;
	}

	.btn-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		color: #666;
		padding: 0;
		width: 30px;
		height: 30px;
	}

	.btn-close:hover {
		color: #000;
	}

	.modal-body {
		padding: 1rem;
	}

	.licencia-info {
		background: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 4px;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.licencia-info h6 {
		margin: 0 0 0.5rem 0;
		color: #495057;
	}

	.info-row {
		margin-bottom: 0.25rem;
		font-size: 0.9rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.25rem;
		font-weight: bold;
		color: #333;
	}

	.form-group textarea {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.form-text {
		font-size: 0.8rem;
		margin-top: 0.25rem;
		display: block;
	}

	.text-danger {
		color: #dc3545;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.btn-danger {
		background: #dc3545;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
	}

	.btn-danger:hover:not(:disabled) {
		background: #c82333;
	}

	.btn-danger:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #545b62;
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}
</style>