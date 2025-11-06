<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import OrganigramaViewer from '$lib/componentes/OrganigramaViewer.svelte';

	let organigramaData = null;
	let loading = true;

	onMount(async () => {
		if (browser) {
			try {
				// Cargar desde localStorage si existe, sino desde el archivo JSON
				const savedData = localStorage.getItem('organigrama');
				if (savedData) {
					organigramaData = JSON.parse(savedData);
				} else {
					// Cargar datos por defecto
					const { default: defaultData } = await import('$lib/data/organigrama.json');
					organigramaData = defaultData;
				}
			} catch (error) {
				console.error('Error cargando organigrama:', error);
			} finally {
				loading = false;
			}
		}
	});
</script>

<svelte:head>
	<title>Organigrama - GIGA</title>
	<meta name="description" content="Organigrama institucional de la Secretaría de Protección Civil" />
</svelte:head>

{#if loading}
	<div class="loading-container">
		<div class="loading-spinner"></div>
		<p>Cargando organigrama...</p>
	</div>
{:else if organigramaData}
	<OrganigramaViewer data={organigramaData} />
{:else}
	<div class="error-container">
		<h2>Error al cargar el organigrama</h2>
		<p>No se pudo cargar la información del organigrama institucional.</p>
	</div>
{/if}

<style>
	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 50vh;
		gap: 1rem;
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #e2e8f0;
		border-top: 4px solid #2563eb;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.error-container {
		text-align: center;
		padding: 2rem;
		max-width: 600px;
		margin: 0 auto;
	}

	.error-container h2 {
		color: #ef4444;
		margin-bottom: 1rem;
	}

	.error-container p {
		color: #64748b;
	}
</style>