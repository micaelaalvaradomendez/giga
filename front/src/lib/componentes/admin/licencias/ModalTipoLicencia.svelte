<script>
	import { createEventDispatcher } from "svelte";

	export let show = false;
	export let isEditing = false;
	export let form = { codigo: "", descripcion: "" };
	export let error = null;
	export let saving = false;

	const dispatch = createEventDispatcher();

	function guardar() {
		dispatch("guardar");
	}

	function cancelar() {
		dispatch("cancelar");
	}
</script>

{#if show}
	<div class="modal-overlay">
		<div class="modal">
			<h3>
				{isEditing
					? "Editar tipo de licencia"
					: "Nuevo tipo de licencia"}
			</h3>
			{#if error}
				<div class="alert alert-error">{error}</div>
			{/if}
			<div class="form-row">
				<label for="codigo">Código / Nombre *</label>
				<input
					id="codigo"
					bind:value={form.codigo}
					placeholder="Ej: VAC, ENF, etc."
					required
				/>
			</div>
			<div class="form-row">
				<label for="desc">Descripción</label>
				<textarea
					id="desc"
					rows="3"
					bind:value={form.descripcion}
					placeholder="Descripción del tipo de licencia"
				></textarea>
			</div>
			<div class="form-actions">
				<button
					class="btn-primary"
					on:click={guardar}
					disabled={saving}
				>
					{saving ? "Guardando..." : "Guardar"}
				</button>
				<button
					class="btn-limpiar"
					on:click={cancelar}
					disabled={saving}
				>
					Cancelar
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

	.modal {
		background: white;
		padding: 2rem;
		border-radius: 16px;
		width: 520px;
		max-width: 92%;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: modalSlideIn 0.3s ease-out;
		border: 1px solid #e5e7eb;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal::-webkit-scrollbar {
		display: none;
	}

	.modal h3 {
		margin-top: 0;
		color: #1e293b;
		margin-bottom: 1.5rem;
		font-size: 1.5rem;
		text-align: center;
		font-weight: 700;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e5e7eb;
	}

	.form-row {
		margin-bottom: 1.5rem;
	}

	.form-row label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
	}

	.form-row input,
	.form-row textarea {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.9rem;
		transition: all 0.2s;
		font-family: inherit;
		box-sizing: border-box;
	}

	.form-row input:focus,
	.form-row textarea:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 2rem;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.btn-primary {
		padding: 0.75rem 1.5rem;
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
	}

	.btn-primary:hover:not(:disabled) {
		background: linear-gradient(135deg, #059669, #047857);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
	}

	.btn-primary:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.btn-limpiar {
		padding: 0.75rem 1.5rem;
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 2px 4px rgba(107, 114, 128, 0.3);
	}

	.btn-limpiar:hover:not(:disabled) {
		background: linear-gradient(135deg, #4b5563, #374151);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(107, 114, 128, 0.4);
	}

	.alert {
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1.5rem;
		font-weight: 500;
	}

	.alert-error {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fecaca;
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
