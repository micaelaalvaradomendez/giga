<script>
	import { auditoriaController } from "$lib/paneladmin/controllers";

	// Stores del controlador
	const { filtros, registros } = auditoriaController;

	// Usar stores derivados en lugar de variables reactivas para evitar problemas de SSR
	import { derived } from 'svelte/store';
	
	const modulosUnicos = derived(registros, ($registros) => {
		if (!$registros || !Array.isArray($registros)) return [];
		return $registros
			.map(registro => registro.nombre_tabla)
			.filter((modulo, index, array) => array.indexOf(modulo) === index)
			.sort()
			.map(modulo => ({
				value: modulo,
				label: auditoriaController.formatearNombreModulo(modulo)
			}));
	});

	const accionesUnicas = derived(registros, ($registros) => {
		if (!$registros || !Array.isArray($registros)) return [];
		return $registros
			.map(registro => registro.accion)
			.filter((accion, index, array) => array.indexOf(accion) === index)
			.sort()
			.map(accion => ({
				value: accion,
				label: auditoriaController.traducirAccion(accion)
			}));
	});

	const usuariosUnicos = derived(registros, ($registros) => {
		if (!$registros || !Array.isArray($registros)) return [];
		return $registros
			.map(registro => registro.creado_por_nombre || 'Sistema')
			.filter((usuario, index, array) => array.indexOf(usuario) === index)
			.sort()
			.map(usuario => ({
				value: usuario,
				label: usuario
			}));
	});

	// Categorías predefinidas
	const categorias = [
		{ value: '', label: 'Todas las categorías' },
		{ value: 'creacion', label: '✅ Creación' },
		{ value: 'modificacion', label: '✏️ Modificación' },
		{ value: 'eliminacion', label: '🗑️ Eliminación' },
		{ value: 'asistencias', label: '🕐 Asistencias' },
		{ value: 'licencias', label: '📄 Licencias' },
		{ value: 'roles', label: '👥 Roles' },
		{ value: 'autenticacion', label: '🔐 Autenticación' },
		{ value: 'aprobacion', label: '✅ Aprobaciones' },
		{ value: 'rechazo', label: '❌ Rechazos' }
	];

	// Funciones para manejar cambios en filtros
	function handleFechaDesdeChange(e) {
		// Si la nueva fecha desde es posterior a la fecha hasta, limpiar fecha hasta
		if ($filtros.fechaDesde && $filtros.fechaHasta && $filtros.fechaDesde > $filtros.fechaHasta) {
			auditoriaController.actualizarFiltros({ fechaHasta: '' });
		}
		actualizarFiltro('fechaDesde', e.target.value);
	}

	function actualizarFiltro(campo, valor) {
		auditoriaController.actualizarFiltros({ [campo]: valor });
	}

	function limpiarFiltros() {
		auditoriaController.limpiarFiltros();
	}

	// Función para obtener fecha formateada para input date
	function formatearFechaParaInput(fecha) {
		if (!fecha) return '';
		return new Date(fecha).toISOString().split('T')[0];
	}

	// Presets de fechas
	function aplicarPresetFecha(tipo) {
		const hoy = new Date();
		let fechaDesde, fechaHasta;
		
		switch(tipo) {
			case 'hoy':
				fechaDesde = fechaHasta = hoy;
				break;
			case 'ayer':
				fechaDesde = fechaHasta = new Date(hoy.getTime() - 24 * 60 * 60 * 1000);
				break;
			case 'ultima_semana':
				fechaDesde = new Date(hoy.getTime() - 7 * 24 * 60 * 60 * 1000);
				fechaHasta = hoy;
				break;
			case 'ultimo_mes':
				fechaDesde = new Date(hoy.getFullYear(), hoy.getMonth() - 1, hoy.getDate());
				fechaHasta = hoy;
				break;
		}
		
		auditoriaController.actualizarFiltros({
			fechaDesde: formatearFechaParaInput(fechaDesde),
			fechaHasta: formatearFechaParaInput(fechaHasta)
		});
	}

	// Computed para verificar si hay filtros activos
	$: hayFiltrosActivos = $filtros.modulo || $filtros.accion || $filtros.usuario || 
		$filtros.fechaDesde || $filtros.fechaHasta || $filtros.categoria;
</script>

<div class="filtros-container">
	<div class="filtros-header">
		<h3>🔧 Filtros Avanzados</h3>
		<div class="filtros-actions">
			{#if hayFiltrosActivos}
				<button class="btn-clear-all" on:click={limpiarFiltros}>
					🗑️ Limpiar todo
				</button>
			{/if}
		</div>
	</div>

	<div class="filtros-grid">
		<!-- Filtro por Módulo/Tabla -->
		<div class="filtro-group">
			<label for="modulo">📦 Módulo</label>
			<select 
				id="modulo"
				bind:value={$filtros.modulo}
				on:change={(e) => actualizarFiltro('modulo', e.target.value)}
			>
				<option value="">Todos los módulos</option>
				{#each $modulosUnicos as modulo}
					<option value={modulo.value}>{modulo.label}</option>
				{/each}
			</select>
		</div>

		<!-- Filtro por Categoría -->
		<div class="filtro-group">
			<label for="categoria">🏷️ Categoría</label>
			<select 
				id="categoria"
				bind:value={$filtros.categoria}
				on:change={(e) => actualizarFiltro('categoria', e.target.value)}
			>
				{#each categorias as categoria}
					<option value={categoria.value}>{categoria.label}</option>
				{/each}
			</select>
		</div>

		<!-- Filtro por Acción específica -->
		<div class="filtro-group">
			<label for="accion">⚡ Acción</label>
			<select 
				id="accion"
				bind:value={$filtros.accion}
				on:change={(e) => actualizarFiltro('accion', e.target.value)}
			>
				<option value="">Todas las acciones</option>
				{#each $accionesUnicas as accion}
					<option value={accion.value}>{accion.label}</option>
				{/each}
			</select>
		</div>

		<!-- Filtro por Usuario -->
		<div class="filtro-group">
			<label for="usuario">👤 Usuario</label>
			<select 
				id="usuario"
				bind:value={$filtros.usuario}
				on:change={(e) => actualizarFiltro('usuario', e.target.value)}
			>
				<option value="">Todos los usuarios</option>
				{#each $usuariosUnicos as usuario}
					<option value={usuario.value}>{usuario.label}</option>
				{/each}
			</select>
		</div>

		<!-- Filtros de Fecha -->
		<div class="filtro-group">
			<label for="fechaDesde">📅 Fecha desde</label>
			<input 
				type="date" 
				id="fechaDesde"
				bind:value={$filtros.fechaDesde}
				on:change={handleFechaDesdeChange}
			/>
		</div>

		<div class="filtro-group">
			<label for="fechaHasta">📅 Fecha hasta</label>
			<input 
				type="date" 
				id="fechaHasta"
				bind:value={$filtros.fechaHasta}
				min={$filtros.fechaDesde}
				on:change={(e) => actualizarFiltro('fechaHasta', e.target.value)}
			/>
		</div>
	</div>

	<!-- Presets de fechas -->
	<div class="presets-fechas">
		<span class="presets-label">⏰ Rangos rápidos:</span>
		<button class="preset-btn" on:click={() => aplicarPresetFecha('hoy')}>
			Hoy
		</button>
		<button class="preset-btn" on:click={() => aplicarPresetFecha('ayer')}>
			Ayer
		</button>
		<button class="preset-btn" on:click={() => aplicarPresetFecha('ultima_semana')}>
			Última semana
		</button>
		<button class="preset-btn" on:click={() => aplicarPresetFecha('ultimo_mes')}>
			Último mes
		</button>
	</div>

	<!-- Indicador de filtros activos -->
	{#if hayFiltrosActivos}
		<div class="filtros-activos">
			<span class="filtros-activos-label">🎯 Filtros aplicados:</span>
			<div class="filtros-activos-tags">
				{#if $filtros.modulo}
					<span class="tag tag-modulo">
						📦 {$modulosUnicos.find(m => m.value === $filtros.modulo)?.label}
						<button on:click={() => actualizarFiltro('modulo', '')}>×</button>
					</span>
				{/if}
				{#if $filtros.categoria}
					<span class="tag tag-categoria">
						🏷️ {categorias.find(c => c.value === $filtros.categoria)?.label}
						<button on:click={() => actualizarFiltro('categoria', '')}>×</button>
					</span>
				{/if}
				{#if $filtros.accion}
					<span class="tag tag-accion">
						⚡ {$accionesUnicas.find(a => a.value === $filtros.accion)?.label}
						<button on:click={() => actualizarFiltro('accion', '')}>×</button>
					</span>
				{/if}
				{#if $filtros.usuario}
					<span class="tag tag-usuario">
						👤 {$filtros.usuario}
						<button on:click={() => actualizarFiltro('usuario', '')}>×</button>
					</span>
				{/if}
				{#if $filtros.fechaDesde || $filtros.fechaHasta}
					<span class="tag tag-fecha">
						📅 {$filtros.fechaDesde || '...'} → {$filtros.fechaHasta || '...'}
						<button on:click={() => actualizarFiltro('fechaDesde', '') || actualizarFiltro('fechaHasta', '')}>×</button>
					</span>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.filtros-container {
		background: white;
		border-radius: 12px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
		margin-bottom: 20px;
		overflow: hidden;
		border-left: 4px solid #667eea;
	}

	.filtros-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 25px 0;
	}

	.filtros-header h3 {
		margin: 0;
		font-size: 1.2rem;
		color: #374151;
		font-weight: 600;
	}

	.btn-clear-all {
		background: #ef4444;
		color: white;
		border: none;
		padding: 8px 16px;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 500;
		transition: all 0.2s ease;
	}

	.btn-clear-all:hover {
		background: #dc2626;
		transform: translateY(-1px);
	}

	.filtros-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 20px;
		padding: 20px 25px;
	}

	.filtro-group {
		display: flex;
		flex-direction: column;
	}

	.filtro-group label {
		font-weight: 600;
		color: #374151;
		margin-bottom: 8px;
		font-size: 0.9rem;
	}

	.filtro-group select,
	.filtro-group input {
		padding: 10px 12px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 0.95rem;
		transition: all 0.3s ease;
		background: white;
	}

	.filtro-group select:focus,
	.filtro-group input:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.presets-fechas {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 0 25px 20px;
		flex-wrap: wrap;
	}

	.presets-label {
		font-size: 0.9rem;
		color: #6b7280;
		font-weight: 500;
	}

	.preset-btn {
		background: #f3f4f6;
		border: 1px solid #d1d5db;
		color: #374151;
		padding: 6px 12px;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.85rem;
		transition: all 0.2s ease;
	}

	.preset-btn:hover {
		background: #e5e7eb;
		border-color: #9ca3af;
	}

	.filtros-activos {
		background: #f8fafc;
		border-top: 1px solid #e5e7eb;
		padding: 15px 25px;
	}

	.filtros-activos-label {
		font-size: 0.9rem;
		color: #374151;
		font-weight: 600;
		display: block;
		margin-bottom: 10px;
	}

	.filtros-activos-tags {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.tag {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		background: #667eea;
		color: white;
		padding: 4px 8px;
		border-radius: 16px;
		font-size: 0.8rem;
		font-weight: 500;
	}

	.tag button {
		background: rgba(255, 255, 255, 0.3);
		border: none;
		color: white;
		border-radius: 50%;
		width: 16px;
		height: 16px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		font-size: 12px;
		line-height: 1;
	}

	.tag button:hover {
		background: rgba(255, 255, 255, 0.5);
	}

	.tag-categoria { background: #10b981; }
	.tag-accion { background: #f59e0b; }
	.tag-usuario { background: #8b5cf6; }
	.tag-fecha { background: #ef4444; }
	.tag-modulo { background: #06b6d4; }

	/* Responsive */
	@media (max-width: 768px) {
		.filtros-grid {
			grid-template-columns: 1fr;
		}

		.filtros-header {
			flex-direction: column;
			align-items: stretch;
			gap: 15px;
		}

		.presets-fechas {
			justify-content: center;
		}

		.filtros-activos-tags {
			justify-content: center;
		}
	}
</style>