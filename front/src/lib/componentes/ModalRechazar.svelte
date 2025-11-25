<script>
	import { rechazarLicencia } from "$lib/paneladmin/controllers/licenciasController.js";
	import { createEventDispatcher } from "svelte";

	// Props
	export let show = false;
	export let licencia = null;

	const dispatch = createEventDispatcher();

	// Form data
	let formRechazo = { motivo: "" };
	let enviando = false;

	// Modal de confirmación / alerta
	let mostrandoConfirmacion = false;
	let tituloConfirmacion = "";
	let mensajeConfirmacion = "";
	let tipoConfirmacion = "success";
	let resolverConfirmacion = null;

	// Reset al cerrar modal principal
	$: if (!show) {
		formRechazo = { motivo: "" };
		enviando = false;
	}

	function cerrarModal() {
		show = false;
		dispatch("close");
	}

	function mostrarConfirmacion(titulo, mensaje = "", tipo = "success") {
		tituloConfirmacion = titulo;
		mensajeConfirmacion = mensaje;

		const valid = ["success", "error", "warning"];
		tipoConfirmacion = valid.includes(tipo) ? tipo : "success";

		mostrandoConfirmacion = true;
		resolverConfirmacion = null;
	}

	// POR SI después querés confirmación real (sí/no)
	function confirmar(titulo, mensaje = "", tipo = "warning") {
		tituloConfirmacion = titulo;
		mensajeConfirmacion = mensaje;

		const valid = ["success", "error", "warning"];
		tipoConfirmacion = valid.includes(tipo) ? tipo : "warning";

		mostrandoConfirmacion = true;

		return new Promise((resolve) => {
			resolverConfirmacion = resolve;
		});
	}

	function aceptarConfirmacion() {
		mostrandoConfirmacion = false;

		if (resolverConfirmacion) {
			resolverConfirmacion(true);
			resolverConfirmacion = null;
		}
	}

	async function handleRechazar() {
		if (!licencia?.id_licencia) {
			mostrarConfirmacion(
				"Error: Licencia no válida",
				"No se ha seleccionado una licencia para rechazar.",
				"error",
			);
			return;
		}

		if (!formRechazo.motivo.trim()) {
			mostrarConfirmacion(
				"Motivo requerido",
				"Debe proporcionar un motivo para rechazar la licencia.",
				"warning",
			);
			return;
		}

		try {
			enviando = true;

			const resultado = await rechazarLicencia(
				licencia.id_licencia,
				formRechazo,
			);

			if (resultado.success) {
				mostrarConfirmacion(
					"Licencia rechazada",
					"Se notificará al agente.",
					"success",
				);

				cerrarModal();
				dispatch("rejected", resultado.data);
			} else {
				throw new Error(
					resultado.message || "Error al rechazar la licencia",
				);
			}
		} catch (err) {
			mostrarConfirmacion("Error al rechazar", err.message, "error");
		} finally {
			enviando = false;
		}
	}
</script>

{#if show && licencia}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Rechazar Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}
					>&times;</button
				>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<div class="info-row">
						<strong>Agente:</strong>
						{licencia.agente?.nombre}
						{licencia.agente?.apellido}
					</div>
					<div class="info-row">
						<strong>Tipo:</strong>
						{licencia.tipo_licencia?.nombre || "N/A"}
					</div>
					<div class="info-row">
						<strong>Período:</strong>
						{licencia.fecha_desde} - {licencia.fecha_hasta}
					</div>
					<div class="info-row">
						<strong>Días:</strong>
						{licencia.dias_solicitados}
					</div>
					{#if licencia.justificacion}
						<div class="info-row">
							<strong>Justificación:</strong>
							{licencia.justificacion}
						</div>
					{/if}
				</div>

				<form on:submit|preventDefault={handleRechazar}>
					<div class="form-group">
						<label for="motivo_rechazo">Motivo del Rechazo *</label>
						<textarea
							id="motivo_rechazo"
							bind:value={formRechazo.motivo}
							placeholder="Ingrese el motivo del rechazo (requerido)..."
							rows="4"
							required
						></textarea>
						<small class="form-text text-danger">
							⚠️ El motivo del rechazo es obligatorio y será
							notificado al solicitante.
						</small>
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
							class="btn-danger"
							disabled={enviando || !formRechazo.motivo.trim()}
						>
							{enviando
								? "⏳ Rechazando..."
								: "❌ Rechazar Licencia"}
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

	.licencia-info {
		background: #f7f7f7;
		border: 1px solid #e1e1e1;
		border-radius: 10px;
		padding: 1.2rem;
		margin-bottom: 1.2rem;
	}

	.licencia-info h6 {
		font-size: 16px;
		margin: 0 0 0.5rem 0;
		color: #495057;
		font-weight: 600;
	}

	.info-row {
		margin-bottom: 0.3rem;
		font-size: 0.9rem;
		width: 100%;
	}

	.form-group {
		margin-bottom: 1.3rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 600;
		color: #313131;
	}

	.form-group textarea {
		width: 94%;
		padding: 12px 15px;
		border: 2px solid #e1e5e9;
		border-radius: 10px;
		font-size: 16px;
		transition: all 0.25s ease;
		font-family: inherit;
		resize: vertical;
		margin-bottom: 5px;
	}

	.form-group textarea:focus {
		border-color: #84a59d;
		box-shadow: 0 0 0 3px rgba(132, 165, 157, 0.25);
	}

	.text-danger {
		color: #dc3545;
		font-size: 16px;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.btn-danger,
	.btn-secondary {
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-danger {
		background: #c9302c;
		color: white;
	}

	.btn-danger:hover:not(:disabled) {
		background: #c9302c;
		transform: scale(1.04);
	}

	.btn-danger:disabled {
		background: #da4141;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #545b62;
		transform: scale(1.04);
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
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
	}
</style>
