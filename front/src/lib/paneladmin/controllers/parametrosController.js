import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';
import { personasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión de parámetros del sistema (áreas y agrupaciones)
 * Centraliza toda la lógica de negocio relacionada con la configuración de parámetros
 */
class ParametrosController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}
		
		// Stores principales para datos
		this.areas = writable([]);
		this.agrupaciones = writable([]);
		this.loading = writable(false);
		this.error = writable(null);

		// Stores para filtrado
		this.busquedaAreas = writable('');
		this.busquedaAgrupaciones = writable('');

		// Stores para modales
		this.modalArea = writable({ isOpen: false, agente: null, isSaving: false });
		this.modalAgrupacion = writable({ isOpen: false, agente: null, isSaving: false });
		this.modalSchedule = writable({ isOpen: false, tipo: '', target: null, isSaving: false });
		this.modalDelete = writable({ 
			isOpen: false, 
			tipo: '', 
			item: null, 
			isDeleting: false, 
			nuevaAsignacion: '' 
		});

		// Stores para formularios
		this.areaForm = writable({ 
			id_area: null, 
			nombre: '', 
			descripcion: '',
			id_area_padre: null,
			jefe_area: null,
			agentes_asignados: [],
			activo: true 
		});
		this.agrupacionForm = writable({ 
			id_agrupacion: null, 
			nombre: '', 
			descripcion: '', 
			color: '#e79043', 
			activo: true 
		});
		this.scheduleForm = writable({ 
			horario_entrada: '08:00',
			horario_salida: '16:00'
		});

		// Stores derivados para datos filtrados
		this.areasFiltradas = derived(
			[this.areas, this.busquedaAreas],
			([$areas, $busquedaAreas]) => {
				if (!$areas || !Array.isArray($areas)) return [];
				
				return $areas.filter(area => {
					return !$busquedaAreas || 
						area.nombre.toLowerCase().includes($busquedaAreas.toLowerCase());
				});
			}
		);

		this.agrupacionesFiltradas = derived(
			[this.agrupaciones, this.busquedaAgrupaciones],
			([$agrupaciones, $busquedaAgrupaciones]) => {
				if (!$agrupaciones || !Array.isArray($agrupaciones)) return [];
				
				return $agrupaciones.filter(agrupacion => {
					return !$busquedaAgrupaciones || 
						agrupacion.nombre.toLowerCase().includes($busquedaAgrupaciones.toLowerCase());
				});
			}
		);

		// Stores derivados para estadísticas
		this.estadisticasAreas = derived(
			[this.areasFiltradas, this.areas],
			([$areasFiltradas, $areas]) => ({
				mostradas: $areasFiltradas ? $areasFiltradas.length : 0,
				total: $areas ? $areas.length : 0,
				activas: $areasFiltradas ? $areasFiltradas.filter(a => a.activo).length : 0
			})
		);

		this.estadisticasAgrupaciones = derived(
			[this.agrupacionesFiltradas, this.agrupaciones],
			([$agrupacionesFiltradas, $agrupaciones]) => ({
				mostradas: $agrupacionesFiltradas ? $agrupacionesFiltradas.length : 0,
				total: $agrupaciones ? $agrupaciones.length : 0,
				activas: $agrupacionesFiltradas ? $agrupacionesFiltradas.filter(a => a.activo).length : 0
			})
		);
	}

	/**
	 * Inicializar el controlador - cargar datos iniciales
	 */
	async init() {
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}
		
		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}

		await this.cargarDatos();
	}

	/**
	 * Cargar todos los datos (áreas y agrupaciones)
	 */
	async cargarDatos() {
		this.loading.set(true);
		this.error.set(null);
		
		try {
			await Promise.all([
				this.cargarAreas(),
				this.cargarAgrupaciones()
			]);
		} catch (err) {
			console.error('Error cargando datos:', err);
			this.error.set('Error al cargar datos del sistema');
			throw err;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Cargar áreas del sistema
	 */
	async cargarAreas() {
		try {
			const response = await personasService.getAreas();
			
			let areasData = [];
			if (response && response.data && response.data.data) {
				areasData = response.data.data.results || [];
			} else if (response && response.data) {
				areasData = response.data.results || [];
			}
			
			this.areas.set(areasData);
			console.log('✅ Áreas cargadas:', areasData.length);
		} catch (error) {
			console.error('❌ Error cargando áreas:', error);
			this.areas.set([]);
			throw error;
		}
	}

	/**
	 * Cargar agrupaciones del sistema
	 */
	async cargarAgrupaciones() {
		try {
			const response = await personasService.getAgrupaciones();
			
			let agrupacionesData = [];
			if (response && response.data && response.data.data) {
				agrupacionesData = response.data.data.results || [];
			} else if (response && response.data) {
				agrupacionesData = response.data.results || [];
			}
			
			this.agrupaciones.set(agrupacionesData);
			console.log('✅ Agrupaciones cargadas:', agrupacionesData.length);
		} catch (error) {
			console.error('❌ Error cargando agrupaciones:', error);
			this.agrupaciones.set([]);
			throw error;
		}
	}

	/**
	 * Cargar agentes disponibles para asignación
	 */
	async cargarAgentes() {
		try {
			const response = await personasService.getAgentes();
			
			let agentesData = [];
			if (response && response.data && response.data.data) {
				agentesData = response.data.data.results || [];
			} else if (response && response.data) {
				agentesData = response.data.results || [];
			}
			
			console.log('✅ Agentes cargados:', agentesData.length);
			return agentesData;
		} catch (error) {
			console.error('❌ Error cargando agentes:', error);
			return [];
		}
	}

	/**
	 * Obtener áreas raíz (sin padre) para el selector jerárquico
	 */
	getAreasRaiz() {
		return derived([this.areas], ([$areas]) => {
			if (!$areas || !Array.isArray($areas)) return [];
			return $areas.filter(area => !area.id_area_padre && area.activo);
		});
	}

	/**
	 * Construir árbol jerárquico de áreas
	 */
	construirArbolAreas(areas = null) {
		if (!areas) {
			return derived([this.areas], ([$areas]) => {
				return this._construirArbol($areas || []);
			});
		}
		return this._construirArbol(areas);
	}

	/**
	 * Función auxiliar para construir árbol jerárquico
	 */
	_construirArbol(areas, parentId = null, level = 0) {
		const result = [];
		const children = areas.filter(area => 
			(parentId === null && !area.id_area_padre) || 
			(area.id_area_padre === parentId)
		);
		
		for (const area of children) {
			const areaWithChildren = {
				...area,
				level,
				children: this._construirArbol(areas, area.id_area, level + 1)
			};
			result.push(areaWithChildren);
		}
		
		return result;
	}

	// =====================================
	// GESTIÓN DE ÁREAS
	// =====================================

	/**
	 * Abrir modal para agregar nueva área
	 */
	agregarArea() {
		this.areaForm.set({ 
			id_area: null, 
			nombre: '', 
			descripcion: '',
			id_area_padre: null,
			jefe_area: null,
			agentes_asignados: [],
			activo: true 
		});
		this.modalArea.set({ isOpen: true, agente: null, isSaving: false });
	}

	/**
	 * Abrir modal para editar un área existente
	 */
	editarArea(area) {
		this.areaForm.set({ ...area });
		this.modalArea.set({ isOpen: true, agente: area, isSaving: false });
	}

	/**
	 * Abrir modal para eliminar un área
	 */
	eliminarArea(area) {
		this.modalDelete.set({
			isOpen: true,
			tipo: 'area',
			item: area,
			isDeleting: false,
			nuevaAsignacion: ''
		});
	}

	/**
	 * Guardar área (crear o actualizar)
	 */
	async guardarArea(formData) {
		if (!formData.nombre.trim()) {
			throw new Error('El nombre del área es requerido');
		}

		// Validar jerarquía: no puede ser su propio padre
		if (formData.id_area && formData.id_area_padre === formData.id_area) {
			throw new Error('Un área no puede ser su propio padre');
		}

		this.modalArea.update(modal => ({ ...modal, isSaving: true }));
		
		try {
			let response;
			
			// Preparar datos con todos los campos jerárquicos
			const areaData = {
				nombre: formData.nombre.trim(),
				descripcion: formData.descripcion?.trim() || null,
				id_area_padre: formData.id_area_padre || null,
				jefe_area: formData.jefe_area || null,
				agentes_asignados: formData.agentes_asignados || [],
				activo: formData.activo
			};
			
			if (formData.id_area) {
				// Actualizar área existente
				response = await personasService.updateArea(formData.id_area, areaData);
			} else {
				// Crear nueva área
				response = await personasService.createArea(areaData);
			}
			
			if (response && response.data && response.data.success) {
				console.log('✅ Área guardada correctamente:', response.data.data);
			}
			
			this.modalArea.set({ isOpen: false, agente: null, isSaving: false });
			await this.cargarAreas();
			
			return { 
				success: true, 
				message: formData.id_area ? 'Área actualizada correctamente' : 'Área creada correctamente',
				data: response.data.data
			};
		} catch (error) {
			console.error('❌ Error guardando área:', error);
			const errorMessage = 'Error al guardar el área: ' + (error.response?.data?.message || error.message);
			throw new Error(errorMessage);
		} finally {
			this.modalArea.update(modal => ({ ...modal, isSaving: false }));
		}
	}

	/**
	 * Confirmar eliminación de área
	 */
	async confirmarEliminarArea(areaId) {
		this.modalDelete.update(modal => ({ ...modal, isDeleting: true }));
		
		try {
			const response = await personasService.deleteArea(areaId);
			
			if (response && response.data && response.data.success) {
				console.log('✅ Área eliminada correctamente');
			}
			
			this.modalDelete.set({
				isOpen: false,
				tipo: '',
				item: null,
				isDeleting: false,
				nuevaAsignacion: ''
			});
			
			await this.cargarAreas();
			
			return { success: true, message: 'Área eliminada correctamente' };
		} catch (error) {
			console.error('❌ Error eliminando área:', error);
			const errorMessage = 'Error al eliminar el área: ' + (error.response?.data?.message || error.message);
			throw new Error(errorMessage);
		} finally {
			this.modalDelete.update(modal => ({ ...modal, isDeleting: false }));
		}
	}

	// =====================================
	// GESTIÓN DE AGRUPACIONES
	// =====================================

	/**
	 * Abrir modal para agregar nueva agrupación
	 */
	agregarAgrupacion() {
		this.agrupacionForm.set({ 
			id_agrupacion: null, 
			nombre: '', 
			descripcion: '', 
			color: '#e79043', 
			activo: true 
		});
		this.modalAgrupacion.set({ isOpen: true, agente: null, isSaving: false });
	}

	/**
	 * Abrir modal para editar una agrupación existente
	 */
	editarAgrupacion(agrupacion) {
		this.agrupacionForm.set({ ...agrupacion });
		this.modalAgrupacion.set({ isOpen: true, agente: agrupacion, isSaving: false });
	}

	/**
	 * Abrir modal para eliminar una agrupación
	 */
	eliminarAgrupacion(agrupacion) {
		this.modalDelete.set({
			isOpen: true,
			tipo: 'agrupacion',
			item: agrupacion,
			isDeleting: false,
			nuevaAsignacion: ''
		});
	}

	/**
	 * Guardar agrupación (crear o actualizar)
	 */
	async guardarAgrupacion(formData) {
		if (!formData.nombre.trim()) {
			throw new Error('El nombre de la agrupación es requerido');
		}

		this.modalAgrupacion.update(modal => ({ ...modal, isSaving: true }));
		
		try {
			let response;
			
			if (formData.id_agrupacion) {
				// Actualizar agrupación existente
				response = await personasService.updateAgrupacion(formData.id_agrupacion, {
					nombre: formData.nombre.trim(),
					descripcion: formData.descripcion.trim(),
					color: formData.color,
					activo: formData.activo
				});
			} else {
				// Crear nueva agrupación
				response = await personasService.createAgrupacion({
					nombre: formData.nombre.trim(),
					descripcion: formData.descripcion.trim(),
					color: formData.color,
					activo: formData.activo
				});
			}
			
			if (response && response.data && response.data.success) {
				console.log('✅ Agrupación guardada correctamente');
			}
			
			this.modalAgrupacion.set({ isOpen: false, agente: null, isSaving: false });
			await this.cargarAgrupaciones();
			
			return { 
				success: true, 
				message: formData.id_agrupacion ? 'Agrupación actualizada correctamente' : 'Agrupación creada correctamente'
			};
		} catch (error) {
			console.error('❌ Error guardando agrupación:', error);
			const errorMessage = 'Error al guardar la agrupación: ' + (error.response?.data?.message || error.message);
			throw new Error(errorMessage);
		} finally {
			this.modalAgrupacion.update(modal => ({ ...modal, isSaving: false }));
		}
	}

	/**
	 * Confirmar eliminación de agrupación
	 */
	async confirmarEliminarAgrupacion(agrupacionId, nuevaAsignacion = null) {
		this.modalDelete.update(modal => ({ ...modal, isDeleting: true }));
		
		try {
			const requestData = nuevaAsignacion ? 
				{ nueva_agrupacion: nuevaAsignacion } : {};
			
			const response = await personasService.deleteAgrupacion(agrupacionId, requestData);
			
			if (response && response.data && response.data.success) {
				console.log('✅ Agrupación eliminada correctamente');
			}
			
			this.modalDelete.set({
				isOpen: false,
				tipo: '',
				item: null,
				isDeleting: false,
				nuevaAsignacion: ''
			});
			
			await this.cargarAgrupaciones();
			
			return { success: true, message: 'Agrupación eliminada correctamente' };
		} catch (error) {
			console.error('❌ Error eliminando agrupación:', error);
			const errorMessage = 'Error al eliminar la agrupación: ' + (error.response?.data?.message || error.message);
			throw new Error(errorMessage);
		} finally {
			this.modalDelete.update(modal => ({ ...modal, isDeleting: false }));
		}
	}

	// =====================================
	// GESTIÓN DE HORARIOS
	// =====================================

	/**
	 * Abrir modal para gestionar horarios
	 */
	gestionarHorarios(tipo, item) {
		this.scheduleForm.set({
			horario_entrada: '08:00',
			horario_salida: '16:00'
		});
		this.modalSchedule.set({
			isOpen: true,
			tipo: tipo,
			target: item,
			isSaving: false
		});
	}

	/**
	 * Actualizar horarios por área o agrupación
	 */
	async actualizarHorarios(formData, tipo, target) {
		console.log('📋 actualizarHorarios llamado con:', { formData, tipo, target });
		
		if (!formData.horario_entrada || !formData.horario_salida) {
			console.error('❌ Faltan datos de horarios:', formData);
			throw new Error('Horarios de entrada y salida son requeridos');
		}

		this.modalSchedule.update(modal => ({ ...modal, isSaving: true }));
		
		try {
			const horarioData = {
				horario_entrada: formData.horario_entrada,
				horario_salida: formData.horario_salida
			};

			console.log('📤 Enviando datos:', horarioData);

			let response;

			if (tipo === 'area') {
				// Actualizar horarios por área
				console.log('🏢 Actualizando horarios por área:', target.id_area);
				response = await personasService.updateAreaSchedule(target.id_area, horarioData);
			} else if (tipo === 'agrupacion') {
				// Actualizar horarios por agrupación
				const agrupacionData = {
					agrupacion: target.nombre,
					...horarioData
				};
				console.log('👥 Actualizando horarios por agrupación:', agrupacionData);
				response = await personasService.updateAgrupacionSchedule(agrupacionData);
			}
			
			console.log('📥 Respuesta recibida:', response);
			
			if (response && response.data && response.data.success) {
				console.log('✅ Horarios actualizados correctamente');
			}
			
			this.modalSchedule.set({ isOpen: false, tipo: '', target: null, isSaving: false });
			
			// Recargar datos para mostrar cambios
			await this.init();
			
			return { success: true, message: 'Horarios actualizados correctamente' };
		} catch (error) {
			console.error('❌ Error actualizando horarios:', error);
			const errorMessage = 'Error al actualizar horarios: ' + (error.response?.data?.message || error.message);
			throw new Error(errorMessage);
		} finally {
			this.modalSchedule.update(modal => ({ ...modal, isSaving: false }));
		}
	}

	// =====================================
	// FUNCIONES DE UTILIDAD
	// =====================================

	/**
	 * Actualizar filtro de búsqueda de áreas
	 */
	actualizarBusquedaAreas(valor) {
		this.busquedaAreas.set(valor);
	}

	/**
	 * Actualizar filtro de búsqueda de agrupaciones
	 */
	actualizarBusquedaAgrupaciones(valor) {
		this.busquedaAgrupaciones.set(valor);
	}

	/**
	 * Limpiar filtros de áreas
	 */
	limpiarFiltrosAreas() {
		this.busquedaAreas.set('');
	}

	/**
	 * Limpiar filtros de agrupaciones
	 */
	limpiarFiltrosAgrupaciones() {
		this.busquedaAgrupaciones.set('');
	}

	/**
	 * Cerrar todos los modales
	 */
	cerrarModales() {
		this.modalArea.set({ isOpen: false, agente: null, isSaving: false });
		this.modalAgrupacion.set({ isOpen: false, agente: null, isSaving: false });
		this.modalSchedule.set({ isOpen: false, tipo: '', target: null, isSaving: false });
		this.modalDelete.set({ 
			isOpen: false, 
			tipo: '', 
			item: null, 
			isDeleting: false, 
			nuevaAsignacion: '' 
		});
	}

	/**
	 * Validar si hay agentes asignados a un área/agrupación antes de eliminar
	 */
	async validarEliminacion(tipo, id) {
		try {
			// Esta función debería implementarse en el backend para verificar
			// si hay agentes asignados antes de permitir la eliminación
			// Por ahora, permitimos la eliminación directa
			return { canDelete: true, agentesCount: 0 };
		} catch (error) {
			console.error('Error validando eliminación:', error);
			return { canDelete: false, agentesCount: 0 };
		}
	}
}

// Exportar una instancia única (singleton)
export const parametrosController = new ParametrosController();