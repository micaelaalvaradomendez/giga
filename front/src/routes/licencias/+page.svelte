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
		aprobarLicencia,
		rechazarLicencia,
		actualizarFiltros,
		limpiarFiltros,
		obtenerPermisos,
		puedeAprobarLicencia,
		puedeAsignarAAgente,
		puedeVerLicenciaDeRol,
		formatearFecha,
		calcularDiasLicencia,
		obtenerColorEstado,
		obtenerIconoEstado,
	} from "$lib/paneladmin/controllers/licenciasController.js";

	import ModalAsignar from "$lib/componentes/admin/licencias/ModalAsignar.svelte";
	import ModalAprobar from "$lib/componentes/admin/licencias/ModalAprobar.svelte";
	import ModalRechazar from "$lib/componentes/admin/licencias/ModalRechazar.svelte";
	import ModalSolicitar from "$lib/componentes/licencias/ModalSolicitar.svelte";
	import ModalAlert from "$lib/componentes/ModalAlert.svelte";
	import { modalAlert } from "$lib/stores/modalAlertStore.js";

	let vistaActual = "licencias"; // 'licencias' o 'tipos'

	let userInfo = null;
	let permisos = {};
	let areas = [];
	let agentes = [];

	// Modal states
	let showModalSolicitar = false;
	let showModalCrear = false;
	let showModalAsignar = false;
	let showModalAprobar = false;
	let showModalRechazar = false;
	let licenciaSeleccionada = null;

	let formAprobacion = {
		observaciones: "",
	};

	let formRechazo = {
		motivo: "",
	};

	let saving = false;

	let tipos = [];
	let loadingTipos = false;
	let errorTipos = null;
	let searchTerm = "";

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

	let alertConfig = {
		show: false,
		type: "info",
		title: "",
		message: "",
		duration: 0,
		showConfirmButton: true,
		confirmText: "Aceptar",
		showCancelButton: false,
		cancelText: "Cancelar",
		onConfirm: null,
		onCancel: null,
		onClose: null,
	};

	onMount(async () => {
		await inicializar();
	});

	function mostrarExito(mensaje, titulo = "Éxito") {
		mostrarAlerta({
			title: titulo,
			message: mensaje,
			type: "success",
			duration: 3000,
		});
	}

	function mostrarError(mensaje, titulo = "Error") {
		mostrarAlerta({
			title: titulo,
			message: mensaje,
			type: "error",
		});
	}

	function mostrarConfirmacion(mensaje, titulo = "Confirmar", onConfirm) {
		mostrarAlerta({
			title: titulo,
			message: mensaje,
			type: "warning",
			showCancelButton: true,
			confirmText: "Sí, continuar",
			cancelText: "Cancelar",
			onConfirm: onConfirm,
		});
	}

	function handleAlertConfirm() {
		if (alertConfig.onConfirm) {
			alertConfig.onConfirm();
		}
		alertConfig.show = false;
	}

	function handleAlertCancel() {
		if (alertConfig.onCancel) {
			alertConfig.onCancel();
		}
		alertConfig.show = false;
	}

	function handleAlertClose() {
		if (alertConfig.onClose) {
			alertConfig.onClose();
		}
		alertConfig.show = false;
	}

	async function inicializar() {
		try {
			// Obtener información del usuario actual
			const userResponse = await AuthService.getCurrentUserData();
			if (userResponse?.success && userResponse.data?.success) {
				userInfo = userResponse.data.data;
				usuario.set(userInfo);

				// Obtener el rol del usuario correctamente
				const rol =
					userInfo.roles?.[0]?.nombre ||
					userInfo.rol_nombre ||
					"Agente";
				console.log(
					"🔐 Usuario actual:",
					userInfo.nombre,
					userInfo.apellido,
					"| Rol:",
					rol,
					"| Área:",
					userInfo.area?.nombre,
				);

				permisos = obtenerPermisos(rol, userInfo.id_area);
				console.log("🔑 Permisos calculados:", permisos);

				// Cargar datos iniciales
				await cargarDatosIniciales();
			} else {
				console.error("❌ No se pudo obtener información del usuario");
				goto("/");
			}
		} catch (err) {
			console.error("❌ Error inicializando:", err);
			goto("/");
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
					areas = todasAreas.filter(
						(a) => a.id_area === userInfo.id_area,
					);
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
			console.error("Error cargando datos iniciales:", err);
			error.set("Error al cargar datos iniciales");
		}
	}

	async function cargarAgentesArea() {
		try {
			const params = permisos.soloSuArea
				? { area_id: userInfo.id_area }
				: {};
			const response = await personasService.getAgentes(params);
			if (response?.data?.success) {
				let agentesCompletos = response.data.data || [];

				// Filtrar agentes según el rol del usuario (especialmente para Agente Avanzado)
				if (permisos.puedeAsignarSoloAgentes) {
					// Agente Avanzado solo puede ver/asignar a agentes simples
					agentes = agentesCompletos.filter(
						(agente) =>
							(agente.rol?.nombre || agente.rol_nombre) ===
							"Agente",
					);
					console.log(
						`🔍 Agente Avanzado: filtrado ${agentes.length} agentes de ${agentesCompletos.length} totales`,
					);
				} else {
					agentes = agentesCompletos;
				}
			}
		} catch (err) {
			console.error("Error cargando agentes:", err);
		}
	}

	function abrirModalCrear() {
		showModalCrear = true;
	}

	function abrirModalAsignar() {
		showModalAsignar = true;
	}

	function abrirModalAprobar(licencia) {
		licenciaSeleccionada = licencia;
		formAprobacion = { observaciones: "" };
		showModalAprobar = true;
	}

	function abrirModalRechazar(licencia) {
		licenciaSeleccionada = licencia;
		formRechazo = { motivo: "" };
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

	function mostrarAlerta(config) {
		if (typeof config === "string") {
			config = {
				title: "Información",
				message: config,
				type: "info",
			};
		}

		alertConfig = {
			...alertConfig,
			...config,
			show: true,
		};
	}

	function handleLicenciaCreada(event) {
		showModalCrear = false;
		mostrarExito("Licencia solicitada correctamente. Aguarde aprobación.");
		cargarLicencias(); // Recargar la lista
	}

	function handleAsignarEvent(event) {
		console.log("Asignar licencia event:", event.detail);
		showModalAsignar = false;
		mostrarExito("Licencia asignada correctamente");
	}

	function handleAprobarEvent(event) {
		if (licenciaSeleccionada) {
			aprobarLicencia(
				licenciaSeleccionada.id_licencia,
				event.detail.observaciones,
			).then((resultado) => {
				if (resultado.success) {
					showModalAprobar = false;
					mostrarExito("Licencia aprobada correctamente.");
				} else {
					mostrarError(resultado.error);
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
					mostrarExito("Licencia rechazada correctamente.");
				} else {
					mostrarError(resultado.error);
				}
			});
		}
	}

	// Función para cambiar entre vistas
	function cambiarVista(vista) {
		vistaActual = vista;
		if (vista === "tipos") {
			cargarTipos();
		}
	}

	// Función para cargar tipos de licencia
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

	// Función para eliminar tipos
	function eliminar(tipo) {
		mostrarConfirmacion(
			`¿Eliminar el tipo de licencia "<strong>${tipo.codigo || tipo.nombre}</strong>"?<br><br>
		Esta acción fallará si hay agentes con este tipo asignado.`,
			"⚠️ Eliminar Tipo de Licencia",
			() => confirmarEliminacionTipo(tipo),
		);
	}

	async function confirmarEliminacionTipo(tipo) {
		const id = tipo.id_tipo_licencia || tipo.id || null;
		if (!id) return;

		try {
			await asistenciaService.deleteTipoLicencia(id);
			tipos = tipos.filter((t) => (t.id_tipo_licencia || t.id) !== id);
			mostrarExito("Tipo de licencia eliminado correctamente");
		} catch (err) {
			console.error(err);
			const msg =
				err?.response?.data?.message ||
				err.message ||
				"No se pudo eliminar. Puede que existan agentes vinculados.";
			mostrarError(msg);
		}
	}

	$: tiposFiltrados = tipos.filter((t) => {
		if (!searchTerm) return true;
		const s = searchTerm.toLowerCase();
		return (
			(t.codigo || t.nombre || "").toLowerCase().includes(s) ||
			(t.descripcion || "").toLowerCase().includes(s)
		);
	});

	async function handleAprobarLicencia() {
		if (!licenciaSeleccionada) return;

		saving = true;
		const resultado = await aprobarLicencia(
			licenciaSeleccionada.id_licencia,
			formAprobacion.observaciones,
		);

		if (resultado.success) {
			cerrarModales();
			mostrarExito("Licencia aprobada correctamente.");
		} else {
			mostrarError(resultado.error);
		}
		saving = false;
	}

	async function handleRechazarLicencia() {
		if (!licenciaSeleccionada || !formRechazo.motivo.trim()) {
			mostrarError("Debe indicar el motivo del rechazo");
			return;
		}

		saving = true;
		const resultado = await rechazarLicencia(
			licenciaSeleccionada.id_licencia,
			formRechazo.motivo,
		);

		if (resultado.success) {
			cerrarModales();
			mostrarExito("Licencia rechazada.");
		} else {
			mostrarError(resultado.error);
		}
		saving = false;
	}

	// Funciones para filtros
	function handleFechaDesdeChange() {
		// Si la nueva fecha desde es posterior a la fecha hasta, limpiar fecha hasta
		if ($filtros.fecha_desde && $filtros.fecha_hasta && $filtros.fecha_desde > $filtros.fecha_hasta) {
			actualizarFiltros({ fecha_hasta: '' });
		}
		aplicarFiltros();
	}

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
		const rol =
			userInfo?.roles?.[0]?.nombre || userInfo?.rol_nombre || "Agente";
		return puedeAprobarLicencia(licencia, rol, userInfo?.id_area);
	}
</script>

<svelte:head>
	<title>Gestión de Licencias - GIGA</title>
</svelte:head>

<div class="page-container">
	<div class="page-header">
		<div class="header-title">
			<h1>📋 Gestión de Licencias</h1>
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
				<label for="fecha_desde">📆 Desde</label>
				<input
					type="date"
					id="fecha_desde"
					bind:value={$filtros.fecha_desde}
					on:change={handleFechaDesdeChange}
				/>
			</div>
			<div class="filtro-group">
				<label for="fecha_hasta">📆 Hasta</label>
				<input
					type="date"
					id="fecha_hasta"
					bind:value={$filtros.fecha_hasta}
					min={$filtros.fecha_desde}
					on:change={aplicarFiltros}
				/>
			</div>
			<div class="filtro-group">
				<label for="area_filter">🗂️ Área ({areas.length} áreas)</label>
				<select
					id="area_filter"
					bind:value={$filtros.area_id}
					on:change={aplicarFiltros}
				>
					<option value={null}>Todas las áreas</option>
					{#each areas as area}
						<option value={area.id_area}>{area.nombre}</option>
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

	<!-- Contenido principal -->
	<div class="page-content">
		{#if $error}
			<div class="alert alert-error">
				<strong>❌ Error:</strong>
				{$error}
				<button class="btn-retry" on:click={() => cargarLicencias()}
					>Reintentar</button
				>
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
					{#if Object.values($filtros).some((v) => v)}
						No hay licencias que coincidan con los filtros
						aplicados.
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
			<!-- Vista de tabla para desktop -->
			<div class="table-container desktop-only">
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
							<tr
								class="licencia-row"
								class:pending={licencia.estado === "pendiente"}
							>
								<td>
									<div class="agente-info">
										<strong>{licencia.agente_nombre}</strong
										>
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
										{formatearFecha(licencia.fecha_desde)} -
										{formatearFecha(licencia.fecha_hasta)}
									</div>
								</td>
								<td>
									<span class="dias-count">
										{calcularDiasLicencia(
											licencia.fecha_desde,
											licencia.fecha_hasta,
										)} días
									</span>
								</td>
								<td>
									<span
										class="estado-badge"
										style="background-color: {obtenerColorEstado(
											licencia.estado,
										)}20; color: {obtenerColorEstado(
											licencia.estado,
										)}; border: 1px solid {obtenerColorEstado(
											licencia.estado,
										)}40"
									>
										{obtenerIconoEstado(licencia.estado)}
										{licencia.estado.toUpperCase()}
									</span>
								</td>
								<td>
									{formatearFecha(licencia.creado_en)}
								</td>
								<td>
									<div class="acciones">
										{#if licencia.estado === "pendiente" && puedeAprobar(licencia)}
											<button
												class="btn-small btn-success"
												on:click={() =>
													abrirModalAprobar(licencia)}
												title="Aprobar licencia"
											>
												✅ Aprobar
											</button>
											<button
												class="btn-small btn-danger"
												on:click={() =>
													abrirModalRechazar(
														licencia,
													)}
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

			<!-- Vista de tarjetas para móvil -->
			<div class="cards-container mobile-only">
				{#each $licenciasFiltradas as licencia (licencia.id_licencia)}
					<div class="licencia-card" class:pending={licencia.estado === "pendiente"}>
						<div class="card-header">
							<div class="card-agente">
								<strong>{licencia.agente_nombre}</strong>
								<small>{licencia.area_nombre}</small>
								<span class="tipo-badge-mobile">{licencia.tipo_licencia_descripcion}</span>
							</div>
							<span
								class="estado-badge"
								style="background-color: {obtenerColorEstado(licencia.estado)}20; color: {obtenerColorEstado(licencia.estado)}; border: 1px solid {obtenerColorEstado(licencia.estado)}40"
							>
								{obtenerIconoEstado(licencia.estado)}
								{licencia.estado.toUpperCase()}
							</span>
						</div>
						
						<div class="card-body">
							<div class="card-row">
								<span class="card-label">📅 Período:</span>
								<span class="card-value">{formatearFecha(licencia.fecha_desde)} - {formatearFecha(licencia.fecha_hasta)}</span>
							</div>
							<div class="card-row">
								<span class="card-label">⏱️ Duración:</span>
								<span class="dias-count-big">{calcularDiasLicencia(licencia.fecha_desde, licencia.fecha_hasta)} días</span>
							</div>
							<div class="card-row">
								<span class="card-label">📨 Solicitado:</span>
								<span class="card-value">{formatearFecha(licencia.creado_en)}</span>
							</div>
						</div>

						{#if licencia.estado === "pendiente" && puedeAprobar(licencia)}
							<div class="card-actions">
								<button
									class="btn-card btn-success"
									on:click={() => abrirModalAprobar(licencia)}
								>
									✅ Aprobar
								</button>
								<button
									class="btn-card btn-danger"
									on:click={() => abrirModalRechazar(licencia)}
								>
									❌ Rechazar
								</button>
							</div>
						{/if}
						
						{#if licencia.observaciones}
							<div class="card-observaciones">
								<span class="card-label">💬 Observaciones:</span>
								<p>{licencia.observaciones}</p>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<!-- Modal Crear/Solicitar Licencia -->
<ModalSolicitar
	bind:show={showModalCrear}
	tiposLicencia={$tiposLicencia}
	{userInfo}
	on:created={handleLicenciaCreada}
	on:close={() => (showModalCrear = false)}
/>

<!-- Modal de Asignar Licencia -->
<ModalAsignar
	bind:show={showModalAsignar}
	{areas}
	tiposLicencia={$tiposLicencia}
	on:assigned={handleAsignarEvent}
	on:close={() => (showModalAsignar = false)}
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

<ModalAlert
	bind:show={alertConfig.show}
	type={alertConfig.type}
	title={alertConfig.title}
	message={alertConfig.message}
	duration={alertConfig.duration}
	showConfirmButton={alertConfig.showConfirmButton}
	confirmText={alertConfig.confirmText}
	showCancelButton={alertConfig.showCancelButton}
	cancelText={alertConfig.cancelText}
	on:confirm={handleAlertConfirm}
	on:cancel={handleAlertCancel}
	on:close={handleAlertClose}
/>

<!-- ModalAlert para showAlert() del store -->
<ModalAlert
	bind:show={$modalAlert.show}
	type={$modalAlert.type}
	title={$modalAlert.title}
	message={$modalAlert.message}
	showConfirmButton={$modalAlert.showConfirmButton}
	confirmText={$modalAlert.confirmText}
	showCancelButton={$modalAlert.showCancelButton}
	cancelText={$modalAlert.cancelText}
	on:confirm={() => $modalAlert.onConfirm && $modalAlert.onConfirm()}
	on:cancel={() => $modalAlert.onCancel && $modalAlert.onCancel()}
/>

<style>
* {
    box-sizing: border-box;
}

html, body {
    overflow-x: hidden;
    max-width: 100vw;
}

.page-container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 1.5rem;
    min-height: 100vh;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    box-sizing: border-box;
    overflow-x: hidden;
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
		font-size: 18px;
		letter-spacing: 0.2px;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: block;
		max-width: 100%;
		word-wrap: break-word;
	}

	@media (min-width: 480px) {
		.header-title h1 {
			font-size: 22px;
		}
	}

	@media (min-width: 640px) {
		.header-title h1 {
			font-size: 26px;
			display: inline-block;
		}
	}

	@media (min-width: 768px) {
		.header-title h1 {
			font-size: 30px;
		}
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

	.header-actions {
		display: flex;
		gap: 10px;
	}

	.btn-primary,
	.btn-secondary {
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

	.btn-primary {
		background: linear-gradient(135deg, #4c51bf 0%, #5b21b6 100%);
		color: white;
		box-shadow: 0 4px 15px rgba(76, 81, 191, 0.3);
	}

	.btn-primary:hover:not(:disabled) {
		background: linear-gradient(135deg, #5b21b6, #6d28d9);
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(76, 81, 191, 0.4);
	}

	.btn-secondary {
		background: linear-gradient(135deg, #b78ef8 0%, #b966d3 100%);
		color: white;
		box-shadow: 0 4px 15px rgba(183, 142, 248, 0.3);
	}

	.btn-secondary:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(215, 111, 241, 0.5);
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

	/* Filtros */
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
	.filtro-group select:focus {
		outline: none;
		border-color: #4c51bf;
		box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
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
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.table-container::-webkit-scrollbar {
		display: none;
	}

	.licencias-table {
		width: 100%;
		border-collapse: collapse;
	}

	/* Header fijo con gradiente */
	.licencias-table thead {
		position: sticky;
		top: 0;
		z-index: 10;
		background: linear-gradient(135deg, #bad0e6 0%, #a3d3fac0 100%);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
	}

	.licencias-table th {
		padding: 18px 20px;
		text-align: left;
		font-weight: 700;
		color: #1e293b;
		font-size: 13px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		background: transparent;
	}

	.licencias-table td {
		padding: 18px 20px;
		font-size: 14px;
		color: #374151;
		vertical-align: middle;
		border-bottom: 1px solid #e5e7eb;
	}

	/* Hover effect para la tabla */
	.licencias-table tbody tr {
		border-bottom: 1px solid #e5e7eb;
		transition: all 0.2s ease;
	}

	.licencias-table tbody tr:hover {
		background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
		transform: scale(1.005);
		box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
	}

	.licencia-row.pending {
		background-color: #fef3c7;
	}

	.agente-info strong {
		display: block;
		color: #2d3748;
	}

	.agente-info small {
		color: #718096;
		font-size: 0.75rem;
	}

	.tipo-badge {
		background: #edf2f7;
		color: #4a5568;
		padding: 0.25rem 0.75rem;
		border-radius: 20px;
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
		display: inline-block;
		padding: 8px 16px;
		border-radius: 20px;
		font-size: 12px;
		font-weight: 700;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

	.acciones {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.btn-small {
		padding: 0.375rem 0.75rem;
		font-size: 14px;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		transition: all 0.2s;
	}

	.btn-success {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
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

	.btn-info {
		background: #0ea5e9;
		color: white;
	}

	.btn-info:hover {
		background: #0284c7;
		transform: translateY(-2px);
	}

	/* Estados de carga y vacío */
	.loading-container {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}

	.loading-container .spinner-large {
		margin: 0 auto 1rem;
		width: 2rem;
		height: 2rem;
		border: 2px solid #e2e8f0;
		border-top: 2px solid #4c51bf;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.empty-state {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}

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

	.btn-retry {
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
	}

	.btn-retry:hover {
		background: linear-gradient(135deg, #5b21b6, #6d28d9);
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(76, 81, 191, 0.4);
	}

	/* Clases para mostrar/ocultar según dispositivo */
	.mobile-only {
		display: none !important;
	}

	.desktop-only {
		display: block;
	}

	/* Estilos de tarjetas para móvil */
	.cards-container {
		flex-direction: column;
		gap: 1rem;
	}

	.licencia-card {
		background: white;
		border-radius: 16px;
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
		overflow: hidden;
		border: 1px solid #e5e7eb;
	}

	.licencia-card.pending {
		border-left: 4px solid #ed8936;
		background: linear-gradient(to right, #fffbeb, white);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		padding: 12px 14px;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		border-bottom: 1px solid #e5e7eb;
		gap: 10px;
	}

	.card-header .estado-badge {
		font-size: 13px;
		padding: 8px 14px;
		white-space: nowrap;
		flex-shrink: 0;
	}

	.card-agente {
		display: flex;
		flex-direction: column;
		gap: 1px;
		flex: 1;
		min-width: 0;
	}

	.card-agente strong {
		font-size: 15px;
		color: #1e293b;
		font-weight: 700;
	}

	.card-agente small {
		font-size: 12px;
		color: #64748b;
	}

	.tipo-badge-mobile {
		display: inline-block;
		margin-top: 6px;
		padding: 4px 10px;
		background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
		color: #3730a3;
		font-size: 11px;
		font-weight: 600;
		border-radius: 12px;
		border: 1px solid #a5b4fc;
	}

	.dias-count-big {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		color: white;
		padding: 4px 12px;
		border-radius: 12px;
		font-size: 14px;
		font-weight: 700;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
	}

	.card-body {
		padding: 8px 14px;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.card-row {
		display: flex;
		justify-content: flex-start;
		align-items: baseline;
		gap: 4px;
		padding: 2px 0;
		flex-wrap: wrap;
	}

	.card-label {
		font-size: 13px;
		color: #64748b;
		font-weight: 500;
		flex-shrink: 0;
	}

	.card-value {
		font-size: 13px;
		color: #1e293b;
		font-weight: 600;
	}

	.tipo-row {
		flex-wrap: wrap;
	}

	.card-tipo-value {
		font-size: 12px;
		color: #1e293b;
		font-weight: 600;
		word-break: break-word;
	}

	.card-actions {
		display: flex;
		gap: 10px;
		padding: 12px 16px;
		background: #f8fafc;
		border-top: 1px solid #e5e7eb;
	}

	.btn-card {
		flex: 1;
		padding: 12px 16px;
		border: none;
		border-radius: 10px;
		font-weight: 600;
		font-size: 14px;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
	}

	.btn-card.btn-success {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
		box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
	}

	.btn-card.btn-success:hover {
		background: linear-gradient(135deg, #059669, #047857);
		transform: translateY(-1px);
	}

	.btn-card.btn-danger {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		box-shadow: 0 2px 6px rgba(239, 68, 68, 0.3);
	}

	.btn-card.btn-danger:hover {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-1px);
	}

	.card-observaciones {
		padding: 12px 16px;
		background: #fef3c7;
		border-top: 1px solid #fcd34d;
	}

	.card-observaciones p {
		margin: 6px 0 0 0;
		font-size: 13px;
		color: #92400e;
		line-height: 1.4;
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
		/* Mostrar tarjetas, ocultar tabla */
		.desktop-only {
			display: none !important;
		}

		.mobile-only {
			display: flex !important;
		}

		.page-container {
			padding: 0.75rem;
			 max-width: 100vw;  
        overflow-x: hidden;
        box-sizing: border-box; 
		}

		.page-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
			padding-bottom: 1rem;
			margin-bottom: 1rem;
		}

		.header-title {
			padding: 18px 12px;
			border-radius: 16px;
			margin: 0;
			width: 100%;
			box-sizing: border-box;
		}

		.header-title h1 {
			font-size: 18px;
			word-break: break-word;
			line-height: 1.3;
		}

		.header-actions {
			flex-direction: column;
			width: 100%;
			gap: 8px;
		}

		.btn-primary,
		.btn-secondary {
			width: 100%;
			justify-content: center;
			margin-left: 0;
			padding: 14px 16px;
			font-size: 14px;
			border-radius: 12px;
		}

		.stats-container {
			grid-template-columns: 1fr;
			gap: 0.75rem;
			padding: 0;
		}

		.stat-card {
			padding: 16px 12px;
			border-radius: 12px;
		}

		.stat-number {
			font-size: 1.75rem;
		}

		.stat-label {
			font-size: 14px;
		}

		.filtros-container {
			padding: 1rem;
			border-radius: 10px;
			margin-bottom: 1rem;
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
			display: block;
			margin-bottom: 6px;
		}

		.filtro-group input,
		.filtro-group select {
			padding: 12px;
			font-size: 14px;
			border-radius: 10px;
		}

		.btn-clear {
			width: 100%;
			height: auto;
			padding: 14px;
			font-size: 14px;
			border-radius: 10px;
			margin-top: 0.5rem;
		}

		/* Tabla responsive */
		.table-container {
			border-radius: 10px;
			max-height: 450px;
			margin: 0;
			width: 100%;
			box-sizing: border-box;
		}

		.licencias-table th {
			padding: 12px 8px;
			font-size: 10px;
		}

		.licencias-table td {
			padding: 10px 8px;
			font-size: 12px;
		}

		.agente-info strong {
			font-size: 12px;
		}

		.agente-info small {
			font-size: 10px;
		}

		.tipo-badge {
			font-size: 9px;
			padding: 4px 8px;
		}

		.estado-badge {
			font-size: 9px;
			padding: 5px 8px;
		}

		.dias-count {
			font-size: 10px;
			padding: 3px 6px;
		}

		.acciones {
			flex-direction: column;
			gap: 4px;
		}

		.btn-small {
			padding: 6px 10px;
			font-size: 11px;
		}

		.periodo {
			font-size: 11px;
		}
	}

	@media (max-width: 480px) {
		.page-container {
			padding: 8px;
		}

		.header-title {
			padding: 15px 10px;
			border-radius: 14px;
		}

		.header-title h1 {
			font-size: 16px;
		}

		.btn-primary,
		.btn-secondary {
			padding: 12px 14px;
			font-size: 13px;
		}

		.stats-container {
			gap: 0.5rem;
		}

		.stat-card {
			padding: 14px 10px;
		}

		.stat-number {
			font-size: 1.5rem;
		}

		.stat-label {
			font-size: 13px;
		}

		.filtros-container {
			padding: 0.75rem;
		}

		.filtro-group label {
			font-size: 13px;
		}

		.filtro-group input,
		.filtro-group select {
			padding: 10px;
			font-size: 13px;
		}

		/* Tabla muy pequeña */
		.table-container {
			max-height: 380px;
			border-radius: 8px;
		}

		.licencias-table th {
			padding: 8px 6px;
			font-size: 9px;
		}

		.licencias-table td {
			padding: 8px 6px;
			font-size: 11px;
		}

		.agente-info strong {
			font-size: 11px;
		}

		.agente-info small {
			font-size: 9px;
		}

		.tipo-badge {
			font-size: 8px;
			padding: 3px 6px;
		}

		.estado-badge {
			font-size: 8px;
			padding: 4px 6px;
		}

		.dias-count {
			font-size: 9px;
		}

		.periodo {
			font-size: 10px;
		}

		.btn-small {
			padding: 5px 8px;
			font-size: 10px;
		}

		.empty-state {
			padding: 2rem 1rem;
		}

		.empty-icon {
			font-size: 2.5rem;
		}

		.empty-state h3 {
			font-size: 16px;
		}

		.empty-state p {
			font-size: 14px;
		}
	}
</style>
