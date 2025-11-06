import { writable, derived } from 'svelte/store';
import { personasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión de usuarios/agentes
 * Centraliza toda la lógica de negocio relacionada con la gestión de agentes
 */
class UsuariosController {
	constructor() {
		// Stores principales
		this.agentes = writable([]);
		this.areasDisponibles = writable([]);
		this.rolesDisponibles = writable([]);
		this.loading = writable(true);
		this.error = writable(null);

		// Stores para filtrado
		this.busqueda = writable('');
		this.filtroArea = writable('');

		// Stores para modales
		this.modalVerAgente = writable({ isOpen: false, agente: null });
		this.modalEditarAgente = writable({ isOpen: false, agente: null, isSaving: false });
		this.modalEliminarAgente = writable({ isOpen: false, agente: null, isDeleting: false });
		this.modalAgregarAgente = writable({ isOpen: false, isSaving: false });

		// Store derivado para agentes filtrados
		this.agentesFiltrados = derived(
			[this.agentes, this.busqueda, this.filtroArea],
			([$agentes, $busqueda, $filtroArea]) => {
				if (!$agentes || !Array.isArray($agentes)) {
					return [];
				}

				return $agentes.filter(agente => {
					// Filtro por búsqueda (nombre, apellido, dni, email, legajo)
					const textoBusqueda = $busqueda.toLowerCase().trim();
					const coincideBusqueda = !textoBusqueda || 
						(agente.nombre && agente.nombre.toLowerCase().includes(textoBusqueda)) ||
						(agente.apellido && agente.apellido.toLowerCase().includes(textoBusqueda)) ||
						(agente.dni && agente.dni.includes(textoBusqueda)) ||
						(agente.email && agente.email.toLowerCase().includes(textoBusqueda)) ||
						(agente.legajo && agente.legajo.toLowerCase().includes(textoBusqueda));

					// Filtro por área - comparar con area_id
					const coincideArea = !$filtroArea || 
						(agente.area_id && agente.area_id.toString() === $filtroArea.toString());

					return coincideBusqueda && coincideArea;
				});
			}
		);

		// Store derivado para estadísticas
		this.estadisticas = derived(
			[this.agentesFiltrados],
			([$agentesFiltrados]) => {
				if (!$agentesFiltrados || !Array.isArray($agentesFiltrados)) {
					return {
						total: 0,
						epu: 0,
						pomys: 0,
						payt: 0,
						conRoles: 0,
						administradores: 0
					};
				}

				return {
					total: $agentesFiltrados.length,
					epu: $agentesFiltrados.filter(a => a.agrupacion === 'EPU').length,
					pomys: $agentesFiltrados.filter(a => a.agrupacion === 'POMYS').length,
					payt: $agentesFiltrados.filter(a => a.agrupacion === 'PAYT').length,
					conRoles: $agentesFiltrados.filter(a => a.roles && a.roles.length > 0).length,
					administradores: $agentesFiltrados.filter(a => a.roles && a.roles.some(r => r.nombre === 'Administrador')).length
				};
			}
		);
	}

	/**
	 * Inicializar el controlador - cargar datos iniciales
	 */
	async init() {
		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}

		console.log('🚀 Iniciando carga de datos de usuarios...');

		try {
			// Cargar catálogos (áreas y roles) primero
			await this.cargarAreas();
			await this.cargarRoles();

			// Cargar agentes
			await this.cargarAgentes();

			console.log('✅ Carga inicial completada');
		} catch (error) {
			console.error('❌ Error en inicialización:', error);
			this.error.set('Error al inicializar: ' + error.message);
			throw error;
		}
	}

	/**
	 * Cargar todos los agentes del sistema
	 */
	async cargarAgentes() {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const response = await personasService.getAgentes();
			
			// Axios pone la respuesta del servidor en response.data
			// La API devuelve: {count, next, previous, results}
			if (response && response.data) {
				const agentesData = response.data.results || [];
				this.agentes.set(agentesData);
				console.log('Agentes cargados:', agentesData.length);
			} else {
				console.error('Estructura de respuesta inesperada:', response);
				throw new Error('Respuesta inválida del servidor');
			}
		} catch (err) {
			console.error('Error cargando agentes:', err);
			const errorMessage = 'Error al cargar los agentes: ' + err.message;
			this.error.set(errorMessage);
			this.agentes.set([]);
			throw err;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Cargar áreas disponibles para filtros
	 */
	async cargarAreas() {
		try {
			const response = await personasService.getAreas();
			console.log('🏢 Respuesta de áreas:', response);
			
			// Axios response: response.data.data.results (doble data)
			const areas = response.data?.data?.results || response.data?.results || [];
			
			// Asegurar que sea array
			if (!Array.isArray(areas)) {
				console.warn('⚠️ areasDisponibles no es array:', areas);
				this.areasDisponibles.set([]);
				return;
			}
			
			this.areasDisponibles.set(areas);
			console.log('✅ Áreas cargadas:', areas.length, areas);
		} catch (error) {
			console.error('❌ Error cargando áreas:', error);
			this.areasDisponibles.set([]);
		}
	}

	/**
	 * Cargar roles disponibles
	 */
	async cargarRoles() {
		try {
			const response = await personasService.getRoles();
			console.log('👥 Respuesta de roles:', response);
			
			// Axios response: response.data.data.results (doble data)
			const roles = response.data?.data?.results || response.data?.results || [];
			
			// Asegurar que sea array
			if (!Array.isArray(roles)) {
				console.warn('⚠️ rolesDisponibles no es array:', roles);
				this.rolesDisponibles.set([]);
				return;
			}
			
			this.rolesDisponibles.set(roles);
			console.log('✅ Roles cargados:', roles.length, roles);
		} catch (error) {
			console.error('❌ Error cargando roles:', error);
			this.rolesDisponibles.set([]);
		}
	}

	/**
	 * Limpiar todos los filtros aplicados
	 */
	limpiarFiltros() {
		this.busqueda.set('');
		this.filtroArea.set('');
		console.log('🧹 Filtros limpiados');
	}

	/**
	 * Cerrar todos los modales
	 */
	cerrarModales() {
		this.modalVerAgente.set({ isOpen: false, agente: null });
		this.modalEditarAgente.set({ isOpen: false, agente: null, isSaving: false });
		this.modalEliminarAgente.set({ isOpen: false, agente: null, isDeleting: false });
		this.modalAgregarAgente.set({ isOpen: false, isSaving: false });
	}

	/**
	 * Abrir modal para ver detalles de un agente
	 */
	verAgente(agente) {
		this.modalVerAgente.set({ isOpen: true, agente });
	}

	/**
	 * Abrir modal para editar un agente
	 */
	editarAgente(agente) {
		this.modalEditarAgente.set({ isOpen: true, agente, isSaving: false });
	}

	/**
	 * Abrir modal para eliminar un agente
	 */
	eliminarAgente(agente) {
		this.modalEliminarAgente.set({ isOpen: true, agente, isDeleting: false });
	}

	/**
	 * Abrir modal para agregar nuevo agente
	 */
	agregarAgente() {
		this.modalAgregarAgente.set({ isOpen: true, isSaving: false });
	}

	/**
	 * Guardar cambios de un agente editado
	 */
	async guardarCambiosAgente(agente, formData) {
		this.modalEditarAgente.update(modal => ({ ...modal, isSaving: true }));
		
		try {
			await personasService.updateAgente(agente.id_agente, formData);
			
			// Si se cambió el rol, actualizar la asignación
			if (formData.rol_id) {
				try {
					console.log('🔄 Actualizando rol del agente:', agente.id_agente, 'al rol:', formData.rol_id);
					
					// Obtener asignaciones actuales del agente
					const asignacionesResponse = await personasService.getAsignaciones();
					const asignaciones = asignacionesResponse.data?.data?.results || asignacionesResponse.data?.results || [];
					
					// Buscar asignación por id_agente (no por usuario)
					const asignacionActual = asignaciones.find(a => a.usuario === agente.id_agente);
					
					console.log('🔍 Asignación actual encontrada:', asignacionActual);
					
					if (asignacionActual && String(asignacionActual.rol) !== String(formData.rol_id)) {
						// Eliminar asignación actual
						console.log('🗑️ Eliminando asignación actual:', asignacionActual.id);
						await personasService.deleteAsignacion(asignacionActual.id);
						
						// Crear nueva asignación con el nuevo rol
						const nuevaAsignacion = {
							usuario: agente.id_agente,  // Usar id_agente correctamente
							rol: parseInt(formData.rol_id)
							// No enviamos área porque AgenteRol no la maneja
						};
						console.log('➕ Creando nueva asignación:', nuevaAsignacion);
						await personasService.createAsignacion(nuevaAsignacion);
						
					} else if (!asignacionActual && formData.rol_id) {
						// Crear asignación si no existe
						const nuevaAsignacion = {
							usuario: agente.id_agente,  // Usar id_agente correctamente
							rol: parseInt(formData.rol_id)
							// No enviamos área porque AgenteRol no la maneja
						};
						console.log('➕ Creando asignación nueva (no existía):', nuevaAsignacion);
						await personasService.createAsignacion(nuevaAsignacion);
					}
					
					console.log('✅ Rol actualizado correctamente');
				} catch (rolError) {
					console.error('❌ Error actualizando rol:', rolError);
					console.error('❌ Error response:', rolError.response?.data);
					throw new Error('El agente se actualizó pero hubo un problema actualizando el rol: ' + (rolError.response?.data?.message || rolError.message));
				}
			}

			// Actualizar la lista de agentes
			await this.actualizarAgenteEnLista(agente.id_agente);
			
			this.cerrarModales();
			return { success: true, message: 'Agente actualizado correctamente' };
		} catch (error) {
			console.error('Error al actualizar agente:', error);
			
			let errorMessage = 'Error al actualizar el agente: ';
			
			if (error.response?.status === 400) {
				const errorData = error.response.data;
				if (errorData.dni) {
					errorMessage += 'DNI inválido o ya existe en otro agente.';
				} else if (errorData.email) {
					errorMessage += 'Email inválido o ya registrado por otro usuario.';
				} else if (errorData.cuil) {
					errorMessage += 'CUIL inválido o ya registrado.';
				} else {
					errorMessage += 'Verifique que todos los campos obligatorios estén completos y correctos.';
				}
			} else if (error.response?.status === 404) {
				errorMessage += 'El agente no fue encontrado en el sistema.';
			} else if (error.response?.status === 500) {
				errorMessage += 'Error interno del servidor. Contacte al administrador.';
			} else {
				errorMessage += (error.response?.data?.message || error.message || 'Error desconocido.');
			}
			
			throw new Error(errorMessage);
		} finally {
			this.modalEditarAgente.update(modal => ({ ...modal, isSaving: false }));
		}
	}

	/**
	 * Confirmar eliminación de un agente
	 */
	async confirmarEliminacionAgente(agente) {
		// Verificar si es el usuario logueado
		const currentUser = AuthService.getCurrentUser();
		if (currentUser && (agente.email === currentUser.email || agente.usuario_email === currentUser.email || agente.id_agente === currentUser.id)) {
			throw new Error('No puedes eliminarte a ti mismo. Solicita a otro administrador que realice esta acción.');
		}
		
		this.modalEliminarAgente.update(modal => ({ ...modal, isDeleting: true }));
		
		try {
			await personasService.deleteAgente(agente.id_agente);
			
			// Remover el agente de la lista
			this.agentes.update(agentes => agentes.filter(a => a.id_agente !== agente.id_agente));
			
			this.cerrarModales();
			return { success: true, message: 'Agente eliminado correctamente' };
		} catch (error) {
			console.error('Error al eliminar agente:', error);
			
			let errorMessage = 'Error al eliminar el agente: ';
			
			if (error.response?.status === 404) {
				errorMessage += 'El agente no fue encontrado en el sistema.';
			} else if (error.response?.status === 403) {
				errorMessage += 'No tienes permisos para eliminar este agente.';
			} else if (error.response?.status === 409) {
				errorMessage += 'No se puede eliminar el agente porque tiene registros asociados.';
			} else if (error.response?.status === 500) {
				errorMessage += 'Error interno del servidor. Contacte al administrador.';
			} else {
				errorMessage += (error.response?.data?.message || error.message || 'Error desconocido.');
			}
			
			throw new Error(errorMessage);
		} finally {
			this.modalEliminarAgente.update(modal => ({ ...modal, isDeleting: false }));
		}
	}

	/**
	 * Crear un nuevo agente
	 */
	async crearNuevoAgente(formData) {
		this.modalAgregarAgente.update(modal => ({ ...modal, isSaving: true }));
		
		console.log('Datos del formulario para crear agente:', formData);
		
		try {
			const response = await personasService.createAgenteConRol(formData);
			console.log('✅ Respuesta de creación:', response);
			
			// El agente creado podría estar en response.data o directamente en response
			const nuevoAgente = response.data || response;
			
			if (nuevoAgente) {
				// Recargar la lista completa para asegurar consistencia
				await this.cargarAgentes();
				this.cerrarModales();
				return { success: true, message: 'Agente creado correctamente con rol asignado' };
			} else {
				throw new Error('No se pudo obtener los datos del agente creado');
			}
		} catch (error) {
			console.error('Error al crear agente:', error);
			
			let errorMessage = 'Error al crear el agente: ';
			
			if (error.response?.status === 400) {
				const errorData = error.response.data;
				
				// Mostrar el error específico del backend si está disponible
				if (errorData.error) {
					errorMessage += errorData.error;
				} else if (errorData.dni) {
					errorMessage += 'DNI inválido o ya existe en el sistema.';
				} else if (errorData.email) {
					errorMessage += 'Email inválido o ya registrado.';
				} else if (errorData.username) {
					errorMessage += 'Nombre de usuario ya existe.';
				} else if (errorData.cuil) {
					errorMessage += 'CUIL inválido o ya registrado.';
				} else {
					console.log('Datos de error completos:', errorData);
					errorMessage += 'Verifique que todos los campos obligatorios estén completos y correctos.';
				}
			} else if (error.response?.status === 500) {
				errorMessage += 'Error interno del servidor. Contacte al administrador.';
			} else {
				errorMessage += (error.response?.data?.message || error.message || 'Error desconocido.');
			}
			
			throw new Error(errorMessage);
		} finally {
			this.modalAgregarAgente.update(modal => ({ ...modal, isSaving: false }));
		}
	}

	/**
	 * Actualizar un agente específico en la lista
	 */
	async actualizarAgenteEnLista(idAgente) {
		try {
			const response = await personasService.getAgente(idAgente);
			const agenteActualizado = response.data;
			
			this.agentes.update(agentes => {
				const index = agentes.findIndex(a => a.id_agente === idAgente);
				if (index !== -1) {
					agentes[index] = agenteActualizado;
				}
				return [...agentes]; // Trigger reactivity
			});
		} catch (error) {
			console.error('Error actualizando agente en lista:', error);
			// Recargar toda la lista como fallback
			await this.cargarAgentes();
		}
	}

	/**
	 * Obtener información del usuario actual para comparaciones
	 */
	getCurrentUser() {
		return AuthService.getCurrentUser();
	}

	/**
	 * Verificar si un agente es el usuario actual
	 */
	isCurrentUser(agente) {
		const currentUser = this.getCurrentUser();
		return currentUser && (
			agente.email === currentUser.email || 
			agente.usuario_email === currentUser.email || 
			agente.id_agente === currentUser.id
		);
	}
}

// Exportar una instancia única (singleton)
export const usuariosController = new UsuariosController();