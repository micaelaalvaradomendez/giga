<script>
	import { createEventDispatcher, onMount } from "svelte";
	export let agente = null;
	export let isOpen = false;
	export let isSaving = false;
	export let areasDisponibles = []; // Recibir áreas como prop desde el controlador
	export let rolesDisponibles = []; // Recibir roles como prop desde el controlador
	const dispatch = createEventDispatcher();
	// Datos del formulario
	let formData = {};
	let initialized = false;
	let isFormValid = false;
	// Inicializar datos solo cuando se necesita
	function initializeFormData() {
		if (!agente || initialized) return;
		// Determinar el área del agente
		let areaId = agente.area_id || null;
		// Preservar datos de dirección existentes
		formData = {
			nombre: agente.nombre || "",
			apellido: agente.apellido || "",
			dni: agente.dni || "", // Solo lectura, no editable
			cuil: agente.cuil || "", // Solo lectura, no editable
			email: agente.email || "",
			telefono: agente.telefono || "",
			fecha_nacimiento: agente.fecha_nacimiento || "",
			categoria_revista: agente.categoria_revista || "",
			agrupacion: agente.agrupacion || "",
			// Preservar dirección completa existente
			calle: agente.calle || "",
			numero: agente.numero || "",
			ciudad: agente.ciudad || "",
			provincia: agente.provincia || "",
			// Horarios opcionales
			horario_entrada: agente.horario_entrada || "",
			horario_salida: agente.horario_salida || "",
			area_id: areaId,
			activo: agente.activo !== false,
		};
		console.log("🎯 FormData inicializado - Dirección preservada:", {
			calle: formData.calle,
			numero: formData.numero,
			ciudad: formData.ciudad,
			provincia: formData.provincia,
			area_id: areaId,
		});
		initialized = true;
		validateForm();
	}
	// Validar formulario de manera eficiente
	function validateForm() {
		isFormValid = !!(
			formData.nombre &&
			formData.apellido &&
			formData.email &&
			formData.categoria_revista &&
			formData.agrupacion
		);
	}
	// Validaciones por pestaña
	function getTabValidation(tab) {
		if (!initialized) return true;
		switch (tab) {
			case "personal":
				return !!(
					formData.nombre &&
					formData.apellido &&
					formData.email
				);
			case "laboral":
				return !!(formData.categoria_revista && formData.agrupacion);
			case "direccion":
				return true; // Dirección es opcional
			default:
				return true;
		}
	}
	// Observar cambios de modal
	$: if (isOpen && agente && !initialized) {
		// Inicializar formulario directamente (las áreas ya están disponibles como prop)
		initializeFormData();
	}
	// Reset cuando se cierra
	$: if (!isOpen) {
		initialized = false;
		formData = {};
		activeTab = "personal"; // Reset a la primera pestaña
	}
	function cerrarModal() {
		if (!isSaving) {
			isOpen = false;
			dispatch("cerrar");
		}
	}
	function guardarCambios() {
		if (isFormValid && !isSaving) {
			dispatch("guardar", { agente, formData });
		}
	}
	function handleInputChange() {
		// Debounce validation
		if (validateTimeout) clearTimeout(validateTimeout);
		validateTimeout = setTimeout(() => {
			validateForm();
			// Trigger reactive update for tab indicators
			formData = { ...formData };
		}, 150);
	}
	let validateTimeout;
	let activeTab = "personal"; // Tab activa para reducir DOM
	function setActiveTab(tab) {
		activeTab = tab;
	}
	// Ya no necesitamos cargar áreas - vienen como prop
</script>
{#if isOpen && agente && initialized}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={cerrarModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>✏️ Editar Agente</h2>
				{#if !isSaving}
					<button class="btn-close" on:click={cerrarModal}>×</button>
				{/if}
			</div>
			<div class="modal-body">
				<!-- Pestañas de navegación -->
				<div class="tabs">
					<button
						type="button"
						class="tab-button {activeTab === 'personal'
							? 'active'
							: ''} {getTabValidation('personal')
							? 'valid'
							: 'invalid'}"
						on:click={() => setActiveTab("personal")}
						disabled={isSaving}
					>
						👤 Personal
						{#if initialized && !getTabValidation("personal")}
							<span class="tab-indicator">!</span>
						{/if}
					</button>
					<button
						type="button"
						class="tab-button {activeTab === 'laboral'
							? 'active'
							: ''} {getTabValidation('laboral')
							? 'valid'
							: 'invalid'}"
						on:click={() => setActiveTab("laboral")}
						disabled={isSaving}
					>
						💼 Laboral
						{#if initialized && !getTabValidation("laboral")}
							<span class="tab-indicator">!</span>
						{/if}
					</button>
					<button
						type="button"
						class="tab-button {activeTab === 'direccion'
							? 'active'
							: ''}"
						on:click={() => setActiveTab("direccion")}
						disabled={isSaving}
					>
						🏠 Dirección
					</button>
				</div>
				<form on:submit|preventDefault={guardarCambios}>
					<div class="form-content">
						<!-- Información Personal -->
						{#if activeTab === "personal"}
							<div class="form-section">
								<h3>👤 Información Personal</h3>
								<div class="form-row">
									<div class="form-group">
										<label for="nombre">Nombre *</label>
										<input
											type="text"
											id="nombre"
											bind:value={formData.nombre}
											on:input={handleInputChange}
											required
											disabled={isSaving}
										/>
									</div>
									<div class="form-group">
										<label for="apellido">Apellido *</label>
										<input
											type="text"
											id="apellido"
											bind:value={formData.apellido}
											on:input={handleInputChange}
											required
											disabled={isSaving}
										/>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="fecha_nacimiento"
											>Fecha de Nacimiento</label
										>
										<input
											type="date"
											id="fecha_nacimiento"
											bind:value={
												formData.fecha_nacimiento
											}
											disabled={isSaving}
										/>
										<small class="help-text"
											>Fecha de nacimiento (opcional)</small
										>
									</div>
								</div>
								<div class="form-group">
									<label for="email">Email *</label>
									<input
										type="email"
										id="email"
										bind:value={formData.email}
										on:input={handleInputChange}
										required
										placeholder="usuario@ejemplo.com"
										disabled={isSaving}
									/>
									<small class="help-text"
										>Dirección de correo electrónico
										institucional</small
									>
								</div>
								<div class="form-group">
									<label for="telefono">Teléfono</label>
									<input
										type="tel"
										id="telefono"
										bind:value={formData.telefono}
										disabled={isSaving}
									/>
								</div>
							</div>
						{/if}
						<!-- Información Laboral -->
						{#if activeTab === "laboral"}
							<div class="form-section">
								<h3>💼 Información Laboral</h3>
								<div class="form-row">
									<div class="form-group">
										<label for="categoria_revista"
											>Categoría Revista *</label
										>
										<input
											type="text"
											id="categoria_revista"
											bind:value={
												formData.categoria_revista
											}
											on:input={handleInputChange}
											required
											placeholder="A1, B2, C3..."
											disabled={isSaving}
										/>
										<small class="help-text"
											>Categoría según convenio colectivo</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="agrupacion"
											>Agrupación</label
										>
										<select
											id="agrupacion"
											bind:value={formData.agrupacion}
											on:change={handleInputChange}
											disabled={isSaving}
										>
											<option value=""
												>Seleccionar agrupación...</option
											>
											<option value="EPU"
												>EPU - Escalafón Profesional
												Universitario</option
											>
											<option value="POMYS"
												>POMyS - Personal de Oficios,
												Mantenimiento y Servicios</option
											>
											<option value="PAYT"
												>PAyT - Personal Administrativo
												y Técnico</option
											>
										</select>
										<small class="help-text"
											>Agrupación laboral según escalafón</small
										>
									</div>
									<div class="form-group">
										<label for="area_id">Área</label>
										<select
											id="area_id"
											bind:value={formData.area_id}
											disabled={isSaving}
										>
											<option value=""
												>Sin área asignada...</option
											>
											{#each areasDisponibles as area}
												<option value={area.id_area}
													>{area.nombre}</option
												>
											{/each}
										</select>
										<small class="help-text"
											>Área de trabajo del agente (Total
											áreas: {areasDisponibles.length})</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="horario_entrada"
											>Horario Entrada (Opcional)</label
										>
										<input
											type="time"
											id="horario_entrada"
											bind:value={
												formData.horario_entrada
											}
											disabled={isSaving}
										/>
										<small class="help-text"
											>Hora de entrada al trabajo
											(opcional)</small
										>
									</div>
									<div class="form-group">
										<label for="horario_salida"
											>Horario Salida (Opcional)</label
										>
										<input
											type="time"
											id="horario_salida"
											bind:value={formData.horario_salida}
											disabled={isSaving}
										/>
										<small class="help-text"
											>Hora de salida del trabajo
											(opcional)</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label class="checkbox-label">
											<input
												type="checkbox"
												bind:checked={formData.activo}
												disabled={isSaving}
											/>
											Agente Activo
										</label>
										<small class="help-text"
											>Indica si el agente está activo en
											el sistema</small
										>
									</div>
								</div>
							</div>
						{/if}
						<!-- Dirección -->
						{#if activeTab === "direccion"}
							<div class="form-section">
								<h3>🏠 Dirección</h3>
								<div class="form-row">
									<div class="form-group">
										<label for="calle">Calle</label>
										<input
											type="text"
											id="calle"
											bind:value={formData.calle}
											disabled={isSaving}
										/>
									</div>
									<div class="form-group">
										<label for="numero">Número</label>
										<input
											type="text"
											id="numero"
											bind:value={formData.numero}
											disabled={isSaving}
										/>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="ciudad">Ciudad</label>
										<input
											type="text"
											id="ciudad"
											bind:value={formData.ciudad}
											disabled={isSaving}
										/>
									</div>
									<div class="form-group">
										<label for="provincia">Provincia</label>
										<input
											type="text"
											id="provincia"
											bind:value={formData.provincia}
											disabled={isSaving}
										/>
									</div>
								</div>
							</div>
						{/if}
					</div>
				</form>
			</div>
			<div class="modal-footer">
				<button
					class="btn btn-secondary"
					on:click={cerrarModal}
					disabled={isSaving}
				>
					Cancelar
				</button>
				<button
					class="btn btn-primary"
					on:click={guardarCambios}
					disabled={isSaving || !isFormValid}
				>
					{#if isSaving}
						<span class="spinner"></span>
						Guardando...
					{:else}
						Guardar Cambios
					{/if}
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
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		padding: 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.modal-content {
		background: white;
		border-radius: 8px;
		max-width: 900px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		scrollbar-width: none;
		-ms-overflow-style: none;
	}
	.modal-content::-webkit-scrollbar {
		display: none;
	}
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e9ecef;
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		border-radius: 8px 8px 0 0;
	}
	.modal-header h2 {
		margin: 0;
		font-size: 1.5rem;
	}
	.btn-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		color: white;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 4px;
		transition: background-color 0.2s;
	}
	.btn-close:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}
	.modal-body {
		padding: 0;
	}
	.tabs {
		display: flex;
		border-bottom: 1px solid #e9ecef;
		background: #f8f9fa;
	}
	.tab-button {
		background: none;
		border: none;
		padding: 1rem 1.5rem;
		cursor: pointer;
		font-size: 0.95rem;
		color: #6c757d;
		transition: all 0.2s;
		border-bottom: 3px solid transparent;
	}
	.tab-button:hover:not(:disabled) {
		background: #e9ecef;
		color: #495057;
	}
	.tab-button.active {
		color: #e79043;
		border-bottom-color: #e79043;
		background: white;
	}
	.tab-button:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}
	.tab-button.invalid {
		position: relative;
	}
	.tab-indicator {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		background: #dc3545;
		color: white;
		border-radius: 50%;
		width: 16px;
		height: 16px;
		font-size: 0.75rem;
		margin-left: 0.5rem;
	}
	.form-content {
		padding: 1.5rem;
		min-height: 400px; 
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.form-section {
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1rem;
		background: #f8f9fa;
	}
	.form-section h3 {
		margin: 0 0 1rem 0;
		color: #2c3e50;
		font-size: 1.1rem;
		padding-bottom: 0.5rem;
		border-bottom: 2px solid #e79043;
	}
	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-bottom: 1rem;
		position: relative;
		z-index: 1;
	}
	.form-group {
		display: flex;
		flex-direction: column;
		margin-bottom: 1rem;
		position: relative;
		z-index: auto;
	}
	.form-group:last-child {
		margin-bottom: 0;
	}
	label {
		font-weight: 500;
		color: #495057d2;
		margin-bottom: 0.25rem;
		font-size: 0.9rem;
	}
	input,
	select {
		padding: 0.5rem;
		border: 1px solid #ced4da;
		border-radius: 4px;
		font-size: 0.9rem;
		transition:
			border-color 0.2s,
			box-shadow 0.2s;
		position: relative;
		z-index: 1;
		background-color: #e9ecef;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
	}
	input:focus,
	select:focus {
		outline: none;
		border-color: #e79043;
		box-shadow: 0 0 0 2px rgba(231, 144, 67, 0.25);
		z-index: 10;
	}
	input:disabled,
	select:disabled {
		background-color: #e9ecef81;
		cursor: not-allowed;
		z-index: 1;
	}
	.checkbox-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
		margin-bottom: 0;
	}
	.checkbox-label input[type="checkbox"] {
		width: auto;
		margin: 0;
	}
	.help-text {
		display: block;
		font-size: 0.75rem;
		color: #6c757d;
		margin-top: 0.25rem;
		line-height: 1.3;
	}
	.modal-footer {
		padding: 1rem 1.5rem;
		border-top: 1px solid #e9ecef;
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
	}
	.btn {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 4px;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}
	.btn-secondary {
		background-color: #6c757d;
		color: white;
	}
	.btn-secondary:hover:not(:disabled) {
		background-color: #5a6268;
	}
	.btn-primary {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
	}
	.btn-primary:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	}
	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	@media (max-width: 768px) {
		.form-row {
			grid-template-columns: 1fr;
		}
		.modal-overlay {
			padding: 1rem;
		}
	}
</style>
