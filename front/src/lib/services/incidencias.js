import { API_BASE_URL } from '../api.js';

class IncidenciasService {
    constructor() {
        this.baseURL = `${API_BASE_URL}/incidencias/`;
    }

    // Obtener token CSRF desde cookie (si existe)
    static getCsrfToken() {
        if (typeof window === 'undefined') return null;
        const match = document.cookie.match(new RegExp('(^|;)\\s*' + 'csrftoken' + '\\s*=\\s*([^;]+)'));
        return match ? match.pop() : null;
    }

    async _makeRequest(endpoint = '', options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        const csrf = IncidenciasService.getCsrfToken();
        if (csrf) {
            headers['X-CSRFToken'] = csrf;
        }

        const defaultOptions = {
            headers,
            credentials: 'include'
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
        }

        return response.json();
    }

    // Obtener todas las incidencias (con filtrado por rol)
    async obtenerIncidencias() {
        const response = await this._makeRequest();

        // Manejar respuesta paginada de DRF
        if (response && typeof response === 'object') {
            // Si tiene structure paginada de DRF: {count, results}
            if ('results' in response && Array.isArray(response.results)) {
                return response.results;
            }
            // Si es un array directo
            if (Array.isArray(response)) {
                return response;
            }
        }

        // Fallback: devolver array vacío en caso de estructura inesperada
        console.warn('Estructura de respuesta inesperada en obtenerIncidencias:', response);
        return [];
    }

    // Obtener incidencias creadas por el usuario
    async obtenerMisIncidencias() {
        const response = await this._makeRequest('mias/');
        // Si es una respuesta paginada, devolver solo los results
        return response.results || response;
    }

    // Obtener incidencias asignadas al usuario
    async obtenerIncidenciasAsignadas() {
        const response = await this._makeRequest('asignadas/');
        // Si es una respuesta paginada, devolver solo los results
        return response.results || response;
    }

    // Obtener una incidencia específica
    async obtenerIncidencia(id) {
        return this._makeRequest(`${id}/`);
    }

    // Crear nueva incidencia
    async crearIncidencia(incidenciaData) {
        return this._makeRequest('', {
            method: 'POST',
            body: JSON.stringify(incidenciaData)
        });
    }

    // Actualizar incidencia
    async actualizarIncidencia(id, incidenciaData) {
        return this._makeRequest(`${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(incidenciaData)
        });
    }

    // Agregar comentario
    async agregarComentario(id, comentario) {
        return this._makeRequest(`${id}/agregar-comentario/`, {
            method: 'POST',
            body: JSON.stringify({ comentario })
        });
    }

    // Cambiar estado
    async cambiarEstado(id, nuevoEstado, comentario = '') {
        return this._makeRequest(`${id}/cambiar-estado/`, {
            method: 'POST',
            body: JSON.stringify({
                estado: nuevoEstado,
                comentario: comentario
            })
        });
    }

    // Asignar incidencia
    async asignarIncidencia(id, agenteId) {
        return this._makeRequest(`${id}/asignar/`, {
            method: 'POST',
            body: JSON.stringify({ agente_id: agenteId })
        });
    }



    // Obtener jefes del área del usuario
    async obtenerJefesArea() {
        return this._makeRequest('jefes-area/');
    }

    // Obtener agentes del área del usuario (para jefes/directores/admins)
    async obtenerAgentesArea() {
        return this._makeRequest('agentes-area/');
    }

    // Eliminar incidencia
    async eliminarIncidencia(id) {
        return this._makeRequest(`${id}/`, {
            method: 'DELETE'
        });
    }

    // Utilidades para el frontend
    static formatearFecha(fechaString) {
        if (!fechaString) return 'No establecida';
        
        try {
            const fecha = new Date(fechaString);
            
            // Verificar que la fecha sea válida
            if (isNaN(fecha.getTime())) {
                console.warn('Fecha inválida:', fechaString);
                return 'Fecha inválida';
            }
            
            // Usar toLocaleString que automáticamente convierte de UTC a hora local
            return fecha.toLocaleString('es-AR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        } catch (error) {
            console.error('Error al formatear fecha:', error);
            return 'Error en fecha';
        }
    }
}

export { IncidenciasService };