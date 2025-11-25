<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import AuthService from "../../lib/login/authService.js";
	import ModalUsuario from "../../lib/componentes/usuario/ModalUsuario.svelte";
	import EditarPerfil from "../../lib/componentes/EditarPerfil.svelte";
	import CambioContrasenaObligatorio from "../../lib/componentes/CambioContrasenaObligatorio.svelte";
	import CalendarioBase from "../../lib/componentes/calendarioBase.svelte";
	import { guardiasService } from "../../lib/services.js";

	let user = null;
	let isLoading = true;
	let errorMessage = "";
	let showModalUsuario = false;
	let showEditProfile = false;
	let showMandatoryPasswordChange = false;
	let feriados = [];
	let guardias = [];
	let loadingFeriados = false;
	let loadingGuardias = false;
	let asistenciaHoy = null;
	let loadingAsistencia = false;

	onMount(async () => {
		try {
			const sessionCheck = await AuthService.checkSession();

			if (sessionCheck.authenticated) {
				user = sessionCheck.user;

				if (
					sessionCheck.requires_password_change ||
					AuthService.requiresPasswordChange()
				) {
					showMandatoryPasswordChange = true;
				}

				await Promise.all([
					cargarFeriados(),
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

	async function cargarFeriados() {
		try {
			loadingFeriados = true;
			const response = await guardiasService.getFeriados();
			feriados = response.data?.results || response.data || [];
		} catch (error) {
			console.error("Error cargando feriados:", error);
			feriados = [];
		} finally {
			loadingFeriados = false;
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
			const response = await fetch("/api/asistencia/estado/", {
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
				const fechaGuardia = new Date(g.fecha);
				fechaGuardia.setHours(0, 0, 0, 0);
				return fechaGuardia >= hoy;
			})
			.sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
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

				<!-- Avatar clickeable -->
				<button class="user-avatar" on:click={toggleModalUsuario}>
					<div class="avatar-circle">
						{getIniciales()}
					</div>
					<span class="avatar-name">{user.first_name}</span>
					<span class="avatar-icon">▼</span>
				</button>
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
														guardia.fecha,
													).getDate()}</span
												>
												<span class="fecha-mes">
													{new Date(
														guardia.fecha,
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
										<span class="estado-label">Entrada</span
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
										<span class="estado-label">Salida</span>
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
							<button
								class="acceso-btn"
								on:click={() => goto("/reportes")}
							>
								<span class="acceso-icon">📊</span>
								<span class="acceso-label">Reportes</span>
							</button>
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
				<div class="card-body calendario-body">
					<CalendarioBase {feriados} {guardias} />
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.loading-container,
	.error-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 80vh;
		padding: 2rem;
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
		min-height: 100vh;
		padding: 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.dashboard-header {
		margin-bottom: 2rem;
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		max-width: 1400px;
		margin: 0 auto;
	}

	.dashboard-title {
		font-size: 40px;
		font-weight: 700;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		margin: 10px;
		position: relative;
		padding-bottom: 0.5rem;
		overflow: hidden;
		display: inline-block;
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
		gap: 0.75rem;
		background: white;
		border: 2px solid #e9ecef;
		padding: 0.5rem 1rem;
		border-radius: 50px;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.user-avatar:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		transform: translateY(-2px);
		border-color: #667eea;
		background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
	}

	.avatar-circle {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1rem;
		font-weight: bold;
		color: white;
	}

	.avatar-name {
		font-weight: 600;
		font-size: 16px;
		color: #1a1a1a;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.avatar-icon {
		font-size: 0.7rem;
		color: #6c757d;
	}

	.dashboard-layout {
		max-width: 1400px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: 380px 1fr;
		gap: 2rem;
	}

	.left-column {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.right-column {
		display: flex;
		flex-direction: column;
	}

	.dashboard-card {
		background: white;
		border-radius: 16px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
		overflow: hidden;
		transition: all 0.3s;
		border: 1px solid #e9ecef;
		position: relative;
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
		padding: 1.5rem;
		border-bottom: 2px solid #f1f3f5;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
	}

	.card-header h2 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #1a1a1a;
	}

	.btn-ir {
		padding: 0.5rem 1rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-ir:hover {
		transform: translateX(4px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}

	.card-body {
		padding: 1.5rem;
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

	/* Guardias */
	.guardias-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.guardia-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: linear-gradient(135deg, #fff7e6 0%, #fff3dc 100%);
		border-radius: 12px;
		border-left: 4px solid #ffc107;
	}

	.guardia-fecha {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: white;
		padding: 0.75rem;
		border-radius: 8px;
		min-width: 60px;
	}

	.fecha-dia {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1a1a1a;
		line-height: 1;
	}

	.fecha-mes {
		font-size: 0.75rem;
		color: #6c757d;
		text-transform: uppercase;
	}

	.guardia-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.guardia-turno {
		font-weight: 600;
		color: #1a1a1a;
	}

	.guardia-detalle {
		font-size: 0.875rem;
		color: #6c757d;
	}

	/* Asistencia */
	.asistencia-estado {
		display: flex;
		gap: 1rem;
	}

	.estado-item {
		flex: 1;
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		border-radius: 12px;
		border: 2px solid;
	}

	.estado-item.marcado {
		background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
		border-color: #28a745;
	}

	.estado-item.pendiente {
		background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
		border-color: #dc3545;
	}

	.estado-icon {
		font-size: 1.5rem;
		font-weight: bold;
	}

	.estado-item.marcado .estado-icon {
		color: #28a745;
	}

	.estado-item.pendiente .estado-icon {
		color: #dc3545;
	}

	.estado-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.estado-label {
		font-size: 0.75rem;
		color: #6c757d;
		text-transform: uppercase;
		font-weight: 600;
	}

	.estado-hora {
		font-weight: 600;
		font-size: 1rem;
		color: #1a1a1a;
	}

	/* Accesos rápidos */
	.accesos-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
	}

	.acceso-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 1.5rem 1rem;
		background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
		border: 2px solid #e0e0e0;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 600;
	}

	.acceso-btn:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
		border-color: #667eea;
	}

	.acceso-btn.admin {
		background: linear-gradient(135deg, #fff7e6 0%, #fff3dc 100%);
		border-color: #ffc107;
	}

	.acceso-icon {
		font-size: 2rem;
	}

	.acceso-label {
		font-size: 0.9rem;
		color: #1a1a1a;
	}

	/* Calendario */
	.calendario-body {
		padding: 1rem;
	}

	@media (max-width: 1024px) {
		.dashboard-layout {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 768px) {
		.dashboard-container {
			padding: 1rem;
		}

		.dashboard-title {
			font-size: 1.5rem;
		}

		.user-avatar {
			padding: 0.5rem;
		}

		.avatar-name {
			display: none;
		}

		.accesos-grid {
			grid-template-columns: 1fr;
		}

		.asistencia-estado {
			flex-direction: column;
		}
	}
</style>
