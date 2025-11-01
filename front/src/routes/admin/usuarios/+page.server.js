import { createApiClient } from '$lib/api.js';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies, request }) {
	try {
		// Extraer cookies de la petición para usar en el servidor
		const cookieHeader = request.headers.get('cookie') || '';
		
		// Crear cliente API que use las cookies de la sesión
		const apiClient = createApiClient();
		
		// Configurar las cookies para que se envíen al backend
		apiClient.defaults.headers.Cookie = cookieHeader;
		
		const response = await apiClient.get('/personas/agentes/');
		
		return {
			agentes: response.data?.results || []
		};
	} catch (e) {
		console.error('Error al cargar los agentes:', e.message);
		console.error('Status:', e.response?.status);
		console.error('Data:', e.response?.data);
		
		// Si es error de autenticación, no es error de servidor
		if (e.response?.status === 403 || e.response?.status === 401) {
			return {
				agentes: []
			};
		}
		
		throw error(500, 'No se pudieron cargar los agentes. Revisa la conexión con el backend.');
	}
}