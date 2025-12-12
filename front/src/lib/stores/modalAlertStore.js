import { writable } from 'svelte/store';

/**
 * Store para controlar el estado del modal de alerta
 */
export const modalAlert = writable({
    show: false,
    type: 'info', // 'info', 'success', 'warning', 'error'
    title: '',
    message: '',
    showConfirmButton: true,
    confirmText: 'Aceptar',
    showCancelButton: false,
    cancelText: 'Cancelar',
    onConfirm: null,
    onCancel: null
});

/**
 * Muestra un modal de alerta simple (equivalente a alert())
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de alerta ('success', 'warning', 'error', 'info')
 * @param {string} title - Título del modal (opcional)
 */
export function showAlert(message, type = 'info', title = '') {
    return new Promise((resolve) => {
        modalAlert.set({
            show: true,
            type,
            title: title || getTitleByType(type),
            message,
            showConfirmButton: true,
            confirmText: 'Aceptar',
            showCancelButton: false,
            cancelText: 'Cancelar',
            onConfirm: () => {
                modalAlert.update(m => ({ ...m, show: false }));
                resolve(true);
            },
            onCancel: null
        });
    });
}

/**
 * Muestra un modal de confirmación (equivalente a confirm())
 * @param {string} message - Mensaje a mostrar
 * @param {string} title - Título del modal (opcional)
 * @param {string} confirmText - Texto del botón confirmar (opcional)
 * @param {string} cancelText - Texto del botón cancelar (opcional)
 * @returns {Promise<boolean>} - true si confirma, false si cancela
 */
export function showConfirm(message, title = '¿Está seguro?', confirmText = 'Confirmar', cancelText = 'Cancelar') {
    return new Promise((resolve) => {
        modalAlert.set({
            show: true,
            type: 'warning',
            title,
            message,
            showConfirmButton: true,
            confirmText,
            showCancelButton: true,
            cancelText,
            onConfirm: () => {
                modalAlert.update(m => ({ ...m, show: false }));
                resolve(true);
            },
            onCancel: () => {
                modalAlert.update(m => ({ ...m, show: false }));
                resolve(false);
            }
        });
    });
}

/**
 * Obtiene el título por defecto según el tipo de alerta
 */
function getTitleByType(type) {
    switch (type) {
        case 'success':
            return 'Éxito';
        case 'error':
            return 'Error';
        case 'warning':
            return 'Advertencia';
        case 'info':
        default:
            return 'Información';
    }
}
