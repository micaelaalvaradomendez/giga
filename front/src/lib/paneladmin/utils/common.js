/**
 * Utilidades comunes para el Panel de Administración
 * Funciones reutilizables para validación, formateo y manejo de datos
 */

/**
 * Validaciones comunes
 */
export const validations = {
	/**
	 * Validar email
	 */
	isValidEmail: (email) => {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	},

	/**
	 * Validar DNI argentino
	 */
	isValidDNI: (dni) => {
		if (!dni) return false;
		const dniStr = dni.toString().replace(/[^0-9]/g, '');
		return dniStr.length >= 7 && dniStr.length <= 8;
	},

	/**
	 * Validar CUIL/CUIT argentino
	 */
	isValidCUIL: (cuil) => {
		if (!cuil) return false;
		const cuilStr = cuil.toString().replace(/[^0-9]/g, '');
		if (cuilStr.length !== 11) return false;

		// Validar dígito verificador
		const factors = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
		let sum = 0;

		for (let i = 0; i < 10; i++) {
			sum += parseInt(cuilStr[i]) * factors[i];
		}

		const remainder = sum % 11;
		const checkDigit = remainder < 2 ? remainder : 11 - remainder;

		return checkDigit === parseInt(cuilStr[10]);
	},

	/**
	 * Validar legajo
	 */
	isValidLegajo: (legajo) => {
		if (!legajo) return false;
		return legajo.toString().trim().length >= 3;
	},

	/**
	 * Validar nombre/apellido
	 */
	isValidName: (name) => {
		if (!name) return false;
		return name.trim().length >= 2;
	},

	/**
	 * Validar contraseña
	 */
	isValidPassword: (password) => {
		if (!password) return false;
		// Mínimo 8 caracteres, al menos una letra y un número
		const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/;
		return passwordRegex.test(password);
	}
};

/**
 * Formateo de datos
 */
export const formatters = {
	/**
	 * Formatear nombre completo
	 */
	fullName: (nombre, apellido) => {
		const n = (nombre || '').trim();
		const a = (apellido || '').trim();
		return `${n} ${a}`.trim();
	},

	/**
	 * Formatear DNI con puntos
	 */
	formatDNI: (dni) => {
		if (!dni) return '';
		const dniStr = dni.toString().replace(/[^0-9]/g, '');
		return dniStr.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
	},

	/**
	 * Formatear CUIL con guiones
	 */
	formatCUIL: (cuil) => {
		if (!cuil) return '';
		const cuilStr = cuil.toString().replace(/[^0-9]/g, '');
		if (cuilStr.length === 11) {
			return `${cuilStr.slice(0, 2)}-${cuilStr.slice(2, 10)}-${cuilStr.slice(10)}`;
		}
		return cuilStr;
	},

	/**
	 * Formatear fecha
	 */
	formatDate: (date, options = {}) => {
		if (!date) return '';
		const d = new Date(date);
		if (isNaN(d.getTime())) return '';

		const defaultOptions = {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			timeZone: 'America/Argentina/Buenos_Aires'
		};

		return d.toLocaleDateString('es-AR', { ...defaultOptions, ...options });
	},

	/**
	 * Formatear hora
	 */
	formatTime: (time) => {
		if (!time) return '';
		// Si viene en formato HH:MM:SS, tomar solo HH:MM
		if (typeof time === 'string' && time.includes(':')) {
			const parts = time.split(':');
			return `${parts[0]}:${parts[1]}`;
		}
		return time;
	},

	/**
	 * Formatear teléfono argentino
	 */
	formatPhone: (phone) => {
		if (!phone) return '';
		const phoneStr = phone.toString().replace(/[^0-9]/g, '');

		// Celular (11 dígitos): +54 9 11 1234-5678
		if (phoneStr.length === 10 && phoneStr.startsWith('11')) {
			return `+54 9 ${phoneStr.slice(0, 2)} ${phoneStr.slice(2, 6)}-${phoneStr.slice(6)}`;
		}

		// Teléfono fijo (10 dígitos): +54 11 1234-5678
		if (phoneStr.length === 10) {
			return `+54 ${phoneStr.slice(0, 2)} ${phoneStr.slice(2, 6)}-${phoneStr.slice(6)}`;
		}

		return phoneStr;
	},

	/**
	 * Capitalizar texto
	 */
	capitalize: (str) => {
		if (!str) return '';
		return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
	},

	/**
	 * Formatear texto para título
	 */
	titleCase: (str) => {
		if (!str) return '';
		return str.toLowerCase().split(' ').map(word =>
			word.charAt(0).toUpperCase() + word.slice(1)
		).join(' ');
	}
};

/**
 * Utilidades para colores y estilos
 */
export const colorUtils = {
	/**
	 * Generar color basado en texto (para avatares, badges, etc.)
	 */
	generateColorFromText: (text) => {
		if (!text) return '#6c757d';

		let hash = 0;
		for (let i = 0; i < text.length; i++) {
			hash = text.charCodeAt(i) + ((hash << 5) - hash);
		}

		const colors = [
			'#e74c3c', '#3498db', '#2ecc71', '#f39c12',
			'#9b59b6', '#1abc9c', '#34495e', '#e67e22',
			'#27ae60', '#8e44ad', '#2980b9', '#d35400'
		];

		return colors[Math.abs(hash) % colors.length];
	},

	/**
	 * Obtener contraste de texto para un color de fondo
	 */
	getTextColor: (backgroundColor) => {
		// Convertir hex a RGB
		const hex = backgroundColor.replace('#', '');
		const r = parseInt(hex.substr(0, 2), 16);
		const g = parseInt(hex.substr(2, 2), 16);
		const b = parseInt(hex.substr(4, 2), 16);

		// Calcular luminancia
		const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

		// Retornar blanco para fondos oscuros, negro para fondos claros
		return luminance > 0.5 ? '#000000' : '#ffffff';
	},

	/**
	 * Paleta de colores para diferentes estados
	 */
	statusColors: {
		success: '#28a745',
		danger: '#dc3545',
		warning: '#ffc107',
		info: '#17a2b8',
		primary: '#e79043',
		secondary: '#6c757d',
		light: '#f8f9fa',
		dark: '#343a40'
	}
};

/**
 * Utilidades para manejo de errores
 */
export const errorUtils = {
	/**
	 * Extraer mensaje de error de respuesta de API
	 */
	extractErrorMessage: (error) => {
		if (!error) return 'Error desconocido';

		// Error de red
		if (!error.response) {
			return 'Error de conexión. Verifique su conexión a internet.';
		}

		const status = error.response.status;
		const data = error.response.data;

		// Errores comunes por código de estado
		switch (status) {
			case 400:
				if (data && typeof data === 'object') {
					// Errores de validación campo por campo
					const fieldErrors = [];
					Object.keys(data).forEach(field => {
						if (Array.isArray(data[field])) {
							fieldErrors.push(`${field}: ${data[field][0]}`);
						} else if (typeof data[field] === 'string') {
							fieldErrors.push(`${field}: ${data[field]}`);
						}
					});
					if (fieldErrors.length > 0) {
						return fieldErrors.join('\n');
					}
				}
				return data.message || 'Datos inválidos';

			case 401:
				return 'Sesión expirada. Por favor, inicie sesión nuevamente.';

			case 403:
				return 'No tiene permisos para realizar esta acción.';

			case 404:
				return 'El recurso solicitado no fue encontrado.';

			case 409:
				return data.message || 'Conflicto con los datos existentes.';

			case 422:
				return data.message || 'Los datos enviados no son válidos.';

			case 500:
				return 'Error interno del servidor. Contacte al administrador.';

			case 503:
				return 'Servicio temporalmente no disponible. Intente más tarde.';

			default:
				return data.message || `Error ${status}: ${error.message}`;
		}
	},

	/**
	 * Crear objeto de error estandarizado
	 */
	createStandardError: (message, code = null, details = null) => {
		return {
			message,
			code,
			details,
			timestamp: new Date().toISOString()
		};
	}
};

/**
 * Utilidades para localStorage/sessionStorage
 */
export const storageUtils = {
	/**
	 * Guardar en localStorage con manejo de errores
	 */
	setItem: (key, value) => {
		try {
			localStorage.setItem(key, JSON.stringify(value));
			return true;
		} catch (error) {
			return false;
		}
	},

	/**
	 * Obtener de localStorage con manejo de errores
	 */
	getItem: (key, defaultValue = null) => {
		try {
			const item = localStorage.getItem(key);
			return item ? JSON.parse(item) : defaultValue;
		} catch (error) {
			return defaultValue;
		}
	},

	/**
	 * Remover de localStorage
	 */
	removeItem: (key) => {
		try {
			localStorage.removeItem(key);
			return true;
		} catch (error) {
			return false;
		}
	}
};

/**
 * Utilidades para URLs y navegación
 */
export const urlUtils = {
	/**
	 * Construir URL con parámetros
	 */
	buildUrl: (baseUrl, params = {}) => {
		const url = new URL(baseUrl, window.location.origin);
		Object.keys(params).forEach(key => {
			if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
				url.searchParams.set(key, params[key]);
			}
		});
		return url.toString();
	},

	/**
	 * Obtener parámetros de URL
	 */
	getUrlParams: () => {
		const params = {};
		const searchParams = new URLSearchParams(window.location.search);
		for (const [key, value] of searchParams) {
			params[key] = value;
		}
		return params;
	}
};

/**
 * Utilidades para arrays y objetos
 */
export const dataUtils = {
	/**
	 * Agrupar array por campo
	 */
	groupBy: (array, field) => {
		return array.reduce((groups, item) => {
			const key = item[field];
			if (!groups[key]) {
				groups[key] = [];
			}
			groups[key].push(item);
			return groups;
		}, {});
	},

	/**
	 * Ordenar array por campo
	 */
	sortBy: (array, field, direction = 'asc') => {
		return [...array].sort((a, b) => {
			const valueA = a[field];
			const valueB = b[field];

			if (valueA < valueB) return direction === 'asc' ? -1 : 1;
			if (valueA > valueB) return direction === 'asc' ? 1 : -1;
			return 0;
		});
	},

	/**
	 * Filtrar array por múltiples campos
	 */
	filterByFields: (array, searchTerm, fields) => {
		const term = searchTerm.toLowerCase().trim();
		if (!term) return array;

		return array.filter(item =>
			fields.some(field => {
				const value = item[field];
				return value && value.toString().toLowerCase().includes(term);
			})
		);
	},

	/**
	 * Crear copia profunda de objeto
	 */
	deepClone: (obj) => {
		return JSON.parse(JSON.stringify(obj));
	}
};