<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import AuthService, {
        isAuthenticated as authStore,
        user as userStore,
    } from "../../lib/login/authService.js";
    let isLoading = true;
    let errorMessage = "";
    export let isActive = false;

    $: currentUser = $userStore;
    $: isAuth = $authStore;
    $: currentPath = $page.url.pathname;

    // función para obtener el rol principal del usuario
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

{#if errorMessage}
    <div class="error-message">{errorMessage}</div>
{:else}
    <div class={"sidebar-container " + (isActive ? "active" : "")}>
        <button
            class="sidebar-tab"
            on:click={toggleMenu}
            class:active={isActive}
            type="button"
            aria-label="Alternar menú"
            aria-expanded={isActive}
        >
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
                    <a
                        href="/inicio"
                        class="menu-item"
                        class:active={currentPath === "/inicio"}
                        on:click={closeMenu}
                    >
                        <span class="menu-item-icon">🏠</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Inicio</div>
                        </div>
                    </a>
                    <a
                        href="/notificar-incidencia"
                        class="menu-item menu-item-highlight"
                        class:active={currentPath === "/notificar-incidencia"}
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
                        class:active={currentPath === "/organigrama"}
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
                        class:active={currentPath === "/asistencia"}
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
                            class:active={currentPath === "/novedades"}
                            on:click={closeMenu}
                        >
                            <span class="menu-item-icon">🏥</span>
                            <div class="menu-item-text">
                                <div class="menu-item-title">
                                    Licencias
                                </div>
                            </div>
                        </a>
                    {/if}

                    <a
                        href="/guardias"
                        class="menu-item"
                        class:active={currentPath === "/guardias"}
                        on:click={closeMenu}
                    >
                        <span class="menu-item-icon">🛡️</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Guardias</div>
                        </div>
                    </a>

                    <a
                        href="/reportes"
                        class="menu-item"
                        class:active={currentPath === "/reportes"}
                        on:click={closeMenu}
                    >
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
                            class:active={currentPath ===
                                "/paneladmin/auditoria"}
                            on:click={closeMenu}
                        >
                            <span class="menu-item-icon">🔍</span>
                            <div class="menu-item-text">
                                <div class="menu-item-title">Auditoría</div>
                            </div>
                        </a>

                        <a
                            href="/paneladmin/compensaciones"
                            class="menu-item"
                            class:active={currentPath.includes("/compensaciones")}
                            on:click={closeMenu}
                        >
                            <span class="menu-item-icon">⏱️</span>
                            <div class="menu-item-text">
                                <div class="menu-item-title">Compensaciones</div>
                            </div>
                        </a>

                        {#if isDirector}
                            <a
                                href="/paneladmin/parametros"
                                class="menu-item"
                                class:active={currentPath ===
                                    "/paneladmin/parametros"}
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
                                class:active={currentPath === "/paneladmin"}
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
                                class:active={currentPath ===
                                    "/paneladmin/organigrama"}
                                on:click={closeMenu}
                            >
                                <span class="menu-item-icon">🏛️</span>
                                <div class="menu-item-text">
                                    <div class="menu-item-title">
                                        Editar Organigrama
                                    </div>
                                </div>
                            </a>

                            <a
                                href="/paneladmin/roles"
                                class="menu-item"
                                class:active={currentPath ===
                                    "/paneladmin/roles"}
                                on:click={closeMenu}
                            >
                                <span class="menu-item-icon">🛡️</span>
                                <div class="menu-item-text">
                                    <div class="menu-item-title">Roles</div>
                                </div>
                            </a>
                        {/if}
                    </div>
                {/if}
            {/if}
            {#if !isAuth}
                <div class="menu-section">
                    <div class="menu-section-title">Acceso</div>
                    <a
                        href="/"
                        class="menu-item"
                        class:active={currentPath === "/"}
                        on:click={closeMenu}
                    >
                        <span class="menu-item-icon">🔐</span>
                        <div class="menu-item-text">
                            <div class="menu-item-title">Iniciar Sesión</div>
                        </div>
                    </a>
                </div>
            {/if}
            <div class="menu-section">
                <div class="menu-section-title">Herramientas</div>
                <a
                    href="/convenio"
                    class="menu-item"
                    class:active={currentPath === "/convenio"}
                    on:click={closeMenu}
                >
                    <span class="menu-item-icon">🧠</span>
                    <div class="menu-item-text">
                        <div class="menu-item-title">Consultar CCT</div>
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
                            goto("/");
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
        font-family: Verdana, Geneva, Tahoma, sans-serif;
    }

    .sidebar-tab {
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(600%);
        background: linear-gradient(
            135deg,
            rgba(64, 123, 255, 0.95) 0%,
            rgba(44, 87, 199, 0.95) 100%
        );
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        color: white;
        padding: 20px 15px;
        border-radius: 0 20px 20px 0;
        cursor: pointer;
        box-shadow:
            4px 0 24px rgba(64, 123, 255, 0.25),
            inset -1px 0 2px rgba(255, 255, 255, 0.3),
            inset 1px 0 2px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-left: none;
        font-family: inherit;
        font-size: inherit;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        z-index: 10000;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .sidebar-tab.active {
        left: 320px;
        opacity: 1;
        visibility: visible;
        margin-left: -55px;
        background: linear-gradient(
            135deg,
            rgba(44, 87, 199, 0.95) 0%,
            rgba(30, 64, 175, 0.95) 100%
        );
        border-radius: 20px 0 0 20px;
        box-shadow:
            -4px 0 24px rgba(64, 123, 255, 0.25),
            inset 1px 0 2px rgba(255, 255, 255, 0.3),
            inset -1px 0 2px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-right: none;
    }

    .sidebar-tab.active:hover {
        background: linear-gradient(
            135deg,
            rgba(30, 64, 175, 0.98) 0%,
            rgba(16, 42, 128, 0.98) 100%
        );
        box-shadow:
            -4px 0 28px rgba(64, 123, 255, 0.35),
            0 0 20px rgba(64, 123, 255, 0.2),
            inset 1px 0 2px rgba(255, 255, 255, 0.4),
            inset -1px 0 2px rgba(0, 0, 0, 0.15);
    }

    .sidebar-container.active .sidebar-tab:not(.active) {
        opacity: 0;
        visibility: hidden;
        left: 0;
        transition: opacity 0.4s;
    }

    .sidebar-tab:hover {
        padding-left: 20px;
        background: linear-gradient(
            135deg,
            rgba(44, 87, 199, 0.98) 0%,
            rgba(30, 58, 138, 0.98) 100%
        );
        box-shadow:
            6px 0 28px rgba(64, 123, 255, 0.3),
            0 0 16px rgba(64, 123, 255, 0.15),
            inset -1px 0 2px rgba(255, 255, 255, 0.4),
            inset 1px 0 2px rgba(0, 0, 0, 0.15);
    }

    .sidebar-tab-icon {
        font-size: 24px;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
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
    }

    .sidebar {
        position: fixed;
        left: -320px;
        width: 320px;
        background: linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.75) 0%,
            rgba(232, 241, 255, 0.7) 100%
        );
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(64, 123, 255, 0.2);
        box-shadow:
            4px 0 32px rgba(64, 123, 255, 0.15),
            inset -1px 0 2px rgba(255, 255, 255, 0.8),
            inset 1px 0 2px rgba(64, 123, 255, 0.1);
        transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        overflow-y: auto;
        top: 0;
        height: 100vh;
        z-index: 9995;
    }

    .sidebar-container.active .sidebar {
        left: 0;
    }

    .sidebar-header {
        background: transparent;
        color: #2c57c7;
        padding: 32px 24px 24px;
        border-bottom: 1px solid rgba(64, 123, 255, 0.12);
    }

    .sidebar-header h2 {
        font-size: 24px;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    .sidebar-header p {
        font-size: 13px;
        font-weight: 600;
        opacity: 0.75;
        letter-spacing: 0.3px;
        color: #407bff;
    }

    .menu-section {
        padding: 24px 0;
        border-bottom: 1px solid rgba(64, 123, 255, 0.1);
    }

    .menu-section-title {
        padding: 0 24px 14px;
        font-size: 11px;
        font-weight: 800;
        color: #2c57c7;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    .menu-item {
        padding: 16px 24px;
        margin: 6px 12px;
        display: flex;
        align-items: center;
        gap: 16px;
        color: #2c57c7;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.4) 0%,
            rgba(255, 255, 255, 0.2) 100%
        );
        border: 1px solid rgba(64, 123, 255, 0.08);
        box-shadow:
            0 2px 8px rgba(64, 123, 255, 0.05),
            inset 0 1px 2px rgba(255, 255, 255, 0.8);
        position: relative;
        overflow: hidden;
    }

    .menu-item::after {
        content: "";
        position: absolute;
        width: 35%;
        height: 2px;
        bottom: 0;
        left: -35%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(64, 123, 255, 0.8),
            transparent
        );
        opacity: 0;
        transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .menu-item:hover {
        background: linear-gradient(
            135deg,
            rgba(232, 241, 255, 0.9) 0%,
            rgba(255, 255, 255, 0.7) 100%
        );
        box-shadow:
            0 4px 16px rgba(64, 123, 255, 0.15),
            0 0 12px rgba(64, 123, 255, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.9),
            inset 0 -1px 2px rgba(64, 123, 255, 0.1);
        transform: translateX(8px) scale(1.02);
        border-color: rgba(64, 123, 255, 0.2);
    }

    .menu-item:hover::after {
        opacity: 1;
        animation: moveLine 2s linear infinite;
    }

    .menu-item.active {
        background: linear-gradient(
            135deg,
            rgba(255, 165, 0, 0.25) 0%,
            rgba(255, 140, 0, 0.2) 100%
        );
        border: 1px solid rgba(255, 165, 0, 0.3);
        color: #b14506;
        box-shadow:
            0 4px 16px rgba(255, 165, 0, 0.2),
            0 0 12px rgba(255, 140, 0, 0.15),
            inset 0 1px 2px rgba(255, 255, 255, 0.9),
            inset 0 -1px 2px rgba(255, 140, 0, 0.2);
        transform: translateX(6px);
        overflow: hidden;
    }

    .menu-item.active::after {
        width: 50%;
        position: absolute;
        background: linear-gradient(
            135deg,
            transparent,
            rgba(255, 140, 0, 0.9),
            transparent
        );
        opacity: 1;
        offset-path: border-box;
        offset-anchor: 100% 70%;
        animation: journey 3s infinite linear;
    }

    .menu-item.active .menu-item-icon {
        filter: drop-shadow(0 2px 6px rgba(255, 140, 0, 0.3));
    }

    .menu-item.active:hover {
        background: linear-gradient(
            135deg,
            rgba(255, 165, 0, 0.35) 0%,
            rgba(255, 140, 0, 0.3) 100%
        );
        box-shadow:
            0 6px 20px rgba(255, 165, 0, 0.3),
            0 0 16px rgba(255, 140, 0, 0.2),
            inset 0 1px 2px rgba(255, 255, 255, 0.95),
            inset 0 -1px 2px rgba(255, 140, 0, 0.25);
        border-color: rgba(255, 165, 0, 0.4);
        transform: translateX(8px) scale(1.02);
    }

    @keyframes moveLine {
        0% {
            left: -35%;
        }
        100% {
            left: 100%;
        }
    }

    @keyframes journey {
        0% {
            offset-distance: 0%;
        }
        100% {
            offset-distance: 100%;
        }
    }

    .menu-item-icon {
        font-size: 22px;
        width: 32px;
        text-align: center;
        flex-shrink: 0;
        filter: drop-shadow(0 2px 4px rgba(64, 123, 255, 0.15));
    }

    .menu-item-text {
        flex: 1;
    }

    .menu-item-title {
        font-weight: 700;
        font-size: 15px;
        letter-spacing: 0.2px;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    .menu-item-highlight {
        background: linear-gradient(
            135deg,
            rgba(255, 240, 240, 0.95) 0%,
            rgba(254, 234, 234, 0.85) 100%
        );
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #dc2626;
        font-weight: 700;
        box-shadow:
            0 4px 12px rgba(239, 68, 68, 0.12),
            inset 0 1px 2px rgba(255, 255, 255, 0.9),
            inset 0 -1px 2px rgba(239, 68, 68, 0.1);
    }

    .menu-item-highlight::after {
        background: linear-gradient(
            90deg,
            transparent,
            rgba(239, 68, 68, 0.8),
            transparent
        );
    }

    .menu-item-highlight:hover {
        background: linear-gradient(
            135deg,
            rgba(254, 234, 234, 0.98) 0%,
            rgba(255, 228, 228, 0.9) 100%
        );
        box-shadow:
            0 6px 16px rgba(239, 68, 68, 0.2),
            0 0 12px rgba(239, 68, 68, 0.1),
            inset 0 1px 2px rgba(255, 255, 255, 0.95),
            inset 0 -1px 2px rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.3);
    }

    .logout-button {
        padding: 16px 24px;
        margin: 6px 12px;
        display: flex;
        align-items: center;
        gap: 16px;
        color: #2c57c7;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.4) 0%,
            rgba(255, 255, 255, 0.2) 100%
        );
        border: 1px solid rgba(64, 123, 255, 0.08);
        box-shadow:
            0 2px 8px rgba(64, 123, 255, 0.05),
            inset 0 1px 2px rgba(255, 255, 255, 0.8);
        width: auto;
        text-align: left;
        font-family: inherit;
        font-size: inherit;
        position: relative;
        overflow: hidden;
    }

    .logout-button::after {
        content: "";
        position: absolute;
        width: 35%;
        height: 2px;
        bottom: 0;
        left: -35%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(239, 68, 68, 0.8),
            transparent
        );
        opacity: 0;
        transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .logout-button:hover {
        background: linear-gradient(
            135deg,
            rgba(255, 241, 241, 0.95) 0%,
            rgba(254, 234, 234, 0.85) 100%
        );
        box-shadow:
            0 4px 16px rgba(239, 68, 68, 0.15),
            0 0 12px rgba(239, 68, 68, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.9),
            inset 0 -1px 2px rgba(239, 68, 68, 0.1);
        transform: translateX(8px) scale(1.02);
        border-color: rgba(239, 68, 68, 0.2);
        color: #dc2626;
    }

    .logout-button:hover::after {
        opacity: 1;
        animation: moveLine 2s linear infinite;
    }

    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(44, 87, 199, 0.25);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        z-index: 9980;
        opacity: 0;
        visibility: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: none;
    }

    .overlay.active {
        opacity: 1;
        visibility: visible;
        pointer-events: auto;
    }

    .sidebar {
        scrollbar-width: none;
        -ms-overflow-style: none;
    }

    .sidebar::-webkit-scrollbar {
        display: none;
        width: 0;
        height: 0;
    }

    .error-message {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(
            135deg,
            rgba(239, 68, 68, 0.98) 0%,
            rgba(220, 38, 38, 0.95) 100%
        );
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        color: white;
        padding: 16px 32px;
        border-radius: 16px;
        font-weight: 600;
        box-shadow:
            0 8px 24px rgba(239, 68, 68, 0.3),
            0 0 16px rgba(239, 68, 68, 0.2),
            inset 0 1px 2px rgba(255, 255, 255, 0.3),
            inset 0 -1px 2px rgba(0, 0, 0, 0.2);
        z-index: 10001;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
