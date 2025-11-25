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

	// Usuario actual para validaciones
	let userInfo = null;

	// Events
	import { createEventDispatcher } from "svelte";
	const dispatch = createEventDispatcher();

	// Form data
	let formLicencia = {
		id_agente: null,
		id_tipo_licencia: null,
		fecha_desde: "",
		fecha_hasta: "",
		observaciones: "",
		justificacion: "",
	};

	let areaSeleccionada = null;
	let agentesDelArea = [];
	let cargandoAgentes = false;
	let enviando = false;

	// Modal de confirmación / alerta
	let mostrandoConfirmacion = false;
	let tituloConfirmacion = "";
	let mensajeConfirmacion = "";
	let tipoConfirmacion = "success";
	let resolverConfirmacion = null;

	// Cargar info del usuario al abrir modal
	$: if (show && !userInfo) {
		cargarUsuarioActual();
	}

	// Limpiar form cuando se cierra el modal
	$: if (!show) {
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: "",
			fecha_hasta: "",
			observaciones: "",
			justificacion: "",
		};
		areaSeleccionada = null;
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
				console.log("👤 Usuario en modal:", userInfo);
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
		console.log("🔄 Cargando agentes para área:", areaId);
		console.log("🔍 Áreas disponibles:", areas);
		if (!areaId) {
			agentesDelArea = [];
			return;
		}

		try {
			cargandoAgentes = true;
			console.log("🌐 Haciendo request para área:", areaId);
			const response = await personasService.getAgentesByArea(areaId);
			console.log("📋 Respuesta completa agentes por área:", response);

			// Verificar la estructura de respuesta
			let agentesCompletos = [];
			if (response?.data) {
				if (response.data.results) {
					// Estructura paginada estándar de Django
					agentesCompletos = response.data.results || [];
					console.log(
						"✅ Agentes cargados (formato paginado):",
						agentesCompletos.length,
					);
				} else if (response.data.success && response.data.data) {
					// Estructura con wrapper de success
					agentesCompletos = response.data.data || [];
					console.log(
						"✅ Agentes cargados (formato success):",
						agentesCompletos.length,
					);
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

			// Filtrar agentes según permisos del usuario
			if (userInfo) {
				const rolUsuario =
					userInfo.roles?.[0]?.nombre ||
					userInfo.rol_nombre ||
					"Agente";
				console.log("🔍 Filtrando agentes para rol:", rolUsuario);

				agentesDelArea = agentesCompletos.filter((agente) => {
					const puedeAsignar = puedeAsignarAAgente(
						agente.rol?.nombre || agente.rol_nombre || "Agente",
						rolUsuario,
						agente.id_area || areaId,
						userInfo.id_area,
					);
					console.log(
						`🔒 ¿Puede asignar a ${agente.nombre} (${agente.rol?.nombre || agente.rol_nombre})?`,
						puedeAsignar,
					);
					return puedeAsignar;
				});

				console.log(
					`✅ Agentes filtrados: ${agentesDelArea.length} de ${agentesCompletos.length} totales`,
				);
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

	// Reactivo: cuando cambia el área seleccionada, cargar agentes
	$: if (areaSeleccionada && show && areas.length > 0) {
		console.log(
			"🔄 Reactivo: área seleccionada cambió a:",
			areaSeleccionada,
		);
		cargarAgentesPorArea(areaSeleccionada);
	}

	async function handleAsignarLicencia() {
		try {
			enviando = true;

			console.log("📝 Asignando licencia:", formLicencia);

			const resultado = await asignarLicencia(formLicencia);

			if (resultado.success) {
				mostrarConfirmacion("✅ Licencia asignada correctamente");
				cerrarModal();
				dispatch("assigned", resultado.data);
			} else {
				// Usar el mensaje específico del backend si está disponible
				const errorMessage =
					resultado.error || "Error al asignar la licencia";
				throw new Error(errorMessage);
			}
		} catch (err) {
			console.error("❌ Error asignando licencia:", err);
			// Mostrar el mensaje específico del backend si está disponible
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
							on:change={(e) =>
								cargarAgentesPorArea(e.target.value)}
							required
						>
							<option value="">Seleccione un área...</option>
							{#each areas as area}
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
							<option value="">Seleccione un tipo...</option>
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
							required
						/>
					</div>

					<div class="form-group">
						<label for="fecha_hasta_asignar">Fecha de Fin *</label>
						<input
							type="date"
							id="fecha_hasta_asignar"
							bind:value={formLicencia.fecha_hasta}
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

	/* Modal de confirmación/alerta */
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
