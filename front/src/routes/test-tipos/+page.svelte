<script>
	// Función de detección de tipo (copiada de OrganigramaViewer)
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
		switch(nivel) {
			case 1: return "secretaria";
			case 2: return "subsecretaria"; 
			case 3: 
			case 4: return "direccion";
			case 5: return "departamento";
			case 6:
			case 7: return "division";
			default: return "area";
		}
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

	// Ejemplos de áreas para probar
	const areasEjemplo = [
		{ nombre: "Secretaría de Protección Civil", nivel: 1 },
		{ nombre: "Subsecretaría de Seguridad Vial", nivel: 2 },
		{ nombre: "Dirección Provincial de Seguridad Vial", nivel: 3 },
		{ nombre: "Dirección General de Planificación de Transporte y Seguridad Vial", nivel: 4 },
		{ nombre: "Dirección Administrativa y Contable", nivel: 4 },
		{ nombre: "Subdirección General de Planificación de Transporte y Seguridad Vial", nivel: 5 },
		{ nombre: "Departamento Administrativo y Contable", nivel: 5 },
		{ nombre: "Departamento de Planificación", nivel: 6 },
		{ nombre: "División de Planificación", nivel: 7 },
		{ nombre: "División de Choferes Zona Norte", nivel: 7 },
		// Casos sin palabras clave específicas (debería usar nivel)
		{ nombre: "Área Sin Palabra Clave Nivel 3", nivel: 3 },
		{ nombre: "Área Sin Palabra Clave Nivel 5", nivel: 5 },
	];
</script>

<svelte:head>
	<title>Test Detección de Tipos - GIGA</title>
</svelte:head>

<div style="padding: 20px; font-family: Arial, sans-serif;">
	<h1>🧪 Test de Detección Automática de Tipos de Área</h1>
	
	<p style="color: #666; margin-bottom: 30px;">
		Esta página prueba la función de detección automática de tipos de área basada en el nombre y nivel jerárquico.
	</p>

	<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;">
		{#each areasEjemplo as area}
			{@const tipoDetectado = detectarTipoArea(area.nombre, area.nivel)}
			<div style="border: 2px solid #e1e5e9; border-radius: 8px; padding: 20px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
				<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
					<span style="font-size: 24px;">{getNodeIcon(tipoDetectado)}</span>
					<div>
						<h3 style="margin: 0; color: #333; font-size: 16px;">{area.nombre}</h3>
						<small style="color: #666;">Nivel: {area.nivel}</small>
					</div>
				</div>
				
				<div style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 14px;">
					<strong>Tipo detectado:</strong> 
					<span style="color: #28a745; font-weight: bold;">{tipoDetectado}</span>
				</div>
				
				<div style="margin-top: 10px; font-size: 12px; color: #666;">
					{#if area.nombre.toLowerCase().includes("secretaría")}
						🔍 Detectado por palabra: "secretaría"
					{:else if area.nombre.toLowerCase().includes("subsecretaría")}
						🔍 Detectado por palabra: "subsecretaría"
					{:else if area.nombre.toLowerCase().includes("dirección general")}
						🔍 Detectado por palabras: "dirección general"
					{:else if area.nombre.toLowerCase().includes("dirección")}
						🔍 Detectado por palabra: "dirección"
					{:else if area.nombre.toLowerCase().includes("subdirección")}
						🔍 Detectado por palabra: "subdirección"
					{:else if area.nombre.toLowerCase().includes("departamento")}
						🔍 Detectado por palabra: "departamento"
					{:else if area.nombre.toLowerCase().includes("división")}
						🔍 Detectado por palabra: "división"
					{:else}
						📊 Detectado por nivel jerárquico ({area.nivel})
					{/if}
				</div>
			</div>
		{/each}
	</div>

	<div style="margin-top: 40px; padding: 20px; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196f3;">
		<h3 style="margin-top: 0; color: #1565c0;">🔧 Lógica de Detección</h3>
		<ol style="color: #424242; line-height: 1.6;">
			<li><strong>Prioridad 1:</strong> Detección por palabras clave en el nombre</li>
			<li><strong>Prioridad 2:</strong> Detección por nivel jerárquico si no hay palabras clave</li>
			<li><strong>Mapeo de niveles:</strong>
				<ul>
					<li>Nivel 1: Secretaría 🏛️</li>
					<li>Nivel 2: Subsecretaría 🏢</li>
					<li>Niveles 3-4: Dirección 📁</li>
					<li>Nivel 5: Departamento 📝</li>
					<li>Niveles 6-7: División 📌</li>
				</ul>
			</li>
		</ol>
	</div>

	<div style="margin-top: 20px; text-align: center;">
		<a href="/organigrama" style="display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
			Ver Organigrama Real
		</a>
	</div>
</div>