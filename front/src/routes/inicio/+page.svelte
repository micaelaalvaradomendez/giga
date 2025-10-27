<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import AuthService from "../../lib/login/authService.js";
    import EditarPerfil from "../../lib/componentes/EditarPerfil.svelte";
    import CambioContrasenaObligatorio from "../../lib/componentes/CambioContrasenaObligatorio.svelte";

    let user = null;
    let isLoading = true;
    let errorMessage = "";
    let showEditProfile = false;
    let showMandatoryPasswordChange = false;

    onMount(async () => {
        // Verificar si el usuario está autenticado
        try {
            const sessionCheck = await AuthService.checkSession();

            if (sessionCheck.authenticated) {
                user = sessionCheck.user;

                // Verificar si se requiere cambio obligatorio de contraseña
                if (
                    sessionCheck.requires_password_change ||
                    AuthService.requiresPasswordChange()
                ) {
                    showMandatoryPasswordChange = true;
                }
            } else {
                // Si no está autenticado, redirigir al login
                goto("/");
                return;
            }
        } catch (error) {
            console.error("Error verificando sesión:", error);
            errorMessage = "Error verificando la sesión";
            // Redirigir al login en caso de error
            setTimeout(() => goto("/"), 2000);
        } finally {
            isLoading = false;
        }
    });

    async function handleLogout() {
        try {
            await AuthService.logout();
            goto("/");
        } catch (error) {
            console.error("Error durante logout:", error);
            // Aun con error, intentar ir al login
            goto("/");
        }
    }

    function getRoleBadgeClass(rol) {
        const roleClasses = {
            Administrador: "role-admin",
            Director: "role-director",
            Jefatura: "role-jefatura",
            "Agente Avanzado": "role-agente-avanzado",
            Agente: "role-agente",
        };
        return roleClasses[rol] || "role-default";
    }

    function openEditProfile() {
        showEditProfile = true;
    }

    function closeEditProfile() {
        showEditProfile = false;
    }

    function handleUserUpdated(event) {
        // Actualizar la información del usuario en la interfaz
        user = { ...user, ...event.detail };
    }
</script>

{#if isLoading}
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>Verificando sesión...</p>
    </div>
{:else if errorMessage}
    <div class="error-container">
        <h2>Error</h2>
        <p>{errorMessage}</p>
        <p>Redirigiendo al login...</p>
    </div>
{:else if user}
    <div class="welcome-container">
        <header class="welcome-header">
            <div class="user-info">
                <h1>¡Bienvenido/a, {user.first_name}!</h1>
                <div class="user-details">
                    <div class="detail-item">
                        <span class="label">Nombre completo:</span>
                        <span class="value">{user.nombre_completo}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Email:</span>
                        <span class="value">{user.email}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">CUIL:</span>
                        <span class="value"
                            >{AuthService.formatCuil(user.cuil)}</span
                        >
                    </div>
                    <div class="detail-item">
                        <span class="label">Rol principal:</span>
                        <span
                            class="role-badge {getRoleBadgeClass(
                                user.rol_principal,
                            )}"
                        >
                            {user.rol_principal}
                        </span>
                    </div>
                    {#if user.roles && user.roles.length > 1}
                        <div class="detail-item">
                            <span class="label">Otros roles:</span>
                            <div class="roles-list">
                                {#each user.roles.filter((role) => role !== user.rol_principal) as role}
                                    <span
                                        class="role-badge {getRoleBadgeClass(
                                            role,
                                        )}">{role}</span
                                    >
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            </div>

            <div class="actions">
                <button class="edit-profile-button" on:click={openEditProfile}>
                    Editar Perfil
                </button>
                <button class="logout-button" on:click={handleLogout}>
                    Cerrar Sesión
                </button>
            </div>
        </header>

        <main class="dashboard-content">
            <div class="welcome-message">
                <h2>Sesión iniciada correctamente</h2>
                <p>Has ingresado exitosamente al sistema GIGA.</p>
                <div class="session-info">
                    <p>
                        <strong>Fecha de acceso:</strong>
                        {new Date().toLocaleString("es-AR")}
                    </p>
                    <p>
                        <strong>Estado:</strong>
                        <span class="status-active">Activo</span>
                    </p>
                </div>
            </div>

            <div class="quick-actions">
                <h3>Acciones rápidas</h3>
                <div class="actions-grid">
                    <div class="action-card">
                        <h4>Asistencia</h4>
                        <p>Registrar entrada/salida</p>
                        <button class="action-button">Ir a Asistencia</button>
                    </div>
                    <div class="action-card">
                        <h4>Guardias</h4>
                        <p>Consultar guardias asignadas</p>
                        <button class="action-button">Ver Guardias</button>
                    </div>
                    <div class="action-card">
                        <h4>Reportes</h4>
                        <p>Generar reportes del sistema</p>
                        <button class="action-button">Generar Reportes</button>
                    </div>
                    {#if AuthService.hasRole("Administrador")}
                        <a href="/admin">
                            <div class="action-card admin-card">
                                <h4>Administración</h4>
                                <p>Panel de administrador</p>
                                <button class="action-button admin-button">
                                    Panel Admin
                                </button>
                            </div>
                        </a>
                    {/if}
                </div>
            </div>
        </main>
    </div>
{:else}
    <div class="error-container">
        <h2>Error de autenticación</h2>
        <p>No se pudo verificar la sesión.</p>
        <button on:click={() => goto("/")}>Ir al Login</button>
    </div>
{/if}

<!-- Modal de editar perfil -->
<EditarPerfil
    bind:showModal={showEditProfile}
    {user}
    on:close={closeEditProfile}
    on:userUpdated={handleUserUpdated}
/>

<!-- Modal obligatorio de cambio de contraseña -->
<CambioContrasenaObligatorio
    bind:showAlert={showMandatoryPasswordChange}
    {user}
/>

<style>
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 50vh;
        gap: 1rem;
    }

    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #e79043;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    .error-container {
        text-align: center;
        padding: 2rem;
        color: #d32f2f;
    }

    .welcome-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        font-family: sans-serif;
    }

    .welcome-header {
        background: linear-gradient(135deg, #e79043, #d17a2e);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(231, 144, 67, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .user-info h1 {
        margin: 0 0 1rem 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .user-details {
        display: grid;
        gap: 0.8rem;
    }

    .detail-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .label {
        font-weight: 600;
        min-width: 120px;
    }

    .value {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        font-weight: 500;
    }

    .role-badge {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .role-admin {
        background: #d32f2f;
        color: white;
    }

    .role-director {
        background: #7b1fa2;
        color: white;
    }

    .role-jefatura {
        background: #303f9f;
        color: white;
    }

    .role-agente-avanzado {
        background: #388e3c;
        color: white;
    }

    .role-agente {
        background: #1976d2;
        color: white;
    }

    .role-default {
        background: #616161;
        color: white;
    }

    .roles-list {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .actions {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .edit-profile-button {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.5);
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .edit-profile-button:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: white;
    }

    .logout-button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 2px solid white;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .logout-button:hover {
        background: white;
        color: #e79043;
    }

    .dashboard-content {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    .welcome-message {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    .welcome-message h2 {
        color: #e79043;
        margin: 0 0 1rem 0;
        font-size: 1.8rem;
    }

    .session-info {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .status-active {
        color: #4caf50;
        font-weight: 600;
    }

    .quick-actions {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .quick-actions h3 {
        color: #333;
        margin: 0 0 1.5rem 0;
        font-size: 1.5rem;
        text-align: center;
    }

    .actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
    }

    .action-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }

    .action-card:hover {
        border-color: #e79043;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231, 144, 67, 0.2);
    }

    .admin-card {
        background: linear-gradient(135deg, #fff3e0, #ffcc02);
    }

    .action-card h4 {
        color: #333;
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
    }

    .action-card p {
        color: #666;
        margin: 0 0 1rem 0;
        font-size: 0.9rem;
    }

    .action-button {
        background: #e79043;
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }

    .action-button:hover {
        background: #d17a2e;
        transform: translateY(-1px);
    }

    .admin-button {
        background: #d32f2f;
    }

    .admin-button:hover {
        background: #b71c1c;
    }

    @media (max-width: 768px) {
        .welcome-header {
            flex-direction: column;
            text-align: center;
        }

        .user-info h1 {
            font-size: 2rem;
        }

        .session-info {
            flex-direction: column;
            gap: 0.5rem;
        }

        .actions-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
