<script>
	import { createEventDispatcher } from "svelte";

	export let isOpen = false;
	export let feriado = null;
	export let selectedDate = null;
	export let isSaving = false;
	export let isDeleting = false;
	export let feriadosController;
	export let existingFeriados = []; // Lista de feriados existentes en la fecha

	let nombreFeriado = "";
	let descripcionFeriado = "";
	let fechaInicio = "";
	let fechaFin = "";
	let esNacional = true;
	let esProvincial = false;
	let esLocal = false;
	let esMultiplesDias = false;
	let repetirAnualmente = false;
	let modoEdicion = false;
	let modalInitialized = false;

	const dispatch = createEventDispatcher();

	// Solo inicializar cuando el modal se abre por primera vez
	$: if (isOpen && !modalInitialized) {
		modalInitialized = true;
		if (feriado) {
			// Modo edición
			modoEdicion = true;
			nombreFeriado = feriado.nombre || "";
			descripcionFeriado = feriado.descripcion || "";
			fechaInicio = feriado.fecha_inicio || selectedDate;
			fechaFin = feriado.fecha_fin || selectedDate;
			esNacional = feriado.es_nacional || false;
			esProvincial = feriado.es_provincial || false;
			esLocal = feriado.es_local || false;
			esMultiplesDias = fechaInicio && fechaFin && fechaInicio !== fechaFin;
		} else {
			// Modo creación
			modoEdicion = false;
			nombreFeriado = "";
			descripcionFeriado = "";
			fechaInicio = selectedDate;
			fechaFin = selectedDate;
			esNacional = true;
			esProvincial = false;
			esLocal = false;
			esMultiplesDias = false;
			repetirAnualmente = false;
		}
	}

	// Resetear flag cuando el modal se cierra
	$: if (!isOpen) {
		modalInitialized = false;
	}

	// Función para manejar el cambio del checkbox esMultiplesDias
	function handleMultipleDaysToggle() {
		if (!esMultiplesDias) {
			fechaFin = fechaInicio;
		}
	}

	function closeModal() {
		dispatch("close");
	}

	async function handleSave() {
		if (!nombreFeriado.trim()) {
			alert("Por favor ingresa un nombre para el feriado");
			return;
		}

		if (!fechaInicio || !fechaFin) {
			alert("Por favor selecciona las fechas");
			return;
		}

		if (new Date(fechaFin) < new Date(fechaInicio)) {
			alert("La fecha fin debe ser mayor o igual a la fecha inicio");
			return;
		}

		try {
			await feriadosController.saveFeriado({
				id_feriado: feriado?.id_feriado || null,
				nombre: nombreFeriado.trim(),
				descripcion: descripcionFeriado.trim(),
				fecha_inicio: fechaInicio,
				fecha_fin: fechaFin,
				es_nacional: esNacional,
				es_provincial: esProvincial,
				es_local: esLocal,
				repetir_anualmente: repetirAnualmente && !modoEdicion, // Solo para feriados nuevos
			});
		} catch (error) {
			// El error ya se maneja en el controlador
			console.error("Error guardando feriado:", error);
		}
	}

	async function handleDelete() {
		if (!feriado?.id_feriado) return;

		if (!confirm("¿Estás seguro de que deseas eliminar este feriado?")) {
			return;
		}

		try {
			await feriadosController.deleteFeriadoFromModal(feriado.id_feriado);
		} catch (error) {
			// El error ya se maneja en el controlador
			console.error("Error eliminando feriado:", error);
		}
	}
</script>

{#if isOpen}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-backdrop" on:click={closeModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>
					{modoEdicion ? "Editar Feriado" : "Agregar Feriado"}
					{#if existingFeriados.length > 0 && !modoEdicion}
						<span class="existing-count">({existingFeriados.length} feriado{existingFeriados.length > 1 ? 's' : ''} existente{existingFeriados.length > 1 ? 's' : ''})</span>
					{/if}
				</h2>
				<button class="close-button" on:click={closeModal}>&times;</button>
			</div>
			<div class="modal-body">
				<!-- Mostrar feriados existentes si los hay -->
				{#if existingFeriados.length > 0 && !modoEdicion}
					<div class="existing-feriados">
						<h4>Feriados existentes en esta fecha:</h4>
						<div class="existing-list">
							{#each existingFeriados as existingFeriado}
								<div class="existing-item">
									<span class="existing-name">{existingFeriado.nombre}</span>
									<span class="existing-type">{existingFeriado.tipo_feriado}</span>
									{#if existingFeriado.es_multiples_dias}
										<span class="existing-duration">({existingFeriado.duracion_dias} días)</span>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Campos del formulario -->
				<div class="form-group">
					<label for="nombre">Nombre del Feriado</label>
					<input
						id="nombre"
						type="text"
						bind:value={nombreFeriado}
						placeholder="Ej: Día de la Independencia"
						disabled={isSaving || isDeleting}
						required
					/>
				</div>

				<div class="form-group">
					<label for="descripcion">Descripción (opcional)</label>
					<textarea
						id="descripcion"
						bind:value={descripcionFeriado}
						placeholder="Descripción adicional del feriado"
						disabled={isSaving || isDeleting}
					></textarea>
				</div>

				<!-- Tipo de feriado -->
				<div class="form-group">
					<label>Tipo de Feriado</label>
					<div class="checkbox-group">
						<label class="checkbox-label">
							<input type="checkbox" bind:checked={esNacional} disabled={isSaving || isDeleting} />
							Nacional
						</label>
						<label class="checkbox-label">
							<input type="checkbox" bind:checked={esProvincial} disabled={isSaving || isDeleting} />
							Provincial
						</label>
						<label class="checkbox-label">
							<input type="checkbox" bind:checked={esLocal} disabled={isSaving || isDeleting} />
							Local
						</label>
					</div>
				</div>

				<!-- Opciones de fecha -->
				<div class="form-group">
					<label class="checkbox-label">
						<input type="checkbox" bind:checked={esMultiplesDias} on:change={handleMultipleDaysToggle} disabled={isSaving || isDeleting} />
						Feriado de múltiples días
					</label>
				</div>

				<!-- Fechas -->
				<div class="form-row">
					<div class="form-group">
						<label for="fecha-inicio">Fecha {esMultiplesDias ? 'de Inicio' : ''}</label>
						<input
							id="fecha-inicio"
							type="date"
							bind:value={fechaInicio}
							disabled={isSaving || isDeleting}
							required
						/>
					</div>
					{#if esMultiplesDias}
						<div class="form-group">
							<label for="fecha-fin">Fecha de Fin</label>
							<input
								id="fecha-fin"
								type="date"
								bind:value={fechaFin}
								min={fechaInicio}
								disabled={isSaving || isDeleting}
								required
							/>
						</div>
					{/if}
				</div>

			{#if esMultiplesDias && fechaInicio && fechaFin}
				{@const duracion = Math.ceil((new Date(fechaFin) - new Date(fechaInicio)) / (1000 * 60 * 60 * 24)) + 1}
				<div class="duration-info">
					<span class="duration-text">Duración: {duracion} día{duracion > 1 ? 's' : ''}</span>
				</div>
			{/if}

			<!-- Opción de repetir anualmente (solo para feriados nuevos) -->
			{#if !modoEdicion}
				<div class="form-group">
					<label class="checkbox-label">
						<input type="checkbox" bind:checked={repetirAnualmente} disabled={isSaving || isDeleting} />
						Repetir este feriado anualmente (próximos 5 años)
					</label>
					{#if repetirAnualmente}
						<div class="help-text">
							Se creará este feriado automáticamente para los próximos 5 años en las mismas fechas.
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
						{isDeleting ? "Eliminando..." : "Eliminar"}
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
						{isSaving ? "Guardando..." : "Guardar"}
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
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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
		color: #0f345c;
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
		justify-content: flex-end; /* Alinear elementos a los extremos */
		align-items: center;
		gap: 1rem;
		margin-top: 2rem;
	}
	.save-actions {
		display: flex;
		gap: 1rem;
	}

	.btn-primary,
	.btn-secondary,
	.btn-danger {
		padding: 0.7rem 1.3rem;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-size: 16px;
		font-weight: 600;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.btn-primary {
		background-color: #367acc;
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

	/* Feriados existentes */
	.existing-feriados {
		background-color: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 8px;
		padding: 1rem;
		margin-bottom: 1.5rem;
	}

	.existing-feriados h4 {
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		color: #495057;
	}

	.existing-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.existing-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem;
		background-color: white;
		border-radius: 4px;
		border-left: 3px solid #007bff;
	}

	.existing-name {
		font-weight: 600;
		color: #0f345c;
	}

	.existing-type {
		background-color: #e3f2fd;
		color: #1976d2;
		padding: 0.25rem 0.5rem;
		border-radius: 12px;
		font-size: 0.8rem;
	}

	.existing-duration {
		color: #666;
		font-size: 0.85rem;
		font-style: italic;
	}

	.existing-count {
		font-size: 0.9rem;
		color: #666;
		font-weight: normal;
	}

	/* Formulario */
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #ccc;
		border-radius: 8px;
		box-sizing: border-box;
		min-height: 80px;
		font-family: inherit;
		resize: vertical;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.checkbox-group {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		cursor: pointer;
		font-size: 0.9rem;
		line-height: 1.4;
		gap: 0.5rem;
	}

	.checkbox-label input[type="checkbox"] {
		width: auto;
		margin: 0;
	}

	.duration-info {
		background-color: #e8f5e8;
		border: 1px solid #c3e6c3;
		border-radius: 6px;
		padding: 0.75rem;
		margin-top: 0.5rem;
	}

	.duration-text {
		color: #155724;
		font-weight: 600;
		font-size: 0.9rem;
	}

	.help-text {
		font-size: 0.8rem;
		color: #666;
		margin-top: 0.5rem;
		padding: 0.5rem;
		background-color: #e4ebf3;
		border-radius: 4px;
		border-left: 3px solid #007bff;
		line-height: 1.4;
	}

	/* Responsive */
	@media (max-width: 600px) {
		.form-row {
			grid-template-columns: 1fr;
		}

		.checkbox-group {
			flex-direction: column;
			gap: 0.75rem;
		}
	}
</style>
