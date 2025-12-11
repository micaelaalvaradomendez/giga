<script>
	import { createEventDispatcher } from "svelte";

	export let isOpen = false;
	export let isSaving = false;
	export let tipoHorarios = "areas"; // 'areas' o 'agrupaciones'
	export let selectedItem = null;
	export let formData = { horario_entrada: "08:00", horario_salida: "17:00" };

	const dispatch = createEventDispatcher();

	function cerrarModal() {
		if (!isSaving) {
			dispatch("cerrar");
		}
	}

	function guardarHorarios() {
		if (!isSaving && formData.horario_entrada && formData.horario_salida) {
			dispatch("guardar", {
				horario_entrada: formData.horario_entrada,
				horario_salida: formData.horario_salida,
				tipo: tipoHorarios,
				target: selectedItem,
			});
		}
	}
</script>

{#if isOpen}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={cerrarModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content horarios-modal" on:click|stopPropagation>
			<div class="modal-header">
				<h2>
					⏰ Horarios - {selectedItem?.nombre || "Sin seleccionar"}
				</h2>
				<button
					class="modal-close"
					on:click={cerrarModal}
					aria-label="Cerrar Modal">×</button
				>
			</div>
			<div class="modal-body">
				<div class="alert-info">
					<strong>⚠️ Importante:</strong> Los horarios se aplicarán a
					<strong>todos los agentes</strong>
					de esta
					{tipoHorarios === "areas" ? "área" : "agrupación"}.
				</div>

				<div class="form-row">
					<div class="form-group">
						<label for="horarioEntrada">Horario de Entrada *</label>
						<input
							type="time"
							id="horarioEntrada"
							bind:value={formData.horario_entrada}
							required
							disabled={isSaving}
							class="hora-input"
						/>
					</div>
					<div class="form-group">
						<label for="horarioSalida">Horario de Salida *</label>
						<input
							type="time"
							id="horarioSalida"
							bind:value={formData.horario_salida}
							required
							disabled={isSaving}
							class="hora-input"
						/>
					</div>
				</div>
			</div>
			<div class="modal-footer">
				<button
					class="btn-cancel"
					on:click={cerrarModal}
					disabled={isSaving}
				>
					Cancelar
				</button>
				<button
					class="btn-save"
					on:click={guardarHorarios}
					disabled={isSaving}
				>
					{isSaving ? "Guardando..." : "Guardar Horarios"}
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
		max-width: 600px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: modalSlide 0.3s ease-out;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-content::-webkit-scrollbar {
		display: none;
	}

	.horarios-modal {
		max-width: 700px;
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
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
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
		padding: 25px;
	}

	.modal-footer {
		padding: 20px 25px;
		border-top: 1px solid #e9ecef;
		display: flex;
		justify-content: flex-end;
		gap: 10px;
		background: #f8f9fa;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
		align-items: end;
	}

	.form-group {
		margin-bottom: 20px;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 600;
		color: #495057;
	}

	.alert-info {
		background: #d1ecf1;
		color: #0c5460;
		padding: 15px;
		border-radius: 8px;
		margin-bottom: 20px;
		border-left: 4px solid #bee5eb;
	}

	.hora-input {
		width: 90%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.hora-input:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.hora-input:disabled {
		background-color: #e9ecef;
		cursor: not-allowed;
	}

	.btn-cancel,
	.btn-save {
		padding: 12px 24px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-cancel {
		background: #6c757d;
		color: white;
	}

	.btn-cancel:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-2px);
	}

	.btn-save {
		background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
		color: white;
	}

	.btn-save:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
	}

	.btn-save:disabled,
	.btn-cancel:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	@media (max-width: 600px) {
		.form-row {
			grid-template-columns: 1fr;
		}
	}
</style>
