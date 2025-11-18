<script>
	import { createEventDispatcher } from "svelte";

	export let isOpen = false;
	export let isSaving = false;
	export let formData = { id_area: null, nombre: "", activo: true };

	const dispatch = createEventDispatcher();

	function cerrarModal() {
		if (!isSaving) {
			dispatch("cerrar");
		}
	}

	function guardar() {
		if (formData.nombre.trim() && !isSaving) {
			dispatch("guardar", formData);
		}
	}
</script>

{#if isOpen}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={cerrarModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>{formData.id_area ? "✏️ Editar" : "➕ Nueva"} Área</h2>
				<button
					class="modal-close"
					on:click={cerrarModal}
					aria-label="Cerrar Modal">×</button
				>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label for="areaNombre">Nombre del Área *</label>
					<input
						type="text"
						id="areaNombre"
						bind:value={formData.nombre}
						placeholder="Ej: Secretaría de Protección Civil"
						required
						disabled={isSaving}
					/>
				</div>

				<div class="checkbox-group">
					<label class="checkbox-label">
						<input
							type="checkbox"
							bind:checked={formData.activo}
							disabled={isSaving}
						/>
						<span class="checkbox-custom"></span>
						Área activa
					</label>
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
					on:click={guardar}
					disabled={isSaving || !formData.nombre.trim()}
				>
					{isSaving ? "Guardando..." : "Guardar Área"}
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
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: modalSlide 0.3s ease-out;
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

	.form-group {
		margin-bottom: 20px;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 600;
		color: #495057;
	}

	.form-group input {
		width: 90%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.form-group input:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.form-group input:disabled {
		background-color: #e9ecef;
		cursor: not-allowed;
	}

	.checkbox-group {
		display: flex;
		align-items: center;
		margin: 15px 0;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		cursor: pointer;
		font-weight: 600;
		color: #495057;
	}

	.checkbox-label input[type="checkbox"] {
		display: none;
	}

	.checkbox-custom {
		width: 20px;
		height: 20px;
		border: 2px solid #ddd;
		border-radius: 4px;
		margin-right: 10px;
		position: relative;
		transition: all 0.3s ease;
	}

	.checkbox-label input:checked + .checkbox-custom {
		background: #3498db;
		border-color: #3498db;
	}

	.checkbox-label input:checked + .checkbox-custom::after {
		content: "✓";
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: white;
		font-weight: bold;
		font-size: 12px;
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
</style>
