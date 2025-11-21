<script>
	import { createEventDispatcher } from 'svelte';

	export let isOpen = false;
	export let isSaving = false;

	let horarioEntrada = '';
	let horarioSalida = '';

	const dispatch = createEventDispatcher();

	function cerrar() {
		horarioEntrada = '';
		horarioSalida = '';
		dispatch('cerrar');
	}

	function guardar() {
		if (!horarioEntrada || !horarioSalida) {
			alert('Debe completar ambos horarios');
			return;
		}

		if (horarioEntrada >= horarioSalida) {
			alert('La hora de entrada debe ser anterior a la hora de salida');
			return;
		}

		dispatch('guardar', {
			horario_entrada: horarioEntrada,
			horario_salida: horarioSalida
		});
	}

	// Resetear valores cuando se abre el modal
	$: if (isOpen) {
		horarioEntrada = '';
		horarioSalida = '';
	}
</script>

{#if isOpen}
	<div class="modal-overlay" on:click={cerrar}>
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>🕐 Establecer Horario Global</h2>
				<button class="btn-close" on:click={cerrar} disabled={isSaving}>×</button>
			</div>

			<div class="modal-body">
				<div class="info-section">
					<p class="info-text">
						<strong>ℹ️ Información:</strong><br>
						Este horario se aplicará a <strong>todos los agentes activos</strong> del sistema.
						Los horarios específicos por área o agrupación tienen prioridad sobre este horario global.
					</p>
				</div>

				<div class="form-group">
					<label for="horario_entrada_global">
						<span class="label-icon">🕐</span>
						Hora de Entrada
					</label>
					<input
						type="time"
						id="horario_entrada_global"
						bind:value={horarioEntrada}
						disabled={isSaving}
						required
					/>
				</div>

				<div class="form-group">
					<label for="horario_salida_global">
						<span class="label-icon">🕐</span>
						Hora de Salida
					</label>
					<input
						type="time"
						id="horario_salida_global"
						bind:value={horarioSalida}
						disabled={isSaving}
						required
					/>
				</div>

				<div class="preview-section">
					<div class="preview-card">
						<span class="preview-label">Vista Previa:</span>
						<span class="preview-value">
							{horarioEntrada || '--:--'} → {horarioSalida || '--:--'}
						</span>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<button class="btn-cancel" on:click={cerrar} disabled={isSaving}>
					Cancelar
				</button>
				<button class="btn-save" on:click={guardar} disabled={isSaving}>
					{#if isSaving}
						⏳ Aplicando...
					{:else}
						✓ Aplicar a Todos
					{/if}
				</button>
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
		align-items: center;
		justify-content: center;
		z-index: 2000;
		animation: fadeIn 0.2s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal-content {
		background: white;
		border-radius: 16px;
		max-width: 550px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s ease-out;
	}

	@keyframes slideUp {
		from {
			transform: translateY(30px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 2rem;
		border-bottom: 2px solid #f0f0f0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 16px 16px 0 0;
	}

	.modal-header h2 {
		margin: 0;
		color: white;
		font-size: 1.5rem;
		font-weight: 700;
	}

	.btn-close {
		background: rgba(255, 255, 255, 0.2);
		border: none;
		font-size: 2rem;
		cursor: pointer;
		color: white;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.3s ease;
		line-height: 1;
	}

	.btn-close:hover:not(:disabled) {
		background: rgba(255, 255, 255, 0.3);
		transform: rotate(90deg);
	}

	.btn-close:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.modal-body {
		padding: 2rem;
	}

	.info-section {
		background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
		padding: 1.25rem;
		border-radius: 12px;
		margin-bottom: 1.5rem;
		border-left: 4px solid #2196f3;
	}

	.info-text {
		margin: 0;
		color: #1565c0;
		line-height: 1.6;
		font-size: 0.95rem;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	.form-group label {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: 600;
		color: #333;
		margin-bottom: 0.5rem;
		font-size: 1rem;
	}

	.label-icon {
		font-size: 1.2rem;
	}

	input[type='time'] {
		width: 100%;
		padding: 12px 16px;
		border: 2px solid #e0e0e0;
		border-radius: 10px;
		font-size: 1.1rem;
		transition: all 0.3s ease;
		background: #fafafa;
		font-family: inherit;
	}

	input[type='time']:focus {
		outline: none;
		border-color: #667eea;
		background: white;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	input[type='time']:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		background: #f5f5f5;
	}

	.preview-section {
		margin-top: 1.5rem;
	}

	.preview-card {
		background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
		padding: 1rem 1.5rem;
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border: 2px dashed #ccc;
	}

	.preview-label {
		font-weight: 600;
		color: #666;
		font-size: 0.9rem;
	}

	.preview-value {
		font-size: 1.3rem;
		font-weight: 700;
		color: #667eea;
		font-family: monospace;
	}

	.modal-footer {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		padding: 1.5rem 2rem;
		border-top: 2px solid #f0f0f0;
		background: #fafafa;
		border-radius: 0 0 16px 16px;
	}

	.btn-cancel,
	.btn-save {
		padding: 12px 28px;
		border: none;
		border-radius: 10px;
		font-weight: 600;
		cursor: pointer;
		font-size: 1rem;
		transition: all 0.3s ease;
	}

	.btn-cancel {
		background: #e0e0e0;
		color: #333;
	}

	.btn-cancel:hover:not(:disabled) {
		background: #d0d0d0;
		transform: translateY(-2px);
	}

	.btn-save {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
	}

	.btn-save:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
	}

	.btn-cancel:disabled,
	.btn-save:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}
</style>
