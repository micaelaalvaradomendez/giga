<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import AuthService from '$lib/login/authService.js';
	import { asistenciaService, personasService } from '$lib/services.js';
	import {
		licencias, tiposLicencia, filtros, loading, error, usuario,
		licenciasFiltradas, estadisticas,
		cargarLicencias, cargarTiposLicencia, crearLicencia,
		aprobarLicencia, rechazarLicencia, actualizarFiltros, limpiarFiltros,
		obtenerPermisos, puedeAprobarLicencia, puedeAsignarAAgente, puedeVerLicenciaDeRol, 
		formatearFecha, calcularDiasLicencia, obtenerColorEstado, obtenerIconoEstado
	} from '$lib/paneladmin/controllers/licenciasController.js';

	let userInfo = null;
	let permisos = {};
	let areas = [];
	let agentes = [];
	
	// Modal states
	let showModalCrear = false;
	let showModalAprobar = false;
	let showModalRechazar = false;
	let showModalAsignar = false;
	let licenciaSeleccionada = null;
	
	// Form data
	let formLicencia = {
		id_agente: null,
		id_tipo_licencia: null,
		fecha_desde: '',
		fecha_hasta: '',
		observaciones: '',
		justificacion: ''
	};
	
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
				
				// Obtener el rol del usuario correctamente
				const rol = userInfo.roles?.[0]?.nombre || userInfo.rol_nombre || 'Agente';
				console.log('🔐 Usuario actual:', userInfo.nombre, userInfo.apellido, '| Rol:', rol, '| Área:', userInfo.area?.nombre);
				
				permisos = obtenerPermisos(rol, userInfo.id_area);
				console.log('🔑 Permisos calculados:', permisos);
				
				// Cargar datos iniciales
				await cargarDatosIniciales();
			} else {
				console.error('❌ No se pudo obtener información del usuario');
				goto('/');
			}
		} catch (err) {
			console.error('❌ Error inicializando:', err);
			goto('/');
		}
	}

	async function cargarDatosIniciales() {
		try {
			// Cargar tipos de licencia
			await cargarTiposLicencia();
			
			// Cargar áreas según permisos
			if (permisos.puedeVerTodasAreas) {
				// Administrador puede ver todas las áreas
				const areasResponse = await personasService.getAreas();
				if (areasResponse?.data?.success) {
					areas = areasResponse.data.data.results || [];
				}
			} else if (permisos.soloSuArea || permisos.puedeAsignar) {
				// Director, Jefatura, Agente Avanzado solo ven su área
				const areasResponse = await personasService.getAreas();
				if (areasResponse?.data?.success) {
					const todasAreas = areasResponse.data.data.results || [];
					areas = todasAreas.filter(a => a.id_area === userInfo.id_area);
				}
			}

			// Cargar agentes de su área si puede asignar licencias
			if (permisos.puedeAsignar) {
				await cargarAgentesArea();
			}
			
			// Cargar licencias con filtros según permisos
			const parametros = {};
			if (permisos.soloSuArea && !permisos.puedeVerTodasAreas) {
				// Filtrar por área para roles que no son administrador
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
				let agentesCompletos = response.data.data || [];
				
				// Filtrar agentes según el rol del usuario (especialmente para Agente Avanzado)
				if (permisos.puedeAsignarSoloAgentes) {
					// Agente Avanzado solo puede ver/asignar a agentes simples
					agentes = agentesCompletos.filter(agente => 
						(agente.rol?.nombre || agente.rol_nombre) === 'Agente'
					);
					console.log(`🔍 Agente Avanzado: filtrado ${agentes.length} agentes de ${agentesCompletos.length} totales`);
				} else {
					agentes = agentesCompletos;
				}
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
			justificacion: 'Asignada por jefatura'
		};
		areaSeleccionada = null;
		agentesDelArea = [];
		cargandoAgentes = false;
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
		showModalAprobar = false;
		showModalRechazar = false;
		showModalAsignar = false;
		licenciaSeleccionada = null;
		saving = false;
	}

	async function handleCrearLicencia() {
		if (!formLicencia.id_tipo_licencia || !formLicencia.fecha_desde || !formLicencia.fecha_hasta) {
			alert('Por favor complete todos los campos obligatorios');
			return;
		}

		if (new Date(formLicencia.fecha_desde) > new Date(formLicencia.fecha_hasta)) {
			alert('La fecha de inicio no puede ser posterior a la fecha de fin');
			return;
		}

		saving = true;
		const resultado = await crearLicencia({
			...formLicencia,
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

		const rol = userInfo?.roles?.[0]?.nombre || userInfo?.rol_nombre || 'Agente';
		saving = true;
		
		// Determinar el estado según el rol del usuario
		let estadoLicencia = 'pendiente';
		let aprobadaPor = null;
		
		if (rol === 'Director' || rol === 'Jefatura') {
			// Director y Jefatura aprueban automáticamente sus asignaciones
			estadoLicencia = 'aprobada';
			aprobadaPor = userInfo.id_agente;
		}
		// Agente Avanzado asigna pero la licencia queda pendiente de aprobación

		const resultado = await crearLicencia({
			...formLicencia,
			estado: estadoLicencia,
			aprobada_por: aprobadaPor
		});

		if (resultado.success) {
			cerrarModales();
			const mensaje = estadoLicencia === 'aprobada' 
				? 'Licencia asignada y aprobada correctamente.' 
				: 'Licencia asignada correctamente. Queda pendiente de aprobación.';
			alert(mensaje);
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
		const rol = userInfo?.roles?.[0]?.nombre || userInfo?.rol_nombre || 'Agente';
		return puedeAprobarLicencia(licencia, rol, userInfo?.id_area);
	}

	$: diasLicencia = calcularDiasLicencia(formLicencia.fecha_desde, formLicencia.fecha_hasta);
</script>

<svelte:head>
	<title>Gestión de Licencias - GIGA</title>
</svelte:head>

<div class="page-container">
	<div class="page-header">
		<div class="header-title">
			<h1>📋 Gestión de Licencias</h1>
			<p>Solicitar, aprobar y gestionar licencias del personal</p>
		</div>
		<div class="header-actions">
			{#if permisos.puedeCrear}
				<button class="btn-primary" on:click={abrirModalCrear}>
					➕ Solicitar Licencia
				</button>
			{/if}
			{#if permisos.puedeAsignar}
				<button class="btn-secondary" on:click={abrirModalAsignar}>
					📝 Asignar Licencia
				</button>
			{/if}
			<button class="btn-refresh" on:click={() => cargarLicencias()}>
				🔄 Actualizar
			</button>
		</div>
	</div>

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
			{#if (permisos.puedeVerTodasAreas || permisos.puedeAsignar) || (permisos.soloSuArea && areas.length > 1)}
				<div class="filtro-group">
					<label>Área</label>
					<select bind:value={$filtros.area_id} on:change={aplicarFiltros}>
						<option value={null}>{permisos.puedeVerTodasAreas || permisos.puedeAsignar ? 'Todas las áreas' : 'Mi área'}</option>
						{#each areas as area}
							<option value={area.id_area}>{area.nombre}</option>
						{/each}
					</select>
				</div>
			{/if}
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
	<div class="page-content">
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
				{#if permisos.puedeCrear}
					<button class="btn-primary" on:click={abrirModalCrear}>
						➕ Solicitar Primera Licencia
					</button>
				{/if}
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
	</div>
</div>

<!-- Modal Crear/Solicitar Licencia -->
{#if showModalCrear}
	<div class="modal-overlay">
		<div class="modal">
			<div class="modal-header">
				<h3>📋 Solicitar Licencia</h3>
				<button class="modal-close" on:click={cerrarModales}>✕</button>
			</div>
			<form on:submit|preventDefault={handleCrearLicencia}>
				<div class="modal-body">
					<div class="form-group">
						<label>Tipo de Licencia *</label>
						<select bind:value={formLicencia.id_tipo_licencia} required>
							<option value={null}>Seleccione un tipo...</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.codigo} - {tipo.descripcion}</option>
							{/each}
						</select>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label>Fecha Desde *</label>
							<input type="date" bind:value={formLicencia.fecha_desde} required />
						</div>
						<div class="form-group">
							<label>Fecha Hasta *</label>
							<input type="date" bind:value={formLicencia.fecha_hasta} required />
						</div>
					</div>

					{#if diasLicencia > 0}
						<div class="info-days">
							📅 Duración: <strong>{diasLicencia} días</strong>
						</div>
					{/if}

					<div class="form-group">
						<label>Justificación *</label>
						<textarea 
							bind:value={formLicencia.justificacion} 
							placeholder="Indique el motivo de la licencia..."
							rows="3"
							required
						></textarea>
					</div>

					<div class="form-group">
						<label>Observaciones adicionales</label>
						<textarea 
							bind:value={formLicencia.observaciones} 
							placeholder="Observaciones opcionales..."
							rows="2"
						></textarea>
					</div>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn-cancel" on:click={cerrarModales} disabled={saving}>
						Cancelar
					</button>
					<button type="submit" class="btn-primary" disabled={saving}>
						{saving ? 'Enviando...' : '📤 Enviar Solicitud'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Modal Asignar Licencia -->
{#if showModalAsignar}
	<div class="modal-overlay">
		<div class="modal">
			<div class="modal-header">
				<h3>📝 Asignar Licencia</h3>
				<button class="modal-close" on:click={cerrarModales}>✕</button>
			</div>
			<form on:submit|preventDefault={handleAsignarLicencia}>
				<div class="modal-body">
					<!-- Selección de Área -->
					<div class="form-group">
						<label>Área *</label>
						<select bind:value={areaSeleccionada} on:change={() => cargarAgentesPorArea(areaSeleccionada)} required>
							<option value={null}>Seleccione un área...</option>
							{#each areas as area}
								<option value={area.id_area}>{area.nombre}</option>
							{/each}
						</select>
					</div>

					<!-- Selección de Agente (solo se muestra si hay un área seleccionada) -->
					{#if areaSeleccionada}
						<div class="form-group">
							<label>Agente *</label>
							<select bind:value={formLicencia.id_agente} disabled={cargandoAgentes} required>
								<option value={null}>
									{cargandoAgentes ? 'Cargando agentes...' : 'Seleccione un agente...'}
								</option>
								{#each agentesDelArea as agente}
									<option value={agente.id_agente}>{agente.nombre} {agente.apellido} - {agente.legajo}</option>
								{/each}
							</select>
							{#if cargandoAgentes}
								<small style="color: #3b82f6; font-style: italic;">
									🔄 Cargando agentes del área seleccionada...
								</small>
							{:else if agentesDelArea.length === 0}
								<small style="color: #6b7280; font-style: italic;">
									No hay agentes disponibles en esta área
								</small>
							{:else}
								<small style="color: #10b981; font-style: italic;">
									{agentesDelArea.length} agente{agentesDelArea.length !== 1 ? 's' : ''} disponible{agentesDelArea.length !== 1 ? 's' : ''}
								</small>
							{/if}
						</div>
					{/if}

					<div class="form-group">
						<label>Tipo de Licencia *</label>
						<select bind:value={formLicencia.id_tipo_licencia} required>
							<option value={null}>Seleccione un tipo...</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}>{tipo.codigo} - {tipo.descripcion}</option>
							{/each}
						</select>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label>Fecha Desde *</label>
							<input type="date" bind:value={formLicencia.fecha_desde} required />
						</div>
						<div class="form-group">
							<label>Fecha Hasta *</label>
							<input type="date" bind:value={formLicencia.fecha_hasta} required />
						</div>
					</div>

					{#if diasLicencia > 0}
						<div class="info-days">
							📅 Duración: <strong>{diasLicencia} días</strong>
						</div>
					{/if}

					<div class="form-group">
						<label>Justificación *</label>
						<textarea 
							bind:value={formLicencia.justificacion} 
							placeholder="Motivo de asignación de la licencia..."
							rows="3"
							required
						></textarea>
					</div>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn-cancel" on:click={cerrarModales} disabled={saving}>
						Cancelar
					</button>
					<button type="submit" class="btn-success" disabled={saving}>
						{saving ? 'Asignando...' : '✅ Asignar Licencia'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Modal Aprobar Licencia -->
{#if showModalAprobar && licenciaSeleccionada}
	<div class="modal-overlay">
		<div class="modal">
			<div class="modal-header">
				<h3>✅ Aprobar Licencia</h3>
				<button class="modal-close" on:click={cerrarModales}>✕</button>
			</div>
			<div class="modal-body">
				<div class="licencia-details">
					<p><strong>Agente:</strong> {licenciaSeleccionada.agente_nombre}</p>
					<p><strong>Tipo:</strong> {licenciaSeleccionada.tipo_licencia_descripcion}</p>
					<p><strong>Período:</strong> {formatearFecha(licenciaSeleccionada.fecha_desde)} - {formatearFecha(licenciaSeleccionada.fecha_hasta)}</p>
					<p><strong>Días:</strong> {calcularDiasLicencia(licenciaSeleccionada.fecha_desde, licenciaSeleccionada.fecha_hasta)}</p>
					{#if licenciaSeleccionada.justificacion}
						<p><strong>Justificación:</strong> {licenciaSeleccionada.justificacion}</p>
					{/if}
				</div>

				<div class="form-group">
					<label>Observaciones de aprobación (opcional)</label>
					<textarea 
						bind:value={formAprobacion.observaciones} 
						placeholder="Observaciones sobre la aprobación..."
						rows="3"
					></textarea>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" on:click={cerrarModales} disabled={saving}>
					Cancelar
				</button>
				<button class="btn-success" on:click={handleAprobarLicencia} disabled={saving}>
					{saving ? 'Aprobando...' : '✅ Aprobar Licencia'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Modal Rechazar Licencia -->
{#if showModalRechazar && licenciaSeleccionada}
	<div class="modal-overlay">
		<div class="modal">
			<div class="modal-header">
				<h3>❌ Rechazar Licencia</h3>
				<button class="modal-close" on:click={cerrarModales}>✕</button>
			</div>
			<div class="modal-body">
				<div class="licencia-details">
					<p><strong>Agente:</strong> {licenciaSeleccionada.agente_nombre}</p>
					<p><strong>Tipo:</strong> {licenciaSeleccionada.tipo_licencia_descripcion}</p>
					<p><strong>Período:</strong> {formatearFecha(licenciaSeleccionada.fecha_desde)} - {formatearFecha(licenciaSeleccionada.fecha_hasta)}</p>
				</div>

				<div class="form-group">
					<label>Motivo del rechazo *</label>
					<textarea 
						bind:value={formRechazo.motivo} 
						placeholder="Indique el motivo por el cual se rechaza la licencia..."
						rows="4"
						required
					></textarea>
				</div>
			</div>
			<div class="modal-footer">
				<button class="btn-cancel" on:click={cerrarModales} disabled={saving}>
					Cancelar
				</button>
				<button class="btn-danger" on:click={handleRechazarLicencia} disabled={saving}>
					{saving ? 'Rechazando...' : '❌ Rechazar Licencia'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Layout principal */
	.page-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 1rem;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e5e7eb;
	}

	.header-title h1 {
		margin: 0;
		font-size: 1.8rem;
		color: #1f2937;
	}

	.header-title p {
		margin: 0.5rem 0 0 0;
		color: #6b7280;
		font-size: 0.9rem;
	}

	.header-actions {
		display: flex;
		gap: 0.75rem;
	}

	/* Estadísticas */
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.stat-card {
		background: white;
		padding: 1.5rem;
		border-radius: 10px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		text-align: center;
		border-left: 4px solid #3b82f6;
	}

	.stat-card.pending { border-left-color: #f59e0b; }
	.stat-card.approved { border-left-color: #10b981; }
	.stat-card.rejected { border-left-color: #ef4444; }

	.stat-number {
		font-size: 2rem;
		font-weight: bold;
		color: #1f2937;
	}

	.stat-label {
		color: #6b7280;
		font-size: 0.875rem;
		margin-top: 0.5rem;
	}

	/* Filtros */
	.filtros-container {
		background: white;
		padding: 1.5rem;
		border-radius: 10px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		margin-bottom: 1.5rem;
	}

	.filtros-row {
		display: flex;
		gap: 1rem;
		align-items: end;
		flex-wrap: wrap;
	}

	.filtro-group {
		display: flex;
		flex-direction: column;
		min-width: 150px;
	}

	.filtro-group label {
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: #374151;
		font-size: 0.875rem;
	}

	.filtro-group input,
	.filtro-group select {
		padding: 0.5rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.875rem;
	}

	.filtro-actions {
		display: flex;
		gap: 0.5rem;
	}

	/* Tabla */
	.table-container {
		background: white;
		border-radius: 10px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		overflow: hidden;
	}

	.licencias-table {
		width: 100%;
		border-collapse: collapse;
	}

	.licencias-table th {
		background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
		color: white;
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		font-size: 0.875rem;
	}

	.licencias-table td {
		padding: 1rem;
		border-bottom: 1px solid #f3f4f6;
	}

	.licencia-row:hover {
		background-color: #f9fafb;
	}

	.licencia-row.pending {
		background-color: #fef3c7;
	}

	.agente-info strong {
		display: block;
		color: #1f2937;
	}

	.agente-info small {
		color: #6b7280;
		font-size: 0.75rem;
	}

	.tipo-badge {
		background: #dbeafe;
		color: #1e40af;
		padding: 0.25rem 0.75rem;
		border-radius: 15px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.periodo {
		font-size: 0.875rem;
		color: #374151;
	}

	.dias-count {
		background: #e0f2fe;
		color: #0369a1;
		padding: 0.25rem 0.5rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 600;
	}

	.estado-badge {
		padding: 0.375rem 0.75rem;
		border-radius: 15px;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.acciones {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	/* Botones */
	.btn-primary,
	.btn-secondary,
	.btn-success,
	.btn-danger,
	.btn-refresh,
	.btn-clear,
	.btn-cancel,
	.btn-retry {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 6px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.875rem;
	}

	.btn-primary { background: #3b82f6; color: white; }
	.btn-primary:hover { background: #2563eb; }

	.btn-secondary { background: #6b7280; color: white; }
	.btn-secondary:hover { background: #4b5563; }

	.btn-success { background: #10b981; color: white; }
	.btn-success:hover { background: #059669; }

	.btn-danger { background: #ef4444; color: white; }
	.btn-danger:hover { background: #dc2626; }

	.btn-refresh { background: #8b5cf6; color: white; }
	.btn-refresh:hover { background: #7c3aed; }

	.btn-clear { background: #f59e0b; color: white; }
	.btn-clear:hover { background: #d97706; }

	.btn-cancel { background: #6b7280; color: white; }
	.btn-cancel:hover { background: #4b5563; }

	.btn-small {
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
	}

	.btn-info {
		background: #0ea5e9;
		color: white;
	}

	/* Modales */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 1rem;
	}

	.modal {
		background: white;
		border-radius: 12px;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
		width: 100%;
		max-width: 600px;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.modal-header h3 {
		margin: 0;
		color: #1f2937;
	}

	.modal-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		color: #6b7280;
		padding: 0.25rem;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.modal-footer {
		display: flex;
		gap: 0.75rem;
		justify-content: flex-end;
		padding: 1rem 1.5rem;
		border-top: 1px solid #e5e7eb;
		background: #f9fafb;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		font-weight: 600;
		margin-bottom: 0.5rem;
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
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.info-days {
		background: #dbeafe;
		color: #1e40af;
		padding: 0.75rem;
		border-radius: 6px;
		margin-bottom: 1rem;
		text-align: center;
	}

	.licencia-details {
		background: #f9fafb;
		padding: 1rem;
		border-radius: 6px;
		margin-bottom: 1rem;
	}

	.licencia-details p {
		margin: 0.5rem 0;
	}

	/* Estados vacíos y de carga */
	.loading-container {
		text-align: center;
		padding: 4rem 2rem;
		color: #6b7280;
	}

	.spinner-large {
		width: 3rem;
		height: 3rem;
		border: 3px solid #e5e7eb;
		border-top: 3px solid #3b82f6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
		color: #6b7280;
	}

	.empty-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.alert {
		padding: 1rem;
		border-radius: 6px;
		margin-bottom: 1rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.alert-error {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fca5a5;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	/* Responsive */
	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}

		.header-actions {
			flex-wrap: wrap;
		}

		.stats-container {
			grid-template-columns: repeat(2, 1fr);
		}

		.filtros-row {
			flex-direction: column;
		}

		.form-row {
			grid-template-columns: 1fr;
		}

		.table-container {
			overflow-x: auto;
		}

		.licencias-table {
			min-width: 800px;
		}
	}
</style>