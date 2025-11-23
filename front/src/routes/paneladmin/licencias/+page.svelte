<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import AuthService from '$lib/login/authService.js';
	import { asistenciaService, personasService } from '$lib/services.js';
	import {
		licencias, tiposLicencia, filtros, loading, error, usuario,
		licenciasFiltradas, estadisticas,
		cargarLicencias, cargarTiposLicencia, crearLicencia, asignarLicencia,
		aprobarLicencia, rechazarLicencia, actualizarFiltros, limpiarFiltros,
		obtenerPermisos, puedeAprobarLicencia, formatearFecha, calcularDiasLicencia,
		obtenerColorEstado, obtenerIconoEstado
	} from '$lib/paneladmin/controllers/licenciasController.js';

	// Estado principal - alternar entre gestión de licencias y tipos
	let vistaActual = 'licencias'; // 'licencias' o 'tipos'

	// Variables principales para gestión de licencias
	let userInfo = null;
	let permisos = {};
	let areas = [];
	
	// Modal states para licencias
	let showModalCrear = false;
	let showModalAprobar = false;
	let showModalRechazar = false;
	let showModalAsignar = false;
	let licenciaSeleccionada = null;
	
	// Variables para asignación de licencias
	let areaSeleccionada = null;
	let agentesDelArea = [];
	let cargandoAgentes = false;
	
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

	let saving = false;

	// Variables para gestión de tipos de licencia (conservando la funcionalidad existente)
	let tipos = [];
	let loadingTipos = false;
	let errorTipos = null;
	let searchTerm = '';

	// Modal / form para tipos
	let showForm = false;
	let isEditing = false;
	let editingId = null;
	let form = {
		codigo: '',
		descripcion: ''
	};

	onMount(async () => {
		console.log('Iniciando página de licencias...');
		await inicializar();
	});

	async function inicializar() {
		console.log('Inicializando datos...');
		
		// Primero cargar datos básicos
		await cargarDatosIniciales();
		
		// Luego intentar autenticación (no bloquear la página si falla)
		try {
			const userResponse = await AuthService.getCurrentUserData();
			console.log('Respuesta de usuario:', userResponse);
			
			if (userResponse?.success && userResponse.data?.success) {
				userInfo = userResponse.data.data;
				usuario.set(userInfo);
				console.log('Usuario cargado:', userInfo);
				
				// Solo mostrar advertencia si no es administrador, pero permitir acceso
				if (userInfo.rol !== 'Administrador') {
					console.warn('Usuario sin rol de administrador accediendo al panel:', userInfo.rol);
				}
			} else {
				console.warn('No se pudo obtener información del usuario, continuando sin autenticación');
			}
		} catch (err) {
			console.error('Error en autenticación, continuando:', err);
		}
	}

	async function cargarDatosIniciales() {
		console.log('Cargando datos iniciales...');
		
		// Cargar tipos de licencia para los selectores
		try {
			console.log('Cargando tipos de licencia...');
			await cargarTiposLicencia();
			console.log('Tipos de licencia cargados');
		} catch (err) {
			console.error('Error cargando tipos de licencia:', err);
		}
		
		// Cargar todas las áreas para filtros
		try {
			console.log('Cargando áreas...');
			const areasResponse = await personasService.getAreas();
			if (areasResponse?.data?.success) {
				areas = areasResponse.data.data || [];
				console.log('Áreas cargadas:', areas.length);
			}
		} catch (err) {
			console.error('Error cargando áreas:', err);
			areas = [];
		}
		
		// Cargar licencias inicialmente
		try {
			console.log('Cargando licencias...');
			await cargarLicencias();
			console.log('Licencias cargadas');
		} catch (err) {
			console.error('Error cargando licencias:', err);
		}
		
		// Cargar tipos para gestión (vista de tipos)
		try {
			console.log('Cargando tipos para gestión...');
			await cargarTipos();
			console.log('Tipos para gestión cargados');
		} catch (err) {
			console.error('Error cargando tipos para gestión:', err);
		}
		
		console.log('Carga de datos iniciales completada');
	}

	// Funciones para carga de agentes por área
	async function cargarAgentesPorArea(areaId) {
		if (!areaId) {
			agentesDelArea = [];
			return;
		}

		try {
			cargandoAgentes = true;
			const response = await personasService.getAgentesPorArea(areaId);
			if (response?.data?.success) {
				agentesDelArea = response.data.data || [];
			} else {
				console.error('Error cargando agentes:', response?.data?.message);
				agentesDelArea = [];
			}
		} catch (err) {
			console.error('Error cargando agentes del área:', err);
			agentesDelArea = [];
		} finally {
			cargandoAgentes = false;
		}
	}

	// Funciones para modales de licencias
	function abrirModalCrear() {
		licenciaSeleccionada = null;
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: '',
			fecha_hasta: '',
			observaciones: '',
			justificacion: ''
		};
		showModalCrear = true;
	}

	function abrirModalAsignar() {
		areaSeleccionada = null;
		agentesDelArea = [];
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: '',
			fecha_hasta: '',
			observaciones: '',
			justificacion: ''
		};
		showModalAsignar = true;
	}

	function abrirModalAprobar(licencia) {
		licenciaSeleccionada = licencia;
		formAprobacion = { observaciones: '' };
		showModalAprobar = true;
	}

	function abrirModalRechazar(licencia) {
		licenciaSeleccionada = licencia;
		formRechazo = { motivo: '' };
		showModalRechazar = true;
	}

	function cerrarModales() {
		showModalCrear = false;
		showModalAsignar = false;
		showModalAprobar = false;
		showModalRechazar = false;
		licenciaSeleccionada = null;
		areaSeleccionada = null;
		agentesDelArea = [];
	}

	// Funciones para manejar las acciones de licencias
	async function handleCrearLicencia() {
		if (!formLicencia.id_tipo_licencia || !formLicencia.fecha_desde || !formLicencia.fecha_hasta) {
			alert('Por favor complete todos los campos obligatorios');
			return;
		}

		if (new Date(formLicencia.fecha_desde) > new Date(formLicencia.fecha_hasta)) {
			alert('La fecha de inicio no puede ser posterior a la fecha de fin');
			return;
		}

		// Verificar que tenemos el ID del agente (usuario actual)
		if (!userInfo?.id_agente) {
			alert('No se puede crear la licencia: información de usuario no disponible');
			return;
		}

		saving = true;
		const resultado = await crearLicencia({
			...formLicencia,
			id_agente: userInfo.id_agente, // Usar el ID del usuario actual
			estado: 'pendiente'
		});

		if (resultado.success) {
			cerrarModales();
			alert('Licencia solicitada correctamente. Aguarde aprobación.');
		} else {
			alert(resultado.error);
		}
		saving = false;
	}

	async function handleAsignarLicencia() {
		if (!areaSeleccionada || !formLicencia.id_agente || !formLicencia.id_tipo_licencia || !formLicencia.fecha_desde || !formLicencia.fecha_hasta) {
			alert('Por favor complete todos los campos obligatorios');
			return;
		}

		saving = true;
		const resultado = await asignarLicencia({
			id_agente: formLicencia.id_agente,
			id_tipo_licencia: formLicencia.id_tipo_licencia,
			fecha_desde: formLicencia.fecha_desde,
			fecha_hasta: formLicencia.fecha_hasta,
			observaciones: formLicencia.observaciones || ''
		});

		if (resultado.success) {
			cerrarModales();
			alert('Licencia asignada correctamente.');
		} else {
			alert(resultado.error);
		}
		saving = false;
	}

	async function handleAprobarLicencia() {
		if (!licenciaSeleccionada) return;
		
		saving = true;
		const resultado = await aprobarLicencia(licenciaSeleccionada.id_licencia, formAprobacion.observaciones);

		if (resultado.success) {
			cerrarModales();
			alert('Licencia aprobada correctamente.');
		} else {
			alert(resultado.error);
		}
		saving = false;
	}

	async function handleRechazarLicencia() {
		if (!licenciaSeleccionada || !formRechazo.motivo.trim()) {
			alert('Debe indicar el motivo del rechazo');
			return;
		}
		
		saving = true;
		const resultado = await rechazarLicencia(licenciaSeleccionada.id_licencia, formRechazo.motivo);

		if (resultado.success) {
			cerrarModales();
			alert('Licencia rechazada.');
		} else {
			alert(resultado.error);
		}
		saving = false;
	}

	// Funciones para filtros
	function aplicarFiltros() {
		cargarLicencias($filtros);
	}

	function limpiarTodosFiltros() {
		limpiarFiltros();
		cargarLicencias();
	}

	// Funciones de utilidad
	function puedeAprobar(licencia) {
		// Como es administrador, siempre puede aprobar
		return licencia.estado === 'pendiente';
	}

	// Función para cambiar entre vistas
	function cambiarVista(vista) {
		vistaActual = vista;
		if (vista === 'tipos') {
			cargarTipos();
		}
	}

	// Funciones para gestión de tipos de licencia (conservando la funcionalidad existente)
	async function cargarTipos() {
		loadingTipos = true;
		errorTipos = null;
		try {
			const resp = await asistenciaService.getTiposLicencia();
			if (resp?.data?.success) {
				tipos = resp.data.data || [];
			} else {
				tipos = [];
				errorTipos = resp?.data?.message || 'Error al cargar tipos';
			}
		} catch (err) {
			console.error(err);
			errorTipos = err?.response?.data?.message || err.message || 'Error cargando tipos';
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
		if (!form.codigo.trim()) {
			alert('El código es obligatorio');
			return;
		}

		saving = true;
		errorTipos = null;
		try {
			if (isEditing && editingId) {
				const resp = await asistenciaService.updateTipoLicencia(editingId, form);
				if (resp?.data?.success) {
					// actualizar en lista
					tipos = tipos.map(t => (t.id_tipo_licencia === editingId || t.id === editingId) ? resp.data.data : t);
					showForm = false;
				} else {
					errorTipos = resp?.data?.message || 'Error al actualizar';
				}
			} else {
				const resp = await asistenciaService.createTipoLicencia(form);
				if (resp?.data?.success) {
					tipos = [resp.data.data, ...tipos];
					showForm = false;
				} else {
					errorTipos = resp?.data?.message || 'Error al crear tipo';
				}
			}
		} catch (err) {
			console.error(err);
			errorTipos = err?.response?.data?.message || err.message || 'Error guardando';
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

	// Variables reactivas
	$: diasLicencia = calcularDiasLicencia(formLicencia.fecha_desde, formLicencia.fecha_hasta);
	
	$: tiposFiltrados = tipos.filter(t => {
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
			<h1>Gestión de Licencias</h1>
		</div>
		<div class="toggle-buttons">
			<button 
				class="btn-toggle {vistaActual === 'licencias' ? 'active' : ''}"
				on:click={() => cambiarVista('licencias')}
			>
				📋 Gestión de Licencias
			</button>
			<button 
				class="btn-toggle {vistaActual === 'tipos' ? 'active' : ''}"
				on:click={() => cambiarVista('tipos')}
			>
				⚙️ Tipos de Licencia
			</button>
		</div>
		
		{#if vistaActual === 'licencias'}
			<div class="header-actions">
				<button class="btn-primary" on:click={abrirModalCrear}>
					➕ Solicitar Licencia
				</button>
				<button class="btn-secondary" on:click={abrirModalAsignar}>
					📝 Asignar Licencia
				</button>
				<button class="btn-refresh" on:click={() => cargarLicencias()}>
					🔄 Actualizar
				</button>
			</div>
		{:else}
			<div class="header-actions">
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
			</div>
		{/if}
	</div>

	<!-- Contenido principal con vista condicional -->
	<div class="page-content">
		{#if vistaActual === 'licencias'}
			<!-- Estadísticas -->
			{#if $estadisticas.total > 0}
				<div class="stats-container">
					<div class="stat-card">
						<div class="stat-number">{$estadisticas.total}</div>
						<div class="stat-label">Total</div>
					</div>
					<div class="stat-card pending">
						<div class="stat-number">{$estadisticas.pendientes}</div>
						<div class="stat-label">Pendientes</div>
					</div>
					<div class="stat-card approved">
						<div class="stat-number">{$estadisticas.aprobadas}</div>
						<div class="stat-label">Aprobadas</div>
					</div>
					<div class="stat-card rejected">
						<div class="stat-number">{$estadisticas.rechazadas}</div>
						<div class="stat-label">Rechazadas</div>
					</div>
				</div>
			{/if}

			<!-- Filtros -->
			<div class="filtros-container">
				<div class="filtros-row">
					<div class="filtro-group">
						<label for="fecha_desde">Desde</label>
						<input type="date" id="fecha_desde" bind:value={$filtros.fecha_desde} on:change={aplicarFiltros} />
					</div>
					<div class="filtro-group">
						<label for="fecha_hasta">Hasta</label>
						<input type="date" id="fecha_hasta" bind:value={$filtros.fecha_hasta} on:change={aplicarFiltros} />
					</div>
					<div class="filtro-group">
						<label for="area_filter">Área</label>
						<select id="area_filter" bind:value={$filtros.area_id} on:change={aplicarFiltros}>
							<option value={null}>Todas las áreas</option>
							{#each areas as area}
								<option value={area.id_area}>{area.nombre}</option>
							{/each}
						</select>
					</div>
					<div class="filtro-group">
						<label for="estado_filter">Estado</label>
						<select id="estado_filter" bind:value={$filtros.estado} on:change={aplicarFiltros}>
							<option value="todas">Todos los estados</option>
							<option value="pendiente">Pendiente</option>
							<option value="aprobada">Aprobada</option>
							<option value="rechazada">Rechazada</option>
						</select>
					</div>
					<div class="filtro-group">
						<label for="tipo_filter">Tipo</label>
						<select id="tipo_filter" bind:value={$filtros.tipo_licencia_id} on:change={aplicarFiltros}>
							<option value={null}>Todos los tipos</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
							{/each}
						</select>
					</div>
					<div class="filtro-group">
						<button class="btn-clear" on:click={limpiarTodosFiltros}>Limpiar Filtros</button>
					</div>
				</div>
			</div>

			<!-- Tabla de licencias -->
			{#if $error}
				<div class="alert alert-error">
					<strong>❌ Error:</strong> {$error}
					<button class="btn-primary" on:click={() => cargarLicencias()}>Reintentar</button>
				</div>
			{/if}

			{#if $loading}
				<div class="loading-state">
					<div class="spinner-large"></div>
					<p>Cargando licencias...</p>
				</div>
			{:else if $licenciasFiltradas.length === 0}
				<div class="no-data">
					{#if Object.values($filtros).some(v => v)}
						<p>No hay licencias que coincidan con los filtros aplicados.</p>
						<button class="btn-secondary" on:click={limpiarTodosFiltros}>Limpiar Filtros</button>
					{:else}
						<p>No hay licencias registradas.</p>
					{/if}
				</div>
			{:else}
				<div class="table-container">
					<table class="table">
						<thead>
							<tr>
								<th>Agente</th>
								<th>Área</th>
								<th>Tipo</th>
								<th>Período</th>
								<th>Días</th>
								<th>Estado</th>
								<th>Fecha Solicitud</th>
								<th>Acciones</th>
							</tr>
						</thead>
						<tbody>
							{#each $licenciasFiltradas as licencia (licencia.id_licencia)}
								<tr>
									<td>
										<div class="agente-info">
											<strong>{licencia.agente?.nombre} {licencia.agente?.apellido}</strong>
											<small>{licencia.agente?.numero_agente}</small>
										</div>
									</td>
									<td>{licencia.agente?.area?.nombre || 'N/A'}</td>
									<td>
										<span class="tipo-badge">{licencia.tipo_licencia?.nombre}</span>
									</td>
									<td>
										{formatearFecha(licencia.fecha_desde)} - {formatearFecha(licencia.fecha_hasta)}
									</td>
									<td class="text-center">{licencia.dias_solicitados}</td>
									<td>
										<span class="estado-badge estado-{licencia.estado}">
											{obtenerIconoEstado(licencia.estado)} {licencia.estado}
										</span>
									</td>
									<td>{formatearFecha(licencia.fecha_creacion)}</td>
									<td>
										<div class="acciones">
											{#if puedeAprobar(licencia)}
												<button 
													class="btn-sm btn-success"
													on:click={() => abrirModalAprobar(licencia)}
													title="Aprobar"
												>
													✅
												</button>
												<button 
													class="btn-sm btn-danger"
													on:click={() => abrirModalRechazar(licencia)}
													title="Rechazar"
												>
													❌
												</button>
											{/if}
										</div>
									</td>
								</tr>
								{#if licencia.observaciones}
									<tr class="observaciones-row">
										<td colspan="8">
											<small><strong>Observaciones:</strong> {licencia.observaciones}</small>
										</td>
									</tr>
								{/if}
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		{:else}
			<!-- Vista de Tipos de Licencia -->
			{#if errorTipos}
				<div class="alert alert-error">
					<strong>❌ Error:</strong>
					{errorTipos}
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
			</div>

			{#if loadingTipos}
				<div class="loading-container">
					<div class="spinner-large"></div>
					<p>Cargando tipos de licencia...</p>
				</div>
			{:else if tiposFiltrados.length === 0 && !loadingTipos}
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
							{#each tiposFiltrados as tipo (tipo.id_tipo_licencia || tipo.id)}
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
		{/if}
	</div>
</div>

<!-- Modales para gestión de licencias -->

<!-- Modal de Crear Licencia -->
{#if showModalCrear}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Nueva Solicitud de Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModales}>&times;</button>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleCrearLicencia}>
					<div class="form-group">
						<label for="tipo_licencia">Tipo de Licencia *</label>
						<select id="tipo_licencia" bind:value={formLicencia.id_tipo_licencia} required>
							<option value="">Seleccione un tipo...</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
							{/each}
						</select>
					</div>
					<div class="form-group">
						<label for="fecha_desde">Fecha de Inicio *</label>
						<input type="date" id="fecha_desde" bind:value={formLicencia.fecha_desde} required />
					</div>
					<div class="form-group">
						<label for="fecha_hasta">Fecha de Fin *</label>
						<input type="date" id="fecha_hasta" bind:value={formLicencia.fecha_hasta} required />
					</div>
					{#if diasLicencia > 0}
						<div class="info-dias">
							<small>📅 Días solicitados: <strong>{diasLicencia}</strong></small>
						</div>
					{/if}
					<div class="form-group">
						<label for="observaciones">Observaciones</label>
						<textarea id="observaciones" bind:value={formLicencia.observaciones} rows="3" placeholder="Motivo o comentarios adicionales..."></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={cerrarModales}>Cancelar</button>
						<button type="submit" class="btn btn-primary" disabled={saving}>
							{saving ? 'Creando...' : 'Crear Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Asignar Licencia -->
{#if showModalAsignar}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Asignar Nueva Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModales}>&times;</button>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleAsignarLicencia}>
					<div class="form-group">
						<label for="area_asignar">Área *</label>
						<select id="area_asignar" bind:value={areaSeleccionada} on:change={() => cargarAgentesPorArea(areaSeleccionada)} required>
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
								<div class="loading-small">Cargando agentes...</div>
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
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
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
					{#if diasLicencia > 0}
						<div class="info-dias">
							<small>📅 Días a asignar: <strong>{diasLicencia}</strong></small>
						</div>
					{/if}
					<div class="form-group">
						<label for="observaciones_asignar">Observaciones</label>
						<textarea id="observaciones_asignar" bind:value={formLicencia.observaciones} rows="3" placeholder="Motivo o comentarios adicionales..."></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={cerrarModales}>Cancelar</button>
						<button type="submit" class="btn btn-primary" disabled={saving || !areaSeleccionada}>
							{saving ? 'Asignando...' : 'Asignar Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Aprobar Licencia -->
{#if showModalAprobar}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Aprobar Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModales}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<p><strong>Agente:</strong> {licenciaSeleccionada?.agente?.nombre} {licenciaSeleccionada?.agente?.apellido}</p>
					<p><strong>Área:</strong> {licenciaSeleccionada?.agente?.area?.nombre}</p>
					<p><strong>Tipo:</strong> {licenciaSeleccionada?.tipo_licencia?.nombre}</p>
					<p><strong>Período:</strong> {formatearFecha(licenciaSeleccionada?.fecha_desde)} al {formatearFecha(licenciaSeleccionada?.fecha_hasta)}</p>
					<p><strong>Días:</strong> {licenciaSeleccionada?.dias_solicitados}</p>
					{#if licenciaSeleccionada?.observaciones}
						<p><strong>Observaciones:</strong> {licenciaSeleccionada.observaciones}</p>
					{/if}
				</div>
				<form on:submit|preventDefault={handleAprobarLicencia}>
					<div class="form-group">
						<label for="observaciones_aprobacion">Observaciones de Aprobación</label>
						<textarea id="observaciones_aprobacion" bind:value={formAprobacion.observaciones} rows="3" placeholder="Comentarios adicionales (opcional)"></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={cerrarModales}>Cancelar</button>
						<button type="submit" class="btn btn-success" disabled={saving}>
							{saving ? 'Aprobando...' : 'Aprobar Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Rechazar Licencia -->
{#if showModalRechazar}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Rechazar Licencia</h5>
				<button type="button" class="btn-close" on:click={cerrarModales}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<p><strong>Agente:</strong> {licenciaSeleccionada?.agente?.nombre} {licenciaSeleccionada?.agente?.apellido}</p>
					<p><strong>Área:</strong> {licenciaSeleccionada?.agente?.area?.nombre}</p>
					<p><strong>Tipo:</strong> {licenciaSeleccionada?.tipo_licencia?.nombre}</p>
					<p><strong>Período:</strong> {formatearFecha(licenciaSeleccionada?.fecha_desde)} al {formatearFecha(licenciaSeleccionada?.fecha_hasta)}</p>
					<p><strong>Días:</strong> {licenciaSeleccionada?.dias_solicitados}</p>
					{#if licenciaSeleccionada?.observaciones}
						<p><strong>Observaciones:</strong> {licenciaSeleccionada.observaciones}</p>
					{/if}
				</div>
				<form on:submit|preventDefault={handleRechazarLicencia}>
					<div class="form-group">
						<label for="motivo_rechazo">Motivo del Rechazo *</label>
						<textarea id="motivo_rechazo" bind:value={formRechazo.motivo} rows="3" placeholder="Indique el motivo del rechazo..." required></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={cerrarModales}>Cancelar</button>
						<button type="submit" class="btn btn-danger" disabled={saving || !formRechazo.motivo.trim()}>
							{saving ? 'Rechazando...' : 'Rechazar Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal para gestión de tipos de licencia -->
{#if showForm}
	<div class="modal-overlay">
		<div class="modal">
			<h3>{isEditing ? 'Editar tipo de licencia' : 'Nuevo tipo de licencia'}</h3>
			{#if errorTipos}
				<div class="alert alert-error">{errorTipos}</div>
			{/if}
			<div class="form-row">
				<label>Código / Nombre *</label>
				<input bind:value={form.codigo} placeholder="Ej: VAC, ENF, etc." required />
			</div>
			<div class="form-row">
				<label>Descripción</label>
				<textarea rows="3" bind:value={form.descripcion} placeholder="Descripción del tipo de licencia"></textarea>
			</div>
			<div class="form-actions">
				<button class="btn-primary" on:click={guardar} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
				<button class="btn-limpiar" on:click={() => (showForm = false)} disabled={saving}>Cancelar</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Estilos del contenedor principal */
	.page-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
		background: #f8fafc;
		min-height: 100vh;
	}

	/* Header */
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e2e8f0;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.header-title h1 {
		margin: 0;
		font-size: 2rem;
		color: #1a202c;
		font-weight: 700;
	}

	.toggle-buttons {
		display: flex;
		gap: 0.5rem;
	}

	.btn-toggle {
		padding: 0.75rem 1.5rem;
		border: 2px solid #e2e8f0;
		background: white;
		color: #4a5568;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 500;
		transition: all 0.2s;
	}

	.btn-toggle.active {
		background: #4c51bf;
		color: white;
		border-color: #4c51bf;
	}

	.btn-toggle:hover:not(.active) {
		background: #f7fafc;
		border-color: #cbd5e0;
	}

	.header-actions {
		display: flex;
		gap: 0.75rem;
	}

	/* Botones */
	.btn-primary, .btn-secondary, .btn-refresh, .btn-header {
		padding: 0.75rem 1.25rem;
		border: none;
		border-radius: 8px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.btn-primary {
		background: #4c51bf;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: #434190;
	}

	.btn-secondary {
		background: #718096;
		color: white;
	}

	.btn-secondary:hover {
		background: #4a5568;
	}

	.btn-refresh, .btn-header {
		background: #ed8936;
		color: white;
	}

	.btn-refresh:hover, .btn-header:hover:not(:disabled) {
		background: #dd6b20;
	}

	.btn-clear {
		padding: 0.5rem 1rem;
		background: #e53e3e;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
	}

	.btn-clear:hover {
		background: #c53030;
	}

	.btn-limpiar {
		background: #6c757d;
		color: white;
		border: none;
		padding: 8px 12px;
		border-radius: 6px;
		cursor: pointer;
	}

	/* Estadísticas */
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.stat-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		text-align: center;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
		border: 1px solid #e2e8f0;
	}

	.stat-number {
		font-size: 2.5rem;
		font-weight: bold;
		color: #4c51bf;
	}

	.stat-card.pending .stat-number { color: #ed8936; }
	.stat-card.approved .stat-number { color: #38a169; }
	.stat-card.rejected .stat-number { color: #e53e3e; }

	.stat-label {
		font-size: 0.875rem;
		color: #718096;
		margin-top: 0.5rem;
		font-weight: 500;
	}

	/* Filtros */
	.filtros-container {
		background: white;
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 2rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.filtros-row {
		display: flex;
		gap: 1rem;
		align-items: end;
		flex-wrap: wrap;
	}

	.filtro-group {
		flex: 1;
		min-width: 150px;
	}

	.filtro-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #4a5568;
	}

	.filtro-group input,
	.filtro-group select {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.875rem;
		background: white;
	}

	.filtro-group input:focus,
	.filtro-group select:focus {
		outline: none;
		border-color: #4c51bf;
		box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
	}

	.input-busqueda {
		padding: 0.75rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.875rem;
		width: 100%;
	}

	.input-busqueda:focus {
		outline: none;
		border-color: #4c51bf;
		box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
	}

	/* Tabla */
	.table-container {
		overflow-x: auto;
		border-radius: 12px;
		background: white;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
		border: 1px solid #e2e8f0;
	}

	.table, .roles-table {
		width: 100%;
		border-collapse: collapse;
	}

	.table th, .roles-table th {
		background: #f7fafc;
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #2d3748;
		border-bottom: 2px solid #e2e8f0;
	}

	.table td, .roles-table td {
		padding: 1rem;
		border-bottom: 1px solid #f1f5f9;
		vertical-align: top;
	}

	.table tr:hover, .roles-table tr:hover {
		background: #f9fafb;
	}

	.agente-info strong {
		display: block;
		color: #2d3748;
	}

	.agente-info small {
		color: #718096;
	}

	.tipo-badge {
		background: #edf2f7;
		color: #4a5568;
		padding: 0.25rem 0.75rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.estado-badge {
		padding: 0.25rem 0.75rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 500;
		white-space: nowrap;
	}

	.estado-pendiente {
		background: #fef3c7;
		color: #92400e;
	}

	.estado-aprobada {
		background: #dcfce7;
		color: #166534;
	}

	.estado-rechazada {
		background: #fee2e2;
		color: #991b1b;
	}

	.acciones {
		display: flex;
		gap: 0.5rem;
	}

	.btn-sm {
		padding: 0.375rem 0.75rem;
		font-size: 0.75rem;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		transition: all 0.2s;
	}

	.btn-success {
		background: #38a169;
		color: white;
	}

	.btn-success:hover {
		background: #2f855a;
	}

	.btn-danger {
		background: #e53e3e;
		color: white;
	}

	.btn-danger:hover {
		background: #c53030;
	}

	.observaciones-row {
		background: #f7fafc;
	}

	.observaciones-row td {
		padding: 0.75rem 1rem;
		border-bottom: none;
	}

	/* Estados de carga y vacío */
	.loading-state, .loading-container {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}

	.loading-state .spinner-large, .loading-container .spinner-large {
		margin: 0 auto 1rem;
		width: 2rem;
		height: 2rem;
		border: 2px solid #e2e8f0;
		border-top: 2px solid #4c51bf;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.loading-small {
		text-align: center;
		color: #718096;
		font-style: italic;
		padding: 0.5rem;
	}

	.no-data, .empty-state {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}

	.no-data p, .empty-state p {
		margin-bottom: 1rem;
	}

	.empty-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
	}

	/* Alertas */
	.alert {
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.alert-error {
		background: #fed7d7;
		color: #742a2a;
		border: 1px solid #feb2b2;
	}

	/* Modales principales */
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.6);
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
	}

	.modal-contenido {
		background: white;
		border-radius: 12px;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
		max-width: 500px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal-header {
		padding: 1.5rem 1.5rem 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 1px solid #e2e8f0;
		margin-bottom: 1rem;
	}

	.modal-header h5 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #2d3748;
	}

	.btn-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		color: #718096;
		padding: 0.25rem;
		border-radius: 4px;
	}

	.btn-close:hover {
		background-color: #f7fafc;
		color: #4a5568;
	}

	.modal-body {
		padding: 0 1.5rem 1.5rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #4a5568;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.875rem;
		transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #4c51bf;
		box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
	}

	.form-group textarea {
		resize: vertical;
		min-height: 80px;
	}

	.info-dias {
		margin-bottom: 1rem;
		padding: 0.75rem;
		background: #f0fff4;
		border: 1px solid #c6f6d5;
		border-radius: 8px;
		text-align: center;
	}

	.licencia-info {
		background: #f7fafc;
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1rem;
		border: 1px solid #e2e8f0;
	}

	.licencia-info h6 {
		margin: 0 0 0.75rem 0;
		font-weight: 600;
		color: #2d3748;
		font-size: 1rem;
	}

	.licencia-info p {
		margin: 0.25rem 0;
		font-size: 0.875rem;
		color: #4a5568;
	}

	.licencia-info strong {
		color: #2d3748;
	}

	.modal-actions {
		display: flex;
		gap: 0.75rem;
		justify-content: flex-end;
		margin-top: 1.5rem;
		padding-top: 1rem;
		border-top: 1px solid #e2e8f0;
	}

	.btn {
		padding: 0.75rem 1.5rem;
		border-radius: 8px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease-in-out;
		border: none;
		font-size: 0.875rem;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/* Modal simple para tipos */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 2000;
	}

	.modal {
		background: white;
		padding: 1.25rem;
		border-radius: 10px;
		width: 520px;
		max-width: 92%;
		box-shadow: 0 10px 30px rgba(0,0,0,0.2);
	}

	.form-row {
		margin-bottom: 0.75rem;
		display: flex;
		flex-direction: column;
	}

	.form-row label {
		font-weight: 600;
		margin-bottom: 6px;
	}

	.form-row input, .form-row textarea {
		padding: 8px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
	}

	.form-actions {
		display: flex;
		gap: 8px;
		justify-content: flex-end;
		margin-top: 8px;
	}

	.modal h3 {
		margin-top: 0;
	}

	/* Spinner */
	.spinner {
		width: 1rem;
		height: 1rem;
		border: 2px solid #e2e8f0;
		border-top: 2px solid #4c51bf;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	/* Utilidades */
	.text-center {
		text-align: center;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.page-container {
			padding: 1rem;
		}

		.page-header {
			flex-direction: column;
			align-items: stretch;
		}

		.toggle-buttons,
		.header-actions {
			justify-content: center;
		}

		.filtros-row {
			flex-direction: column;
		}

		.filtro-group {
			min-width: auto;
		}

		.table-container {
			font-size: 0.875rem;
		}

		.modal-contenido {
			margin: 1rem;
			max-width: calc(100vw - 2rem);
		}
	}
</style>