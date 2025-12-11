<script>
	import { createEventDispatcher } from "svelte";

	export let show = false;
	export let tipo = null;

	const dispatch = createEventDispatcher();

	function confirmar() {
		dispatch("confirmar");
	}

	function cancelar() {
		dispatch("cancelar");
	}
</script>

{#if show && tipo}
	<div class="modal-overlay">
		<div class="modal-confirm">
			<div class="modal-header-warning">
				<h3>⚠️ Confirmar Eliminación</h3>
			</div>
			<div class="modal-body-confirm">
				<p>
					¿Eliminar el tipo de licencia <strong
						>"{tipo.codigo || tipo.nombre}"</strong
					>?
				</p>
				<p class="warning-text">
					Esta acción fallará si hay agentes con este tipo.
				</p>
			</div>
			<div class="modal-footer-confirm">
				<button class="btn-cancelar-confirm" on:click={cancelar}>
					Cancelar
				</button>
				<button class="btn-eliminar-confirm" on:click={confirmar}>
					Eliminar
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
		justify-content: center;
		align-items: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.modal-confirm {
		background: white;
		border-radius: 16px;
		width: 480px;
		max-width: 92%;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		overflow: hidden;
		animation: modalSlideIn 0.3s ease-out;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-confirm::-webkit-scrollbar {
		display: none;
	}

	.modal-header-warning {
		background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
		padding: 1.5rem;
		color: white;
	}

	.modal-header-warning h3 {
		margin: 0;
		font-size: 20px;
		font-weight: 700;
		color: white;
	}

	.modal-body-confirm {
		padding: 2rem;
	}

	.warning-text {
		color: #d97706;
		font-size: 14px;
		font-weight: 500;
		margin-top: 1rem;
	}

	.modal-footer-confirm {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
		padding: 1.5rem;
		background: #f9fafb;
		border-top: 1px solid #e5e7eb;
	}

	.btn-cancelar-confirm {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-cancelar-confirm:hover {
		background: linear-gradient(135deg, #4b5563, #374151);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(107, 114, 128, 0.4);
	}

	.btn-eliminar-confirm {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-eliminar-confirm:hover {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
	}

	@keyframes modalSlideIn {
		from {
			opacity: 0;
			transform: translateY(-20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
