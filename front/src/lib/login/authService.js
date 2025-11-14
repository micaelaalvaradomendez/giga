import { writable } from 'svelte/store';

const isBrowser = typeof window !== 'undefined';
export const isAuthenticated = writable(false);
export const user = writable(null);

// Usar la URL a través de nginx (puerto 80) en lugar de directo al backend
const API_BASE_URL = '/api';

export class AuthService {
    // Obtener token CSRF desde cookie (si existe)
    static getCsrfToken() {
        if (!isBrowser) return null;
        const match = document.cookie.match(new RegExp('(^|;)\\s*' + 'csrftoken' + '\\s*=\\s*([^;]+)'));
        return match ? match.pop() : null;
    }

    static async login(cuil, password) {
        try {
            const cleanCuil = cuil.replace(/\D/g, '');
            const requestBody = {
                cuil: cleanCuil,
                password: password
            };
            const headers = { 'Content-Type': 'application/json' };
            const csrf = this.getCsrfToken();
            if (csrf) headers['X-CSRFToken'] = csrf;

            const response = await fetch(`${API_BASE_URL}/personas/auth/login/`, {
                method: 'POST',
                headers,
                credentials: 'include',
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            if (data.success) {
                if (isBrowser) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    localStorage.setItem('isAuthenticated', 'true');
                    localStorage.setItem('requires_password_change', data.requires_password_change || false);
                }
                isAuthenticated.set(true);
                user.set(data.user);
                return { 
                    success: true, 
                    user: data.user, 
                    message: data.message,
                    requires_password_change: data.requires_password_change || false,
                    password_reset_reason: data.password_reset_reason
                };
            } else {
                return { success: false, message: data.message || 'Error en el login' };
            }
        } catch (error) {
            return { success: false, message: 'Error de conexión. Verifique su conexión a internet.' };
        }
    }

    static async logout() {
        try {
            const headers = { 'Content-Type': 'application/json' };
            const csrf = this.getCsrfToken();
            if (csrf) headers['X-CSRFToken'] = csrf;
            await fetch(`${API_BASE_URL}/personas/auth/logout/`, {
                method: 'POST',
                headers,
                credentials: 'include'
            });
        } catch (error) {
            console.error('Error en logout:', error);
        } finally {
            if (isBrowser) {
                localStorage.removeItem('user');
                localStorage.removeItem('isAuthenticated');
            }
            isAuthenticated.set(false);
            user.set(null);
        }
        return { success: true, message: 'Sesión cerrada' };
    }

    static async checkSession() {
        if (!isBrowser) return { authenticated: false };

        try {
            const response = await fetch(`${API_BASE_URL}/personas/auth/check-session/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });

            const data = await response.json();

            if (data.authenticated) {
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('isAuthenticated', 'true');
                localStorage.setItem('requires_password_change', data.requires_password_change || false);
                isAuthenticated.set(true);
                user.set(data.user);
                return { 
                    authenticated: true, 
                    user: data.user,
                    requires_password_change: data.requires_password_change || false
                };
            } else {
                localStorage.removeItem('user');
                localStorage.removeItem('isAuthenticated');
                localStorage.removeItem('requires_password_change');
                isAuthenticated.set(false);
                user.set(null);
                return { authenticated: false };
            }
        } catch (error) {
            console.error('Error verificando sesión:', error);
            if (isBrowser) {
                localStorage.removeItem('user');
                localStorage.removeItem('isAuthenticated');
            }
            isAuthenticated.set(false);
            user.set(null);
            return { authenticated: false, error: 'Error de conexión' };
        }
    }

    static getCurrentUser() {
        if (!isBrowser) return null;
        try {
            const userStr = localStorage.getItem('user');
            const isAuth = localStorage.getItem('isAuthenticated');
            if (isAuth === 'true' && userStr) {
                return JSON.parse(userStr);
            }
            return null;
        } catch (error) {
            console.error('Error obteniendo usuario actual:', error);
            return null;
        }
    }

    static isAuthenticated() {
        if (!isBrowser) return false;
        const isAuth = localStorage.getItem('isAuthenticated');
        return isAuth === 'true';
    }

    static getUserRoles() {
        if (!isBrowser) return [];
        const user = this.getCurrentUser();
        return user ? user.roles : [];
    }

    static hasRole(role) {
        if (!isBrowser) return false;
        const roles = this.getUserRoles();
        
        // Manejar tanto roles como strings ["Administrador"] como objetos [{nombre: "Administrador"}]
        if (roles && roles.length > 0) {
            if (typeof roles[0] === 'string') {
                return roles.includes(role);
            } else if (typeof roles[0] === 'object' && roles[0].nombre) {
                return roles.some(r => r.nombre === role);
            }
        }
        return false;
    }

    static formatCuil(cuil) {
        if (!cuil || cuil.length !== 11) return cuil;
        return `${cuil.slice(0, 2)}-${cuil.slice(2, 10)}-${cuil.slice(10)}`;
    }

    static requiresPasswordChange() {
        if (!isBrowser) return false;
        const requiresChange = localStorage.getItem('requires_password_change');
        return requiresChange === 'true';
    }

    static async changePassword(currentPassword, newPassword, confirmPassword) {
        try {
            const headers = { 'Content-Type': 'application/json' };
            const csrf = this.getCsrfToken();
            if (csrf) headers['X-CSRFToken'] = csrf;

            const response = await fetch(`${API_BASE_URL}/personas/auth/change-password/`, {
                method: 'POST',
                headers,
                credentials: 'include',
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: 'Error de conexión. Verifique su conexión a internet.' };
        }
    }

    static async updateProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/personas/auth/update-profile/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });

            const data = await response.json();
            
            if (data.success && isBrowser) {
                localStorage.setItem('user', JSON.stringify(data.user));
                user.set(data.user);
            }
            
            return data;
        } catch (error) {
            return { success: false, message: 'Error de conexión.' };
        }
    }

    static async recoverPassword(cuil) {
        try {
            const cleanCuil = cuil.replace(/\D/g, '');
            const response = await fetch(`${API_BASE_URL}/personas/auth/recover-password/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ cuil: cleanCuil })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            return { success: false, message: 'Error de conexión. Verifique su conexión a internet.' };
        }
    }
}

export default AuthService;