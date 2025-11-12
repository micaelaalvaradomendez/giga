<script>
    import AuthService from "../lib/login/authService.js";

    let cuil = "";
    let password = "";
    let showPassword = false;
    let errorMessage = "";
    let isLoading = false;

    function togglePassword() {
        showPassword = !showPassword;
    }

    function handleCuilInput(event) {
        let input = (event.target.value || "").replace(/\D/g, "");
        if (input.length > 11) {
            input = input.slice(0, 11);
        }
        let formattedCuil = "";
        if (input.length > 2) {
            formattedCuil += input.slice(0, 2) + "-";
            if (input.length > 10) {
                formattedCuil += input.slice(2, 10) + "-";
                formattedCuil += input.slice(10);
            } else if (input.length > 2) {
                formattedCuil += input.slice(2);
            }
        } else {
            formattedCuil = input;
        }
        cuil = formattedCuil;
        try {
            event.target.value = formattedCuil;
        } catch (e) {}
    }

    async function handleLogin() {
        errorMessage = "";

        if (!cuil.trim()) {
            errorMessage = "Por favor ingrese su CUIL";
            return;
        }

        if (!password.trim()) {
            errorMessage = "Por favor ingrese su contraseña";
            return;
        }

        if (cuil.replace(/\D/g, "").length < 11) {
            errorMessage = "El CUIL debe tener al menos 11 dígitos";
            return;
        }

        isLoading = true;

        try {
            const result = await AuthService.login(cuil, password);

            if (result.success) {
                // Guardar información de cambio de contraseña en localStorage si es necesario
                if (result.requires_password_change) {
                    localStorage.setItem("requires_password_change", "true");
                    localStorage.setItem(
                        "password_reset_reason",
                        result.password_reset_reason ||
                            "Debe cambiar su contraseña por seguridad",
                    );
                } else {
                    localStorage.setItem("requires_password_change", "false");
                }

                // Login exitoso - redirigir siempre a inicio
                window.location.href = "/inicio";
            } else {
                errorMessage = result.message || "Error en el login";
            }
        } catch (error) {
            console.error("Error durante el login:", error);
            errorMessage = "Error de conexión. Intente nuevamente.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="page-wrap">
    <div class="card-wrapper">
        <div class="container">
            <div class="textB">Bienvenido</div>
            <form class="form" on:submit|preventDefault={handleLogin}>
                <input
                    id="cuil"
                    type="tel"
                    class="input"
                    placeholder="CUIL"
                    value={cuil}
                    maxlength="13"
                    inputmode="numeric"
                    pattern="\d*"
                    on:input={(e) => handleCuilInput(e)}
                    disabled={isLoading}
                />
                <div class="input-wrapper">
                    <input
                        id="contrasenia"
                        placeholder="Contraseña"
                        class="input"
                        value={password}
                        on:input={(e) => (password = e.target.value)}
                        type={showPassword ? "text" : "password"}
                        autocomplete="current-password"
                        disabled={isLoading}
                    />
                    <button
                        type="button"
                        class="eye-button"
                        on:click={togglePassword}
                        aria-label={showPassword
                            ? "Ocultar contraseña"
                            : "Mostrar contraseña"}
                    >
                        {#if showPassword}
                            <svg
                                class="eye-slash"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 640 512"
                                height="18"
                                width="18"
                                ><path
                                    d="M38.8 5.1C28.4-3.1 13.3-1.2 5.1 9.2S-1.2 34.7 9.2 42.9l592 464c10.4 8.2 25.5 6.3 33.7-4.1s6.3-25.5-4.1-33.7L525.6 386.7c39.6-40.6 66.4-86.1 79.9-118.4c3.3-7.9 3.3-16.7 0-24.6c-14.9-35.7-46.2-87.7-93-131.1C465.5 68.8 400.8 32 320 32c-68.2 0-125 26.3-169.3 60.8L38.8 5.1zM223.1 149.5C248.6 126.2 282.7 112 320 112c79.5 0 144 64.5 144 144c0 24.9-6.3 48.3-17.4 68.7L408 294.5c8.4-19.3 10.6-41.4 4.8-63.3c-11.1-41.5-47.8-69.4-88.6-71.1c-5.8-.2-9.2 6.1-7.4 11.7c2.1 6.4 3.3 13.2 3.3 20.3c0 10.2-2.4 19.8-6.6 28.3l-90.3-70.8zM373 389.9c-16.4 6.5-34.3 10.1-53 10.1c-79.5 0-144-64.5-144-144c0-6.9 .5-13.6 1.4-20.2L83.1 161.5C60.3 191.2 44 220.8 34.5 243.7c-3.3 7.9-3.3 16.7 0 24.6c14.9 35.7 46.2 87.7 93 131.1C174.5 443.2 239.2 480 320 480c47.8 0 89.9-12.9 126.2-32.5L373 389.9z"
                                /></svg
                            >
                        {:else}
                            <svg
                                class="eye"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 576 512"
                                height="18"
                                width="18"
                                ><path
                                    d="M288 32c-80.8 0-145.5 36.8-192.6 80.6C48.6 156 17.3 208 2.5 243.7c-3.3 7.9-3.3 16.7 0 24.6C17.3 304 48.6 356 95.4 399.4C142.5 443.2 207.2 480 288 480s145.5-36.8 192.6-80.6c46.8-43.5 78.1-95.4 93-131.1c3.3-7.9 3.3-16.7 0-24.6c-14.9-35.7-46.2-87.7-93-131.1C433.5 68.8 368.8 32 288 32zM144 256a144 144 0 1 1 288 0 144 144 0 1 1 -288 0zm144-64c0 35.3-28.7 64-64 64c-7.1 0-13.9-1.2-20.3-3.3c-5.5-1.8-11.9 1.6-11.7 7.4c.3 6.9 1.3 13.8 3.2 20.7c13.7 51.2 66.4 81.6 117.6 67.9s81.6-66.4 67.9-117.6c-11.1-41.5-47.8-69.4-88.6-71.1c-5.8-.2-9.2 6.1-7.4 11.7c2.1 6.4 3.3 13.2 3.3 20.3z"
                                /></svg
                            >
                        {/if}
                    </button>
                </div>
                <button
                    value="Iniciar Sesión"
                    type="submit"
                    class="animated-button"
                    disabled={isLoading}
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="arr-2"
                        viewBox="0 0 24 24"
                    >
                        <path
                            d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
                        ></path>
                    </svg>
                    <span class="text">
                        {#if isLoading}
                            Iniciando...
                        {:else}
                            Iniciar Sesión
                        {/if}
                    </span>
                    <span class="circle"></span>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="arr-1"
                        viewBox="0 0 24 24"
                    >
                        <path
                            d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
                        ></path>
                    </svg>
                </button>
                {#if errorMessage}
                    <div class="error-message">{errorMessage}</div>
                {/if}
                <div class="recover-password">
                    <a href="/contrasena">Recuperar contraseña</a>
                </div>
            </form>
        </div>
    </div>
</div>

<style>
    .page-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 100px;
    }

    .card-wrapper {
        background-image: linear-gradient(163deg, #8eb6e4 0%, #3d97ff 90%);
        border-radius: 20px;
        transition: all 0.3s;
        padding: 0;
    }

    .card-wrapper:hover {
        box-shadow: 0px 0px 30px 1px rgba(55, 101, 138, 0.3);
    }

    .container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
            sans-serif;
        max-width: 450px;
        background: linear-gradient(
            0deg,
            rgb(255, 255, 255) 0%,
            rgb(255, 255, 255) 80%
        );
        border-radius: 22px;
        padding: 25px 35px;
        transition: all 0.2s;
        margin: 3px;
    }

    .container:hover {
        transform: scale(0.98);
        border-radius: 15px;
    }

    .textB {
        text-align: center;
        font-weight: 700;
        font-size: 40px;
        color: rgb(16, 137, 211);
    }

    .form {
        margin-top: 20px;
    }

    .form .input {
        font-size: 18px;
        width: 85%;
        background: white;
        border: 2px solid #a2b8e7;
        padding: 15px 20px;
        border-radius: 20px;
        margin-top: 15px;
        box-shadow: #cff0ff 0px 10px 10px -5px;
    }

    .form .input::placeholder {
        color: rgb(170, 170, 170);
    }
    .form .input:focus {
        outline: none;
        border-inline: 2px solid #12b1d1;
    }

    .animated-button {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        padding: 12px 32px;
        font-size: 18px;
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
        margin: 20px auto;
    }

    .animated-button svg {
        position: absolute;
        width: 24px;
        fill: rgb(16, 137, 211);
        z-index: 9;
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .animated-button .arr-1 {
        right: 16px;
    }

    .animated-button .arr-2 {
        left: -25%;
    }

    .animated-button .circle {
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

    .animated-button .text {
        position: relative;
        z-index: 1;
        transform: translateX(-12px);
        transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .animated-button:hover {
        box-shadow: 0 0 0 2px rgb(16, 137, 211);
        color: #212121;
        border-radius: 25px;
    }

    .animated-button:hover .arr-1 {
        right: -25%;
    }

    .animated-button:hover .arr-2 {
        left: 16px;
    }

    .animated-button:hover .text {
        transform: translateX(12px);
    }

    .animated-button:hover svg {
        fill: rgb(16, 137, 211);
    }

    .animated-button:active {
        scale: 0.96;
        box-shadow: 0 0 0 3px rgb(149, 185, 192);
    }

    .animated-button:hover .circle {
        width: 400px;
        height: 400px;
        opacity: 1;
    }

    .animated-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    .animated-button:disabled:hover {
        box-shadow: 0 0 0 2px rgb(16, 137, 211);
        border-radius: 100px;
    }

    .animated-button:disabled:hover .arr-1 {
        right: 16px;
    }

    .animated-button:disabled:hover .arr-2 {
        left: -25%;
    }

    .animated-button:disabled:hover .text {
        transform: translateX(-12px);
    }

    .animated-button:disabled:hover .circle {
        width: 20px;
        height: 20px;
        opacity: 0;
    }

    .form .input:disabled {
        background-color: #f5f5f5;
        color: #888;
        cursor: not-allowed;
    }
    .input-wrapper {
        position: relative;
        width: auto;
        display: block;
    }

    .input-wrapper .input {
        padding-right: 45px;
        width: 76%;
    }

    .eye-button {
        position: absolute;
        right: 10px;
        top: 60%;
        transform: translateY(-50%);
        background: transparent;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        color: #5a6b80;
        transition: color 0.2s;
        width: 24px;
        height: 35px;
    }

    .eye-button:focus {
        outline: none;
    }

    .eye-button:hover {
        color: rgb(16, 137, 211);
    }

    .eye {
        animation: keyframes-fill 0.5s;
        display: inline-block;
    }

    .eye-slash {
        animation: keyframes-fill 0.5s;
        display: inline-block;
    }

    .form .recover-password {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .form .recover-password a {
        font-size: 20px;
        color: #0099ff;
        text-decoration: underline;
    }

    .error-message {
        background: #ff4444;
        color: white;
        padding: 0.7rem;
        border-radius: 20px;
        text-align: center;
        font-size: 15px;
        margin-top: 0.5rem;
    }

    @keyframes keyframes-fill {
        0% {
            transform: scale(0);
            opacity: 0;
        }

        50% {
            transform: scale(1.2);
        }
    }
</style>
