import { writable, derived } from 'svelte/store';
import { guardiasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión de feriados
 * Centraliza toda la lógica de negocio relacionada con la gestión de feriados del calendario
 */
class FeriadosController {
	constructor() {
		// Stores principales
		this.feriados = writable([]);
		this.loading = writable(false);
		this.error = writable(null);
		this.success = writable(null);

		// Stores para modales
		this.modalGestionFeriado = writable({
			isOpen: false,
			feriado: null,
			selectedDate: null,
			isSaving: false,
			isDeleting: false
		});

		// Store para formulario
		this.feriadoForm = writable({
			id: null,
			fecha: '',
			descripcion: ''
		});

		// Store derivado para feriados por fecha (útil para el calendario)
		this.feriadosPorFecha = derived(
			[this.feriados],
			([$feriados]) => {
				const feriadosMap = new Map();
				$feriados.forEach(feriado => {
					feriadosMap.set(feriado.fecha, feriado);
				});
				return feriadosMap;
			}
		);

		// Inicializar
		this.initialized = false;
	}

	/**
	 * Inicializa el controlador cargando los datos necesarios
	 */
	async init() {
		if (this.initialized) return;

		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}

		try {
			this.loading.set(true);
			await this.loadFeriados();
			this.initialized = true;
		} catch (error) {
			console.error('Error inicializando controlador de feriados:', error);
			this.error.set('Error al inicializar el controlador de feriados');
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga todos los feriados
	 */
	async loadFeriados() {
		try {
			this.loading.set(true);
			this.error.set(null);


			const response = await guardiasService.getFeriados();

			const feriadosData = response.data?.results || response.data || [];
			this.feriados.set(feriadosData);

		} catch (error) {
			console.error('Error cargando feriados:', error);
			this.error.set('Error al cargar los feriados');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Crea un nuevo feriado (con soporte multi-día)
	 */
	async createFeriado(feriadoData) {
		try {
			this.loading.set(true);
			this.error.set(null);
			this.success.set(null);

			const requestData = {
				nombre: feriadoData.nombre,
				descripcion: feriadoData.descripcion || '',
				fecha_inicio: feriadoData.fecha_inicio,
				fecha_fin: feriadoData.fecha_fin || feriadoData.fecha_inicio, // Default a mismo día
				es_nacional: feriadoData.es_nacional || false,
				es_provincial: feriadoData.es_provincial || false,
				es_local: feriadoData.es_local || false
			};

			// Agregar repetición anual si está especificada (mantenemos compatibilidad)
			if (feriadoData.repetir_anualmente) {
				requestData.repetir_anualmente = true;
			}

			const response = await guardiasService.createFeriado(requestData);

			// Actualizar la lista de feriados
			await this.loadFeriados();

			// Mensaje personalizado
			if (feriadoData.repetir_anualmente && response.data?.feriados_creados) {
				this.success.set(`Feriado creado para ${response.data.feriados_creados} años: ${response.data.años.join(', ')}`);
			} else if (feriadoData.fecha_inicio === feriadoData.fecha_fin) {
				this.success.set('Feriado creado exitosamente');
			} else {
				const duracion = this.calculateDaysDifference(feriadoData.fecha_inicio, feriadoData.fecha_fin) + 1;
				this.success.set(`Feriado de ${duracion} días creado exitosamente`);
			}

			return response.data;

		} catch (error) {
			console.error('Error creando feriado:', error);
			const errorMsg = error.response?.data?.error || error.response?.data?.message || 'Error al crear el feriado';
			this.error.set(errorMsg);
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Actualiza un feriado existente
	 */
	async updateFeriado(id, feriadoData) {
		try {
			this.loading.set(true);
			this.error.set(null);
			this.success.set(null);

			const requestData = {
				nombre: feriadoData.nombre,
				descripcion: feriadoData.descripcion || '',
				fecha_inicio: feriadoData.fecha_inicio,
				fecha_fin: feriadoData.fecha_fin || feriadoData.fecha_inicio,
				es_nacional: feriadoData.es_nacional || false,
				es_provincial: feriadoData.es_provincial || false,
				es_local: feriadoData.es_local || false
			};

			const response = await guardiasService.updateFeriado(id, requestData);

			// Actualizar la lista de feriados
			await this.loadFeriados();

			this.success.set('Feriado actualizado exitosamente');
			return response.data;

		} catch (error) {
			console.error('Error actualizando feriado:', error);
			const errorMsg = error.response?.data?.message || 'Error al actualizar el feriado';
			this.error.set(errorMsg);
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Elimina un feriado
	 */
	async deleteFeriado(id) {
		try {
			this.loading.set(true);
			this.error.set(null);
			this.success.set(null);

			await guardiasService.deleteFeriado(id);

			// Actualizar la lista de feriados
			await this.loadFeriados();

			this.success.set('Feriado eliminado exitosamente');

		} catch (error) {
			console.error('Error eliminando feriado:', error);
			const errorMsg = error.response?.data?.message || 'Error al eliminar el feriado';
			this.error.set(errorMsg);
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Obtiene todos los feriados que incluyen una fecha específica
	 */
	getFeriadosByDate(fecha) {
		let feriadosEnFecha = [];

		const unsubscribe = this.feriados.subscribe(feriados => {
			feriadosEnFecha = feriados.filter(feriado => {
				return fecha >= feriado.fecha_inicio && fecha <= feriado.fecha_fin;
			});
		});
		unsubscribe();

		return feriadosEnFecha;
	}

	/**
	 * Obtiene un feriado por fecha (compatibilidad - devuelve el primero si hay múltiples)
	 */
	getFeriadoByDate(fecha) {
		const feriados = this.getFeriadosByDate(fecha);
		return feriados.length > 0 ? feriados[0] : null;
	}

	/**
	 * Verifica si una fecha tiene feriados
	 */
	isFeriado(fecha) {
		return this.getFeriadosByDate(fecha).length > 0;
	}

	/**
	 * Verifica si una fecha tiene múltiples feriados
	 */
	hasMultipleFeriados(fecha) {
		return this.getFeriadosByDate(fecha).length > 1;
	}

	/**
	 * Calcula la diferencia en días entre dos fechas
	 */
	calculateDaysDifference(fecha1, fecha2) {
		const date1 = new Date(fecha1);
		const date2 = new Date(fecha2);
		const diffTime = Math.abs(date2 - date1);
		return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
	}

	// Métodos para manejo de modales

	/**
	 * Abre el modal de gestión de feriados
	 */
	openModal(selectedDate, feriado = null) {
		// Si se especifica un feriado, es modo edición; si no, buscar feriados existentes
		const feriadosExistentes = feriado ? [] : this.getFeriadosByDate(selectedDate);

		this.modalGestionFeriado.set({
			isOpen: true,
			feriado: feriado, // null para crear, objeto para editar
			existingFeriados: feriadosExistentes, // Array de feriados existentes en la fecha
			selectedDate,
			isSaving: false,
			isDeleting: false
		});

		// Inicializar formulario
		if (feriado) {
			// Modo edición - usar el feriado pasado como parámetro
			this.feriadoForm.set({
				id: feriado.id_feriado,
				nombre: feriado.nombre,
				descripcion: feriado.descripcion || '',
				fecha_inicio: feriado.fecha_inicio,
				fecha_fin: feriado.fecha_fin,
				es_nacional: feriado.es_nacional,
				es_provincial: feriado.es_provincial,
				es_local: feriado.es_local
			});
		} else {
			// Modo creación
			this.feriadoForm.set({
				id: null,
				nombre: '',
				descripcion: '',
				fecha_inicio: selectedDate,
				fecha_fin: selectedDate,
				es_nacional: false,
				es_provincial: false,
				es_local: true
			});
		}
	}

	/**
	 * Cierra el modal de gestión de feriados
	 */
	closeModal() {
		this.modalGestionFeriado.update(modal => ({
			...modal,
			isOpen: false
		}));
	}

	/**
	 * Guarda un feriado (crear o actualizar)
	 */
	async saveFeriado(feriadoData) {
		try {
			// Actualizar estado del modal
			this.modalGestionFeriado.update(modal => ({
				...modal,
				isSaving: true
			}));

			if (feriadoData.id_feriado) {
				// Actualizar feriado existente
				await this.updateFeriado(feriadoData.id_feriado, feriadoData);
			} else {
				// Crear nuevo feriado
				await this.createFeriado(feriadoData);
			}

			// Cerrar modal en caso de éxito
			this.closeModal();

		} catch (error) {
			// El error ya se maneja en los métodos individuales
			throw error;
		} finally {
			// Resetear estado del modal
			this.modalGestionFeriado.update(modal => ({
				...modal,
				isSaving: false
			}));
		}
	}

	/**
	 * Elimina un feriado desde el modal
	 */
	async deleteFeriadoFromModal(id) {
		try {
			// Actualizar estado del modal
			this.modalGestionFeriado.update(modal => ({
				...modal,
				isDeleting: true
			}));

			await this.deleteFeriado(id);

			// Cerrar modal en caso de éxito
			this.closeModal();

		} catch (error) {
			// El error ya se maneja en el método deleteFeriado
			throw error;
		} finally {
			// Resetear estado del modal
			this.modalGestionFeriado.update(modal => ({
				...modal,
				isDeleting: false
			}));
		}
	}

	/**
	 * Limpia mensajes de error y éxito
	 */
	clearMessages() {
		this.error.set(null);
		this.success.set(null);
	}

	/**
	 * Reset del controlador (útil para logout)
	 */
	reset() {
		this.feriados.set([]);
		this.error.set(null);
		this.success.set(null);
		this.modalGestionFeriado.set({
			isOpen: false,
			feriado: null,
			selectedDate: null,
			isSaving: false,
			isDeleting: false
		});
		this.feriadoForm.set({
			id: null,
			fecha: '',
			descripcion: ''
		});
		this.initialized = false;
	}
}

// Crear instancia singleton
export const feriadosController = new FeriadosController();

// Exportar clase para casos especiales
export { FeriadosController };

// Export por defecto
export default feriadosController;