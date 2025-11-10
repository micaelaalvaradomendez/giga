import { createApiClient } from '$lib/api.js';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ request }) {
	try {
		const cookieHeader = request.headers.get('cookie') || '';

		const apiClient = createApiClient();
		apiClient.defaults.headers.Cookie = cookieHeader;

		const response = await apiClient.get('/auditoria/registros/');

		return {
			registros: response.data?.results || []
		};
	} catch (e) {
		console.error('Error al cargar los registros de auditoría:', e.message);

		if (e.response?.status === 403 || e.response?.status === 401) {
			return { registros: [] };
		}

		throw error(500, 'No se pudieron cargar los registros. Revisa la conexión con el backend.');
	}
}
