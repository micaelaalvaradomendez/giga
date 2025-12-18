<script>
	import { createEventDispatcher, onMount } from "svelte";
	import { personasService } from "$lib/services.js";
	export let isOpen = false;
	export let isSaving = false;
	export let areasDisponibles = []; // Recibir áreas como prop desde el controlador
	export let rolesDisponibles = []; // Recibir roles como prop desde el controlador
	const dispatch = createEventDispatcher();
	// Datos del formulario para nuevo agente
	let formData = {
		// Usuario
		email: "",
		cuil: "",
		password: "",
		rol_id: "", // Nuevo campo para el rol
		// Agente
		nombre: "",
		apellido: "",
		dni: "",
		legajo: "",
		telefono: "",
		fecha_nacimiento: "",
		categoria_revista: "24", // Valor por defecto
		agrupacion: "",
		area_id: null,
		// Dirección
		calle: "",
		numero: "",
		ciudad: "",
		provincia: "",
		// Laborales
		horario_entrada: "08:00",
		horario_salida: "16:00",
		activo: true,
	};
	let activeTab = "personal";
	let validateTimeout;
	let isFormValid = false;
	// Ya no necesitamos cargar roles - vienen como props
	function setActiveTab(tab) {
		activeTab = tab;
	}
	function validateForm() {
		// La contraseña se genera automáticamente del DNI
		if (formData.dni) {
			formData.password = formData.dni;
		}
		// Generar legajo automático si no existe y tenemos DNI
		if (!formData.legajo && formData.dni) {
			formData.legajo = `LEG-${formData.dni}`;
		}
		isFormValid = !!(
			(
				formData.email &&
				formData.cuil &&
				formData.rol_id &&
				formData.nombre &&
				formData.apellido &&
				formData.dni &&
				formData.categoria_revista &&
				formData.agrupacion &&
				formData.legajo
			) // Asegurar que el legajo existe
		);
	}
	function handleInputChange(event) {
		// Si se cambia el DNI, actualizar automáticamente la contraseña
		if (event.target.id === "dni") {
			formData.password = formData.dni;
		}

		// Validaciones de entrada
		if (event.target.id === "nombre" || event.target.id === "apellido") {
			// Solo letras y espacios
			formData[event.target.id] = event.target.value.replace(
				/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g,
				"",
			);
		}
		if (event.target.id === "telefono") {
			// Solo números, espacios, + y -
			formData[event.target.id] = event.target.value.replace(
				/[^0-9+\-\s]/g,
				"",
			);
		}
		if (validateTimeout) clearTimeout(validateTimeout);
		validateTimeout = setTimeout(() => {
			validateForm();
			formData = { ...formData };
		}, 150);
	}
	function cerrarModal() {
		if (!isSaving) {
			isOpen = false;
			// Reset form
			formData = {
				email: "",
				cuil: "",
				password: "",
				rol_id: "",
				nombre: "",
				apellido: "",
				dni: "",
				legajo: "",
				telefono: "",
				fecha_nacimiento: "",
				categoria_revista: "24",
				agrupacion: "",
				area_id: null,
				calle: "",
				numero: "",
				ciudad: "",
				provincia: "",
				horario_entrada: "08:00",
				horario_salida: "16:00",
				activo: true,
			};
			activeTab = "personal";
			dispatch("cerrar");
		}
	}
	function guardarAgente() {
		if (isFormValid && !isSaving) {
			dispatch("guardar", { formData });
		} else {
		}
	}
	// Validaciones por pestaña
	function getTabValidation(tab) {
		switch (tab) {
			case "personal":
				return !!(
					formData.nombre &&
					formData.apellido &&
					formData.dni &&
					formData.email &&
					formData.cuil
				);
			case "usuario":
				return !!(formData.email && formData.rol_id);
			case "laboral":
				return !!(formData.categoria_revista && formData.agrupacion);
			case "direccion":
				return !!(
					formData.calle &&
					formData.numero &&
					formData.ciudad &&
					formData.provincia
				);
			default:
				return true;
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
				<h2>➕ Añadir Nuevo Agente</h2>
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
						{#if !getTabValidation("personal")}
							<span class="tab-indicator">!</span>
						{/if}
					</button>
					<button
						type="button"
						class="tab-button {activeTab === 'usuario'
							? 'active'
							: ''} {getTabValidation('usuario')
							? 'valid'
							: 'invalid'}"
						on:click={() => setActiveTab("usuario")}
						disabled={isSaving}
					>
						🔑 Usuario
						{#if !getTabValidation("usuario")}
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
						{#if !getTabValidation("laboral")}
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
						{#if !getTabValidation("direccion")}
							<span class="tab-indicator">!</span>
						{/if}
					</button>
				</div>
				<form on:submit|preventDefault={guardarAgente}>
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
											placeholder="Ej: Juan, María, Carlos"
											required
											disabled={isSaving}
										/>
										<small class="help-text"
											>Nombre(s) de pila del agente</small
										>
									</div>
									<div class="form-group">
										<label for="apellido">Apellido *</label>
										<input
											type="text"
											id="apellido"
											bind:value={formData.apellido}
											on:input={handleInputChange}
											placeholder="Ej: García, López, Fernández"
											required
											disabled={isSaving}
										/>
										<small class="help-text"
											>Apellido(s) del agente</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="dni">DNI *</label>
										<input
											type="text"
											id="dni"
											bind:value={formData.dni}
											on:input={handleInputChange}
											required
											pattern="[0-9]{(7, 8)}"
											placeholder="12345678"
											maxlength="8"
											disabled={isSaving}
										/>
										<small class="help-text"
											>Documento Nacional de Identidad
											(7-8 dígitos, sin puntos)</small
										>
									</div>
									<div class="form-group">
										<label for="cuil">CUIL *</label>
										<input
											type="text"
											id="cuil"
											bind:value={formData.cuil}
											on:input={handleInputChange}
											required
											pattern="[0-9]{11}"
											placeholder="27123456784"
											maxlength="11"
											disabled={isSaving}
										/>
										<small class="help-text"
											>Código Único de Identificación
											Laboral (11 dígitos, sin guiones)</small
										>
									</div>
								</div>
								<div class="form-row">
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
										<label for="fecha_nacimiento"
											>Fecha de Nacimiento *</label
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
											>Fecha de nacimiento</small
										>
									</div>
								</div>
								<div class="form-group">
									<label for="telefono">Teléfono *</label>
									<input
										type="tel"
										id="telefono"
										bind:value={formData.telefono}
										placeholder="+54 11 1234-5678"
										disabled={isSaving}
										maxlength="20"
									/>
									<small class="help-text"
										>Número de teléfono de contacto (incluir
										código de área)</small
									>
								</div>
							</div>
						{/if}
						<!-- Usuario y Acceso -->
						{#if activeTab === "usuario"}
							<div class="form-section">
								<h3>🔑 Datos de Usuario</h3>
								<div class="form-row">
									<div class="form-group">
										<label for="password"
											>Contraseña Inicial</label
										>
										<small class="help-text"
											>La contraseña inicial será el DNI.
											El usuario deberá cambiarla en el
											primer acceso.</small
										>
									</div>
								</div>
								<div class="form-group">
									<label for="rol_id">Rol del Usuario *</label
									>
									<select
										id="rol_id"
										bind:value={formData.rol_id}
										on:change={handleInputChange}
										required
										disabled={isSaving}
									>
										<option value=""
											>Seleccionar rol...</option
										>
										{#each rolesDisponibles as rol}
											<option value={rol.id_rol}
												>{rol.nombre} - {rol.descripcion ||
													""}</option
											>
										{/each}
									</select>
									<small class="help-text"
										>Define los permisos y nivel de acceso
										del usuario en el sistema (Roles
										disponibles: {rolesDisponibles.length})</small
									>
								</div>
							</div>
						{/if}
						<!-- Información Laboral -->
						{#if activeTab === "laboral"}
							<div class="form-section">
								<h3>💼 Información Laboral</h3>
								<div class="form-row">
									<div class="form-group">
										<label for="agrupacion"
											>Agrupación *</label
										>
										<select
											id="agrupacion"
											bind:value={formData.agrupacion}
											on:change={handleInputChange}
											required
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
										<label for="categoria_revista"
											>Categoría *</label
										>
										<input
											type="text"
											id="categoria_revista"
											bind:value={
												formData.categoria_revista
											}
											on:input={handleInputChange}
											required
											placeholder="Ej: 24, A1, B2, C3..."
											disabled={isSaving}
										/>
										<small class="help-text"
											>Categoría según convenio colectivo</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="area_id">Área *</label>
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
											>Área de trabajo del agente (Áreas
											disponibles: {areasDisponibles.length})</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="horario_entrada"
											>Horario Entrada</label
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
											>Hora de entrada al trabajo</small
										>
									</div>
									<div class="form-group">
										<label for="horario_salida"
											>Horario Salida</label
										>
										<input
											type="time"
											id="horario_salida"
											bind:value={formData.horario_salida}
											disabled={isSaving}
										/>
										<small class="help-text"
											>Hora de salida del trabajo</small
										>
									</div>
								</div>
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
										>Indica si el agente estará activo en el
										sistema</small
									>
								</div>
							</div>
						{/if}
						<!-- Dirección -->
						{#if activeTab === "direccion"}
							<div class="form-section">
								<h3>🏠 Dirección</h3>
								<div class="form-row">
									<div class="form-group">
										<label for="calle">Calle *</label>
										<input
											type="text"
											id="calle"
											bind:value={formData.calle}
											placeholder="Av. San Martín"
											disabled={isSaving}
										/>
										<small class="help-text"
											>Nombre de la calle o avenida</small
										>
									</div>
									<div class="form-group">
										<label for="numero">Número *</label>
										<input
											type="text"
											id="numero"
											bind:value={formData.numero}
											placeholder="1234"
											disabled={isSaving}
										/>
										<small class="help-text"
											>Número de la dirección</small
										>
									</div>
								</div>
								<div class="form-row">
									<div class="form-group">
										<label for="ciudad">Ciudad *</label>
										<input
											type="text"
											id="ciudad"
											bind:value={formData.ciudad}
											placeholder="Ej: Ushuaia, Buenos Aires, Córdoba..."
											disabled={isSaving}
										/>
										<small class="help-text"
											>Ciudad o localidad de residencia</small
										>
									</div>
									<div class="form-group">
										<label for="provincia"
											>Provincia *</label
										>
										<input
											type="text"
											id="provincia"
											bind:value={formData.provincia}
											placeholder="Ej: Tierra del Fuego, Buenos Aires, Córdoba..."
											disabled={isSaving}
										/>
										<small class="help-text"
											>Provincia de residencia</small
										>
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
					on:click={guardarAgente}
					disabled={isSaving || !isFormValid}
				>
					{#if isSaving}
						<span class="spinner"></span>
						Guardando...
					{:else}
						Crear Agente
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
		background: linear-gradient(135deg, #28a745, #20c997);
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
		color: #28a745;
		border-bottom-color: #28a745;
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
		border-bottom: 2px solid #28a745;
	}
	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-bottom: 1rem;
	}
	.form-group {
		display: flex;
		flex-direction: column;
		margin-bottom: 1rem;
	}
	.form-group:last-child {
		margin-bottom: 0;
	}
	label {
		font-weight: 500;
		color: #495057;
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
	}
	input:focus,
	select:focus {
		outline: none;
		border-color: #28a745;
		box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.25);
	}
	input:disabled,
	select:disabled {
		background-color: #e9ecef;
		cursor: not-allowed;
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
		background: linear-gradient(135deg, #28a745, #20c997);
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
			padding: 0.5rem;
			align-items: flex-start; 
		}
		.modal-content {
			max-height: 95vh;
			display: flex;
			flex-direction: column;
		}
		.modal-header {
			padding: 1rem;
		}
		.modal-header h2 {
			font-size: 1.1rem; 
		}
		.tabs {
			overflow-x: auto; 
			white-space: nowrap;
			-webkit-overflow-scrolling: touch;
		}
		.tab-button {
			padding: 0.75rem 1rem;
			font-size: 0.85rem;
		}
		.form-content {
			padding: 1rem;
		}
	}
</style>
