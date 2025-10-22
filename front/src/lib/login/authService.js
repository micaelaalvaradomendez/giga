// Servicio de autenticación para comunicarse con el backend
const API_BASE_URL = 'http://localhost:8000/api';

export class AuthService {
    
    /**
     * Realiza el login con CUIL y contraseña
     * @param {string} cuil - CUIL del usuario (con o sin guiones)
     * @param {string} password - Contraseña del usuario
     * @returns {Promise<Object>} Respuesta del servidor
     */
    static async login(cuil, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/personas/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Importante para las cookies de sesión
                body: JSON.stringify({
                    cuil: cuil.replace(/\D/g, ''), // Remover caracteres no numéricos
                    password: password
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Guardar información del usuario en localStorage
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('isAuthenticated', 'true');
                
                return {
                    success: true,
                    user: data.user,
                    message: data.message
                };
            } else {
                return {
                    success: false,
                    message: data.message || 'Error en el login'
                };
            }
        } catch (error) {
            console.error('Error en login:', error);
            return {
                success: false,
                message: 'Error de conexión. Verifique su conexión a internet.'
            };
        }
    }

    /**
     * Cierra la sesión del usuario
     * @returns {Promise<Object>} Respuesta del logout
     */
    static async logout() {
        try {
            const response = await fetch(`${API_BASE_URL}/personas/auth/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            const data = await response.json();
            
            // Limpiar localStorage independientemente de la respuesta
            localStorage.removeItem('user');
            localStorage.removeItem('isAuthenticated');
            
            return {
                success: true,
                message: 'Sesión cerrada correctamente'
            };
        } catch (error) {
            console.error('Error en logout:', error);
            // Aun con error, limpiamos el localStorage
            localStorage.removeItem('user');
            localStorage.removeItem('isAuthenticated');
            
            return {
                success: false,
                message: 'Error al cerrar sesión, pero se limpió la sesión local'
            };
        }
    }

    /**
     * Verifica si el usuario está autenticado
     * @returns {Promise<Object>} Estado de autenticación
     */
    static async checkSession() {
        try {
            const response = await fetch(`${API_BASE_URL}/personas/auth/check-session/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            const data = await response.json();
            
            if (data.authenticated) {
                // Actualizar información del usuario en localStorage
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('isAuthenticated', 'true');
                
                return {
                    authenticated: true,
                    user: data.user
                };
            } else {
                // Limpiar localStorage si no está autenticado
                localStorage.removeItem('user');
                localStorage.removeItem('isAuthenticated');
                
                return {
                    authenticated: false
                };
            }
        } catch (error) {
            console.error('Error verificando sesión:', error);
            // En caso de error, asumir no autenticado
            localStorage.removeItem('user');
            localStorage.removeItem('isAuthenticated');
            
            return {
                authenticated: false,
                error: 'Error de conexión'
            };
        }
    }

    /**
     * Obtiene el usuario desde localStorage
     * @returns {Object|null} Datos del usuario o null si no está autenticado
     */
    static getCurrentUser() {
        try {
            const userStr = localStorage.getItem('user');
            const isAuthenticated = localStorage.getItem('isAuthenticated');
            
            if (isAuthenticated === 'true' && userStr) {
                return JSON.parse(userStr);
            }
            
            return null;
        } catch (error) {
            console.error('Error obteniendo usuario actual:', error);
            return null;
        }
    }

    /**
     * Verifica si el usuario está autenticado (verificación local)
     * @returns {boolean} True si está autenticado
     */
    static isAuthenticated() {
        const isAuth = localStorage.getItem('isAuthenticated');
        const user = localStorage.getItem('user');
        
        return isAuth === 'true' && user !== null;
    }

    /**
     * Obtiene el rol principal del usuario actual
     * @returns {string|null} Rol del usuario o null
     */
    static getUserRole() {
        const user = this.getCurrentUser();
        return user ? user.rol_principal : null;
    }

    /**
     * Obtiene todos los roles del usuario actual
     * @returns {Array} Array de roles del usuario
     */
    static getUserRoles() {
        const user = this.getCurrentUser();
        return user ? user.roles : [];
    }

    /**
     * Verifica si el usuario tiene un rol específico
     * @param {string} role - Rol a verificar
     * @returns {boolean} True si el usuario tiene el rol
     */
    static hasRole(role) {
        const roles = this.getUserRoles();
        return roles.includes(role);
    }

    /**
     * Formatea el CUIL para mostrar con guiones
     * @param {string} cuil - CUIL sin formato
     * @returns {string} CUIL formateado XX-XXXXXXXX-X
     */
    static formatCuil(cuil) {
        if (!cuil || cuil.length !== 11) return cuil;
        
        return `${cuil.slice(0, 2)}-${cuil.slice(2, 10)}-${cuil.slice(10)}`;
    }
}

export default AuthService;