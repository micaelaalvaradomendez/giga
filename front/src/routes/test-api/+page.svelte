<script>
	import { onMount } from 'svelte';
	import { personasService } from '$lib/services.js';

	let agentes = [];
	let loading = true;
	let error = null;

	onMount(async () => {
		try {
			console.log('Iniciando carga de agentes...');
			const response = await personasService.getAgentes();
			console.log('Respuesta:', response);
			
			if (response && response.data) {
				agentes = response.data.results || [];
				console.log('Agentes cargados:', agentes.length);
			} else {
				throw new Error('Respuesta inválida');
			}
		} catch (err) {
			console.error('Error:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	});
</script>

<div>
	<h1>Test API - Agentes</h1>
	
	{#if loading}
		<p>Cargando...</p>
	{:else if error}
		<p style="color: red;">Error: {error}</p>
	{:else}
		<p>Se encontraron {agentes.length} agentes:</p>
		<ul>
			{#each agentes as agente}
				<li>{agente.nombre} {agente.apellido} - {agente.email}</li>
			{/each}
		</ul>
	{/if}
</div>