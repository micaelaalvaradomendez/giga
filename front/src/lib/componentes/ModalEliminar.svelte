<script>
	import { createEventDispatcher } from 'svelte';

	export let isOpen = false;
	export let isDeleting = false;
	export let itemToDelete = null;
	export let type = 'item'; // 'area' o 'agrupacion'

	const dispatch = createEventDispatcher();

	function cerrarModal() {
		if (!isDeleting) {
			dispatch('cerrar');
		}
	}

	function confirmarEliminacion() {
		if (!isDeleting && itemToDelete) {
			dispatch('confirmar', itemToDelete);
		}
	}

	$: typeLabel = type === 'area' ? 'área' : 'agrupación';
</script>

{#if isOpen && itemToDelete}
	<div class="modal-overlay" on:click={cerrarModal}>
		<div class="modal-content eliminar-modal" on:click|stopPropagation>
			<div class="modal-header danger">
				<h2>🗑️ Eliminar {typeLabel}</h2>
				<button class="modal-close" on:click={cerrarModal}>×</button>
			</div>
			<div class="modal-body">
				<div class="warning-icon">
					⚠️
				</div>
				<p class="warning-text">
					¿Estás seguro de que deseas eliminar {typeLabel === 'área' ? 'el área' : 'la agrupación'} 
					<strong>"{itemToDelete.nombre}"</strong>?
				</p>
				<p class="warning-subtext">
					Esta acción no se puede deshacer. Todos los datos asociados también se eliminarán permanentemente.
				</p>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" on:click={cerrarModal} disabled={isDeleting}>
					Cancelar
				</button>
				<button class="btn-delete" on:click={confirmarEliminacion} disabled={isDeleting}>
					{isDeleting ? 'Eliminando...' : `Eliminar ${typeLabel}`}
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
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(5px);
	}

	.modal-content {
		background: white;
		border-radius: 12px;
		width: 90%;
		max-width: 450px;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: modalSlide 0.3s ease-out;
	}

	.eliminar-modal {
		border: 2px solid #dc3545;
	}

	@keyframes modalSlide {
		from {
			opacity: 0;
			transform: translateY(-50px) scale(0.9);
		}
		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	.modal-header {
		padding: 20px 25px;
		border-bottom: 1px solid #e9ecef;
		display: flex;
		justify-content: space-between;
		align-items: center;
		color: white;
	}

	.modal-header.danger {
		background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
	}

	.modal-header h2 {
		margin: 0;
		font-size: 1.3rem;
		font-weight: 600;
	}

	.modal-close {
		background: none;
		border: none;
		color: white;
		font-size: 24px;
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

	.modal-close:hover {
		background: rgba(255, 255, 255, 0.2);
	}

	.modal-body {
		padding: 30px 25px;
		text-align: center;
	}

	.warning-icon {
		font-size: 4rem;
		margin-bottom: 20px;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.1);
		}
		100% {
			transform: scale(1);
		}
	}

	.warning-text {
		font-size: 1.1rem;
		font-weight: 600;
		color: #495057;
		margin-bottom: 15px;
		line-height: 1.4;
	}

	.warning-text strong {
		color: #dc3545;
	}

	.warning-subtext {
		font-size: 0.9rem;
		color: #6c757d;
		line-height: 1.4;
		margin-bottom: 0;
	}

	.modal-footer {
		padding: 20px 25px;
		border-top: 1px solid #e9ecef;
		display: flex;
		justify-content: flex-end;
		gap: 15px;
		background: #f8f9fa;
	}

	.btn-cancel, .btn-delete {
		padding: 12px 24px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 14px;
	}

	.btn-cancel {
		background: #6c757d;
		color: white;
	}

	.btn-cancel:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-2px);
	}

	.btn-delete {
		background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
		color: white;
	}

	.btn-delete:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
	}

	.btn-delete:disabled,
	.btn-cancel:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}
</style>