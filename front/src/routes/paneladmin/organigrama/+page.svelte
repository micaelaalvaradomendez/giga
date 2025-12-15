<script>
	import { onMount } from "svelte";
	import { browser } from "$app/environment";
	import OrganigramaViewer from "$lib/componentes/admin/organigrama/OrganigramaViewer.svelte";
	import AdminNodeRenderer from "$lib/componentes/admin/organigrama/AdminNodeRenderer.svelte";
	import ModalEliminar from "$lib/componentes/admin/parametros/ModalEliminar.svelte";
	import { organigramaController } from "$lib/paneladmin/controllers";
	import { API_BASE_URL } from "$lib/api";
	import ModalAlert from "$lib/componentes/ModalAlert.svelte";
	import { modalAlert, showAlert, showConfirm } from "$lib/stores/modalAlertStore.js";

	let organigramaData = null;
	let loading = true;
	let showModal = false;
	let modalType = "add"; // 'add', 'edit', 'delete'
	let selectedNode = null;
	let selectedParent = null;
	let searchTerm = "";
	let expandedNodes = new Set();
	let allNodes = []; // Lista plana de todos los nodos para el selector
	let showParentSelector = false;
	let fileInput;
	let showUnsavedWarning = false; // Indicar si hay cambios pendientes de guardar
	let showDeleteModal = false;
	let nodeToDelete = null;

	// Datos del formulario
	let formData = {
		nombre: "",
		tipo: "departamento",
		descripcion: "",
		titular: "",
		email: "",
		telefono: "",
	};

	const tiposNodo = [
		{ value: "secretaria", label: "Secretaría" },
		{ value: "subsecretaria", label: "Subsecretaría" },
		{ value: "direccion", label: "Dirección" },
		{ value: "direccion_general", label: "Dirección General" },
		{ value: "subdireccion", label: "Subdirección" },
		{ value: "departamento", label: "Departamento" },
		{ value: "division", label: "División" },
	];

	onMount(async () => {
		if (browser) {
			await loadOrganigrama();

			// Recargar cuando la página vuelve a ser visible
			const handleVisibilityChange = () => {
				if (document.visibilityState === "visible") {
					loadOrganigrama();
				}
			};

			const handleFocus = () => {
				loadOrganigrama();
			};

			document.addEventListener(
				"visibilitychange",
				handleVisibilityChange,
			);
			window.addEventListener("focus", handleFocus);

			return () => {
				document.removeEventListener(
					"visibilitychange",
					handleVisibilityChange,
				);
				window.removeEventListener("focus", handleFocus);
			};
		}
	});

	async function loadOrganigrama() {
		try {
			loading = true;
			console.log("🔄 Cargando organigrama desde API...");

			// CARGAR DESDE API DEL BACKEND
			const response = await fetch(
				`${API_BASE_URL}/personas/organigrama/`,
				{
					method: "GET",
					credentials: "include",
				},
			);

			console.log("📡 Response status:", response.status);

			if (response.ok) {
				const result = await response.json();
				console.log("📥 API Response:", result);

				if (result.success) {
					// Convertir estructura de la API al formato esperado por el frontend
					organigramaData = {
						version: result.data.version,
						lastUpdated: result.data.actualizado_en,
						updatedBy: result.data.creado_por,
						organigrama: result.data.estructura,
					};

					console.log("✅ Organigrama cargado:", organigramaData);
					console.log(
						"✅ Estructura length:",
						result.data.estructura?.length,
					);
				} else {
					console.error(
						"❌ API success=false, message:",
						result.message,
					);
					throw new Error(
						result.message || "Error al cargar organigrama",
					);
				}
			} else {
				console.error(
					"❌ Response not ok:",
					response.status,
					response.statusText,
				);
				throw new Error("Error de conexión con el servidor");
			}

			// Actualizar lista de nodos para el selector
			updateNodesList();

			console.log(
				"✅ Lista de nodos actualizada:",
				allNodes.length,
				"nodos",
			);
		} catch (error) {
			console.error("❌ Error cargando organigrama:", error);

			// Datos de fallback básicos para mostrar algo en caso de error
			organigramaData = {
				version: "1.0.0",
				lastUpdated: new Date().toISOString(),
				updatedBy: "Sistema",
				organigrama: [
					{
						id: "root",
						tipo: "secretaria",
						nombre: "Secretaría de Protección Civil",
						titular: "No disponible",
						email: "",
						telefono: "",
						descripcion: "Organigrama no disponible temporalmente",
						nivel: 0,
						children: [],
					},
				],
			};
			updateNodesList();
			console.log("✅ Usando datos de fallback básicos");
		} finally {
			loading = false;
		}
	}

	async function sincronizarConAreas() {
		if (!browser) return;

		const confirmado = await showConfirm(
			"¿Sincronizar el organigrama con la estructura actual de áreas? Esto reemplazará el organigrama actual.",
			"Sincronizar con Áreas",
			"Sincronizar",
			"Cancelar"
		);
		
		if (!confirmado) {
			return;
		}

		try {
			loading = true;

			const response = await fetch(
				`${API_BASE_URL}/personas/organigrama/sincronizar/`,
				{
					method: "POST",
					credentials: "include",
					headers: {
						"Content-Type": "application/json",
					},
				},
			);

			if (response.ok) {
				const result = await response.json();
				if (result.success) {
					console.log("✅ Organigrama sincronizado correctamente");
					await showAlert(
						"Organigrama sincronizado exitosamente con las áreas del sistema",
						"success",
						"Éxito"
					);

					// Recargar el organigrama
					await loadOrganigrama();
					return true;
				} else {
					throw new Error(
						result.message || "Error al sincronizar organigrama",
					);
				}
			} else {
				throw new Error("Error de conexión con el servidor");
			}
		} catch (error) {
			console.error("❌ Error sincronizando organigrama:", error);
			await showAlert(`Error al sincronizar: ${error.message}`, "error", "Error");
			return false;
		} finally {
			loading = false;
		}
	}

	async function saveOrganigrama() {
		if (!browser || !organigramaData) return;

		try {
			loading = true;

			// GUARDAR EN LA API DEL BACKEND
			const response = await fetch(
				`${API_BASE_URL}/personas/organigrama/save/`,
				{
					method: "POST",
					credentials: "include",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						nombre: "Secretaría de Protección Civil",
						estructura: organigramaData.organigrama,
						version: organigramaData.version || "1.0.0",
						creado_por: "Administrador",
					}),
				},
			);

			if (response.ok) {
				const result = await response.json();
				if (result.success) {
					console.log("✅ Organigrama guardado correctamente");

					// Actualizar datos locales con la respuesta del servidor
					organigramaData.lastUpdated = result.data.actualizado_en;
					organigramaData.updatedBy = result.data.creado_por;
					showUnsavedWarning = false;

					updateNodesList();
					return true;
				} else {
					throw new Error(
						result.message || "Error al guardar organigrama",
					);
				}
			} else {
				throw new Error("Error de conexión con el servidor");
			}
		} catch (error) {
			console.error("❌ Error guardando organigrama:", error);
			await showAlert("Error al guardar los cambios: " + error.message, "error", "Error");
			return false;
		} finally {
			loading = false;
		}
	}

	function updateNodesList() {
		allNodes = [];
		if (organigramaData?.organigrama) {
			// Convertir estructura jerárquica a lista plana
			function flattenNodes(node, path = "") {
				const currentPath = path
					? `${path} > ${node.nombre}`
					: node.nombre;
				allNodes.push({
					id: node.id,
					nombre: node.nombre,
					tipo: node.tipo,
					nivel: node.nivel || 0,
					path: currentPath,
					node: node,
				});

				if (node.children) {
					node.children.forEach((child) =>
						flattenNodes(child, currentPath),
					);
				}
			}

			if (Array.isArray(organigramaData.organigrama)) {
				organigramaData.organigrama.forEach((root) =>
					flattenNodes(root),
				);
			} else {
				flattenNodes(organigramaData.organigrama);
			}
		}
	}

	function generateId() {
		return (
			"node_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9)
		);
	}

	function openAddModal(parent = null) {
		modalType = "add";
		selectedParent = parent;
		showParentSelector = !parent; // Mostrar selector solo si no se especifica padre
		resetForm();
		showModal = true;
	}

	function openEditModal(node) {
		modalType = "edit";
		selectedNode = node;
		formData = {
			nombre: node.nombre,
			tipo: node.tipo,
			descripcion: node.descripcion,
			titular: node.titular || "",
			email: node.email || "",
			telefono: node.telefono || "",
		};
		showModal = true;
	}

	function openDeleteModal(node) {
		nodeToDelete = node;
		showDeleteModal = true;
	}

	function closeDeleteModal() {
		showDeleteModal = false;
		nodeToDelete = null;
	}

	function resetForm() {
		formData = {
			nombre: "",
			tipo: "departamento",
			descripcion: "",
			titular: "",
			email: "",
			telefono: "",
		};
	}

	function closeModal() {
		showModal = false;
		selectedNode = null;
		selectedParent = null;
		showParentSelector = false;
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
			root.children = root.children.filter((child) => {
				if (child.id === targetId) {
					return false;
				}
				removeNodeById(child, targetId);
				return true;
			});
		}
	}

	async function handleSubmit() {
		if (!formData.nombre.trim()) {
			await showAlert("El nombre es obligatorio", "warning", "Advertencia");
			return;
		}

		if (modalType === "add") {
			const newNode = {
				id: generateId(),
				nombre: formData.nombre.trim(),
				tipo: formData.tipo,
				nivel: selectedParent ? selectedParent.nivel + 1 : 0,
				descripcion: formData.descripcion.trim(),
				titular: formData.titular.trim(),
				email: formData.email.trim(),
				telefono: formData.telefono.trim(),
				children: [],
			};

			if (selectedParent) {
				// Agregar como hijo del nodo seleccionado
				if (!selectedParent.children) {
					selectedParent.children = [];
				}
				selectedParent.children.push(newNode);
			} else {
				// Agregar como nodo raíz - convertir a array si es necesario
				if (!organigramaData.organigrama) {
					organigramaData.organigrama = [];
				}

				if (Array.isArray(organigramaData.organigrama)) {
					organigramaData.organigrama.push(newNode);
				} else {
					// Convertir nodo único a array
					const currentRoot = organigramaData.organigrama;
					organigramaData.organigrama = [currentRoot, newNode];
				}
			}
		} else if (modalType === "edit" && selectedNode) {
			selectedNode.nombre = formData.nombre.trim();
			selectedNode.tipo = formData.tipo;
			selectedNode.descripcion = formData.descripcion.trim();
			selectedNode.titular = formData.titular.trim();
			selectedNode.email = formData.email.trim();
			selectedNode.telefono = formData.telefono.trim();
		}

		// � SOLO ACTUALIZAR LOCALMENTE (no guardar en API todavía)
		organigramaData = { ...organigramaData }; // Trigger reactivity
		updateNodesList();
		closeModal();

		// Mostrar mensaje de que hay cambios pendientes
		showUnsavedWarning = true;
	}

	async function handleDelete() {
		if (nodeToDelete) {
			if (Array.isArray(organigramaData.organigrama)) {
				// Eliminar de array de raíces
				organigramaData.organigrama =
					organigramaData.organigrama.filter(
						(root) => root.id !== nodeToDelete.id,
					);
				// También eliminar de hijos si está anidado
				organigramaData.organigrama.forEach((root) => {
					removeNodeById(root, nodeToDelete.id);
				});
			} else {
				// Estructura de nodo único
				if (nodeToDelete.id === organigramaData.organigrama.id) {
					organigramaData.organigrama = null;
				} else {
					removeNodeById(
						organigramaData.organigrama,
						nodeToDelete.id,
					);
				}
			}

			// SOLO ACTUALIZAR LOCALMENTE
			organigramaData = { ...organigramaData }; // Trigger reactivity
			updateNodesList();
			showUnsavedWarning = true; // Marcar cambios pendientes
			closeDeleteModal();
		}
	}

	function exportData() {
		const dataStr = JSON.stringify(organigramaData, null, 2);
		const dataBlob = new Blob([dataStr], { type: "application/json" });
		const url = URL.createObjectURL(dataBlob);
		const link = document.createElement("a");
		link.href = url;
		link.download = "organigrama_export.json";
		link.click();
		URL.revokeObjectURL(url);
	}

	async function importData(event) {
		const file = event.target.files[0];
		if (file) {
			const reader = new FileReader();
			reader.onload = async (e) => {
				try {
					const importedData = JSON.parse(e.target.result);
					if (importedData.organigrama) {
						organigramaData = importedData;

						// GUARDAR CON PERSISTENCIA REAL
						const saved = await saveOrganigrama();
						if (saved) {
							organigramaData = { ...organigramaData }; // Trigger reactivity
							await showAlert("✅ Organigrama importado exitosamente", "success", "Éxito");
						}
					} else {
						await showAlert("❌ Formato de archivo inválido", "error", "Error");
					}
				} catch (error) {
					await showAlert("❌ Error al importar el archivo: " + error.message, "error", "Error");
				}
			};
			reader.readAsText(file);
		}
		event.target.value = ""; // Reset file input
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

<svelte:head>
	<title>Administrar Organigrama - GIGA</title>
</svelte:head>

<div class="admin-container">
	<div class="admin-header">
		<div class="admin-header-title">
			<h1>Administrar Organigrama</h1>
		</div>
		{#if showUnsavedWarning}
			<div class="unsaved-warning">
				⚠️ <strong>Hay cambios sin guardar</strong> - Haga clic en "💾 Guardar
				Cambios" para persistir en el sistema
			</div>
		{/if}

		<div class="admin-actions">
			<button class="btn btn-primary" on:click={() => openAddModal()}>
				➕ Agregar
			</button>
			<button
				class="btn btn-success"
				on:click={saveOrganigrama}
				disabled={loading}
			>
				💾 Guardar
			</button>
			<button
				class="btn"
				style="background: #3b82f6; color: white;"
				on:click={sincronizarConAreas}
				disabled={loading}
				title="Sincronizar organigrama con la estructura de áreas del sistema"
			>
				🔄 Sincronizar con Áreas
			</button>
			<input
				type="file"
				accept=".json"
				style="display: none;"
				on:change={importData}
				bind:this={fileInput}
			/>
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
				{#if Array.isArray(organigramaData.organigrama)}
					{#each organigramaData.organigrama as rootNode}
						<div class="root-node-container">
							<AdminNodeRenderer
								node={rootNode}
								{expandedNodes}
								{toggleNode}
								{getNodeIcon}
								{getNodeColor}
								{detectarTipoArea}
								{openAddModal}
								{openEditModal}
								{openDeleteModal}
							/>
						</div>
					{/each}
				{:else}
					<AdminNodeRenderer
						node={organigramaData.organigrama}
						{expandedNodes}
						{toggleNode}
						{getNodeIcon}
						{getNodeColor}
						{detectarTipoArea}
						{openAddModal}
						{openEditModal}
						{openDeleteModal}
					/>
				{/if}
			</div>
		</div>
	{:else}
		<div
			class="no-data"
			style="background: #fee2e2; padding: 20px; border-radius: 8px; text-align: center;"
		>
			<h3>❌ No hay organigrama configurado</h3>
			<p>Haga clic en "Agregar" para comenzar</p>
		</div>
	{/if}
</div>

<ModalEliminar
	isOpen={showDeleteModal}
	isDeleting={false}
	itemToDelete={nodeToDelete}
	type="nodo"
	on:cerrar={closeDeleteModal}
	on:confirmar={handleDelete}
/>

<!-- Modal de alertas -->
<ModalAlert
	bind:show={$modalAlert.show}
	type={$modalAlert.type}
	title={$modalAlert.title}
	message={$modalAlert.message}
	showConfirmButton={$modalAlert.showConfirmButton}
	confirmText={$modalAlert.confirmText}
	showCancelButton={$modalAlert.showCancelButton}
	cancelText={$modalAlert.cancelText}
	on:confirm={() => $modalAlert.onConfirm && $modalAlert.onConfirm()}
	on:cancel={() => $modalAlert.onCancel && $modalAlert.onCancel()}
/>

<!-- Modal -->
{#if showModal}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={closeModal}>
		<div
			class="modal-content"
			on:click|stopPropagation
			role="dialog"
			aria-modal="true"
			aria-labelledby="modal-title"
			tabindex="-1"
		>
			<div class="modal-header">
				<h2 id="modal-title">
					{#if modalType === "add"}
						➕ Agregar
					{:else}
						✏️ Editar
					{/if}
				</h2>
				<button type="button" class="modal-close" on:click={closeModal}>
					✕
				</button>
			</div>

			<form on:submit|preventDefault={handleSubmit}>
				<div class="modal-body">
					{#if showParentSelector}
						<div class="form-group">
							<label for="parent">Padre (opcional)</label>
							<select id="parent" bind:value={selectedParent}>
								<option value={null}
									>-- Raíz (sin padre) --</option
								>
								{#each allNodes as nodeOption}
									<option value={nodeOption.node}>
										{nodeOption.path} ({nodeOption.tipo})
									</option>
								{/each}
							</select>
							<small class="form-help">
								Seleccione dónde agregar el nuevo. Si no
								selecciona nada, será una raíz.
							</small>
						</div>
					{:else if selectedParent}
						<div class="form-group">
							<label for="nodo-padre">Padre Seleccionado:</label>
							<div class="selected-parent">
								{getNodeIcon(selectedParent.tipo)}
								{selectedParent.nombre}
							</div>
						</div>
					{/if}

					<div class="form-group">
						<label for="nombre">Nombre *</label>
						<input
							type="text"
							id="nombre"
							bind:value={formData.nombre}
							required
							placeholder="Nombre del área/departamento"
						/>
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
						/>
					</div>

					<div class="form-group">
						<label for="email">Email</label>
						<input
							type="email"
							id="email"
							bind:value={formData.email}
							placeholder="correo@ejemplo.com"
						/>
					</div>

					<div class="form-group">
						<label for="telefono">Teléfono</label>
						<input
							type="tel"
							id="telefono"
							bind:value={formData.telefono}
							placeholder="+54 XXX XXX-XXXX"
						/>
					</div>
				</div>

				<div class="modal-footer">
					<button
						type="button"
						class="btn-cancel"
						on:click={closeModal}
					>
						Cancelar
					</button>
					<button type="submit" class="btn-save">
						{modalType === "add" ? "Agregar" : "Guardar"}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- El componente AdminNodeRenderer se importa al inicio -->

<style>
	.admin-container {
		width: 100%;
		max-width: 1660px;
		margin: 0 auto;
		padding: 1.5rem 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		box-sizing: border-box;
	}

	.admin-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin: 0;
		padding: 0 2rem 20px 2rem; 
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		gap: 2rem;
	}

	.admin-header-title {
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 40px;
		margin: 0 40px 0 0;
		max-width: 1000px;
		border-radius: 28px;
		overflow: hidden;
		text-align: center;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 10px 30px rgba(30, 64, 175, 0.4);
	}

	.admin-header-title ::before {
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

	.admin-header h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 30px;
		letter-spacing: 0.2px;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: inline-block;
	}

	.admin-header-title h1::after {
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

	.unsaved-warning {
		background: #fef3c7;
		border: 2px solid #f59e0b;
		color: #92400e;
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1rem;
		text-align: center;
		font-weight: 500;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0% {
			opacity: 1;
		}
		50% {
			opacity: 0.8;
		}
		100% {
			opacity: 1;
		}
	}

	.admin-actions {
		display: flex;
		gap: 1rem;
	}

	.admin-content {
		background: white;
		border-radius: 8px;
		padding: 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		width: 100%;
		box-sizing: border-box;
	}

	.organigrama-admin {
		width: 100%;
	}

	.root-node-container {
		width: 100%;
	}

	/* Hacer que los nodos admin ocupen todo el ancho */
	.organigrama-admin :global(.admin-node-container) {
		width: 100%;
		max-width: none;
	}

	.organigrama-admin :global(.admin-node) {
		width: 100%;
		box-sizing: border-box;
	}

	.loading {
		text-align: center;
		padding: 4rem 2rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
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
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
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
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-content::-webkit-scrollbar {
		display: none;
	}

	.modal-header {
		padding: 20px 25px;
		border-bottom: 1px solid #e9ecef;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.modal-header h2 {
		margin: 0;
		color: #ffffff;
	}

	.modal-close {
		background: none;
		border: none;
		color: white;
		font-size: 24px;
		cursor: pointer;
		padding: 0;
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		transition: all 0.3s ease;
	}

	.modal-close:hover {
		background: rgba(255, 255, 255, 0.2);
	}
	.modal-body {
		padding: 1.25rem 1.5rem 0.75rem 1.5rem;
	}

	.modal-footer {
		padding: 1.5rem;
		border-top: 1px solid #e5e7eb;
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
	}

	.form-group {
		margin-bottom: auto;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: 600;
		color: #495057;
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		width: 100%;
		padding: 10px 12px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		box-sizing: border-box;
		margin-bottom: 10px;
		font-size: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: #2563eb;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.form-help {
		color: #6b7280;
		font-size: 0.875rem;
		margin-top: 0;
		display: block;
		margin-bottom: 10px;
	}

	.selected-parent {
		margin-top: 5px;
		padding: 0.5rem;
		background: #4747472a;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-weight: 500;
		margin-bottom: 10px;
	}

	.root-node-container {
		margin-bottom: 2rem;
		padding: 1rem;
		border: 2px dashed rgba(78, 78, 78, 0.103);
		border-radius: 8px;
		background: rgba(163, 163, 163, 0.226);
	}

	.root-node-container:first-child {
		margin-top: 0;
	}

	/* Button styles */
	.btn {
		padding: 15px 20px;
		border: none;
		border-radius: 10px;
		cursor: pointer;
		font-weight: 600;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
		gap: 10px;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.247);
	}

	.btn-primary {
		margin: 0 0 0 15px;
		background: #2563eb;
		color: white;
	}

	.btn-primary:hover {
		background: #1d4ed8;
	}

	.btn-success {
		background: #10b981;
		color: white;
	}

	.btn-success:hover {
		background: #059669;
	}

	.btn-success:disabled {
		background: #9ca3af;
		cursor: not-allowed;
	}

	.btn-cancel,
	.btn-save {
		padding: 12px 24px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-cancel {
		background: #6c757d;
		color: white;
	}

	.btn-cancel:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-2px);
	}

	.btn-save {
		background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
		color: white;
	}

	.btn-save:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
	}

	.btn-save:disabled,
	.btn-cancel:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.admin-container {
			padding: 1rem;
			overflow-x: hidden;
		}

		.admin-header {
			flex-direction: column;
			gap: 1rem;
			align-items: center; /* Centrar todo el header */
			margin: 0 0 1.5rem 0;
			padding-bottom: 0;
			width: 100%;
		}

		.admin-header-title {
			padding: 1.5rem 1rem;
			margin: 0;
			border-radius: 16px;
			width: 100%;
			text-align: center;
			box-sizing: border-box;
		}

		.admin-header-title h1 {
			font-size: 1.5rem;
			margin: 0;
			width: 100%;
		}

		.admin-actions {
			flex-direction: column;
			gap: 0.75rem;
			width: 100%;
			align-items: center;
		}

		.admin-actions .btn {
			width: 100%;
			font-size: 1rem;
			padding: 14px;
			text-align: center;
			justify-content: center;
			margin: 0 !important;
			border-radius: 10px;
		}

		.admin-content {
			padding: 1rem;
			border-radius: 12px;
			width: 100%;
			box-sizing: border-box;
		}

		.organigrama-admin {
			overflow-x: auto;
			width: 100%;
		}

		.root-node-container {
			padding: 0.5rem;
			margin-bottom: 1rem;
			width: 100%;
			box-sizing: border-box;
		}

		.unsaved-warning {
			font-size: 0.9rem;
			padding: 1rem;
			margin-bottom: 1rem;
			width: 100%;
			box-sizing: border-box;
		}

		.modal-overlay {
			padding: 0.5rem;
		}

		.modal-content {
			width: 100%;
			max-width: 100%;
			margin: 0;
			max-height: 90vh;
			border-radius: 12px;
		}

		.modal-header {
			padding: 1rem;
		}

		.modal-header h2 {
			font-size: 1.2rem;
		}

		.modal-body {
			padding: 1rem;
		}

		.modal-footer {
			padding: 1rem;
			flex-direction: column;
			gap: 0.5rem;
		}

		.btn-cancel,
		.btn-save {
			width: 100%;
			padding: 12px;
		}
	}

	@media (max-width: 480px) {
		.admin-container {
			padding: 0.5rem;
		}

		.admin-header-title {
			padding: 16px 12px;
			border-radius: 14px;
		}

		.admin-header-title h1 {
			font-size: 18px;
		}

		.admin-actions .btn {
			flex: 1 1 100%;
			font-size: 0.8rem;
		}

		.admin-content {
			padding: 0.75rem;
		}

		.form-group label {
			font-size: 0.9rem;
		}

		.form-group input,
		.form-group select,
		.form-group textarea {
			padding: 0.6rem;
			font-size: 0.9rem;
		}
	}
</style>
