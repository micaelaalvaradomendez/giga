<script>
	import { createEventDispatcher } from 'svelte';

	export let agente = null;
	export let isOpen = false;
	export let isDeleting = false;

	const dispatch = createEventDispatcher();

	function cerrarModal() {
		if (!isDeleting) {
			isOpen = false;
			dispatch('cerrar');
		}
	}

	function confirmarEliminacion() {
		dispatch('confirmar', { agente });
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
				<h2>🗑️ Eliminar Agente</h2>
				{#if !isDeleting}
					<button class="btn-close" on:click={cerrarModal}>×</button>
				{/if}
			</div>
			
			<div class="modal-body">
				<div class="warning-message">
					<div class="warning-icon">⚠️</div>
					<div class="warning-text">
						<p><strong>¡Atención!</strong> Estás a punto de eliminar al agente:</p>
						<div class="agente-info">
							<p><strong>{agente.nombre} {agente.apellido}</strong></p>
							<p>DNI: {agente.dni}</p>
							<p>Legajo: {agente.legajo || 'N/A'}</p>
							<p>Email: {agente.email}</p>
						</div>
						<p class="danger-text">
							<strong>Esta acción no se puede deshacer.</strong> 
							Se eliminará toda la información del agente del sistema.
						</p>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<button 
					class="btn btn-secondary" 
					on:click={cerrarModal}
					disabled={isDeleting}
				>
					Cancelar
				</button>
				<button 
					class="btn btn-danger" 
					on:click={confirmarEliminacion}
					disabled={isDeleting}
				>
					{#if isDeleting}
						<span class="spinner"></span>
						Eliminando...
					{:else}
						Eliminar Agente
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
		justify-content: center;
		align-items: center;
		z-index: 1000;
	}

	.modal-content {
		background: white;
		border-radius: 8px;
		max-width: 500px;
		width: 90%;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e9ecef;
		background: linear-gradient(135deg, #dc3545, #c82333);
		color: white;
		border-radius: 8px 8px 0 0;
	}

	.modal-header h2 {
		margin: 0;
		font-size: 1.3rem;
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

	.warning-message {
		display: flex;
		gap: 1rem;
		align-items: flex-start;
	}

	.warning-icon {
		font-size: 2rem;
		flex-shrink: 0;
	}

	.warning-text {
		flex-grow: 1;
	}

	.warning-text p {
		margin: 0 0 1rem 0;
		color: #495057;
		line-height: 1.5;
	}

	.agente-info {
		background: #f8f9fa;
		border: 1px solid #e9ecef;
		border-radius: 4px;
		padding: 1rem;
		margin: 1rem 0;
	}

	.agente-info p {
		margin: 0.25rem 0;
		color: #212529;
	}

	.danger-text {
		color: #dc3545 !important;
		font-weight: 500;
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
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background-color: #5a6268;
	}

	.btn-danger {
		background-color: #dc3545;
		color: white;
	}

	.btn-danger:hover:not(:disabled) {
		background-color: #c82333;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>