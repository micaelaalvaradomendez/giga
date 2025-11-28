<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import AuthService from "$lib/login/authService.js";
	import { asistenciaService, personasService } from "$lib/services.js";
	import {
		licencias,
		tiposLicencia,
		filtros,
		loading,
		error,
		usuario,
		licenciasFiltradas,
		estadisticas,
		cargarLicencias,
		cargarTiposLicencia,
		crearLicencia,
		asignarLicencia,
		aprobarLicencia,
		rechazarLicencia,
		eliminarLicencia,
		actualizarFiltros,
		limpiarFiltros,
		obtenerPermisos,
		puedeAprobarLicencia,
		formatearFecha,
		calcularDiasLicencia,
		obtenerColorEstado,
		obtenerIconoEstado,
	} from "$lib/paneladmin/controllers/licenciasController.js";

	// Componentes modales
	import ModalSolicitar from "$lib/componentes/admin/licencias/ModalSolicitar.svelte";
	import ModalAsignar from "$lib/componentes/admin/licencias/ModalAsignar.svelte";
	import ModalAprobar from "$lib/componentes/admin/licencias/ModalAprobar.svelte";
	import ModalRechazar from "$lib/componentes/admin/licencias/ModalRechazar.svelte";

	// Estado principal - alternar entre gestión de licencias y tipos
	let vistaActual = "licencias"; // 'licencias' o 'tipos'

	// Variables principales para gestión de licencias
	let userInfo = null;
	let permisos = {};
	let areas = [];

	// Estados de modales - usando componentes
	let showModalSolicitar = false;
	let showModalCrear = false;
	let showModalAsignar = false;
	let showModalAprobar = false;
	let showModalRechazar = false;
	let licenciaSeleccionada = null;

	// Variables para asignación de licencias
	let areaSeleccionada = null;
	let agentesDelArea = [];
	let cargandoAgentes = false;

	// Form data para licencias
	let formLicencia = {
		id_agente: null,
		id_tipo_licencia: null,
		fecha_desde: "",
		fecha_hasta: "",
		observaciones: "",
		justificacion: "",
	};

	let saving = false;

	// Variables para gestión de tipos de licencia
	let tipos = [];
	let loadingTipos = false;
	let errorTipos = null;
	let searchTerm = "";

	// Modal / form para tipos
	let showForm = false;
	let isEditing = false;
	let editingId = null;
	let form = {
		codigo: "",
		descripcion: "",
	};

	// Modal de confirmación para tipos
	let showConfirmDelete = false;
	let tipoAEliminar = null;

	// Modal de confirmación para eliminar licencias
	let showConfirmDeleteLicencia = false;
	let licenciaAEliminar = null;
	let eliminandoLicencia = false;

	onMount(async () => {
		console.log("Iniciando página de licencias...");
		await inicializar();
	});

	async function inicializar() {
		console.log("Inicializando datos...");

		// Primero cargar datos básicos
		await cargarDatosIniciales();

		// Luego intentar autenticación
		try {
			const userResponse = await AuthService.getCurrentUserData();
			console.log("Respuesta de usuario:", userResponse);

			if (userResponse?.success && userResponse.data?.success) {
				userInfo = userResponse.data.data;
				usuario.set(userInfo);
				console.log("Usuario cargado:", userInfo);

				// Verificar si el usuario tiene rol de administrador
				const tieneRolAdmin =
					userInfo.roles &&
					userInfo.roles.length > 0 &&
					userInfo.roles.some(
						(rol) =>
							(typeof rol === "string" &&
								rol === "Administrador") ||
							(typeof rol === "object" &&
								rol.nombre === "Administrador"),
					);

				if (!tieneRolAdmin) {
					console.warn(
						"Usuario sin rol de administrador accediendo al panel. Roles:",
						userInfo.roles,
					);
				} else {
					console.log("✅ Usuario administrador verificado");
				}
			} else {
				console.warn(
					"No se pudo obtener información del usuario, continuando sin autenticación",
				);
			}
		} catch (err) {
			console.error("Error en autenticación, continuando:", err);
		}
	}

	async function cargarDatosIniciales() {
		console.log("🚀 Cargando datos iniciales...");

		// Cargar tipos de licencia para los selectores
		try {
			console.log("📋 Cargando tipos de licencia...");
			await cargarTiposLicencia();
		} catch (err) {
			console.error("❌ Error cargando tipos de licencia:", err);
		}

		// Cargar todas las áreas para filtros
		try {
			console.log("🏢 Cargando áreas...");
			const areasResponse = await personasService.getAreas();
			console.log("🏢 Respuesta de áreas:", areasResponse);
			if (
				areasResponse?.data?.success &&
				areasResponse?.data?.data?.results
			) {
				areas = areasResponse.data.data.results || [];
				console.log("✅ Áreas cargadas:", areas.length, areas);
			} else if (areasResponse?.data?.results) {
				areas = areasResponse.data.results || [];
				console.log(
					"✅ Áreas cargadas (formato alt):",
					areas.length,
					areas,
				);
			} else {
				console.warn(
					"⚠️ No se pudieron cargar las áreas:",
					areasResponse,
				);
				areas = [];
			}
		} catch (err) {
			console.error("❌ Error cargando áreas:", err);
			areas = [];
		}

		// Cargar licencias inicialmente
		try {
			console.log("Cargando licencias...");
			await cargarLicencias();
			console.log("Licencias cargadas");
		} catch (err) {
			console.error("Error cargando licencias:", err);
		}

		// Cargar tipos para gestión (vista de tipos)
		try {
			console.log("Cargando tipos para gestión...");
			await cargarTipos();
			console.log("Tipos para gestión cargados");
		} catch (err) {
			console.error("Error cargando tipos para gestión:", err);
		}

		console.log("Carga de datos iniciales completada");
	}

	// Funciones para carga de agentes por área
	async function cargarAgentesPorArea(areaId) {
		console.log("🔄 Cargando agentes para área:", areaId);
		if (!areaId) {
			agentesDelArea = [];
			return;
		}

		try {
			cargandoAgentes = true;
			const response = await personasService.getAgentesByArea(areaId);
			console.log("📋 Respuesta agentes por área:", response);
			if (response?.data?.success) {
				agentesDelArea = response.data.data || [];
				console.log("✅ Agentes cargados:", agentesDelArea.length);
			} else {
				console.error(
					"Error cargando agentes:",
					response?.data?.message,
				);
				agentesDelArea = [];
			}
		} catch (err) {
			console.error("Error cargando agentes del área:", err);
			agentesDelArea = [];
		} finally {
			cargandoAgentes = false;
		}
	}

	// Funciones para modales de licencias
	function abrirModalCrear() {
		console.log("🆕 Abriendo modal crear licencia");
		console.log("🧑 Usuario actual:", userInfo);
		console.log("📋 Tipos disponibles:", $tiposLicencia.length);
		licenciaSeleccionada = null;
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: "",
			fecha_hasta: "",
			observaciones: "",
			justificacion: "",
		};
		showModalCrear = true;
	}

	function abrirModalAsignar() {
		console.log("📝 Abriendo modal asignar licencia");
		console.log("🏢 Áreas disponibles:", areas.length);
		console.log("📋 Tipos disponibles:", $tiposLicencia.length);
		areaSeleccionada = null;
		agentesDelArea = [];
		formLicencia = {
			id_agente: null,
			id_tipo_licencia: null,
			fecha_desde: "",
			fecha_hasta: "",
			observaciones: "",
			justificacion: "",
		};
		showModalAsignar = true;
	}

	function abrirModalAprobar(licencia) {
		licenciaSeleccionada = licencia;
		showModalAprobar = true;
	}

	function abrirModalRechazar(licencia) {
		licenciaSeleccionada = licencia;
		showModalRechazar = true;
	}

	// Funciones para modal de eliminar licencia
	function abrirModalEliminarLicencia(licencia) {
		licenciaAEliminar = licencia;
		showConfirmDeleteLicencia = true;
	}

	function cancelarEliminacionLicencia() {
		showConfirmDeleteLicencia = false;
		licenciaAEliminar = null;
		eliminandoLicencia = false;
	}

	async function confirmarEliminacionLicencia() {
		if (!licenciaAEliminar) return;

		eliminandoLicencia = true;

		try {
			const resultado = await eliminarLicencia(
				licenciaAEliminar.id_licencia,
			);

			if (resultado.success) {
				mostrarAlerta("✅ Licencia eliminada correctamente", "success");
				// Recargar la lista de licencias
				await cargarLicencias();
			} else {
				mostrarAlerta(`❌ Error: ${resultado.error}`, "error");
			}
		} catch (err) {
			console.error("Error eliminando licencia:", err);
			mostrarAlerta("❌ Error al eliminar la licencia", "error");
		} finally {
			cancelarEliminacionLicencia();
		}
	}

	// Handlers para eventos de los componentes
	function handleAsignarEvent(event) {
		console.log("Asignar licencia event:", event.detail);
		showModalAsignar = false;
	}

	function handleAprobarEvent(event) {
		if (licenciaSeleccionada) {
			aprobarLicencia(
				licenciaSeleccionada.id_licencia,
				event.detail.observaciones,
			).then((resultado) => {
				if (resultado.success) {
					showModalAprobar = false;
					mostrarAlerta(
						"Licencia aprobada correctamente.",
						"success",
					);
				} else {
					mostrarAlerta(resultado.error, "error");
				}
			});
		}
	}

	function handleRechazarEvent(event) {
		if (licenciaSeleccionada) {
			rechazarLicencia(
				licenciaSeleccionada.id_licencia,
				event.detail.motivo,
			).then((resultado) => {
				if (resultado.success) {
					showModalRechazar = false;
					mostrarAlerta("Licencia rechazada.", "success");
				} else {
					mostrarAlerta(resultado.error, "error");
				}
			});
		}
	}

	function mostrarAlerta(mensaje, tipo = "info") {
		mostrarAlerta(mensaje);
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
		if (
			!formLicencia.id_tipo_licencia ||
			!formLicencia.fecha_desde ||
			!formLicencia.fecha_hasta
		) {
			mostrarAlerta(
				"Por favor complete todos los campos obligatorios",
				"error",
			);
			return;
		}

		if (
			new Date(formLicencia.fecha_desde) >
			new Date(formLicencia.fecha_hasta)
		) {
			mostrarAlerta(
				"La fecha de inicio no puede ser posterior a la fecha de fin",
				"error",
			);
			return;
		}

		// Verificar que tenemos el ID del agente (usuario actual)
		if (!userInfo?.id_agente) {
			mostrarAlerta(
				"No se puede crear la licencia: información de usuario no disponible",
				"error",
			);
			return;
		}

		saving = true;
		const resultado = await crearLicencia({
			...formLicencia,
			id_agente: userInfo.id_agente, // Usar el ID del usuario actual
			estado: "pendiente",
		});

		if (resultado.success) {
			cerrarModales();
			mostrarAlerta(
				"Licencia solicitada correctamente. Aguarde aprobación.",
				"success",
			);
		} else {
			mostrarAlerta(resultado.error, "error");
		}
		saving = false;
	}

	// Funciones para filtros
	function aplicarFiltros() {
		console.log("🔍 Aplicando filtros:", $filtros);
		console.log(
			"📊 Datos disponibles - Áreas:",
			areas.length,
			"Tipos:",
			$tiposLicencia.length,
		);
		cargarLicencias($filtros);
	}

	function limpiarTodosFiltros() {
		limpiarFiltros();
		cargarLicencias();
	}

	// Funciones de utilidad
	function puedeAprobar(licencia) {
		// Como es administrador, siempre puede aprobar
		return licencia.estado === "pendiente";
	}

	// Función para cambiar entre vistas
	function cambiarVista(vista) {
		vistaActual = vista;
		if (vista === "tipos") {
			cargarTipos();
		}
	}

	// Funciones para gestión de tipos de licencia
	async function cargarTipos() {
		loadingTipos = true;
		errorTipos = null;
		try {
			const resp = await asistenciaService.getTiposLicencia();
			if (resp?.data?.success) {
				tipos = resp.data.data || [];
			} else {
				tipos = [];
				errorTipos = resp?.data?.message || "Error al cargar tipos";
			}
		} catch (err) {
			console.error(err);
			errorTipos =
				err?.response?.data?.message ||
				err.message ||
				"Error cargando tipos";
		} finally {
			loadingTipos = false;
		}
	}

	function abrirAlta() {
		isEditing = false;
		editingId = null;
		form = { codigo: "", descripcion: "" };
		showForm = true;
	}

	function abrirEdicion(tipo) {
		isEditing = true;
		editingId = tipo.id_tipo_licencia || tipo.id || null;
		form = {
			codigo: tipo.codigo || tipo.nombre || "",
			descripcion: tipo.descripcion || "",
		};
		showForm = true;
	}

	async function guardar() {
		if (!form.codigo.trim()) {
			mostrarAlerta("El código es obligatorio", "error");
			return;
		}

		saving = true;
		errorTipos = null;
		try {
			if (isEditing && editingId) {
				const resp = await asistenciaService.updateTipoLicencia(
					editingId,
					form,
				);
				if (resp?.data?.success) {
					// actualizar en lista
					tipos = tipos.map((t) =>
						t.id_tipo_licencia === editingId || t.id === editingId
							? resp.data.data
							: t,
					);
					showForm = false;
				} else {
					errorTipos = resp?.data?.message || "Error al actualizar";
				}
			} else {
				const resp = await asistenciaService.createTipoLicencia(form);
				if (resp?.data?.success) {
					tipos = [resp.data.data, ...tipos];
					showForm = false;
				} else {
					errorTipos = resp?.data?.message || "Error al crear tipo";
				}
			}
		} catch (err) {
			console.error(err);
			errorTipos =
				err?.response?.data?.message ||
				err.message ||
				"Error guardando";
		} finally {
			saving = false;
		}
	}

	function eliminar(tipo) {
		tipoAEliminar = tipo;
		showConfirmDelete = true;
	}

	async function confirmarEliminacion() {
		const id = tipoAEliminar.id_tipo_licencia || tipoAEliminar.id || null;
		if (!id) return;

		try {
			await asistenciaService.deleteTipoLicencia(id);
			tipos = tipos.filter((t) => (t.id_tipo_licencia || t.id) !== id);
			showConfirmDelete = false;
			tipoAEliminar = null;
		} catch (err) {
			console.error(err);
			const msg =
				err?.response?.data?.message ||
				err.message ||
				"No se pudo eliminar. Puede que existan agentes vinculados.";
			mostrarAlerta(msg, "error");
		}
	}

	function cancelarEliminacion() {
		showConfirmDelete = false;
		tipoAEliminar = null;
	}

	// Variables reactivas
	$: diasLicencia = calcularDiasLicencia(
		formLicencia.fecha_desde,
		formLicencia.fecha_hasta,
	);

	$: tiposFiltrados = tipos.filter((t) => {
		if (!searchTerm) return true;
		const s = searchTerm.toLowerCase();
		return (
			(t.codigo || t.nombre || "").toLowerCase().includes(s) ||
			(t.descripcion || "").toLowerCase().includes(s)
		);
	});
</script>

<svelte:head>
	<title>Gestión de Licencias - GIGA</title>
</svelte:head>

<div class="page-container">
	<div class="page-header">
		<div class="header-title">
			<h1>Gestión de Licencias</h1>
		</div>
		{#if vistaActual === "licencias"}
			<div class="header-actions">
				<button
					class="btn-secondary"
					on:click={() => (showModalAsignar = true)}
				>
					📝 Asignar Licencia
				</button>
				<button class="btn-refresh" on:click={() => cargarLicencias()}>
					🔄 Actualizar
				</button>
			</div>
		{:else}
			<div class="header-actions">
				<button class="btn-nuevoTipo" on:click={abrirAlta}
					>➕ Nuevo Tipo</button
				>
				<button
					class="btn-refresh"
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
			</div>
		{/if}
	</div>

	<div class="toggle-buttons">
		<button
			class="btn-toggle {vistaActual === 'licencias' ? 'active' : ''}"
			on:click={() => cambiarVista("licencias")}
		>
			📋 Gestión de Licencias
		</button>
		<button
			class="btn-toggle {vistaActual === 'tipos' ? 'active' : ''}"
			on:click={() => cambiarVista("tipos")}
		>
			⚙️ Tipos de Licencia
		</button>
	</div>

	<!-- Contenido principal con vista condicional -->
	<div class="page-content">
		{#if vistaActual === "licencias"}
			<!-- Estadísticas -->
			{#if $estadisticas.total > 0}
				<div class="stats-container">
					<div class="stat-card">
						<div class="stat-number">{$estadisticas.total}</div>
						<div class="stat-label">Total</div>
					</div>
					<div class="stat-card pending">
						<div class="stat-number">
							{$estadisticas.pendientes}
						</div>
						<div class="stat-label">Pendientes</div>
					</div>
					<div class="stat-card approved">
						<div class="stat-number">{$estadisticas.aprobadas}</div>
						<div class="stat-label">Aprobadas</div>
					</div>
					<div class="stat-card rejected">
						<div class="stat-number">
							{$estadisticas.rechazadas}
						</div>
						<div class="stat-label">Rechazadas</div>
					</div>
				</div>
			{/if}

			<!-- Filtros -->
			<div class="filtros-container">
				<div class="filtros-row">
					<div class="filtro-group">
						<label for="fecha_desde">📆 Desde</label>
						<input
							type="date"
							id="fecha_desde"
							bind:value={$filtros.fecha_desde}
							on:change={aplicarFiltros}
						/>
					</div>
					<div class="filtro-group">
						<label for="fecha_hasta">📆 Hasta</label>
						<input
							type="date"
							id="fecha_hasta"
							bind:value={$filtros.fecha_hasta}
							on:change={aplicarFiltros}
						/>
					</div>
					<div class="filtro-group">
						<label for="area_filter"
							>🗂️ Área ({areas.length} áreas)</label
						>
						<select
							id="area_filter"
							bind:value={$filtros.area_id}
							on:change={aplicarFiltros}
						>
							<option value={null}>Todas las áreas</option>
							{#each areas as area}
								<option value={area.id_area}
									>{area.nombre}</option
								>
							{/each}
						</select>
					</div>
					<div class="filtro-group">
						<label for="estado_filter">✨ Estado</label>
						<select
							id="estado_filter"
							bind:value={$filtros.estado}
							on:change={aplicarFiltros}
						>
							<option value="todas">Todos los estados</option>
							<option value="pendiente">Pendiente</option>
							<option value="aprobada">Aprobada</option>
							<option value="rechazada">Rechazada</option>
						</select>
					</div>
					<div class="filtro-group">
						<label for="tipo_filter"
							>📝 Tipo ({$tiposLicencia.length} tipos)</label
						>
						<select
							id="tipo_filter"
							bind:value={$filtros.tipo_licencia_id}
							on:change={aplicarFiltros}
						>
							<option value={null}>Todos los tipos</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}
									>{tipo.nombre ||
										tipo.descripcion ||
										tipo.codigo ||
										`Tipo ${tipo.id_tipo_licencia}`}</option
								>
							{/each}
						</select>
					</div>
					<div class="filtro-group">
						<button class="btn-clear" on:click={limpiarTodosFiltros}
							>🗑️ Limpiar Filtros</button
						>
					</div>
				</div>
			</div>

			<!-- Tabla de licencias -->
			{#if $error}
				<div class="alert alert-error">
					<strong>❌ Error:</strong>
					{$error}
					<button
						class="btn-primary"
						on:click={() => cargarLicencias()}>Reintentar</button
					>
				</div>
			{/if}

			{#if $loading}
				<div class="loading-state">
					<div class="spinner-large"></div>
					<p>Cargando licencias...</p>
				</div>
			{:else if $licenciasFiltradas.length === 0}
				<div class="no-data">
					{#if Object.values($filtros).some((v) => v)}
						<p>
							No hay licencias que coincidan con los filtros
							aplicados.
						</p>
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
											<strong
												>{licencia.agente_nombre ||
													"SIN AGENTE"}</strong
											>
											<small
												>{licencia.area_nombre ||
													"N/A"}</small
											>
										</div>
									</td>
									<td>
										<span class="tipo-badge"
											>{licencia.tipo_licencia_descripcion ||
												"SIN TIPO"}</span
										>
									</td>
									<td>
										{formatearFecha(licencia.fecha_desde)} -
										{formatearFecha(licencia.fecha_hasta)}
									</td>
									<td class="text-center"
										>{licencia.dias_licencia}</td
									>
									<td>
										<span
											class="estado-badge estado-{licencia.estado}"
										>
											{obtenerIconoEstado(
												licencia.estado,
											)}
											{licencia.estado}
										</span>
									</td>
									<td>{formatearFecha(licencia.creado_en)}</td
									>
									<td>
										<div class="acciones">
											{#if puedeAprobar(licencia)}
												<button
													class="btn-sm btn-success"
													on:click={() =>
														abrirModalAprobar(
															licencia,
														)}
													title="Aprobar"
												>
													✅
												</button>
												<button
													class="btn-sm btn-danger"
													on:click={() =>
														abrirModalRechazar(
															licencia,
														)}
													title="Rechazar"
												>
													❌
												</button>
											{/if}
											<!-- Botón eliminar - siempre disponible para administradores -->
											<button
												class="btn-sm btn-warning"
												on:click={() =>
													abrirModalEliminarLicencia(
														licencia,
													)}
												title="Eliminar licencia"
												style="margin-left: 4px;"
											>
												🗑️
											</button>
										</div>
									</td>
								</tr>
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
					<button class="btn-primary" on:click={cargarTipos}
						>Reintentar</button
					>
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
						<button
							class="btn-clear"
							on:click={() => (searchTerm = "")}
							title="Limpiar filtros">🗑️ Limpiar</button
						>
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
										<strong
											>{tipo.codigo ||
												tipo.nombre ||
												"—"}</strong
										>
									</td>
									<td>{tipo.descripcion || "—"}</td>
									<td>
										<button
											class="btn-primary"
											on:click={() => abrirEdicion(tipo)}
											>✏️ Editar</button
										>
										<button
											class="btn-secondary"
											on:click={() => eliminar(tipo)}
											style="margin-left:6px"
											>🗑️ Eliminar</button
										>
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
				<button type="button" class="btn-close" on:click={cerrarModales}
					>&times;</button
				>
			</div>
			<div class="modal-body">
				<form on:submit|preventDefault={handleCrearLicencia}>
					<div class="form-group">
						<label for="tipo_licencia">Tipo de Licencia *</label>
						<select
							id="tipo_licencia"
							bind:value={formLicencia.id_tipo_licencia}
							required
						>
							<option value="">Seleccione un tipo...</option>
							{#each $tiposLicencia as tipo}
								<option value={tipo.id_tipo_licencia}
									>{tipo.nombre}</option
								>
							{/each}
						</select>
					</div>
					<div class="form-group">
						<label for="fecha_desde">Fecha de Inicio *</label>
						<input
							type="date"
							id="fecha_desde"
							bind:value={formLicencia.fecha_desde}
							required
						/>
					</div>
					<div class="form-group">
						<label for="fecha_hasta">Fecha de Fin *</label>
						<input
							type="date"
							id="fecha_hasta"
							bind:value={formLicencia.fecha_hasta}
							required
						/>
					</div>
					{#if diasLicencia > 0}
						<div class="info-dias">
							<small
								>📅 Días solicitados: <strong
									>{diasLicencia}</strong
								></small
							>
						</div>
					{/if}
					<div class="form-group">
						<label for="observaciones">Observaciones</label>
						<textarea
							id="observaciones"
							bind:value={formLicencia.observaciones}
							rows="3"
							placeholder="Motivo o comentarios adicionales..."
						></textarea>
					</div>
					<div class="modal-actions">
						<button
							type="button"
							class="btn btn-secondary"
							on:click={cerrarModales}>Cancelar</button
						>
						<button
							type="submit"
							class="btn btn-primary"
							disabled={saving}
						>
							{saving ? "Creando..." : "Crear Licencia"}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de Asignar Licencia -->
<ModalAsignar
	bind:show={showModalAsignar}
	{areas}
	tiposLicencia={$tiposLicencia}
	on:asignar={handleAsignarEvent}
	on:cancelar={() => (showModalAsignar = false)}
/>

<!-- Modal de Aprobar Licencia -->
<ModalAprobar
	bind:show={showModalAprobar}
	licencia={licenciaSeleccionada}
	on:aprobar={handleAprobarEvent}
	on:cancelar={() => (showModalAprobar = false)}
/>

<!-- Modal de Rechazar Licencia -->
<ModalRechazar
	bind:show={showModalRechazar}
	licencia={licenciaSeleccionada}
	on:rechazar={handleRechazarEvent}
	on:cancelar={() => (showModalRechazar = false)}
/>

<!-- Modal de confirmación para eliminar licencia -->
{#if showConfirmDeleteLicencia && licenciaAEliminar}
	<div class="modal-overlay">
		<div class="modal-confirm">
			<div class="modal-header-warning">
				<h3>🗑️ Eliminar Licencia</h3>
			</div>
			<div class="modal-body-confirm">
				<p>
					¿Estás seguro de que deseas eliminar la licencia de <strong
						>{licenciaAEliminar.agente_nombre}</strong
					>?
				</p>
				<div class="licencia-details">
					<p>
						<strong>Tipo:</strong>
						{licenciaAEliminar.tipo_licencia_descripcion ||
							"Sin tipo"}
					</p>
					<p>
						<strong>Período:</strong>
						{formatearFecha(licenciaAEliminar.fecha_desde)} al {formatearFecha(
							licenciaAEliminar.fecha_hasta,
						)}
					</p>
					<p><strong>Estado:</strong> {licenciaAEliminar.estado}</p>
					<p>
						<strong>Días:</strong>
						{licenciaAEliminar.dias_licencia}
					</p>
				</div>
				<p class="warning-text">
					⚠️ Esta acción no se puede deshacer y eliminará
					permanentemente la licencia del sistema.
				</p>
			</div>
			<div class="modal-footer-confirm">
				<button
					class="btn-cancelar-confirm"
					on:click={cancelarEliminacionLicencia}
				>
					Cancelar
				</button>
				<button
					class="btn-eliminar-confirm"
					on:click={confirmarEliminacionLicencia}
					disabled={eliminandoLicencia}
				>
					{eliminandoLicencia ? "Eliminando..." : "Eliminar Licencia"}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Modal para gestión de tipos de licencia -->
{#if showForm}
	<div class="modal-overlay">
		<div class="modal">
			<h3>
				{isEditing
					? "Editar tipo de licencia"
					: "Nuevo tipo de licencia"}
			</h3>
			{#if errorTipos}
				<div class="alert alert-error">{errorTipos}</div>
			{/if}
			<div class="form-row">
				<label for="codigo">Código / Nombre *</label>
				<input
					bind:value={form.codigo}
					placeholder="Ej: VAC, ENF, etc."
					required
				/>
			</div>
			<div class="form-row">
				<label for="desc">Descripción</label>
				<textarea
					rows="3"
					bind:value={form.descripcion}
					placeholder="Descripción del tipo de licencia"
				></textarea>
			</div>
			<div class="form-actions">
				<button class="btn-primary" on:click={guardar} disabled={saving}
					>{saving ? "Guardando..." : "Guardar"}</button
				>
				<button
					class="btn-limpiar"
					on:click={() => (showForm = false)}
					disabled={saving}>Cancelar</button
				>
			</div>
		</div>
	</div>
{/if}

<!-- Modal de confirmación para eliminar tipos -->
{#if showConfirmDelete && tipoAEliminar}
	<div class="modal-overlay">
		<div class="modal-confirm">
			<div class="modal-header-warning">
				<h3>⚠️ Confirmar Eliminación</h3>
			</div>
			<div class="modal-body-confirm">
				<p>
					¿Eliminar el tipo de licencia <strong
						>"{tipoAEliminar.codigo ||
							tipoAEliminar.nombre}"</strong
					>?
				</p>
				<p class="warning-text">
					Esta acción fallará si hay agentes con este tipo.
				</p>
			</div>
			<div class="modal-footer-confirm">
				<button
					class="btn-cancelar-confirm"
					on:click={cancelarEliminacion}
				>
					Cancelar
				</button>
				<button
					class="btn-eliminar-confirm"
					on:click={confirmarEliminacion}
				>
					Eliminar
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-container {
		max-width: 1600px;
		margin: 0 auto;
		min-height: 100vh;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding-bottom: 20px;
	}

	.header-title {
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 40px;
		margin: 0;
		max-width: 1000px;
		border-radius: 28px;
		overflow: hidden;
		text-align: center;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
	}

	.header-title::before {
		content: "";
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-image: linear-gradient(
				90deg,
				rgba(255, 255, 255, 0.03) 1px,
				transparent 1px
			),
			linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
		background-size: 50px 50px;
		animation: moveLines 20s linear infinite;
	}

	.header-title h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 30px;
		letter-spacing: 0.2px;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: inline-block;
	}

	.header-title h1::after {
		content: "";
		position: absolute;
		width: 40%;
		height: 3px;
		bottom: 0;
		left: 0;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(255, 255, 255, 0.9),
			transparent
		);
		animation: moveLine 2s linear infinite;
	}

	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
	}

	.toggle-buttons {
		display: flex;
		gap: 1rem;
		justify-content: center;
		margin-bottom: 2rem;
		padding: 1rem;
		border-radius: 16px;
	}

	.btn-toggle {
		padding: 1rem 2.5rem;
		border: none;
		background: rgb(228, 228, 228);
		color: #475569;
		border-radius: 12px;
		cursor: pointer;
		font-weight: 600;
		font-size: 16px;
		transition: all 0.3s ease;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		position: relative;
		overflow: hidden;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-toggle::before {
		content: "";
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(255, 255, 255, 0.3),
			transparent
		);
		transition: left 0.5s;
	}

	.btn-toggle:hover::before {
		left: 100%;
	}

	.btn-toggle.active {
		background: linear-gradient(135deg, #4c51bf 0%, #5b21b6 100%);
		color: white;
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(76, 81, 191, 0.4);
	}

	.btn-toggle:hover:not(.active) {
		background: linear-gradient(135deg, #d6d7d8, #d4d9e0);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	}

	.header-actions {
		display: flex;
		gap: 10px;
	}

	.btn-secondary,
	.btn-refresh,
	.btn-nuevoTipo {
		padding: 16px 32px;
		border: none;
		border-radius: 10px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 10px;
		font-size: 17px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-secondary {
		background: linear-gradient(135deg, #b78ef8 0%, #b966d3 100%);
		color: white;
		box-shadow: 0 4px 15px rgba(102, 126rgb (125, 138, 175) 0.3);
		margin-left: 10px;
	}

	.btn-secondary:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(215, 111, 241, 0.5);
	}

	.btn-refresh,
	.btn-header {
		background: linear-gradient(135deg, #ff9939 0%, #ffa358 100%);
		color: white;
	}

	.btn-refresh:hover,
	.btn-header:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(226, 148, 59, 0.4);
	}

	.btn-nuevoTipo {
		background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
		color: white;
	}

	.btn-nuevoTipo:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
	}

	/* Botones */
	.btn-primary,
	.btn-header {
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

	/* Estadísticas */
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
		margin-top: 20px;
		margin-bottom: 20px;
	}

	.stat-card {
		background: white;
		padding: 20px;
		border-radius: 16px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
		text-align: center;
		border-top: 4px solid #4c51bf;
		transition: transform 0.3s ease;
	}

	.stat-card:hover {
		transform: translateY(-5px);
	}

	.stat-number {
		font-size: 2.2rem;
		font-weight: 700;
		color: #4c51bf;
	}

	.stat-card.pending .stat-number {
		color: #ed8936;
	}
	.stat-card.approved .stat-number {
		color: #38a169;
	}
	.stat-card.rejected .stat-number {
		color: #e53e3e;
	}

	.stat-card.pending {
		border-top: 4px solid #ed8936;
	}
	.stat-card.approved {
		border-top: 4px solid #38a169;
	}
	.stat-card.rejected {
		border-top: 4px solid #e53e3e;
	}

	.stat-label {
		font-size: 16px;
		color: #222222e0;
		margin-top: 0.5rem;
		font-weight: 600;
	}

	.filtros-container {
		background: #f3f3f3d8;
		border: 1px solid #e0e0e09c;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 2rem;
	}
	.filtros-row {
		display: flex;
		gap: 2rem;
		align-items: end;
		flex-wrap: nowrap;
	}

	.filtro-group {
		flex: 1 1 200px;
		min-width: 160px;
		max-width: 100%;
	}

	.filtro-group label {
		color: #1a1a1a;
		font-weight: 600;
		color: #374151;
		font-size: 16px;
	}

	.filtro-group input,
	.filtro-group select {
		margin-top: 10px;
		width: 100%;
		padding: 0.7rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.875rem;
		background: white;
		appearance: none;
	}

	.filtro-group input:focus,
	.filtro-group select:focus,
	.input-busqueda:focus {
		outline: none;
		border-color: #4c51bf;
		box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
	}

	.filtro-actions {
		display: flex;
		gap: 10px;
		flex-shrink: 0;
		align-self: flex-end;
	}

	.btn-clear {
		padding: 10px 25px;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.3s ease;
		white-space: nowrap;
		height: 42px;
	}

	.btn-clear:hover {
		background: #5a6268;
		transform: translateY(-1px);
	}

	/* Tabla */
	.table-container {
		overflow-x: auto;
		overflow-y: auto;
		border: 1px solid #e5e7eb;
		border-radius: 12px;
		background: white;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
		max-height: 600px;
	}

	.table-container::-webkit-scrollbar {
		height: 8px;
		width: 8px;
	}

	.table-container::-webkit-scrollbar-track {
		background: #f1f5f9;
		border-radius: 10px;
	}

	.table-container::-webkit-scrollbar-thumb {
		background: #cbd5e1;
		border-radius: 10px;
	}

	.table-container::-webkit-scrollbar-thumb:hover {
		background: #94a3b8;
	}

	.table,
	.roles-table {
		width: 100%;
		border-collapse: collapse;
	}

	/* Header fijo con gradiente */
	.table thead,
	.roles-table thead {
		position: sticky;
		top: 0;
		z-index: 10;
		background: linear-gradient(135deg, #bad0e6 0%, #a3d3fac0 100%);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
	}

	.table th,
	.roles-table th {
		padding: 18px 20px;
		text-align: left;
		font-weight: 700;
		color: #1e293b;
		font-size: 13px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		border-bottom: 3px solid #3b82f6;
		background: transparent;
	}

	.table td,
	.roles-table td {
		padding: 18px 20px;
		font-size: 14px;
		color: #374151;
		vertical-align: middle;
		border-bottom: 1px solid #e5e7eb;
	}

	/* Hover effect para ambas tablas */
	.table tbody tr,
	.roles-table tbody tr {
		border-bottom: 1px solid #e5e7eb;
		transition: all 0.2s ease;
	}

	.table tbody tr:hover,
	.roles-table tbody tr:hover {
		background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
		transform: scale(1.005);
		box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
	}

	/* Estilos específicos para tabla de roles */
	.roles-table td strong {
		color: #1e293b;
		font-size: 14px;
		font-weight: 600;
	}

	/* Botones en tabla de roles */
	.roles-table .btn-primary {
		background: linear-gradient(135deg, #4c51bf, #5b21b6);
		color: white;
		padding: 8px 16px;
		border-radius: 8px;
		font-size: 13px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(76, 81, 191, 0.3);
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}

	.roles-table .btn-primary:hover {
		background: linear-gradient(135deg, #5b21b6, #6d28d9);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(76, 81, 191, 0.4);
	}

	.roles-table .btn-secondary {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		color: white;
		padding: 8px 16px;
		border-radius: 8px;
		font-size: 13px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}

	.roles-table .btn-secondary:hover {
		background: linear-gradient(135deg, #b91c1c, #991b1b);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(220, 38, 38, 0.4);
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
		display: inline-block;
		padding: 8px 16px;
		border-radius: 20px;
		font-size: 12px;
		font-weight: 700;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.estado-pendiente {
		background: linear-gradient(135deg, #fef3c7, #fde68a);
		color: #92400e;
		border: 1px solid #fcd34d;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.05);
		}
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
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
	}

	.btn-success:hover {
		background: linear-gradient(135deg, #059669, #047857);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
	}

	.btn-danger {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
	}

	.btn-danger:hover {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
	}

	.btn-warning {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
		box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
	}

	.btn-warning:hover {
		background: linear-gradient(135deg, #d97706, #b45309);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(245, 158, 11, 0.4);
	}

	.observaciones-row {
		background: #f7fafc;
	}

	/* Estados de carga y vacío */
	.loading-state,
	.loading-container {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}

	.loading-state .spinner-large,
	.loading-container .spinner-large {
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

	.no-data,
	.empty-state {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}

	.no-data p,
	.empty-state p {
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
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.1),
			0 10px 10px -5px rgba(0, 0, 0, 0.04);
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
		transition:
			border-color 0.15s ease-in-out,
			box-shadow 0.15s ease-in-out;
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
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 2000;
		backdrop-filter: blur(4px);
		animation: fadeIn 0.2s ease;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal {
		background: white;
		padding: 2rem;
		border-radius: 16px;
		width: 520px;
		max-width: 92%;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s ease;
		border: 1px solid #e5e7eb;
	}

	@keyframes slideUp {
		from {
			transform: translateY(20px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.modal h3 {
		margin: 0 0 1.5rem 0;
		color: #1e293b;
		font-size: 22px;
		font-weight: 700;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e5e7eb;
	}

	.form-row {
		margin-bottom: 1.25rem;
		display: flex;
		flex-direction: column;
	}

	.form-row label {
		font-weight: 600;
		margin-bottom: 8px;
		color: #374151;
		font-size: 14px;
	}

	.form-row input,
	.form-row textarea {
		padding: 12px 14px;
		border: 2px solid #e2e8f0;
		border-radius: 8px;
		font-size: 14px;
		transition: all 0.2s ease;
		font-family: inherit;
	}

	.form-row input:focus,
	.form-row textarea:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.form-row textarea {
		min-height: 100px;
		resize: vertical;
	}

	.form-actions {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
		margin-top: 1.5rem;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	/* Botones del modal */
	.modal .btn-primary {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 16px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.modal .btn-primary:hover:not(:disabled) {
		background: linear-gradient(135deg, #059669, #047857);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
	}

	.modal .btn-primary:disabled {
		opacity: 0.6;
		cursor: not-allowed;

		transform: none;
	}

	.modal .btn-limpiar {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 16px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(107, 114, 128, 0.3);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.modal .btn-limpiar:hover:not(:disabled) {
		background: linear-gradient(135deg, #4b5563, #374151);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(107, 114, 128, 0.4);
	}

	.modal .btn-limpiar:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	/* Modal de confirmación específico */
	.modal-confirm {
		background: white;
		border-radius: 16px;
		width: 480px;
		max-width: 92%;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		overflow: hidden;
	}

	.modal-header-warning {
		background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
		padding: 1.5rem;
		color: white;
	}

	.modal-header-warning h3 {
		margin: 0;
		font-size: 20px;
		font-weight: 700;
	}

	.modal-body-confirm {
		padding: 2rem;
	}

	.modal-body-confirm p {
		margin: 0 0 1rem 0;
		color: #374151;
		font-size: 15px;
	}

	.modal-body-confirm strong {
		color: #1e293b;
		font-weight: 600;
	}

	.warning-text {
		color: #d97706;
		font-size: 14px;
		font-weight: 500;
	}

	.modal-footer-confirm {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
		padding: 1.5rem;
		background: #f9fafb;
		border-top: 1px solid #e5e7eb;
	}

	.btn-cancelar-confirm {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-cancelar-confirm:hover {
		background: linear-gradient(135deg, #4b5563, #374151);
		transform: translateY(-2px);
	}

	.btn-eliminar-confirm {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-eliminar-confirm:hover {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-2px);
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
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	/* Responsive */
	@media (max-width: 1200px) {
		.page-container {
			padding: 1rem;
		}

		.header-title {
			max-width: 100%;
			padding: 20px 30px;
		}

		.header-title h1 {
			font-size: 24px;
		}

		.filtros-row {
			flex-wrap: wrap;
			gap: 1rem;
		}

		.filtro-group {
			flex: 1 1 calc(50% - 0.5rem);
			min-width: 200px;
		}

		.table-container {
			font-size: 0.875rem;
		}
	}

	@media (max-width: 768px) {
		.page-container {
			padding: 0.5rem;
		}

		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
			padding-bottom: 1rem;
		}

		.header-title {
			padding: 20px 15px;
			border-radius: 16px;
			margin-right: 0;
		}

		.header-title h1 {
			font-size: 20px;
		}

		.header-actions {
			flex-direction: column;
			width: 100%;
		}

		.btn-secondary,
		.btn-refresh,
		.btn-header {
			width: 100%;
			justify-content: center;
			margin-left: 0;
			padding: 12px 20px;
			font-size: 15px;
		}

		.toggle-buttons {
			flex-direction: column;
			gap: 0.75rem;
			padding: 0.75rem;
		}

		.btn-toggle {
			width: 100%;
			padding: 0.75rem 1.5rem;
			font-size: 15px;
		}

		.stats-container {
			grid-template-columns: repeat(2, 1fr);
			gap: 0.75rem;
		}

		.stat-card {
			padding: 15px;
		}

		.stat-number {
			font-size: 1.8rem;
		}

		.filtros-container {
			padding: 1rem;
		}

		.filtros-row {
			flex-direction: column;
			gap: 1rem;
		}

		.filtro-group {
			flex: 1 1 100%;
			min-width: 100%;
		}

		.filtro-group label {
			font-size: 14px;
		}

		.btn-clear {
			width: 100%;
			height: auto;
			padding: 12px;
		}

		/* Tabla responsive */
		.table-container {
			border-radius: 8px;
			max-height: 500px;
		}

		.table th,
		.roles-table th {
			padding: 12px 10px;
			font-size: 11px;
		}

		.table td,
		.roles-table td {
			padding: 12px 10px;
			font-size: 13px;
		}

		.agente-info strong {
			font-size: 13px;
		}

		.agente-info small {
			font-size: 11px;
		}

		.tipo-badge,
		.estado-badge {
			font-size: 10px;
			padding: 6px 10px;
		}

		.acciones {
			flex-direction: column;
			gap: 6px;
		}

		.btn-sm {
			width: 100%;
			padding: 8px 12px;
			font-size: 12px;
		}

		/* Modales responsive */
		.modal-contenido,
		.modal {
			margin: 0.5rem;
			max-width: calc(100vw - 1rem);
			max-height: calc(100vh - 1rem);
		}

		.modal-header {
			padding: 1rem;
		}

		.modal-header h5,
		.modal h3 {
			font-size: 18px;
		}

		.modal-body {
			padding: 0 1rem 1rem;
		}

		.form-group label {
			font-size: 14px;
		}

		.form-group input,
		.form-group select,
		.form-group textarea {
			padding: 0.6rem;
			font-size: 14px;
		}

		.modal-actions {
			flex-direction: column;
			gap: 0.5rem;
		}

		.btn {
			width: 100%;
			padding: 0.875rem 1rem;
		}
	}

	@media (max-width: 480px) {
		.header-title h1 {
			font-size: 18px;
		}

		.stats-container {
			grid-template-columns: 1fr;
		}

		.stat-number {
			font-size: 1.5rem;
		}

		.stat-label {
			font-size: 14px;
		}

		.btn-toggle {
			padding: 0.6rem 1rem;
			font-size: 14px;
		}

		/* Tabla muy pequeña */
		.table th,
		.roles-table th {
			padding: 10px 8px;
			font-size: 10px;
		}

		.table td,
		.roles-table td {
			padding: 10px 8px;
			font-size: 12px;
		}

		.table-container {
			max-height: 400px;
		}
	}
</style>
