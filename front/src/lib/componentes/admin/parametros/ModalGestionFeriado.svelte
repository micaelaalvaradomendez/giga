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
			await ferladosController.deleteFeriadoFromModal(feriado.id_feriado);
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
</script>

{#if isOpen}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={closeModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>
					{modoEdicion ? "Editar Feriado" : "Agregar Feriado"}
					{#if existingFeriados.length > 0 && !modoEdicion}
						<span class="existing-count"
							>({existingFeriados.length} feriado{existingFeriados.length >
							1
								? "s"
								: ""} existente{existingFeriados.length > 1
								? "s"
								: ""})</span
						>
					{/if}
				</h2>
				<button class="btn-close" on:click={closeModal}>×</button>
			</div>
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
												editarFeriadoExistente(
													existingFeriado,
												)}
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
							>Duración: {duracion} día{duracion > 1
								? "s"
								: ""}</span
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
								Se creará este feriado automáticamente para los
								próximos 5 años en las mismas fechas.
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
						class="btn-marcar-ausente"
						disabled={isSaving || isDeleting}
						on:click={handleDelete}
					>
						{isDeleting ? "Eliminando..." : "Eliminar"}
					</button>
				{/if}

				<div class="save-actions">
					<button
						type="button"
						class="btn-cancelar"
						on:click={closeModal}
						disabled={isSaving || isDeleting}
					>
						Cancelar
					</button>
					<button
						type="button"
						class="btn-marcar-salida"
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
	/* Modal Overlay & Content */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.6);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.modal-content {
		background: white;
		border-radius: 16px;
		width: 100%;
		max-width: 600px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-content::-webkit-scrollbar {
		display: none;
	}

	/* Header */
	.modal-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 1.5rem 2rem;
		border-radius: 16px 16px 0 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.modal-header h2 {
		margin: 0;
		color: white;
		font-size: 1.5rem;
		font-weight: 600;
	}

	.existing-count {
		font-size: 0.9rem;
		opacity: 0.9;
		font-weight: normal;
		margin-left: 0.5rem;
	}

	.btn-close {
		background: rgba(255, 255, 255, 0.2);
		border: none;
		color: white;
		font-size: 1.8rem;
		font-weight: 600;
		cursor: pointer;
		padding: 0;
		border-radius: 8px;
		transition: all 0.3s ease;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
	}

	.btn-close:hover {
		background: rgba(255, 255, 255, 0.3);
		transform: scale(1.1);
	}

	/* Modal Body */
	.modal-body {
		padding: 2rem;
	}

	/* Form Groups */
	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
		font-size: 0.95rem;
	}

	.form-group input[type="text"],
	.form-group input[type="date"],
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 2px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.95rem;
		font-family: inherit;
		transition: all 0.2s;
		box-sizing: border-box;
	}

	.form-group input:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.form-group textarea {
		min-height: 80px;
		resize: vertical;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.checkbox-group {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.95rem;
		color: #374151;
		cursor: pointer;
		font-weight: 500;
	}

	.checkbox-label input[type="checkbox"] {
		width: 18px;
		height: 18px;
		cursor: pointer;
		accent-color: #667eea;
	}

	.duration-info {
		background-color: #f0fdf4;
		border: 1px solid #bbf7d0;
		border-radius: 8px;
		padding: 0.75rem;
		margin-top: 0.5rem;
		display: flex;
		align-items: center;
	}

	.duration-text {
		color: #15803d;
		font-weight: 600;
		font-size: 0.9rem;
	}

	.help-text {
		color: #64748b;
		font-size: 0.85rem;
		margin-top: 0.5rem;
		padding: 0.75rem;
		background-color: #eff6ff;
		border-radius: 8px;
		border-left: 3px solid #3b82f6;
		line-height: 1.4;
	}

	/* Modal Footer */
	.modal-footer {
		display: flex;
		justify-content: space-between; /* To separate delete button from save actions */
		align-items: center;
		padding: 1.5rem 2rem;
		border-top: 1px solid #e2e8f0;
		background: #f8fafc;
		border-radius: 0 0 16px 16px;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.save-actions {
		display: flex;
		gap: 0.75rem;
		margin-left: auto; /* Push to right if delete button exists */
	}

	/* Buttons */
	.modal-footer button {
		padding: 0.75rem 1.25rem;
		border: none;
		border-radius: 8px;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: inherit;
	}

	.btn-cancelar {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
	}

	.btn-cancelar:hover {
		background: linear-gradient(135deg, #4b5563, #374151);
		transform: translateY(-2px);
	}

	.btn-marcar-salida {
		background: linear-gradient(135deg, #3b82f6, #2563eb);
		color: white;
	}

	.btn-marcar-salida:hover:not(:disabled) {
		background: linear-gradient(135deg, #2563eb, #1d4ed8);
		transform: translateY(-2px);
	}

	.btn-marcar-salida:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-marcar-ausente {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
	}

	.btn-marcar-ausente:hover:not(:disabled) {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-2px);
	}

	/* Feriados existentes */
	.existing-feriados {
		background-color: #f8fafc;
		border: 1px solid #e2e8f0;
		border-radius: 10px;
		padding: 1rem;
		margin-bottom: 1.5rem;
	}

	.existing-feriados h4 {
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		color: #475569;
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
		border-left: 4px solid #3b82f6;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
	}

	.existing-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex: 1;
		flex-wrap: wrap;
	}

	.existing-name {
		font-weight: 600;
		color: #1e293b;
	}

	.existing-type {
		background-color: #eff6ff;
		color: #2563eb;
		padding: 0.25rem 0.5rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.existing-duration {
		color: #64748b;
		font-size: 0.85rem;
		font-style: italic;
	}

	.existing-actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn-edit-existing,
	.btn-delete-existing {
		background: #f1f5f9;
		border: none;
		width: 32px;
		height: 32px;
		border-radius: 6px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1rem;
		transition: all 0.2s ease;
	}

	.btn-edit-existing:hover {
		background-color: #e0f2fe;
		color: #0284c7;
	}

	.btn-delete-existing:hover {
		background-color: #fee2e2;
		color: #dc2626;
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

		.modal-footer {
			flex-direction: column;
		}

		.modal-footer button {
			width: 100%;
		}

		.save-actions {
			width: 100%;
			margin-left: 0;
		}
	}
</style>
