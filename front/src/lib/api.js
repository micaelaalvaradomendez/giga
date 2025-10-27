import axios from 'axios';
import { browser } from '$app/environment';

// Cuando el código se ejecuta en el servidor (dentro de Docker), usamos el nombre del servicio 'back'.
// Cuando se ejecuta en el navegador del cliente, usamos la URL pública 'localhost'.
const API_BASE_URL = browser
	? import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
	: 'http://back:8000/api';

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