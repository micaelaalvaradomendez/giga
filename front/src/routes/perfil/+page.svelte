<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import AuthService from "../../lib/login/authService.js";
    import EditarPerfil from "../../lib/componentes/EditarPerfil.svelte";
    import CambioContrasenaObligatorio from "../../lib/componentes/CambioContrasenaObligatorio.svelte";
    import CalendarioBase from "../../lib/componentes/calendarioBase.svelte";
    import { guardiasService } from "../../lib/services.js";

    let user = null;
    let isLoading = true;
    let errorMessage = "";
    let showEditProfile = false;
    let showMandatoryPasswordChange = false;
    let guardias = [];
    let loadingGuardias = false;
    let feriados = [];
    let loadingFeriados = false;

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

                // Cargar las guardias del agente y los feriados
                await cargarGuardias();
                await cargarFeriados();
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

    async function cargarGuardias() {
        if (!user || !user.agente_id) return;
        
        try {
            loadingGuardias = true;
            const response = await guardiasService.getGuardiasAgente(user.agente_id);
            guardias = response.data?.guardias || [];
            console.log('Guardias del agente:', guardias);
        } catch (error) {
            console.error('Error cargando guardias:', error);
        } finally {
            loadingGuardias = false;
        }
    }

    async function cargarFeriados() {
        try {
            loadingFeriados = true;
            const response = await guardiasService.getFeriados();
            feriados = response.data?.results || response.data || [];
            console.log('Feriados cargados:', feriados);
        } catch (error) {
            console.error('Error cargando feriados:', error);
            feriados = []; // En caso de error, asegurar que sea un array vacío
        } finally {
            loadingFeriados = false;
        }
    }

    function formatearFecha(fecha) {
        if (!fecha) return '';
        const d = new Date(fecha);
        return d.toLocaleDateString('es-AR', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        });
    }

    function formatearHora(hora) {
        if (!hora) return '';
        return hora.slice(0, 5); // HH:MM
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

    <!-- Sección de Guardias -->
    <div class="guardias-container">
        <h2>Mis Guardias</h2>
        {#if loadingGuardias}
            <div class="loading-guardias">
                <div class="loading-spinner"></div>
                <p>Cargando guardias...</p>
            </div>
        {:else if guardias.length === 0}
            <div class="no-guardias">
                <p>📋 No tenés guardias asignadas actualmente</p>
            </div>
        {:else}
            <div class="guardias-lista">
                {#each guardias as guardia}
                    <div class="guardia-card">
                        <div class="guardia-header">
                            <span class="guardia-tipo tipo-{guardia.tipo}">{guardia.tipo || 'Regular'}</span>
                            <span class="guardia-estado estado-{guardia.estado}">{guardia.estado || 'Planificada'}</span>
                        </div>
                        <div class="guardia-body">
                            <div class="guardia-info">
                                <strong>📅 Fecha:</strong> {formatearFecha(guardia.fecha)}
                            </div>
                            <div class="guardia-info">
                                <strong>🕒 Horario:</strong> {formatearHora(guardia.hora_inicio)} - {formatearHora(guardia.hora_fin)}
                            </div>
                            {#if guardia.observaciones}
                                <div class="guardia-observaciones">
                                    <strong>📝 Observaciones:</strong> {guardia.observaciones}
                                </div>
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <div>
        {#if loadingFeriados}
            <div class="loading">Cargando feriados...</div>
        {:else}
            <CalendarioBase {feriados} />
        {/if}
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

    /* Estilos para la sección de guardias */
    .guardias-container {
        max-width: 1000px;
        margin: 2rem auto;
        padding: 1.5rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .guardias-container h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1.5rem;
        text-align: center;
        border-bottom: 3px solid #e79043;
        padding-bottom: 0.75rem;
    }

    .loading-guardias {
        text-align: center;
        padding: 2rem;
        color: #666;
    }

    .no-guardias {
        text-align: center;
        padding: 3rem 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        color: #666;
    }

    .no-guardias p {
        font-size: 1.1rem;
        margin: 0;
    }

    .guardias-lista {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
    }

    .guardia-card {
        background: #f8f9fa;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .guardia-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    .guardia-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .guardia-tipo,
    .guardia-estado {
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .guardia-tipo {
        background: rgba(255, 255, 255, 0.2);
        color: white;
    }

    .guardia-estado {
        background: rgba(255, 255, 255, 0.9);
        color: #333;
    }

    .estado-planificada {
        background: #fff3cd !important;
        color: #856404 !important;
    }

    .estado-confirmada {
        background: #d1ecf1 !important;
        color: #0c5460 !important;
    }

    .estado-completada {
        background: #d4edda !important;
        color: #155724 !important;
    }

    .tipo-regular {
        background: rgba(59, 130, 246, 0.2) !important;
    }

    .tipo-especial {
        background: rgba(249, 115, 22, 0.2) !important;
    }

    .tipo-feriado {
        background: rgba(220, 38, 38, 0.2) !important;
    }

    .tipo-emergencia {
        background: rgba(239, 68, 68, 0.2) !important;
    }

    .guardia-body {
        padding: 1.25rem;
    }

    .guardia-info {
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        color: #333;
    }

    .guardia-info strong {
        color: #555;
        margin-right: 0.5rem;
    }

    .guardia-observaciones {
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid #dee2e6;
        font-size: 0.9rem;
        color: #666;
        font-style: italic;
    }

    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #e79043;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @media (max-width: 768px) {
        .guardias-lista {
            grid-template-columns: 1fr;
        }
    }
</style>
