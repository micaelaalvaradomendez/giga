import { writable } from 'svelte/store';

const isBrowser = typeof window !== 'undefined';
export const isAuthenticated = writable(false);
export const user = writable(null);

const API_BASE_URL = 'http://localhost:8000/api';

export class AuthService {

    static async login(cuil, password) {
        try {
            const cleanCuil = cuil.replace(/\D/g, '');
            const requestBody = {
                cuil: cleanCuil,
                password: password
            };
            const response = await fetch(`${API_BASE_URL}/auth/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            await fetch(`${API_BASE_URL}/auth/logout/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            const response = await fetch(`${API_BASE_URL}/auth/check-session/`, {
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
        return roles.includes(role);
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
}

export default AuthService;