<script>
	import { crearLicencia } from '$lib/paneladmin/controllers/licenciasController.js';
	
	// Props
	export let show = false;
	export let tiposLicencia = [];
	export let userInfo = null;

	// Events
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

	// Form data
	let formLicencia = {
		id_agente: null,
		id_tipo_licencia: null,
		fecha_desde: '',
		fecha_hasta: '',
		observaciones: '',
		justificacion: ''
	};

	let enviando = false;

	// Limpiar form cuando se cierra el modal
	$: if (!show) {
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: '',
			fecha_hasta: '',
			observaciones: '',
			justificacion: ''
		};
		enviando = false;
	}

	function cerrarModal() {
		show = false;
		dispatch('close');
	}

	async function handleCrearLicencia() {
		if (!userInfo?.id_agente) {
			alert('Error: No se pudo obtener la información del usuario. Por favor, recargue la página e intente nuevamente.');
			return;
		}

		try {
			enviando = true;
			
			// Asignar el agente actual automáticamente
			const datosLicencia = {
				...formLicencia,
				id_agente: userInfo.id_agente
			};

			console.log('📝 Creando licencia:', datosLicencia);
			
			const resultado = await crearLicencia(datosLicencia);
			
			if (resultado.success) {
				alert('✅ Licencia solicitada correctamente');
				cerrarModal();
				dispatch('created', resultado.data);
			} else {
				throw new Error(resultado.message || 'Error al crear la licencia');
			}
		} catch (err) {
			console.error('❌ Error creando licencia:', err);
			alert(`Error: ${err.message}`);
		} finally {
			enviando = false;
		}
	}
</script>

{#if show}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Nueva Solicitud de Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}>&times;</button>
			</div>
			<div class="modal-body">
				<!-- Debug info -->
				<div style="background: #f0f0f0; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 12px;">
					<strong>Debug Modal Solicitud:</strong><br>
					Usuario: {userInfo?.nombre} {userInfo?.apellido} (ID: {userInfo?.id_agente})<br>
					Tipos disponibles: {tiposLicencia.length}
				</div>
				
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
							<option value="">Seleccione un tipo...</option>
							{#each tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
							{/each}
						</select>
					</div>

					<div class="form-group">
						<label for="fecha_desde_crear">Fecha de Inicio *</label>
						<input type="date" id="fecha_desde_crear" bind:value={formLicencia.fecha_desde} required />
					</div>

					<div class="form-group">
						<label for="fecha_hasta_crear">Fecha de Fin *</label>
						<input type="date" id="fecha_hasta_crear" bind:value={formLicencia.fecha_hasta} required />
					</div>

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
	}

	.modal-contenido {
		background: white;
		border-radius: 8px;
		width: 90%;
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		border-bottom: 1px solid #eee;
	}

	.modal-header h5 {
		margin: 0;
		font-size: 1.2rem;
		color: #333;
	}

	.btn-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		color: #666;
		padding: 0;
		width: 30px;
		height: 30px;
	}

	.btn-close:hover {
		color: #000;
	}

	.modal-body {
		padding: 1rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.25rem;
		font-weight: bold;
		color: #333;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.form-group input:disabled {
		background-color: #f5f5f5;
		color: #666;
	}

	.form-text {
		font-size: 0.8rem;
		color: #666;
		margin-top: 0.25rem;
		display: block;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		margin-top: 1.5rem;
	}

	.btn-primary {
		background: #007bff;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
	}

	.btn-primary:hover:not(:disabled) {
		background: #0056b3;
	}

	.btn-primary:disabled {
		background: #6c757d;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #545b62;
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}
</style>