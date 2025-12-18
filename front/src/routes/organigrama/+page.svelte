<script>
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import OrganigramaViewer from "$lib/componentes/admin/organigrama/OrganigramaViewer.svelte";
	import { organigrama as organigramaStore, loadOrganigrama } from "$lib/stores/dataCache.js";

	let loading = true;
	
	// Usar store de organigrama
	$: organigramaData = $organigramaStore;

	onMount(async () => {
		if (browser) {
			await cargarOrganigramaOptimizado();
		}
	});

	async function cargarOrganigramaOptimizado() {
		try {
			console.log("🔄 Cargando organigrama...");
			loading = true;
			
			// Usar caché global - evita cargas duplicadas
			const data = await loadOrganigrama();
			
			// Si no hay datos en caché, usar fallback
			if (!data) {
				console.log("⚠️ No hay datos de organigrama, usando fallback");
				// Los datos de fallback ya están manejados en dataCache.js
			}
		} catch (error) {
			console.error("❌ Error cargando organigrama:", error);
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Organigrama - GIGA</title>
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
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
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
