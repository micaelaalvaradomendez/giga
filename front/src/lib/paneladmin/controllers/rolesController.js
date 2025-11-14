import { writable, derived } from 'svelte/store';
import { personasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión de roles y permisos
 * Centraliza toda la lógica de negocio relacionada con la asignación de roles
 */
class RolesController {
	constructor() {
		// Stores principales
		this.agentes = writable([]);
		this.rolesDisponibles = writable([]);
		this.areasDisponibles = writable([]);
		this.loading = writable(true);
		this.error = writable(null);

		// Stores para filtrado
		this.searchTerm = writable('');
		this.filtroArea = writable('');

		// Stores para edición de roles
		this.editingRoleId = writable(null);
		this.savingRoleId = writable(null);

		// Store para usuario actual
		this.currentUser = writable(null);

		// Store derivado para agentes filtrados
		this.filteredAgentes = derived(
			[this.agentes, this.searchTerm, this.filtroArea],
			([$agentes, $searchTerm, $filtroArea]) => {
				if (!$agentes || !Array.isArray($agentes)) {
					return [];
				}

				let resultado = [...$agentes];

				// Filtrar por búsqueda
				if ($searchTerm.trim()) {
					const term = $searchTerm.toLowerCase();
					resultado = resultado.filter(agente => 
						agente.nombre?.toLowerCase().includes(term) ||
						agente.apellido?.toLowerCase().includes(term) ||
						agente.legajo?.toLowerCase().includes(term) ||
						agente.dni?.includes(term) ||
						agente.email?.toLowerCase().includes(term) ||
						agente.categoria_revista?.toLowerCase().includes(term)
					);
				}

				// Filtrar por área
				if ($filtroArea) {
					resultado = resultado.filter(agente => 
						agente.area_id === parseInt($filtroArea)
					);
				}

				return resultado;
			}
		);

		// Store derivado para estadísticas
		this.estadisticas = derived(
			[this.filteredAgentes, this.agentes],
			([$filteredAgentes, $agentes]) => ({
				mostrados: $filteredAgentes ? $filteredAgentes.length : 0,
				total: $agentes ? $agentes.length : 0
			})
		);
	}

	/**
	 * Inicializar el controlador - cargar datos iniciales
	 */
	async init() {
		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}

		// Establecer usuario actual
		this.currentUser.set(AuthService.getCurrentUser());

		await this.cargarDatos();
	}

	/**
	 * Cargar todos los datos necesarios (agentes, roles, áreas)
	 */
	async cargarDatos() {
		try {
			this.loading.set(true);
			this.error.set(null);

			// Cargar cada endpoint por separado para mejor debugging
			const [agentesResponse, rolesResponse, areasResponse] = await Promise.all([
				personasService.getAgentes(),
				personasService.getRoles(),
				personasService.getAreas()
			]);

			// Agentes vienen directamente en formato paginado
			const agentesData = agentesResponse.data?.results || agentesResponse.results || [];
			
			// Asegurar que sea array
			if (!Array.isArray(agentesData)) {
				this.agentes.set([]);
			} else {
				this.agentes.set(agentesData);
			}

			// Roles y áreas: hay que acceder correctamente a axios response
			const rolesData = rolesResponse.data?.data?.results || rolesResponse.data?.results || [];
			const areasData = areasResponse.data?.data?.results || areasResponse.data?.results || [];

			// Asegurar que sean arrays
			if (!Array.isArray(rolesData)) {
				this.rolesDisponibles.set([]);
			} else {
				this.rolesDisponibles.set(rolesData);
			}

			if (!Array.isArray(areasData)) {
				this.areasDisponibles.set([]);
			} else {
				this.areasDisponibles.set(areasData);
			}

			console.log('✅ Datos cargados correctamente');
		} catch (err) {
			console.error('❌ Error cargando datos:', err);
			
			let errorMessage = '';
			if (err.response?.status === 401) {
				throw new Error('Sesión expirada');
			} else if (err.response?.status === 403) {
				errorMessage = 'No tienes permisos para acceder a esta información.';
			} else {
				errorMessage = `Error al cargar los datos: ${err.response?.data?.message || err.message}. Por favor, intenta nuevamente.`;
			}
			
			this.error.set(errorMessage);
			throw err;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Limpiar todos los filtros aplicados
	 */
	limpiarFiltros() {
		this.searchTerm.set('');
		this.filtroArea.set('');
	}

	/**
	 * Obtener rol actual de un agente
	 */
	obtenerRolActual(agente) {
		if (agente.roles && agente.roles.length > 0) {
			const rolAgente = agente.roles[0];
			console.log('Rol actual del agente:', agente.nombre, rolAgente);
			return rolAgente;
		}
		return null;
	}

	/**
	 * Obtener nombre de un rol por su ID
	 */
	obtenerNombreRol(rolId, rolesDisponibles) {
		if (!rolId) return 'Sin rol asignado';
		// Los roles en el catálogo usan id_rol, pero en los agentes usan id
		const rol = rolesDisponibles.find(r => r.id_rol === rolId || r.id === rolId);
		return rol ? rol.nombre : 'Rol desconocido';
	}

	/**
	 * Obtener nombre de un rol por su ID usando el store actual
	 */
	obtenerNombreRolPorId(rolId) {
		let rolesDisponibles = [];
		this.rolesDisponibles.subscribe(roles => {
			rolesDisponibles = roles;
		})();
		
		if (!rolId) return 'Sin rol asignado';
		const rol = rolesDisponibles.find(r => r.id_rol === rolId || r.id === rolId);
		return rol ? rol.nombre : 'Rol desconocido';
	}

	/**
	 * Obtener nombre de un área por su ID
	 */
	obtenerNombreArea(areaId, areasDisponibles) {
		if (!areaId) return 'Sin área';
		const area = areasDisponibles.find(a => a.id_area === areaId || a.id === areaId);
		return area ? area.nombre : 'Área desconocida';
	}

	/**
	 * Obtener nombre completo de un agente
	 */
	getNombreCompleto(agente) {
		return `${agente.nombre} ${agente.apellido}`;
	}

	/**
	 * Iniciar edición de rol para un agente
	 */
	iniciarEdicionRol(agenteId) {
		this.editingRoleId.set(agenteId);
	}

	/**
	 * Cancelar edición de rol
	 */
	cancelarEdicionRol() {
		this.editingRoleId.set(null);
	}

	/**
	 * Verificar si se puede editar el rol de un agente
	 */
	puedeEditarRol(agente, currentUser) {
		// No permitir que el usuario se cambie el rol a sí mismo
		if (!currentUser) return true;
		
		// Comparar por email ya que es más confiable
		return currentUser.email !== agente.email;
	}

	/**
	 * Guardar cambio de rol para un agente
	 */
	async guardarCambioRol(agente, nuevoRolId) {
		// Verificar que no se esté cambiando el rol a sí mismo
		const currentUserValue = AuthService.getCurrentUser();
		if (!this.puedeEditarRol(agente, currentUserValue)) {
			throw new Error('No puedes cambiar tu propio rol. Solicita a otro administrador que realice esta acción.');
		}

		this.savingRoleId.set(agente.id_agente);
		
		try {
			// Obtener rol anterior para auditoría
			const rolAnterior = this.obtenerRolActual(agente);
			
			// Obtener asignaciones actuales del agente
			const asignacionesResponse = await personasService.getAsignaciones();
			const asignaciones = asignacionesResponse.data?.results || [];
			
			// Buscar TODAS las asignaciones del agente (puede tener múltiples roles)
			const asignacionesAgente = asignaciones.filter(a => 
				a.usuario === agente.id_agente
			);
			
			// Eliminar TODAS las asignaciones previas para asegurar UN SOLO ROL
			for (const asignacion of asignacionesAgente) {
				console.log(`Eliminando asignación previa: ${asignacion.id} (rol ${asignacion.rol})`);
				await personasService.deleteAsignacion(asignacion.id);
			}
			
			// Solo crear nueva asignación si se seleccionó un rol (permite "Sin rol")
			if (nuevoRolId && nuevoRolId.trim() !== '') {
				const asignacionData = {
					usuario: agente.id_agente,
					rol: parseInt(nuevoRolId)
				};

				console.log('Creando nueva asignación:', asignacionData);
				await personasService.createAsignacion(asignacionData);
			}
			
			// Recargar datos para mostrar el cambio
			await this.cargarDatos();
			this.editingRoleId.set(null);
			
			// Log del cambio para auditoría
			const rolNuevo = nuevoRolId ? this.obtenerNombreRolPorId(parseInt(nuevoRolId)) : 'Sin rol';
			const rolAnteriorNombre = rolAnterior ? rolAnterior.nombre : 'Sin rol';
			
			console.log(`🔄 Cambio de rol realizado: ${agente.nombre} ${agente.apellido} - ${rolAnteriorNombre} → ${rolNuevo}`);
			
			return { 
				success: true, 
				message: `Rol actualizado: ${rolAnteriorNombre} → ${rolNuevo}` 
			};
		} catch (err) {
			console.error('Error al cambiar rol:', err);
			console.error('Respuesta del error:', err.response?.data);
			
			let errorMessage = 'Error al cambiar el rol: ';
			
			if (err.response?.status === 400) {
				const errorData = err.response.data;
				if (errorData) {
					console.error('Detalles del error 400:', errorData);
					// Mostrar errores específicos de campo
					if (errorData.usuario) errorMessage += `Usuario: ${errorData.usuario[0]}. `;
					if (errorData.rol) errorMessage += `Rol: ${errorData.rol[0]}. `;
					if (errorData.area) errorMessage += `Área: ${errorData.area[0]}. `;
					if (errorData.non_field_errors) errorMessage += `${errorData.non_field_errors[0]}. `;
				}
				if (errorMessage === 'Error al cambiar el rol: ') {
					errorMessage += 'Datos inválidos. Verifique la información.';
				}
			} else if (err.response?.status === 403) {
				errorMessage += 'No tienes permisos para realizar esta acción.';
			} else if (err.response?.status === 404) {
				errorMessage += 'Usuario o rol no encontrado.';
			} else {
				errorMessage += (err.response?.data?.message || err.message || 'Error desconocido.');
			}
			
			throw new Error(errorMessage);
		} finally {
			this.savingRoleId.set(null);
		}
	}

	/**
	 * Manejar eventos de teclado en la edición de roles
	 */
	async handleKeyPress(event, agente, nuevoRolId) {
		if (event.key === 'Enter') {
			try {
				await this.guardarCambioRol(agente, nuevoRolId);
			} catch (error) {
				// Re-lanzar para que el componente maneje la UI del error
				throw error;
			}
		} else if (event.key === 'Escape') {
			this.cancelarEdicionRol();
		}
	}

	/**
	 * Actualizar término de búsqueda
	 */
	actualizarBusqueda(valor) {
		this.searchTerm.set(valor);
	}

	/**
	 * Actualizar filtro por área
	 */
	actualizarFiltroArea(valor) {
		this.filtroArea.set(valor);
	}

	/**
	 * Limpiar búsqueda
	 */
	limpiarBusqueda() {
		this.searchTerm.set('');
	}

	/**
	 * Obtener información del usuario actual
	 */
	getCurrentUser() {
		return AuthService.getCurrentUser();
	}
}

// Exportar una instancia única (singleton)
export const rolesController = new RolesController();