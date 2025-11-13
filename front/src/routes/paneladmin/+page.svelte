<script>
	const modules = [
		{
			name: "Usuarios",
			path: "/paneladmin/usuarios",
			icon: "👥",
			description: "Gestionar personal y usuarios",
		},
		{
			name: "Organigrama",
			path: "/paneladmin/organigrama",
			icon: "🏛️",
			description: "Definir áreas y jerarquías       -",
		},
		{
			name: "Roles",
			path: "/paneladmin/roles",
			icon: "🔐",
			description: "Configurar roles de acceso",
		},
		{
			name: "Asistencias (falta)",
			path: "/paneladmin/asistencias",
			icon: "📋",
			description: "Revisar registros de asistencia",
		},
		{
			name: "Licencias (falta)",
			path: "/paneladmin/licencias",
			icon: "🏥",
			description: "Administrar licencias y novedades",
		},
		{
			name: "Guardias (falta)",
			path: "/paneladmin/guardias",
			icon: "🛡️",
			description: "Planificar guardias y turnos",
		},
		{
			name: "Feriados",
			path: "/paneladmin/feriados",
			icon: "🎉",
			description: "Gestionar días no laborables",
		},
		{
			name: "Reportes (falta)",
			path: "/paneladmin/reportes",
			icon: "📊",
			description: "Generar informes del sistema",
		},
		{
			name: "Parámetros",
			path: "/paneladmin/parametros",
			icon: "⚙️",
			description: "Ajustar la configuración global de Areas y hora de entrada y salida general",
		},
		{
			name: "Auditoría",
			path: "/paneladmin/auditoria",
			icon: "🔍",
			description: "Rastrear cambios en el sistema",
		},
	];
</script>

<div class="dashboard-welcome">
	<h1>Panel de Administración GIGA</h1>
	<p>Sistema de Gestión Integral de Guardias y Asistencias</p>
</div>

<div class="modules-grid">
	{#each modules as module}
		<a href={module.path} class="module-card">
			<div class="module-icon">{module.icon}</div>
			<div class="module-info">
				<h2>{module.name}</h2>
				<p>{module.description}</p>
			</div>
		</a>
	{/each}
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
		background-color: #f8f9fa;
		color: #212529;
	}

	:global(.admin-layout) {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	:global(.admin-header) {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 1.5rem;
		height: 70px;
		background: linear-gradient(135deg, #e79043, #f39c12);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	:global(.admin-header .logo a) {
		font-weight: bold;
		font-size: 1.3rem;
		text-decoration: none;
		color: white;
		transition: opacity 0.2s;
	}

	:global(.admin-main) {
		display: flex;
		flex-grow: 1;
		overflow: hidden;
		background-color: #f8f9fa;
	}

	:global(.admin-content-full) {
		flex-grow: 1;
		padding: 2rem;
		overflow-y: auto;
		width: 100%;
		background-color: #ffffff;
		margin: 1rem;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.dashboard-welcome {
		text-align: center;
		margin-bottom: 3rem;
		padding: 5px 0px 15px 0px;
		background: linear-gradient(135deg, #e79043, #f39c12);
		border-radius: 12px;
		color: white;
		margin-bottom: 6px;
	}

	.dashboard-welcome h1 {
		font-size: 2.5rem;
		margin-bottom: 0.5rem;
		font-weight: 700;
	}

	.dashboard-welcome p {
		font-size: 1.1rem;
		color: rgba(255, 255, 255, 0.9);
		margin: 0;
	}

	.modules-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1.5rem;
		padding: 1rem 0;
	}

	.module-card {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		align-items: center;
		text-align: center;
		background-color: #ffffff;
		border: 2px solid #e9ecef;
		border-radius: 12px;
		padding: 2rem 1.5rem;
		text-decoration: none;
		color: inherit;
		transition: all 0.3s ease;
		min-height: 180px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}

	.module-card:hover {
		transform: translateY(-8px);
		border-color: #e79043;
		box-shadow: 0 12px 24px rgba(231, 144, 67, 0.2);
		background-color: #f7b780;
	}

	.module-icon {
		font-size: 3.5rem;
		margin-bottom: 1rem;
		color: #e79043;
		transition: transform 0.3s ease;
	}

	.module-card:hover .module-icon {
		transform: scale(1.1);
	}

	.module-info {
		width: 100%;
	}

	.module-info h2 {
		font-size: 1.3rem;
		margin-bottom: 0.75rem;
		font-weight: 600;
		color: #2c3e50;
	}

	.module-info p {
		font-size: 0.95rem;
		color: white;
		line-height: 1.4;
		background: linear-gradient(135deg, #e79043, #f39c12);
		padding: 0.5rem 0.75rem;
		border-radius: 7px;
		margin: 1px;
		box-shadow: 3px 2px 4px 2px rgba(0, 0, 0, 0.1);
	}
	@media (max-width: 768px) {
		.modules-grid {
			grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
			gap: 1rem;
		}

		.module-card {
			padding: 1.5rem 1rem;
			min-height: 150px;
		}

		.module-icon {
			font-size: 3rem;
		}

		.module-info h2 {
			font-size: 1.1rem;
		}

		.module-info p {
			font-size: 0.85rem;
		}

		.dashboard-welcome {
			margin: -2rem -1rem 2rem -1rem;
			padding: 1.5rem;
		}

		.dashboard-welcome h1 {
			font-size: 2rem;
		}
	}
</style>
