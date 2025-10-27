import { personasService } from '$lib/services.js';
import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
	try {
		const token = cookies.get('auth_token');
		const response = await personasService.getAllAgentes(token); 
		return {
			agentes: response.data
		};
	} catch (e) {
		console.error('Error al cargar los agentes:', e);
		throw error(500, 'No se pudieron cargar los agentes. Revisa la conexión con el backend.');
	}
}