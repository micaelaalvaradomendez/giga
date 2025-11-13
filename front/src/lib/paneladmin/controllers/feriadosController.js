import { writable, derived } from 'svelte/store';
import { createApiClient } from '$lib/api.js';
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

			const apiClient = createApiClient();
			const response = await apiClient.get('/guardias/feriados/');
			
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
	 * Crea un nuevo feriado
	 */
	async createFeriado(feriadoData) {
		try {
			this.loading.set(true);
			this.error.set(null);
			this.success.set(null);

			const apiClient = createApiClient();
			const response = await apiClient.post('/guardias/feriados/', {
				fecha: feriadoData.fecha,
				descripcion: feriadoData.descripcion
			});

			// Actualizar la lista de feriados
			await this.loadFeriados();
			
			this.success.set('Feriado creado exitosamente');
			return response.data;

		} catch (error) {
			console.error('Error creando feriado:', error);
			const errorMsg = error.response?.data?.message || 'Error al crear el feriado';
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

			const apiClient = createApiClient();
			const response = await apiClient.put(`/guardias/feriados/${id}/`, {
				fecha: feriadoData.fecha,
				descripcion: feriadoData.descripcion
			});

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

			const apiClient = createApiClient();
			await apiClient.delete(`/guardias/feriados/${id}/`);

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
	 * Obtiene un feriado por fecha
	 */
	getFeriadoByDate(fecha) {
		let feriado = null;
		this.feriadosPorFecha.subscribe(feriadosMap => {
			feriado = feriadosMap.get(fecha) || null;
		})();
		return feriado;
	}

	/**
	 * Verifica si una fecha es feriado
	 */
	isFeriado(fecha) {
		return this.getFeriadoByDate(fecha) !== null;
	}

	// Métodos para manejo de modales
	
	/**
	 * Abre el modal de gestión de feriados
	 */
	openModal(selectedDate, feriado = null) {
		this.modalGestionFeriado.set({
			isOpen: true,
			feriado,
			selectedDate,
			isSaving: false,
			isDeleting: false
		});

		// Inicializar formulario
		this.feriadoForm.set({
			id: feriado?.id || null,
			fecha: selectedDate,
			descripcion: feriado?.descripcion || ''
		});
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

			if (feriadoData.id) {
				// Actualizar feriado existente
				await this.updateFeriado(feriadoData.id, feriadoData);
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