/**
 * Debounce Utility
 * 
 * Implementa funcionalidad de debounce para optimizar operaciones costosas
 * como búsquedas, filtros y validaciones en tiempo real.
 */

/**
 * Crea una función debounced que retrasa la invocación de func
 * hasta que hayan pasado wait milisegundos desde la última vez que se invocó.
 * 
 * @param {Function} func - La función a debounce
 * @param {number} wait - El número de milisegundos a retrasar
 * @returns {Function} - La función debounced
 */
export function debounce(func, wait = 300) {
	let timeout;
	
	return function executedFunction(...args) {
		const later = () => {
			clearTimeout(timeout);
			func(...args);
		};
		
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
	};
}

/**
 * Crea una función throttled que solo invoca func como máximo una vez por cada intervalo.
 * Útil para eventos que se disparan muy frecuentemente (scroll, resize).
 * 
 * @param {Function} func - La función a throttle
 * @param {number} limit - El intervalo mínimo en milisegundos entre llamadas
 * @returns {Function} - La función throttled
 */
export function throttle(func, limit = 300) {
	let inThrottle;
	
	return function executedFunction(...args) {
		if (!inThrottle) {
			func(...args);
			inThrottle = true;
			setTimeout(() => inThrottle = false, limit);
		}
	};
}

/**
 * Constantes de tiempo de debounce recomendadas
 * Importadas desde constants si existen, sino valores por defecto
 */
export const DEBOUNCE_TIMES = {
	SEARCH: 300,      // Búsquedas de texto
	FILTER: 300,      // Filtros
	VALIDATION: 500,  // Validaciones de formulario
	AUTOSAVE: 1000,   // Guardado automático
	RESIZE: 150,      // Eventos de resize
	SCROLL: 100,      // Eventos de scroll
};
