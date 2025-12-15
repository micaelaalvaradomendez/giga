<script>
	export let node;
	export let expandedNodes;
	export let toggleNode;
	export let getNodeIcon;
	export let getNodeColor;
	export let detectarTipoArea;
</script>

{#if node}
	<div class="node-container">
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div 
			class="node {getNodeColor(detectarTipoArea ? detectarTipoArea(node.nombre, node.nivel) : node.tipo)} nivel-{node.nivel}"
			on:click={() => node.children?.length && toggleNode(node.id)}
		>
			<div class="node-header">
				<div class="node-icon">
					{getNodeIcon(detectarTipoArea ? detectarTipoArea(node.nombre, node.nivel) : node.tipo)}
				</div>
				<div class="node-content">
					<h3 class="node-title">{node.nombre}</h3>
					{#if node.descripcion}
						<p class="node-description">{node.descripcion}</p>
					{/if}
					{#if node.jefe?.nombre}
						<p class="node-titular">Jefe: {node.jefe.nombre}</p>
					{/if}
					{#if node.jefe?.email}
						<p class="node-contact">📧 {node.jefe.email}</p>
					{/if}
					{#if node.total_agentes !== undefined && node.total_agentes > 0}
						<p class="node-agents">� {node.total_agentes} agentes</p>
					{/if}
				</div>
				{#if node.children?.length}
					<div class="expand-icon {expandedNodes.has(node.id) ? 'expanded' : ''}">
						▼
					</div>
				{/if}
			</div>
		</div>

		{#if node.children?.length && expandedNodes.has(node.id)}
			<div class="children-container">
				{#each node.children as child (child.id)}
					<svelte:self 
						node={child} 
						{expandedNodes} 
						{toggleNode} 
						{getNodeIcon} 
						{getNodeColor} 
						{detectarTipoArea}
					/>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
	.node-container {
		margin: 0.5rem 0;
		width: 100%;
	}

	.node {
		background: white;
		border: 2px solid;
		border-radius: 8px;
		padding: 1rem;
		margin: 0.5rem;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.node:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.node-header {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.node-icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}

	.node-content {
		flex: 1;
	}

	.node-title {
		font-size: 1.1rem;
		font-weight: 600;
		color: #1e293b;
		margin: 0 0 0.25rem 0;
		line-height: 1.4;
	}

	.node-description {
		font-size: 0.9rem;
		color: #64748b;
		margin: 0 0 0.25rem 0;
		line-height: 1.3;
	}

	.node-titular {
		font-size: 0.85rem;
		color: #059669;
		font-weight: 500;
		margin: 0 0 0.25rem 0;
	}

	.node-contact {
		font-size: 0.8rem;
		color: #6366f1;
		margin: 0 0 0.25rem 0;
	}

	.node-agents {
		font-size: 0.8rem;
		color: #7c3aed;
		font-weight: 500;
		margin: 0 0 0.25rem 0;
	}

	.expand-icon {
		font-size: 0.8rem;
		color: #64748b;
		transition: transform 0.3s ease;
	}

	.expand-icon.expanded {
		transform: rotate(180deg);
	}

	.children-container {
		margin-left: 2rem;
		padding-left: 2rem;
		border-left: 2px dashed #cbd5e1;
		margin-top: 1rem;
	}

	/* Estilos específicos por nivel */
	.nivel-0 {
		font-size: 1.1em;
	}

	.nivel-1 {
		font-size: 1.05em;
	}

	.nivel-2 {
		font-size: 1em;
	}

	.nivel-3 {
		font-size: 0.95em;
	}

	.nivel-4, .nivel-5, .nivel-6 {
		font-size: 0.9em;
	}

	/* Colores por tipo de nodo */
	.border-blue-600 { border-color: #2563eb; }
	.bg-blue-50 { background-color: #eff6ff; }
	.border-blue-500 { border-color: #3b82f6; }
	.bg-blue-40 { background-color: #dbeafe; }
	.border-green-500 { border-color: #10b981; }
	.bg-green-40 { background-color: #d1fae5; }
	.border-green-400 { border-color: #34d399; }
	.bg-green-30 { background-color: #a7f3d0; }
	.border-yellow-500 { border-color: #eab308; }
	.bg-yellow-40 { background-color: #fef3c7; }
	.border-orange-500 { border-color: #f97316; }
	.bg-orange-40 { background-color: #fed7aa; }
	.border-purple-500 { border-color: #a855f7; }
	.bg-purple-40 { background-color: #e9d5ff; }
	.border-gray-500 { border-color: #6b7280; }
	.bg-gray-40 { background-color: #f3f4f6; }

	/* Responsive */
	@media (max-width: 768px) {
		.node {
			padding: 0.75rem;
			margin: 0.5rem 0.25rem 0.5rem 0; /* Ajustar margen derecho */
		}

		.node-container {
			width: auto; /* Dejar que el padding del contenedor padre maneje el ancho */
			padding-right: 0.5rem;
		}

		.children-container {
			margin-left: 1rem;
			padding-left: 1rem;
		}
	}
</style>