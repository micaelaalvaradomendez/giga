<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let cuil = '';
    let isLoading = false;
    let successMessage = '';
    let errorMessage = '';
    let showResult = false;
    let maskedEmail = '';

    function formatCuil(value) {
        // Remover todo excepto números
        const numbers = value.replace(/\D/g, '');
        
        // Formatear como XX-XXXXXXXX-X
        if (numbers.length <= 2) {
            return numbers;
        } else if (numbers.length <= 10) {
            return `${numbers.slice(0, 2)}-${numbers.slice(2)}`;
        } else {
            return `${numbers.slice(0, 2)}-${numbers.slice(2, 10)}-${numbers.slice(10, 11)}`;
        }
    }

    function handleCuilInput(event) {
        const formatted = formatCuil(event.target.value);
        cuil = formatted;
        event.target.value = formatted;
    }

    async function handleSubmit(event) {
        event.preventDefault();
        
        // Resetear mensajes
        successMessage = '';
        errorMessage = '';
        showResult = false;
        
        // Validar CUIL
        const cleanCuil = cuil.replace(/\D/g, '');
        if (!cleanCuil) {
            errorMessage = 'Por favor ingresa tu CUIL';
            return;
        }
        
        if (cleanCuil.length !== 11) {
            errorMessage = 'El CUIL debe tener 11 dígitos';
            return;
        }

        isLoading = true;

        try {
            const response = await fetch('http://localhost:8000/api/auth/recover-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    cuil: cleanCuil
                })
            });

            const result = await response.json();

            if (result.success) {
                successMessage = result.message;
                maskedEmail = result.email;
                showResult = true;
                
                // Limpiar el formulario
                cuil = '';
            } else {
                errorMessage = result.message || 'Error al procesar la solicitud';
            }
        } catch (error) {
            console.error('Error:', error);
            errorMessage = 'Error de conexión. Intenta nuevamente.';
        } finally {
            isLoading = false;
        }
    }

    function goToLogin() {
        goto('/');
    }
</script>

<svelte:head>
    <title>Recuperar Contraseña - GIGA</title>
</svelte:head>

<div class="login-container">
    <div class="login-card">

        <!-- Contenido principal -->
        <div class="content">
            <div class="title-section">
                <h1>Recuperar Contraseña</h1>
                <p class="subtitle">Sistema de Gestión Integral de Guardias y Asistencias</p>
            </div>

            {#if !showResult}
                <!-- Formulario de recuperación -->
                <form on:submit={handleSubmit} class="form">
                    <div class="form-group">
                        <label for="cuil">CUIL</label>
                        <input
                            type="text"
                            id="cuil"
                            bind:value={cuil}
                            on:input={handleCuilInput}
                            placeholder="XX-XXXXXXXX-X"
                            maxlength="13"
                            disabled={isLoading}
                            required
                        />
                    </div>

                    {#if errorMessage}
                        <div class="error-message">
                            {errorMessage}
                        </div>
                    {/if}

                    <div class="form-actions">
                        <button 
                            type="submit" 
                            class="submit-btn"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Procesando...' : 'Recuperar Contraseña'}
                        </button>
                        
                        <button 
                            type="button" 
                            class="back-btn"
                            on:click={goToLogin}
                            disabled={isLoading}
                        >
                            Volver al Login
                        </button>
                    </div>
                </form>
            {:else}
                <!-- Resultado exitoso -->
                <div class="success-content">
                    <div class="success-icon">
                        ✓
                    </div>
                    <h2>Solicitud Procesada</h2>
                    <div class="success-message">
                        <p>{successMessage}</p>
                        {#if maskedEmail !== '***@***.***'}
                            <p class="email-info">
                                Se ha enviado un correo a: <strong>{maskedEmail}</strong>
                            </p>
                        {/if}
                    </div>
                    
                    <div class="instructions">
                        <h3>Instrucciones:</h3>
                        <ul>
                            <li>Revisa tu bandeja de entrada (y carpeta de spam)</li>
                            <li>Tu nueva contraseña temporal será tu número de DNI</li>
                            <li>Por seguridad, deberás cambiarla en el primer inicio de sesión</li>
                        </ul>
                    </div>

                    <button 
                        type="button" 
                        class="back-btn"
                        on:click={goToLogin}
                    >
                        Ir al inicio de sesión>
                    </button>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .login-container {
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .login-card {
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        width: 100%;
        max-width: 480px;
        animation: slideUp 0.6s ease-out;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .header {
        background: linear-gradient(135deg, #e79043, #d17a2e);
        padding: 30px 20px;
        text-align: center;
    }

    .logos {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        flex-wrap: wrap;
    }

    .logo {
        height: 50px;
        width: auto;
        filter: brightness(0) invert(1);
        transition: transform 0.3s ease;
    }

    .logo:hover {
        transform: scale(1.1);
    }

    .content {
        padding: 40px 30px;
    }

    .title-section {
        text-align: center;
        margin-bottom: 35px;
    }

    .title-section h1 {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 10px 0;
    }

    .subtitle {
        color: #7f8c8d;
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.4;
    }

    .form {
        display: flex;
        flex-direction: column;
        gap: 25px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
    }

    .form-group label {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 0.95rem;
    }

    .form-group input {
        padding: 15px;
        border: 2px solid #ecf0f1;
        border-radius: 10px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f8f9fa;
    }

    .form-group input:focus {
        outline: none;
        border-color: #e79043;
        background: white;
        box-shadow: 0 0 0 3px rgba(231, 144, 67, 0.1);
    }

    .form-group input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .error-message {
        background: #fee;
        color: #c33;
        padding: 12px 15px;
        border-radius: 8px;
        border: 1px solid #fcc;
        font-size: 0.9rem;
        text-align: center;
    }

    .form-actions {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .submit-btn {
        background: linear-gradient(135deg, #e79043, #d17a2e);
        color: white;
        border: none;
        padding: 15px 25px;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .submit-btn:hover:not(:disabled) {
        background: linear-gradient(135deg, #d17a2e, #b8661e);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(231, 144, 67, 0.3);
    }

    .submit-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
        transform: none;
    }

    .back-btn {
        background: transparent;
        color: #7f8c8d;
        border: 2px solid #ecf0f1;
        padding: 12px 25px;
        border-radius: 10px;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .back-btn:hover:not(:disabled) {
        color: #2c3e50;
        border-color: #bdc3c7;
        background: #f8f9fa;
    }

    .back-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .success-content {
        text-align: center;
    }

    .success-icon {
        width: 80px;
        height: 80px;
        background: #27ae60;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0 auto 25px auto;
        animation: bounce 0.6s ease-out;
    }

    @keyframes bounce {
        0%, 20%, 53%, 80%, 100% {
            transform: translate3d(0, 0, 0);
        }
        40%, 43% {
            transform: translate3d(0, -10px, 0);
        }
        70% {
            transform: translate3d(0, -5px, 0);
        }
        90% {
            transform: translate3d(0, -2px, 0);
        }
    }

    .success-content h2 {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 20px 0;
    }

    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        margin-bottom: 25px;
    }

    .success-message p {
        margin: 0 0 10px 0;
        line-height: 1.5;
    }

    .success-message p:last-child {
        margin-bottom: 0;
    }

    .email-info {
        font-weight: 600;
    }

    .instructions {
        text-align: left;
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
    }

    .instructions h3 {
        color: #2c3e50;
        font-size: 1.1rem;
        margin: 0 0 15px 0;
    }

    .instructions ul {
        margin: 0;
        padding-left: 20px;
        color: #5a6c7d;
    }

    .instructions li {
        margin-bottom: 8px;
        line-height: 1.4;
    }

    .footer {
        background: #f8f9fa;
        padding: 20px;
        text-align: center;
        border-top: 1px solid #ecf0f1;
    }

    .footer p {
        color: #7f8c8d;
        font-size: 0.85rem;
        margin: 0;
    }

    /* Responsive */
    @media (max-width: 600px) {
        .login-container {
            padding: 10px;
        }

        .content {
            padding: 30px 20px;
        }

        .title-section h1 {
            font-size: 1.7rem;
        }

        .logos {
            gap: 10px;
        }

        .logo {
            height: 40px;
        }

        .form-actions {
            gap: 12px;
        }
    }
</style>
