import { fetchAPI } from '$lib/utils/api';

/**
 * Obtiene todos los tipos de licencia.
 * @returns {Promise<any>}
 */
export const listarTiposLicencia = async () => {
    return await fetchAPI({
        method: 'GET',
        url: '/asistencia/admin/tipos-licencia/'
    });
};

/**
 * Crea un nuevo tipo de licencia.
 * @param {object} data - Datos del tipo de licencia { codigo, descripcion }.
 * @returns {Promise<any>}
 */
export const crearTipoLicencia = async (data) => {
    return await fetchAPI({
        method: 'POST',
        url: '/asistencia/admin/tipos-licencia/crear/',
        data
    });
};

/**
 * Actualiza un tipo de licencia existente.
 * @param {number} id - ID del tipo de licencia.
 * @param {object} data - Datos a actualizar.
 * @returns {Promise<any>}
 */
export const actualizarTipoLicencia = async (id, data) => {
    return await fetchAPI({
        method: 'PUT',
        url: `/asistencia/admin/tipos-licencia/actualizar/${id}/`,
        data
    });
};

/**
 * Elimina un tipo de licencia.
 * @param {number} id - ID del tipo de licencia.
 * @returns {Promise<any>}
 */
export const eliminarTipoLicencia = async (id) => {
    return await fetchAPI({
        method: 'DELETE',
        url: `/asistencia/admin/tipos-licencia/eliminar/${id}/`
    });
};
