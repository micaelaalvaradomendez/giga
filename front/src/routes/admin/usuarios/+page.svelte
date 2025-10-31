<script>
	import { personasService } from '$lib/services.js';
	import AuthService from '$lib/login/authService.js';
	import ModalVerAgente from '$lib/componentes/ModalVerAgente.svelte';
	import ModalEditarAgente from '$lib/componentes/ModalEditarAgente.svelte';
	import ModalEliminarAgente from '$lib/componentes/ModalEliminarAgente.svelte';
	import ModalAgregarAgente from '$lib/componentes/ModalAgregarAgente.svelte';

	/** @type {import('./$types').PageData} */
	export let data;
	
	// Los agentes vienen cargados desde +page.server.js
	let { agentes } = data;
	
	// Estados de los modales
	let modalVerAgente = {
		isOpen: false,
		agente: null
	};
	
	let modalEditarAgente = {
		isOpen: false,
		agente: null,
		isSaving: false
	};
	
	let modalEliminarAgente = {
		isOpen: false,
		agente: null,
		isDeleting: false
	};

	let modalAgregarAgente = {
		isOpen: false,
		isSaving: false
	};

	// Funciones para abrir modales
	function verAgente(agente) {
		modalVerAgente = { isOpen: true, agente };
	}

	function editarAgente(agente) {
		modalEditarAgente = { isOpen: true, agente, isSaving: false };
	}

	function eliminarAgente(agente) {
		modalEliminarAgente = { isOpen: true, agente, isDeleting: false };
	}

	function agregarAgente() {
		modalAgregarAgente = { isOpen: true, isSaving: false };
	}

	// Función para cerrar modales
	function cerrarModales() {
		modalVerAgente.isOpen = false;
		modalEditarAgente.isOpen = false;
		modalEliminarAgente.isOpen = false;
		modalAgregarAgente.isOpen = false;
	}

	// Función para guardar cambios del agente
	async function guardarCambiosAgente(event) {
		const { agente, formData } = event.detail;
		modalEditarAgente.isSaving = true;
		
		try {
			await personasService.updateAgente(agente.id, formData);
			
			// Si se cambió el rol, actualizar la asignación
			if (formData.rol_id) {
				try {
					// Obtener asignaciones actuales del agente
					const asignacionesResponse = await personasService.getAsignaciones();
					const asignaciones = asignacionesResponse.data.results || [];
					const asignacionActual = asignaciones.find(a => a.usuario === agente.usuario);
					
					if (asignacionActual && String(asignacionActual.rol) !== String(formData.rol_id)) {
						// Eliminar asignación actual
						await personasService.deleteAsignacion(asignacionActual.id);
						
						// Crear nueva asignación con el nuevo rol
						await personasService.createAsignacion({
							usuario: agente.usuario,  // Usar usuario, no agente_id
							rol: formData.rol_id,
							area: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', // Área por defecto
						});
					} else if (!asignacionActual && formData.rol_id) {
						// Crear asignación si no existe
						await personasService.createAsignacion({
							usuario: agente.usuario,  // Usar usuario, no agente_id
							rol: formData.rol_id,
							area: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', // Área por defecto
						});
					}
				} catch (rolError) {
					console.error('Error actualizando rol:', rolError);
					alert('El agente se actualizó pero hubo un problema actualizando el rol');
				}
			}
			
			// Actualizar la lista de agentes
			const agenteIndex = agentes.findIndex(a => a.id === agente.id);
			if (agenteIndex !== -1) {
				// Recargar los datos del agente actualizado
				const response = await personasService.getAgente(agente.id);
				agentes[agenteIndex] = response.data;
				agentes = [...agentes]; // Trigger reactivity
			}
			
			alert('Agente actualizado correctamente');
			cerrarModales();
		} catch (error) {
			console.error('Error al actualizar agente:', error);
			let errorMessage = 'Error al actualizar el agente: ';
			
			if (error.response?.status === 400) {
				const errorData = error.response.data;
				if (errorData.dni) {
					errorMessage += 'DNI inválido o ya existe en otro agente.';
				} else if (errorData.email) {
					errorMessage += 'Email inválido o ya registrado por otro usuario.';
				} else if (errorData.cuil) {
					errorMessage += 'CUIL inválido o ya registrado.';
				} else {
					errorMessage += 'Verifique que todos los campos obligatorios estén completos y correctos.';
				}
			} else if (error.response?.status === 404) {
				errorMessage += 'El agente no fue encontrado en el sistema.';
			} else if (error.response?.status === 500) {
				errorMessage += 'Error interno del servidor. Contacte al administrador.';
			} else {
				errorMessage += (error.response?.data?.message || error.message || 'Error desconocido.');
			}
			
			alert(errorMessage);
		} finally {
			modalEditarAgente.isSaving = false;
		}
	}

	// Función para confirmar eliminación
	async function confirmarEliminacionAgente(event) {
		const { agente } = event.detail;
		
		// Verificar si es el usuario logueado
		const currentUser = AuthService.getCurrentUser();
		if (currentUser && (agente.email === currentUser.email || agente.usuario_email === currentUser.email || agente.id === currentUser.id)) {
			alert('⚠️ No puedes eliminarte a ti mismo. Solicita a otro administrador que realice esta acción.');
			modalEliminarAgente.isDeleting = false;
			return;
		}
		
		modalEliminarAgente.isDeleting = true;
		
		try {
			await personasService.deleteAgente(agente.id);
			
			// Remover el agente de la lista
			agentes = agentes.filter(a => a.id !== agente.id);
			
			alert('Agente eliminado correctamente');
			cerrarModales();
		} catch (error) {
			console.error('Error al eliminar agente:', error);
			let errorMessage = 'Error al eliminar el agente: ';
			
			if (error.response?.status === 404) {
				errorMessage += 'El agente no fue encontrado en el sistema.';
			} else if (error.response?.status === 403) {
				errorMessage += 'No tienes permisos para eliminar este agente.';
			} else if (error.response?.status === 409) {
				errorMessage += 'No se puede eliminar el agente porque tiene registros asociados.';
			} else if (error.response?.status === 500) {
				errorMessage += 'Error interno del servidor. Contacte al administrador.';
			} else {
				errorMessage += (error.response?.data?.message || error.message || 'Error desconocido.');
			}
			
			alert(errorMessage);
		} finally {
			modalEliminarAgente.isDeleting = false;
		}
	}

	// Función para crear nuevo agente
	async function crearNuevoAgente(event) {
		const { formData } = event.detail;
		modalAgregarAgente.isSaving = true;
		
		console.log('Datos del formulario para crear agente:', formData);
		
		try {
			const response = await personasService.createAgenteConRol(formData);
			
			// Agregar el nuevo agente a la lista
			agentes = [...agentes, response.data];
			
			alert('✅ Agente creado correctamente con rol asignado');
			cerrarModales();
		} catch (error) {
			console.error('Error al crear agente:', error);
			let errorMessage = 'Error al crear el agente: ';
			
			if (error.response?.status === 400) {
				const errorData = error.response.data;
				
				// Mostrar el error específico del backend si está disponible
				if (errorData.error) {
					errorMessage += errorData.error;
				} else if (errorData.dni) {
					errorMessage += 'DNI inválido o ya existe en el sistema.';
				} else if (errorData.email) {
					errorMessage += 'Email inválido o ya registrado.';
				} else if (errorData.username) {
					errorMessage += 'Nombre de usuario ya existe.';
				} else if (errorData.cuil) {
					errorMessage += 'CUIL inválido o ya registrado.';
				} else {
					console.log('Datos de error completos:', errorData);
					errorMessage += 'Verifique que todos los campos obligatorios estén completos y correctos.';
				}
			} else if (error.response?.status === 500) {
				errorMessage += 'Error interno del servidor. Contacte al administrador.';
			} else {
				errorMessage += (error.response?.data?.message || error.message || 'Error desconocido.');
			}
			
			alert(errorMessage);
		} finally {
			modalAgregarAgente.isSaving = false;
		}
	}
</script>

<div class="logo">
    <a href="/admin">Panel de Administración</a>
</div>

<div class="page-header">
	<h1>Gestión de Agentes</h1>
	<button class="btn-primary" on:click={agregarAgente}>
		+ Añadir Agente
	</button>
</div>

<!-- Resumen de estadísticas -->
{#if agentes && agentes.length > 0}
<div class="stats-container">
	<div class="stat-card">
		<h3>Total Agentes</h3>
		<p class="stat-number">{agentes.length}</p>
	</div>
	<div class="stat-card">
		<h3>EPU</h3>
		<p class="stat-number">{agentes.filter(a => a.agrupacion === 'EPU').length}</p>
	</div>
	<div class="stat-card">
		<h3>POMyS</h3>
		<p class="stat-number">{agentes.filter(a => a.agrupacion === 'POMYS').length}</p>
	</div>
	<div class="stat-card">
		<h3>PAyT</h3>
		<p class="stat-number">{agentes.filter(a => a.agrupacion === 'PAYT').length}</p>
	</div>
	<div class="stat-card">
		<h3>Con Roles</h3>
		<p class="stat-number">{agentes.filter(a => a.roles && a.roles.length > 0).length}</p>
	</div>
	<div class="stat-card">
		<h3>Administradores</h3>
		<p class="stat-number">{agentes.filter(a => a.roles && a.roles.some(r => r.nombre === 'Administrador')).length}</p>
	</div>
</div>
{/if}

<div class="table-container">
	<table>
		<thead>
			<tr>
				<th>Legajo</th>
				<th>Nombre Completo</th>
				<th>DNI</th>
				<th>Roles</th>
				<th>Categoría</th>
				<th>Fecha Nac.</th>
				<th>Email</th>
				<th>Teléfono</th>
				<th>Dirección</th>
				<th>Agrupación</th>
				<th>Acciones</th>
			</tr>
		</thead>
		<tbody>
		{#if agentes && agentes.length > 0}
			{#each agentes as agente}
				{@const currentUser = AuthService.getCurrentUser()}
				<tr class={currentUser && (agente.email === currentUser.email || agente.id === currentUser.id) ? 'current-user' : ''}>
					<td><strong>{agente.legajo || 'N/A'}</strong></td>
					<td>
						<strong>{agente.nombre} {agente.apellido}</strong>
						{#if currentUser && (agente.email === currentUser.email || agente.id === currentUser.id)}
							<span class="badge badge-current-user">Tú</span>
						{/if}
					</td>
						<td>{agente.dni}</td>
						<td>
							{#if agente.roles && agente.roles.length > 0}
								<div class="roles-container">
									{#each agente.roles as rol}
										<div class="role-item">
											<span class="badge badge-role">{rol.nombre}</span>
										</div>
									{/each}
								</div>
							{:else}
								<span class="badge badge-sin-rol">Sin roles</span>
							{/if}
						</td>
						<td>{agente.categoria_revista}</td>
						<td><small>{agente.fecha_nac ? new Date(agente.fecha_nac).toLocaleDateString('es-AR') : 'N/A'}</small></td>
						<td><small>{agente.email}</small></td>
						<td>{agente.telefono}</td>
						<td><small>{agente.direccion || 'N/A'}</small></td>
						<td><span class="badge badge-{agente.agrupacion?.toLowerCase()}">{agente.agrupacion_display || 'Sin agrupación'}</span></td>
					<td class="actions">
						<button class="btn-icon" title="Editar" on:click={() => editarAgente(agente)}>✏️</button>
						<button class="btn-icon" title="Ver detalles" on:click={() => verAgente(agente)}>👁️</button>
						{#if currentUser && (agente.email === currentUser.email || agente.id === currentUser.id)}
							<button class="btn-icon-disabled" title="No puedes eliminarte a ti mismo" disabled>🔒</button>
						{:else}
							<button class="btn-icon-danger" title="Eliminar" on:click={() => eliminarAgente(agente)}>🗑️</button>
						{/if}
					</td>
					</tr>
				{/each}
			{:else}
				<tr>
					<td colspan="11" style="text-align: center; padding: 2rem;">
						No se encontraron agentes. Total: {agentes ? agentes.length : 'undefined'}
					</td>
				</tr>
			{/if}
		</tbody>
	</table>
</div>

<!-- Modales -->
<ModalVerAgente 
	bind:isOpen={modalVerAgente.isOpen}
	agente={modalVerAgente.agente}
	on:cerrar={cerrarModales}
/>

<ModalEditarAgente 
	bind:isOpen={modalEditarAgente.isOpen}
	agente={modalEditarAgente.agente}
	bind:isSaving={modalEditarAgente.isSaving}
	on:cerrar={cerrarModales}
	on:guardar={guardarCambiosAgente}
/>

<ModalEliminarAgente 
	bind:isOpen={modalEliminarAgente.isOpen}
	agente={modalEliminarAgente.agente}
	bind:isDeleting={modalEliminarAgente.isDeleting}
	on:cerrar={cerrarModales}
	on:confirmar={confirmarEliminacionAgente}
/>

<ModalAgregarAgente 
	bind:isOpen={modalAgregarAgente.isOpen}
	bind:isSaving={modalAgregarAgente.isSaving}
	on:cerrar={cerrarModales}
	on:guardar={crearNuevoAgente}
/>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
		background-color: #f8f9fa;
		color: #212529;
	}

	:global(.admin-layout) {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	:global(.admin-header) {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 1.5rem;
		height: 70px;
		background: linear-gradient(135deg, #e79043, #f39c12);
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	:global(.admin-header .logo a) {
		font-weight: bold;
		font-size: 1.3rem;
		text-decoration: none;
		color: white;
		transition: opacity 0.2s;
	}

	:global(.admin-header .logo a:hover) {
		opacity: 0.9;
	}

	:global(.admin-main) {
		display: flex;
		flex-grow: 1;
		overflow: hidden;
	}

	:global(.admin-content-full) {
		flex-grow: 1;
		padding: 2rem;
		overflow-y: auto;
		width: 100%;
		background-color: #ffffff;
		margin: 1rem;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
	}

	.logo {
		display: none; /* Ocultar porque ya está en el header */
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e9ecef;
	}

	.page-header h1 {
		margin: 0;
		color: #2c3e50;
		font-size: 2rem;
		font-weight: 600;
	}

	/* Estilos para estadísticas */
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.stat-card {
		background: white;
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1rem;
		text-align: center;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.stat-card h3 {
		margin: 0 0 0.5rem 0;
		font-size: 0.875rem;
		color: #6c757d;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.stat-number {
		margin: 0;
		font-size: 1.75rem;
		font-weight: 700;
		color: #e79043;
	}

	.btn-primary {
		background: linear-gradient(135deg, #e79043, #f39c12);
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.btn-primary:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0,0,0,0.15);
	}

	.table-container {
		overflow-x: auto;
		border-radius: 8px;
		border: 1px solid #e9ecef;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		background: white;
	}

	thead {
		background: #f8f9fa;
	}

	th {
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #495057;
		border-bottom: 2px solid #e9ecef;
	}

	td {
		padding: 1rem;
		border-bottom: 1px solid #e9ecef;
	}

	tbody tr:hover {
		background-color: #f8f9fa;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
	}

	.btn-icon, .btn-icon-danger {
		background: none;
		border: none;
		font-size: 1.2rem;
		cursor: pointer;
		padding: 0.25rem;
		border-radius: 4px;
		transition: background-color 0.2s;
	}

	.btn-icon:hover {
		background-color: #e9ecef;
	}

	.btn-icon-danger:hover {
		background-color: #f8d7da;
	}

	.btn-icon-disabled {
		background: none;
		border: none;
		font-size: 1.2rem;
		padding: 0.25rem;
		border-radius: 4px;
		color: #6c757d;
		cursor: not-allowed;
		opacity: 0.5;
	}

	/* Estilos para badges */
	.badge {
		display: inline-block;
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		border-radius: 4px;
		text-align: center;
		white-space: nowrap;
	}

	.badge-epu {
		background-color: #d4edda;
		color: #155724;
		border: 1px solid #c3e6cb;
	}

	.badge-pomys {
		background-color: #d1ecf1;
		color: #0c5460;
		border: 1px solid #bee5eb;
	}

	.badge-payt {
		background-color: #fff3cd;
		color: #856404;
		border: 1px solid #ffeaa7;
	}

	.badge-jefe {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.badge-agente {
		background-color: #e2e3e5;
		color: #383d41;
		border: 1px solid #d6d8db;
	}

	.badge-role {
		background-color: #cff4fc;
		color: #055160;
		border: 1px solid #b6effb;
		margin-right: 0.25rem;
	}

	.badge-sin-rol {
		background-color: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.badge-current-user {
		background-color: #e79043;
		color: white;
		border: 1px solid #d68a3b;
		margin-left: 0.5rem;
		font-size: 0.7rem;
	}

	.current-user {
		background-color: #fef9e7;
		border-left: 4px solid #e79043;
	}

	.roles-container {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.role-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.area-text {
		color: #6c757d;
		font-style: italic;
	}

	/* Responsive Design */
	@media (max-width: 1200px) {
		.stats-container {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}
		
		.stats-container {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.table-container {
			overflow-x: auto;
		}
		
		table {
			min-width: 800px; /* Reducir ancho mínimo para móviles */
		}
		
		th, td {
			padding: 0.5rem;
			font-size: 0.875rem;
		}
		
		.btn-icon, .btn-icon-danger {
			padding: 0.5rem;
		}
	}

	@media (max-width: 480px) {
		.stats-container {
			grid-template-columns: 1fr;
		}
		
		.stat-card {
			padding: 0.75rem;
		}
		
		.stat-number {
			font-size: 1.5rem;
		}
	}

	th:nth-child(4), td:nth-child(4) { /* Email */
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	th:nth-child(6), td:nth-child(6) { /* Dirección */
		max-width: 180px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	th:nth-child(7), td:nth-child(7) { /* Agrupación */
		text-align: center;
	}

	th:nth-child(9), td:nth-child(9) { /* Roles */
		max-width: 200px;
	}
</style>
