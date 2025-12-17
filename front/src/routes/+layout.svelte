<script>
	import { browser } from '$app/environment';
	import { onMount } from "svelte";
	
	let Navbar, Footer, Menu, Breadcrumbs, AuthService;
	let isMenuOpen = false;
	let componentsLoaded = false;

	onMount(async () => {
		if (browser) {
			try {
				// Importación dinámica de todos los componentes
				const [navbarModule, footerModule, menuModule, breadcrumbsModule, authModule] = await Promise.all([
					import("$lib/componentes/navbar.svelte"),
					import("$lib/componentes/footer.svelte"),
					import("$lib/componentes/menu.svelte"),
					import("$lib/componentes/breadcrumbs.svelte"),
					import("$lib/login/authService.js")
				]);
				
				Navbar = navbarModule.default;
				Footer = footerModule.default;
				Menu = menuModule.default;
				Breadcrumbs = breadcrumbsModule.default;
				AuthService = authModule.AuthService;
				
				componentsLoaded = true;
				
				// Verificar sesión
				await AuthService.checkSession();
			} catch (error) {
				console.error('Error loading components:', error);
				// En caso de error, mostrar mensaje al usuario
				// Los componentes no se cargarán y se mostrará el loading spinner
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" />
	<title>Sistema GIGA</title>
	<meta
		name="description"
		content="Sistema de Gestión Integral de Guardias y Asistencia"
	/>
</svelte:head>

{#if componentsLoaded}
	<svelte:component this={Navbar} />
	<svelte:component this={Menu} bind:isActive={isMenuOpen} />
	
	<div class="layout-container" class:menu-open={isMenuOpen}>
		<main>
			<div class="main-content-wrapper">
				<svelte:component this={Breadcrumbs} />
				<slot />
			</div>
		</main>
	</div>
	
	<svelte:component this={Footer} />
{:else}
	<!-- Loading placeholder -->
	<div class="loading-placeholder">
		<div class="spinner"></div>
	</div>
{/if}

<style>
	* {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(html) {
		margin: 0;
		padding: 0;
		overflow-x: hidden;
		color-scheme: light only;
		-webkit-color-scheme: light;
	}

	:global(body) {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		margin: 0;
		padding: 0;
		overflow-x: hidden;
		width: 100%;
		background-color: #ffffff !important;
		color: #000000 !important;
		color-scheme: light only;
		-webkit-color-scheme: light;
		overscroll-behavior-y: contain;
	}

	.layout-container {
		display: flex;
		flex-direction: column;
		flex: 1 0 auto;
		width: 100%;
		min-height: 0;
		position: relative;
	}

	main {
		padding: 0;
		width: 100%;
		max-width: 100%;
		overflow-x: hidden;
		box-sizing: border-box;
	}

	.main-content-wrapper {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100%;
	}

	.loading-placeholder {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 100vh;
		background: #f5f5f5;
	}

	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid rgba(64, 123, 255, 0.2);
		border-top-color: rgba(64, 123, 255, 0.8);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
