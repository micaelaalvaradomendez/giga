<script>
	export let show = false;
	export let type = "success"; // success, error, warning
	export let title = "";
	export let message = "";
	export let onClose = () => {};
</script>

{#if show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={onClose}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="mensaje-modal" on:click|stopPropagation>
			<div class="mensaje-header {type}">
				<div class="mensaje-icono">
					{#if type === "success"}
						<svg
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="currentColor"
						>
							<path
								d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
							/>
						</svg>
					{:else if type === "error"}
						<svg
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="currentColor"
						>
							<path
								d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
							/>
						</svg>
					{:else if type === "warning"}
						<svg
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="currentColor"
						>
							<path
								d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
							/>
						</svg>
					{/if}
				</div>
				<h3>{title}</h3>
			</div>

			<div class="mensaje-contenido">
				<p>{message}</p>
			</div>

			<div class="mensaje-acciones">
				<button class="btn-mensaje" on:click={onClose}>
					Aceptar
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
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-overlay::-webkit-scrollbar {
		display: none;
	}

	.mensaje-modal {
		max-width: 450px;
		width: 90%;
		background: white;
		border-radius: 16px;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
		overflow: hidden;
		animation: slideIn 0.3s ease-out;
	}

	.mensaje-header {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.mensaje-header.success {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		border-bottom: none;
	}

	.mensaje-header.error {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		border-bottom: none;
	}

	.mensaje-header.warning {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
		border-bottom: none;
	}

	.mensaje-icono {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.2);
	}

	.mensaje-header h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 500;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.mensaje-contenido {
		padding: 1.5rem;
	}

	.mensaje-contenido p {
		margin: 0;
		font-size: 1rem;
		line-height: 1.6;
		color: #4b5563;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		font-weight: 400;
	}

	.mensaje-acciones {
		display: flex;
		justify-content: flex-end;
		padding: 1rem 1.5rem 1.5rem;
		gap: 0.5rem;
	}

	.btn-mensaje {
		background: #3b82f6;
		color: white;
		border: none;
		padding: 0.75rem 2rem;
		border-radius: 8px;
		font-weight: 400;
		cursor: pointer;
		transition: all 0.2s ease;
		font-size: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-mensaje:hover {
		background: #2563eb;
	}

	.btn-mensaje:active {
		transform: translateY(0);
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: scale(0.9) translateY(-20px);
		}
		to {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
	}

	/* Responsive */
	@media (max-width: 768px) {
		.mensaje-modal {
			width: 95%;
			margin: 1rem;
		}

		.mensaje-header {
			padding: 1.25rem;
		}

		.mensaje-contenido,
		.mensaje-acciones {
			padding: 1rem;
		}

		.btn-mensaje {
			padding: 0.65rem 1.5rem;
		}
	}

	@media (max-width: 480px) {
		.mensaje-modal {
			width: 90%;
		}

		.mensaje-header {
			padding: 1rem;
			flex-wrap: wrap;
		}

		.mensaje-header h3 {
			font-size: 1.1rem;
		}

		.mensaje-contenido {
			padding: 1rem;
		}

		.mensaje-acciones {
			padding: 0.75rem 1rem 1rem;
		}

		.btn-mensaje {
			width: 100%;
			padding: 0.75rem;
		}
	}
</style>
