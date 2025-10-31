<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import AuthService from '../login/authService.js';

    const dispatch = createEventDispatcher();

    // Props
    export let showModal = false;
    export let user = null;

    // Estado del formulario
    let formData = {
        email: '',
        password: '',
        confirmPassword: '',
        currentPassword: ''
    };

    let errors = {};
    let loading = false;
    let successMessage = '';

    // Resetear formulario cuando se abre el modal
    $: if (showModal && user) {
        formData = {
            email: user.email || '',
            password: '',
            confirmPassword: '',
            currentPassword: ''
        };
        errors = {};
        successMessage = '';
    }

    function closeModal() {
        showModal = false;
        dispatch('close');
    }

    function validateForm() {
        errors = {};

        // Validar que se proporcione la contraseña actual
        if (!formData.currentPassword) {
            errors.currentPassword = 'La contraseña actual es requerida';
        }

        // Validar email si se cambió
        if (formData.email !== user.email) {
            if (!formData.email) {
                errors.email = 'El email es requerido';
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
                errors.email = 'Formato de email inválido';
            }
        }

        // Validar contraseña si se proporciona
        if (formData.password) {
            if (formData.password.length < 6) {
                errors.password = 'La contraseña debe tener al menos 6 caracteres';
            }
            
            if (formData.password !== formData.confirmPassword) {
                errors.confirmPassword = 'Las contraseñas no coinciden';
            }
        }

        // Verificar que al menos se quiera cambiar algo
        const emailChanged = formData.email !== user.email;
        const passwordChanged = formData.password.length > 0;
        
        if (!emailChanged && !passwordChanged) {
            errors.general = 'Debe cambiar al menos el email o la contraseña';
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
                current_password: formData.currentPassword
            };

            // Solo incluir email si cambió
            if (formData.email !== user.email) {
                updateData.email = formData.email;
            }

            // Solo incluir contraseña si se proporcionó
            if (formData.password) {
                updateData.password = formData.password;
            }

            const response = await fetch('http://localhost:8000/api/auth/update-profile/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(updateData)
            });

            const result = await response.json();

            if (result.success) {
                successMessage = result.message;
                
                // Si se cambió la contraseña, cerrar sesión después de 3 segundos
                if (result.password_changed) {
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
                    // Si solo se cambió el email, actualizar la información del usuario
                    if (result.email_changed) {
                        dispatch('userUpdated', result.user);
                    }
                    
                    // Cerrar modal después de 2 segundos
                    setTimeout(() => {
                        closeModal();
                    }, 2000);
                }
            } else {
                errors.general = result.message || 'Error al actualizar el perfil';
            }
        } catch (error) {
            console.error('Error al actualizar perfil:', error);
            errors.general = 'Error de conexión. Intente nuevamente.';
        } finally {
            loading = false;
        }
    }

    // Cerrar modal al presionar Escape
    function handleKeydown(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if showModal}
    <!-- Overlay -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={closeModal}>
        <!-- Modal -->
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="modal" on:click|stopPropagation>
            <div class="modal-header">
                <h2>Editar Perfil</h2>
                <button class="close-button" on:click={closeModal} disabled={loading}>
                    &times;
                </button>
            </div>

            <div class="modal-body">
                {#if successMessage}
                    <div class="success-message">
                        <p>{successMessage}</p>
                        {#if successMessage.includes('contraseña')}
                            <p><strong>Cerrando sesión en 3 segundos...</strong></p>
                        {/if}
                    </div>
                {:else}
                    <form on:submit|preventDefault={handleSubmit}>
                        <!-- Email -->
                        <div class="form-group">
                            <label for="email">Email:</label>
                            <input
                                type="email"
                                id="email"
                                bind:value={formData.email}
                                disabled={loading}
                                class:error={errors.email}
                            />
                            {#if errors.email}
                                <span class="error-text">{errors.email}</span>
                            {/if}
                        </div>

                        <!-- Nueva contraseña -->
                        <div class="form-group">
                            <label for="password">Nueva contraseña (opcional):</label>
                            <input
                                type="password"
                                id="password"
                                bind:value={formData.password}
                                disabled={loading}
                                class:error={errors.password}
                                placeholder="Dejar vacío para mantener la actual"
                            />
                            {#if errors.password}
                                <span class="error-text">{errors.password}</span>
                            {/if}
                        </div>

                        <!-- Confirmar nueva contraseña -->
                        {#if formData.password}
                            <div class="form-group">
                                <label for="confirmPassword">Confirmar nueva contraseña:</label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    bind:value={formData.confirmPassword}
                                    disabled={loading}
                                    class:error={errors.confirmPassword}
                                />
                                {#if errors.confirmPassword}
                                    <span class="error-text">{errors.confirmPassword}</span>
                                {/if}
                            </div>
                        {/if}

                        <!-- Contraseña actual -->
                        <div class="form-group">
                            <label for="currentPassword">Contraseña actual *:</label>
                            <input
                                type="password"
                                id="currentPassword"
                                bind:value={formData.currentPassword}
                                disabled={loading}
                                class:error={errors.currentPassword}
                                required
                            />
                            {#if errors.currentPassword}
                                <span class="error-text">{errors.currentPassword}</span>
                            {/if}
                        </div>

                        <!-- Error general -->
                        {#if errors.general}
                            <div class="error-message">
                                {errors.general}
                            </div>
                        {/if}

                        <!-- Botones -->
                        <div class="modal-actions">
                            <button 
                                type="button" 
                                class="cancel-button" 
                                on:click={closeModal}
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                            <button 
                                type="submit" 
                                class="submit-button"
                                disabled={loading}
                            >
                                {loading ? 'Actualizando...' : 'Actualizar Perfil'}
                            </button>
                        </div>
                    </form>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal {
        background: white;
        border-radius: 8px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid #e0e0e0;
    }

    .modal-header h2 {
        margin: 0;
        color: #333;
        font-size: 1.5em;
    }

    .close-button {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .close-button:hover {
        color: #000;
    }

    .close-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .modal-body {
        padding: 20px;
    }

    .form-group {
        margin-bottom: 20px;
    }

    .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 500;
        color: #333;
    }

    .form-group input {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        box-sizing: border-box;
    }

    .form-group input:focus {
        outline: none;
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
    }

    .form-group input.error {
        border-color: #dc3545;
    }

    .form-group input:disabled {
        background-color: #f8f9fa;
        opacity: 0.7;
    }

    .error-text {
        display: block;
        color: #dc3545;
        font-size: 12px;
        margin-top: 5px;
    }

    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 20px;
        border: 1px solid #f5c6cb;
    }

    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
        border: 1px solid #c3e6cb;
        text-align: center;
    }

    .success-message p {
        margin: 0 0 10px 0;
    }

    .success-message p:last-child {
        margin-bottom: 0;
    }

    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
    }

    .cancel-button {
        background: #6c757d;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }

    .cancel-button:hover {
        background: #5a6268;
    }

    .submit-button {
        background: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }

    .submit-button:hover {
        background: #0056b3;
    }

    .cancel-button:disabled,
    .submit-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .submit-button:disabled:hover {
        background: #007bff;
    }
</style>