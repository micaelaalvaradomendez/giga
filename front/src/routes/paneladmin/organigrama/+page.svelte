<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import OrganigramaViewer from '$lib/componentes/OrganigramaViewer.svelte';
	import AdminNodeRenderer from '$lib/componentes/AdminNodeRenderer.svelte';

	let organigramaData = null;
	let loading = true;
	let showModal = false;
	let modalType = 'add'; // 'add', 'edit', 'delete'
	let selectedNode = null;
	let selectedParent = null;
	let searchTerm = '';
	let expandedNodes = new Set();

	// Datos del formulario
	let formData = {
		nombre: '',
		tipo: 'departamento',
		descripcion: '',
		titular: '',
		email: '',
		telefono: ''
	};

	const tiposNodo = [
		{ value: 'secretaria', label: 'Secretaría' },
		{ value: 'subsecretaria', label: 'Subsecretaría' },
		{ value: 'direccion', label: 'Dirección' },
		{ value: 'direccion_general', label: 'Dirección General' },
		{ value: 'subdireccion', label: 'Subdirección' },
		{ value: 'departamento', label: 'Departamento' },
		{ value: 'division', label: 'División' }
	];

	onMount(async () => {
		if (browser) {
			await loadOrganigrama();
		}
	});

	async function loadOrganigrama() {
		try {
			const savedData = localStorage.getItem('organigrama');
			if (savedData) {
				organigramaData = JSON.parse(savedData);
			} else {
				// Cargar datos por defecto
				const { default: defaultData } = await import('$lib/data/organigrama.json');
				organigramaData = defaultData;
				saveOrganigrama();
			}
		} catch (error) {
			console.error('Error cargando organigrama:', error);
		} finally {
			loading = false;
		}
	}

	function saveOrganigrama() {
		if (browser && organigramaData) {
			organigramaData.lastUpdated = new Date().toISOString();
			organigramaData.updatedBy = 'Administrador';
			localStorage.setItem('organigrama', JSON.stringify(organigramaData));
		}
	}

	function generateId() {
		return 'node_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
	}

	function openAddModal(parent = null) {
		modalType = 'add';
		selectedParent = parent;
		resetForm();
		showModal = true;
	}

	function openEditModal(node) {
		modalType = 'edit';
		selectedNode = node;
		formData = {
			nombre: node.nombre,
			tipo: node.tipo,
			descripcion: node.descripcion,
			titular: node.titular || '',
			email: node.email || '',
			telefono: node.telefono || ''
		};
		showModal = true;
	}

	function openDeleteModal(node) {
		modalType = 'delete';
		selectedNode = node;
		showModal = true;
	}

	function resetForm() {
		formData = {
			nombre: '',
			tipo: 'departamento',
			descripcion: '',
			titular: '',
			email: '',
			telefono: ''
		};
	}

	function closeModal() {
		showModal = false;
		selectedNode = null;
		selectedParent = null;
		resetForm();
	}

	function findNodeById(root, id) {
		if (root.id === id) return root;
		if (root.children) {
			for (let child of root.children) {
				const found = findNodeById(child, id);
				if (found) return found;
			}
		}
		return null;
	}

	function findNodeParent(root, targetId, parent = null) {
		if (root.id === targetId) return parent;
		if (root.children) {
			for (let child of root.children) {
				const found = findNodeParent(child, targetId, root);
				if (found) return found;
			}
		}
		return null;
	}

	function removeNodeById(root, targetId) {
		if (root.children) {
			root.children = root.children.filter(child => {
				if (child.id === targetId) {
					return false;
				}
				removeNodeById(child, targetId);
				return true;
			});
		}
	}

	function handleSubmit() {
		if (!formData.nombre.trim()) {
			alert('El nombre es obligatorio');
			return;
		}

		if (modalType === 'add') {
			const newNode = {
				id: generateId(),
				nombre: formData.nombre.trim(),
				tipo: formData.tipo,
				nivel: selectedParent ? selectedParent.nivel + 1 : 0,
				descripcion: formData.descripcion.trim(),
				titular: formData.titular.trim(),
				email: formData.email.trim(),
				telefono: formData.telefono.trim(),
				children: []
			};

			if (selectedParent) {
				if (!selectedParent.children) {
					selectedParent.children = [];
				}
				selectedParent.children.push(newNode);
			} else {
				// Agregar como raíz (reemplazar)
				organigramaData.organigrama = newNode;
			}
		} else if (modalType === 'edit' && selectedNode) {
			selectedNode.nombre = formData.nombre.trim();
			selectedNode.tipo = formData.tipo;
			selectedNode.descripcion = formData.descripcion.trim();
			selectedNode.titular = formData.titular.trim();
			selectedNode.email = formData.email.trim();
			selectedNode.telefono = formData.telefono.trim();
		}

		saveOrganigrama();
		organigramaData = { ...organigramaData }; // Trigger reactivity
		closeModal();
	}

	function handleDelete() {
		if (selectedNode) {
			if (selectedNode.id === organigramaData.organigrama.id) {
				// Eliminar nodo raíz
				organigramaData.organigrama = null;
			} else {
				removeNodeById(organigramaData.organigrama, selectedNode.id);
			}
			
			saveOrganigrama();
			organigramaData = { ...organigramaData }; // Trigger reactivity
		}
		closeModal();
	}

	function exportData() {
		const dataStr = JSON.stringify(organigramaData, null, 2);
		const dataBlob = new Blob([dataStr], { type: 'application/json' });
		const url = URL.createObjectURL(dataBlob);
		const link = document.createElement('a');
		link.href = url;
		link.download = 'organigrama_export.json';
		link.click();
		URL.revokeObjectURL(url);
	}

	function importData(event) {
		const file = event.target.files[0];
		if (file) {
			const reader = new FileReader();
			reader.onload = (e) => {
				try {
					const importedData = JSON.parse(e.target.result);
					if (importedData.organigrama) {
						organigramaData = importedData;
						saveOrganigrama();
						organigramaData = { ...organigramaData }; // Trigger reactivity
						alert('Organigrama importado exitosamente');
					} else {
						alert('Formato de archivo inválido');
					}
				} catch (error) {
					alert('Error al importar el archivo: ' + error.message);
				}
			};
			reader.readAsText(file);
		}
		event.target.value = ''; // Reset file input
	}

	// Funciones para la vista del organigrama
	function toggleNode(nodeId) {
		if (expandedNodes.has(nodeId)) {
			expandedNodes.delete(nodeId);
		} else {
			expandedNodes.add(nodeId);
		}
		expandedNodes = expandedNodes;
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

<svelte:head>
	<title>Administrar Organigrama - GIGA</title>
</svelte:head>

<div class="admin-container">
	<div class="admin-header">
		<h1>Administrar Organigrama</h1>
		<div class="admin-actions">
			<button class="btn btn-secondary" on:click={exportData}>
				📥 Exportar
			</button>
			<label class="btn btn-secondary">
				📤 Importar
				<input type="file" accept=".json" on:change={importData} style="display: none;">
			</label>
			<button class="btn btn-primary" on:click={() => openAddModal()}>
				➕ Agregar Nodo Raíz
			</button>
		</div>
	</div>

	{#if loading}
		<div class="loading">
			<div class="spinner"></div>
			<p>Cargando organigrama...</p>
		</div>
	{:else if organigramaData?.organigrama}
		<div class="admin-content">
			<div class="organigrama-admin">
				<AdminNodeRenderer 
					node={organigramaData.organigrama}
					{expandedNodes}
					{toggleNode}
					{getNodeIcon}
					{getNodeColor}
					{openAddModal}
					{openEditModal}
					{openDeleteModal}
				/>
			</div>
		</div>
	{:else}
		<div class="no-data">
			<h3>No hay organigrama configurado</h3>
			<p>Haga clic en "Agregar Nodo Raíz" para comenzar</p>
		</div>
	{/if}
</div>

<!-- Modal -->
{#if showModal}
	<div class="modal-overlay" on:click={closeModal} role="dialog" tabindex="-1">
		<div class="modal-content" on:click|stopPropagation role="document">
			<div class="modal-header">
				<h2>
					{#if modalType === 'add'}
						Agregar Nodo
					{:else if modalType === 'edit'}
						Editar Nodo
					{:else}
						Eliminar Nodo
					{/if}
				</h2>
				<button class="modal-close" on:click={closeModal}>✕</button>
			</div>

			{#if modalType === 'delete'}
				<div class="modal-body">
					<p>¿Está seguro que desea eliminar el nodo "<strong>{selectedNode?.nombre}</strong>"?</p>
					{#if selectedNode?.children?.length}
						<p class="warning">⚠️ Este nodo tiene {selectedNode.children.length} nodos hijos que también serán eliminados.</p>
					{/if}
				</div>
				<div class="modal-footer">
					<button class="btn btn-secondary" on:click={closeModal}>Cancelar</button>
					<button class="btn btn-danger" on:click={handleDelete}>Eliminar</button>
				</div>
			{:else}
				<form on:submit|preventDefault={handleSubmit}>
					<div class="modal-body">
						<div class="form-group">
							<label for="nombre">Nombre *</label>
							<input 
								type="text" 
								id="nombre"
								bind:value={formData.nombre}
								required
								placeholder="Nombre del área/departamento"
							>
						</div>

						<div class="form-group">
							<label for="tipo">Tipo</label>
							<select id="tipo" bind:value={formData.tipo}>
								{#each tiposNodo as tipo}
									<option value={tipo.value}>{tipo.label}</option>
								{/each}
							</select>
						</div>

						<div class="form-group">
							<label for="descripcion">Descripción</label>
							<textarea 
								id="descripcion"
								bind:value={formData.descripcion}
								placeholder="Descripción de las funciones"
								rows="3"
							></textarea>
						</div>

						<div class="form-group">
							<label for="titular">Titular</label>
							<input 
								type="text" 
								id="titular"
								bind:value={formData.titular}
								placeholder="Nombre del titular del cargo"
							>
						</div>

						<div class="form-group">
							<label for="email">Email</label>
							<input 
								type="email" 
								id="email"
								bind:value={formData.email}
								placeholder="correo@ejemplo.com"
							>
						</div>

						<div class="form-group">
							<label for="telefono">Teléfono</label>
							<input 
								type="tel" 
								id="telefono"
								bind:value={formData.telefono}
								placeholder="+54 XXX XXX-XXXX"
							>
						</div>
					</div>

					<div class="modal-footer">
						<button type="button" class="btn btn-secondary" on:click={closeModal}>
							Cancelar
						</button>
						<button type="submit" class="btn btn-primary">
							{modalType === 'add' ? 'Agregar' : 'Guardar'}
						</button>
					</div>
				</form>
			{/if}
		</div>
	</div>
{/if}

<!-- El componente AdminNodeRenderer se importa al inicio -->

<style>
	.admin-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
	}

	.admin-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		padding: 1.5rem;
		background: white;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.admin-header h1 {
		color: #1e40af;
		margin: 0;
	}

	.admin-actions {
		display: flex;
		gap: 1rem;
	}

	.admin-content {
		background: white;
		border-radius: 8px;
		padding: 2rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.loading {
		text-align: center;
		padding: 4rem 2rem;
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #e2e8f0;
		border-top: 4px solid #2563eb;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 1rem;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.no-data {
		text-align: center;
		padding: 4rem 2rem;
		color: #64748b;
	}

	/* Modal styles */
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
		border-radius: 8px;
		width: 90%;
		max-width: 600px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.modal-header h2 {
		margin: 0;
		color: #1f2937;
	}

	.modal-close {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		color: #6b7280;
		padding: 0.25rem;
	}

	.modal-close:hover {
		color: #374151;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.modal-footer {
		padding: 1.5rem;
		border-top: 1px solid #e5e7eb;
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #374151;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 1rem;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #2563eb;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.warning {
		color: #dc2626;
		font-weight: 500;
		margin-top: 0.5rem;
	}

	/* Button styles */
	.btn {
		padding: 0.75rem 1rem;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-weight: 500;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		transition: all 0.2s;
	}

	.btn-primary {
		background: #2563eb;
		color: white;
	}

	.btn-primary:hover {
		background: #1d4ed8;
	}

	.btn-secondary {
		background: #6b7280;
		color: white;
	}

	.btn-secondary:hover {
		background: #4b5563;
	}

	.btn-danger {
		background: #dc2626;
		color: white;
	}

	.btn-danger:hover {
		background: #b91c1c;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.admin-container {
			padding: 1rem;
		}

		.admin-header {
			flex-direction: column;
			gap: 1rem;
			align-items: stretch;
		}

		.admin-actions {
			justify-content: center;
		}

		.modal-content {
			width: 95%;
			margin: 1rem;
		}
	}
</style>