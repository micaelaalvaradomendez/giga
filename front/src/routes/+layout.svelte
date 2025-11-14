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

	:global(html, body) {
		height: 100%;
		margin: 0;
		padding: 0;
	}

	:global(body) {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	.layout-container {
		display: flex;
		flex: 1;
		transition: margin-left 0.4s ease;
		margin-left: 0;
	}

	.layout-container.menu-open {
		margin-left: 320px;
	}

	main {
		flex: 1;
		padding: 2rem;
	}
</style>
