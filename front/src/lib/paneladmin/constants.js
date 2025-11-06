/**
 * Constantes del Panel de Administración
 * Valores reutilizables y configuraciones centralizadas
 */

/**
 * Configuración de la aplicación
 */
export const APP_CONFIG = {
	// Información de la aplicación
	APP_NAME: 'GIGA',
	APP_TITLE: 'Sistema de Gestión Integral de Agentes',
	VERSION: '2.0.0',
	
	// Configuración de paginación
	DEFAULT_PAGE_SIZE: 25,
	PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
	
	// Timeouts y delays
	API_TIMEOUT: 30000, // 30 segundos
	DEBOUNCE_DELAY: 300, // 300ms para búsquedas
	AUTO_SAVE_DELAY: 2000, // 2 segundos para auto-guardado
	
	// Límites de archivos
	MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
	ALLOWED_FILE_TYPES: ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.xls', '.xlsx'],
	
	// Configuración de sesión
	SESSION_TIMEOUT: 60 * 60 * 1000, // 1 hora en milisegundos
	SESSION_WARNING: 5 * 60 * 1000, // Advertencia 5 minutos antes
	
	// Configuración regional
	TIMEZONE: 'America/Argentina/Buenos_Aires',
	LOCALE: 'es-AR',
	CURRENCY: 'ARS'
};

/**
 * Estados y códigos de respuesta
 */
export const HTTP_STATUS = {
	OK: 200,
	CREATED: 201,
	NO_CONTENT: 204,
	BAD_REQUEST: 400,
	UNAUTHORIZED: 401,
	FORBIDDEN: 403,
	NOT_FOUND: 404,
	CONFLICT: 409,
	UNPROCESSABLE_ENTITY: 422,
	INTERNAL_SERVER_ERROR: 500,
	SERVICE_UNAVAILABLE: 503
};

/**
 * Tipos de notificaciones
 */
export const NOTIFICATION_TYPES = {
	SUCCESS: 'success',
	ERROR: 'error',
	WARNING: 'warning',
	INFO: 'info'
};

/**
 * Roles del sistema
 */
export const SYSTEM_ROLES = {
	ADMINISTRADOR: 'Administrador',
	JEFE: 'Jefe',
	AGENTE: 'Agente',
	SUPERVISOR: 'Supervisor',
	COORDINADOR: 'Coordinador'
};

/**
 * Agrupaciones predefinidas
 */
export const AGRUPACIONES = {
	EPU: {
		nombre: 'EPU',
		descripcion: 'Equipos de Prevención Urbana',
		color: '#28a745'
	},
	POMYS: {
		nombre: 'POMyS',
		descripcion: 'Prevención, Operaciones y Monitoreo y Seguimiento',
		color: '#17a2b8'
	},
	PAYT: {
		nombre: 'PAyT',
		descripcion: 'Prevención, Asistencia y Trabajo',
		color: '#ffc107'
	}
};

/**
 * Estados de agentes
 */
export const AGENT_STATUS = {
	ACTIVO: {
		key: 'activo',
		label: 'Activo',
		color: '#28a745',
		icon: '✅'
	},
	INACTIVO: {
		key: 'inactivo',
		label: 'Inactivo',
		color: '#dc3545',
		icon: '❌'
	},
	SUSPENDIDO: {
		key: 'suspendido',
		label: 'Suspendido',
		color: '#ffc107',
		icon: '⚠️'
	},
	LICENCIA: {
		key: 'licencia',
		label: 'En Licencia',
		color: '#6c757d',
		icon: '🏖️'
	}
};

/**
 * Tipos de documentos
 */
export const DOCUMENT_TYPES = {
	DNI: 'DNI',
	CUIL: 'CUIL',
	CUIT: 'CUIT',
	PASAPORTE: 'Pasaporte',
	CEDULA: 'Cédula'
};

/**
 * Categorías de revista
 */
export const CATEGORIA_REVISTA = {
	PLANTA_PERMANENTE: 'Planta Permanente',
	PLANTA_TEMPORARIA: 'Planta Temporaria',
	CONTRATADO: 'Contratado',
	MONOTRIBUTISTA: 'Monotributista',
	BECARIO: 'Becario',
	PASANTE: 'Pasante'
};

/**
 * Tipos de contacto
 */
export const CONTACT_TYPES = {
	EMAIL_PERSONAL: 'Email Personal',
	EMAIL_INSTITUCIONAL: 'Email Institucional',
	TELEFONO_MOVIL: 'Teléfono Móvil',
	TELEFONO_FIJO: 'Teléfono Fijo',
	TELEFONO_EMERGENCIA: 'Teléfono de Emergencia'
};

/**
 * Configuración de formularios
 */
export const FORM_CONFIG = {
	// Longitudes mínimas y máximas
	MIN_NAME_LENGTH: 2,
	MAX_NAME_LENGTH: 50,
	MIN_PASSWORD_LENGTH: 8,
	MAX_PASSWORD_LENGTH: 128,
	MIN_DESCRIPTION_LENGTH: 0,
	MAX_DESCRIPTION_LENGTH: 500,
	
	// Patrones de validación
	EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
	DNI_PATTERN: /^\d{7,8}$/,
	CUIL_PATTERN: /^\d{2}-\d{8}-\d{1}$/,
	PHONE_PATTERN: /^[\d\s\-\+\(\)]{10,15}$/,
	
	// Configuración de campos
	REQUIRED_FIELDS: {
		agente: ['nombre', 'apellido', 'dni', 'email'],
		area: ['nombre'],
		agrupacion: ['nombre'],
		rol: ['nombre']
	}
};

/**
 * Configuración de tablas y listados
 */
export const TABLE_CONFIG = {
	// Columnas por defecto para diferentes entidades
	AGENTES_COLUMNS: [
		{ key: 'legajo', label: 'Legajo', sortable: true, width: '100px' },
		{ key: 'nombre_completo', label: 'Nombre Completo', sortable: true, width: 'auto' },
		{ key: 'dni', label: 'DNI', sortable: true, width: '120px' },
		{ key: 'email', label: 'Email', sortable: true, width: 'auto' },
		{ key: 'area', label: 'Área', sortable: true, width: '150px' },
		{ key: 'rol', label: 'Rol', sortable: false, width: '120px' },
		{ key: 'acciones', label: 'Acciones', sortable: false, width: '150px' }
	],
	
	AREAS_COLUMNS: [
		{ key: 'nombre', label: 'Nombre', sortable: true, width: 'auto' },
		{ key: 'total_agentes', label: 'Total Agentes', sortable: true, width: '150px' },
		{ key: 'activo', label: 'Estado', sortable: true, width: '120px' },
		{ key: 'acciones', label: 'Acciones', sortable: false, width: '200px' }
	],
	
	AGRUPACIONES_COLUMNS: [
		{ key: 'nombre', label: 'Nombre', sortable: true, width: 'auto' },
		{ key: 'descripcion', label: 'Descripción', sortable: false, width: 'auto' },
		{ key: 'total_agentes', label: 'Total Agentes', sortable: true, width: '150px' },
		{ key: 'activo', label: 'Estado', sortable: true, width: '120px' },
		{ key: 'acciones', label: 'Acciones', sortable: false, width: '200px' }
	]
};

/**
 * Configuración de modales
 */
export const MODAL_CONFIG = {
	// Tamaños de modales
	SIZES: {
		SMALL: 'modal-sm',
		MEDIUM: 'modal-md',
		LARGE: 'modal-lg',
		EXTRA_LARGE: 'modal-xl'
	},
	
	// Tipos de modales
	TYPES: {
		FORM: 'form',
		CONFIRMATION: 'confirmation',
		INFO: 'info',
		WARNING: 'warning'
	}
};

/**
 * Configuración de colores del tema
 */
export const THEME_COLORS = {
	// Colores principales
	PRIMARY: '#e79043',
	PRIMARY_DARK: '#d68a3b',
	PRIMARY_LIGHT: '#f2a968',
	
	// Colores de estado
	SUCCESS: '#28a745',
	DANGER: '#dc3545',
	WARNING: '#ffc107',
	INFO: '#17a2b8',
	
	// Colores neutros
	LIGHT: '#f8f9fa',
	DARK: '#343a40',
	MUTED: '#6c757d',
	WHITE: '#ffffff',
	
	// Colores para gráficos
	CHART_COLORS: [
		'#e79043', '#28a745', '#17a2b8', '#ffc107',
		'#dc3545', '#6f42c1', '#20c997', '#fd7e14'
	]
};

/**
 * Configuración de animaciones
 */
export const ANIMATION_CONFIG = {
	// Duraciones en milisegundos
	FAST: 150,
	NORMAL: 300,
	SLOW: 500,
	
	// Easings
	EASE_OUT: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
	EASE_IN: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',
	EASE_IN_OUT: 'cubic-bezier(0.645, 0.045, 0.355, 1)'
};

/**
 * Mensajes del sistema
 */
export const SYSTEM_MESSAGES = {
	// Mensajes de éxito
	SUCCESS: {
		CREATED: 'Registro creado exitosamente',
		UPDATED: 'Registro actualizado exitosamente',
		DELETED: 'Registro eliminado exitosamente',
		SAVED: 'Cambios guardados exitosamente'
	},
	
	// Mensajes de error
	ERROR: {
		GENERIC: 'Ha ocurrido un error inesperado',
		NETWORK: 'Error de conexión. Verifique su conexión a internet',
		UNAUTHORIZED: 'No tiene permisos para realizar esta acción',
		NOT_FOUND: 'El recurso solicitado no fue encontrado',
		VALIDATION: 'Por favor, verifique los datos ingresados'
	},
	
	// Mensajes de confirmación
	CONFIRMATION: {
		DELETE: '¿Está seguro de que desea eliminar este registro?',
		UNSAVED_CHANGES: 'Tiene cambios sin guardar. ¿Desea continuar?',
		LOGOUT: '¿Está seguro de que desea cerrar sesión?'
	},
	
	// Mensajes informativos
	INFO: {
		LOADING: 'Cargando información...',
		NO_DATA: 'No se encontraron registros',
		EMPTY_SEARCH: 'No se encontraron resultados para su búsqueda',
		SESSION_EXPIRING: 'Su sesión expirará pronto. ¿Desea extenderla?'
	}
};

/**
 * Configuración de URLs de la API
 */
export const API_ENDPOINTS = {
	// Base
	BASE_URL: '/api',
	
	// Autenticación
	AUTH: {
		LOGIN: '/auth/login/',
		LOGOUT: '/auth/logout/',
		REFRESH: '/auth/refresh/',
		PROFILE: '/auth/profile/'
	},
	
	// Personas
	PERSONAS: {
		AGENTES: '/personas/agentes/',
		AREAS: '/personas/areas/',
		ROLES: '/personas/roles/',
		ASIGNACIONES: '/personas/asignaciones/',
		AGRUPACIONES: '/personas/agrupaciones/'
	},
	
	// Reportes
	REPORTES: {
		DASHBOARD: '/reportes/dashboard/',
		ASISTENCIA: '/reportes/asistencia/',
		EXPORT: '/reportes/export/'
	}
};

/**
 * Configuración de localStorage keys
 */
export const STORAGE_KEYS = {
	USER_TOKEN: 'giga_user_token',
	USER_DATA: 'giga_user_data',
	PREFERENCES: 'giga_preferences',
	THEME: 'giga_theme',
	LANGUAGE: 'giga_language',
	LAST_ROUTE: 'giga_last_route'
};

/**
 * Configuración de eventos del sistema
 */
export const SYSTEM_EVENTS = {
	USER_LOGIN: 'user:login',
	USER_LOGOUT: 'user:logout',
	DATA_UPDATED: 'data:updated',
	ERROR_OCCURRED: 'error:occurred',
	NOTIFICATION_SHOW: 'notification:show'
};