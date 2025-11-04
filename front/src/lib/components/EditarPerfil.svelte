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
            errors.currentPassword = 'Ingrese su contraseña actual para continuar.';
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
            errors.general = 'Debe cambiar el email o la contraseña';
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
    <div class="modal-backdrop" on:click={closeModal}>
        <!-- Modal -->
        <div class="modal-content" on:click|stopPropagation>
            <div class="modal-header">
                <h2>Editar Perfil</h2>
                <button class="close-button" on:click={closeModal} disabled={loading}>
                    &times;
                </button>
            </div>

            <div class="modal-body">
                {#if successMessage}
                    <div class="message success">
                        <p>{successMessage}</p>
                        {#if successMessage.includes('contraseña')}
                            <p><strong>Cerrando sesión en 3 segundos...</strong></p>
                        {/if}
                    </div>
                {:else}
                    <form on:submit|preventDefault={handleSubmit}>
                        <!-- Email -->
                        <div class="form-group">
                            <label for="email">Email</label>
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
                            <label for="password">Nueva Contraseña (opcional)</label>
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
                                <label for="confirmPassword">Confirmar Nueva Contraseña</label>
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
                        <div class="form-group current-password-group">
                            <label for="currentPassword">Contraseña Actual (obligatoria)</label>
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
                            <div class="message error">
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
                                class="save-button"
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
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        /* Estilo principal similar al profile-container */
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
        width: 90%;
        max-width: 500px;
        font-family: sans-serif;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }

    .modal-header h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
        margin: 0;
    }

    .close-button {
        background: none;
        border: none;
        font-size: 2rem;
        color: #333;
        cursor: pointer;
        line-height: 1;
    }

    .form-group {
        margin-bottom: 1.25rem;
    }

    .form-group label {
        display: block;
        font-weight: 600;
        color: #4a5568;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .form-group input {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f8f9fa;
        font-size: 1rem;
        box-sizing: border-box; /* Importante para que el padding no afecte el ancho */
    }

    .form-group input.error {
        border-color: #dc3545;
    }
    
    .current-password-group {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.3);
    }

    .error-text {
        display: block;
        color: #dc3545;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
    }

    .cancel-button,
    .save-button {
        padding: 0.7rem 1.3rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .cancel-button {
        background-color: #6c757d;
        color: white;
        border-color: #5a6268;
    }
    .cancel-button:hover {
        background-color: #5a6268;
    }

    .save-button {
        background-color: #2c5282;
        color: white;
        border-color: #1a365d;
    }
    .save-button:hover {
        background-color: #1a365d;
    }

    .cancel-button:disabled,
    .save-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 500;
    }
    .error {
        background-color: #fed7d7;
        color: #c53030;
    }
    .success {
        background-color: #c6f6d5;
        color: #2f855a;
    }
</style>