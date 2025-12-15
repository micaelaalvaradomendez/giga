<script>
	import Navbar from "$lib/componentes/navbar.svelte";
	import Footer from "$lib/componentes/footer.svelte";
	import Menu from "$lib/componentes/menu.svelte";
	import Breadcrumbs from "$lib/componentes/breadcrumbs.svelte";
	import { onMount } from "svelte";
	import { AuthService } from "$lib/login/authService.js";
	let isMenuOpen = false;

	onMount(async () => {
		await AuthService.checkSession();
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

<Navbar />

<Menu bind:isActive={isMenuOpen} />

<div class="layout-container" class:menu-open={isMenuOpen}>
	<main>
		<div class="main-content-wrapper">
			<Breadcrumbs />
			<slot />
		</div>
	</main>
</div>

<Footer />

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

</style>
