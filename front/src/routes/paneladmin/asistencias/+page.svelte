<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { asistenciasController } from "$lib/paneladmin/controllers";
    import ModalCorreccionAsistencia from "$lib/componentes/admin/asistencias/ModalCorreccionAsistencia.svelte";
    import ModalAlert from "$lib/componentes/ModalAlert.svelte";
    import { modalAlert, showAlert } from "$lib/stores/modalAlertStore.js";
    // Obtener stores del controlador
    const {
        loading,
        areas,
        resumen,
        licencias,
        asistenciasFiltradas,
        fechaSeleccionada,
        areaSeleccionada,
        tabActiva,
        modalCorreccion,
        asistenciaEditando,
        observacionEdit,
        horaEntrada,
        horaSalida,
        usarHoraEspecifica,
    } = asistenciasController;
    onMount(async () => {
        
        try {
            await asistenciasController.init();
            
            // Recargar cuando la página vuelve a ser visible
            if (typeof window !== "undefined") {
                const handleVisibilityChange = () => {
                    if (document.visibilityState === "visible") {
                        asistenciasController.recargar();
                    }
                };
                const handleFocus = () => {
                    asistenciasController.recargar();
                };
                document.addEventListener(
                    "visibilitychange",
                    handleVisibilityChange,
                );
                window.addEventListener("focus", handleFocus);
                return () => {
                    document.removeEventListener(
                        "visibilitychange",
                        handleVisibilityChange,
                    );
                    window.removeEventListener("focus", handleFocus);
                };
            }
        } catch (err) {
            console.error("❌ Error inicializando controlador:", err);
            if (err.message.includes("no autenticado")) {
                goto("/");
                return;
            }
        }
    });
    function limpiarFiltros() {
        asistenciasController.limpiarFiltros();
    }
    // Funciones delegadas al controlador
    async function handleMarcarEntrada() {
        const result = await asistenciasController.marcarEntrada();
        if (result.message) {
            const tipo = result.success ? "success" : "error";
            const titulo = result.success ? "Éxito" : "Error";
            await showAlert(result.message, tipo, titulo);
        }
    }
    async function handleMarcarSalida() {
        const result = await asistenciasController.marcarSalida();
        if (result.message) {
            const tipo = result.success ? "success" : "error";
            const titulo = result.success ? "Éxito" : "Error";
            await showAlert(result.message, tipo, titulo);
        }
    }
    async function handleCorregirAsistencia() {
        const result = await asistenciasController.corregirAsistencia();
        if (result.message) {
            const tipo = result.success ? "success" : "error";
            const titulo = result.success ? "Éxito" : "Error";
            await showAlert(result.message, tipo, titulo);
        }
    }
    async function handleMarcarAusente() {
        const result = await asistenciasController.marcarComoAusente();
        if (result.message) {
            const tipo = result.success ? "success" : "error";
            const titulo = result.success ? "Éxito" : "Error";
            await showAlert(result.message, tipo, titulo);
        }
    }
    function handleCheckboxChange() {
        asistenciasController.toggleHoraEspecifica();
    }
</script>
<svelte:head>
    <title>Gestión de Asistencias - Admin</title>
</svelte:head>
<div class="page-container">
    <div class="page-header">
        <div class="header-title">
            <h1>Gestión de Asistencias</h1>
        </div>
    </div>
    <div class="page-content">
    <!-- Resumen -->
    {#if $resumen}
        <div class="resumen-grid">
            <div class="resumen-card total">
                <div class="numero">{$resumen.total_agentes}</div>
                <div class="label">Total Agentes</div>
            </div>
            <div class="resumen-card presentes">
                <div class="numero">{$resumen.presentes}</div>
                <div class="label">Presentes</div>
            </div>
            <div class="resumen-card ausentes">
                <div class="numero">{$resumen.ausentes}</div>
                <div class="label">Ausentes</div>
            </div>
            <div class="resumen-card sin-salida">
                <div class="numero">{$resumen.sin_salida}</div>
                <div class="label">Sin Salida</div>
            </div>
            <div class="resumen-card automaticas">
                <div class="numero">{$resumen.salidas_automaticas}</div>
                <div class="label">Salidas Auto</div>
            </div>
        </div>
    {/if}
    <!-- Filtros -->
    <div class="filtros-container">
        <div class="filtros-row">
            <div class="filtro-group">
                <label for="fecha">📅 Fecha</label>
                <input
                    type="date"
                    id="fecha"
                    bind:value={$fechaSeleccionada}
                    on:change={() =>
                        asistenciasController.setFecha($fechaSeleccionada)}
                />
            </div>
            <div class="filtro-group">
                <label for="area">📍 Filtrar por área</label>
                <select
                    id="area"
                    bind:value={$areaSeleccionada}
                    on:change={() =>
                        asistenciasController.setArea($areaSeleccionada)}
                >
                    <option value="">Todas las áreas ({$areas.length})</option>
                    {#each $areas as area}
                        <option value={area.id_area}>{area.nombre}</option>
                    {/each}
                    {#if $areas.length === 0}
                        <option disabled>❌ No hay áreas cargadas</option>
                    {/if}
                </select>
            </div>
            <div class="filtro-group">
                <button
                    class="btn-clear"
                    on:click={limpiarFiltros}
                    title="Limpiar filtros"
                >
                    🗑️ Limpiar Filtros
                </button>
            </div>
        </div>
    </div>
    <!-- Tabs -->
    <div class="tabs">
        <button
            class:active={$tabActiva === "todas"}
            on:click={() => asistenciasController.setTabActiva("todas")}
        >
            Todas
        </button>
        <button
            class:active={$tabActiva === "completas"}
            on:click={() => asistenciasController.setTabActiva("completas")}
        >
            Completas
        </button>
        <button
            class:active={$tabActiva === "sin_salida"}
            on:click={() => asistenciasController.setTabActiva("sin_salida")}
        >
            Sin Salida
        </button>
        <button
            class:active={$tabActiva === "sin_entrada"}
            on:click={() => asistenciasController.setTabActiva("sin_entrada")}
        >
            Sin Entrada
        </button>
        <button
            class:active={$tabActiva === "salidas_auto"}
            on:click={() => asistenciasController.setTabActiva("salidas_auto")}
        >
            Salidas Auto
        </button>
        <button
            class:active={$tabActiva === "licencias"}
            on:click={() => asistenciasController.setTabActiva("licencias")}
        >
            Licencias
        </button>
    </div>
    <!-- Contenido -->
    {#if $loading}
        <div class="loading">Cargando...</div>
    {:else if $tabActiva === "licencias"}
        <!-- Lista de Licencias -->
        <!-- Desktop View -->
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Agente</th>
                        <th>DNI</th>
                        <th>Área</th>
                        <th>Tipo de Licencia</th>
                        <th>Desde</th>
                        <th>Hasta</th>
                    </tr>
                </thead>
                <tbody>
                    {#if $licencias.length === 0}
                        <tr>
                            <td colspan="6" class="empty"
                                >No hay licencias en esta fecha</td
                            >
                        </tr>
                    {:else}
                        {#each $licencias as licencia}
                            <tr>
                                <td>{licencia.agente_nombre}</td>
                                <td>{licencia.agente_dni || licencia.dni || (licencia.agente ? licencia.agente.dni : "N/A")}</td>
                                <td>{licencia.area_nombre || "N/A"}</td>
                                <td>{licencia.tipo_licencia_descripcion}</td>
                                <td
                                    >{asistenciasController.formatDate(
                                        licencia.fecha_desde,
                                    )}</td
                                >
                                <td
                                    >{asistenciasController.formatDate(
                                        licencia.fecha_hasta,
                                    )}</td
                                >
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
        <!-- Mobile View -->
    {:else}
        <!-- Lista de Asistencias -->
        <!-- Desktop View -->
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Agente</th>
                        <th>DNI</th>
                        <th>Área</th>
                        <th>Entrada</th>
                        <th>Salida</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {#if $asistenciasFiltradas.length === 0}
                        <tr>
                            <td colspan="7" class="empty">No hay registros</td>
                        </tr>
                    {:else}
                        {#each $asistenciasFiltradas as asistencia}
                            <tr>
                                <td>
                                    {asistencia.agente_nombre}
                                    {#if asistencia.es_correccion}
                                        <span
                                            class="badge-correccion"
                                            title="Corregido por {asistencia.corregido_por_nombre}"
                                        >
                                            ✏️
                                        </span>
                                    {/if}
                                </td>
                                <td>{asistencia.agente_dni}</td>
                                <td>{asistencia.area_nombre || "N/A"}</td>
                                <td>
                                    <span class="hora"
                                        >{asistenciasController.formatTime(
                                            asistencia.hora_entrada,
                                        )}</span
                                    >
                                    {#if asistencia.marcacion_entrada_automatica}
                                        <span class="badge-auto">AUTO</span>
                                    {/if}
                                </td>
                                <td>
                                    <span class="hora"
                                        >{asistenciasController.formatTime(
                                            asistencia.hora_salida,
                                        )}</span
                                    >
                                    {#if asistencia.marcacion_salida_automatica}
                                        <span class="badge-auto">AUTO</span>
                                    {/if}
                                </td>
                                <td>
                                    {#if asistencia.estado}
                                        {@const badge =
                                            asistenciasController.getEstadoBadge(
                                                asistencia,
                                            )}
                                        <span class="badge {badge.class}"
                                            >{badge.text}</span
                                        >
                                    {/if}
                                </td>
                                <td>
                                    <button
                                        class="btn-editar"
                                        on:click={() => {
                                            if (asistencia) {
                                                asistenciasController.abrirModalCorreccion(
                                                    asistencia,
                                                );
                                            } else {
                                                showAlert(
                                                    "Error: Datos de asistencia no disponibles",
                                                    "error",
                                                    "Error",
                                                );
                                                console.error(
                                                    "❌ Asistencia es null:",
                                                    asistencia,
                                                );
                                            }
                                        }}
                                    >
                                        ✏️ Corregir
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
        <!-- Mobile View -->
    {/if}
    </div>
</div>
<!-- Modal de Corrección -->
<ModalCorreccionAsistencia
    show={$modalCorreccion}
    asistencia={$asistenciaEditando}
    bind:observacion={$observacionEdit}
    bind:horaEntrada={$horaEntrada}
    bind:horaSalida={$horaSalida}
    bind:usarHoraEspecifica={$usarHoraEspecifica}
    on:cerrar={() => asistenciasController.cerrarModal()}
    on:marcarEntrada={handleMarcarEntrada}
    on:marcarSalida={handleMarcarSalida}
    on:corregir={handleCorregirAsistencia}
    on:marcarAusente={handleMarcarAusente}
    on:toggleHoraEspecifica={handleCheckboxChange}
/>
<!-- Modal de alertas -->
<ModalAlert
    bind:show={$modalAlert.show}
    type={$modalAlert.type}
    title={$modalAlert.title}
    message={$modalAlert.message}
    showConfirmButton={$modalAlert.showConfirmButton}
    confirmText={$modalAlert.confirmText}
    showCancelButton={$modalAlert.showCancelButton}
    cancelText={$modalAlert.cancelText}
    on:confirm={() => $modalAlert.onConfirm && $modalAlert.onConfirm()}
    on:cancel={() => $modalAlert.onCancel && $modalAlert.onCancel()}
/>
<style>
    * {
        box-sizing: border-box;
    }
    .page-container {
        margin: 0 auto;
        padding: 1.5rem;
        min-height: 100vh;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        box-sizing: border-box;
        overflow-x: hidden;
        width: 100%;
    }
    .page-content {
        width: 100%;
    }
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .header-title {
        position: relative;
        background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
        color: white;
        padding: 30px 40px;
        margin: 0;
        border-radius: 28px;
        overflow: hidden;
        text-align: center;
        box-shadow:
            0 0 0 1px rgba(255, 255, 255, 0.1) inset,
            0 20px 60px rgba(30, 64, 175, 0.4);
    }
    .header-title::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.03) 1px,
                transparent 1px
            ),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: moveLines 20s linear infinite;
    }
    .header-title h1 {
        margin: 10px;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 0.2px;
        position: relative;
        padding-bottom: 12px;
        overflow: hidden;
        display: block;
        max-width: 100%;
        word-wrap: break-word;
    }
    @media (min-width: 480px) {
        .header-title h1 {
            font-size: 22px;
        }
    }
    @media (min-width: 640px) {
        .header-title h1 {
            font-size: 26px;
            display: inline-block;
        }
    }
    @media (min-width: 768px) {
        .header-title h1 {
            font-size: 30px;
        }
    }
    @media (min-width: 768px) {
        .header-title h1 {
            font-size: 30px;
        }
    }
    @media (max-width: 768px) {
        .header-title {
            padding: 20px 20px;
        }
    }
    .header-title h1::after {
        content: "";
        position: absolute;
        width: 40%;
        height: 3px;
        bottom: 0;
        left: 0;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.9),
            transparent
        );
        animation: moveLine 2s linear infinite;
    }
    @keyframes moveLine {
        0% {
            left: -40%;
        }
        100% {
            left: 100%;
        }
    }
    @keyframes moveLines {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 50px 50px;
        }
    }

    .resumen-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .resumen-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 4px solid #4c51bf;
        transition: transform 0.3s ease;
    }
    .resumen-card:hover {
        transform: translateY(-5px);
    }
    .numero {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4c51bf;
    }
    .resumen-card.total {
        border-top-color: #667eea;
    }
    .resumen-card.presentes {
        border-top-color: #28a745;
    }
    .resumen-card.ausentes {
        border-top-color: #dc3545;
    }
    .resumen-card.sin-salida {
        border-top-color: #ffc107;
    }
    .resumen-card.automaticas {
        border-top-color: #17a2b8;
    }
    .resumen-card.presentes .numero {
        color: #28a745;
    }
    .resumen-card.ausentes .numero {
        color: #dc3545;
    }
    .resumen-card.sin-salida .numero {
        color: #ffc107;
    }
    .resumen-card.automaticas .numero {
        color: #17a2b8;
    }
    .resumen-card .label {
        font-size: 16px;
        color: #222222e0;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    .filtros-container {
        background: #f3f3f3d8;
        border: 1px solid #e0e0e09c;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    .filtros-row {
        display: flex;
        gap: 2rem;
        align-items: end;
        flex-wrap: nowrap;
    }
    .filtro-group {
        flex: 1 1 200px;
        min-width: 160px;
        max-width: 100%;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .filtro-group label {
        font-weight: 600;
        font-size: 14px;
        color: #4a5568;
    }
    .filtro-group input,
    .filtro-group select {
        padding: 0.75rem;
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        font-size: 1rem;
        background: white;
        transition: all 0.2s;
    }
    .filtro-group input:focus,
    .filtro-group select:focus {
        outline: none;
        border-color: #4c51bf;
        box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
    }
    .btn-clear {
        padding: 0.5rem 1rem;
        background: #e53e3e;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
    }
    .btn-clear:hover {
        background: #c53030;
    }

    .tabs {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        font-weight: 700;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 14px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    .tabs button {
        padding: 0.875rem 1.75rem;
        background: transparent;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        font-weight: 700;
        font-size: 0.95rem;
        color: #64748b;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .tabs button::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #c6d3f8;
        border-radius: 12px;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: -1;
    }
    .tabs button:hover::before {
        opacity: 1;
    }
    .tabs button:hover {
        color: #667eea;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.12);
    }
    .tabs button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
        transform: translateY(-1px);
    }
    .tabs button.active:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        color: #f0f0f0;
    }

    .table-container {
        overflow-x: auto;
        max-height: 600px;
        overflow-y: auto;
        position: relative;
        border-radius: 24px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
        background: white;
        scrollbar-width: thin;
        scrollbar-color: #c1c7cd #f1f3f4;
    }
    
    @media (min-width: 1024px) {
        .table-container {
            overflow-x: hidden;
        }
    }
    .table-container::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    .table-container::-webkit-scrollbar-track {
        background: #f1f3f4;
        border-radius: 10px;
    }
    .table-container::-webkit-scrollbar-thumb {
        background: #c1c7cd;
        border-radius: 10px;
        transition: background 0.3s ease;
    }
    .table-container::-webkit-scrollbar-thumb:hover {
        background: #a8aeb4;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        background: white;
    }
    thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        position: sticky;
        top: 0;
        z-index: 10;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    th {
        padding: 15px 20px;
        text-align: left;
        font-weight: 600;
        color: white;
        border-bottom: none;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: transparent;
    }
    td {
        padding: 15px 20px;
        border-bottom: 1px solid #f1f3f4;
        vertical-align: middle;
        font-size: 0.95rem;
    }
    tbody tr {
        transition: all 0.3s ease;
    }
    tbody tr:hover {
        background-color: #f8f9fa;
        transform: scale(1.01);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .empty {
        text-align: center;
        color: #999;
        font-style: italic;
        padding: 3rem !important;
    }
    .hora {
        font-family: "Courier New", monospace;
        font-weight: 600;
    }
    .badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }
    .badge-success {
        background: #d4edda;
        color: #155724;
    }
    .badge-warning {
        background: #fff3cd;
        color: #856404;
    }
    .badge-error {
        background: #f8d7da;
        color: #721c24;
    }
    .badge-auto {
        background: #17a2b8;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-left: 0.5rem;
    }
    .badge-correccion {
        margin-left: 0.5rem;
        cursor: help;
    }
    .btn-editar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        transition: transform 0.2s ease;
    }
    .btn-editar:hover {
        transform: translateY(-2px);
    }
    .loading {
        text-align: center;
        padding: 3rem;
        color: #666;
        font-size: 1.2rem;
    }
    .desktop-only {
        display: block;
    }
    .mobile-only {
        display: none;
    }
    @media (max-width: 768px) {
        .desktop-only {
            display: none !important;
        }
        .mobile-only {
            display: flex !important;
            flex-direction: column;
        }
        .page-container {
            padding: 0.75rem;
            max-width: 100vw;
            overflow-x: hidden;
            box-sizing: border-box;
        }
        .page-header {
            flex-direction: column;
            gap: 1rem;
            align-items: stretch;
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        .header-title {
            padding: 18px 12px;
            border-radius: 16px;
            margin: 0;
            width: 100%;
            box-sizing: border-box;
        }
        .header-title h1 {
            font-size: 18px;
            word-break: break-word;
            line-height: 1.3;
        }
        .filtros-container {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .filtros-row {
            flex-direction: column;
            gap: 1rem;
        }
        .filtro-group {
            flex: 1 1 100%;
            min-width: 100%;
        }
        .filtro-group label {
            font-size: 14px;
            display: block;
            margin-bottom: 6px;
        }
        .filtro-group input,
        .filtro-group select {
            padding: 12px;
            font-size: 14px;
            border-radius: 10px;
        }
        .btn-clear {
            width: 100%;
            height: auto;
            padding: 14px;
            font-size: 14px;
            border-radius: 10px;
            margin-top: 0.5rem;
        }
        .tabs {
            flex-direction: column;
        }
        .tabs button {
            width: 100%;
        }
    }

    .cards-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    .licencia-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    .licencia-card.pending {
        border-left: 4px solid #ed8936;
        background: linear-gradient(to right, #fffbeb, white);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 12px 14px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-bottom: 1px solid #e5e7eb;
        gap: 10px;
    }
    .card-agente {
        display: flex;
        flex-direction: column;
        gap: 1px;
        flex: 1;
        min-width: 0;
    }
    .card-agente strong {
        font-size: 15px;
        color: #1e293b;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .card-agente small {
        font-size: 12px;
        color: #64748b;
    }
    .tipo-badge-mobile {
        display: inline-block;
        margin-top: 6px;
        padding: 4px 10px;
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        color: #3730a3;
        font-size: 11px;
        font-weight: 600;
        border-radius: 12px;
        border: 1px solid #a5b4fc;
        align-self: flex-start;
    }
    .card-body {
        padding: 8px 14px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 4px;
        padding: 2px 0;
        flex-wrap: wrap;
    }
    .card-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        flex-shrink: 0;
    }
    .card-value {
        font-size: 13px;
        color: #1e293b;
        font-weight: 600;
        text-align: right;
    }
    .card-actions {
        display: flex;
        gap: 10px;
        padding: 12px 16px;
        background: #f8fafc;
        border-top: 1px solid #e5e7eb;
    }
    .btn-card {
        flex: 1;
        padding: 12px 16px;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #718096;
    }
</style>

