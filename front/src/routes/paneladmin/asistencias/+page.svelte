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
        console.log(
            "🔄 Componente de asistencias montado, iniciando controlador...",
        );
        try {
            await asistenciasController.init();
            console.log(
                "✅ Controlador de asistencias inicializado exitosamente",
            );
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
<div class="admin-container">
    <div class="header">
        <h1>Gestión de Asistencias</h1>
    </div>
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
    <div class="filtros-card">
        <div class="filtros-grid">
            <div class="form-group">
                <label for="fecha">📅 Fecha</label>
                <input
                    type="date"
                    id="fecha"
                    bind:value={$fechaSeleccionada}
                    on:change={() =>
                        asistenciasController.setFecha($fechaSeleccionada)}
                />
            </div>
            <div class="form-group">
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
            <div class="filtro-actions">
                <button
                    class="btn-limpiar"
                    on:click={limpiarFiltros}
                    title="Limpiar filtros"
                >
                    🗑️ Limpiar
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
                                <td>{licencia.agente_dni || "N/A"}</td>
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
    {:else}
        <!-- Lista de Asistencias -->
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
    {/if}
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
    .admin-container {
        width: 100%;
        max-width: 1600px;
        margin: 0 auto;
        padding: 1rem;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }
    .header {
        position: relative;
        background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
        color: white;
        padding: 20px;
        margin-bottom: 30px;
        border-radius: 28px;
        overflow: hidden;
        text-align: center;
        box-shadow:
            0 0 0 1px rgba(255, 255, 255, 0.1) inset,
            0 10px 30px rgba(30, 64, 175, 0.4);
    }
    @media (min-width: 768px) {
        .header {
            padding: 30px 40px;
        }
    }
    .header::before {
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
    .header h1 {
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
        .header h1 {
            font-size: 22px;
        }
    }
    @media (min-width: 640px) {
        .header h1 {
            font-size: 26px;
            display: inline-block;
        }
    }
    @media (min-width: 768px) {
        .header h1 {
            font-size: 30px;
        }
    }
    .header h1::after {
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
    .filtros-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    .filtros-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
        align-items: stretch;
        margin-bottom: 1rem;
    }
    @media (min-width: 768px) {
        .filtros-grid {
            grid-template-columns: 1fr auto auto;
            align-items: end;
        }
    }
    .form-group {
        display: flex;
        flex-direction: column;
    }
    .form-group label {
        font-weight: 600;
        margin-bottom: 0.9rem;
        color: #555;
    }
    .form-group input,
    .form-group select {
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-size: 1rem;
    }
    .filtro-actions {
        display: flex;
        gap: 10px;
        flex-shrink: 0;
    }
    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: #667eea;
    }
    .btn-limpiar {
        padding: 10px 25px;
        background: #6c757d;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        white-space: nowrap;
        height: 42px;
    }
    .btn-limpiar:hover {
        background: #5a6268;
        transform: translateY(-1px);
    }
    .resumen-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
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
        color: #5771e4;
    }
    .table-container {
        overflow-x: auto;
        max-height: 600px;
        overflow-y: auto;
        position: relative;
        border-radius: 24px;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
        background: white;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .table-container::-webkit-scrollbar {
        display: none;
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
    @media (max-width: 768px) {
        .admin-container {
            padding: 1rem;
        }
        .filtros-grid {
            grid-template-columns: 1fr;
        }
        .resumen-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .tabs {
            flex-direction: column;
        }
        .tabs button {
            width: 100%;
        }
        .table-container {
            overflow-x: auto;
        }
        table {
            min-width: 800px;
        }
    }
</style>
