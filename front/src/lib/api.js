// Conectado al backend Django GIGA
import axios from 'axios';
import { browser } from '$app/environment';

// Configuración de API que funciona tanto en desarrollo como en producción
const getApiBaseUrl = () => {
	// En el navegador (cliente)
	if (browser) {
		// Usar la variable de entorno o el valor por defecto (nginx)
		return import.meta.env.VITE_API_BASE || '/api';
	}
	
	// En el servidor (SSR)
	// En Docker (tanto dev como prod): usar el nombre del servicio del contenedor
	return 'http://giga-django:8000/api';
};

export const API_BASE_URL = getApiBaseUrl();

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
			'Content-Type': 'application/json'
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

export default api;