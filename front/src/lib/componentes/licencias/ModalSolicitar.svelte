<script>
	import { createEventDispatcher } from 'svelte';
	import { crearLicencia, calcularDiasLicencia } from '$lib/paneladmin/controllers/licenciasController.js';

	export let show = false;
	export let tiposLicencia = [];
	export let userInfo = null;

	const dispatch = createEventDispatcher();

	let formLicencia = {
		id_tipo_licencia: "",
		observaciones: "",
		justificacion: "",
		fecha_desde: "",
		fecha_hasta: ""
	};

	let enviando = false;
	let diasLicencia = 0;

	$: if (!show) {
		formLicencia = {
			id_tipo_licencia: "",
			observaciones: "",
			justificacion: "",
			fecha_desde: "",
			fecha_hasta: ""
		};
		enviando = false;
	}

	$: diasLicencia = calcularDiasLicencia(formLicencia.fecha_desde, formLicencia.fecha_hasta);

	function cerrarModal() {
		dispatch('close');
	}

	async function handleCrearLicencia() {
		if (!formLicencia.id_tipo_licencia || !formLicencia.fecha_desde || !formLicencia.fecha_hasta || !formLicencia.justificacion) {
			alert("Por favor complete todos los campos obligatorios");
			return;
		}

		enviando = true;
		const datos = {
			...formLicencia,
			id_agente: userInfo?.id_agente
		};

		const resultado = await crearLicencia(datos);

		if (resultado.success) {
			dispatch('created');
			cerrarModal();
		} else {
			alert(resultado.error || "Error al crear la licencia");
		}
		enviando = false;
	}
</script>

{#if show}
	<div class="modal-backdrop" on:click={cerrarModal}>
		<div class="modal-contenido" on:click|stopPropagation>
			<div class="modal-header">
				<h5>Nueva Solicitud de Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}>&times;</button>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleCrearLicencia}>
					<div class="form-group">
						<label for="agente_solicitante">Agente Solicitante</label>
						<input 
							type="text" 
							id="agente_solicitante" 
							value="{userInfo?.nombre} {userInfo?.apellido}" 
							disabled 
						/>
						<small class="form-text">La licencia se solicitará automáticamente para su usuario.</small>
					</div>

					<div class="form-group">
						<label for="tipo_licencia_crear">Tipo de Licencia *</label>
						<select id="tipo_licencia_crear" bind:value={formLicencia.id_tipo_licencia} required>
							<option value="">Seleccione tipo de licencia</option>
							{#each tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.descripcion}</option>
							{/each}
						</select>
					</div>

					<div class="row">
						<div class="form-group" style="flex: 1;">
							<label for="fecha_desde_crear">Desde *</label>
							<input 
								type="date" 
								id="fecha_desde_crear" 
								bind:value={formLicencia.fecha_desde} 
								required 
							/>
						</div>
						<div class="form-group" style="flex: 1;">
							<label for="fecha_hasta_crear">Hasta *</label>
							<input 
								type="date" 
								id="fecha_hasta_crear" 
								bind:value={formLicencia.fecha_hasta} 
								required 
							/>
						</div>
					</div>

					{#if diasLicencia > 0}
						<div class="info-days">
							Duración: <strong>{diasLicencia} días</strong>
						</div>
					{/if}

					<div class="form-group">
						<label for="justificacion_crear">Justificación *</label>
						<textarea 
							id="justificacion_crear" 
							bind:value={formLicencia.justificacion} 
							placeholder="Escriba la justificación de la licencia..."
							rows="3"
							required
						></textarea>
					</div>

					<div class="form-group">
						<label for="observaciones_crear">Observaciones</label>
						<textarea 
							id="observaciones_crear" 
							bind:value={formLicencia.observaciones} 
							placeholder="Observaciones adicionales (opcional)..."
							rows="2"
						></textarea>
					</div>

					<div class="modal-footer">
						<button type="button" class="btn-secondary" on:click={cerrarModal} disabled={enviando}>
							Cancelar
						</button>
						<button type="submit" class="btn-primary" disabled={enviando}>
							{enviando ? '⏳ Enviando...' : '✅ Solicitar Licencia'}
						</button>
					</div>
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
		width: 90%;
		max-width: 500px;
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
		font-weight: 600;
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

	.btn-close:hover {
		background: rgba(255, 255, 255, 0.2);
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
		width: 100%;
		box-sizing: border-box;
	}

	.form-group textarea {
		resize: vertical;
	}

	.form-group input:disabled {
		background-color: #f5f5f5;
		color: #666;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.form-text {
		font-size: 0.8rem;
		color: #666;
		margin-top: 0.25rem;
		display: block;
	}

	.row {
		display: flex;
		gap: 1rem;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.btn-primary {
		padding: 10px 20px;
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
		font-size: 16px;
	}

	.btn-primary:hover:not(:disabled) {
		background: linear-gradient(135deg, #059669, #047857);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
	}

	.btn-primary:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
		border: none;
		padding: 10px 20px;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #545b62;
		transform: translateY(-2px);
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.info-days {
		background-color: #e0f2fe;
		color: #0369a1;
		padding: 10px;
		border-radius: 8px;
		margin-bottom: 1rem;
		text-align: center;
		font-size: 0.9rem;
		font-weight: 600;
	}

	@media (max-width: 480px) {
		.row {
			flex-direction: column;
			gap: 0.5rem;
		}
		
		.modal-contenido {
			width: 95%;
			margin: 10px;
		}
		
		.modal-header {
			padding: 1rem;
		}
		
		.modal-body {
			padding: 1rem;
		}
	}
</style>