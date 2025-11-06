<script>
	import { onMount } from 'svelte';
	import NodeRenderer from './NodeRenderer.svelte';

	export let data = null;

	let expandedNodes = new Set();

	// Expandir automáticamente los primeros 2 niveles
	onMount(() => {
		if (data?.organigrama) {
			expandAllNodes(data.organigrama, 2);
		}
	});

	function expandAllNodes(node, maxLevel) {
		if (node.nivel < maxLevel) {
			expandedNodes.add(node.id);
			if (node.children) {
				node.children.forEach(child => expandAllNodes(child, maxLevel));
			}
		}
		expandedNodes = expandedNodes; // Trigger reactivity
	}

	function toggleNode(nodeId) {
		if (expandedNodes.has(nodeId)) {
			expandedNodes.delete(nodeId);
		} else {
			expandedNodes.add(nodeId);
		}
		expandedNodes = expandedNodes; // Trigger reactivity
	}

	function getNodeIcon(tipo) {
		const icons = {
			secretaria: '🏛️',
			subsecretaria: '🏢',
			direccion: '📁',
			direccion_general: '📋',
			subdireccion: '📄',
			departamento: '📝',
			division: '📌'
		};
		return icons[tipo] || '📋';
	}

	function getNodeColor(tipo) {
		const colors = {
			secretaria: 'border-blue-600 bg-blue-50',
			subsecretaria: 'border-blue-500 bg-blue-40',
			direccion: 'border-green-500 bg-green-40',
			direccion_general: 'border-green-400 bg-green-30',
			subdireccion: 'border-yellow-500 bg-yellow-40',
			departamento: 'border-orange-500 bg-orange-40',
			division: 'border-purple-500 bg-purple-40'
		};
		return colors[tipo] || 'border-gray-500 bg-gray-40';
	}
</script>

{#if data?.organigrama}
	<div class="container-organigrama">
		<div class="header-organigrama">
			<h1>Organigrama Institucional</h1>
			<p class="descripcion">
				Estructura organizacional de la Secretaría de Protección Civil
			</p>
			<div class="info-actualización">
				<span class="fecha-actualizacion">
					Última actualización: {new Date(data.lastUpdated).toLocaleDateString('es-AR')}
				</span>
				{#if data.updatedBy}
					<span class="actualizado-por">
						Actualizado por: {data.updatedBy}
					</span>
				{/if}
			</div>
		</div>

		<div class="organigrama-container">
			<div class="organigrama-tree">
				<NodeRenderer 
					node={data.organigrama} 
					{expandedNodes} 
					{toggleNode} 
					{getNodeIcon} 
					{getNodeColor} 
				/>
			</div>
		</div>
	</div>
{:else}
	<div class="no-data">
		<p>No hay datos de organigrama disponibles</p>
	</div>
{/if}

<style>
	.container-organigrama {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
		background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
		min-height: 100vh;
	}

	.header-organigrama {
		text-align: center;
		margin-bottom: 3rem;
		padding: 2rem;
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	.header-organigrama h1 {
		font-size: 2.5rem;
		font-weight: 700;
		color: #1e40af;
		margin-bottom: 0.5rem;
	}

	.descripcion {
		font-size: 1.2rem;
		color: #64748b;
		margin-bottom: 1rem;
	}

	.info-actualización {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		align-items: center;
	}

	.fecha-actualizacion {
		display: inline-block;
		background: #dbeafe;
		color: #1e40af;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		font-size: 0.9rem;
		font-weight: 500;
	}

	.actualizado-por {
		font-size: 0.8rem;
		color: #64748b;
	}

	.organigrama-container {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	.organigrama-tree {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.no-data {
		text-align: center;
		padding: 4rem 2rem;
		color: #64748b;
		font-size: 1.1rem;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.container-organigrama {
			padding: 1rem;
		}

		.header-organigrama {
			padding: 1.5rem;
		}

		.header-organigrama h1 {
			font-size: 2rem;
		}

		.organigrama-container {
			padding: 1rem;
		}
	}
</style>