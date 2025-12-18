<script>
	import { onMount, onDestroy, tick } from "svelte";
	import { goto } from "$app/navigation";
	import AuthService from "$lib/login/authService.js";
	import AuditService from "$lib/services/auditService.js";
	import ModalAlert from "$lib/componentes/ModalAlert.svelte";
	import { modalAlert, showAlert } from "$lib/stores/modalAlertStore.js";

	// Cleanup references for event listeners
	let containerRef = null;
	let initTimeoutId = null;
	// Store card references and their event handlers for cleanup
	let cardHandlers = [];

	const allModules = [
		{
			name: "Usuarios",
			path: "/paneladmin/usuarios",
			description: "Gestionar personal y usuarios",
		},
		{
			name: "Organigrama",
			path: "/paneladmin/organigrama",
			description: "Definir áreas y jerarquías",
		},
		{
			name: "Roles",
			path: "/paneladmin/roles",
			description: "Configurar roles de acceso",
		},
		{
			name: "Asistencias",
			path: "/paneladmin/asistencias",
			description: "Revisar registros de asistencia",
		},
		{
			name: "Licencias",
			path: "/paneladmin/licencias",
			description: "Administrar licencias y novedades",
		},
		{
			name: "Guardias",
			path: "/paneladmin/guardias",
			description: "Planificar guardias y turnos",
		},
		{
			name: "Feriados",
			path: "/paneladmin/feriados",
			description: "Gestionar días no laborables",
		},
		{
			name: "Reportes Generales",
			path: "/paneladmin/reportes",
			description: "Generar informes del sistema",
		},
		{
			name: "Parámetros",
			path: "/paneladmin/parametros",
			description:
				"Ajustar la configuración global de Areas y hora de entrada y salida general",
		},
		{
			name: "Auditoría",
			path: "/paneladmin/auditoria",
			description: "Rastrear cambios en el sistema",
		},
	];

	// Modulos visibles segun rol
	let modules = [];

	onMount(async () => {
		try {
			const userResponse = await AuthService.getCurrentUserData();

			// No autenticado -> mostrar mensaje y redirigir a /
			if (!userResponse?.success || !userResponse.data?.success) {
				// Registrar intento sin autenticación
				await AuditService.logUnauthorizedAccess({
					ruta: "/paneladmin",
					accion: "acceso_sin_autenticacion",
					rol: "desconocido",
					userId: 0,
				});
				await showAlert("Usuario no autorizado", "error", "Acceso Denegado");
				goto("/");
				return;
			}

			const userInfo = userResponse.data.data;

			// Determinar roles
			const userRoles = Array.isArray(userInfo.roles)
				? userInfo.roles
						.map((rol) =>
							typeof rol === "string" ? rol : rol.nombre,
						)
						.filter(Boolean)
						.map((r) => r.toLowerCase())
				: [];

			const isAdmin = userRoles.includes("administrador");
			const isJefatura =
				userRoles.includes("jefatura") ||
				userRoles.includes("director");
			const isAgenteAvanzado = userRoles.includes("agente avanzado");

			if (isAdmin) {
				// Administrador: TODO
				modules = allModules;
			} else if (isJefatura) {
				// Director/Jefatura: TODO menos Auditoría, Roles, Feriados, Parámetros y Reportes
				const allowedPaths = [
					"/paneladmin/usuarios",
					"/paneladmin/organigrama",
					"/paneladmin/asistencias",
					"/paneladmin/licencias",
					"/paneladmin/guardias",
					// Excluidos: auditoria, roles, feriados, parametros, reportes
				];
				modules = allModules.filter((m) =>
					allowedPaths.includes(m.path),
				);
			} else if (isAgenteAvanzado) {
				// Agente Avanzado: solo Usuarios, Licencias y Asistencias
				const allowedPaths = [
					"/paneladmin/usuarios",
					"/paneladmin/licencias",
					"/paneladmin/asistencias",
				];
				modules = allModules.filter((m) =>
					allowedPaths.includes(m.path),
				);
			} else {
				// Agente: sin acceso - registrar en auditoría
				await AuditService.logUnauthorizedAccess({
					ruta: "/paneladmin",
					accion: "acceso_denegado_rol_insuficiente",
					rol: userRoles[0] || "agente",
					userId: userInfo.id,
				});
				await showAlert("Usuario no autorizado", "error", "Acceso Denegado");
				goto("/inicio");
				return;
			}

			// Registrar acceso exitoso
			await AuditService.logSuccessfulAccess({
				ruta: "/paneladmin",
				rol: userRoles[0] || "desconocido",
				userId: userInfo.id,
			});

			// Esperar a que Svelte actualice el DOM con los módulos
			await tick();

			// Usar setTimeout para asegurar que el DOM esté completamente renderizado
			initTimeoutId = setTimeout(() => {
				// Inicializar animaciones si hay módulos visibles
				const cards = document.querySelectorAll(".module-card");
				const container = document.querySelector(".modules-space");

				if (container && cards.length) {
					// Store reference for cleanup
					containerRef = container;
					
					// Optimized approach: attach handlers per card with cached rect
					cards.forEach((card) => {
						let rect = null;
						
						const enterHandler = () => {
							// Cache bounding rect on pointer enter (only recalculate when entering)
							rect = card.getBoundingClientRect();
						};
						
						const leaveHandler = () => {
							rect = null;
							card.style.removeProperty("--mouse-x");
							card.style.removeProperty("--mouse-y");
						};
						
						const moveHandler = (e) => {
							if (!rect) rect = card.getBoundingClientRect(); // Fallback
							const x = e.clientX - rect.left;
							const y = e.clientY - rect.top;
							// Use requestAnimationFrame to batch style updates
							requestAnimationFrame(() => {
								card.style.setProperty("--mouse-x", `${x}px`);
								card.style.setProperty("--mouse-y", `${y}px`);
							});
						};
						
						card.addEventListener("pointerenter", enterHandler);
						card.addEventListener("pointerleave", leaveHandler);
						card.addEventListener("pointermove", moveHandler);
						
						// Store handlers for cleanup
						cardHandlers.push({
							card,
							enterHandler,
							leaveHandler,
							moveHandler
						});
					});
				}
			}, 100);
		} catch (error) {
			await showAlert("Usuario no autorizado", "error", "Acceso Denegado");
			goto("/");
		}
	});

	// Cleanup event listeners and timers on component destroy
	onDestroy(() => {
		if (initTimeoutId) {
			clearTimeout(initTimeoutId);
		}
		// Clean up all card event handlers
		cardHandlers.forEach(({ card, enterHandler, leaveHandler, moveHandler }) => {
			card.removeEventListener("pointerenter", enterHandler);
			card.removeEventListener("pointerleave", leaveHandler);
			card.removeEventListener("pointermove", moveHandler);
		});
		cardHandlers = [];
	});
</script>

<div class="dashboard-welcome">
	<h1>Panel de Administración GIGA</h1>
</div>

<div class="modules-space">
	{#each modules as module}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="module-card" on:click={() => (window.location.href = module.path)}>
			<div class="module-info">
				<div class="text-content">
					<h2>{module.name}</h2>
					<p>{module.description}</p>
				</div>
				<div class="arrow-icon">
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
						<path d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"></path>
					</svg>
				</div>
			</div>
		</div>
	{/each}
</div>

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
	.dashboard-welcome {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 20px;
		margin: 5px auto 25px auto;
		max-width: 1200px;
		min-height: 80px;
		border-radius: 28px;
		overflow: visible;
		text-align: center;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
	}

	.dashboard-welcome::before {
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
		z-index: 0;
		pointer-events: none;
	}

	.dashboard-welcome h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 20px;
		letter-spacing: 0.2px;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
		position: relative;
		z-index: 1;
		padding-bottom: 12px;
		display: inline-block;
		max-width: 100%;
		word-wrap: break-word;
		white-space: normal;
		line-height: 1.4;
		overflow: hidden;
	}

	@media (min-width: 480px) {
		.dashboard-welcome h1 {
			font-size: 24px;
		}
	}

	@media (min-width: 640px) {
		.dashboard-welcome h1 {
			font-size: 28px;
			display: inline-block;
		}
	}

	@media (min-width: 768px) {
		.dashboard-welcome h1 {
			font-size: 30px;
		}
	}

	.dashboard-welcome h1::after {
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

	.modules-space {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		width: 90%;
		display: grid;
		margin-top: 20px;
		margin-right: auto;
		margin-left: auto;
		grid-template-rows: repeat(3, 1fr);
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
		padding-bottom: 40px;
	}

	.module-card {
		--color: 25 90% 60%;
		display: flex;
		flex-direction: column;
		position: relative;
		overflow: hidden;
		justify-content: flex-start;
		align-items: flex-start;
		background: linear-gradient(135deg, #fffcf8 0%, #fff8f0 100%);
		border: 2px solid rgba(224, 152, 27, 0.35);
		border-radius: 12px;
		padding: 1.25rem 1.5rem;
		text-decoration: none;
		color: inherit;
		transition: all 0.3s ease;
		min-height: 100px;
		box-shadow: 0 2px 10px rgba(224, 152, 27, 0.1);
		isolation: isolate;
		max-width: 100%;
		box-sizing: border-box;
		cursor: pointer;
	}

	.module-card::before {
		content: "";
		position: absolute;
		inset: 0;
		z-index: 0;
		pointer-events: none;
		border-radius: inherit;
		background: radial-gradient(
			500px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
			hsl(var(--color) / 0.4),
			rgba(255, 255, 255, 0.03) 40%,
			transparent 70%
		);

		opacity: 0;
		transition:
			opacity 0.28s ease,
			transform 0.28s ease;
		transform: scale(1.05);
	}

	.module-card:hover::before {
		opacity: 1;
		transform: scale(1);
	}

	.module-card:hover {
		transform: translateY(-8px);
		cursor: pointer;
	}

	.module-card .module-info {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
		width: 100%;
		height: 100%;
	}

	.module-info .text-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.module-info h2 {
		font-size: 1.3rem;
		margin: 0;
		font-weight: 600;
		color: #2c3e50;
		line-height: 1.2;
	}

	.module-info p {
		font-size: 0.9rem;
		color: #6c757d;
		line-height: 1.3;
		margin: 0;
	}

	.arrow-icon {
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
		border: 2px solid #dee2e6;
		flex-shrink: 0;
		transition: all 0.3s ease;
	}

	.arrow-icon svg {
		width: 20px;
		height: 20px;
		fill: #6c757d;
		transition: all 0.3s ease;
	}

	.module-card:hover .arrow-icon {
		background: linear-gradient(135deg, #e0981b 0%, #d4850f 100%);
		border-color: #e0981b;
		transform: translateX(3px);
	}

	.module-card:hover .arrow-icon svg {
		fill: white;
	}

	.module-info button {
		display: block;
		position: relative;
		width: 56px;
		height: 56px;
		margin: 0;
		overflow: hidden;
		outline: none;
		background-color: transparent;
		cursor: pointer;
		border: 0;
		flex-shrink: 0;
	}

	.module-info button:before,
	.module-info button:after {
		content: "";
		position: absolute;
		border-radius: 50%;
		inset: 7px;
	}

	.module-info button:before {
		border: 4px solid #a39e98;
		transition:
			opacity 0.4s cubic-bezier(0.77, 0, 0.175, 1) 80ms,
			transform 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) 80ms;
	}

	.module-info button:after {
		border: 4px solid #e0981b;
		transform: scale(1.3);
		transition:
			opacity 0.4s cubic-bezier(0.165, 0.84, 0.44, 1),
			transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
		opacity: 0;
	}

	.module-info button:hover:before,
	.module-info button:focus:before {
		opacity: 1;
		transform: scale(1);
		transition:
			opacity 0.4s cubic-bezier(0.77, 0, 0.175, 1) 80ms,
			transform 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) 80ms;
	}

	.module-info button:hover:after,
	.module-info button:focus:after {
		opacity: 1;
		transform: scale(1);
		transition:
			opacity 0.4s cubic-bezier(0.77, 0, 0.175, 1) 80ms,
			transform 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) 80ms;
	}

	.button-box {
		display: flex;
		position: absolute;
		top: 0;
		left: 0;
	}

	.button-elem {
		display: block;
		width: 20px;
		height: 20px;
		margin: 17px 18px 0 18px;
		fill: #24201c;
	}

	.button-elem svg {
		width: 100%;
		height: 100%;
		fill: inherit;
	}

	.module-info button:hover .button-elem {
		fill: #533e19;
	}

	.module-info button:hover .button-box,
	.module-info button:focus .button-box {
		transition: 0.4s;
		transform: translateX(-56px);
	}

	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
	}

	@media (max-width: 768px) {
		.modules-space {
			grid-template-columns: 1fr;
			width: 95%;
			gap: 12px;
			padding-bottom: 20px;
		}
		
		.module-card {
			padding: 1rem;
			min-height: auto;
			width: 100%;
			box-sizing: border-box;
		}
		
		.module-info {
			flex-direction: row;
			align-items: center;
		}
		
		.module-info h2 {
			font-size: 1rem;
		}

		.module-info p {
			font-size: 0.8rem;
		}
		
		.module-info button {
			width: 44px;
			height: 44px;
		}
		
		.button-elem {
			margin: 12px 12px 0 12px;
		}

		.dashboard-welcome {
			margin: 10px 10px 20px 10px;
			padding: 20px 15px;
			border-radius: 20px;
		}

		.dashboard-welcome h1 {
			font-size: 18px;
			line-height: 1.3;
		}
	}
	
	@media (max-width: 480px) {
		.dashboard-welcome {
			margin: 8px;
			padding: 16px 12px;
			border-radius: 16px;
		}
		
		.dashboard-welcome h1 {
			font-size: 20px;
		}
		
		.modules-space {
			width: 100%;
			padding: 0 12px 30px 12px;
			gap: 10px;
			box-sizing: border-box;
			overflow-x: hidden;
		}
		
		.module-card {
			padding: 12px;
			width: 100%;
			box-sizing: border-box;
		}
		
		.module-info h2 {
			font-size: 0.95rem;
		}
		
		.module-info p {
			font-size: 0.75rem;
		}
	}
</style>
