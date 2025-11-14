<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import AuthService from "../../lib/login/authService.js";

    let cuil = "";
    let isLoading = false;
    let successMessage = "";
    let errorMessage = "";
    let showResult = false;
    let maskedEmail = "";

    function formatCuil(value) {
        // Remover todo excepto números
        const numbers = value.replace(/\D/g, "");

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
        successMessage = "";
        errorMessage = "";
        showResult = false;

        // Validar CUIL
        const cleanCuil = cuil.replace(/\D/g, "");
        if (!cleanCuil) {
            errorMessage = "Por favor ingresa tu CUIL";
            return;
        }

        if (cleanCuil.length !== 11) {
            errorMessage = "El CUIL debe tener 11 dígitos";
            return;
        }

        isLoading = true;

        try {
            const result = await AuthService.recoverPassword(cleanCuil);

            if (result.success) {
                successMessage = result.message;
                maskedEmail = result.email || "***@***.***";
                showResult = true;

                // Limpiar el formulario
                cuil = "";
            } else {
                errorMessage =
                    result.message || "Error al procesar la solicitud";
            }
        } catch (error) {
            console.error("Error:", error);
            errorMessage = "Error de conexión. Intenta nuevamente.";
        } finally {
            isLoading = false;
        }
    }

    function goToLogin() {
        goto("/");
    }
</script>

<svelte:head>
    <title>Recuperar contraseña - Sistema GIGA</title>
</svelte:head>

<div class="login-container">
    <div class="login-card">
        <div class="content">
            <div class="title-section">
                Recuperar Contraseña
                <p class="subtitle">
                    Sistema de Gestión Integral de Guardias y Asistencias
                </p>
            </div>

            {#if !showResult}
                <div class="form">
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
                        />
                    </div>

                    {#if errorMessage}
                        <div class="error-message">
                            {errorMessage}
                        </div>
                    {/if}

                    <div class="form-actions">
                        <button
                            type="button"
                            class="submit-btn"
                            on:click={handleSubmit}
                            disabled={isLoading}
                        >
                            <span class="text">
                                {isLoading
                                    ? "Procesando..."
                                    : "Recuperar Contraseña"}
                            </span>
                        </button>

                        <button
                            type="button"
                            class="back-btn"
                            on:click={goToLogin}
                            disabled={isLoading}
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="arr-2"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    d="M7.82843 10.9999L13.1924 5.63589L11.7782 4.22168L4 11.9999L11.7782 19.778L13.1924 18.3638L7.82843 12.9999H20V10.9999H7.82843Z"
                                ></path>
                            </svg>
                            <span class="text">
                                {#if isLoading}
                                    ...
                                {:else}
                                    Volver al inicio de sesión
                                {/if}
                            </span>
                            <span class="circle"></span>
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="arr-1"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    d="M7.82843 10.9999L13.1924 5.63589L11.7782 4.22168L4 11.9999L11.7782 19.778L13.1924 18.3638L7.82843 12.9999H20V10.9999H7.82843Z"
                                ></path>
                            </svg>
                        </button>
                    </div>
                </div>
            {:else}
                <div class="success-content">
                    <div class="success-icon">✓</div>
                    <h2>Solicitud Procesada</h2>
                    <div class="success-message">
                        <p>{successMessage}</p>
                        {#if maskedEmail !== "***@***.***"}
                            <p class="email-info">
                                Se ha enviado un correo a: <strong
                                    >{maskedEmail}</strong
                                >
                            </p>
                        {/if}
                    </div>

                    <div class="instructions">
                        <h3>Instrucciones:</h3>
                        <ul>
                            <li>
                                Revisa tu bandeja de entrada (y carpeta de
                                spam).
                            </li>
                            <li>
                                Tu nueva contraseña te llegará al correo
                                registrado en el sistema.
                            </li>
                            <li>
                                Por seguridad, deberás cambiarla en el primer
                                inicio de sesión.
                            </li>
                        </ul>
                    </div>

                    <button type="button" class="back-btn" on:click={goToLogin}>
                        Ir al inicio de sesión
                    </button>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 100px;
    }

    .login-card {
        background-image: linear-gradient(163deg, #8eb6e4 0%, #3d97ff 90%);
        border-radius: 24px;
        transition: all 0.3s;
        padding: 3px;
        box-shadow: 
            0 8px 32px rgba(64, 123, 255, 0.25),
            inset 0 1px 2px rgba(255, 255, 255, 0.3);
    }

    .login-card:hover {
        box-shadow: 
            0 12px 48px rgba(64, 123, 255, 0.35),
            0 0 24px rgba(64, 123, 255, 0.15),
            inset 0 1px 2px rgba(255, 255, 255, 0.4);
    }

    .content {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            sans-serif;
        max-width: 450px;
        background: linear-gradient(
            0deg,
            rgb(255, 255, 255) 0%,
            rgb(255, 255, 255) 80%
        );
        border-radius: 20px;
        padding: 25px 35px;
        transition: all 0.2s;
        margin: 3px;
    }

    .content:hover {
        transform: scale(0.98);
        border-radius: 15px;
    }

    .title-section {
        text-align: center;
        font-weight: 700;
        font-size: 40px;
        color: rgb(16, 137, 211);
    }

    .subtitle {
        font-size: 23px;
        color: rgb(16, 137, 211);
        margin-top: 5px;
    }

    .form {
        margin-top: 20px;
    }

    .form-group {
        font-size: 18px;
        width: 90%;
        background: white;
        border: 2px solid #a2b8e7;
        padding: 15px 20px;
        border-radius: 16px;
        margin-top: 15px;
        box-shadow: 
            0 4px 16px rgba(64, 123, 255, 0.12),
            inset 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    .form-group input {
        width: 100%;
        border: none;
        outline: none;
        font-size: 18px;
    }

    .form-group input::placeholder {
        color: rgb(170, 170, 170);
    }

    .form-group:focus-within {
        border-color: #12b1d1;
    }

    .form-group input:disabled {
        background-color: #f5f5f5;
        color: #888;
        cursor: not-allowed;
    }

    .submit-btn {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 16px 32px;
        margin: 20px 0 10px 0;
        font-weight: 700;
        font-size: 18px;
        color: #ffffff;
        background-color: #2ba8fb;
        border: 2px solid rgb(16, 137, 211);
        border-radius: 100px;
        cursor: pointer;
        transition: all 0.5s;
        margin-bottom: 15px;
    }

    .submit-btn:hover {
        background-color: #55aee9;
        box-shadow: 0 0 20px #6fc5ff75;
        transform: scale(1.05);
    }

    .submit-btn:active {
        background-color: #3d94cf;
        transition: all 0.25s;
        box-shadow: none;
        transform: scale(0.97);
    }

    .submit-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    .back-btn {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        padding: 12px 32px;
        font-size: 16px;
        border: none;
        background-color: white;
        border-radius: 100px;
        font-weight: 600;
        color: rgb(16, 137, 211);
        box-shadow: 0 0 0 2px rgb(16, 137, 211);
        cursor: pointer;
        overflow: hidden;
        transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
        width: 100%;
        margin: 10px 0;
    }

    .back-btn svg {
        position: absolute;
        width: 24px;
        fill: rgb(16, 137, 211);
        z-index: 9;
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .back-btn .arr-1 {
        right: 16px;
    }

    .back-btn .arr-2 {
        left: -25%;
    }

    .back-btn .circle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        background-color: rgba(18, 177, 209, 0.3);
        border-radius: 50%;
        opacity: 0;
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .back-btn .text {
        position: relative;
        z-index: 1;
        transform: translateX(-12px);
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .back-btn:hover {
        border-radius: 25px;
    }

    .back-btn:hover .arr-1 {
        right: -25%;
    }

    .back-btn:hover .arr-2 {
        left: 16px;
    }

    .back-btn:hover .text {
        transform: translateX(12px);
    }

    .back-btn:active {
        scale: 0.96;
    }

    .back-btn:hover .circle {
        width: 600px;
        height: 100px;
        opacity: 1;
    }

    .back-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .back-btn:disabled:hover {
        border-radius: 100px;
    }

    .back-btn:disabled:hover .arr-1 {
        right: 16px;
    }

    .back-btn:disabled:hover .arr-2 {
        left: -25%;
    }

    .back-btn:disabled:hover .text {
        transform: translateX(-12px);
    }

    .back-btn:disabled:hover .circle {
        width: 20px;
        height: 20px;
        opacity: 0;
    }

    .error-message {
        background: #ff4444;
        color: white;
        padding: 14px 18px;
        border-radius: 16px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        margin-top: 15px;
        width: 90%;
        box-shadow: 
            0 4px 16px rgba(255, 68, 68, 0.25),
            inset 0 1px 2px rgba(255, 255, 255, 0.2);
        animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .success-content {
        text-align: center;
        padding: 20px 0;
    }

    .success-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto 20px;
        background: linear-gradient(135deg, #84c5eb, rgb(16, 137, 211));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        color: white;
        font-weight: bold;
    }

    .success-content h2 {
        color: rgb(16, 137, 211);
        margin-bottom: 20px;
    }

    .success-message {
        background: #e8f5ff;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 
            0 4px 16px rgba(64, 123, 255, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.6);
    }

    .success-message p {
        margin: 10px 0;
        color: #333;
    }

    .email-info {
        color: rgb(16, 137, 211);
        font-size: 16px;
    }

    .instructions {
        text-align: left;
        background: #f8f9fa;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 
            0 4px 16px rgba(64, 123, 255, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.6);
    }

    .instructions h3 {
        color: rgb(16, 137, 211);
        margin-bottom: 15px;
    }

    .instructions ul {
        list-style: none;
        padding: 0;
    }

    .instructions li {
        padding: 8px 0;
        padding-left: 25px;
        position: relative;
        color: #555;
    }

    .instructions li::before {
        content: "→";
        position: absolute;
        left: 0;
        color: rgb(16, 137, 211);
        font-weight: bold;
    }

    label {
        display: block;
        margin-bottom: 8px;
        color: rgb(16, 137, 211);
        font-weight: 600;
    }
</style>
