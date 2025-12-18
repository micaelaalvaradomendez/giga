<script>
    import { onMount, createEventDispatcher } from "svelte";
    import { fly, fade, slide } from "svelte/transition";
    import { notificacionesService } from "$lib/services";
    const dispatch = createEventDispatcher();
    let notificaciones = [];
    let loading = true;
    let isOpen = false;
    let unreadCount = 0;
    let dropdownRef;
    let buttonRef;
    const icons = {
        GUARDIA: "🛡️",
        HORA_EXTRA: "💰",
        INCIDENCIA: "⚠️",
        ASISTENCIA: "✅",
        USUARIO: "👤",
        LICENCIA: "🏖️",
        FERIADO: "📅",
        ORGANIGRAMA: "🏢",
        ROL: "👑",
        LOGIN: "🔐",
        CRONOGRAMA: "🗓️",
        GENERICO: "🔔",
    };
    onMount(async () => {
        await cargarNotificaciones();
        document.addEventListener("click", handleClickOutside);
        return () => {
            document.removeEventListener("click", handleClickOutside);
        };
    });
    function handleClickOutside(event) {
        if (
            isOpen &&
            dropdownRef &&
            !dropdownRef.contains(event.target) &&
            !buttonRef.contains(event.target)
        ) {
            isOpen = false;
        }
    }
    async function cargarNotificaciones() {
        try {
            loading = true;
            const response = await notificacionesService.getNotificaciones();
            let data = response.data?.results || response.data || [];
            notificaciones = data.filter((n) => !n.leida);
        } catch (e) {
            if (e.response && e.response.data) {
            }
            notificaciones = [];
        } finally {
            loading = false;
            actualizarContador();
        }
    }
    function actualizarContador() {
        unreadCount = notificaciones.length;
    }
    async function marcarLeida(id, event) {
        if (event) event.stopPropagation();
        try {
            await notificacionesService.marcarLeida(id);
            notificaciones = notificaciones.filter((n) => n.id !== id);
            actualizarContador();
        } catch (e) {
            notificaciones = notificaciones.filter((n) => n.id !== id);
            actualizarContador();
        }
    }
    async function marcarTodas() {
        try {
            await notificacionesService.marcarTodasLeidas();
            notificaciones = [];
            actualizarContador();
        } catch (e) {
            notificaciones = [];
            actualizarContador();
        }
    }
    function toggleDropdown() {
        isOpen = !isOpen;
    }
    function timeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        if (seconds < 60) return "hace unos segundos";
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `hace ${minutes} m`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `hace ${hours} h`;
        return date.toLocaleDateString();
    }
</script>
<div class="notifications-container">
    <button
        class="bell-btn {unreadCount > 0 ? 'has-notifications' : ''}"
        on:click={toggleDropdown}
        bind:this={buttonRef}
        aria-label="Notificaciones"
    >
        <span class="bell-icon">🔔</span>
        {#if unreadCount > 0}
            <span class="badge" in:fly={{ y: -5, duration: 200 }}
                >{unreadCount}</span
            >
        {/if}
    </button>
    {#if isOpen}
        <div
            class="dropdown-menu"
            bind:this={dropdownRef}
            transition:fly={{ y: 10, duration: 200 }}
        >
            <div class="dropdown-header">
                <h3>Notificaciones</h3>
                {#if unreadCount > 0}
                    <button class="btn-clean" on:click={marcarTodas}>
                        Marcar todas leídas
                    </button>
                {/if}
            </div>
            <div class="dropdown-body">
                {#if loading}
                    <div class="loading-state"><div class="spinner"></div></div>
                {:else if notificaciones.length === 0}
                    <div class="empty-state">
                        <span class="empty-icon">🔕</span>
                        <p>No tienes notificaciones</p>
                    </div>
                {:else}
                    <div class="notif-list">
                        {#each notificaciones as notif (notif.id)}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div
                                class="notif-item {notif.tipo.toLowerCase()} {notif.leida
                                    ? 'read'
                                    : 'unread'}"
                                on:click={() =>
                                    !notif.leida && marcarLeida(notif.id)}
                            >
                                <div class="notif-icon">
                                    {icons[notif.tipo] || icons["GENERICO"]}
                                </div>
                                <div class="notif-content">
                                    <div class="notif-top">
                                        <span class="notif-title"
                                            >{notif.titulo}</span
                                        >
                                        <span class="notif-time"
                                            >{timeAgo(
                                                notif.fecha_creacion,
                                            )}</span
                                        >
                                    </div>
                                    <p class="notif-msg">{notif.mensaje}</p>
                                </div>
                                {#if !notif.leida}
                                    <div class="unread-indicator"></div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>
<style>
    .notifications-container {
        position: relative;
        display: inline-block;
        font-family: "Segoe UI", system-ui, sans-serif;
    }
    .bell-btn {
        background: white;
        border: none;
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        transition: all 0.2s;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    .bell-btn:hover,
    .bell-btn.active {
        background-color: #f8f9fa;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .bell-icon {
        font-size: 1.2rem;
    }
    .badge {
        position: absolute;
        top: -2px;
        right: -2px;
        background-color: #ff4757;
        color: white;
        border-radius: 10px;
        padding: 2px 6px;
        font-size: 0.7rem;
        font-weight: bold;
        border: 2px solid white;
        min-width: 18px;
        text-align: center;
    }
    .dropdown-menu {
        position: absolute;
        top: 120%;
        right: 0;
        width: 350px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        overflow: hidden;
        border: 1px solid rgba(0, 0, 0, 0.08);
        transform-origin: top right;
    }
    @media (max-width: 640px) {
        .dropdown-menu {
            position: fixed;
            width: calc(100vw - 20px);
            max-width: 350px;
            left: 50%;
            top: 230px;
            transform: translateX(-50%);
            transform-origin: top center;
        }
    }
    .dropdown-header {
        padding: 1rem;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #fff;
    }
    .dropdown-header h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 700;
        color: #333;
    }
    .btn-clean {
        background: none;
        border: none;
        color: #007bff;
        font-size: 0.8rem;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .btn-clean:hover {
        background: #eef5ff;
    }
    .dropdown-body {
        max-height: 400px;
        overflow-y: auto;
        overscroll-behavior: contain;
    }
    .notif-item {
        display: flex;
        padding: 12px 16px;
        border-bottom: 1px solid #f5f5f5;
        gap: 12px;
        cursor: pointer;
        transition: background 0.2s;
        position: relative;
    }
    .notif-item:hover {
        background-color: #f8f9fa;
    }
    .notif-item.unread {
        background-color: #f0f7ff;
    }
    .notif-item.unread:hover {
        background-color: #e6f2ff;
    }
    .notif-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .notif-item.guardia .notif-icon {
        background: #e3f2fd;
    }
    .notif-item.incidencia .notif-icon {
        background: #ffebee;
    }
    .notif-item.asistencia .notif-icon {
        background: #e8f5e9;
    }
    .notif-item.licencia .notif-icon {
        background: #e0f7fa;
    }
    .notif-content {
        flex: 1;
        min-width: 0;
    }
    .notif-top {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        align-items: center;
    }
    .notif-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #333;
    }
    .notif-time {
        font-size: 0.7rem;
        color: #888;
        white-space: nowrap;
    }
    .notif-msg {
        margin: 0;
        font-size: 0.85rem;
        color: #666;
        line-height: 1.3;
    }
    .unread-indicator {
        width: 8px;
        height: 8px;
        background-color: #007bff;
        border-radius: 50%;
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
    }
    .empty-state {
        padding: 3rem 1rem;
        text-align: center;
        color: #888;
    }
    .empty-icon {
        font-size: 2rem;
        display: block;
        margin-bottom: 0.5rem;
        opacity: 0.5;
    }
    .dropdown-body::-webkit-scrollbar {
        width: 6px;
    }
    .dropdown-body::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    .dropdown-body::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 3px;
    }
    .dropdown-body::-webkit-scrollbar-thumb:hover {
        background: #bbb;
    }
</style>
