<script>
	import { onMount } from 'svelte';
	import { asistenciaService } from '$lib/services.js';
	import { goto } from '$app/navigation';

	let tipos = [];
	let loading = false;
	let error = null;
	let searchTerm = '';

	// Modal / form
	let showForm = false;
	let isEditing = false;
	let editingId = null;
	let saving = false;
	let form = {
		codigo: '',
		descripcion: ''
	};

	onMount(() => {
		cargarTipos();
	});

	async function cargarTipos() {
		loading = true;
		error = null;
		try {
			const resp = await asistenciaService.getTiposLicencia();
			if (resp?.data?.success) {
				tipos = resp.data.data || [];
			} else {
				tipos = [];
			}
		} catch (err) {
			console.error(err);
			error = err?.response?.data?.message || err.message || 'Error cargando tipos';
		} finally {
			loading = false;
		}
	}

	function abrirAlta() {
		isEditing = false;
		editingId = null;
		form = { codigo: '', descripcion: '' };
		showForm = true;
	}

	function abrirEdicion(tipo) {
		isEditing = true;
		editingId = tipo.id_tipo_licencia || tipo.id || null;
		form = { codigo: tipo.codigo || tipo.nombre || '', descripcion: tipo.descripcion || '' };
		showForm = true;
	}

	async function guardar() {
		saving = true;
		error = null;
		try {
			if (isEditing && editingId) {
				const resp = await asistenciaService.updateTipoLicencia(editingId, form);
				if (resp?.data?.success) {
					// actualizar en lista
					tipos = tipos.map(t => (t.id_tipo_licencia === editingId || t.id === editingId) ? resp.data.data : t);
					showForm = false;
				} else {
					error = resp?.data?.message || 'Error al actualizar';
				}
			} else {
				const resp = await asistenciaService.createTipoLicencia(form);
				if (resp?.data?.success) {
					tipos = [resp.data.data, ...tipos];
					showForm = false;
				} else {
					error = resp?.data?.message || 'Error al crear tipo';
				}
			}
		} catch (err) {
			console.error(err);
			error = err?.response?.data?.message || err.message || 'Error guardando';
		} finally {
			saving = false;
		}
	}

	async function eliminar(tipo) {
		const id = tipo.id_tipo_licencia || tipo.id || null;
		if (!id) return;
		if (!confirm(`¿Eliminar el tipo de licencia "${tipo.codigo || tipo.nombre}"? Esta acción fallará si hay agentes con este tipo.`)) return;
		try {
			await asistenciaService.deleteTipoLicencia(id);
			tipos = tipos.filter(t => (t.id_tipo_licencia || t.id) !== id);
		} catch (err) {
			console.error(err);
			const msg = err?.response?.data?.message || err.message || 'No se pudo eliminar. Puede que existan agentes vinculados.';
			alert(msg);
		}
	}

	$: filtered = tipos.filter(t => {
		if (!searchTerm) return true;
		const s = searchTerm.toLowerCase();
		return (t.codigo || t.nombre || '').toLowerCase().includes(s) || (t.descripcion || '').toLowerCase().includes(s);
	});
</script>

<svelte:head>
	<title>Tipos de Licencia - GIGA</title>
</svelte:head>

<div class="page-container">
	<div class="page-header">
		<div class="header-title">
			<h1>Tipos de Licencia (Nomenclador)</h1>
		</div>
		<div class="header-actions">
			<button
				class="btn-header"
				style="background: #8b5cf6; color: white"
				on:click={cargarTipos}
				disabled={loading}
			>
				{#if loading}
					<span class="spinner"></span>
				{:else}
					🔄
				{/if}
				Actualizar
			</button>
			<button class="btn-header" on:click={abrirAlta} style="background:#22c55e;color:white">➕ Nuevo</button>
		</div>
	</div>

	<div class="page-content">
		{#if error}
			<div class="alert alert-error">
				<strong>❌ Error:</strong>
				{error}
				<button class="btn-primary" on:click={cargarTipos}>Reintentar</button>
			</div>
		{/if}

		<div class="filtros-container">
			<div class="filtros-row">
				<div class="filtro-group">
					<label for="busqueda">🔍 Buscar tipo</label>
					<input
						type="text"
						id="busqueda"
						bind:value={searchTerm}
						placeholder="Buscar por código o descripción..."
						class="input-busqueda"
					/>
				</div>
				<div class="filtro-actions">
					<button class="btn-limpiar" on:click={() => (searchTerm = '')} title="Limpiar filtros">🗑️ Limpiar</button>
				</div>
			</div>
		</div>

		{#if loading}
			<div class="loading-container">
				<div class="spinner-large"></div>
				<p>Cargando información...</p>
			</div>
		{:else if filtered.length === 0 && !loading}
			<div class="empty-state">
				<div class="empty-icon">📄</div>
				<h3>No se encontraron tipos</h3>
				<p>
					{#if searchTerm}
						No hay tipos que coincidan con "{searchTerm}".
					{:else}
						No hay tipos de licencia registrados.
					{/if}
				</p>
				{#if searchTerm}
					<button class="btn-primary" on:click={() => (searchTerm = '')}>Limpiar búsqueda</button>
				{/if}
			</div>
		{:else}
			<div class="table-container">
				<table class="roles-table">
					<thead>
						<tr>
							<th>Código</th>
							<th>Descripción</th>
							<th>Acciones</th>
						</tr>
					</thead>
					<tbody>
						{#each filtered as tipo (tipo.id_tipo_licencia || tipo.id)}
							<tr>
								<td>
									<strong>{tipo.codigo || tipo.nombre || '—'}</strong>
								</td>
								<td>{tipo.descripcion || '—'}</td>
								<td>
									<button class="btn-primary" on:click={() => abrirEdicion(tipo)}>✏️ Editar</button>
									<button class="btn-secondary" on:click={() => eliminar(tipo)} style="margin-left:6px">🗑️ Eliminar</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}

		{#if showForm}
			<div class="modal-overlay">
				<div class="modal">
					<h3>{isEditing ? 'Editar tipo de licencia' : 'Nuevo tipo de licencia'}</h3>
					{#if error}
						<div class="alert alert-error">{error}</div>
					{/if}
					<div class="form-row">
						<label>Código</label>
						<input bind:value={form.codigo} />
					</div>
					<div class="form-row">
						<label>Descripción</label>
						<textarea rows="3" bind:value={form.descripcion}></textarea>
					</div>
					<div class="form-actions">
						<button class="btn-primary" on:click={guardar} disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
						<button class="btn-limpiar" on:click={() => (showForm = false)} disabled={saving}>Cancelar</button>
					</div>
				</div>
			</div>
		{/if}

	</div>
</div>

<style>
	/* Reuse page styles found in other paneladmin pages (kept minimal here) */
	.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; padding-bottom:1rem }
	.header-title h1 { margin:0; font-size:22px }
	.header-actions { display:flex; gap:0.5rem }
	.filtros-container { background: white; border:1px solid #e9ecef; border-radius:8px; padding:1rem; margin-bottom:1rem }
	.filtros-row { display:flex; gap:1rem; align-items:end }
	.filtro-group label { font-weight:500 }
	.input-busqueda { padding:0.6rem; border:1px solid #ced4da; border-radius:6px }
	.table-container { overflow-x:auto; border-radius:12px; background:white }
	table { width:100%; border-collapse:collapse }
	th, td { padding:12px 16px; text-align:left }
	thead { background:linear-gradient(135deg,#4865e9 0%,#527ab6d0 100%); color:white }
	tbody tr:hover { background:#f8f9fa }
	.btn-header, .btn-primary, .btn-limpiar, .btn-secondary { border:none; padding:8px 12px; border-radius:6px; cursor:pointer }
	.btn-primary { background:linear-gradient(135deg,#e79043,#f39c12); color:white }
	.btn-limpiar { background:#6c757d; color:white }
	.btn-secondary { background:#6b7280; color:white }

	/* Modal simple */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:2000 }
	.modal { background:white; padding:1.25rem; border-radius:10px; width:520px; max-width:92%; box-shadow:0 10px 30px rgba(0,0,0,0.2) }
	.form-row { margin-bottom:0.75rem; display:flex; flex-direction:column }
	.form-row label { font-weight:600; margin-bottom:6px }
	.form-row input, .form-row textarea { padding:8px; border:1px solid #d1d5db; border-radius:6px }
	.form-actions { display:flex; gap:8px; justify-content:flex-end; margin-top:8px }
	.modal h3 { margin-top:0 }
</style>
