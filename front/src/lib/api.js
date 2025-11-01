import axios from 'axios';
import { browser } from '$app/environment';

// Configuración de API que funciona tanto en desarrollo como en producción
const getApiBaseUrl = () => {
	// En el navegador (cliente)
	if (browser) {
		// Usar la variable de entorno o el valor por defecto
		return import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
	}
	
	// En el servidor (SSR)
	// En Docker (tanto dev como prod): usar el nombre del servicio del contenedor
	// El frontend está en un contenedor y necesita hablar con el backend usando nombres de Docker
	return 'http://backend:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Crea una instancia de Axios configurada.
 * Esta función funciona con autenticación por sesiones/cookies de Django.
 * @param {string | null} token - Parámetro legacy, no se usa ya que usamos cookies.
 * @returns Una instancia de Axios.
 */
export const createApiClient = (token = null) => {
	const apiClient = axios.create({
		baseURL: API_BASE_URL,
		timeout: 10000,
		headers: {
			'Content-Type': 'application/json'
		},
		// Importante: enviar cookies con cada petición
		withCredentials: true
	});

	// Interceptor para manejar errores de respuesta (ej. 401 No autorizado)
	apiClient.interceptors.response.use(
		(response) => response,
		(error) => {
			if (browser && (error.response?.status === 401 || error.response?.status === 403)) {
				// Si estamos en el navegador y no está autenticado, redirigir al login
				localStorage.removeItem('user');
				localStorage.removeItem('isAuthenticated');
				window.location.href = '/';
			}
			return Promise.reject(error);
		}
	);

	return apiClient;
};

// Exportamos una instancia por defecto para uso general en el cliente.
// Esta instancia usa cookies para autenticación, no tokens.
const api = createApiClient();

export default api;