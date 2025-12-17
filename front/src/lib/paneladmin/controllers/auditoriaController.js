import { browser } from '$app/environment';
import { writable, derived, get } from 'svelte/store';
import { auditoriaService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión de auditoría del sistema
 * Centraliza toda la lógica de negocio relacionada con la consulta de registros de auditoría
 */
class AuditoriaController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}
		
		// Stores principales
		this.registros = writable([]);
		this.loading = writable(false);
		this.error = writable(null);

		// Stores para filtros
		this.terminoBusqueda = writable('');
		this.filtros = writable({
			modulo: '', // filtro por tabla/módulo
			accion: '', // filtro por tipo de acción
			usuario: '', // filtro por usuario que realiza la acción
			fechaDesde: '', // filtro por fecha desde
			fechaHasta: '', // filtro por fecha hasta
			categoria: '' // filtro por categoría de acción
		});

		// Store derivado para registros filtrados con filtros avanzados
		this.registrosFiltrados = derived(
			[this.registros, this.terminoBusqueda, this.filtros],
			([$registros, $terminoBusqueda, $filtros]) => {
				if (!$registros || !Array.isArray($registros)) {
					return [];
				}

				let registrosFiltrados = [...$registros];

				// Aplicar filtros avanzados
				if ($filtros.modulo) {
					registrosFiltrados = registrosFiltrados.filter(registro => 
						registro.nombre_tabla === $filtros.modulo
					);
				}

				if ($filtros.accion) {
					registrosFiltrados = registrosFiltrados.filter(registro => 
						registro.accion === $filtros.accion
					);
				}

				if ($filtros.categoria) {
					const acciones = this.getAccionesPorCategoria($filtros.categoria);
					registrosFiltrados = registrosFiltrados.filter(registro => 
						acciones.includes(registro.accion)
					);
				}

				if ($filtros.usuario) {
					const usuarioLower = $filtros.usuario.toLowerCase();
					registrosFiltrados = registrosFiltrados.filter(registro => {
						const usuario = registro.creado_por_nombre || 'Sistema';
						return usuario.toLowerCase().includes(usuarioLower);
					});
				}

				// Optimize date filtering: parse filter dates once outside the loop
				if ($filtros.fechaDesde) {
					// Parse as local date, not UTC
					const [year, month, day] = $filtros.fechaDesde.split('-').map(Number);
					const fechaDesde = new Date(year, month - 1, day, 0, 0, 0, 0);
					const fechaDesdeTs = fechaDesde.getTime();
					registrosFiltrados = registrosFiltrados.filter(registro => {
						const fechaRegistro = new Date(registro.creado_en);
						return fechaRegistro.getTime() >= fechaDesdeTs;
					});
				}

				if ($filtros.fechaHasta) {
					// Parse as local date, not UTC
					const [year, month, day] = $filtros.fechaHasta.split('-').map(Number);
					const fechaHasta = new Date(year, month - 1, day, 23, 59, 59, 999);
					const fechaHastaTs = fechaHasta.getTime();
					registrosFiltrados = registrosFiltrados.filter(registro => {
						const fechaRegistro = new Date(registro.creado_en);
						return fechaRegistro.getTime() <= fechaHastaTs;
					});
				}

				// Aplicar búsqueda de texto libre
				if ($terminoBusqueda.trim()) {
					const busqueda = $terminoBusqueda.toLowerCase().trim();
					
					// Mapeo de acciones traducidas para búsqueda (static, defined once)
					const traduccionAccion = {
						// Acciones generales
						'CREAR': 'alta de registro',
						'MODIFICAR': 'modificación',
						'ELIMINAR': 'registro eliminado',
						'ACTUALIZAR': 'actualización',
						'create': 'alta de registro',
						'update': 'modificación',
						'delete': 'registro eliminado',
						
						// Acciones específicas de asistencias
						'CREAR_ASISTENCIA': 'crear asistencia',
						'MARCAR_ENTRADA': 'marcar entrada',
						'MARCAR_SALIDA': 'marcar salida',
						'MARCAR_ENTRADA_ADMIN': 'marcar entrada admin',
						'MARCAR_SALIDA_ADMIN': 'marcar salida admin',
						'CORREGIR_ASISTENCIA': 'corregir asistencia',
						'MARCAR_AUSENTE': 'marcar ausente',
						
						// Acciones específicas de licencias
						'CREAR_LICENCIA': 'crear licencia',
						'APROBAR_LICENCIA': 'aprobar licencia',
						'RECHAZAR_LICENCIA': 'rechazar licencia',
						'ELIMINAR_LICENCIA': 'eliminar licencia',
						
						// Acciones específicas de tipos de licencia
						'CREAR_TIPO_LICENCIA': 'crear tipo licencia',
						'ACTUALIZAR_TIPO_LICENCIA': 'actualizar tipo licencia',
						'ELIMINAR_TIPO_LICENCIA': 'eliminar tipo licencia',
						
						// Acciones específicas de roles
						'ASIGNAR_ROL': 'asignar rol',
						'QUITAR_ROL': 'quitar rol',
						'CAMBIO_ROL_ATOMICO': 'cambio rol',
						
						// Acciones de autenticación
						'LOGIN_EXITOSO': 'login exitoso',
						'LOGIN_FALLIDO': 'login fallido',
						'LOGOUT': 'logout'
					};
					
					registrosFiltrados = registrosFiltrados.filter(registro => {
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

				return registrosFiltrados;
			}
		);

		// Inicializar
		this.initialized = false;
	}

	/**
	 * Inicializa el controlador cargando los registros de auditoría
	 * Siempre recarga para obtener los datos más recientes
	 */
	async init() {
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}
		
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
				
				// Precompute timestamp for efficient sorting (avoid new Date() on each sort)
				const _ts_creado_en = registro.creado_en ? new Date(registro.creado_en).getTime() : 0;
				
				return {
					...registro,
					creado_por_nombre,
					_ts_creado_en,
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
	 * Actualiza los filtros
	 */
	actualizarFiltros(nuevosFiltros) {
		this.filtros.update(filtros => ({ ...filtros, ...nuevosFiltros }));
	}

	/**
	 * Limpia todos los filtros
	 */
	limpiarFiltros() {
		this.filtros.set({
			modulo: '',
			accion: '',
			usuario: '',
			fechaDesde: '',
			fechaHasta: '',
			categoria: ''
		});
		this.terminoBusqueda.set('');
	}

	/**
	 * Obtiene acciones por categoría
	 */
	getAccionesPorCategoria(categoria) {
		const categorias = {
			'creacion': ['CREAR', 'CREAR_ASISTENCIA', 'CREAR_LICENCIA', 'CREAR_TIPO_LICENCIA', 'create'],
			'modificacion': ['MODIFICAR', 'ACTUALIZAR', 'ACTUALIZAR_TIPO_LICENCIA', 'CORREGIR_ASISTENCIA', 'update'],
			'eliminacion': ['ELIMINAR', 'ELIMINAR_LICENCIA', 'ELIMINAR_TIPO_LICENCIA', 'delete'],
			'asistencias': ['CREAR_ASISTENCIA', 'MARCAR_ENTRADA', 'MARCAR_SALIDA', 'MARCAR_ENTRADA_ADMIN', 'MARCAR_SALIDA_ADMIN', 'CORREGIR_ASISTENCIA', 'MARCAR_AUSENTE'],
			'licencias': ['CREAR_LICENCIA', 'APROBAR_LICENCIA', 'RECHAZAR_LICENCIA', 'ELIMINAR_LICENCIA'],
			'roles': ['ASIGNAR_ROL', 'QUITAR_ROL', 'CAMBIO_ROL_ATOMICO'],
			'autenticacion': ['LOGIN_EXITOSO', 'LOGIN_FALLIDO', 'LOGOUT'],
			'aprobacion': ['APROBAR_LICENCIA', 'APROBAR_COMPENSACION'],
			'rechazo': ['RECHAZAR_LICENCIA', 'RECHAZAR_COMPENSACION']
		};
		
		return categorias[categoria] || [];
	}

	/**
	 * Obtiene módulos únicos de los registros
	 */
	getModulosUnicos() {
		return derived([this.registros], ([$registros]) => {
			if (!$registros || !Array.isArray($registros)) return [];
			
			const modulos = [...new Set($registros.map(r => r.nombre_tabla))].sort();
			return modulos.map(modulo => ({
				value: modulo,
				label: this.formatearNombreModulo(modulo)
			}));
		});
	}

	/**
	 * Obtiene acciones únicas de los registros
	 */
	getAccionesUnicas() {
		return derived([this.registros], ([$registros]) => {
			if (!$registros || !Array.isArray($registros)) return [];
			
			const acciones = [...new Set($registros.map(r => r.accion))].sort();
			return acciones.map(accion => ({
				value: accion,
				label: this.traducirAccion(accion)
			}));
		});
	}

	/**
	 * Obtiene usuarios únicos de los registros
	 */
	getUsuariosUnicos() {
		return derived([this.registros], ([$registros]) => {
			if (!$registros || !Array.isArray($registros)) return [];
			
			const usuarios = [...new Set($registros.map(r => r.creado_por_nombre || 'Sistema'))].sort();
			return usuarios.map(usuario => ({
				value: usuario,
				label: usuario
			}));
		});
	}

	/**
	 * Formatea el nombre del módulo/tabla para display
	 */
	formatearNombreModulo(modulo) {
		const nombres = {
			'agente': 'Usuarios/Agentes',
			'area': 'Áreas',
			'asistencia': 'Asistencias',
			'licencia': 'Licencias',
			'tipo_licencia': 'Tipos de Licencia',
			'guardia': 'Guardias',
			'organigrama': 'Organigrama',
			'cronograma': 'Cronogramas',
			'funciones_plus': 'Funciones Plus',
			'hora_compensacion': 'Compensaciones'
		};
		
		return nombres[modulo] || modulo.charAt(0).toUpperCase() + modulo.slice(1);
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
			// Acciones generales
			'CREAR': 'Alta de registro',
			'MODIFICAR': 'Modificación',
			'ELIMINAR': 'Registro eliminado',
			'ACTUALIZAR': 'Actualización',
			'create': 'Alta de registro',
			'update': 'Modificación',
			'delete': 'Registro eliminado',
			
			// Acciones específicas de asistencias
			'CREAR_ASISTENCIA': 'Crear asistencia',
			'MARCAR_ENTRADA': 'Marcar entrada',
			'MARCAR_SALIDA': 'Marcar salida',
			'MARCAR_ENTRADA_ADMIN': 'Marcar entrada (Admin)',
			'MARCAR_SALIDA_ADMIN': 'Marcar salida (Admin)',
			'CORREGIR_ASISTENCIA': 'Corregir asistencia',
			'MARCAR_AUSENTE': 'Marcar ausente',
			
			// Acciones específicas de licencias
			'CREAR_LICENCIA': 'Crear licencia',
			'APROBAR_LICENCIA': 'Aprobar licencia',
			'RECHAZAR_LICENCIA': 'Rechazar licencia',
			'ELIMINAR_LICENCIA': 'Eliminar licencia',
			
			// Acciones específicas de tipos de licencia
			'CREAR_TIPO_LICENCIA': 'Crear tipo de licencia',
			'ACTUALIZAR_TIPO_LICENCIA': 'Actualizar tipo de licencia',
			'ELIMINAR_TIPO_LICENCIA': 'Eliminar tipo de licencia',
			
			// Acciones específicas de roles
			'ASIGNAR_ROL': 'Asignar rol',
			'QUITAR_ROL': 'Quitar rol',
			'CAMBIO_ROL_ATOMICO': 'Cambio de rol',
			
			// Acciones de autenticación
			'LOGIN_EXITOSO': 'Inicio de sesión exitoso',
			'LOGIN_FALLIDO': 'Intento de inicio de sesión fallido',
			'LOGOUT': 'Cierre de sesión'
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
			// Acciones de creación (verde)
			'CREAR': 'bg-green-500 text-white',
			'CREAR_ASISTENCIA': 'bg-green-500 text-white',
			'CREAR_LICENCIA': 'bg-green-500 text-white',
			'CREAR_TIPO_LICENCIA': 'bg-green-500 text-white',
			'create': 'bg-green-500 text-white',
			
			// Acciones de modificación/actualización (amarillo)
			'MODIFICAR': 'bg-yellow-400 text-black',
			'ACTUALIZAR': 'bg-yellow-400 text-black',
			'ACTUALIZAR_TIPO_LICENCIA': 'bg-yellow-400 text-black',
			'CORREGIR_ASISTENCIA': 'bg-yellow-400 text-black',
			'update': 'bg-yellow-400 text-black',
			
			// Acciones de eliminación (rojo)
			'ELIMINAR': 'bg-red-500 text-white',
			'ELIMINAR_LICENCIA': 'bg-red-500 text-white',
			'ELIMINAR_TIPO_LICENCIA': 'bg-red-500 text-white',
			'delete': 'bg-red-500 text-white',
			
			// Acciones de aprobación/rechazo (azul/naranja)
			'APROBAR_LICENCIA': 'bg-blue-500 text-white',
			'RECHAZAR_LICENCIA': 'bg-orange-500 text-white',
			
			// Acciones de marcación (púrpura)
			'MARCAR_ENTRADA': 'bg-purple-500 text-white',
			'MARCAR_SALIDA': 'bg-purple-600 text-white',
			'MARCAR_ENTRADA_ADMIN': 'bg-purple-700 text-white',
			'MARCAR_SALIDA_ADMIN': 'bg-purple-700 text-white',
			'MARCAR_AUSENTE': 'bg-gray-600 text-white',
			
			// Acciones de roles (índigo)
			'ASIGNAR_ROL': 'bg-indigo-500 text-white',
			'QUITAR_ROL': 'bg-indigo-600 text-white',
			'CAMBIO_ROL_ATOMICO': 'bg-indigo-700 text-white',
			
			// Acciones de autenticación (cyan)
			'LOGIN_EXITOSO': 'bg-cyan-500 text-white',
			'LOGIN_FALLIDO': 'bg-red-600 text-white',
			'LOGOUT': 'bg-cyan-600 text-white'
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

	/**
	 * Limpia todos los filtros
	 */
	limpiarFiltros() {
		this.filtros.set({
			modulo: '',
			categoria: '',
			accion: '',
			usuario: '',
			fechaDesde: '',
			fechaHasta: ''
		});
		this.terminoBusqueda.set('');
	}
}

// Exportar una instancia singleton
export const auditoriaController = new AuditoriaController();
