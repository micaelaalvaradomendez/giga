<script>
	import { createEventDispatcher } from "svelte";
	import BaseModal from "$lib/componentes/incidencias/BaseModal.svelte";

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
			esMultiplesDias =
				fechaInicio && fechaFin && fechaInicio !== fechaFin;
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

	function editarFeriadoExistente(feriadoExistente) {
		// Cambiar a modo edición con el feriado seleccionado
		modoEdicion = true;
		nombreFeriado = feriadoExistente.nombre || "";
		descripcionFeriado = feriadoExistente.descripcion || "";
		fechaInicio = feriadoExistente.fecha_inicio || selectedDate;
		fechaFin = feriadoExistente.fecha_fin || selectedDate;
		esNacional = feriadoExistente.es_nacional || false;
		esProvincial = feriadoExistente.es_provincial || false;
		esLocal = feriadoExistente.es_local || false;
		esMultiplesDias = fechaInicio && fechaFin && fechaInicio !== fechaFin;

		// Establecer el feriado para edición
		feriado = feriadoExistente;
	}

	async function eliminarFeriadoExistente(feriadoExistente) {
		if (
			!confirm(
				`¿Estás seguro de que deseas eliminar el feriado "${feriadoExistente.nombre}"?`,
			)
		) {
			return;
		}

		try {
			await feriadosController.deleteFeriadoFromModal(
				feriadoExistente.id_feriado,
			);
			// El modal se cerrará automáticamente después de la eliminación exitosa
		} catch (error) {
			console.error("Error eliminando feriado existente:", error);
		}
	}

	$: modalTitle = modoEdicion ? "Editar Feriado" : "Agregar Feriado";
</script>

<BaseModal
	show={isOpen}
	title={modalTitle}
	maxWidth="600px"
	onClose={closeModal}
>
	<div class="modal-body">
		<!-- Mostrar feriados existentes si los hay -->
		{#if existingFeriados.length > 0 && !modoEdicion}
			<div class="existing-feriados">
				<h4>Feriados existentes en esta fecha:</h4>
				<div class="existing-list">
					{#each existingFeriados as existingFeriado}
						<div class="existing-item">
							<div class="existing-info">
								<span class="existing-name"
									>{existingFeriado.nombre}</span
								>
								<span class="existing-type"
									>{existingFeriado.tipo_feriado}</span
								>
								{#if existingFeriado.es_multiples_dias}
									<span class="existing-duration"
										>({existingFeriado.duracion_dias}
										días)</span
									>
								{/if}
							</div>
							<div class="existing-actions">
								<button
									class="btn-edit-existing"
									on:click={() =>
										editarFeriadoExistente(existingFeriado)}
									title="Editar este feriado"
								>
									✏️
								</button>
								<button
									class="btn-delete-existing"
									on:click={() =>
										eliminarFeriadoExistente(
											existingFeriado,
										)}
									title="Eliminar este feriado"
								>
									🗑️
								</button>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Campos del formulario -->
		<div class="form-group">
			<label for="nombre">Nombre del Feriado *</label>
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
			<label for="tipo">Tipo de Feriado</label>
			<div class="checkbox-group">
				<label class="checkbox-label">
					<input
						type="checkbox"
						bind:checked={esNacional}
						disabled={isSaving || isDeleting}
					/>
					Nacional
				</label>
				<label class="checkbox-label">
					<input
						type="checkbox"
						bind:checked={esProvincial}
						disabled={isSaving || isDeleting}
					/>
					Provincial
				</label>
				<label class="checkbox-label">
					<input
						type="checkbox"
						bind:checked={esLocal}
						disabled={isSaving || isDeleting}
					/>
					Local
				</label>
			</div>
		</div>

		<!-- Opciones de fecha -->
		<div class="form-group">
			<label class="checkbox-label">
				<input
					type="checkbox"
					bind:checked={esMultiplesDias}
					on:change={handleMultipleDaysToggle}
					disabled={isSaving || isDeleting}
				/>
				Feriado de múltiples días
			</label>
		</div>

		<!-- Fechas -->
		<div class="form-row">
			<div class="form-group">
				<label for="fecha-inicio"
					>Fecha {esMultiplesDias ? "de Inicio" : ""}</label
				>
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
			{@const duracion =
				Math.ceil(
					(new Date(fechaFin) - new Date(fechaInicio)) /
						(1000 * 60 * 60 * 24),
				) + 1}
			<div class="duration-info">
				<span class="duration-text"
					>Duración: {duracion} día{duracion > 1 ? "s" : ""}</span
				>
			</div>
		{/if}

		<!-- Opción de repetir anualmente (solo para feriados nuevos) -->
		{#if !modoEdicion}
			<div class="form-group">
				<label class="checkbox-label">
					<input
						type="checkbox"
						bind:checked={repetirAnualmente}
						disabled={isSaving || isDeleting}
					/>
					Repetir este feriado anualmente (próximos 5 años)
				</label>
				{#if repetirAnualmente}
					<div class="help-text">
						Se creará este feriado automáticamente para los próximos
						5 años en las mismas fechas.
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<div class="modal-footer">
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
				class="btn-cancel"
				on:click={closeModal}
				disabled={isSaving || isDeleting}
			>
				Cancelar
			</button>
			<button
				type="button"
				class="btn-save"
				disabled={isSaving || isDeleting}
				on:click={handleSave}
			>
				{isSaving ? "Guardando..." : "Guardar"}
			</button>
		</div>
	</div>
</BaseModal>

<style>
	.modal-body {
		padding: 2rem;
		max-height: 70vh;
		overflow-y: auto;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-body::-webkit-scrollbar {
		display: none;
	}

	.modal-footer {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		align-items: center;
		gap: 0.75rem;
		padding: 0 2rem 2rem;
	}

	.save-actions {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	/* Botones con estilos unificados */
	.btn-cancel,
	.btn-save,
	.btn-danger {
		padding: 0.75rem 1.5rem;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		border: none;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		font-size: 0.875rem;
		white-space: nowrap;
		min-width: fit-content;
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

	.btn-danger {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
	}

	.btn-danger:hover:not(:disabled) {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
	}

	.btn-cancel:disabled,
	.btn-save:disabled,
	.btn-danger:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	/* Feriados existentes */
	.existing-feriados {
		background-color: #f8fafc;
		border: 1px solid #e5e7eb;
		border-radius: 12px;
		padding: 1.25rem;
		margin-bottom: 1.5rem;
	}

	.existing-feriados h4 {
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		color: #374151;
		font-weight: 600;
	}

	.existing-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.existing-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem;
		background-color: white;
		border-radius: 8px;
		border-left: 4px solid #4c51bf;
		transition: all 0.2s ease;
		gap: 0.5rem;
	}

	.existing-item:hover {
		transform: translateX(4px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.existing-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex: 1;
		flex-wrap: wrap;
		min-width: 0;
	}

	.existing-actions {
		display: flex;
		gap: 0.25rem;
		flex-shrink: 0;
	}

	.btn-edit-existing,
	.btn-delete-existing {
		background: none;
		border: none;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
		transition: background-color 0.2s ease;
	}

	.btn-edit-existing:hover {
		background-color: #e3f2fd;
	}

	.btn-delete-existing:hover {
		background-color: #ffebee;
	}

	.existing-name {
		font-weight: 600;
		color: #1f2937;
		word-break: break-word;
	}

	.existing-type {
		background-color: #e0e7ff;
		color: #4c51bf;
		padding: 0.25rem 0.65rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 600;
		white-space: nowrap;
	}

	.existing-duration {
		color: #6b7280;
		font-size: 0.85rem;
		font-style: italic;
	}

	/* Formulario */
	.form-group {
		margin-bottom: 1.5rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		font-size: 0.875rem;
	}

	.form-group input,
	.form-group textarea {
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

	.form-group input:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.form-group textarea {
		resize: vertical;
		min-height: 100px;
	}

	.form-group input:disabled,
	.form-group textarea:disabled {
		background-color: #f5f5f5;
		cursor: not-allowed;
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
		font-weight: 400;
		color: #374151;
	}

	.checkbox-label input[type="checkbox"] {
		width: auto;
		margin: 0;
		cursor: pointer;
	}

	.duration-info {
		background-color: #ecfdf5;
		border: 1px solid #a7f3d0;
		border-radius: 8px;
		padding: 0.75rem;
		margin-top: 0.5rem;
	}

	.duration-text {
		color: #065f46;
		font-weight: 600;
		font-size: 0.9rem;
	}

	.help-text {
		font-size: 0.8rem;
		color: #6b7280;
		margin-top: 0.5rem;
		padding: 0.65rem;
		background-color: #eff6ff;
		border-radius: 6px;
		border-left: 3px solid #3b82f6;
		line-height: 1.5;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.modal-body {
			padding: 1.5rem;
		}

		.modal-footer {
			padding: 0 1.5rem 1.5rem;
			gap: 0.5rem;
		}

		.form-row {
			grid-template-columns: 1fr;
		}

		.btn-cancel,
		.btn-save,
		.btn-danger {
			padding: 0.65rem 1.25rem;
			font-size: 0.8125rem;
		}

		.existing-item {
			flex-direction: column;
			align-items: flex-start;
		}

		.existing-actions {
			width: 100%;
			justify-content: flex-end;
		}
	}

	@media (max-width: 480px) {
		.modal-body {
			padding: 1rem;
		}

		.modal-footer {
			padding: 0 1rem 1rem;
			flex-direction: column;
			align-items: stretch;
		}

		.save-actions {
			flex-direction: column;
			width: 100%;
		}

		.btn-cancel,
		.btn-save,
		.btn-danger {
			width: 100%;
			padding: 0.75rem;
		}

		.checkbox-group {
			flex-direction: column;
			gap: 0.75rem;
		}

		.existing-info {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
