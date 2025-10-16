<script>
	import Navbar from '$lib/componentes/navbar.svelte';
	import Footer from '$lib/componentes/footer.svelte';
	import '$lib/componentes/componentes.css';
	
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" />
	<title>Sistema GIGA</title>
	<meta name="description" content="Sistema de Gestión Integral de Guardias y Asistencia" />
</svelte:head>

<Navbar />

<main>
	{@render children?.()}
</main>

<Footer />

<!--
aca definimos todo lo que se va a repetir en todas las paginas del sw
-->

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
	
	main {
		flex: 1;
		padding: 2rem;
	}
</style>

