<script>
	import { onMount } from "svelte";
	import NodeRenderer from "./NodeRenderer.svelte";
	export let data = null;
	let expandedNodes = new Set();
	// Expandir automáticamente los primeros 2 niveles
	onMount(() => {
		if (data?.organigrama) {
			if (Array.isArray(data.organigrama)) {
				data.organigrama.forEach((rootNode) =>
					expandAllNodes(rootNode, 2),
				);
			} else {
				expandAllNodes(data.organigrama, 2);
			}
		}
	});
	function expandAllNodes(node, maxLevel) {
		if (node.nivel < maxLevel) {
			expandedNodes.add(node.id);
			if (node.children) {
				node.children.forEach((child) =>
					expandAllNodes(child, maxLevel),
				);
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
			secretaria: "🏛️",
			subsecretaria: "🏢",
			direccion: "📁",
			direccion_general: "📋",
			subdireccion: "📄",
			departamento: "📝",
			division: "📌",
		};
		return icons[tipo] || "📋";
	}
	// Nueva función para detectar tipo automáticamente basado en el nombre y nivel
	function detectarTipoArea(nombre, nivel = 0) {
		if (!nombre) return "area";
		const nombreLower = nombre.toLowerCase();
		// Secretarías (nivel 1 generalmente)
		if (nombreLower.includes("secretaría")) {
			return "secretaria";
		}
		// Subsecretarías (nivel 2 generalmente)
		if (nombreLower.includes("subsecretaría")) {
			return "subsecretaria";
		}
		// Direcciones Generales (nivel 4 generalmente)
		if (nombreLower.includes("dirección general")) {
			return "direccion_general";
		}
		// Direcciones (nivel 3-4 generalmente)
		if (nombreLower.includes("dirección")) {
			return "direccion";
		}
		// Subdirecciones (nivel 5 generalmente)
		if (nombreLower.includes("subdirección")) {
			return "subdireccion";
		}
		// Departamentos (nivel 5-6 generalmente)
		if (nombreLower.includes("departamento")) {
			return "departamento";
		}
		// Divisiones (nivel 6-7 generalmente)
		if (nombreLower.includes("división")) {
			return "division";
		}
		// Detección por nivel si no hay palabra clave específica
		switch (nivel) {
			case 1:
				return "secretaria";
			case 2:
				return "subsecretaria";
			case 3:
			case 4:
				return "direccion";
			case 5:
				return "departamento";
			case 6:
			case 7:
				return "division";
			default:
				return "area";
		}
	}
	function getNodeColor(tipo) {
		const colors = {
			secretaria: "border-blue-600 bg-blue-50",
			subsecretaria: "border-blue-500 bg-blue-40",
			direccion: "border-green-500 bg-green-40",
			direccion_general: "border-green-400 bg-green-30",
			subdireccion: "border-yellow-500 bg-yellow-40",
			departamento: "border-orange-500 bg-orange-40",
			division: "border-purple-500 bg-purple-40",
		};
		return colors[tipo] || "border-gray-500 bg-gray-40";
	}
</script>
{#if data?.organigrama}
	<div class="container-organigrama">
		<div class="header-organigrama">
			<h1>Organigrama Institucional</h1>
			<div class="info-actualización">
				<span class="fecha-actualizacion">
					Última actualización: {new Date(
						data.lastUpdated,
					).toLocaleDateString("es-AR")}
				</span>
			</div>
		</div>
		<div class="organigrama-container">
			<div class="organigrama-tree">
				{#if Array.isArray(data.organigrama)}
					{#each data.organigrama as rootNode (rootNode.id)}
						<NodeRenderer
							node={rootNode}
							{expandedNodes}
							{toggleNode}
							{getNodeIcon}
							{getNodeColor}
							{detectarTipoArea}
						/>
					{/each}
				{:else}
					<NodeRenderer
						node={data.organigrama}
						{expandedNodes}
						{toggleNode}
						{getNodeIcon}
						{getNodeColor}
						{detectarTipoArea}
					/>
				{/if}
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
		width: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 1.5rem 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		box-sizing: border-box;
	}
	.header-organigrama {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 40px;
		margin: 0 0 0.5rem 0;
		border-radius: 28px;
		overflow: hidden;
		box-sizing: border-box;
		width: 100%;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 2rem;
	}
	.header-organigrama::before {
		content: "";
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-image: linear-gradient(
				90deg,
				rgba(255, 255, 255, 0.03) 1px,
				transparent 1px
			),
			linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
		background-size: 50px 50px;
		animation: moveLines 20s linear infinite;
	}
	.header-organigrama h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 30px;
		letter-spacing: 0.2px;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: inline-block;
		white-space: normal;
		word-break: break-word;
		line-height: 1.2;
		max-width: 100%;
	}
	.header-organigrama h1::after {
		content: "";
		position: absolute;
		width: 40%;
		height: 3px;
		bottom: 0;
		left: 0;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(255, 255, 255, 0.9),
			transparent
		);
		animation: moveLine 2s linear infinite;
	}
	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
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
		font-size: 17px;
		font-weight: 500;
	}
	.organigrama-container {
		border-radius: 12px;
		padding: 2rem;
		border: none;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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
	@media (max-width: 640px) {
		.container-organigrama {
			padding: 1rem 0.75rem 1.5rem;
			width: 100%;
			box-sizing: border-box;
			overflow-x: hidden;
		}
		.header-organigrama {
			padding: 1rem;
			flex-direction: column;
			align-items: center;
			text-align: center;
			gap: 1rem;
			width: 100%;
			box-sizing: border-box;
		}
		.header-organigrama h1 {
			font-size: 1.75rem; 
			margin-bottom: 0.5rem;
			max-width: 100%;
			width: 100%;
			text-align: center;
			display: block;
		}
		.header-organigrama h1::after {
			left: 50%;
			transform: translateX(-50%);
			animation: moveLine 2s linear infinite;
		}
		.info-actualización {
			width: 100%;
			align-items: center;
		}
		.organigrama-container {
			padding: 0.5rem;
		}
	}
</style>
