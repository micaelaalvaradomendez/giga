<script>
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import OrganigramaViewer from "$lib/componentes/OrganigramaViewer.svelte";

	let organigramaData = null;
	let loading = true;

	onMount(async () => {
		if (browser) {
			await loadOrganigrama();
		}
	});

	async function loadOrganigrama() {
		try {
			// CARGAR DESDE API DEL BACKEND
			const response = await fetch("/api/personas/organigrama/", {
				method: "GET",
				credentials: "include",
			});

			if (response.ok) {
				const result = await response.json();
				console.log("🔍 Respuesta del API organigrama:", result);
				if (result.success) {
					// Convertir estructura de la API al formato esperado por el frontend
					organigramaData = {
						version: result.data.version,
						lastUpdated: result.data.actualizado_en,
						updatedBy: result.data.creado_por,
						organigrama: result.data.estructura,
					};
					console.log("✅ Datos del organigrama procesados:", organigramaData);
				} else {
					throw new Error(
						result.message || "Error al cargar organigrama",
					);
				}
			} else {
				throw new Error("Error de conexión con el servidor");
			}
		} catch (error) {
			console.error("❌ Error cargando organigrama desde API:", error);

			// Datos de fallback básicos para mostrar algo en caso de error
			organigramaData = {
				version: "1.0.0",
				lastUpdated: new Date().toISOString(),
				updatedBy: "Sistema",
				organigrama: [
					{
						id: "root",
						tipo: "secretaria",
						nombre: "Secretaría de Protección Civil",
						titular: "No disponible",
						email: "",
						telefono: "",
						descripcion: "Organigrama no disponible temporalmente",
						nivel: 0,
						children: [],
					},
				],
			};
			console.log("✅ Usando datos de fallback básicos");
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
