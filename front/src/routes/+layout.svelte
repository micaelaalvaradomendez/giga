<script>
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" />
	<title>Sistema de Control Horario y Guardias</title>
	<meta name="description" content="Sistema integral de gestión de recursos humanos, control de asistencia y guardias" />
</svelte:head>

{@render children?.()}

<!--
Aca vamos a definir el navbar y footer que se va a repetir en todas las paginas
-->
