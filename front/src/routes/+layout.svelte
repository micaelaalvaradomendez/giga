<script>
	import Navbar from "$lib/componentes/navbar.svelte";
	import Footer from "$lib/componentes/footer.svelte";
	import Menu from "$lib/componentes/menu.svelte";
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
		<slot />
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
		height: 100%;
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
		height: 100%;
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
		flex: 1;
		width: 100%;
		min-height: 0;
		position: relative;
	}

	main {
		flex: 1;
		padding: 0;
		width: 100%;
		max-width: 100%;
		overflow-x: hidden;
		box-sizing: border-box;
	}


</style>
