<script>
	const modules = [
		{ name: 'Usuarios', path: '/admin/usuarios', icon: '👥', description: 'Gestionar personal y usuarios' },
		{ name: 'Organigrama', path: '/admin/organigrama', icon: '🏛️', description: 'Definir áreas y jerarquías       -' },
		{ name: 'Roles y Permisos', path: '/admin/roles', icon: '🔐', description: 'Configurar roles de acceso' },
		{ name: 'Asistencias', path: '/admin/asistencias', icon: '📋', description: 'Revisar registros de asistencia' },
		{ name: 'Licencias', path: '/admin/licencias', icon: '🏥', description: 'Administrar licencias y novedades' },
		{ name: 'Guardias', path: '/admin/guardias', icon: '🛡️', description: 'Planificar guardias y turnos' },
		{ name: 'Feriados', path: '/admin/feriados', icon: '🎉', description: 'Gestionar días no laborables' },
		{ name: 'Reportes', path: '/admin/reportes', icon: '📊', description: 'Generar informes del sistema' },
		{ name: 'Parámetros', path: '/admin/parametros', icon: '⚙️', description: 'Ajustar la configuración global' },
		{ name: 'Auditoría', path: '/admin/auditoria', icon: '🔍', description: 'Rastrear cambios en el sistema' },
	];
</script>

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
	.dashboard-welcome {
		text-align: center;
		margin-bottom: 3rem;
		color: white;
	}

	.dashboard-welcome h1 {
		font-size: 2.5rem;
		margin-bottom: 0.5rem;
		font-weight: 700;
	}

	.dashboard-welcome p {
		font-size: 1.1rem;
		color: rgba(255, 255, 255, 0.85);
	}

	.modules-grid {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 1.5rem;
	}

	.module-card {
		display: flex;
		flex-direction: column;
		justify-content: center; 
		align-items: center; 
		text-align: center;
		background-color: #f8f9fa;
		border: 2px solid #f8f9fa ;
		border-radius: 8px;
		padding: 2rem 1.5rem;
		text-decoration: none;
		color: inherit;
		transition: transform 0.2s ease, box-shadow 0.2s ease;
		flex-basis: 180px;
		width: 180px;
		height: 150px;
	}

	.module-card:hover {
		transform: translateY(-5px);
		border-color: #fd7e14;
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
	}

	.module-icon {
		font-size: 3.5rem;
		margin-bottom: 1rem;
		color: #fd7e14;
	}

	.module-info h2 {
		font-size: 1.2rem;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #343a40;
	}

	.module-info p {
		font-size: 0.9rem;
		color: white;
		line-height: 1.4;
		max-width: 200px;
		background-color: #e79043;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
	}
</style>