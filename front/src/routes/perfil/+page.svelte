<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import AuthService from "../../lib/login/authService.js";
    import EditarPerfil from "../../lib/componentes/EditarPerfil.svelte";
    import CambioContrasenaObligatorio from "../../lib/componentes/CambioContrasenaObligatorio.svelte";
    import CalendarioBase from "../../lib/componentes/calendarioBase.svelte";

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
            "Administrador": "role-admin",
            "Director": "role-director",
            "Jefatura": "role-jefatura",
            "Agente Avanzado": "role-agente-avanzado",
            "Agente": "role-agente",
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
    <div class="profile-container">
        <div class="profile-header">
            <h1>Perfil de Usuario</h1>
        </div>
        <div class="profile-details">
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
                <span class="value">{AuthService.formatCuil(user.cuil)}</span>
            </div>
            {#if user.roles && user.roles.length > 0}
                <div class="detail-item">
                    <span class="label">Rol principal:</span>
                    <span
                        class="role-badge {getRoleBadgeClass(user.roles[0].nombre)}"
                    >
                        {user.roles[0].nombre}
                    </span>
                </div>
                {#if user.roles.length > 1}
                    <div class="detail-item">
                        <span class="label">Otros roles:</span>
                        <div class="roles-list">
                            {#each user.roles.slice(1) as role}
                                <span class="role-badge {getRoleBadgeClass(role.nombre)}"
                                    >{role.nombre}</span
                                >
                            {/each}
                        </div>
                    </div>
                {/if}
            {/if}
        </div>
        <div class="actions">
            <button class="edit-profile-button" on:click={openEditProfile}>
                Editar Perfil
            </button>
            <button class="logout-button" on:click={handleLogout}>
                Cerrar Sesión
            </button>
        </div>
    </div>
    <div>
        <CalendarioBase />
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
    .profile-container {
        max-width: 1000px;
        margin: 1.5rem auto;
        padding: 1.5rem;
        background: #e79043;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        font-family: sans-serif;
    }
    .profile-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .profile-details {
        display: grid;
        gap: 1rem;
    }
    .detail-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .label {
        font-weight: 600;
        min-width: 150px;
        color: #555;
    }
    .value {
        font-weight: 500;
        color: #333;
    }
    .actions {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
        justify-content: center;
    }
    .edit-profile-button,
    .logout-button {
        padding: 0.7rem 1.3rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .edit-profile-button {
        background-color: #2c5282;
        color: white;
        border: 2px solid #1a365d;
    }
    .edit-profile-button:hover {
        background-color: #1a365d;
        border-color: #0f2137;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .logout-button {
        background-color: #c53030;
        color: white;
        border: 2px solid #9b2c2c;
    }
    .logout-button:hover {
        background-color: #9b2c2c;
        border-color: #742a2a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .role-badge {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: white;
    }
    .role-admin {
        background: #d32f2f;
    }
    .role-director {
        background: #7b1fa2;
    }
    .role-jefatura {
        background: #303f9f;
    }
    .role-agente-avanzado {
        background: #388e3c;
    }
    .role-agente {
        background: #1976d2;
    }
    .role-default {
        background: #616161;
    }
    .roles-list {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .loading-container,
    .error-container {
        text-align: center;
        padding: 2rem;
    }
</style>
