<script>
	import { asignarLicencia, puedeAsignarAAgente, puedeVerLicenciaDeRol } from '$lib/paneladmin/controllers/licenciasController.js';
	import { personasService } from '$lib/services.js';
	import AuthService from '$lib/login/authService.js';
	
	// Props
	export let show = false;
	export let tiposLicencia = [];
	export let areas = [];
	
	// Usuario actual para validaciones
	let userInfo = null;

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

	let areaSeleccionada = null;
	let agentesDelArea = [];
	let cargandoAgentes = false;
	let enviando = false;

	// Cargar info del usuario al abrir modal
	$: if (show && !userInfo) {
		cargarUsuarioActual();
	}

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
				console.log('👤 Usuario en modal:', userInfo);
			}
		} catch (err) {
			console.error('Error cargando usuario en modal:', err);
		}
	}

	function cerrarModal() {
		show = false;
		dispatch('close');
	}

	async function cargarAgentesPorArea(areaId) {
		console.log('🔄 Cargando agentes para área:', areaId);
		console.log('🔍 Áreas disponibles:', areas);
		if (!areaId) {
			agentesDelArea = [];
			return;
		}

		try {
			cargandoAgentes = true;
			console.log('🌐 Haciendo request para área:', areaId);
			const response = await personasService.getAgentesByArea(areaId);
			console.log('📋 Respuesta completa agentes por área:', response);
			
			// Verificar la estructura de respuesta
			let agentesCompletos = [];
			if (response?.data) {
				if (response.data.results) {
					// Estructura paginada estándar de Django
					agentesCompletos = response.data.results || [];
					console.log('✅ Agentes cargados (formato paginado):', agentesCompletos.length);
				} else if (response.data.success && response.data.data) {
					// Estructura con wrapper de success
					agentesCompletos = response.data.data || [];
					console.log('✅ Agentes cargados (formato success):', agentesCompletos.length);
				} else {
					console.warn('⚠️ Respuesta sin formato conocido:', response.data);
					agentesCompletos = [];
				}
			} else {
				console.warn('⚠️ No hay data en la respuesta:', response);
				agentesCompletos = [];
			}

			// Filtrar agentes según permisos del usuario
			if (userInfo) {
				const rolUsuario = userInfo.roles?.[0]?.nombre || userInfo.rol_nombre || 'Agente';
				console.log('🔍 Filtrando agentes para rol:', rolUsuario);
				
				agentesDelArea = agentesCompletos.filter(agente => {
					const puedeAsignar = puedeAsignarAAgente(
						agente.rol?.nombre || agente.rol_nombre || 'Agente',
						rolUsuario,
						agente.id_area || areaId,
						userInfo.id_area
					);
					console.log(`🔒 ¿Puede asignar a ${agente.nombre} (${agente.rol?.nombre || agente.rol_nombre})?`, puedeAsignar);
					return puedeAsignar;
				});
				
				console.log(`✅ Agentes filtrados: ${agentesDelArea.length} de ${agentesCompletos.length} totales`);
			} else {
				agentesDelArea = agentesCompletos;
			}
		} catch (err) {
			console.error('❌ Error cargando agentes:', err);
			agentesDelArea = [];
		} finally {
			cargandoAgentes = false;
		}
	}

	// Reactivo: cuando cambia el área seleccionada, cargar agentes
	$: if (areaSeleccionada && show && areas.length > 0) {
		console.log('🔄 Reactivo: área seleccionada cambió a:', areaSeleccionada);
		cargarAgentesPorArea(areaSeleccionada);
	}

	async function handleAsignarLicencia() {
		try {
			enviando = true;
			
			console.log('📝 Asignando licencia:', formLicencia);
			
			const resultado = await asignarLicencia(formLicencia);
			
			if (resultado.success) {
				alert('✅ Licencia asignada correctamente');
				cerrarModal();
				dispatch('assigned', resultado.data);
			} else {
				// Usar el mensaje específico del backend si está disponible
				const errorMessage = resultado.error || 'Error al asignar la licencia';
				throw new Error(errorMessage);
			}
	} catch (err) {
		console.error('❌ Error asignando licencia:', err);
		// Mostrar el mensaje específico del backend si está disponible
		const errorMessage = err?.response?.data?.message || err.message || 'Error desconocido';
		alert(`Error: ${errorMessage}`);
	} finally {
			enviando = false;
		}
	}
</script>

{#if show}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Asignar Nueva Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModal}>&times;</button>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleAsignarLicencia}>
					<div class="form-group">
						<label for="area_asignar">Área * (Total: {areas.length})</label>
						<select id="area_asignar" bind:value={areaSeleccionada} on:change={(e) => cargarAgentesPorArea(e.target.value)} required>
							<option value="">Seleccione un área...</option>
							{#each areas as area}
								<option value={area.id_area}>{area.nombre}</option>
							{/each}
						</select>
					</div>

					{#if areaSeleccionada}
						<div class="form-group">
							<label for="agente_asignar">Agente *</label>
							{#if cargandoAgentes}
								<div class="loading-small">⏳ Cargando agentes...</div>
							{:else if agentesDelArea.length === 0}
								<div class="no-agentes">⚠️ No hay agentes en esta área</div>
							{:else}
								<select id="agente_asignar" bind:value={formLicencia.id_agente} required>
									<option value="">Seleccione un agente...</option>
									{#each agentesDelArea as agente}
										<option value={agente.id_agente}>{agente.nombre} {agente.apellido}</option>
									{/each}
								</select>
							{/if}
						</div>
					{/if}

					<div class="form-group">
						<label for="tipo_licencia_asignar">Tipo de Licencia *</label>
						<select id="tipo_licencia_asignar" bind:value={formLicencia.id_tipo_licencia} required>
							<option value="">Seleccione un tipo...</option>
							{#each tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.codigo} - {tipo.descripcion}</option>
							{/each}
						</select>
					</div>

					<div class="form-group">
						<label for="fecha_desde_asignar">Fecha de Inicio *</label>
						<input type="date" id="fecha_desde_asignar" bind:value={formLicencia.fecha_desde} required />
					</div>

					<div class="form-group">
						<label for="fecha_hasta_asignar">Fecha de Fin *</label>
						<input type="date" id="fecha_hasta_asignar" bind:value={formLicencia.fecha_hasta} required />
					</div>

					<div class="form-group">
						<label for="justificacion_asignar">Justificación *</label>
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
						<button type="button" class="btn-secondary" on:click={cerrarModal} disabled={enviando}>
							Cancelar
						</button>
						<button type="submit" class="btn-primary" disabled={enviando || !formLicencia.id_agente}>
							{enviando ? '⏳ Enviando...' : '✅ Asignar Licencia'}
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