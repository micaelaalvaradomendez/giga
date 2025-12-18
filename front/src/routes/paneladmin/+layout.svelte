<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { page } from "$app/stores";
	import AuthService from "$lib/login/authService.js";
	import ModalAlert from "$lib/componentes/ModalAlert.svelte";
	import { modalAlert, showAlert } from "$lib/stores/modalAlertStore.js";

	let authorized = false;
	let checking = true;

	// Rutas permitidas por rol
	const routePermissions = {
		"agente avanzado": [
			"/paneladmin",
			"/paneladmin/usuarios",
			"/paneladmin/licencias",
			"/paneladmin/asistencias",
			"/paneladmin/reportes",
		],
		agente: ["/paneladmin", "/paneladmin/reportes"],
		jefatura: [
			"/paneladmin",
			"/paneladmin/usuarios",
			"/paneladmin/organigrama",
			"/paneladmin/asistencias",
			"/paneladmin/licencias",
			"/paneladmin/guardias",
			"/paneladmin/guardias/compensaciones",
			"/paneladmin/guardias/planificador",
			"/paneladmin/guardias/aprobaciones",
			"/paneladmin/auditoria",
		],
		director: [
			"/paneladmin",
			"/paneladmin/usuarios",
			"/paneladmin/organigrama",
			"/paneladmin/asistencias",
			"/paneladmin/licencias",
			"/paneladmin/guardias",
			"/paneladmin/guardias/compensaciones",
			"/paneladmin/guardias/planificador",
			"/paneladmin/guardias/aprobaciones",
			"/paneladmin/parametros",
			"/paneladmin/auditoria",
		],
		administrador: null, // null = acceso a todo
	};

	function checkRouteAccess(userRoles, currentPath) {
		// Administrador tiene acceso a todo
		if (userRoles.includes("administrador")) {
			return true;
		}

		// Verificar en orden de jerarquía (director > jefatura > agente avanzado > agente)
		const roleHierarchy = ["director", "jefatura", "agente avanzado", "agente"];
		
		for (const role of roleHierarchy) {
			if (userRoles.includes(role)) {
				const allowedRoutes = routePermissions[role];
				if (allowedRoutes === null) return true; // acceso a todo
				
				// Verificar si la ruta actual está en las permitidas
				return allowedRoutes.some(route => {
					// Si la ruta permitida es el panel base, solo permitir acceso exacto
					if (route === "/paneladmin") {
						return currentPath === route;
					}
					// Para otras rutas, permitir la ruta exacta o sus subrutas
					return currentPath === route || currentPath.startsWith(route + "/");
				});
			}
		}
		
		return false;
	}

	onMount(async () => {
		try {
			const userResponse = await AuthService.getCurrentUserData();

			if (!userResponse?.success || !userResponse.data?.success) {
				await showAlert("Usuario no autorizado", "error", "Acceso Denegado");
				goto("/");
				return;
			}

			const userInfo = userResponse.data.data;
			const userRoles = Array.isArray(userInfo.roles)
				? userInfo.roles
						.map((rol) => (typeof rol === "string" ? rol : rol.nombre))
						.filter(Boolean)
						.map((r) => r.toLowerCase())
				: [];

			// Roles que tienen acceso al panel admin
			const allowedRoles = [
				"administrador",
				"jefatura",
				"director",
				"agente avanzado",
				"agente",
			];
			const hasGeneralAccess = userRoles.some((rol) => allowedRoles.includes(rol));

			if (!hasGeneralAccess) {
				await showAlert(
					"No tienes permisos para acceder al panel de administración",
					"error",
					"Acceso Denegado",
				);
				goto("/inicio");
				return;
			}

			// Verificar acceso a la ruta específica
			const currentPath = $page.url.pathname;
			const hasRouteAccess = checkRouteAccess(userRoles, currentPath);

			if (!hasRouteAccess) {
				await showAlert(
					"No tienes permisos para acceder a esta sección",
					"error",
					"Acceso Denegado",
				);
				if (
					userRoles.includes("agente avanzado") ||
					userRoles.includes("agente") ||
					userRoles.includes("jefatura") ||
					userRoles.includes("director")
				) {
					goto("/inicio");
				} else {
					goto("/paneladmin");
				}
				return;
			}

			authorized = true;
		} catch (error) {
			await showAlert("Error de autenticación", "error", "Acceso Denegado");
			goto("/");
		} finally {
			checking = false;
		}
	});
</script>

{#if checking}
	<div class="loading-container">
		<div class="spinner"></div>
		<p>Verificando acceso...</p>
	</div>
{:else if authorized}
	<slot />
{/if}

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
	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
		gap: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}
	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid #f3f4f6;
		border-top: 3px solid #3b82f6;
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
</style>
