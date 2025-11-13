import { writable, derived } from 'svelte/store';
import { auditoriaService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión de auditoría del sistema
 * Centraliza toda la lógica de negocio relacionada con la consulta de registros de auditoría
 */
class AuditoriaController {
	constructor() {
		// Stores principales
		this.registros = writable([]);
		this.loading = writable(false);
		this.error = writable(null);

		// Store para búsqueda
		this.terminoBusqueda = writable('');

		// Store derivado para registros filtrados
		this.registrosFiltrados = derived(
			[this.registros, this.terminoBusqueda],
			([$registros, $terminoBusqueda]) => {
				if (!$registros || !Array.isArray($registros)) {
					return [];
				}

				if (!$terminoBusqueda.trim()) {
					return $registros;
				}

				const busqueda = $terminoBusqueda.toLowerCase().trim();
				
				return $registros.filter(registro => {
					// Mapeo de acciones traducidas
					const traduccionAccion = {
						'CREAR': 'alta de registro',
						'MODIFICAR': 'modificación',
						'ELIMINAR': 'registro eliminado',
						'create': 'alta de registro',
						'update': 'modificación',
						'delete': 'registro eliminado'
					};

					// Campos de búsqueda
					const usuario = (registro.creado_por_nombre || registro.id_agente?.nombre || 'sistema').toLowerCase();
					const accion = (traduccionAccion[registro.accion] || registro.accion || '').toLowerCase();
					const tabla = (registro.nombre_tabla || '').toLowerCase();
					
					// Buscar en todos los campos relevantes
					return usuario.includes(busqueda) || 
						   accion.includes(busqueda) || 
						   tabla.includes(busqueda);
				});
			}
		);

		// Inicializar
		this.initialized = false;
	}

	/**
	 * Inicializa el controlador cargando los registros de auditoría
	 */
	async init() {
		if (this.initialized) return;

		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}

		try {
			this.loading.set(true);
			await this.loadRegistros();
			this.initialized = true;
		} catch (error) {
			console.error('Error inicializando controlador de auditoría:', error);
			this.error.set('Error al inicializar el controlador de auditoría');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga todos los registros de auditoría
	 */
	async loadRegistros() {
		try {
			this.loading.set(true);
			this.error.set(null);

			// Las cookies de sesión se incluyen automáticamente
			const response = await auditoriaService.getRegistrosAuditoria();
			
			const registrosData = response.data?.results || response.data || [];
			
			// Procesar y enriquecer los datos
			const registrosProcesados = registrosData.map(registro => {
				// Manejar el nombre del creador de forma segura
				let creado_por_nombre = 'Sistema';
				if (registro.creado_por_nombre) {
					creado_por_nombre = registro.creado_por_nombre;
				} else if (registro.id_agente && (registro.id_agente.nombre || registro.id_agente.apellido)) {
					creado_por_nombre = `${registro.id_agente.nombre || ''} ${registro.id_agente.apellido || ''}`.trim();
				}
				
				return {
					...registro,
					creado_por_nombre,
					fecha_formateada: this.formatearFecha(registro.creado_en),
					accion_traducida: this.traducirAccion(registro.accion)
				};
			});

			this.registros.set(registrosProcesados);
			
		} catch (error) {
			console.error('Error cargando registros de auditoría:', error);
			this.error.set('Error al cargar los registros de auditoría');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Actualiza el término de búsqueda
	 */
	setBusqueda(termino) {
		this.terminoBusqueda.set(termino);
	}

	/**
	 * Recarga los registros de auditoría
	 */
	async recargar() {
		await this.loadRegistros();
	}

	/**
	 * Limpia el término de búsqueda
	 */
	limpiarBusqueda() {
		this.terminoBusqueda.set('');
	}

	/**
	 * Formatea una fecha en formato ISO a un string legible para Argentina
	 */
	formatearFecha(fechaISO) {
		if (!fechaISO) return 'N/A';
		
		try {
			const fecha = new Date(fechaISO);
			return fecha.toLocaleString('es-AR', {
				day: '2-digit',
				month: '2-digit',
				year: 'numeric',
				hour: '2-digit',
				minute: '2-digit',
				hour12: false
			});
		} catch (error) {
			console.error('Error formateando fecha:', error);
			return 'Fecha inválida';
		}
	}

	/**
	 * Traduce las acciones de auditoría a español
	 */
	traducirAccion(accion) {
		const traducciones = {
			'CREAR': 'Alta de registro',
			'MODIFICAR': 'Modificación',
			'ELIMINAR': 'Registro eliminado',
			'create': 'Alta de registro',
			'update': 'Modificación',
			'delete': 'Registro eliminado'
		};

		return traducciones[accion] || accion?.toUpperCase() || 'Acción desconocida';
	}

	/**
	 * Formatea un objeto JSON para mostrarlo de forma legible
	 */
	formatearValor(valor) {
		if (valor === null || valor === undefined) {
			return '-';
		}

		if (typeof valor !== 'object' || Object.keys(valor).length === 0) {
			return '-';
		}

		try {
			return Object.entries(valor)
				.map(([key, val]) => `${key}: ${val}`)
				.join(', ');
		} catch (error) {
			console.error('Error formateando valor:', error);
			return 'Valor inválido';
		}
	}

	/**
	 * Obtiene el color del badge según el tipo de acción
	 */
	getBadgeColor(accion) {
		const colores = {
			'CREAR': 'bg-green-500 text-white',
			'MODIFICAR': 'bg-yellow-400 text-black',
			'ELIMINAR': 'bg-red-500 text-white',
			'create': 'bg-green-500 text-white',
			'update': 'bg-yellow-400 text-black',
			'delete': 'bg-red-500 text-white'
		};

		return colores[accion] || 'bg-gray-500 text-white';
	}

	/**
	 * Obtiene estadísticas básicas de los registros
	 */
	getEstadisticas() {
		return derived([this.registros], ([$registros]) => {
			if (!$registros || !Array.isArray($registros)) {
				return {
					total: 0,
					crear: 0,
					modificar: 0,
					eliminar: 0
				};
			}

			return {
				total: $registros.length,
				crear: $registros.filter(r => ['CREAR', 'create'].includes(r.accion)).length,
				modificar: $registros.filter(r => ['MODIFICAR', 'update'].includes(r.accion)).length,
				eliminar: $registros.filter(r => ['ELIMINAR', 'delete'].includes(r.accion)).length
			};
		});
	}
}

// Exportar una instancia singleton
export const auditoriaController = new AuditoriaController();
