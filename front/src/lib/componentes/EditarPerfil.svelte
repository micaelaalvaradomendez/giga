<script>
    import { createEventDispatcher } from 'svelte';
    import AuthService from '../login/authService.js';

    const dispatch = createEventDispatcher();

    export let showModal = false;
    export let user = null;

    let activeTab = 'email';

    // Formulario para cambio de email
    let emailFormData = {
        newEmail: '',
        currentPassword: ''
    };

    // Formulario para cambio de contraseña
    let passwordFormData = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    };

    let errors = {};
    let loading = false;
    let successMessage = '';

    // Limpiar formularios cuando se abre el modal
    $: if (showModal) {
        resetForms();
    }

    function resetForms() {
        emailFormData = {
            newEmail: user?.email || '',
            currentPassword: ''
        };
        passwordFormData = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
        };
        errors = {};
        successMessage = '';
        activeTab = 'email';
    }

    function closeModal() {
        showModal = false;
        dispatch('close');
    }

    function validateEmailForm() {
        errors = {};

        if (!emailFormData.newEmail) {
            errors.newEmail = 'El email es requerido';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailFormData.newEmail)) {
            errors.newEmail = 'Formato de email inválido';
        }

        if (!emailFormData.currentPassword) {
            errors.currentPassword = 'La contraseña actual es requerida';
        }

        return Object.keys(errors).length === 0;
    }

    function validatePasswordForm() {
        errors = {};

        if (!passwordFormData.currentPassword) {
            errors.currentPassword = 'La contraseña actual es requerida';
        }

        if (!passwordFormData.newPassword) {
            errors.newPassword = 'La nueva contraseña es requerida';
        } else if (passwordFormData.newPassword.length < 6) {
            errors.newPassword = 'La contraseña debe tener al menos 6 caracteres';
        }

        if (user && user.dni && passwordFormData.newPassword === user.dni) {
            errors.newPassword = 'La nueva contraseña no puede ser igual a su DNI';
        }

        if (passwordFormData.newPassword !== passwordFormData.confirmPassword) {
            errors.confirmPassword = 'Las contraseñas no coinciden';
        }

        return Object.keys(errors).length === 0;
    }

    async function handleEmailSubmit() {
        if (!validateEmailForm()) {
            return;
        }

        loading = true;
        errors = {};
        successMessage = '';

        try {
            const response = await fetch('/api/auth/update-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    new_email: emailFormData.newEmail,
                    current_password: emailFormData.currentPassword
                })
            });

            const result = await response.json();

            if (result.success) {
                successMessage = 'Email actualizado exitosamente';
                
                // Actualizar la información del usuario
                const updatedUser = { ...user, email: emailFormData.newEmail };
                dispatch('userUpdated', updatedUser);
                
                setTimeout(() => {
                    closeModal();
                }, 2000);
            } else {
                errors.general = result.message || 'Error al actualizar el email';
            }
        } catch (error) {
            console.error('Error al actualizar email:', error);
            errors.general = 'Error de conexión. Intente nuevamente.';
        } finally {
            loading = false;
        }
    }

    async function handlePasswordSubmit() {
        if (!validatePasswordForm()) {
            return;
        }

        loading = true;
        errors = {};
        successMessage = '';

        try {
            const response = await fetch('/api/auth/change-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    current_password: passwordFormData.currentPassword,
                    new_password: passwordFormData.newPassword,
                    confirm_password: passwordFormData.confirmPassword
                })
            });

            const result = await response.json();

            if (result.success) {
                successMessage = 'Contraseña actualizada exitosamente. Cerrando sesión...';
                
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
                errors.general = result.message || 'Error al cambiar la contraseña';
            }
        } catch (error) {
            console.error('Error al cambiar contraseña:', error);
            errors.general = 'Error de conexión. Intente nuevamente.';
        } finally {
            loading = false;
        }
    }

    function handleKeydown(event) {
        if (event.key === 'Escape' && !loading) {
            closeModal();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if showModal}
    <div class="modal-overlay" on:click={closeModal}>
        <div class="modal-container" on:click|stopPropagation>
            <div class="modal-header">
                <h2>Editar Perfil</h2>
                <button class="close-button" on:click={closeModal} disabled={loading}>✕</button>
            </div>
            <div class="modal-body">
                <div class="tabs">
                    <button 
                        class="tab {activeTab === 'email' ? 'active' : ''}"
                        on:click={() => activeTab = 'email'}
                        disabled={loading}
                    >
                        📧 Cambiar Email
                    </button>
                    <button 
                        class="tab {activeTab === 'password' ? 'active' : ''}"
                        on:click={() => activeTab = 'password'}
                        disabled={loading}
                    >
                        🔒 Cambiar Contraseña
                    </button>
                </div>

                {#if successMessage}
                    <div class="success-message">
                        <p>{successMessage}</p>
                    </div>
                {:else}
                
                {#if activeTab === 'email'}
                    <div class="tab-content">
                        <h3>Cambiar Email</h3>
                        <form on:submit|preventDefault={handleEmailSubmit}>
                            <div class="form-group">
                                <label for="newEmail">Nuevo Email:</label>
                                <input
                                    type="email"
                                    id="newEmail"
                                    bind:value={emailFormData.newEmail}
                                    disabled={loading}
                                    class:error={errors.newEmail}
                                    required
                                    placeholder="nuevo@email.com"
                                />
                                {#if errors.newEmail}
                                    <span class="error-text">{errors.newEmail}</span>
                                {/if}
                            </div>

                            <div class="form-group">
                                <label for="currentPasswordEmail">Contraseña actual:</label>
                                <input
                                    type="password"
                                    id="currentPasswordEmail"
                                    bind:value={emailFormData.currentPassword}
                                    disabled={loading}
                                    class:error={errors.currentPassword}
                                    required
                                    placeholder="Su contraseña actual"
                                />
                                {#if errors.currentPassword}
                                    <span class="error-text">{errors.currentPassword}</span>
                                {/if}
                            </div>

                            {#if errors.general}
                                <div class="error-message">
                                    {errors.general}
                                </div>
                            {/if}

                            <div class="form-actions">
                                <button 
                                    type="submit" 
                                    class="submit-button"
                                    disabled={loading}
                                >
                                    {loading ? 'Actualizando...' : 'Actualizar Email'}
                                </button>
                            </div>
                        </form>
                    </div>
                {/if}

                {#if activeTab === 'password'}
                    <div class="tab-content">
                        <h3>Cambiar Contraseña</h3>
                        <form on:submit|preventDefault={handlePasswordSubmit}>
                            <div class="form-group">
                                <label for="currentPasswordPass">Contraseña actual:</label>
                                <input
                                    type="password"
                                    id="currentPasswordPass"
                                    bind:value={passwordFormData.currentPassword}
                                    disabled={loading}
                                    class:error={errors.currentPassword}
                                    required
                                    placeholder="Su contraseña actual"
                                />
                                {#if errors.currentPassword}
                                    <span class="error-text">{errors.currentPassword}</span>
                                {/if}
                            </div>

                            <div class="form-group">
                                <label for="newPassword">Nueva contraseña:</label>
                                <input
                                    type="password"
                                    id="newPassword"
                                    bind:value={passwordFormData.newPassword}
                                    disabled={loading}
                                    class:error={errors.newPassword}
                                    required
                                    placeholder="Mínimo 6 caracteres"
                                />
                                {#if errors.newPassword}
                                    <span class="error-text">{errors.newPassword}</span>
                                {/if}
                            </div>

                            <div class="form-group">
                                <label for="confirmPassword">Confirmar nueva contraseña:</label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    bind:value={passwordFormData.confirmPassword}
                                    disabled={loading}
                                    class:error={errors.confirmPassword}
                                    required
                                    placeholder="Repita la nueva contraseña"
                                />
                                {#if errors.confirmPassword}
                                    <span class="error-text">{errors.confirmPassword}</span>
                                {/if}
                            </div>

                            {#if errors.general}
                                <div class="error-message">
                                    {errors.general}
                                </div>
                            {/if}

                            <div class="security-info">
                                <h4>⚠️ Importante:</h4>
                                <ul>
                                    <li>Al cambiar la contraseña, su sesión será cerrada</li>
                                    <li>Deberá iniciar sesión nuevamente con la nueva contraseña</li>
                                    <li>Use al menos 6 caracteres</li>
                                    <li>No use su DNI como contraseña</li>
                                </ul>
                            </div>

                            <div class="form-actions">
                                <button 
                                    type="submit" 
                                    class="submit-button"
                                    disabled={loading}
                                >
                                    {loading ? 'Cambiando...' : 'Cambiar Contraseña'}
                                </button>
                            </div>
                        </form>
                    </div>
                {/if}
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
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-container {
        background: white;
        border-radius: 15px;
        max-width: 600px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        background: linear-gradient(135deg, #e79043, #d17a2e);
        color: white;
        padding: 20px 25px;
        border-radius: 15px 15px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .modal-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .close-button {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 5px 10px;
        border-radius: 50%;
    }

    .modal-body {
        padding: 30px 25px;
    }

    .tabs {
        display: flex;
        gap: 5px;
        margin-bottom: 25px;
        background: #f8f9fa;
        padding: 5px;
        border-radius: 10px;
    }

    .tab {
        flex: 1;
        background: none;
        border: none;
        padding: 12px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        color: #666;
    }

    .tab.active {
        background: #e79043;
        color: white;
    }

    .tab-content {
        padding: 20px 0;
    }

    .tab-content h3 {
        margin: 0 0 15px 0;
        color: #2c3e50;
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
        border-color: #e79043;
        box-shadow: 0 0 0 3px rgba(231, 144, 67, 0.1);
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
        background: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #ffeaa7;
    }

    .security-info h4 {
        margin: 0 0 10px 0;
        color: #856404;
        font-size: 1rem;
    }

    .security-info ul {
        margin: 0;
        padding-left: 20px;
        color: #856404;
    }

    .security-info li {
        margin-bottom: 5px;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .form-actions {
        text-align: center;
    }

    .submit-button {
        background: linear-gradient(135deg, #e79043, #d17a2e);
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
        background: linear-gradient(135deg, #d17a2e, #b8661e);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(231, 144, 67, 0.3);
    }

    .submit-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    .close-button:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.2);
    }

    .close-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    @media (max-width: 600px) {
        .modal-container {
            width: 95%;
        }

        .modal-header, .modal-body {
            padding: 20px 15px;
        }

        .tabs {
            flex-direction: column;
        }

        .tab {
            margin-bottom: 5px;
        }
    }
</style>
