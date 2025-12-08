<script>
	import BaseModal from "./BaseModal.svelte";

	export let show = false;
	export let title = "";
	export let maxWidth = "600px";
	export let onClose = () => {};
	export let onSubmit = () => {};
	export let submitText = "Guardar";
	export let cancelText = "Cancelar";
	export let isSubmitting = false;

	function handleSubmit() {
		onSubmit();
	}
</script>

<BaseModal {show} {title} {maxWidth} {onClose}>
	<form on:submit|preventDefault={handleSubmit}>
		<div class="modal-body">
			<slot />
		</div>
		<div class="modal-footer">
			<button
				type="button"
				class="btn-cancel"
				on:click={onClose}
				disabled={isSubmitting}
			>
				{cancelText}
			</button>
			<button type="submit" class="btn-save" disabled={isSubmitting}>
				{isSubmitting ? "Guardando..." : submitText}
			</button>
		</div>
	</form>
</BaseModal>

<style>
	.modal-body {
		padding: 2rem;
	}

	.modal-footer {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		padding: 0 2rem 2rem;
	}

	.btn-cancel,
	.btn-save {
		padding: 0.75rem 1.5rem;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		border: none;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		font-size: 0.875rem;
	}

	.btn-cancel {
		background: #6c757d;
		color: white;
	}

	.btn-cancel:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
	}

	.btn-save {
		background: linear-gradient(135deg, #4c51bf, #5b21b6);
		color: white;
		box-shadow: 0 4px 15px rgba(76, 81, 191, 0.3);
	}

	.btn-save:hover:not(:disabled) {
		background: linear-gradient(135deg, #5b21b6, #6d28d9);
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(76, 81, 191, 0.4);
	}

	.btn-cancel:disabled,
	.btn-save:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	/* Form styles globals para componentes dentro del slot */
	:global(.modal-body .form-group) {
		margin-bottom: 1.5rem;
	}

	:global(.modal-body .form-group label) {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		font-size: 0.875rem;
	}

	:global(.modal-body .form-group input),
	:global(.modal-body .form-group textarea),
	:global(.modal-body .form-group select) {
		width: 100%;
		padding: 0.75rem;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 0.875rem;
		transition: all 0.3s ease;
		box-sizing: border-box;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		color: #374151;
	}

	:global(.modal-body .form-group input:focus),
	:global(.modal-body .form-group textarea:focus),
	:global(.modal-body .form-group select:focus) {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	:global(.modal-body .form-group textarea) {
		resize: vertical;
		min-height: 100px;
	}

	:global(.modal-body .form-group input:disabled),
	:global(.modal-body .form-group textarea:disabled),
	:global(.modal-body .form-group select:disabled) {
		background-color: #f5f5f5;
		cursor: not-allowed;
	}
</style>
