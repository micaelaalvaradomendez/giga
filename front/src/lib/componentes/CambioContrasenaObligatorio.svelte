<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import AuthService from '../login/authService.js';

    const dispatch = createEventDispatcher();

    // Props
    export let showAlert = false;
    export let user = null;

    // Estado del formulario
    let formData = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    };

    let errors = {};
    let loading = false;
    let successMessage = '';

    function validateForm() {
        errors = {};

        // Validar contraseña actual
        if (!formData.currentPassword) {
            errors.currentPassword = 'La contraseña actual es requerida';
        }

        // Validar nueva contraseña
        if (!formData.newPassword) {
            errors.newPassword = 'La nueva contraseña es requerida';
        } else if (formData.newPassword.length < 6) {
            errors.newPassword = 'La contraseña debe tener al menos 6 caracteres';
        }

        // Verificar que la nueva contraseña no sea igual al DNI
        if (user && user.cuil && formData.newPassword) {
            const dni = user.cuil.slice(2, 10); // Extraer DNI del CUIL
            if (formData.newPassword === dni) {
                errors.newPassword = 'La nueva contraseña no puede ser igual a tu DNI';
            }
        }

        // Confirmar contraseña
        if (formData.newPassword !== formData.confirmPassword) {
            errors.confirmPassword = 'Las contraseñas no coinciden';
        }

        return Object.keys(errors).length === 0;
    }

    async function handleSubmit() {
        if (!validateForm()) {
            return;
        }

        loading = true;
        errors = {};
        successMessage = '';

        try {
            const updateData = {
                current_password: formData.currentPassword,
                new_password: formData.newPassword,
                confirm_password: formData.confirmPassword
            };

            const response = await fetch('/api/auth/change-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(updateData)
            });

            const result = await response.json();

            if (result.success) {
                successMessage = 'Contraseña actualizada exitosamente. Cerrando sesión...';
                
                // Marcar que ya no requiere cambio de contraseña
                if (typeof localStorage !== 'undefined') {
                    localStorage.setItem('requires_password_change', 'false');
                }
                
                // Cerrar sesión después de 3 segundos
                setTimeout(async () => {
                    try {
                        await AuthService.logout();
                        window.location.href = '/';
                    } catch (error) {
                        console.error('Error al cerrar sesión:', error);
                        window.location.href = '/';
                    }
                }, 3000);
            } else {
                errors.general = result.message || 'Error al actualizar la contraseña';
            }
        } catch (error) {
            console.error('Error al actualizar contraseña:', error);
            errors.general = 'Error de conexión. Intente nuevamente.';
        } finally {
            loading = false;
        }
    }

    // No permitir cerrar hasta cambiar la contraseña
    function handleKeydown(event) {
        // Bloquear escape
        if (event.key === 'Escape') {
            event.preventDefault();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if showAlert}
    <!-- Overlay que no se puede cerrar -->
    <div class="mandatory-overlay">
        <!-- Modal -->
        <div class="mandatory-modal">
            <div class="modal-header">
                <h2>Cambio de Contraseña Obligatorio</h2>
                <p class="warning-text">
                    Por razones de seguridad, debes cambiar tu contraseña actual antes de continuar.
                </p>
            </div>

            <div class="modal-body">
                {#if successMessage}
                    <div class="success-message">
                        <p>{successMessage}</p>
                    </div>
                {:else}
                    <form on:submit|preventDefault={handleSubmit}>
                        <!-- Contraseña actual -->
                        <div class="form-group">
                            <label for="currentPassword">Contraseña actual:</label>
                            <input
                                type="password"
                                id="currentPassword"
                                bind:value={formData.currentPassword}
                                disabled={loading}
                                class:error={errors.currentPassword}
                                required
                                placeholder="Tu contraseña actual"
                            />
                            {#if errors.currentPassword}
                                <span class="error-text">{errors.currentPassword}</span>
                            {/if}
                        </div>

                        <!-- Nueva contraseña -->
                        <div class="form-group">
                            <label for="newPassword">Nueva contraseña:</label>
                            <input
                                type="password"
                                id="newPassword"
                                bind:value={formData.newPassword}
                                disabled={loading}
                                class:error={errors.newPassword}
                                required
                                placeholder="Mínimo 6 caracteres"
                            />
                            {#if errors.newPassword}
                                <span class="error-text">{errors.newPassword}</span>
                            {/if}
                        </div>

                        <!-- Confirmar nueva contraseña -->
                        <div class="form-group">
                            <label for="confirmPassword">Confirmar nueva contraseña:</label>
                            <input
                                type="password"
                                id="confirmPassword"
                                bind:value={formData.confirmPassword}
                                disabled={loading}
                                class:error={errors.confirmPassword}
                                required
                                placeholder="Repite la nueva contraseña"
                            />
                            {#if errors.confirmPassword}
                                <span class="error-text">{errors.confirmPassword}</span>
                            {/if}
                        </div>

                        <!-- Error general -->
                        {#if errors.general}
                            <div class="error-message">
                                {errors.general}
                            </div>
                        {/if}

                        <!-- Información de seguridad -->
                        <div class="security-info">
                            <h4>Recomendaciones de seguridad:</h4>
                            <ul>
                                <li>Usa al menos 6 caracteres</li>
                                <li>No uses tu DNI como contraseña</li>
                                <li>Combina letras, números y símbolos</li>
                                <li>No uses información personal</li>
                            </ul>
                        </div>

                        <!-- Botón de envío -->
                        <div class="modal-actions">
                            <button 
                                type="submit" 
                                class="submit-button"
                                disabled={loading}
                            >
                                {loading ? 'Cambiando...' : 'Cambiar Contraseña'}
                            </button>
                        </div>
                    </form>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    .mandatory-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        backdrop-filter: blur(5px);
    }

    .mandatory-modal {
        background: white;
        border-radius: 15px;
        max-width: 500px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        border: 3px solid #e74c3c;
    }

    .modal-header {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 25px 20px;
        text-align: center;
        border-radius: 12px 12px 0 0;
    }

    .warning-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    .modal-header h2 {
        margin: 0 0 10px 0;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .warning-text {
        margin: 0;
        font-size: 1rem;
        line-height: 1.4;
        opacity: 0.9;
    }

    .modal-body {
        padding: 30px 25px;
    }

    .form-group {
        margin-bottom: 20px;
    }

    .form-group label {
        display: block;
        margin-bottom: 6px;
        font-weight: 600;
        color: #2c3e50;
        font-size: 0.95rem;
    }

    .form-group input {
        width: 100%;
        padding: 12px;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 14px;
        box-sizing: border-box;
        transition: all 0.3s ease;
    }

    .form-group input:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }

    .form-group input.error {
        border-color: #e74c3c;
    }

    .form-group input:disabled {
        background-color: #f8f9fa;
        opacity: 0.7;
    }

    .error-text {
        display: block;
        color: #e74c3c;
        font-size: 12px;
        margin-top: 5px;
        font-weight: 500;
    }

    .error-message {
        background-color: #fdf2f2;
        color: #c53030;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #fed7d7;
        font-weight: 500;
    }

    .success-message {
        background-color: #f0fff4;
        color: #2d7d32;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #c8e6c9;
        text-align: center;
        font-weight: 500;
    }

    .security-info {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border-left: 4px solid #3498db;
    }

    .security-info h4 {
        margin: 0 0 12px 0;
        color: #2c3e50;
        font-size: 1rem;
    }

    .security-info ul {
        margin: 0;
        padding-left: 20px;
        color: #5a6c7d;
    }

    .security-info li {
        margin-bottom: 6px;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .modal-actions {
        text-align: center;
    }

    .submit-button {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        cursor: pointer;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .submit-button:hover:not(:disabled) {
        background: linear-gradient(135deg, #229954, #27ae60);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
    }

    .submit-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    .submit-button:disabled:hover {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
    }
</style>