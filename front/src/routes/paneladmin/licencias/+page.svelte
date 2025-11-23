<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { asistenciaService, personasService } from '$lib/services.js';
	import AuthService from '$lib/login/authService.js';
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
	
	// Variables para gestión de licencias de usuarios
	let userInfo = null;
	let areas = [];
	let agentes = [];
	
	// Modal states para licencias
	let mostrarModalCrear = false;
	let mostrarModalAprobar = false;
	let mostrarModalRechazar = false;
	let mostrarModalAsignar = false;
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

	// Variables para modales y datos de formularios
	let nuevaLicencia = {
		fecha_desde: '',
		fecha_hasta: '',
		tipo_licencia_id: '',
		observaciones: ''
	};

	let asignacionLicencia = {
		area_id: '',
		agente_id: '',
		tipo_licencia_id: '',
		fecha_desde: '',
		fecha_hasta: '',
		observaciones: ''
	};

	let aprobacion = {
		observaciones_aprobacion: ''
	};

	let rechazo = {
		motivo_rechazo: ''
	};

	// Loading states
	let cargandoCrear = false;
	let cargandoAsignar = false;
	let cargandoAprobacion = false;
	let cargandoRechazo = false;
	let agentesArea = [];
	
	// Variables para asignación de licencias
	let areaSeleccionada = null;
	let agentesDelArea = [];
	let cargandoAgentes = false;
	
	let formAprobacion = {
		observaciones: ''
	};
	
	let formRechazo = {
		motivo: ''
	};

	let saving = false;

	// Variables para gestión de tipos de licencia
	let tipos = [];
	let loadingTipos = false;
	let searchTerm = '';
	let errorTipos = null; // Error local para la gestión de tipos

	// Modal / form para tipos
	let showForm = false;
	let isEditing = false;
	let editingId = null;
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
				
				// Cargar datos iniciales
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
			
			// Cargar todas las áreas (solo administradores acceden a esta página)
			const areasResponse = await personasService.getAreas();
			if (areasResponse?.data?.success) {
				areas = areasResponse.data.data.results || [];
			}
			
			// Cargar todos los agentes
			await cargarAgentesArea();
			
			// Cargar todas las licencias sin filtros
			await cargarLicencias();
		} catch (err) {
			console.error('Error cargando datos iniciales:', err);
			error.set('Error al cargar datos iniciales');
		}
	}

	async function cargarAgentesArea() {
		try {
			const response = await personasService.getAgentes();
			if (response?.data) {
				agentes = response.data.results || [];
			}
		} catch (err) {
			console.error('Error cargando agentes:', err);
		}
	}

	async function cargarAgentesPorArea(areaId) {
		try {
			if (!areaId) {
				agentesDelArea = [];
				cargandoAgentes = false;
				return;
			}
			
			cargandoAgentes = true;
			const response = await personasService.getAgentesByArea(areaId);
			if (response?.data) {
				// La API devuelve estructura paginada: { count, results: [...] }
				agentesDelArea = response.data.results || [];
			} else {
				agentesDelArea = [];
			}
			
			// Reset agente seleccionado cuando cambia el área
			formLicencia.id_agente = null;
		} catch (err) {
			console.error('Error cargando agentes del área:', err);
			agentesDelArea = [];
		} finally {
			cargandoAgentes = false;
		}
	}

	function abrirModalCrear() {
		formLicencia = {
			id_agente: userInfo.id_agente, // Por defecto, el usuario actual
			id_tipo_licencia: null,
			fecha_desde: '',
			fecha_hasta: '',
			observaciones: '',
			justificacion: ''
		};
		showModalCrear = true;
	}

	function abrirModalAsignar() {
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: '',
			fecha_hasta: '',
			observaciones: '',
			justificacion: 'Asignada por administrador'
		};
		areaSeleccionada = null;
		agentesDelArea = [];
		cargandoAgentes = false;
		mostrarModalAsignar = true;
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
		showModalAprobar = false;
		showModalRechazar = false;
		mostrarModalAsignar = false;
		licenciaSeleccionada = null;
		saving = false;
	}

	async function handleCrearLicencia() {
		if (!nuevaLicencia.tipo_licencia_id || !nuevaLicencia.fecha_desde || !nuevaLicencia.fecha_hasta) {
			alert('Por favor complete todos los campos obligatorios');
			return;
		}

		if (new Date(nuevaLicencia.fecha_desde) > new Date(nuevaLicencia.fecha_hasta)) {
			alert('La fecha de inicio no puede ser posterior a la fecha de fin');
			return;
		}

		try {
			cargandoCrear = true;
			const resultado = await crearLicencia({
				id_tipo_licencia: nuevaLicencia.tipo_licencia_id,
				fecha_desde: nuevaLicencia.fecha_desde,
				fecha_hasta: nuevaLicencia.fecha_hasta,
				observaciones: nuevaLicencia.observaciones || '',
				estado: 'pendiente'
			});

			if (resultado.success) {
				mostrarModalCrear = false;
				await cargarLicencias();
				alert('Licencia solicitada correctamente. Aguarde aprobación.');
			} else {
				alert(resultado.error || 'Error al crear la licencia');
			}
		} catch (err) {
			console.error('Error creando licencia:', err);
			alert('Error al crear la licencia');
		} finally {
			cargandoCrear = false;
		}
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

	async function handleAsignarLicencia() {
		if (!asignacionLicencia.area_id || !asignacionLicencia.agente_id || !asignacionLicencia.tipo_licencia_id ||
			!asignacionLicencia.fecha_desde || !asignacionLicencia.fecha_hasta) {
			return;
		}

		try {
			cargandoAsignar = true;
			const response = await asignarLicencia(asignacionLicencia);
			if (response.success) {
				mostrarModalAsignar = false;
				await cargarLicencias();
				alert('Licencia asignada exitosamente');
			} else {
				alert(response.error || 'Error al asignar la licencia');
			}
		} catch (err) {
			console.error('Error asignando licencia:', err);
			alert('Error al asignar la licencia');
		} finally {
			cargandoAsignar = false;
		}
	}

	async function confirmarAprobacion() {
		if (!licenciaSeleccionada) return;

		try {
			cargandoAprobacion = true;
			const response = await aprobarLicencia(
				licenciaSeleccionada.id_licencia,
				aprobacion.observaciones_aprobacion
			);
			
			if (response.success) {
				mostrarModalAprobar = false;
				await cargarLicencias();
				alert('Licencia aprobada exitosamente');
			} else {
				alert(response.error || 'Error al aprobar la licencia');
			}
		} catch (err) {
			console.error('Error aprobando licencia:', err);
			alert('Error al aprobar la licencia');
		} finally {
			cargandoAprobacion = false;
		}
	}

	async function confirmarRechazo() {
		if (!licenciaSeleccionada || !rechazo.motivo_rechazo.trim()) return;

		try {
			cargandoRechazo = true;
			const response = await rechazarLicencia(
				licenciaSeleccionada.id_licencia,
				rechazo.motivo_rechazo
			);
			
			if (response.success) {
				mostrarModalRechazar = false;
				await cargarLicencias();
				alert('Licencia rechazada exitosamente');
			} else {
				alert(response.error || 'Error al rechazar la licencia');
			}
		} catch (err) {
			console.error('Error rechazando licencia:', err);
			alert('Error al rechazar la licencia');
		} finally {
			cargandoRechazo = false;
		}
	}

	// Funciones para filtros
	function aplicarFiltros() {
		// Los filtros se actualizan automáticamente por el binding con $filtros
		// Solo necesitamos recargar las licencias con los filtros actuales
		cargarLicencias($filtros);
	}

	function limpiarTodosFiltros() {
		limpiarFiltros();
		cargarLicencias();
	}

	// Funciones de utilidad
	function puedeAprobar(licencia) {
		// Como es administrador, siempre puede aprobar
		return true;
	}

	$: diasLicencia = calcularDiasLicencia(formLicencia.fecha_desde, formLicencia.fecha_hasta);

	async function cargarTipos() {
		loadingTipos = true;
		errorTipos = null;
		try {
			const resp = await asistenciaService.getTiposLicencia();
			if (resp?.data?.success) {
				tipos = resp.data.data || [];
			} else {
				tipos = [];
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

	// Funciones para cambiar vista
	function mostrarLicencias() {
		vistaActual = 'licencias';
	}

	function mostrarTipos() {
		vistaActual = 'tipos';
		if (tipos.length === 0) {
			cargarTipos();
		}
	}

	$: filtered = tipos.filter(t => {
		if (!searchTerm) return true;
		const s = searchTerm.toLowerCase();
		return (t.codigo || t.nombre || '').toLowerCase().includes(s) || (t.descripcion || '').toLowerCase().includes(s);
	});
</script>

<svelte:head>
	<title>Administración de Licencias - GIGA</title>
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
				<button class="btn-primary" on:click={abrirModalCrear}>
					➕ Solicitar Licencia
				</button>
				<button class="btn-secondary" on:click={abrirModalAsignar}>
					📝 Asignar Licencia
				</button>
				<button class="btn-refresh" on:click={() => cargarLicencias()}>
					🔄 Actualizar
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
	</div>	<!-- Contenido principal con vista condicional -->
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
						<label>Desde</label>
						<input type="date" bind:value={$filtros.fecha_desde} on:change={aplicarFiltros} />
					</div>
					<div class="filtro-group">
						<label>Hasta</label>
						<input type="date" bind:value={$filtros.fecha_hasta} on:change={aplicarFiltros} />
					</div>
					<div class="filtro-group">
						<label>Área</label>
						<select bind:value={$filtros.area_id} on:change={aplicarFiltros}>
							<option value={null}>Todas las áreas</option>
							{#each areas as area}
								<option value={area.id_area}>{area.nombre}</option>
							{/each}
						</select>
					</div>
					<div class="filtro-group">
						<label>Estado</label>
						<select bind:value={$filtros.estado} on:change={aplicarFiltros}>
							<option value="todas">Todos</option>
							<option value="pendiente">Pendientes</option>
							<option value="aprobada">Aprobadas</option>
							<option value="rechazada">Rechazadas</option>
						</select>
					</div>
					<div class="filtro-group">
						<label>Tipo</label>
						<select bind:value={$filtros.tipo_licencia_id} on:change={aplicarFiltros}>
							<option value={null}>Todos los tipos</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.codigo}</option>
							{/each}
						</select>
					</div>
					<div class="filtro-actions">
						<button class="btn-clear" on:click={limpiarTodosFiltros}>
							🗑️ Limpiar
						</button>
					</div>
				</div>
			</div>

			<!-- Contenido principal -->
			{#if $error}
				<div class="alert alert-error">
					<strong>❌ Error:</strong> {$error}
					<button class="btn-retry" on:click={() => cargarLicencias()}>Reintentar</button>
				</div>
			{/if}

			{#if $loading}
				<div class="loading-container">
					<div class="spinner-large"></div>
					<p>Cargando licencias...</p>
				</div>
			{:else if $licenciasFiltradas.length === 0}
				<div class="empty-state">
					<div class="empty-icon">📋</div>
					<h3>No se encontraron licencias</h3>
					<p>
						{#if Object.values($filtros).some(v => v)}
							No hay licencias que coincidan con los filtros aplicados.
						{:else}
							No hay licencias registradas aún.
						{/if}
					</p>
					<button class="btn-primary" on:click={abrirModalCrear}>
						➕ Solicitar Primera Licencia
					</button>
				</div>
			{:else}
				<div class="table-container">
					<table class="licencias-table">
						<thead>
							<tr>
								<th>Agente</th>
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
								<tr class="licencia-row" class:pending={licencia.estado === 'pendiente'}>
									<td>
										<div class="agente-info">
											<strong>{licencia.agente_nombre}</strong>
											<small>{licencia.area_nombre}</small>
										</div>
									</td>
									<td>
										<span class="tipo-badge">
											{licencia.tipo_licencia_descripcion}
										</span>
									</td>
									<td>
										<div class="periodo">
											{formatearFecha(licencia.fecha_desde)} - {formatearFecha(licencia.fecha_hasta)}
										</div>
									</td>
									<td>
										<span class="dias-count">
											{calcularDiasLicencia(licencia.fecha_desde, licencia.fecha_hasta)} días
										</span>
									</td>
									<td>
										<span 
											class="estado-badge" 
											style="background-color: {obtenerColorEstado(licencia.estado)}20; color: {obtenerColorEstado(licencia.estado)}; border: 1px solid {obtenerColorEstado(licencia.estado)}40"
										>
											{obtenerIconoEstado(licencia.estado)} {licencia.estado.toUpperCase()}
										</span>
									</td>
									<td>
										{formatearFecha(licencia.creado_en)}
									</td>
									<td>
										<div class="acciones">
											{#if licencia.estado === 'pendiente' && puedeAprobar(licencia)}
												<button 
													class="btn-small btn-success" 
													on:click={() => abrirModalAprobar(licencia)}
													title="Aprobar licencia"
												>
													✅ Aprobar
												</button>
												<button 
													class="btn-small btn-danger" 
													on:click={() => abrirModalRechazar(licencia)}
													title="Rechazar licencia"
												>
													❌ Rechazar
												</button>
											{/if}
											{#if licencia.observaciones}
												<button 
													class="btn-small btn-info" 
													title="Observaciones: {licencia.observaciones}"
												>
													💬 Info
												</button>
											{/if}
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
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
		
		{#if vistaActual === 'tipos'}
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
			
			<!-- Nota informativa sobre la funcionalidad -->
			<div style="margin-top: 1rem; padding: 1rem; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px;">
				<p style="margin: 0; color: #1565c0; font-size: 0.9rem;">
					<strong>📋 Gestión de Licencias:</strong> Esta sección administra los tipos de licencia del sistema. 
					Para gestionar licencias de usuarios (asignar, aprobar, rechazar), utiliza el botón 
					<strong>"👥 Ver Licencias de Usuarios"</strong> arriba.
				</p>
			</div>
		</div>

		{#if loadingTipos}
			<div class="loading-container">
				<div class="spinner-large"></div>
				<p>Cargando información...</p>
			</div>
		{:else if filtered.length === 0 && !loadingTipos}
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
					{#if errorTipos}
						<div class="alert alert-error">{errorTipos}</div>
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

<!-- Modal de Crear Licencia -->
{#if mostrarModalCrear}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Nueva Solicitud de Licencia</h5>
				<button type="button" class="btn-close" on:click={() => mostrarModalCrear = false}>&times;</button>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleCrearLicencia}>
					<div class="form-group">
						<label for="fecha_desde">Fecha de Inicio:</label>
						<input type="date" id="fecha_desde" bind:value={nuevaLicencia.fecha_desde} required />
					</div>
					<div class="form-group">
						<label for="fecha_hasta">Fecha de Fin:</label>
						<input type="date" id="fecha_hasta" bind:value={nuevaLicencia.fecha_hasta} required />
					</div>
					<div class="form-group">
						<label for="tipo_licencia">Tipo de Licencia:</label>
						<select id="tipo_licencia" bind:value={nuevaLicencia.tipo_licencia_id} required>
							<option value="">Seleccione un tipo...</option>
							{#each tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
							{/each}
						</select>
					</div>
					<div class="form-group">
						<label for="observaciones">Observaciones:</label>
						<textarea id="observaciones" bind:value={nuevaLicencia.observaciones} rows="3"></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={() => mostrarModalCrear = false}>Cancelar</button>
						<button type="submit" class="btn btn-primary" disabled={cargandoCrear}>
							{cargandoCrear ? 'Creando...' : 'Crear Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Asignar Licencia -->
{#if mostrarModalAsignar}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Asignar Nueva Licencia</h5>
				<button type="button" class="btn-close" on:click={() => mostrarModalAsignar = false}>&times;</button>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleAsignarLicencia}>
					<div class="form-group">
						<label for="area_asignar">Área:</label>
						<select id="area_asignar" bind:value={asignacionLicencia.area_id} on:change={cargarAgentesPorArea} required>
							<option value="">Seleccione un área...</option>
							{#each areas as area}
								<option value={area.id_area}>{area.nombre}</option>
							{/each}
						</select>
					</div>
					{#if asignacionLicencia.area_id}
						<div class="form-group">
							<label for="agente_asignar">Agente:</label>
							<select id="agente_asignar" bind:value={asignacionLicencia.agente_id} required>
								<option value="">Seleccione un agente...</option>
								{#each agentesArea as agente}
									<option value={agente.id_agente}>{agente.nombre} {agente.apellido}</option>
								{/each}
							</select>
						</div>
					{/if}
					<div class="form-group">
						<label for="tipo_licencia_asignar">Tipo de Licencia:</label>
						<select id="tipo_licencia_asignar" bind:value={asignacionLicencia.tipo_licencia_id} required>
							<option value="">Seleccione un tipo...</option>
							{#each tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.nombre}</option>
							{/each}
						</select>
					</div>
					<div class="form-group">
						<label for="fecha_desde_asignar">Fecha de Inicio:</label>
						<input type="date" id="fecha_desde_asignar" bind:value={asignacionLicencia.fecha_desde} required />
					</div>
					<div class="form-group">
						<label for="fecha_hasta_asignar">Fecha de Fin:</label>
						<input type="date" id="fecha_hasta_asignar" bind:value={asignacionLicencia.fecha_hasta} required />
					</div>
					<div class="form-group">
						<label for="observaciones_asignar">Observaciones:</label>
						<textarea id="observaciones_asignar" bind:value={asignacionLicencia.observaciones} rows="3"></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={() => mostrarModalAsignar = false}>Cancelar</button>
						<button type="submit" class="btn btn-primary" disabled={cargandoAsignar || !asignacionLicencia.area_id}>
							{cargandoAsignar ? 'Asignando...' : 'Asignar Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Aprobar Licencia -->
{#if mostrarModalAprobar}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Aprobar Licencia</h5>
				<button type="button" class="btn-close" on:click={() => mostrarModalAprobar = false}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<p><strong>Agente:</strong> {licenciaSeleccionada?.agente?.nombre} {licenciaSeleccionada?.agente?.apellido}</p>
					<p><strong>Tipo:</strong> {licenciaSeleccionada?.tipo_licencia?.nombre}</p>
					<p><strong>Período:</strong> {licenciaSeleccionada?.fecha_desde} al {licenciaSeleccionada?.fecha_hasta}</p>
					<p><strong>Días:</strong> {licenciaSeleccionada?.dias_solicitados}</p>
					{#if licenciaSeleccionada?.observaciones}
						<p><strong>Observaciones:</strong> {licenciaSeleccionada.observaciones}</p>
					{/if}
				</div>
				<form on:submit|preventDefault={confirmarAprobacion}>
					<div class="form-group">
						<label for="observaciones_aprobacion">Observaciones de Aprobación:</label>
						<textarea id="observaciones_aprobacion" bind:value={aprobacion.observaciones_aprobacion} rows="3" placeholder="Comentarios adicionales (opcional)"></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={() => mostrarModalAprobar = false}>Cancelar</button>
						<button type="submit" class="btn btn-success" disabled={cargandoAprobacion}>
							{cargandoAprobacion ? 'Aprobando...' : 'Aprobar Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Rechazar Licencia -->
{#if mostrarModalRechazar}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>Rechazar Licencia</h5>
				<button type="button" class="btn-close" on:click={() => mostrarModalRechazar = false}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="licencia-info">
					<h6>Información de la Licencia</h6>
					<p><strong>Agente:</strong> {licenciaSeleccionada?.agente?.nombre} {licenciaSeleccionada?.agente?.apellido}</p>
					<p><strong>Tipo:</strong> {licenciaSeleccionada?.tipo_licencia?.nombre}</p>
					<p><strong>Período:</strong> {licenciaSeleccionada?.fecha_desde} al {licenciaSeleccionada?.fecha_hasta}</p>
					<p><strong>Días:</strong> {licenciaSeleccionada?.dias_solicitados}</p>
					{#if licenciaSeleccionada?.observaciones}
						<p><strong>Observaciones:</strong> {licenciaSeleccionada.observaciones}</p>
					{/if}
				</div>
				<form on:submit|preventDefault={confirmarRechazo}>
					<div class="form-group">
						<label for="motivo_rechazo">Motivo del Rechazo: *</label>
						<textarea id="motivo_rechazo" bind:value={rechazo.motivo_rechazo} rows="3" placeholder="Indique el motivo del rechazo..." required></textarea>
					</div>
					<div class="modal-actions">
						<button type="button" class="btn btn-secondary" on:click={() => mostrarModalRechazar = false}>Cancelar</button>
						<button type="submit" class="btn btn-danger" disabled={cargandoRechazo || !rechazo.motivo_rechazo.trim()}>
							{cargandoRechazo ? 'Rechazando...' : 'Rechazar Licencia'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

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

        /* Modal styles */
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
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }

        .modal-header h5 {
            margin: 0;
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }

        .btn-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6b7280;
            padding: 0.25rem;
            border-radius: 4px;
        }

        .btn-close:hover {
            background-color: #f3f4f6;
            color: #374151;
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
            color: #374151;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 0.875rem;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }

        .modal-actions {
            display: flex;
            gap: 0.75rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease-in-out;
            border: none;
            font-size: 0.875rem;
        }

        .btn-primary {
            background-color: #3b82f6;
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            background-color: #2563eb;
        }

        .btn-secondary {
            background-color: #6b7280;
            color: white;
        }

        .btn-secondary:hover {
            background-color: #4b5563;
        }

        .btn-success {
            background-color: #10b981;
            color: white;
        }

        .btn-success:hover:not(:disabled) {
            background-color: #059669;
        }

        .btn-danger {
            background-color: #ef4444;
            color: white;
        }

        .btn-danger:hover:not(:disabled) {
            background-color: #dc2626;
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .licencia-info {
            background-color: #f9fafb;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #e5e7eb;
        }

        .licencia-info h6 {
            margin: 0 0 0.75rem 0;
            font-weight: 600;
            color: #374151;
            font-size: 1rem;
        }

        .licencia-info p {
            margin: 0.25rem 0;
            font-size: 0.875rem;
            color: #4b5563;
        }

        .licencia-info strong {
            color: #111827;
        }
</style>