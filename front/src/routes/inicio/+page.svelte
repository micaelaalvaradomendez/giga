<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { API_BASE_URL } from "$lib/api.js";
	import AuthService from "$lib/login/authService.js";
	import ModalUsuario from "$lib/componentes/usuario/ModalUsuario.svelte";
	import EditarPerfil from "$lib/componentes/usuario/EditarPerfil.svelte";
	import CambioContrasenaObligatorio from "$lib/componentes/usuario/CambioContrasenaObligatorio.svelte";
	import CalendarioBase from "$lib/componentes/calendarioBase.svelte";
	import { guardiasService } from "$lib/services.js";
    import Notificaciones from "$lib/componentes/notificaciones/Notificaciones.svelte";
	import { feriados as feriadosStore, loadFeriados } from "$lib/stores/dataCache.js";
	
	let user = null;
	let isLoading = true;
	let errorMessage = "";
	let showModalUsuario = false;
	let showEditProfile = false;
	let showMandatoryPasswordChange = false;
	let guardias = [];
	let loadingGuardias = false;
	let asistenciaHoy = null;
	let loadingAsistencia = false;
	
	// Usar store de feriados en lugar de variable local
	$: feriados = $feriadosStore;
	
	onMount(async () => {
		try {
			// Use getCurrentUser from localStorage first (checkSession already called in +layout.svelte)
			user = AuthService.getCurrentUser();
			if (user) {
				// Check password change requirement from localStorage
				if (AuthService.requiresPasswordChange()) {
					showMandatoryPasswordChange = true;
				}
				await Promise.all([
					cargarFeriadosOptimizado(),
					cargarGuardias(),
					cargarEstadoAsistencia(),
				]);
			} else {
				goto("/");
				return;
			}
		} catch (error) {
			console.error("Error verificando sesión:", error);
			errorMessage = "Error verificando la sesión";
			setTimeout(() => goto("/"), 2000);
		} finally {
			isLoading = false;
		}
	});
	
	async function cargarFeriadosOptimizado() {
		try {
			// Usar caché global - evita cargas duplicadas
			await loadFeriados();
		} catch (error) {
			console.error("Error cargando feriados:", error);
		}
	}
	
	async function cargarGuardias() {
		if (!user || !user.id) return;
		try {
			loadingGuardias = true;
			const response = await guardiasService.getGuardiasAgente(user.id);
			guardias = response.data?.guardias || [];
		} catch (error) {
			console.error("Error cargando guardias:", error);
			guardias = [];
		} finally {
			loadingGuardias = false;
		}
	}
	async function cargarEstadoAsistencia() {
		try {
			loadingAsistencia = true;
			const response = await fetch(`${API_BASE_URL}/asistencia/estado/`, {
				credentials: "include",
			});
			if (response.ok) {
				const data = await response.json();
				asistenciaHoy = data.data;
			}
		} catch (error) {
			console.error("Error cargando estado asistencia:", error);
		} finally {
			loadingAsistencia = false;
		}
	}
	async function handleLogout() {
		try {
			await AuthService.logout();
			goto("/");
		} catch (error) {
			console.error("Error durante logout:", error);
			goto("/");
		}
	}
	function toggleModalUsuario() {
		showModalUsuario = !showModalUsuario;
	}
	function handleEditarPerfil() {
		showModalUsuario = false;
		showEditProfile = true;
	}
	function handleCerrarSesion() {
		showModalUsuario = false;
		handleLogout();
	}
	function closeEditProfile() {
		showEditProfile = false;
	}
	function handleUserUpdated(event) {
		user = { ...user, ...event.detail };
	}
	function getProximasGuardias() {
		if (!guardias || guardias.length === 0) return [];
		const hoy = new Date();
		hoy.setHours(0, 0, 0, 0);
		return guardias
			.filter((g) => {
				const fechaGuardia = new Date(g.fecha + "T00:00:00");
				fechaGuardia.setHours(0, 0, 0, 0);
				return fechaGuardia >= hoy;
			})
			.sort((a, b) => new Date(a.fecha + "T00:00:00") - new Date(b.fecha + "T00:00:00"))
			.slice(0, 3);
	}
	function formatearFecha(fecha) {
		if (!fecha) return "";
		const d = new Date(fecha);
		return d.toLocaleDateString("es-AR", {
			day: "2-digit",
			month: "2-digit",
			year: "numeric",
		});
	}
	function formatearHora(hora) {
		if (!hora) return "";
		return hora.slice(0, 5);
	}
	function esAdministrador() {
		if (!user || !user.roles) return false;
		return user.roles.some((r) =>
			["Administrador", "Director", "Jefatura"].includes(r.nombre),
		);
	}
	function getIniciales() {
		if (!user) return "";
		const first = user.first_name?.charAt(0).toUpperCase() || "";
		const last = user.last_name?.charAt(0).toUpperCase() || "";
		return first + last;
	}
</script>
{#if showMandatoryPasswordChange}
	<CambioContrasenaObligatorio
		bind:showModal={showMandatoryPasswordChange}
		on:passwordChanged={() => {
			showMandatoryPasswordChange = false;
		}}
	/>
{/if}
{#if showEditProfile && user}
	<EditarPerfil
		bind:showModal={showEditProfile}
		{user}
		on:close={closeEditProfile}
		on:userUpdated={handleUserUpdated}
	/>
{/if}
<ModalUsuario
	bind:isOpen={showModalUsuario}
	{user}
	on:cerrar={toggleModalUsuario}
	on:editarPerfil={handleEditarPerfil}
	on:cerrarSesion={handleCerrarSesion}
/>
{#if isLoading}
	<div class="loading-container">
		<div class="loading-spinner"></div>
		<p>Cargando dashboard...</p>
	</div>
{:else if errorMessage}
	<div class="error-container">
		<h2>Error</h2>
		<p>{errorMessage}</p>
		<p>Redirigiendo al login...</p>
	</div>
{:else if user}
	<div class="dashboard-container">
		<!-- Header con usuario -->
		<header class="dashboard-header">
			<div class="header-content">
				<h1 class="dashboard-title">
					¡Bienvenido/a, {user.first_name}!
				</h1>
				<div class="header-actions">
                    <!-- Avatar clickeable -->
                    <button class="user-avatar" on:click={toggleModalUsuario}>
                        <div class="avatar-circle">
                            {getIniciales()}
                        </div>
                        <span class="avatar-name">{user.first_name}</span>
                        <span class="avatar-icon">▼</span>
                    </button>
                    <Notificaciones />
                </div>
			</div>
		</header>
		<!-- Layout principal: 2 columnas -->
		<div class="dashboard-layout">
			<!-- Columna izquierda: Tarjetas funcionales -->
			<div class="left-column">
				<!-- Tarjeta de Guardias -->
				<div class="dashboard-card guardias-card">
					<div class="card-header">
						<h2>🛡️ Mis Guardias</h2>
						<button
							class="btn-ir"
							on:click={() => goto("/guardias")}
						>
							Ir a Guardias →
						</button>
					</div>
					<div class="card-body">
						{#if loadingGuardias}
							<div class="card-loading">
								<div class="loading-spinner-small"></div>
								<span>Cargando...</span>
							</div>
						{:else}
							{@const proximasGuardias = getProximasGuardias()}
							{#if proximasGuardias.length > 0}
								<div class="guardias-list">
									{#each proximasGuardias as guardia}
										<div class="guardia-item">
											<div class="guardia-fecha">
												<span class="fecha-dia"
													>{new Date(
														guardia.fecha + "T00:00:00",
													).getDate()}</span
												>
												<span class="fecha-mes">
													{new Date(
														guardia.fecha + "T00:00:00",
													).toLocaleDateString(
														"es-AR",
														{ month: "short" },
													)}
												</span>
											</div>
											<div class="guardia-info">
												<span class="guardia-turno"
													>{guardia.turno ||
														"Turno completo"}</span
												>
												<span class="guardia-detalle">
													{guardia.hora_inicio
														? `${formatearHora(guardia.hora_inicio)} - ${formatearHora(guardia.hora_fin)}`
														: "Día completo"}
												</span>
											</div>
										</div>
									{/each}
								</div>
							{:else}
								<div class="empty-state">
									<span class="empty-icon">📅</span>
									<p>No tienes guardias próximas asignadas</p>
								</div>
							{/if}
						{/if}
					</div>
				</div>
				<!-- Tarjeta de Asistencia -->
				<div class="dashboard-card asistencia-card">
					<div class="card-header">
						<h2>Asistencia Hoy</h2>
						<button
							class="btn-ir"
							on:click={() => goto("/asistencia")}
						>
							Ir a Asistencia →
						</button>
					</div>
					<div class="card-body">
						{#if loadingAsistencia}
							<div class="card-loading">
								<div class="loading-spinner-small"></div>
								<span>Cargando...</span>
							</div>
						{:else if asistenciaHoy}
							{#if asistenciaHoy.es_dia_no_laborable}
								<div class="dia-no-laborable">
									<div class="icono-no-laborable">🏖️</div>
									<h3>Día No Laborable</h3>
									<p class="motivo-no-laborable">
										Hoy es <strong
											>{asistenciaHoy.motivo_no_laborable}</strong
										>
									</p>
									<p class="info-no-laborable">
										No se registra asistencia en este día.
									</p>
								</div>
							{:else}
								<div class="asistencia-estado">
									<div
										class="estado-item {asistenciaHoy.tiene_entrada
											? 'marcado'
											: 'pendiente'}"
									>
										<span class="estado-icon"
											>{asistenciaHoy.tiene_entrada
												? "✓"
												: "○"}</span
										>
										<div class="estado-info">
											<span class="estado-label"
												>Entrada</span
											>
											<span class="estado-hora">
												{asistenciaHoy.hora_entrada
													? formatearHora(
															asistenciaHoy.hora_entrada,
														)
													: "Sin marcar"}
											</span>
										</div>
									</div>
									<div
										class="estado-item {asistenciaHoy.tiene_salida
											? 'marcado'
											: 'pendiente'}"
									>
										<span class="estado-icon"
											>{asistenciaHoy.tiene_salida
												? "✓"
												: "○"}</span
										>
										<div class="estado-info">
											<span class="estado-label"
												>Salida</span
											>
											<span class="estado-hora">
												{asistenciaHoy.hora_salida
													? formatearHora(
															asistenciaHoy.hora_salida,
														)
													: "Sin marcar"}
											</span>
										</div>
									</div>
								</div>
							{/if}
						{:else}
							<div class="empty-state">
								<span class="empty-icon">📋</span>
								<p>No hay registro de asistencia hoy</p>
							</div>
						{/if}
					</div>
				</div>
				<!-- Botones de acceso rápido -->
				<div class="dashboard-card accesos-card">
					<div class="card-header">
						<h2>Accesos Rápidos</h2>
					</div>
					<div class="card-body">
						<div class="accesos-grid">
							{#if esAdministrador()}
							<button
								class="acceso-btn"
								on:click={() => goto("paneladmin/reportes")}
							>
								<span class="acceso-icon">📊</span>
								<span class="acceso-label">Reportes</span>
							</button>
							{/if}
							<button
								class="acceso-btn"
								on:click={() => goto("/guardias")}
							>
								<span class="acceso-icon">🛡️</span>
								<span class="acceso-label">Guardias</span>
							</button>
							{#if esAdministrador()}
								<button
									class="acceso-btn admin"
									on:click={() => goto("/paneladmin")}
								>
									<span class="acceso-icon">⚙️</span>
									<span class="acceso-label"
										>Administración</span
									>
								</button>
							{/if}
							<button
								class="acceso-btn"
								on:click={() => goto("/organigrama")}
							>
								<span class="acceso-icon">🏢</span>
								<span class="acceso-label">Organigrama</span>
							</button>
						</div>
					</div>
				</div>
			</div>
			<!-- Columna derecha: Calendario -->
			<div class="right-column">
				<div class="dashboard-card calendario-card">
					<div class="card-header">
						<h2>📅 Calendario</h2>
					</div>
					<div class="card-body calendario-body">
						<CalendarioBase {feriados} {guardias} />
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
<style>
	:global(*) {
		color-scheme: light only !important;
		-webkit-color-scheme: light !important;
	}
	.loading-container,
	.error-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 80vh;
		padding: 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.loading-spinner {
		border: 4px solid #f3f3f3;
		border-top: 4px solid #667eea;
		border-radius: 50%;
		width: 50px;
		height: 50px;
		animation: spin 1s linear infinite;
		margin-bottom: 1rem;
	}
	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}
	.dashboard-container {
		padding: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		overflow-x: hidden;
		background-color: #f8f9fa !important;
		color: #1a1a1a !important;
		color-scheme: light only !important;
	}
	@media (min-width: 768px) {
		.dashboard-container {
			padding: 2rem;
		}
	}
	.dashboard-header {
		margin-bottom: 1.5rem;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
        position: relative;
        z-index: 100;
	}
	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		max-width: 100%;
		width: 100%;
		margin: 0 auto;
		gap: 0.5rem;
		flex-wrap: wrap;
		box-sizing: border-box;
	}
    .header-actions {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
	@media (min-width: 1024px) {
		.header-content {
			max-width: 1400px;
		}
	}
	.dashboard-title {
		font-size: 1.5rem;
		font-weight: 700;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		margin: 0;
		position: relative;
		padding-bottom: 0.5rem;
		overflow: hidden;
		display: block;
		max-width: 100%;
		word-wrap: break-word;
		box-sizing: border-box;
	}
	@media (min-width: 640px) {
		.dashboard-title {
			font-size: 32px;
		}
	}
	@media (min-width: 1024px) {
		.dashboard-title {
			font-size: 40px;
		}
	}
	.dashboard-title::after {
		content: "";
		position: absolute;
		bottom: 0;
		left: 0;
		width: 80px;
		height: 4px;
		background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
		border-radius: 2px;
		animation: moveLine 2.2s linear infinite;
	}
	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
	}
	.user-avatar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: white !important;
		background-color: #ffffff !important;
		border: 2px solid #e9ecef;
		padding: 0.4rem 0.6rem;
		border-radius: 50px;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		flex-shrink: 0;
		max-width: 100%;
		overflow: hidden;
	}
	@media (min-width: 640px) {
		.user-avatar {
			gap: 0.75rem;
			padding: 0.5rem 1rem;
		}
	}
	.user-avatar:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		transform: translateY(-2px);
		border-color: #667eea;
		background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
	}
	.avatar-circle {
		width: 36px;
		height: 36px;
		border-radius: 50%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.9rem;
		font-weight: bold;
		color: white !important;
		flex-shrink: 0;
	}
	@media (min-width: 640px) {
		.avatar-circle {
			width: 40px;
			height: 40px;
			font-size: 1rem;
		}
	}
	.avatar-name {
		font-weight: 600;
		font-size: 0.875rem;
		color: #1a1a1a !important;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 120px;
		display: none;
	}
	@media (min-width: 640px) {
		.avatar-name {
			display: block;
			font-size: 16px;
		}
	}
	.avatar-icon {
		font-size: 0.7rem;
		color: #6c757d;
	}
	.dashboard-layout {
		max-width: 100%;
		width: 100%;
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr;
		gap: 0.75rem;
		box-sizing: border-box;
		overflow-x: hidden;
	}
	@media (min-width: 1024px) {
		.dashboard-layout {
			max-width: 1400px;
			grid-template-columns: 380px 1fr;
			gap: 2rem;
		}
	}
	.left-column {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		overflow-x: hidden;
	}
	@media (min-width: 768px) {
		.left-column {
			gap: 1.5rem;
		}
	}
	.right-column {
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		overflow-x: hidden;
	}
	.dashboard-card {
		background: white !important;
		background-color: #ffffff !important;
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
		overflow: hidden;
		transition: all 0.3s;
		border: 1px solid #e9ecef;
		position: relative;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		color: #1a1a1a !important;
		margin: 0;
		min-width: 0;
	}
	@media (min-width: 768px) {
		.dashboard-card {
			border-radius: 16px;
		}
	}
	.dashboard-card::before {
		content: "";
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 4px;
		background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
	}
	.guardias-card::before {
		background: linear-gradient(90deg, #ffc107 0%, #ff9800 100%);
	}
	.asistencia-card::before {
		background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
	}
	.accesos-card::before {
		background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
	}
	.dashboard-card:hover {
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
		transform: translateY(-4px);
		border-color: #667eeabd;
	}
	.card-header {
		padding: 0.75rem;
		border-bottom: 2px solid #f1f3f5;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
		gap: 0.5rem;
		flex-wrap: wrap;
		box-sizing: border-box;
	}
	@media (min-width: 768px) {
		.card-header {
			padding: 1.5rem;
		}
	}
	.card-header h2 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: #1a1a1a !important;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	@media (min-width: 640px) {
		.card-header h2 {
			font-size: 1.1rem;
		}
	}
	@media (min-width: 1024px) {
		.card-header h2 {
			font-size: 1.25rem;
		}
	}
	.btn-ir {
		padding: 0.35rem 0.6rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white !important;
		border: none;
		border-radius: 8px;
		font-size: 0.7rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		white-space: nowrap;
		flex-shrink: 0;
	}
	@media (min-width: 640px) {
		.btn-ir {
			padding: 0.5rem 1rem;
			font-size: 0.85rem;
		}
	}
	@media (min-width: 1024px) {
		.btn-ir {
			font-size: 0.9rem;
		}
	}
	.btn-ir:hover {
		transform: translateX(4px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}
	.card-body {
		padding: 0.75rem;
		box-sizing: border-box;
		width: 100%;
		max-width: 100%;
		overflow-x: hidden;
		min-width: 0;
	}
	@media (min-width: 768px) {
		.card-body {
			padding: 1.5rem;
		}
	}
	.card-loading {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		padding: 2rem;
		color: #6c757d;
	}
	.loading-spinner-small {
		border: 3px solid #f3f3f3;
		border-top: 3px solid #667eea;
		border-radius: 50%;
		width: 24px;
		height: 24px;
		animation: spin 1s linear infinite;
	}
	.empty-state {
		text-align: center;
		padding: 2rem;
		color: #6c757d;
	}
	.empty-icon {
		font-size: 3rem;
		display: block;
		margin-bottom: 1rem;
	}
	.guardias-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	.guardia-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		background: linear-gradient(
			135deg,
			#fff7e6 0%,
			#fff3dc 100%
		) !important;
		border-radius: 8px;
		border-left: 4px solid #ffc107;
		box-sizing: border-box;
		width: 100%;
		max-width: 100%;
	}
	@media (min-width: 640px) {
		.guardia-item {
			gap: 1rem;
			padding: 1rem;
			border-radius: 12px;
		}
	}
	.guardia-fecha {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: white !important;
		padding: 0.5rem;
		border-radius: 8px;
		min-width: 50px;
		max-width: 60px;
		flex-shrink: 0;
	}
	@media (min-width: 640px) {
		.guardia-fecha {
			padding: 0.75rem;
			min-width: 60px;
		}
	}
	.fecha-dia {
		font-size: 1.25rem;
		font-weight: 700;
		color: #1a1a1a !important;
		line-height: 1;
	}
	@media (min-width: 640px) {
		.fecha-dia {
			font-size: 1.5rem;
		}
	}
	.fecha-mes {
		font-size: 0.65rem;
		color: #6c757d !important;
		text-transform: uppercase;
	}
	@media (min-width: 640px) {
		.fecha-mes {
			font-size: 0.75rem;
		}
	}
	.guardia-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
		min-width: 0;
		overflow: hidden;
	}
	.guardia-turno {
		font-weight: 600;
		color: #1a1a1a !important;
		font-size: 0.9rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	@media (min-width: 640px) {
		.guardia-turno {
			font-size: 1rem;
		}
	}
	.guardia-detalle {
		font-size: 0.75rem;
		color: #6c757d !important;
	}
	@media (min-width: 640px) {
		.guardia-detalle {
			font-size: 0.875rem;
		}
	}
	.asistencia-estado {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		width: 100%;
	}
	@media (min-width: 640px) {
		.asistencia-estado {
			flex-direction: row;
			gap: 1rem;
		}
	}
	.estado-item {
		flex: 1;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		border-radius: 8px;
		border: 2px solid;
		box-sizing: border-box;
		width: 100%;
		min-width: 0;
	}
	@media (min-width: 640px) {
		.estado-item {
			gap: 1rem;
			padding: 1rem;
			border-radius: 12px;
		}
	}
	.estado-item.marcado {
		background: linear-gradient(
			135deg,
			#d4edda 0%,
			#c3e6cb 100%
		) !important;
		border-color: #28a745 !important;
	}
	.estado-item.pendiente {
		background: linear-gradient(
			135deg,
			#f8d7da 0%,
			#f5c6cb 100%
		) !important;
		border-color: #dc3545 !important;
	}
	.estado-icon {
		font-size: 1.25rem;
		font-weight: bold;
		flex-shrink: 0;
	}
	@media (min-width: 640px) {
		.estado-icon {
			font-size: 1.5rem;
		}
	}
	.estado-item.marcado .estado-icon {
		color: #28a745 !important;
	}
	.estado-item.pendiente .estado-icon {
		color: #dc3545 !important;
	}
	.estado-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
		min-width: 0;
	}
	.estado-label {
		font-size: 0.65rem;
		color: #6c757d !important;
		text-transform: uppercase;
		font-weight: 600;
	}
	@media (min-width: 640px) {
		.estado-label {
			font-size: 0.75rem;
		}
	}
	.estado-hora {
		font-weight: 600;
		font-size: 0.9rem;
		color: #1a1a1a !important;
	}
	@media (min-width: 640px) {
		.estado-hora {
			font-size: 1rem;
		}
	}
	.accesos-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 0.75rem;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		overflow-x: hidden;
	}
	@media (min-width: 640px) {
		.accesos-grid {
			gap: 1rem;
		}
	}
	@media (min-width: 1024px) {
		.accesos-grid {
			grid-template-columns: 1fr 1fr;
			gap: 1.5rem;
		}
	}
	.acceso-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 1rem 0.5rem;
		background: white !important;
		border: 2px solid #e9ecef;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.2s;
		text-decoration: none;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		box-sizing: border-box;
		width: 100%;
		max-width: 100%;
		min-width: 0;
	}
	@media (min-width: 640px) {
		.acceso-btn {
			gap: 0.5rem;
			padding: 1.5rem 1rem;
			border-radius: 12px;
		}
	}
	.acceso-btn:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
		border-color: #667eea;
	}
	.acceso-btn.admin {
		background: linear-gradient(
			135deg,
			#fff7e6 0%,
			#fff3dc 100%
		) !important;
		border-color: #ffc107 !important;
	}
	.acceso-icon {
		font-size: 1.5rem;
	}
	@media (min-width: 640px) {
		.acceso-icon {
			font-size: 2rem;
		}
	}
	.acceso-label {
		font-size: 0.75rem;
		color: #1a1a1a !important;
		text-align: center;
		word-wrap: break-word;
	}
	@media (min-width: 640px) {
		.acceso-label {
			font-size: 0.9rem;
		}
	}
	.calendario-card::before {
		background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
	}
	.calendario-body {
		padding: 0.5rem !important;
		overflow-x: auto;
		-webkit-overflow-scrolling: touch;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		min-width: 0;
	}
	.calendario-body :global(.calendar-container) {
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		min-width: 0;
	}
	.calendario-body :global(.calendar-grid) {
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
	}
	.calendario-body :global(.calendar-day) {
		min-width: 0;
		box-sizing: border-box;
	}
	.calendario-card {
		overflow: hidden;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		min-width: 0;
	}
	@media (min-width: 640px) {
		.calendario-body {
			padding: 1rem !important;
		}
	}
	@media (max-width: 480px) {
		.accesos-grid {
			grid-template-columns: 1fr;
		}
		.dashboard-header {
			margin-bottom: 1rem;
		}
	}
	.dia-no-laborable {
		text-align: center;
		padding: 1.5rem;
		background: linear-gradient(135deg, #e3f2fd 0%, #f1f8e9 100%);
		border-radius: 12px;
		border: 2px solid #4caf50;
	}
	.icono-no-laborable {
		font-size: 3rem;
		margin-bottom: 0.5rem;
	}
	.dia-no-laborable h3 {
		color: #2e7d32;
		margin: 0 0 0.5rem 0;
		font-size: 1.1rem;
		font-weight: 600;
	}
	.motivo-no-laborable {
		font-size: 1rem;
		margin-bottom: 0.25rem;
		color: #2e7d32;
	}
	.motivo-no-laborable strong {
		color: #1b5e20;
		font-weight: 600;
	}
	.info-no-laborable {
		font-size: 0.9rem;
		color: #558b2f;
		margin: 0;
	}
</style>
