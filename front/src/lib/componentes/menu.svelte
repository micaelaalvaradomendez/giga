<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import AuthService, {
        isAuthenticated as authStore,
        user as userStore,
    } from "../../lib/login/authService.js";
    let isLoading = true;
    let errorMessage = "";
    export let isActive = false;

    $: currentUser = $userStore;
    $: isAuth = $authStore;

    // Función para obtener el rol principal del usuario
    function getUserRole(user) {
        if (!user || !user.roles || user.roles.length === 0) return null;
        return user.roles[0].nombre;
    }

    $: userRole = getUserRole(currentUser);
    $: isAdmin = userRole === "Administrador";
    $: isDirector = userRole === "Director" || isAdmin;
    $: isJefatura = userRole === "Jefatura" || isDirector;
    $: isAgenteAvanzado = userRole === "Agente Avanzado" || isJefatura;

    export function toggleMenu() {
        isActive = !isActive;
    }

    export function closeMenu() {
        isActive = false;
    }

    onMount(async () => {
        try {
            const sessionCheck = await AuthService.checkSession();
            console.log("Session check result:", sessionCheck);

            if (!sessionCheck.authenticated) {
                console.log("Usuario NO autenticado");
                const currentPath = window.location.pathname;
                if (currentPath !== "/" && currentPath !== "/convenio") {
                    goto("/");
                    return;
                }
            } else {
                console.log("Usuario autenticado:", sessionCheck.user);
            }
        } catch (error) {
            console.error("Error verificando sesión:", error);
            errorMessage = "Error verificando la sesión";
        } finally {
            isLoading = false;
        }
    });

    function getRoleBadgeClass(user) {
        const role = getUserRole(user);
        const roleClasses = {
            Administrador: "role-admin",
            Director: "role-director",
            Jefatura: "role-jefatura",
            "Agente Avanzado": "role-agente-avanzado",
            Agente: "role-agente",
        };
        return roleClasses[role] || "role-default";
    }
</script>

{#if isLoading}
    <div class="loading-spinner">Cargando...</div>
{:else if errorMessage}
    <div class="error-message">{errorMessage}</div>
{:else}
    <div class={"sidebar-container " + (isActive ? "active" : "")}>
        <button class="sidebar-tab" on:click={toggleMenu} class:active={isActive} 
                type="button" aria-label="Alternar menú" 
                aria-expanded={isActive}>
            <div class="sidebar-tab-icon">☰</div>
        </button>
        {#if currentUser}
            <div class={getRoleBadgeClass(currentUser)}></div>
        {/if}
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Menú Principal</h2>
                <p>Sistema GIGA</p>
            </div>

            {#if isAuth && currentUser}
                <div class="menu-section">
                    <div class="menu-section-title">Principal</div>
                    <a href="/inicio" class="menu-item" on:click={closeMenu}>
                        <span class="menu-item-icon">🏠</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Inicio</div>
                        </div>
                    </a>
                    <a href="/perfil" class="menu-item" on:click={closeMenu}>
                        <span class="menu-item-icon">👤</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Mi Perfil</div>
                        </div>
                    </a>
                    <a
                        href="/notificar-incidencia"
                        class="menu-item menu-item-highlight"
                        on:click={closeMenu}
                    >
                        <span class="menu-item-icon">📧</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">
                                Notificar Incidencia
                            </div>
                        </div>
                    </a>
                    <a
                        href="/organigrama"
                        class="menu-item"
                        on:click={closeMenu}
                    >
                        <span class="menu-item-icon">🏛️</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Organigrama</div>
                        </div>
                    </a>
                </div>

                <div class="menu-section">
                    <div class="menu-section-title">Operaciones</div>
                    <a
                        href="/asistencia"
                        class="menu-item"
                        on:click={closeMenu}
                    >
                        <span class="menu-item-icon">📋</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Asistencia</div>
                        </div>
                    </a>

                    {#if isAgenteAvanzado}
                        <a
                            href="/novedades"
                            class="menu-item"
                            on:click={closeMenu}
                        >
                            <span class="menu-item-icon">🏥</span>
                            <div class="menu-item-text">
                                <div class="menu-item-title">
                                    Licencias y Novedades
                                </div>
                            </div>
                        </a>
                    {/if}

                    <a href="/guardias" class="menu-item" on:click={closeMenu}>
                        <span class="menu-item-icon">🛡️</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Guardias</div>
                        </div>
                    </a>

                    <a href="/reportes" class="menu-item" on:click={closeMenu}>
                        <span class="menu-item-icon">📊</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Reportes</div>
                        </div>
                    </a>

                    
                </div>

                {#if isJefatura}
                    <div class="menu-section">
                        <div class="menu-section-title">
                            Administración y Control
                        </div>

                        <a
                            href="/paneladmin/auditoria"
                            class="menu-item"
                            on:click={closeMenu}
                        >
                            <span class="menu-item-icon">🔍</span>
                            <div class="menu-item-text">
                                <div class="menu-item-title">Auditoría</div>
                            </div>
                        </a>

                        {#if isDirector}
                            <a
                                href="/paneladmin/parametros"
                                class="menu-item"
                                on:click={closeMenu}
                            >
                                <span class="menu-item-icon">⏱️</span>
                                <div class="menu-item-text">
                                    <div class="menu-item-title">
                                        Parámetros
                                    </div>
                                </div>
                            </a>
                        {/if}

                        {#if isAdmin}
                            <a
                                href="/paneladmin"
                                class="menu-item"
                                on:click={closeMenu}
                            >
                                <span class="menu-item-icon">👥</span>
                                <div class="menu-item-text">
                                    <div class="menu-item-title">
                                        Panel Administrativo
                                    </div>
                                </div>
                            </a>
                            <a
                                href="/paneladmin/organigrama"
                                class="menu-item"
                                on:click={closeMenu}
                            >
                                <span class="menu-item-icon">🏛️</span>
                                <div class="menu-item-text">
                                    <div class="menu-item-title">Editar Organigrama</div>
                                </div>
                            </a>
                            
                            <a
                                href="/paneladmin/roles"
                                class="menu-item"
                                on:click={closeMenu}
                            >
                                <span class="menu-item-icon">🛡️</span>
                                <div class="menu-item-text">
                                    <div class="menu-item-title">
                                        Roles
                                    </div>
                                </div>
                            </a>
                        {/if}
                    </div>
                {/if}
            {/if}
            {#if !isAuth}
                <div class="menu-section">
                    <div class="menu-section-title">Acceso</div>
                    <a href="/" class="menu-item" on:click={closeMenu}>
                        <span class="menu-item-icon">🔐</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Iniciar Sesión</div>
                        </div>
                    </a>
                </div>
            {/if}
            <div class="menu-section">
                <div class="menu-section-title">Herramientas</div>
                <a href="/convenio" class="menu-item" on:click={closeMenu}>
                    <span class="menu-item-icon">🧠</span>
                    <div class="menu-item-text">
                        <div class="menu-item-title">Consultar Convenio</div>
                    </div>
                </a>
            </div>

            {#if isAuth}
                <div class="menu-section">
                    <div class="menu-section-title">Sesión</div>
                    <button 
                        class="menu-item logout-button" 
                        on:click={async () => {
                            await AuthService.logout();
                            closeMenu();
                            goto('/');
                        }}
                    >
                        <span class="menu-item-icon">🚪</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Cerrar Sesión</div>
                        </div>
                    </button>
                </div>
            {/if}
        </div>
    </div>
{/if}

{#if isActive}
    <div
        class="overlay"
        class:active={isActive}
        on:click={closeMenu}
        on:keydown={(e) => e.key === "Enter" && closeMenu()}
        role="button"
        tabindex="0"
    ></div>
{/if}

<style>
    .sidebar-container {
        position: fixed;
        left: 0;
        top: 0;
        z-index: 9990;
    }

    .sidebar-tab {
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(600%);
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        padding: 20px 15px;
        border-radius: 0 15px 15px 0;
        cursor: pointer;
        box-shadow: 3px 0 15px rgba(0, 0, 0, 0.2);
        transition:
            all 0.4s ease,
            visibility 0s linear 0.3s,
            opacity 0.3s;
        border: none;
        font-family: inherit;
        font-size: inherit;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        z-index: 10000;
    }

    .sidebar-tab.active {
        left: 320px;
        opacity: 1;
        visibility: visible;
        margin-left: -55px;
        background: #1e40af;
        border-radius: 15px 0 0 15px;
        box-shadow: -3px 0 15px rgba(0, 0, 0, 0.2);
    }

    .sidebar-tab.active:hover {
        background: #102a80;
    }

    .sidebar-container.active .sidebar-tab:not(.active) {
        opacity: 0;
        visibility: hidden;
        left: 0;
        transition: opacity 0.4s;
    }

    .sidebar-tab:hover {
        padding-left: 20px;
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
    }

    .sidebar-tab-icon {
        font-size: 24px;
        transition: transform 0.3s ease;
    }

    .sidebar-container:hover .sidebar-tab-icon,
    .sidebar-container.active .sidebar-tab-icon {
        transform: translateX(5px);
    }

    .sidebar-tab-text {
        writing-mode: vertical-rl;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 1px;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
    }

    .sidebar {
        position: fixed;
        left: -320px;
        width: 320px;
        background: white;
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.15);
        transition: left 0.4s ease;
        overflow-y: auto;
        top: 0;
        height: 100vh;
        z-index: 9995;
        font-family: Verdana, Geneva, Tahoma, sans-serif;
    }

    .sidebar-container.active .sidebar {
        left: 0;
    }

    .sidebar-header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        padding: 25px 20px;
    }

    .sidebar-header h2 {
        font-size: 22px;
        margin-bottom: 5px;
    }

    .sidebar-header p {
        font-size: 13px;
        opacity: 0.9;
    }

    .menu-section {
        padding: 20px 0;
        border-bottom: 1px solid #e5e5e5;
    }

    .menu-section-title {
        padding: 0 20px 12px;
        font-size: 11px;
        font-weight: 700;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .menu-item {
        padding: 14px 20px;
        display: flex;
        align-items: center;
        gap: 15px;
        color: #333;
        text-decoration: none;
        transition: all 0.2s;
        cursor: pointer;
        border-left: 3px solid transparent;
    }

    .menu-item:hover {
        background: #f0f7ff;
        border-left-color: #2563eb;
    }

    .menu-item-icon {
        font-size: 22px;
        width: 28px;
        text-align: center;
        flex-shrink: 0;
    }

    .menu-item-text {
        flex: 1;
    }

    .menu-item-title {
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 2px;
    }

    .menu-item-highlight {
        background: #fff8f8;
        border-left: 3px solid #ef4444;
        color: #ef4444;
        font-weight: 600;
    }
    .menu-item-highlight:hover {
        background: #feeaea;
        border-left-color: #dc2626;
    }

    .logout-button {
        background: none;
        border: none;
        width: 100%;
        text-align: left;
    }

    .logout-button:hover {
        background: #fff1f1;
        border-left-color: #ef4444;
        color: #dc2626;
    }

    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 9980;
        opacity: 0;
        visibility: hidden;
        transition:
            opacity 0.4s ease,
            visibility 0.4s ease;
        pointer-events: none;
    }

    .overlay.active {
        opacity: 1;
        visibility: visible;
        pointer-events: auto;
    }

    .sidebar::-webkit-scrollbar {
        width: 6px;
    }

    .sidebar::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .sidebar::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
    }

    .sidebar::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    .loading-spinner {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #2563eb;
        font-size: 18px;
    }

    .error-message {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ef4444;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 10001;
    }
</style>
