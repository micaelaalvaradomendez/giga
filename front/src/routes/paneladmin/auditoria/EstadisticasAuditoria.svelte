<script>
	import { auditoriaController } from "$lib/paneladmin/controllers";

	export let registros = [];

	// Función para obtener estadísticas generales
	// Optimized: reduce Date instantiation in loops
	function calcularEstadisticas(registros) {
		if (!registros || registros.length === 0) {
			return {
				total: 0,
				hoy: 0,
				estaSemana: 0,
				esteMes: 0,
				porAccion: {},
				porModulo: {},
				porUsuario: {},
				actividad: []
			};
		}

		// Calculate reference dates once
		const hoy = new Date();
		hoy.setHours(0, 0, 0, 0);
		const hoyTs = hoy.getTime();
		
		const inicioSemana = new Date(hoy);
		inicioSemana.setDate(hoy.getDate() - hoy.getDay());
		const inicioSemanaTs = inicioSemana.getTime();
		
		const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
		const inicioMesTs = inicioMes.getTime();

		// Contadores básicos
		const stats = {
			total: registros.length,
			hoy: 0,
			estaSemana: 0,
			esteMes: 0,
			porAccion: {},
			porModulo: {},
			porUsuario: {},
			actividad: []
		};

		// Crear array para actividad diaria (últimos 7 días)
		const actividadDiaria = Array(7).fill(0);
		const fechaLabels = [];
		
		// Pre-calculate day timestamps for activity buckets
		const dayBuckets = [];
		for (let i = 6; i >= 0; i--) {
			const fecha = new Date();
			fecha.setDate(fecha.getDate() - i);
			fecha.setHours(0, 0, 0, 0);
			fechaLabels.push(fecha.toLocaleDateString('es-AR', { 
				weekday: 'short', 
				day: 'numeric' 
			}));
			dayBuckets.push(fecha.getTime());
		}

		// One day in milliseconds
		const oneDay = 24 * 60 * 60 * 1000;

		// Procesar cada registro
		registros.forEach(registro => {
			// Use precomputed timestamp if available, otherwise parse once
			const tsRegistro = registro._ts_creado_en || new Date(registro.creado_en).getTime();
			
			// Create date only for resetting time (needed for day comparison)
			const fechaRegistro = new Date(tsRegistro);
			fechaRegistro.setHours(0, 0, 0, 0);
			const fechaRegistroTs = fechaRegistro.getTime();

			// Contadores por fecha
			if (fechaRegistroTs >= hoyTs) {
				stats.hoy++;
			}
			if (fechaRegistroTs >= inicioSemanaTs) {
				stats.estaSemana++;
			}
			if (fechaRegistroTs >= inicioMesTs) {
				stats.esteMes++;
			}

			// Actividad diaria (últimos 7 días) - use timestamp comparison
			const diasAtras = Math.floor((hoyTs - fechaRegistroTs) / oneDay);
			if (diasAtras >= 0 && diasAtras < 7) {
				actividadDiaria[6 - diasAtras]++;
			}

			// Por acción
			const accion = auditoriaController.traducirAccion(registro.accion);
			stats.porAccion[accion] = (stats.porAccion[accion] || 0) + 1;

			// Por módulo
			const modulo = auditoriaController.formatearNombreModulo(registro.nombre_tabla);
			stats.porModulo[modulo] = (stats.porModulo[modulo] || 0) + 1;

			// Por usuario
			const usuario = registro.creado_por_nombre || 'Sistema';
			stats.porUsuario[usuario] = (stats.porUsuario[usuario] || 0) + 1;
		});

		// Crear datos de actividad
		stats.actividad = fechaLabels.map((label, index) => ({
			fecha: label,
			cantidad: actividadDiaria[index]
		}));

		return stats;
	}

	// Función para obtener top N elementos de un objeto
	function getTop(objeto, n = 5) {
		return Object.entries(objeto)
			.sort((a, b) => b[1] - a[1])
			.slice(0, n);
	}

	// Función para obtener color por acción
	function getColorAccion(accion) {
		return auditoriaController.getBadgeColor(accion.toUpperCase().replace(/ /g, '_'));
	}

	// Reactive statements
	$: estadisticas = calcularEstadisticas(registros);
	$: topAcciones = getTop(estadisticas.porAccion);
	$: topModulos = getTop(estadisticas.porModulo);
	$: topUsuarios = getTop(estadisticas.porUsuario);
	$: actividadMaxima = Math.max(...estadisticas.actividad.map(a => a.cantidad), 1);
</script>

<div class="estadisticas-container">
	<!-- Tarjetas de resumen -->
	<div class="tarjetas-resumen">
		<div class="tarjeta">
			<div class="tarjeta-icono total">📊</div>
			<div class="tarjeta-content">
				<div class="tarjeta-numero">{estadisticas.total.toLocaleString()}</div>
				<div class="tarjeta-titulo">Total de Registros</div>
			</div>
		</div>

		<div class="tarjeta">
			<div class="tarjeta-icono hoy">📅</div>
			<div class="tarjeta-content">
				<div class="tarjeta-numero">{estadisticas.hoy}</div>
				<div class="tarjeta-titulo">Hoy</div>
			</div>
		</div>

		<div class="tarjeta">
			<div class="tarjeta-icono semana">📈</div>
			<div class="tarjeta-content">
				<div class="tarjeta-numero">{estadisticas.estaSemana}</div>
				<div class="tarjeta-titulo">Esta Semana</div>
			</div>
		</div>

		<div class="tarjeta">
			<div class="tarjeta-icono mes">📊</div>
			<div class="tarjeta-content">
				<div class="tarjeta-numero">{estadisticas.esteMes}</div>
				<div class="tarjeta-titulo">Este Mes</div>
			</div>
		</div>
	</div>

	<!-- Gráficos y estadísticas detalladas -->
	<div class="graficos-grid">
		<!-- Actividad Diaria -->
		<div class="grafico-card">
			<h3>📈 Actividad de los Últimos 7 Días</h3>
			<div class="grafico-barras">
				{#each estadisticas.actividad as dia}
					<div class="barra-container">
						<div class="barra-label">{dia.fecha}</div>
						<div class="barra-wrapper">
							<div 
								class="barra"
								style="height: {(dia.cantidad / actividadMaxima) * 100}%"
								title="{dia.cantidad} registros"
							></div>
						</div>
						<div class="barra-valor">{dia.cantidad}</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Top Acciones -->
		<div class="lista-card">
			<h3>⚡ Acciones Más Frecuentes</h3>
			<div class="lista-items">
				{#each topAcciones as [accion, cantidad]}
					<div class="lista-item">
						<div class="lista-info">
							<span class="badge {getColorAccion(accion)}">{accion}</span>
							<span class="lista-porcentaje">
								{((cantidad / estadisticas.total) * 100).toFixed(1)}%
							</span>
						</div>
						<div class="lista-barra">
							<div 
								class="lista-progreso"
								style="width: {(cantidad / topAcciones[0][1]) * 100}%"
							></div>
						</div>
						<div class="lista-cantidad">{cantidad}</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Top Módulos -->
		<div class="lista-card">
			<h3>📦 Módulos Más Activos</h3>
			<div class="lista-items">
				{#each topModulos as [modulo, cantidad]}
					<div class="lista-item">
						<div class="lista-info">
							<span class="modulo-name">{modulo}</span>
							<span class="lista-porcentaje">
								{((cantidad / estadisticas.total) * 100).toFixed(1)}%
							</span>
						</div>
						<div class="lista-barra">
							<div 
								class="lista-progreso modulo"
								style="width: {(cantidad / topModulos[0][1]) * 100}%"
							></div>
						</div>
						<div class="lista-cantidad">{cantidad}</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Top Usuarios -->
		<div class="lista-card">
			<h3>👥 Usuarios Más Activos</h3>
			<div class="lista-items">
				{#each topUsuarios as [usuario, cantidad]}
					<div class="lista-item">
						<div class="lista-info">
							<span class="usuario-name">
								{#if usuario === 'Sistema'}
									🤖 {usuario}
								{:else}
									👤 {usuario}
								{/if}
							</span>
							<span class="lista-porcentaje">
								{((cantidad / estadisticas.total) * 100).toFixed(1)}%
							</span>
						</div>
						<div class="lista-barra">
							<div 
								class="lista-progreso usuario"
								style="width: {(cantidad / topUsuarios[0][1]) * 100}%"
							></div>
						</div>
						<div class="lista-cantidad">{cantidad}</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>

<style>
	.estadisticas-container {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.tarjetas-resumen {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 20px;
	}

	.tarjeta {
		background: white;
		border-radius: 12px;
		padding: 24px;
		display: flex;
		align-items: center;
		gap: 16px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		transition: transform 0.2s ease, box-shadow 0.2s ease;
	}

	.tarjeta:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
	}

	.tarjeta-icono {
		width: 60px;
		height: 60px;
		border-radius: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24px;
		font-weight: bold;
		color: white;
	}

	.tarjeta-icono.total {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}

	.tarjeta-icono.hoy {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
	}

	.tarjeta-icono.semana {
		background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
	}

	.tarjeta-icono.mes {
		background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
	}

	.tarjeta-content {
		flex: 1;
	}

	.tarjeta-numero {
		font-size: 2rem;
		font-weight: bold;
		color: #1f2937;
		line-height: 1.2;
	}

	.tarjeta-titulo {
		font-size: 0.9rem;
		color: #6b7280;
		font-weight: 500;
	}

	.graficos-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
		gap: 24px;
	}

	.grafico-card, .lista-card {
		background: white;
		border-radius: 12px;
		padding: 24px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.grafico-card h3, .lista-card h3 {
		margin: 0 0 20px 0;
		color: #1f2937;
		font-size: 1.1rem;
		font-weight: 600;
	}

	.grafico-barras {
		display: flex;
		align-items: end;
		gap: 12px;
		height: 200px;
		padding: 20px 0;
	}

	.barra-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		height: 100%;
	}

	.barra-label {
		font-size: 0.8rem;
		color: #6b7280;
		margin-bottom: 8px;
		text-align: center;
	}

	.barra-wrapper {
		flex: 1;
		width: 100%;
		display: flex;
		align-items: end;
		padding: 0 4px;
	}

	.barra {
		width: 100%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 4px 4px 0 0;
		min-height: 4px;
		transition: all 0.3s ease;
	}

	.barra:hover {
		background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
	}

	.barra-valor {
		font-size: 0.8rem;
		color: #374151;
		font-weight: 600;
		margin-top: 8px;
	}

	.lista-items {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.lista-item {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.lista-info {
		flex: 1;
		display: flex;
		justify-content: space-between;
		align-items: center;
		min-width: 0;
	}

	.modulo-name, .usuario-name {
		font-weight: 500;
		color: #374151;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.lista-porcentaje {
		font-size: 0.8rem;
		color: #6b7280;
		font-weight: 600;
	}

	.lista-barra {
		width: 60px;
		height: 6px;
		background: #f3f4f6;
		border-radius: 3px;
		overflow: hidden;
	}

	.lista-progreso {
		height: 100%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 3px;
		transition: width 0.3s ease;
	}

	.lista-progreso.modulo {
		background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
	}

	.lista-progreso.usuario {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
	}

	.lista-cantidad {
		font-size: 0.9rem;
		font-weight: 600;
		color: #374151;
		min-width: 30px;
		text-align: right;
	}

	.badge {
		padding: 2px 6px;
		border-radius: 8px;
		font-size: 0.8rem;
		font-weight: 600;
		white-space: nowrap;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.tarjetas-resumen {
			grid-template-columns: repeat(2, 1fr);
		}

		.graficos-grid {
			grid-template-columns: 1fr;
		}

		.tarjeta {
			padding: 16px;
		}

		.tarjeta-icono {
			width: 48px;
			height: 48px;
			font-size: 20px;
		}

		.tarjeta-numero {
			font-size: 1.5rem;
		}

		.grafico-card, .lista-card {
			padding: 16px;
		}

		.grafico-barras {
			height: 150px;
		}
	}

	@media (max-width: 480px) {
		.tarjetas-resumen {
			grid-template-columns: 1fr;
		}

		.lista-item {
			flex-direction: column;
			align-items: stretch;
			gap: 8px;
		}

		.lista-barra {
			width: 100%;
		}
	}
</style>