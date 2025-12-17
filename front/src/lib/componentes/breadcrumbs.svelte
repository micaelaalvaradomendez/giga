<script>
    import { browser } from '$app/environment';
    import { page } from "$app/stores";
    
    // Mapeo de rutas a nombres amigables
    const routeNames = {
        inicio: "Inicio",
        incidencias: "Incidencias",
        organigrama: "Organigrama",
        asistencia: "Asistencia",
        licencias: "Licencias",
        guardias: "Guardias",
        reportes: "Reportes",
        paneladmin: "Administración",
        auditoria: "Auditoría",
        compensaciones: "Compensaciones",
        parametros: "Parámetros",
        roles: "Roles",
        convenio: "Convenio CCT",
    };
    
    let crumbs = [];
    
    // Solo calcular breadcrumbs en el cliente
    $: if (browser && $page?.url?.pathname) {
        crumbs = $page.url.pathname
            .split("/")
            .filter(Boolean)
            .map((part, i, arr) => {
                const path = "/" + arr.slice(0, i + 1).join("/");
                let label = routeNames[part] || part;
                if (!routeNames[part]) {
                    label = part.charAt(0).toUpperCase() + part.slice(1);
                }
                return {
                    label,
                    href: path,
                    isLast: i === arr.length - 1,
                };
            });
    }
</script>

{#if browser && crumbs.length > 0 && $page.url.pathname !== "/"}
    <div class="breadcrumbs-container">
        <nav aria-label="Breadcrumb">
            <ol>
                <li>
                    <a href="/inicio">🏠</a>
                    {#if crumbs.length > 0}
                        <span class="separator">/</span>
                    {/if}
                </li>
                {#each crumbs as crumb}
                    <li class:active={crumb.isLast}>
                        {#if crumb.isLast}
                            <span aria-current="page">{crumb.label}</span>
                        {:else}
                            <a href={crumb.href}>{crumb.label}</a>
                            <span class="separator">/</span>
                        {/if}
                    </li>
                {/each}
            </ol>
        </nav>
    </div>
{/if}
<style>
    .breadcrumbs-container {
        padding: 16px 24px;
        margin: 24px 24px 0 24px;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.4) 0%,
            rgba(255, 255, 255, 0.2) 100%
        );
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(64, 123, 255, 0.08);
        border-radius: 16px;
        box-shadow:
            0 2px 8px rgba(64, 123, 255, 0.05),
            inset 0 1px 2px rgba(255, 255, 255, 0.8);
        width: fit-content;
    }
    ol {
        display: flex;
        flex-wrap: wrap;
        list-style: none;
        margin: 0;
        padding: 0;
        align-items: center;
        gap: 8px;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
    }
    li {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #64748b;
    }
    a {
        text-decoration: none;
        color: #407bff;
        font-weight: 600;
        transition: all 0.2s ease;
        padding: 4px 8px;
        border-radius: 8px;
    }
    a:hover {
        background: rgba(64, 123, 255, 0.1);
        color: #2c57c7;
    }
    .separator {
        color: #94a3b8;
        font-size: 12px;
        margin: 0 4px;
    }
    .active span {
        color: #1e293b;
        font-weight: 700;
        padding: 4px 8px;
        background: rgba(64, 123, 255, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(64, 123, 255, 0.1);
    }
    @media (max-width: 768px) {
        .breadcrumbs-container {
            margin: 16px auto 0;
            padding: 10px 14px;
            width: calc(100% - 32px);
            max-width: 100%;
            overflow-x: visible;
        }
        ol {
            font-size: 13px;
            flex-wrap: wrap; 
            justify-content: center; 
        }
    }
</style>
