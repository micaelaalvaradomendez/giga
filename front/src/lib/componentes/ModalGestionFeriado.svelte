<script>
	import { createEventDispatcher } from 'svelte';

	export let isOpen = false;
	export let feriado = null; 
	export let selectedDate = null; 
	export let isSaving = false;
	export let isDeleting = false;
	export let feriadosController;

	let nombreFeriado = '';
	let repetirAnualmente = false;

	const dispatch = createEventDispatcher();
	
	$: if (isOpen) {	
		nombreFeriado = feriado ? feriado.descripcion : '';
		repetirAnualmente = false; // Reset la opción al abrir modal
	}

	function closeModal() {
		dispatch('close');
	}

	async function handleSave() {
		if (!nombreFeriado.trim()) {
			alert('Por favor ingresa un nombre para el feriado');
			return;
		}

		try {
			await feriadosController.saveFeriado({
				id: feriado?.id || null,
				fecha: selectedDate,
				descripcion: nombreFeriado.trim(),
				repetir_anualmente: repetirAnualmente
			});
		} catch (error) {
			// El error ya se maneja en el controlador
			console.error('Error guardando feriado:', error);
		}
	}

	async function handleDelete() {
		if (!feriado?.id) return;

		if (!confirm('¿Estás seguro de que deseas eliminar este feriado?')) {
			return;
		}

		try {
			await feriadosController.deleteFeriadoFromModal(feriado.id);
		} catch (error) {
			// El error ya se maneja en el controlador
			console.error('Error eliminando feriado:', error);
		}
	}

</script>

{#if isOpen}
	<div class="modal-backdrop" on:click={closeModal}>
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>{feriado ? 'Editar Feriado' : 'Añadir Feriado'}</h2>
				<button class="close-button" on:click={closeModal}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="form-group">
					<label for="fecha-display">Fecha</label>
					<input
						id="fecha-display"
						type="text"
						value={new Date(selectedDate).toLocaleDateString('es-AR', { timeZone: 'UTC' })}
						readonly
					/>
				</div>
				<div class="form-group">
					<label for="descripcion">Nombre del Feriado</label>
					<input
						id="descripcion-input" 
						type="text"
						bind:value={nombreFeriado}
						placeholder="Ej: Día de la Independencia"
						disabled={isSaving || isDeleting}
						required
					/>
				</div>
				
				<!-- Solo mostrar opción de repetición para feriados nuevos -->
				{#if !feriado}
					<div class="form-group">
						<label class="checkbox-label">
							<input
								type="checkbox"
								bind:checked={repetirAnualmente}
								disabled={isSaving || isDeleting}
							/>
							<span class="checkmark"></span>
							Repetir este feriado todos los años (próximos 10 años)
						</label>
						{#if repetirAnualmente}
							<div class="help-text">
								Se creará este feriado para los próximos 10 años en la misma fecha.
							</div>
						{/if}
					</div>
				{/if}
			</div>
			<div class="modal-actions">
				<!-- Botón de Eliminar -->
				{#if feriado}
					<button 
						type="button" 
						class="btn-danger" 
						disabled={isSaving || isDeleting}
						on:click={handleDelete}
					>
						{isDeleting ? 'Eliminando...' : 'Eliminar'}
					</button>
				{/if}

				<div class="save-actions">
					<button 
						type="button" 
						class="btn-secondary" 
						on:click={closeModal} 
						disabled={isSaving || isDeleting}
					>
						Cancelar
					</button>
					<button 
						type="button" 
						class="btn-primary" 
						disabled={isSaving || isDeleting}
						on:click={handleSave}
					>
						{isSaving ? 'Guardando...' : 'Guardar'}
					</button>
				</div>
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
		background-color: rgba(0, 0, 0, 0.6);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
	}
	.modal-content {
		background: white;
		padding: 1.5rem;
		border-radius: 12px;
		width: 90%;
		max-width: 500px;
	}
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 1px solid #eee;
		padding-bottom: 1rem;
		margin-bottom: 1.5rem;
	}
	.modal-header h2 {
		margin: 0;
		font-size: 1.5rem;
	}
	.close-button {
		background: none;
		border: none;
		font-size: 2rem;
		cursor: pointer;
	}
	.form-group {
		margin-bottom: 1rem;
	}
	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
	}
	.form-group input {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ccc;
		border-radius: 8px;
		box-sizing: border-box;
	}
	.form-group input[readonly] {
		background-color: #f0f0f0;
	}
	.modal-actions {
		display: flex;
		justify-content: space-between; /* Alinear elementos a los extremos */
		align-items: center;
		gap: 1rem;
		margin-top: 2rem;
	}
	.save-actions {
		display: flex;
		gap: 1rem;
	}
	.btn-secondary,
	.btn-danger {
		padding: 0.7rem 1.3rem;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 600;
	}
	.btn-primary {
		background-color: #2c5282;
		color: white;
	}
	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}
	.btn-danger {
		background-color: #c53030;
		color: white;
	}
	
	/* Estilos para checkbox personalizado */
	.checkbox-label {
		display: flex;
		align-items: center;
		cursor: pointer;
		font-size: 0.9rem;
		line-height: 1.4;
		gap: 0.75rem;
	}
	
	.checkbox-label input[type="checkbox"] {
		width: auto;
		margin: 0;
	}
	
	.help-text {
		font-size: 0.8rem;
		color: #666;
		margin-top: 0.5rem;
		padding: 0.5rem;
		background-color: #f8f9fa;
		border-radius: 4px;
		border-left: 3px solid #007bff;
	}
</style>
