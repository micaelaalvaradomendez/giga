// place files you want to import through the `$lib` alias in this folder.
/**
 * Panel de Administración - Controladores
 * 
 * Este archivo centraliza la exportación de todos los controladores del panel de administración.
 * Los controladores encapsulan la lógica de negocio y el manejo de estado para cada sección
 * del panel, separando la lógica de la presentación.
 * 
 * Arquitectura:
 * - Cada controlador maneja una sección específica del panel de administración
 * - Los controladores usan Svelte stores para el manejo de estado reactivo
 * - Se implementa el patrón singleton para evitar múltiples instancias
 * - La lógica de negocio está separada de los componentes UI
 * 
 * Uso:
 * import { usuariosController } from '$lib/paneladmin/controllers';
 * await usuariosController.init();
 */

// Importar todos los controladores
import { usuariosController } from './usuariosController.js';
import { rolesController } from './rolesController.js';
import { parametrosController } from './parametrosController.js';
import { organigramaController } from './organigramaController.js';
import { feriadosController } from './feriadosController.js';
import { auditoriaController } from './auditoriaController.js';
import { guardiasController } from './guardiasController.js';

// Exportar controladores
export { usuariosController, rolesController, parametrosController, organigramaController, feriadosController, auditoriaController, guardiasController };

// Re-exportar para compatibilidad
export {
	usuariosController as UsuariosController,
	rolesController as RolesController,
	parametrosController as ParametrosController,
	organigramaController as OrganigramaController,
	feriadosController as FeriadosController,
	auditoriaController as AuditoriaController,
	guardiasController as GuardiasController
};

/**
 * Función utilitaria para inicializar todos los controladores
 * Útil para inicialización en layout principal del panel de administración
 */
export async function initializeAllControllers() {
	try {
		// Los controladores se inicializan bajo demanda
		// Esta función está disponible para casos especiales donde se necesite
		// inicializar todos los controladores de una vez
		console.log('📋 Controladores del panel de administración disponibles');
		return {
			usuarios: usuariosController,
			roles: rolesController,
			parametros: parametrosController,
			organigrama: organigramaController,
			feriados: feriadosController,
			auditoria: auditoriaController,
			guardias: guardiasController
		};
	} catch (error) {
		console.error('❌ Error inicializando controladores:', error);
		throw error;
	}
}

/**
 * Función utilitaria para limpiar todos los stores
 * Útil para logout o cambio de sesión
 */
export function resetAllControllers() {
	try {
		// Cada controlador debería implementar un método reset si es necesario
		console.log('🧹 Limpiando estado de controladores');
		
		// Por ahora, los stores se limpiarán automáticamente en la siguiente carga
		// En el futuro, cada controlador puede implementar un método reset()
		
	} catch (error) {
		console.error('❌ Error limpiando controladores:', error);
	}
}