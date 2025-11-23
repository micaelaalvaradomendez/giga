<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { asistenciaService, personasService } from '$lib/services.js';
	import AuthService from '$lib/login/authService.js';
	import {
		licencias, tiposLicencia, filtros, loading, error, usuario,
		licenciasFiltradas, estadisticas,
		cargarLicencias, cargarTiposLicencia, crearLicencia,
		aprobarLicencia, rechazarLicencia, actualizarFiltros, limpiarFiltros,
		obtenerPermisos, puedeAprobarLicencia, formatearFecha, calcularDiasLicencia,
		obtenerColorEstado, obtenerIconoEstado
	} from '$lib/paneladmin/controllers/licenciasController.js';

	// Estado principal - alternar entre gestión de licencias y tipos
	let vistaActual = 'licencias'; // 'licencias' o 'tipos'
	
	// Variables para gestión de licencias de usuarios
	let userInfo = null;
	let permisos = {};
	let areas = [];
	let agentes = [];
	
	// Modal states para licencias
	let showModalCrear = false;
	let showModalAprobar = false;
	let showModalRechazar = false;
	let showModalAsignar = false;
	let licenciaSeleccionada = null;
	
	// Form data para licencias
	let formLicencia = {
		id_agente: null,
		id_tipo_licencia: null,
		fecha_desde: '',
		fecha_hasta: '',
		observaciones: '',
		justificacion: ''
	};
	
	let formAprobacion = {
		observaciones: ''
	};
	
	let formRechazo = {
		motivo: ''
	};

	// Variables para gestión de tipos de licencia
	let tipos = [];
	let loadingTipos = false;
	let searchTerm = '';

	// Modal / form para tipos
	let showForm = false;
	let isEditing = false;
	let editingId = null;
	let saving = false;
	let form = {
		codigo: '',
		descripcion: ''
	};

	onMount(async () => {
		await inicializar();
	});

	async function inicializar() {
		try {
			// Obtener información del usuario actual
			const userResponse = await AuthService.getCurrentUserData();
			if (userResponse?.success && userResponse.data?.success) {
				userInfo = userResponse.data.data;
				usuario.set(userInfo);
				permisos = obtenerPermisos(userInfo.rol_nombre, userInfo.id_area);
				
				// Cargar datos iniciales para licencias
				await cargarDatosIniciales();
			} else {
				goto('/');
			}
		} catch (err) {
			console.error('Error inicializando:', err);
			goto('/');
		}
	}

	async function cargarDatosIniciales() {
		try {
			// Cargar tipos de licencia
			await cargarTiposLicencia();
			
			// Cargar áreas si tiene permisos
			if (permisos.puedeVerTodasAreas || permisos.soloSuArea) {
				const areasResponse = await personasService.getAreas();
				if (areasResponse?.data?.success) {
					areas = areasResponse.data.data || [];
					// Si solo puede ver su área, filtrar
					if (permisos.soloSuArea && !permisos.puedeVerTodasAreas) {
						areas = areas.filter(a => a.id_area === userInfo.id_area);
					}
				}
			}
			
			// Cargar agentes de su área si puede asignar licencias
			if (permisos.puedeAsignar) {
				await cargarAgentesArea();
			}
			
			// Cargar licencias con filtros según permisos
			const parametros = {};
			if (permisos.soloSuArea && !permisos.puedeVerTodasAreas) {
				parametros.area_id = userInfo.id_area;
			}
			
			await cargarLicencias(parametros);
		} catch (err) {
			console.error('Error cargando datos iniciales:', err);
			error.set('Error al cargar datos iniciales');
		}
	}

	async function cargarAgentesArea() {
		try {
			const params = permisos.soloSuArea ? { area_id: userInfo.id_area } : {};
			const response = await personasService.getAgentes(params);
			if (response?.data?.success) {
				agentes = response.data.data || [];
			}
		} catch (err) {
			console.error('Error cargando agentes:', err);
		}
	}

	async function cargarTipos() {
		loadingTipos = true;
		error = null;
		try {
			const resp = await asistenciaService.getTiposLicencia();
			if (resp?.data?.success) {
				tipos = resp.data.data || [];
			} else {
				tipos = [];
			}
		} catch (err) {
			console.error(err);
			error = err?.response?.data?.message || err.message || 'Error cargando tipos';
		} finally {
			loadingTipos = false;
		}
	}

	function abrirAlta() {
		isEditing = false;
		editingId = null;
		form = { codigo: '', descripcion: '' };
		showForm = true;
	}

	function abrirEdicion(tipo) {
		isEditing = true;
		editingId = tipo.id_tipo_licencia || tipo.id || null;
		form = { codigo: tipo.codigo || tipo.nombre || '', descripcion: tipo.descripcion || '' };
		showForm = true;
	}

	async function guardar() {
		saving = true;
		error = null;
		try {
			if (isEditing && editingId) {
				const resp = await asistenciaService.updateTipoLicencia(editingId, form);
				if (resp?.data?.success) {
					// actualizar en lista
					tipos = tipos.map(t => (t.id_tipo_licencia === editingId || t.id === editingId) ? resp.data.data : t);
					showForm = false;
				} else {
					error = resp?.data?.message || 'Error al actualizar';
				}
			} else {
				const resp = await asistenciaService.createTipoLicencia(form);
				if (resp?.data?.success) {
					tipos = [resp.data.data, ...tipos];
					showForm = false;
				} else {
					error = resp?.data?.message || 'Error al crear tipo';
				}
			}
		} catch (err) {
			console.error(err);
			error = err?.response?.data?.message || err.message || 'Error guardando';
		} finally {
			saving = false;
		}
	}

	async function eliminar(tipo) {
		const id = tipo.id_tipo_licencia || tipo.id || null;
		if (!id) return;
		if (!confirm(`¿Eliminar el tipo de licencia "${tipo.codigo || tipo.nombre}"? Esta acción fallará si hay agentes con este tipo.`)) return;
		try {
			await asistenciaService.deleteTipoLicencia(id);
			tipos = tipos.filter(t => (t.id_tipo_licencia || t.id) !== id);
		} catch (err) {
			console.error(err);
			const msg = err?.response?.data?.message || err.message || 'No se pudo eliminar. Puede que existan agentes vinculados.';
			alert(msg);
		}
	}

	// Funciones para cambiar vista
	function mostrarLicencias() {
		vistaActual = 'licencias';
	}

	function mostrarTipos() {
		vistaActual = 'tipos';
	}

	$: filtered = tipos.filter(t => {
		if (!searchTerm) return true;
		const s = searchTerm.toLowerCase();
		return (t.codigo || t.nombre || '').toLowerCase().includes(s) || (t.descripcion || '').toLowerCase().includes(s);
	});
</script>

<svelte:head>
	<title>Tipos de Licencia - GIGA</title>
</svelte:head>

<div class="page-container">
		<div class="page-header">
			<div class="header-title">
				<h1>📋 Administración de Licencias</h1>
				<p>Gestión completa de licencias de usuarios y tipos de licencia</p>
			</div>
			<div class="header-actions">
				<!-- Toggle entre vistas -->
				<div class="toggle-buttons">
					<button
						class="btn-toggle {vistaActual === 'licencias' ? 'active' : ''}"
						on:click={mostrarLicencias}
					>
						👥 Gestión de Licencias
					</button>
					<button
						class="btn-toggle {vistaActual === 'tipos' ? 'active' : ''}"
						on:click={mostrarTipos}
					>
						📋 Tipos de Licencia
					</button>
				</div>
				
				{#if vistaActual === 'licencias'}
					<button
						class="btn-header"
						style="background: #8b5cf6; color: white"
						on:click={inicializar}
						disabled={loading}
					>
						{#if loading}
							<span class="spinner"></span>
						{:else}
							🔄
						{/if}
						Actualizar
					</button>
				{:else}
					<button
						class="btn-header"
						style="background: #8b5cf6; color: white"
						on:click={cargarTipos}
						disabled={loadingTipos}
					>
						{#if loadingTipos}
							<span class="spinner"></span>
						{:else}
							🔄
						{/if}
						Actualizar
					</button>
					<button class="btn-header" on:click={abrirAlta} style="background:#22c55e;color:white">➕ Nuevo Tipo</button>
				{/if}
			</div>
		</div>
	
	<!-- Contenido principal con vista condicional -->
	<div class="page-content">
		{#if vistaActual === 'licencias'}
			<!-- Vista de Gestión de Licencias -->
			<div class="licencias-content">
				{#if $loading}
					<div class="loading-state">
						<div class="spinner"></div>
						<p>Cargando licencias...</p>
					</div>
				{:else if $error}
					<div class="alert alert-error">
						<strong>❌ Error:</strong>
						{$error}
						<button class="btn-primary" on:click={inicializar}>Reintentar</button>
					</div>
				{:else}
					<!-- Filtros para licencias -->
					<div class="filtros-container">
						<div class="filtros-row">
							<div class="filtro-group">
								<label>📅 Estado</label>
								<select bind:value={$filtros.estado} on:change={() => actualizarFiltros()}>
									<option value="">Todos los estados</option>
									<option value="pendiente">Pendiente</option>
									<option value="aprobada">Aprobada</option>
									<option value="rechazada">Rechazada</option>
								</select>
							</div>
							
							{#if permisos.puedeVerTodasAreas || areas.length > 1}
								<div class="filtro-group">
									<label>🏢 Área</label>
									<select bind:value={$filtros.area_id} on:change={() => actualizarFiltros()}>
										<option value="">Todas las áreas</option>
										{#each areas as area}
											<option value={area.id_area}>{area.nombre}</option>
										{/each}
									</select>
								</div>
							{/if}
							
							<div class="filtro-group">
								<label>📋 Tipo de Licencia</label>
								<select bind:value={$filtros.tipo_id} on:change={() => actualizarFiltros()}>
									<option value="">Todos los tipos</option>
									{#each $tiposLicencia as tipo}
										<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
									{/each}
								</select>
							</div>
							
							<button class="btn-secondary" on:click={limpiarFiltros}>🧹 Limpiar</button>
						</div>
					</div>

					<!-- Estadísticas -->
					{#if $estadisticas}
						<div class="stats-container">
							<div class="stat-card">
								<div class="stat-number">{$estadisticas.total || 0}</div>
								<div class="stat-label">Total Licencias</div>
							</div>
							<div class="stat-card">
								<div class="stat-number">{$estadisticas.pendientes || 0}</div>
								<div class="stat-label">Pendientes</div>
							</div>
							<div class="stat-card">
								<div class="stat-number">{$estadisticas.aprobadas || 0}</div>
								<div class="stat-label">Aprobadas</div>
							</div>
							<div class="stat-card">
								<div class="stat-number">{$estadisticas.rechazadas || 0}</div>
								<div class="stat-label">Rechazadas</div>
							</div>
						</div>
					{/if}

					<!-- Tabla de licencias -->
					<div class="table-container">
						<table>
							<thead>
								<tr>
									<th>Agente</th>
									<th>Área</th>
									<th>Tipo</th>
									<th>Fecha Inicio</th>
									<th>Fecha Fin</th>
									<th>Días</th>
									<th>Estado</th>
									<th>Solicitada</th>
									{#if permisos.puedeAprobar}
										<th>Acciones</th>
									{/if}
								</tr>
							</thead>
							<tbody>
								{#each $licenciasFiltradas as licencia}
									<tr>
										<td>{licencia.agente_nombre} {licencia.agente_apellido}</td>
										<td>{licencia.area_nombre}</td>
										<td>{licencia.tipo_nombre}</td>
										<td>{formatearFecha(licencia.fecha_inicio)}</td>
										<td>{formatearFecha(licencia.fecha_fin)}</td>
										<td>{calcularDiasLicencia(licencia.fecha_inicio, licencia.fecha_fin)}</td>
										<td>
											<span class="badge badge-{obtenerColorEstado(licencia.estado)}">
												{obtenerIconoEstado(licencia.estado)} {licencia.estado}
											</span>
										</td>
										<td>{formatearFecha(licencia.creado_en)}</td>
										{#if permisos.puedeAprobar && puedeAprobarLicencia(licencia)}
											<td>
												{#if licencia.estado === 'pendiente'}
													<div class="action-buttons">
														<button 
															class="btn-success btn-sm"
															on:click={() => aprobarLicencia(licencia.id_licencia)}
															title="Aprobar licencia"
														>
															✅
														</button>
														<button 
															class="btn-danger btn-sm"
															on:click={() => rechazarLicencia(licencia.id_licencia)}
															title="Rechazar licencia"
														>
															❌
														</button>
													</div>
												{:else}
													<span class="text-muted">—</span>
												{/if}
											</td>
										{/if}
									</tr>
								{:else}
									<tr>
										<td colspan="8" style="text-align: center; padding: 2rem; color: #6c757d;">
											No hay licencias para mostrar con los filtros actuales
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</div>
		{:else}
			<!-- Vista de Tipos de Licencia -->
			{#if error}
				<div class="alert alert-error">
					<strong>❌ Error:</strong>
					{error}
					<button class="btn-primary" on:click={cargarTipos}>Reintentar</button>
				</div>
			{/if}

		<div class="filtros-container">
			<div class="filtros-row">
				<div class="filtro-group">
					<label for="busqueda">🔍 Buscar tipo</label>
					<input
						type="text"
						id="busqueda"
						bind:value={searchTerm}
						placeholder="Buscar por código o descripción..."
						class="input-busqueda"
					/>
				</div>
				<div class="filtro-actions">
					<button class="btn-limpiar" on:click={() => (searchTerm = '')} title="Limpiar filtros">🗑️ Limpiar</button>
				</div>
			</div>
			
			<!-- Nota informativa sobre la funcionalidad -->
			<div style="margin-top: 1rem; padding: 1rem; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px;">
				<p style="margin: 0; color: #1565c0; font-size: 0.9rem;">
					<strong>📋 Gestión de Licencias:</strong> Esta sección administra los tipos de licencia del sistema. 
					Para gestionar licencias de usuarios (asignar, aprobar, rechazar), utiliza el botón 
					<strong>"👥 Ver Licencias de Usuarios"</strong> arriba.
				</p>
			</div>
		</div>

		{#if loading}
			<div class="loading-container">
				<div class="spinner-large"></div>
				<p>Cargando información...</p>
			</div>
		{:else if filtered.length === 0 && !loading}
			<div class="empty-state">
				<div class="empty-icon">📄</div>
				<h3>No se encontraron tipos</h3>
				<p>
					{#if searchTerm}
						No hay tipos que coincidan con "{searchTerm}".
					{:else}
						No hay tipos de licencia registrados.
					{/if}
				</p>
				{#if searchTerm}
					<button class="btn-primary" on:click={() => (searchTerm = '')}>Limpiar búsqueda</button>
				{/if}
			</div>
		{:else}
			<div class="table-container">
				<table class="roles-table">
					<thead>
						<tr>
							<th>Código</th>
							<th>Descripción</th>
							<th>Acciones</th>
						</tr>
					</thead>
					<tbody>
						{#each filtered as tipo (tipo.id_tipo_licencia || tipo.id)}
							<tr>
								<td>
									<strong>{tipo.codigo || tipo.nombre || '—'}</strong>
								</td>
								<td>{tipo.descripcion || '—'}</td>
								<td>
									<button class="btn-primary" on:click={() => abrirEdicion(tipo)}>✏️ Editar</button>
									<button class="btn-secondary" on:click={() => eliminar(tipo)} style="margin-left:6px">🗑️ Eliminar</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}

		{#if showForm}
			<div class="modal-overlay">
				<div class="modal">
					<h3>{isEditing ? 'Editar tipo de licencia' : 'Nuevo tipo de licencia'}</h3>
					{#if error}
						<div class="alert alert-error">{error}</div>
					{/if}
					<div class="form-row">
						<label>Código</label>
						<input bind:value={form.codigo} />
					</div>
					<div class="form-row">
						<label>Descripción</label>
						<textarea rows="3" bind:value={form.descripcion}></textarea>
					</div>
					<div class="form-actions">
						<button class="btn-primary" on:click={guardar} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
						<button class="btn-limpiar" on:click={() => (showForm = false)} disabled={saving}>Cancelar</button>
					</div>
				</div>
			</div>
		{/if}
		{/if}
	</div>
</div>

<style>
	/* Reuse page styles found in other paneladmin pages (kept minimal here) */
	.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; padding-bottom:1rem }
	.header-title h1 { margin:0; font-size:22px }
	.header-actions { display:flex; gap:0.5rem }
	.filtros-container { background: white; border:1px solid #e9ecef; border-radius:8px; padding:1rem; margin-bottom:1rem }
	.filtros-row { display:flex; gap:1rem; align-items:end }
	.filtro-group label { font-weight:500 }
	.input-busqueda { padding:0.6rem; border:1px solid #ced4da; border-radius:6px }
	.table-container { overflow-x:auto; border-radius:12px; background:white }
	table { width:100%; border-collapse:collapse }
	th, td { padding:12px 16px; text-align:left }
	thead { background:linear-gradient(135deg,#4865e9 0%,#527ab6d0 100%); color:white }
	tbody tr:hover { background:#f8f9fa }
	.btn-header, .btn-primary, .btn-limpiar, .btn-secondary { border:none; padding:8px 12px; border-radius:6px; cursor:pointer }
	.btn-primary { background:linear-gradient(135deg,#e79043,#f39c12); color:white }
	.btn-limpiar { background:#6c757d; color:white }
	.btn-secondary { background:#6b7280; color:white }

	/* Modal simple */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:2000 }
	.modal { background:white; padding:1.25rem; border-radius:10px; width:520px; max-width:92%; box-shadow:0 10px 30px rgba(0,0,0,0.2) }
	.form-row { margin-bottom:0.75rem; display:flex; flex-direction:column }
	.form-row label { font-weight:600; margin-bottom:6px }
	.form-row input, .form-row textarea { padding:8px; border:1px solid #d1d5db; border-radius:6px }
	.form-actions { display:flex; gap:8px; justify-content:flex-end; margin-top:8px }
	.modal h3 { margin-top:0 }
	
	/* Toggle buttons */
	.toggle-buttons { display: flex; gap: 0.5rem; margin-right: 1rem; }
	.btn-toggle { 
		border: none; 
		padding: 10px 16px; 
		border-radius: 6px; 
		cursor: pointer; 
		background: #f8f9fa; 
		color: #495057; 
		font-weight: 500;
		transition: all 0.2s ease;
	}
	.btn-toggle:hover { background: #e9ecef; }
	.btn-toggle.active { 
		background: linear-gradient(135deg, #4865e9 0%, #527ab6d0 100%); 
		color: white; 
	}
	
	/* Licencias management styles */
	.loading-state { text-align: center; padding: 3rem; color: #6c757d; }
	.loading-state .spinner { margin: 0 auto 1rem; width: 2rem; height: 2rem; }
	.stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
	.stat-card { background: white; border-radius: 8px; padding: 1.5rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
	.stat-number { font-size: 2rem; font-weight: bold; color: #4865e9; }
	.stat-label { font-size: 0.875rem; color: #6c757d; margin-top: 0.5rem; }
	.badge { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 500; }
	.badge-pendiente { background: #fef3c7; color: #d97706; }
	.badge-aprobada { background: #dcfce7; color: #16a34a; }
	.badge-rechazada { background: #fee2e2; color: #dc2626; }
	.action-buttons { display: flex; gap: 0.5rem; }
	.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; }
	.btn-success { background: #22c55e; color: white; border: none; border-radius: 4px; cursor: pointer; }
	.btn-danger { background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; }
	.text-muted { color: #6c757d; }
	select { padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 4px; background: white; }
</style>
