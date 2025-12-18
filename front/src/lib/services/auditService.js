/**
 * Servicio de Auditoría - Frontend
 * Registra eventos de seguridad y acceso en el sistema
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class AuditService {
    /**
     * Registra un intento de acceso no autorizado
     * @param {Object} params - Parámetros del evento
     * @param {string} params.ruta - Ruta a la que se intentó acceder
     * @param {string} params.accion - Acción que se intentó realizar
     * @param {string} params.rol - Rol del usuario que intent\u00f3 acceder
     * @param {number} params.userId - ID del usuario
     */
    async logUnauthorizedAccess({ ruta, accion, rol, userId }) {
        try {
            const response = await fetch(`${API_URL}/api/auditoria/log-unauthorized/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    nombre_tabla: 'sistema_acceso',
                    accion: 'ACCESO_DENEGADO',
                    pk_afectada: userId,
                    valor_nuevo: {
                        ruta,
                        accion_intentada: accion,
                        rol_usuario: rol,
                        timestamp: new Date().toISOString(),
                        user_agent: navigator.userAgent
                    }
                })
            });

        } catch (error) {
            // No lanzar error para no interrumpir el flujo de la aplicación
        }
    }

    /**
     * Registra acceso exitoso al panel admin
     * @param {Object} params - Parámetros del evento
     */
    async logSuccessfulAccess({ ruta, rol, userId }) {
        try {
            await fetch(`${API_URL}/api/auditoria/log-access/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    nombre_tabla: 'sistema_acceso',
                    accion: 'ACCESO_EXITOSO',
                    pk_afectada: userId,
                    valor_nuevo: {
                        ruta,
                        rol_usuario: rol,
                        timestamp: new Date().toISOString()
                    }
                })
            });
        } catch (error) {
        }
    }
}

export default new AuditService();
