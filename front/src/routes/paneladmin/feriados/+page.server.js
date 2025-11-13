import { createApiClient } from '$lib/api.js';
import { error, fail } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ request }) {
	try {
		// Extraer cookies de la petición para usar en el servidor
		const cookieHeader = request.headers.get('cookie') || '';
		
		// Crear cliente API que use las cookies de la sesión
		const apiClient = createApiClient();
		
		// Configurar las cookies para que se envíen al backend
		apiClient.defaults.headers.Cookie = cookieHeader;
		
		const response = await apiClient.get('/guardias/feriados/');
		
		return {
			feriados: response.data?.results || []
		};
	} catch (e) {
		console.error('Error al cargar los feriados:', e.message);
		
		// Si es error de autenticación, no es un error de servidor, simplemente no hay datos
		if (e.response?.status === 403 || e.response?.status === 401) {
			return {
				feriados: []
			};
		}
		
		throw error(500, 'No se pudieron cargar los feriados. Revisa la conexión con el backend.');
	}
}

/** @type {import('./$types').Actions} */
export const actions = {
	// Acción para crear un feriado
	createFeriado: async ({ request }) => {
		const data = await request.formData();
		const payload = {
			fecha: data.get('fecha'),
			descripcion: data.get('descripcion')
		};

		if (!payload.descripcion) {
			return fail(400, { success: false, message: 'La descripción es obligatoria.' });
		}

		try {
			const cookieHeader = request.headers.get('cookie') || '';
			const apiClient = createApiClient();
			apiClient.defaults.headers.Cookie = cookieHeader;
			await apiClient.post('/guardias/feriados/', payload);
			return { success: true, message: 'Feriado creado exitosamente.' };
		} catch (err) {
			console.error('Error creando feriado:', err.response?.data || err.message);
			return fail(500, { success: false, message: 'Error del servidor al crear el feriado.' });
		}
	},

	// Acción para actualizar un feriado
	updateFeriado: async ({ request }) => {
		const data = await request.formData();
		const id = data.get('id');
		const payload = {
			fecha: data.get('fecha'),
			descripcion: data.get('descripcion')
		};

		if (!id || !payload.descripcion) {
			return fail(400, { success: false, message: 'Faltan datos para actualizar.' });
		}

		try {
			const cookieHeader = request.headers.get('cookie') || '';
			const apiClient = createApiClient();
			apiClient.defaults.headers.Cookie = cookieHeader;
			await apiClient.put(`/guardias/feriados/${id}/`, payload);
			return { success: true, message: 'Feriado actualizado exitosamente.' };
		} catch (err) {
			console.error('Error actualizando feriado:', err.response?.data || err.message);
			return fail(500, { success: false, message: 'Error del servidor al actualizar el feriado.' });
		}
	},

	// Acción para eliminar un feriado
	deleteFeriado: async ({ request }) => {
		const data = await request.formData();
		const id = data.get('id');

		if (!id) {
			return fail(400, { success: false, message: 'No se proporcionó un ID para eliminar.' });
		}

		try {
			const cookieHeader = request.headers.get('cookie') || '';
			const apiClient = createApiClient();
			apiClient.defaults.headers.Cookie = cookieHeader;
			await apiClient.delete(`/guardias/feriados/${id}/`);
			return { success: true, message: 'Feriado eliminado exitosamente.' };
		} catch (err) {
			console.error('Error eliminando feriado:', err.response?.data || err.message);
			return fail(500, { success: false, message: 'Error del servidor al eliminar el feriado.' });
		}
	}
};
