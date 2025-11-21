<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let agente = null;
	let loading = true;
	let areas = [];
	let asistencias = [];
	let licencias = [];
	let resumen = null;

	// Filtros
	let fechaSeleccionada = new Date().toISOString().split('T')[0];
	let areaSeleccionada = '';
	let tabActiva = 'todas'; // 'todas', 'completas', 'sin_salida', 'sin_entrada', 'salidas_auto', 'licencias'

	// Modal de corrección
	let modalCorreccion = false;
	let asistenciaEditando = null;
	let horaEntradaEdit = '';
	let horaSalidaEdit = '';
	let observacionEdit = '';

	onMount(async () => {
		try {
			const sessionResponse = await fetch('/api/personas/auth/check-session/', {
				credentials: 'include'
			});

			if (!sessionResponse.ok) {
				goto('/');
				return;
			}

			const sessionData = await sessionResponse.json();
			
			if (!sessionData.authenticated) {
				goto('/');
				return;
			}

		agente = sessionData.user;

		// Verificar permisos - revisar roles por nombre
		const roles = sessionData.user.roles || [];
		const roleNames = roles.map(r => r.nombre);
		
		if (!roleNames.some(nombre => ['Administrador', 'Director', 'Jefatura'].includes(nombre))) {
			goto('/inicio');
			return;
		}			await cargarAreas();
			await cargarDatos();
		} catch (error) {
			console.error('Error al verificar sesión:', error);
			goto('/');
		}
	});

	async function cargarAreas() {
		try {
			const response = await fetch('/api/personas/catalogs/areas/', {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				// El endpoint devuelve { success: true, data: { results: [...] } }
				areas = data.data?.results || data.results || data;
				console.log('✅ Áreas cargadas:', areas.length);
			}
		} catch (error) {
			console.error('Error al cargar áreas:', error);
		}
	}

	async function cargarDatos() {
		loading = true;
		try {
			await Promise.all([cargarAsistencias(), cargarResumen(), cargarLicencias()]);
		} catch (error) {
			console.error('Error al cargar datos:', error);
		} finally {
			loading = false;
		}
	}

	async function cargarAsistencias() {
		try {
			let url = `/api/asistencia/admin/listar/?fecha_desde=${fechaSeleccionada}&fecha_hasta=${fechaSeleccionada}`;

			if (areaSeleccionada) {
				url += `&area_id=${areaSeleccionada}`;
			}

			if (tabActiva !== 'todas' && tabActiva !== 'licencias') {
				const estadoMap = {
					completas: 'completa',
					sin_salida: 'sin_salida',
					sin_entrada: 'sin_entrada'
				};
				if (estadoMap[tabActiva]) {
					url += `&estado=${estadoMap[tabActiva]}`;
				}
			}

			console.log('🔍 Cargando asistencias con URL:', url);

			const response = await fetch(url, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				asistencias = data.data || [];
				console.log(`✅ Asistencias cargadas (tab: ${tabActiva}):`, asistencias.length, 'registros');
				if (tabActiva === 'sin_entrada') {
					console.log('📋 Ausentes:', asistencias.map(a => a.agente_nombre));
				}
			}
		} catch (error) {
			console.error('Error al cargar asistencias:', error);
		}
	}

	async function cargarResumen() {
		try {
			let url = `/api/asistencia/admin/resumen/?fecha=${fechaSeleccionada}`;

			if (areaSeleccionada) {
				url += `&area_id=${areaSeleccionada}`;
			}

			const response = await fetch(url, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				resumen = data.data;
			}
		} catch (error) {
			console.error('Error al cargar resumen:', error);
		}
	}

	async function cargarLicencias() {
		try {
			let url = `/api/asistencia/admin/licencias/?fecha=${fechaSeleccionada}`;

			if (areaSeleccionada) {
				url += `&area_id=${areaSeleccionada}`;
			}

			const response = await fetch(url, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				licencias = data.data || [];
			}
		} catch (error) {
			console.error('Error al cargar licencias:', error);
		}
	}

	function abrirModalCorreccion(asistencia) {
		asistenciaEditando = asistencia;
		observacionEdit = '';
		modalCorreccion = true;
	}

	function cerrarModal() {
		modalCorreccion = false;
		asistenciaEditando = null;
	}

	async function marcarEntrada() {
		if (!asistenciaEditando || !asistenciaEditando.agente_dni) {
			alert('No se puede marcar entrada sin DNI del agente');
			return;
		}

		if (asistenciaEditando.hora_entrada) {
			if (!confirm('Este agente ya tiene entrada marcada. ¿Desea marcar nuevamente?')) {
				return;
			}
		}

		try {
			const response = await fetch('/api/asistencia/marcar/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					dni: asistenciaEditando.agente_dni,
					tipo_marcacion: 'entrada',
					observacion: observacionEdit || 'Marcación corregida por administrador'
				})
			});

			const data = await response.json();

			if (response.ok && data.success) {
				alert('✅ Entrada marcada correctamente');
				cerrarModal();
				await cargarDatos();
			} else {
				alert('❌ Error: ' + (data.message || 'No se pudo marcar la entrada'));
			}
		} catch (error) {
			console.error('Error al marcar entrada:', error);
			alert('❌ Error de conexión');
		}
	}

	async function marcarSalida() {
		if (!asistenciaEditando || !asistenciaEditando.agente_dni) {
			alert('No se puede marcar salida sin DNI del agente');
			return;
		}

		if (!asistenciaEditando.hora_entrada) {
			alert('El agente debe tener una entrada marcada antes de marcar salida');
			return;
		}

		if (asistenciaEditando.hora_salida) {
			if (!confirm('Este agente ya tiene salida marcada. ¿Desea marcar nuevamente?')) {
				return;
			}
		}

		try {
			const response = await fetch('/api/asistencia/marcar/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					dni: asistenciaEditando.agente_dni,
					tipo_marcacion: 'salida',
					observacion: observacionEdit || 'Marcación corregida por administrador'
				})
			});

			const data = await response.json();

			if (response.ok && data.success) {
				alert('✅ Salida marcada correctamente');
				cerrarModal();
				await cargarDatos();
			} else {
				alert('❌ Error: ' + (data.message || 'No se pudo marcar la salida'));
			}
		} catch (error) {
			console.error('Error al marcar salida:', error);
			alert('❌ Error de conexión');
		}
	}

	function formatTime(time) {
		if (!time) return '--:--';
		return time.substring(0, 5);
	}

	function formatDate(dateStr) {
		const date = new Date(dateStr + 'T00:00:00');
		return date.toLocaleDateString('es-AR', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric'
		});
	}

	function getEstadoBadge(asistencia) {
		if (asistencia.hora_entrada && asistencia.hora_salida) {
			return { text: 'Completa', class: 'badge-success' };
		} else if (asistencia.hora_entrada && !asistencia.hora_salida) {
			return { text: 'Sin salida', class: 'badge-warning' };
		} else {
			return { text: 'Sin entrada', class: 'badge-error' };
		}
	}

	$: asistenciasFiltradas = (() => {
		if (tabActiva === 'salidas_auto') {
			return asistencias.filter((a) => a.marcacion_salida_automatica);
		}
		return asistencias;
	})();

	$: {
		// Recargar cuando cambian los filtros (solo en el browser, no en SSR)
		if (typeof window !== 'undefined' && (fechaSeleccionada || areaSeleccionada !== undefined || tabActiva)) {
			cargarDatos();
		}
	}
</script>

<svelte:head>
	<title>Gestión de Asistencias - Admin</title>
</svelte:head>

<div class="admin-container">
	<div class="header">
		<h1>Gestión de Asistencias</h1>
		<p class="subtitle">Panel de administración</p>
	</div>

	<!-- Filtros -->
	<div class="filtros-card">
		<div class="filtros-grid">
			<div class="form-group">
				<label for="fecha">Fecha</label>
				<input type="date" id="fecha" bind:value={fechaSeleccionada} />
			</div>

			<div class="form-group">
				<label for="area">Área</label>
				<select id="area" bind:value={areaSeleccionada}>
					<option value="">Todas las áreas</option>
					{#each areas as area}
						<option value={area.id_area}>{area.nombre}</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	<!-- Resumen -->
	{#if resumen}
		<div class="resumen-grid">
			<div class="resumen-card total">
				<div class="numero">{resumen.total_agentes}</div>
				<div class="label">Total Agentes</div>
			</div>
			<div class="resumen-card presentes">
				<div class="numero">{resumen.presentes}</div>
				<div class="label">Presentes</div>
			</div>
			<div class="resumen-card ausentes">
				<div class="numero">{resumen.ausentes}</div>
				<div class="label">Ausentes</div>
			</div>
			<div class="resumen-card sin-salida">
				<div class="numero">{resumen.sin_salida}</div>
				<div class="label">Sin Salida</div>
			</div>
			<div class="resumen-card automaticas">
				<div class="numero">{resumen.salidas_automaticas}</div>
				<div class="label">Salidas Auto</div>
			</div>
			<div class="resumen-card licencias">
				<div class="numero">{resumen.en_licencia}</div>
				<div class="label">En Licencia</div>
			</div>
		</div>
	{/if}

	<!-- Tabs -->
	<div class="tabs">
		<button
			class:active={tabActiva === 'todas'}
			on:click={() => {
				tabActiva = 'todas';
			}}
		>
			Todas
		</button>
		<button
			class:active={tabActiva === 'completas'}
			on:click={() => {
				tabActiva = 'completas';
			}}
		>
			Completas
		</button>
		<button
			class:active={tabActiva === 'sin_salida'}
			on:click={() => {
				tabActiva = 'sin_salida';
			}}
		>
			Sin Salida
		</button>
		<button
			class:active={tabActiva === 'sin_entrada'}
			on:click={() => {
				tabActiva = 'sin_entrada';
			}}
		>
			Sin Entrada
		</button>
		<button
			class:active={tabActiva === 'salidas_auto'}
			on:click={() => {
				tabActiva = 'salidas_auto';
			}}
		>
			Salidas Auto
		</button>
		<button
			class:active={tabActiva === 'licencias'}
			on:click={() => {
				tabActiva = 'licencias';
			}}
		>
			Licencias
		</button>
	</div>

	<!-- Contenido -->
	{#if loading}
		<div class="loading">Cargando...</div>
	{:else if tabActiva === 'licencias'}
		<!-- Lista de Licencias -->
		<div class="table-container">
			<table>
				<thead>
					<tr>
						<th>Agente</th>
						<th>DNI</th>
						<th>Área</th>
						<th>Tipo de Licencia</th>
						<th>Desde</th>
						<th>Hasta</th>
					</tr>
				</thead>
				<tbody>
					{#if licencias.length === 0}
						<tr>
							<td colspan="6" class="empty">No hay licencias en esta fecha</td>
						</tr>
					{:else}
						{#each licencias as licencia}
							<tr>
								<td>{licencia.agente_nombre}</td>
								<td>{licencia.agente_dni || 'N/A'}</td>
								<td>{licencia.area_nombre || 'N/A'}</td>
								<td>{licencia.tipo_licencia_descripcion}</td>
								<td>{formatDate(licencia.fecha_desde)}</td>
								<td>{formatDate(licencia.fecha_hasta)}</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	{:else}
		<!-- Lista de Asistencias -->
		<div class="table-container">
			<table>
				<thead>
					<tr>
						<th>Agente</th>
						<th>DNI</th>
						<th>Área</th>
						<th>Entrada</th>
						<th>Salida</th>
						<th>Estado</th>
						<th>Acciones</th>
					</tr>
				</thead>
				<tbody>
					{#if asistenciasFiltradas.length === 0}
						<tr>
							<td colspan="7" class="empty">No hay registros</td>
						</tr>
					{:else}
						{#each asistenciasFiltradas as asistencia}
							<tr>
								<td>
									{asistencia.agente_nombre}
									{#if asistencia.es_correccion}
										<span class="badge-correccion" title="Corregido por {asistencia.corregido_por_nombre}">
											✏️
										</span>
									{/if}
								</td>
								<td>{asistencia.agente_dni}</td>
								<td>{asistencia.area_nombre || 'N/A'}</td>
								<td>
									<span class="hora">{formatTime(asistencia.hora_entrada)}</span>
									{#if asistencia.marcacion_entrada_automatica}
										<span class="badge-auto">AUTO</span>
									{/if}
								</td>
								<td>
									<span class="hora">{formatTime(asistencia.hora_salida)}</span>
									{#if asistencia.marcacion_salida_automatica}
										<span class="badge-auto">AUTO</span>
									{/if}
								</td>
								<td>
									{#if asistencia.estado}
										{@const badge = getEstadoBadge(asistencia)}
										<span class="badge {badge.class}">{badge.text}</span>
									{/if}
								</td>
								<td>
									<button class="btn-editar" on:click={() => abrirModalCorreccion(asistencia)}>
										✏️ Corregir
									</button>
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<!-- Modal de Corrección -->
{#if modalCorreccion && asistenciaEditando}
	<div class="modal-overlay" on:click={cerrarModal}>
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>Marcar Asistencia</h2>
				<button class="btn-close" on:click={cerrarModal}>×</button>
			</div>

			<div class="modal-body">
				<p class="agente-info">
					<strong>{asistenciaEditando.agente_nombre}</strong><br>
					<span class="dni-info">DNI: {asistenciaEditando.agente_dni}</span><br>
					<span class="fecha-info">{formatDate(asistenciaEditando.fecha)}</span>
				</p>

				{#if asistenciaEditando.horario_esperado_entrada || asistenciaEditando.horario_esperado_salida}
					<div class="horario-esperado">
						<h3>📅 Horario Esperado</h3>
						<div class="horario-grid">
							<div class="horario-item">
								<span class="horario-label">Entrada:</span>
								<span class="horario-valor esperado">
									{asistenciaEditando.horario_esperado_entrada ? formatTime(asistenciaEditando.horario_esperado_entrada) : '--:--'}
								</span>
							</div>
							<div class="horario-item">
								<span class="horario-label">Salida:</span>
								<span class="horario-valor esperado">
									{asistenciaEditando.horario_esperado_salida ? formatTime(asistenciaEditando.horario_esperado_salida) : '--:--'}
								</span>
							</div>
						</div>
					</div>
				{/if}

				<div class="estado-actual">
					<h3>✅ Estado Actual</h3>
					<div class="estado-grid">
						<div class="estado-item">
							<span class="estado-label">Entrada:</span>
							<span class="estado-valor {asistenciaEditando.hora_entrada ? 'marcado' : 'sin-marcar'}">
								{asistenciaEditando.hora_entrada ? formatTime(asistenciaEditando.hora_entrada) : 'Sin marcar'}
							</span>
						</div>
						<div class="estado-item">
							<span class="estado-label">Salida:</span>
							<span class="estado-valor {asistenciaEditando.hora_salida ? 'marcado' : 'sin-marcar'}">
								{asistenciaEditando.hora_salida ? formatTime(asistenciaEditando.hora_salida) : 'Sin marcar'}
							</span>
						</div>
					</div>
				</div>

				<div class="form-group">
					<label for="observacion_edit">Observación (opcional)</label>
					<textarea
						id="observacion_edit"
						bind:value={observacionEdit}
						placeholder="Motivo de la corrección (ej: 'Agente olvidó marcar')"
						rows="2"
					></textarea>
				</div>

				{#if asistenciaEditando.observaciones}
					<div class="observaciones-previas">
						<strong>Observaciones anteriores:</strong>
						<p>{asistenciaEditando.observaciones}</p>
					</div>
				{/if}
			</div>

			<div class="modal-footer">
				<button class="btn-cancelar" on:click={cerrarModal}>Cancelar</button>
				<button 
					class="btn-marcar-entrada" 
					on:click={marcarEntrada}
					disabled={asistenciaEditando.hora_entrada}
				>
					🕐 Marcar Entrada
				</button>
				<button 
					class="btn-marcar-salida" 
					on:click={marcarSalida}
					disabled={!asistenciaEditando.hora_entrada || asistenciaEditando.hora_salida}
				>
					🕐 Marcar Salida
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.admin-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem 1rem;
	}

	.header {
		margin-bottom: 2rem;
	}

	.header h1 {
		font-size: 2rem;
		color: #1a1a1a;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: #666;
		font-size: 1rem;
	}

	/* Filtros */
	.filtros-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 1.5rem;
	}

	.filtros-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}

	.form-group label {
		display: block;
		font-weight: 600;
		color: #1a1a1a;
		margin-bottom: 0.5rem;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 2px solid #e0e0e0;
		border-radius: 8px;
		font-size: 1rem;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #2196f3;
	}

	/* Resumen */
	.resumen-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.resumen-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		text-align: center;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border-left: 4px solid;
	}

	.resumen-card.total {
		border-color: #607d8b;
	}
	.resumen-card.presentes {
		border-color: #4caf50;
	}
	.resumen-card.ausentes {
		border-color: #f44336;
	}
	.resumen-card.sin-salida {
		border-color: #ff9800;
	}
	.resumen-card.automaticas {
		border-color: #9c27b0;
	}
	.resumen-card.licencias {
		border-color: #2196f3;
	}

	.resumen-card .numero {
		font-size: 2.5rem;
		font-weight: bold;
		color: #1a1a1a;
	}

	.resumen-card .label {
		font-size: 0.9rem;
		color: #666;
		margin-top: 0.5rem;
	}

	/* Tabs */
	.tabs {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
		overflow-x: auto;
		background: white;
		padding: 1rem;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.tabs button {
		padding: 0.75rem 1.5rem;
		border: 2px solid #e0e0e0;
		background: white;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 500;
		color: #666;
		transition: all 0.2s;
		white-space: nowrap;
	}

	.tabs button:hover {
		border-color: #2196f3;
		color: #2196f3;
	}

	.tabs button.active {
		background: #2196f3;
		color: white;
		border-color: #2196f3;
	}

	/* Tabla */
	.table-container {
		background: white;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		overflow: hidden;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	thead {
		background: #f5f5f5;
	}

	th {
		padding: 1rem;
		text-align: left;
		font-weight: 600;
		color: #1a1a1a;
		border-bottom: 2px solid #e0e0e0;
	}

	td {
		padding: 1rem;
		border-bottom: 1px solid #f0f0f0;
		color: #1a1a1a;
	}

	tr:hover {
		background: #fafafa;
	}

	.empty {
		text-align: center;
		color: #999;
		padding: 2rem;
	}

	.hora {
		font-family: 'Courier New', monospace;
		font-weight: 600;
	}

	/* Badges */
	.badge {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.85rem;
		font-weight: 600;
	}

	.badge-success {
		background: #e8f5e9;
		color: #2e7d32;
	}

	.badge-warning {
		background: #fff3e0;
		color: #e65100;
	}

	.badge-error {
		background: #ffebee;
		color: #c62828;
	}

	.badge-auto {
		background: #e1bee7;
		color: #6a1b9a;
		padding: 0.15rem 0.5rem;
		border-radius: 8px;
		font-size: 0.7rem;
		margin-left: 0.5rem;
	}

	.badge-correccion {
		margin-left: 0.5rem;
		cursor: help;
	}

	/* Botones */
	.btn-editar {
		padding: 0.5rem 1rem;
		background: #2196f3;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.2s;
	}

	.btn-editar:hover {
		background: #1976d2;
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: #666;
		font-size: 1.2rem;
	}

	/* Modal */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal-content {
		background: white;
		border-radius: 12px;
		max-width: 500px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e0e0e0;
	}

	.modal-header h2 {
		margin: 0;
		color: #1a1a1a;
	}

	.btn-close {
		background: none;
		border: none;
		font-size: 2rem;
		cursor: pointer;
		color: #999;
		line-height: 1;
	}

	.btn-close:hover {
		color: #1a1a1a;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.agente-info {
		margin-bottom: 1.5rem;
		padding: 1rem;
		background: #f5f5f5;
		border-radius: 8px;
	}

	.observaciones-previas {
		margin-top: 1rem;
		padding: 1rem;
		background: #fff3e0;
		border-left: 4px solid #ff9800;
		border-radius: 4px;
	}

	.observaciones-previas p {
		margin: 0.5rem 0 0;
		color: #5d4037;
	}

	.modal-footer {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		padding: 1.5rem;
		border-top: 1px solid #e0e0e0;
	}

	.btn-cancelar {
		padding: 0.75rem 1.5rem;
		background: #e0e0e0;
		color: #1a1a1a;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 500;
	}

	.btn-cancelar:hover {
		background: #d0d0d0;
	}

	.btn-guardar,
	.btn-marcar-entrada,
	.btn-marcar-salida {
		padding: 0.75rem 1.5rem;
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-weight: 600;
		transition: all 0.3s ease;
	}

	.btn-guardar {
		background: #4caf50;
		cursor: pointer;
		font-weight: 500;
	}

	.btn-guardar:hover {
		background: #45a049;
	}

	.btn-marcar-entrada {
		background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
	}

	.btn-marcar-entrada:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
	}

	.btn-marcar-salida {
		background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
	}

	.btn-marcar-salida:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
	}

	.btn-marcar-entrada:disabled,
	.btn-marcar-salida:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	.dni-info,
	.fecha-info {
		display: block;
		font-size: 0.9rem;
		color: #666;
		margin-top: 0.3rem;
	}

	.horario-esperado {
		margin: 1.5rem 0;
		padding: 1rem;
		background: linear-gradient(135deg, #fff7e6 0%, #fff3dc 100%);
		border-radius: 8px;
		border: 2px solid #ffc107;
	}

	.horario-esperado h3 {
		margin: 0 0 1rem 0;
		font-size: 1rem;
		color: #8a6d3b;
		font-weight: 600;
	}

	.horario-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.horario-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.horario-label {
		font-weight: 600;
		font-size: 0.85rem;
		color: #8a6d3b;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.horario-valor {
		padding: 0.5rem;
		border-radius: 6px;
		text-align: center;
		font-weight: 600;
		font-size: 1.1rem;
		font-family: 'Courier New', monospace;
	}

	.horario-valor.esperado {
		background: #fff;
		color: #8a6d3b;
		border: 2px solid #ffc107;
	}

	.estado-actual {
		margin: 1.5rem 0;
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 8px;
		border: 2px solid #e0e0e0;
	}

	.estado-actual h3 {
		margin: 0 0 1rem 0;
		font-size: 1rem;
		color: #333;
	}

	.estado-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.estado-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.estado-label {
		font-weight: 600;
		font-size: 0.85rem;
		color: #666;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.estado-valor {
		padding: 0.5rem;
		border-radius: 6px;
		text-align: center;
		font-weight: 600;
		font-size: 1.1rem;
	}

	.estado-valor.marcado {
		background: #d4edda;
		color: #155724;
		border: 2px solid #c3e6cb;
	}

	.estado-valor.sin-marcar {
		background: #f8d7da;
		color: #721c24;
		border: 2px solid #f5c6cb;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.resumen-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.tabs {
			flex-wrap: wrap;
		}

		table {
			font-size: 0.9rem;
		}

		th,
		td {
			padding: 0.75rem 0.5rem;
		}
	}
</style>
