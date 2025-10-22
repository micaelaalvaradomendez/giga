<script>
    import IconifyIcon from "@iconify/svelte";
    let cuil = "";
    let password = "";
    let showPassword = false;
    let errorMessage = "";
    let isLoading = false;

    function togglePassword() {
        showPassword = !showPassword;
    }

    function handleCuilInput(event) {
        let input = event.target.value.replace(/\D/g, "");
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

        if (cuil.length < 11) {
            errorMessage = "El CUIL debe tener el formato correcto";
            return;
        }

        isLoading = true;

        try {
            const response = await fetch("/api/login", {
                //ajustar url con la respectiva del back
                method: "POST",
                headers: { "Content-Type": "application/json" }, //ajustar si es necesario
                body: JSON.stringify({ cuil, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                errorMessage = data.message; // Mostrar el error que viene del backend
            } else {
                window.location.href = "/dashboard";
            }
        } catch (error) {
            errorMessage = "Error de conexión. Intente nuevamente.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="h1">
    <h1>Inicie Sesión</h1>
</div>
<div class="page-container">
    <div class="component-one">
        <h2>Ingrese su CUIL:</h2>
        <input
            type="text"
            id="cuil"
            bind:value={cuil}
            maxlength="13"
            placeholder="XX-XXXXXXXX-X"
            on:input={handleCuilInput}
        />
        <h2>Ingrese su contraseña:</h2>
        <div class="password-container">
            <input
                id="password"
                bind:value={password}
                type={showPassword ? "text" : "password"}
                class="password-input"
                placeholder="•••••••••"
            />
            <button
                type="button"
                class="eye-button"
                on:click={togglePassword}
                aria-label={showPassword
                    ? "Ocultar contraseña"
                    : "Mostrar contraseña"}
            >
                <IconifyIcon icon={showPassword ? "mdi:eye-off" : "mdi:eye"} />
            </button>
        </div>
        <button class="login-button" on:click={handleLogin}>Iniciar</button>
        {#if errorMessage}
            <div class="error-message">{errorMessage}</div>
        {/if}
        <div class="recover-password"><a href>Recuperar contraseña</a></div>
        <!-- Aca podriamos hacer como una notificacion de que revise su correo donde le va a llegar la nueva clave-->
    </div>
</div>

<style>
    .h1 {
        text-align: center;
        font-family: sans-serif;
    }

    .page-container {
        min-height: 40vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .component-one {
        padding: 1rem 2rem;
        width: 40%;
        background: #e79043;
        color: white;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        border-radius: 10px;
        box-shadow: 0 10px 10px rgb(128, 78, 35);
        font-family: sans-serif;
    }

    h2 {
        margin: 0;
        font-size: 1.1rem;
    }

    input {
        padding: 0.7rem;
        border-radius: 5px;
        border: none;
        font-size: 1rem;
        width: 100%;
        box-sizing: border-box;
    }

    .password-container {
        position: relative;
        width: 100%;
    }

    .password-input {
        padding-right: 3rem;
    }

    .eye-button {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.5rem;
        color: #666;
        padding: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.2s;
    }

    .eye-button:hover {
        color: #333;
    }

    .eye-button:focus {
        outline: 2px solid #666;
        outline-offset: 2px;
        border-radius: 4px;
    }

    .login-button {
        width: 100%;
        padding: 0.8rem;
        background: #ffffff;
        color: #e79043;
        border: 2px solid #fff;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 600;
        font-family: sans-serif;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.5px;
    }
    .login-button:hover {
        background: #804e23;
        color: white;
        border-color: #fff;
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    .login-button:active {
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
    }
    .login-button:focus {
        outline: 3px solid rgba(255, 255, 255, 0.5);
        outline-offset: 2px;
    }
    .recover-password {
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    a {
        color: #fff;
        text-decoration: underline;
    }
    .error-message {
        background: #ff4444;
        color: white;
        padding: 0.7rem;
        border-radius: 5px;
        text-align: center;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
