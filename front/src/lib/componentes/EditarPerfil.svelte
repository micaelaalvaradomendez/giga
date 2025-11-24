<script>
    import { createEventDispatcher } from "svelte";
    import AuthService from "../login/authService.js";

    const dispatch = createEventDispatcher();

    export let showModal = false;
    export let user = null;

    let activeTab = "email";

    // Formulario para cambio de email
    let emailFormData = {
        newEmail: "",
        currentPassword: "",
    };

    // Formulario para cambio de contraseña
    let passwordFormData = {
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
    };

    let errors = {};
    let loading = false;
    let successMessage = "";

    // Limpiar formularios cuando se abre el modal
    $: if (showModal) {
        resetForms();
    }

    function resetForms() {
        emailFormData = {
            newEmail: user?.email || "",
            currentPassword: "",
        };
        passwordFormData = {
            currentPassword: "",
            newPassword: "",
            confirmPassword: "",
        };
        errors = {};
        successMessage = "";
        activeTab = "email";
    }

    function closeModal() {
        showModal = false;
        dispatch("close");
    }

    function validateEmailForm() {
        errors = {};

        if (!emailFormData.newEmail) {
            errors.newEmail = "El email es requerido";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailFormData.newEmail)) {
            errors.newEmail = "Formato de email inválido";
        }

        if (!emailFormData.currentPassword) {
            errors.currentPassword = "La contraseña actual es requerida";
        }

        return Object.keys(errors).length === 0;
    }

    function validatePasswordForm() {
        errors = {};

        if (!passwordFormData.currentPassword) {
            errors.currentPassword = "La contraseña actual es requerida";
        }

        if (!passwordFormData.newPassword) {
            errors.newPassword = "La nueva contraseña es requerida";
        } else if (passwordFormData.newPassword.length < 6) {
            errors.newPassword =
                "La contraseña debe tener al menos 6 caracteres";
        }

        if (user && user.dni && passwordFormData.newPassword === user.dni) {
            errors.newPassword =
                "La nueva contraseña no puede ser igual a su DNI";
        }

        if (passwordFormData.newPassword !== passwordFormData.confirmPassword) {
            errors.confirmPassword = "Las contraseñas no coinciden";
        }

        return Object.keys(errors).length === 0;
    }

    async function handleEmailSubmit() {
        if (!validateEmailForm()) {
            return;
        }

        loading = true;
        errors = {};
        successMessage = "";

        try {
            const response = await fetch("/api/personas/auth/update-email/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    new_email: emailFormData.newEmail,
                    current_password: emailFormData.currentPassword,
                }),
            });

            const result = await response.json();

            if (result.success) {
                successMessage = "Email actualizado exitosamente";

                // Actualizar la información del usuario
                const updatedUser = { ...user, email: emailFormData.newEmail };
                dispatch("userUpdated", updatedUser);

                setTimeout(() => {
                    closeModal();
                }, 2000);
            } else {
                errors.general =
                    result.message || "Error al actualizar el email";
            }
        } catch (error) {
            console.error("Error al actualizar email:", error);
            errors.general = "Error de conexión. Intente nuevamente.";
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
        successMessage = "";

        try {
            const result = await AuthService.changePassword(
                passwordFormData.currentPassword,
                passwordFormData.newPassword,
                passwordFormData.confirmPassword,
            );

            if (result.success) {
                successMessage =
                    "Contraseña actualizada exitosamente. Cerrando sesión...";

                setTimeout(async () => {
                    try {
                        await AuthService.logout();
                        window.location.href = "/";
                    } catch (error) {
                        console.error("Error al cerrar sesión:", error);
                        window.location.href = "/";
                    }
                }, 3000);
            } else {
                errors.general =
                    result.message || "Error al cambiar la contraseña";
            }
        } catch (error) {
            console.error("Error al cambiar contraseña:", error);
            errors.general = "Error de conexión. Intente nuevamente.";
        } finally {
            loading = false;
        }
    }

    function handleKeydown(event) {
        if (event.key === "Escape" && !loading) {
            closeModal();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if showModal}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={closeModal}>
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="modal-container" on:click|stopPropagation>
            <div class="modal-header">
                <h2>Editar Perfil</h2>
                <button
                    class="close-button"
                    on:click={closeModal}
                    disabled={loading}>✕</button
                >
            </div>
            <div class="modal-body">
                <div class="tabs">
                    <button
                        class="tab {activeTab === 'email' ? 'active' : ''}"
                        on:click={() => (activeTab = "email")}
                        disabled={loading}
                    >
                        📧 Cambiar Email
                    </button>
                    <button
                        class="tab {activeTab === 'password' ? 'active' : ''}"
                        on:click={() => (activeTab = "password")}
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
                    {#if activeTab === "email"}
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
                                        <span class="error-text"
                                            >{errors.newEmail}</span
                                        >
                                    {/if}
                                </div>

                                <div class="form-group">
                                    <label for="currentPasswordEmail"
                                        >Contraseña actual:</label
                                    >
                                    <input
                                        type="password"
                                        id="currentPasswordEmail"
                                        bind:value={
                                            emailFormData.currentPassword
                                        }
                                        disabled={loading}
                                        class:error={errors.currentPassword}
                                        required
                                        placeholder="Su contraseña actual"
                                    />
                                    {#if errors.currentPassword}
                                        <span class="error-text"
                                            >{errors.currentPassword}</span
                                        >
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
                                        {loading
                                            ? "Actualizando..."
                                            : "Actualizar Email"}
                                    </button>
                                </div>
                            </form>
                        </div>
                    {/if}

                    {#if activeTab === "password"}
                        <div class="tab-content">
                            <h3>Cambiar Contraseña</h3>
                            <form
                                on:submit|preventDefault={handlePasswordSubmit}
                            >
                                <div class="form-group">
                                    <label for="currentPasswordPass"
                                        >Contraseña actual:</label
                                    >
                                    <input
                                        type="password"
                                        id="currentPasswordPass"
                                        bind:value={
                                            passwordFormData.currentPassword
                                        }
                                        disabled={loading}
                                        class:error={errors.currentPassword}
                                        required
                                        placeholder="Su contraseña actual"
                                    />
                                    {#if errors.currentPassword}
                                        <span class="error-text"
                                            >{errors.currentPassword}</span
                                        >
                                    {/if}
                                </div>

                                <div class="form-group">
                                    <label for="newPassword"
                                        >Nueva contraseña:</label
                                    >
                                    <input
                                        type="password"
                                        id="newPassword"
                                        bind:value={
                                            passwordFormData.newPassword
                                        }
                                        disabled={loading}
                                        class:error={errors.newPassword}
                                        required
                                        placeholder="Mínimo 6 caracteres"
                                    />
                                    {#if errors.newPassword}
                                        <span class="error-text"
                                            >{errors.newPassword}</span
                                        >
                                    {/if}
                                </div>

                                <div class="form-group">
                                    <label for="confirmPassword"
                                        >Confirmar nueva contraseña:</label
                                    >
                                    <input
                                        type="password"
                                        id="confirmPassword"
                                        bind:value={
                                            passwordFormData.confirmPassword
                                        }
                                        disabled={loading}
                                        class:error={errors.confirmPassword}
                                        required
                                        placeholder="Repita la nueva contraseña"
                                    />
                                    {#if errors.confirmPassword}
                                        <span class="error-text"
                                            >{errors.confirmPassword}</span
                                        >
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
                                        <li>
                                            Al cambiar la contraseña, su sesión
                                            será cerrada
                                        </li>
                                        <li>
                                            Deberá iniciar sesión nuevamente con
                                            la nueva contraseña
                                        </li>
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
                                        {loading
                                            ? "Cambiando..."
                                            : "Cambiar Contraseña"}
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
        backdrop-filter: blur(4px);
    }

    .modal-container {
        background: white;
        border-radius: 16px;
        max-width: 600px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease-out;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .modal-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 2rem;
        border-radius: 16px 16px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
    }

    .modal-header h2 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
    }

    .close-button {
        background: transparent;
        border: none;
        color: white;
        font-size: 2rem;
        cursor: pointer;
        padding: 0;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        font-weight: 300;
    }

    .close-button:hover:not(:disabled) {
        transform: scale(1.2) rotate(90deg);
        color: rgba(255, 255, 255, 0.8);
    }

    .close-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .modal-body {
        padding: 2rem;
    }

    .tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 12px;
        border: 2px solid #e9ecef;
    }

    .tab {
        flex: 1;
        background: white;
        border: 2px solid #dee2e6;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        color: #6c757d;
        font-size: 0.95rem;
        transition: all 0.3s;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        position: relative;
    }

    .tab:hover:not(:disabled) {
        color: #667eea;
        background: #f8f9ff;
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.15);
    }

    .tab.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .tab.active::after {
        margin-left: 0.5rem;
        font-weight: bold;
    }

    .tab:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .tab-content h3 {
        margin: 0 0 1.5rem 0;
        color: #1a1a1a;
        font-size: 1.25rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        padding-bottom: 0.75rem;
    }

    .tab-content h3::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from {
            width: 0;
            opacity: 0;
        }
        to {
            width: 60px;
            opacity: 1;
        }
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #1a1a1a;
        font-size: 18px;
    }

    .form-group input {
        width: 100%;
        padding: 0.875rem 1rem;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        font-size: 18px;
        box-sizing: border-box;
        transition: all 0.2s ease;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .form-group input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .form-group input.error {
        border-color: #f5576c;
    }

    .form-group input:disabled {
        background-color: #f8f9fa;
        opacity: 0.7;
        cursor: not-allowed;
    }

    .error-text {
        display: block;
        color: #f5576c;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    .error-message {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
        color: #c53030;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 2px solid #fed7d7;
        font-weight: 500;
        font-size: 0.9rem;
    }

    .success-message {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        color: #22543d;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 2px solid #9ae6b4;
        text-align: center;
        font-weight: 600;
        font-size: 1rem;
        animation: slideUp 0.3s ease-out;
    }

    .security-info {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 2px solid #ffeaa7;
    }

    .security-info h4 {
        margin: 0 0 0.75rem 0;
        color: #694f00;
        font-size: 18px;
        font-weight: 600;
    }

    .security-info ul {
        margin: 0;
        padding-left: 1.5rem;
        color: #856404;
    }

    .security-info li {
        margin-bottom: 0.5rem;
        font-size: 16px;
        line-height: 1.5;
    }

    .form-actions {
        text-align: center;
        margin-top: 2rem;
    }

    .submit-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        cursor: pointer;
        font-size: 20px;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .submit-button:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    .submit-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    @media (max-width: 600px) {
        .modal-container {
            width: 95%;
        }

        .modal-header,
        .modal-body {
            padding: 1.5rem;
        }

        .modal-header h2 {
            font-size: 1.5rem;
        }

        .tabs {
            flex-direction: column;
            gap: 0.5rem;
        }
    }
</style>
