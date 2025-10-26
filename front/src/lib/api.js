import axios from 'axios';
import { browser } from '$app/environment';

// Cuando el código se ejecuta en el servidor (dentro de Docker), usamos el nombre del servicio 'back'.
// Cuando se ejecuta en el navegador del cliente, usamos la URL pública 'localhost'.
const API_BASE_URL = browser
	? import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
	: 'http://back:8000/api';

/**
 * Crea una instancia de Axios configurada.
 * Esta función es clave para que la autenticación funcione tanto en el cliente como en el servidor.
 * @param {string | null} token - El token de autenticación para las peticiones.
 * @returns Una instancia de Axios.
 */
export const createApiClient = (token = null) => {
	const apiClient = axios.create({
		baseURL: API_BASE_URL,
		timeout: 10000,
		headers: {
			'Content-Type': 'application/json'
		}
	});

	// Interceptor para añadir el token de autenticación a cada solicitud
	apiClient.interceptors.request.use(
		(config) => {
			if (token) {
				config.headers.Authorization = `Token ${token}`;
			}
			return config;
		},
		(error) => {
			return Promise.reject(error);
		}
	);

	// Interceptor para manejar errores de respuesta (ej. 401 No autorizado)
	apiClient.interceptors.response.use(
		(response) => response,
		(error) => {
			if (browser && error.response?.status === 401) {
				// Si estamos en el navegador y el token es inválido, limpiamos y redirigimos.
				localStorage.removeItem('authToken'); // Asumiendo que usas esto.
				window.location.href = '/login'; // Redirige a la página de login.
			}
			return Promise.reject(error);
		}
	);

	return apiClient;
};

// Exportamos una instancia por defecto para uso general en el cliente.
// Esta instancia no tendrá token por defecto, se debe manejar en el AuthService.
const api = createApiClient(browser ? localStorage.getItem('authToken') : null);

export default api;