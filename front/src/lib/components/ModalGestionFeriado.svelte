<script>
	import { createEventDispatcher } from 'svelte';

	export let isOpen = false;
	export let feriado = null; 
	export let selectedDate = null; 

	let nombreFeriado = '';
	let isSaving = false;
	let isDeleting = false;

	const dispatch = createEventDispatcher();
	
	$: if (isOpen) {	
		nombreFeriado = feriado ? feriado.descripcion : '';
		isSaving = false;
		isDeleting = false;
	}

	function closeModal() {
		dispatch('close');
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
			</div>
			<div class="modal-actions">
				<!-- Botón de Eliminar (ahora es un formulario separado) -->
				{#if feriado}
					<form method="POST" action="?/deleteFeriado" use:enhance on:submit={() => { if (!confirm('¿Estás seguro de que deseas eliminar este feriado?')) event.preventDefault(); else isDeleting = true; }}>
						<input type="hidden" name="id" value={feriado.id} />
						<button type="submit" class="btn-danger" disabled={isSaving || isDeleting}>
							{isDeleting ? 'Eliminando...' : 'Eliminar'}
						</button>
					</form>
				{/if}

				<!-- Formulario para Guardar/Crear -->
				<form method="POST" action={feriado ? `?/updateFeriado` : '?/createFeriado'} use:enhance on:submit={() => isSaving = true} class="save-actions">
					<input type="hidden" name="id" value={feriado?.id} />
					<input type="hidden" name="fecha" value={selectedDate} />
					<input type="hidden" name="descripcion" value={nombreFeriado} />
					
					<button type="button" class="btn-secondary" on:click={closeModal} disabled={isSaving || isDeleting}>
						Cancelar
					</button>
					<button type="submit" class="btn-primary" disabled={isSaving || isDeleting}>
						{isSaving ? 'Guardando...' : 'Guardar'}
					</button>
				</form>
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
</style>
