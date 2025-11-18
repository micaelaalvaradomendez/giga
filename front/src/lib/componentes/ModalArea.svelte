<script>
	import { createEventDispatcher, onMount } from "svelte";

	export let isOpen = false;
	export let isSaving = false;
	export let formData = {
		id_area: null,
		nombre: "",
		descripcion: "",
		id_area_padre: null,
		jefe_area: null,
		agentes_asignados: [],
		activo: true,
	};

	const dispatch = createEventDispatcher();

	let areas = [];
	let agentes = [];
	let loadingAreas = false;
	let loadingAgentes = false;

	// Cargar datos cuando se abre el modal
	$: if (isOpen) {
		cargarAreas();
		cargarAgentes();
	}

	async function cargarAreas() {
		if (loadingAreas) return;

		try {
			loadingAreas = true;
			const response = await fetch("/api/personas/catalogs/areas/", {
				credentials: "include",
			});

			if (response.ok) {
				const result = await response.json();
				areas = result.success ? result.data?.results || [] : [];
				// Filtrar el área actual para no permitir auto-referencia
				if (formData.id_area) {
					areas = areas.filter(
						(area) => area.id_area !== formData.id_area,
					);
				}
			}
		} catch (error) {
			console.error("Error cargando áreas:", error);
			areas = [];
		} finally {
			loadingAreas = false;
		}
	}

	async function cargarAgentes() {
		if (loadingAgentes) return;

		try {
			loadingAgentes = true;
			const response = await fetch("/api/personas/agentes/", {
				credentials: "include",
			});

			if (response.ok) {
				const result = await response.json();
				agentes = result.success ? result.data?.results || [] : [];
			}
		} catch (error) {
			console.error("Error cargando agentes:", error);
			agentes = [];
		} finally {
			loadingAgentes = false;
		}
	}

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

	function toggleAgenteAsignado(agenteId) {
		if (!formData.agentes_asignados) {
			formData.agentes_asignados = [];
		}

		const index = formData.agentes_asignados.indexOf(agenteId);
		if (index > -1) {
			formData.agentes_asignados.splice(index, 1);
		} else {
			formData.agentes_asignados.push(agenteId);
		}
		formData.agentes_asignados = formData.agentes_asignados; // Trigger reactivity
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

				<div class="form-group">
					<label for="areaDescripcion">Descripción</label>
					<textarea
						id="areaDescripcion"
						bind:value={formData.descripcion}
						placeholder="Descripción de las funciones y responsabilidades del área"
						rows="3"
						disabled={isSaving}
					></textarea>
				</div>

				<div class="form-group">
					<label for="areaPadre">Área Padre (opcional)</label>
					{#if loadingAreas}
						<div class="loading-select">Cargando áreas...</div>
					{:else}
						<select
							id="areaPadre"
							bind:value={formData.id_area_padre}
							disabled={isSaving}
						>
							<option value={null}
								>-- Sin área padre (raíz) --</option
							>
							{#each areas as area}
								<option value={area.id_area}>
									{area.nombre_completo || area.nombre}
								</option>
							{/each}
						</select>
					{/if}
					<small class="form-help">
						Seleccione el área padre para establecer la jerarquía
						organizacional
					</small>
				</div>

				<div class="form-group">
					<label for="jefeArea">Jefe del Área (opcional)</label>
					{#if loadingAgentes}
						<div class="loading-select">Cargando agentes...</div>
					{:else}
						<select
							id="jefeArea"
							bind:value={formData.jefe_area}
							disabled={isSaving}
						>
							<option value={null}>-- Sin jefe asignado --</option
							>
							{#each agentes as agente}
								<option value={agente.id_agente}>
									{agente.nombre}
									{agente.apellido} ({agente.legajo})
								</option>
							{/each}
						</select>
					{/if}
					<small class="form-help">
						Seleccione el agente que será jefe de esta área
					</small>
				</div>

				<div class="form-group">
					<label>Agentes a Asignar (opcional)</label>
					{#if loadingAgentes}
						<div class="loading-select">Cargando agentes...</div>
					{:else if agentes.length > 0}
						<div class="agentes-list">
							{#each agentes as agente}
								<label class="agente-checkbox">
									<input
										type="checkbox"
										checked={formData.agentes_asignados &&
											formData.agentes_asignados.includes(
												agente.id_agente,
											)}
										on:change={() =>
											toggleAgenteAsignado(
												agente.id_agente,
											)}
										disabled={isSaving}
									/>
									<span class="checkbox-custom"></span>
									<div class="agente-info">
										<strong
											>{agente.nombre}
											{agente.apellido}</strong
										>
										<small>Legajo: {agente.legajo}</small>
										{#if agente.area_actual}
											<small class="area-actual"
												>Área actual: {agente.area_actual}</small
											>
										{/if}
									</div>
								</label>
							{/each}
						</div>
					{:else}
						<div class="no-agentes">No hay agentes disponibles</div>
					{/if}
					<small class="form-help">
						Seleccione los agentes que pertenecerán a esta área
					</small>
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
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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

	/* Estilos para los nuevos campos */
	.form-group textarea {
		width: 100%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.3s ease;
		font-family: inherit;
		resize: vertical;
		min-height: 80px;
	}

	.form-group textarea:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.form-group textarea:disabled {
		background-color: #e9ecef;
		cursor: not-allowed;
	}

	.form-group select {
		width: 100%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.3s ease;
		font-family: inherit;
		background-color: white;
	}

	.form-group select:focus {
		outline: none;
		border-color: #3498db;
		box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
	}

	.form-group select:disabled {
		background-color: #e9ecef;
		cursor: not-allowed;
	}

	.form-help {
		display: block;
		margin-top: 0.25rem;
		color: #6c757d;
		font-size: 0.875rem;
		line-height: 1.3;
		font-weight: 400;
	}

	.loading-select {
		padding: 12px 15px;
		color: #6c757d;
		font-style: italic;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		background-color: #f8f9fa;
		text-align: center;
	}

	.agentes-list {
		max-height: 300px;
		overflow-y: auto;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		padding: 0.5rem;
		background-color: #f8f9fa;
	}

	.agente-checkbox {
		display: flex;
		align-items: flex-start;
		padding: 0.75rem;
		margin-bottom: 0.5rem;
		border-radius: 6px;
		cursor: pointer;
		transition: background-color 0.2s ease;
		background-color: white;
		border: 1px solid #e9ecef;
	}

	.agente-checkbox:hover {
		background-color: #e9ecef;
		border-color: #3498db;
	}

	.agente-checkbox:last-child {
		margin-bottom: 0;
	}

	.agente-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.agente-info strong {
		font-size: 0.9rem;
		color: #333;
	}

	.agente-info small {
		font-size: 0.8rem;
		color: #6c757d;
	}

	.agente-info .area-actual {
		color: #007bff;
		font-weight: 500;
	}

	.no-agentes {
		text-align: center;
		padding: 2rem;
		color: #6c757d;
		font-style: italic;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		background-color: #f8f9fa;
	}
</style>
