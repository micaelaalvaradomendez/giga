// Conectado al backend Django GIGA
import axios from 'axios';
import { browser } from '$app/environment';

// Configuración de API que funciona tanto en desarrollo como en producción
const getApiBaseUrl = () => {
	// En el navegador (cliente)
	if (browser) {
		// Usar variable VITE_API_BASE (disponible en build time)
		return import.meta.env.VITE_API_BASE || '/api';
	}

	// En el servidor (SSR)
	// Usar variable de entorno normal (disponible en runtime)
	if (typeof process !== 'undefined' && process.env?.API_BASE_URL) {
		return process.env.API_BASE_URL;
	}

	// Fallback para desarrollo local con Docker
	return 'http://giga-django:8000/api';
};

export const API_BASE_URL = getApiBaseUrl();

// Helper para leer el csrftoken de las cookies cuando estamos en el navegador
const getCsrfToken = () => {
    if (!browser) return null;
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
};

/**
 * Crea una instancia de API real conectada al backend Django.
 * @param {string | null} token - Parámetro legacy, no se usa ya que usamos cookies.
 * @returns Una instancia de axios configurada.
 */
export const createApiClient = (token = null) => {
	const apiClient = axios.create({
		baseURL: API_BASE_URL,
		timeout: 10000,
		withCredentials: true, // Importante para cookies de sesión Django
		headers: {
            'Content-Type': 'application/json',
            ...(getCsrfToken() ? { 'X-CSRFToken': getCsrfToken() } : {}),
            'X-Requested-With': 'XMLHttpRequest'
        }
	});

	// Interceptor para manejo de errores de autenticación
	apiClient.interceptors.response.use(
		(response) => response,
		(error) => {
			if (browser && error.response?.status === 401) {
				// Limpiar localStorage y redirigir al login
				localStorage.clear();
				window.location.href = '/';
			}
			return Promise.reject(error);
		}
	);

	return apiClient;
};

// Exportamos una instancia por defecto para uso general en el cliente.
const api = createApiClient();

// Clase API para compatibilidad con componentes que la usan
export class API {
	static async get(url) {
		const response = await api.get(url);
		return response.data;
	}

	static async post(url, data) {
		const response = await api.post(url, data);
		return response.data;
	}

	static async put(url, data) {
		const response = await api.put(url, data);
		return response.data;
	}

	static async delete(url) {
		const response = await api.delete(url);
		return response.data;
	}

	static async patch(url, data) {
		const response = await api.patch(url, data);
		return response.data;
	}
}

export default api;

