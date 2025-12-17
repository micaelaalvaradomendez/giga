<script>
	import {
		asignarLicencia,
		puedeAsignarAAgente,
		puedeVerLicenciaDeRol,
	} from "$lib/paneladmin/controllers/licenciasController.js";
	import { personasService } from "$lib/services.js";
	import AuthService from "$lib/login/authService.js";
	// Props
	export let show = false;
	export let tiposLicencia = [];
	export let areas = [];
	export let userRol = null;
	export let userArea = null;
	let userInfo = null;
	import { createEventDispatcher } from "svelte";
	const dispatch = createEventDispatcher();
	let formLicencia = {
		id_agente: "",
		id_tipo_licencia: "",
		fecha_desde: "",
		fecha_hasta: "",
		observaciones: "",
		justificacion: "",
	};
	let areaSeleccionada = "";
	let agentesDelArea = [];
	let cargandoAgentes = false;
	let enviando = false;
	let areasDisponibles = [];
	let mostrandoConfirmacion = false;
	let tituloConfirmacion = "";
	let mensajeConfirmacion = "";
	let tipoConfirmacion = "success";
	let resolverConfirmacion = null;
	// filtra áreas según el rol del usuario
	$: {
		if (!areas || areas.length === 0) {
			// No limpiar areasDisponibles si solo temporalmente no hay areas
			// Esto previene que el dropdown se vacíe durante re-renders
		} else if (userRol) {
			// Si es administrador, puede ver todas las áreas
			if (userRol.toLowerCase() === "administrador") {
				areasDisponibles = areas;
			} else if (
				userRol.toLowerCase() === "director" ||
				userRol.toLowerCase() === "jefatura"
			) {
				// Director y Jefatura solo ven su área
				areasDisponibles = areas.filter(
					(area) => area.id_area === userArea,
				);
			} else {
				// Otros roles sin permisos especiales
				areasDisponibles = [];
			}
		} else if (areas.length > 0 && areasDisponibles.length === 0) {
			// Si no hay userRol pero hay áreas y areasDisponibles está vacío,
			// mostrar todas las áreas como fallback
			areasDisponibles = areas;
		}
	}
	$: if (show && !userInfo) {
		cargarUsuarioActual();
	}
	function handleFechaDesdeChange() {
		// Si la nueva fecha desde es posterior a la fecha hasta, limpiar fecha hasta
		if (
			formLicencia.fecha_desde &&
			formLicencia.fecha_hasta &&
			formLicencia.fecha_desde > formLicencia.fecha_hasta
		) {
			formLicencia.fecha_hasta = "";
		}
	}
	$: if (!show) {
		formLicencia = {
			id_agente: "",
			id_tipo_licencia: "",
			fecha_desde: "",
			fecha_hasta: "",
			observaciones: "",
			justificacion: "",
		};
		areaSeleccionada = "";
		agentesDelArea = [];
		cargandoAgentes = false;
		enviando = false;
		userInfo = null;
	}
	async function cargarUsuarioActual() {
		try {
			const userResponse = await AuthService.getCurrentUserData();
			if (userResponse?.success && userResponse.data?.success) {
				userInfo = userResponse.data.data;
			}
		} catch (err) {
			console.error("Error cargando usuario en modal:", err);
		}
	}
	function cerrarModal() {
		show = false;
		dispatch("close");
	}
	async function cargarAgentesPorArea(areaId) {
		if (!areaId) {
			agentesDelArea = [];
			return;
		}
		try {
			cargandoAgentes = true;
			const response = await personasService.getAgentesByArea(areaId);
			let agentesCompletos = [];
			if (response?.data) {
				if (response.data.results) {
					agentesCompletos = response.data.results || [];
				} else if (response.data.success && response.data.data) {
					agentesCompletos = response.data.data || [];
				} else {
					console.warn(
						"⚠️ Respuesta sin formato conocido:",
						response.data,
					);
					agentesCompletos = [];
				}
			} else {
				console.warn("⚠️ No hay data en la respuesta:", response);
				agentesCompletos = [];
			}
			if (userRol) {
				agentesDelArea = agentesCompletos.filter((agente) => {
					const puedeAsignar = puedeAsignarAAgente(
						agente.rol?.nombre || agente.rol_nombre || "Agente",
						userRol,
						agente.id_area || areaId,
						userArea,
					);
					return puedeAsignar;
				});
			} else {
				agentesDelArea = agentesCompletos;
			}
		} catch (err) {
			console.error("❌ Error cargando agentes:", err);
			agentesDelArea = [];
		} finally {
			cargandoAgentes = false;
		}
	}
	$: if (areaSeleccionada && show && areas.length > 0) {
		cargarAgentesPorArea(areaSeleccionada);
	}
	async function handleAsignarLicencia() {
		try {
			enviando = true;

			const resultado = await asignarLicencia(formLicencia);
			if (resultado.success) {
				cerrarModal();
				dispatch("assigned", resultado.data);
			} else {
				const errorMessage =
					resultado.error || "Error al asignar la licencia";
				throw new Error(errorMessage);
			}
		} catch (err) {
			console.error("❌ Error asignando licencia:", err);
			const errorMessage =
				err?.response?.data?.message ||
				err.message ||
				"Error desconocido";
			mostrarConfirmacion("Error", errorMessage, "error");
		} finally {
			enviando = false;
		}
	}
	function mostrarConfirmacion(titulo, mensaje, tipo = "success") {
		tituloConfirmacion = titulo;
		mensajeConfirmacion = mensaje;
		const tiposValidos = ["success", "error", "warning"];
		tipoConfirmacion = tiposValidos.includes(tipo) ? tipo : "success";
		mostrandoConfirmacion = true;
	}
	function cerrarConfirmacion() {
		mostrandoConfirmacion = false;
	}
	function confirmar(titulo, mensaje = "", tipo = "success") {
		tituloConfirmacion = titulo;
		mensajeConfirmacion = mensaje;
		const tiposValidos = ["success", "error", "warning"];
		tipoConfirmacion = tiposValidos.includes(tipo) ? tipo : "success";
		mostrandoConfirmacion = true;
		return new Promise((resolve) => {
			resolverConfirmacion = resolve;
		});
	}
	function aceptarConfirmacion() {
		mostrandoConfirmacion = false;
		if (resolverConfirmacion) {
			resolverConfirmacion(true);
		}
		resolverConfirmacion = null;
	}
</script>

{#if show}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Asignar Nueva Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}
					>&times;</button
				>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleAsignarLicencia}>
					<div class="form-group">
						<label for="area_asignar"
							>Área * (Total: {areas.length})</label
						>
						<select
							id="area_asignar"
							bind:value={areaSeleccionada}
							required
						>
							<option value="">Seleccione área</option>
							{#each areasDisponibles as area}
								<option value={area.id_area}
									>{area.nombre}</option
								>
							{/each}
						</select>
					</div>
					{#if areaSeleccionada}
						<div class="form-group">
							<label for="agente_asignar">Agente *</label>
							{#if cargandoAgentes}
								<div class="loading-small">
									⏳ Cargando agentes...
								</div>
							{:else if agentesDelArea.length === 0}
								<div class="no-agentes">
									⚠️ No hay agentes en esta área
								</div>
							{:else}
								<select
									id="agente_asignar"
									bind:value={formLicencia.id_agente}
									required
								>
									<option value=""
										>Seleccione un agente...</option
									>
									{#each agentesDelArea as agente}
										<option value={agente.id_agente}
											>{agente.nombre}
											{agente.apellido}</option
										>
									{/each}
								</select>
							{/if}
						</div>
					{/if}
					<div class="form-group">
						<label for="tipo_licencia_asignar"
							>Tipo de Licencia *</label
						>
						<select
							id="tipo_licencia_asignar"
							bind:value={formLicencia.id_tipo_licencia}
							required
						>
							<option value="">Seleccione tipo de licencia</option
							>
							{#each tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}
									>{tipo.codigo} - {tipo.descripcion}</option
								>
							{/each}
						</select>
					</div>
					<div class="form-group">
						<label for="fecha_desde_asignar"
							>Fecha de Inicio *</label
						>
						<input
							type="date"
							id="fecha_desde_asignar"
							bind:value={formLicencia.fecha_desde}
							on:change={handleFechaDesdeChange}
							required
						/>
					</div>
					<div class="form-group">
						<label for="fecha_hasta_asignar">Fecha de Fin *</label>
						<input
							type="date"
							id="fecha_hasta_asignar"
							bind:value={formLicencia.fecha_hasta}
							min={formLicencia.fecha_desde}
							required
						/>
					</div>
					<div class="form-group">
						<label for="justificacion_asignar"
							>Justificación *</label
						>
						<textarea
							id="justificacion_asignar"
							bind:value={formLicencia.justificacion}
							placeholder="Escriba la justificación de la licencia..."
							rows="3"
							required
						></textarea>
					</div>
					<div class="form-group">
						<label for="observaciones_asignar">Observaciones</label>
						<textarea
							id="observaciones_asignar"
							bind:value={formLicencia.observaciones}
							placeholder="Observaciones adicionales (opcional)..."
							rows="2"
						></textarea>
					</div>
					<div class="modal-footer">
						<button
							type="button"
							class="btn-secondary"
							on:click={cerrarModal}
							disabled={enviando}
						>
							Cancelar
						</button>
						<button
							type="submit"
							class="btn-primary"
							disabled={enviando || !formLicencia.id_agente}
						>
							{enviando
								? "⏳ Enviando..."
								: "✅ Asignar Licencia"}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
{#if mostrandoConfirmacion}
	<div class="modal-confirmacion">
		<div class="modal-confirmacion-contenido {tipoConfirmacion}">
			<div class="modal-confirmacion-icono">
				{#if tipoConfirmacion === "success"}
					✓
				{:else if tipoConfirmacion === "error"}
					✕
				{:else if tipoConfirmacion === "warning"}
					⚠
				{:else}
					✓
				{/if}
			</div>
			<h3 class="modal-confirmacion-titulo">{tituloConfirmacion}</h3>
			<p class="modal-confirmacion-mensaje">{mensajeConfirmacion}</p>
			<div class="modal-confirmacion-botones">
				<button
					class="modal-confirmacion-boton"
					on:click={aceptarConfirmacion}
				>
					Aceptar
				</button>
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
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
	}
	.modal-contenido {
		background: white;
		border-radius: 16px;
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}
	.modal-contenido::-webkit-scrollbar {
		display: none;
	}
	.modal-header {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 1.5rem 2rem;
		border-radius: 16px 16px 0 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.modal-header h5 {
		margin: 0;
		font-size: 1.5rem;
	}
	.btn-close {
		background: none;
		border: none;
		color: white;
		font-size: 25px;
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
	.modal-body {
		padding: 2rem;
	}
	.form-group {
		margin-bottom: 1rem;
	}
	.form-group label {
		display: block;
		margin-bottom: 5px;
		font-weight: 600;
		color: #313131;
	}
	.form-group input,
	.form-group select,
	.form-group textarea {
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 8px;
		font-size: 16px;
		transition: all 0.3s ease;
		font-family: inherit;
		resize: vertical;
	}
	.form-group input {
		width: 94%;
	}
	.form-group select {
		width: 100%;
	}
	.form-group textarea {
		width: 94%;
	}
	.loading-small {
		padding: 0.5rem;
		text-align: center;
		background-color: #f8f9fa;
		border: 1px solid #dee2e6;
		border-radius: 4px;
		color: #666;
	}
	.no-agentes {
		padding: 0.5rem;
		text-align: center;
		background-color: #fff3cd;
		border: 1px solid #ffeaa7;
		border-radius: 4px;
		color: #856404;
	}
	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}
	.btn-secondary,
	.btn-primary {
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.btn-primary {
		background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
		color: white;
	}
	.btn-primary:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
	}
	.btn-secondary {
		background: #6c757d;
		color: white;
	}
	.btn-secondary:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-2px);
	}
	.btn-primary:disabled,
	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}
	.modal-confirmacion {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.55);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 99999;
		backdrop-filter: blur(4px);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.modal-confirmacion-contenido {
		background: #ffffff;
		padding: 32px;
		width: 380px;
		border-radius: 16px;
		text-align: center;
		box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
	}
	.modal-confirmacion-contenido.success {
		background: #d4edda;
		border: 4px solid #28a745;
	}
	.modal-confirmacion-contenido.error {
		background: #f8d7da;
		border: 4px solid #dc3545;
	}
	.modal-confirmacion-contenido.warning {
		background: #fff3cd;
		border: 4px solid #ffc107;
	}
	.modal-confirmacion-icono {
		font-size: 3rem;
		font-weight: bold;
		color: inherit;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.modal-confirmacion-titulo {
		font-size: 20px;
		font-weight: 700;
		color: #1e293b;
		margin-bottom: 8px;
	}
	.modal-confirmacion-mensaje {
		font-size: 15px;
		color: #475569;
		margin-bottom: 20px;
	}
	.modal-confirmacion-botones {
		display: flex;
		justify-content: center;
		gap: 10px;
	}
	.modal-confirmacion-boton {
		padding: 10px 28px;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 14px;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 3px 6px rgba(59, 130, 246, 0.3);
	}
	.modal-confirmacion-boton:hover {
		background: #2563eb;
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
	}
</style>
