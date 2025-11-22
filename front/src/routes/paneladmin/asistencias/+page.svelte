<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { asistenciasController } from "$lib/paneladmin/controllers";

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
            alert(result.message);
        }
    }

    async function handleMarcarSalida() {
        const result = await asistenciasController.marcarSalida();
        if (result.message) {
            alert(result.message);
        }
    }

    async function handleCorregirAsistencia() {
        const result = await asistenciasController.corregirAsistencia();
        if (result.message) {
            alert(result.message);
        }
    }
</script>

<svelte:head>
    <title>Gestión de Asistencias - Admin</title>
</svelte:head>

<div class="admin-container">
    <div class="header">
        <h1>Gestión de Asistencias</h1>
    </div>

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
                                        on:click={() =>
                                            asistenciasController.abrirModalCorreccion(
                                                asistencia,
                                            )}
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
{#if $modalCorreccion && $asistenciaEditando}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div
        class="modal-overlay"
        on:click={() => asistenciasController.cerrarModal()}
    >
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="modal-content" on:click|stopPropagation>
            <div class="modal-header">
                <h2>
                    {#if $asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida}
                        ✏️ Corregir Asistencia
                    {:else}
                        ➕ Marcar Asistencia
                    {/if}
                </h2>
                <button
                    class="btn-close"
                    on:click={() => asistenciasController.cerrarModal()}
                    >×</button
                >
            </div>

            <div class="modal-body">
                <p class="agente-info">
                    <strong>{$asistenciaEditando.agente_nombre}</strong><br />
                    <span class="dni-info"
                        >DNI: {$asistenciaEditando.agente_dni}</span
                    ><br />
                    <span class="fecha-info"
                        >{asistenciasController.formatDate(
                            $asistenciaEditando.fecha,
                        )}</span
                    >
                </p>

                {#if $asistenciaEditando.horario_esperado_entrada || $asistenciaEditando.horario_esperado_salida}
                    <div class="horario-esperado">
                        <h3>📅 Horario Esperado</h3>
                        <div class="horario-grid">
                            <div class="horario-item">
                                <span class="horario-label">Entrada:</span>
                                <span class="horario-valor esperado">
                                    {$asistenciaEditando.horario_esperado_entrada
                                        ? asistenciasController.formatTime(
                                              $asistenciaEditando.horario_esperado_entrada,
                                          )
                                        : "--:--"}
                                </span>
                            </div>
                            <div class="horario-item">
                                <span class="horario-label">Salida:</span>
                                <span class="horario-valor esperado">
                                    {$asistenciaEditando.horario_esperado_salida
                                        ? asistenciasController.formatTime(
                                              $asistenciaEditando.horario_esperado_salida,
                                          )
                                        : "--:--"}
                                </span>
                            </div>
                        </div>
                    </div>
                {/if}

                <div class="estado-actual">
                    <h3>✅ Estado Actual</h3>
                    <div class="estado-grid">
                        <div class="estado-item">
                            <span class="estado-label">Entrada:</span>
                            <span
                                class="estado-valor {$asistenciaEditando.hora_entrada
                                    ? 'marcado'
                                    : 'sin-marcar'}"
                            >
                                {$asistenciaEditando.hora_entrada
                                    ? asistenciasController.formatTime(
                                          $asistenciaEditando.hora_entrada,
                                      )
                                    : "Sin marcar"}
                            </span>
                        </div>
                        <div class="estado-item">
                            <span class="estado-label">Salida:</span>
                            <span
                                class="estado-valor {$asistenciaEditando.hora_salida
                                    ? 'marcado'
                                    : 'sin-marcar'}"
                            >
                                {$asistenciaEditando.hora_salida
                                    ? asistenciasController.formatTime(
                                          $asistenciaEditando.hora_salida,
                                      )
                                    : "Sin marcar"}
                            </span>
                        </div>
                    </div>
                </div>

                {#if $asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida}
                    <div class="info-correccion">
                        <div class="info-header">
                            <span class="info-icon">ℹ️</span>
                            <strong>Corrección de Asistencia</strong>
                        </div>
                        <p>Esta asistencia ya tiene marcaciones registradas. Puede corregir las horas especificando los nuevos valores.</p>
                        <p><strong>Importante:</strong> La corrección quedará registrada en el historial de auditoría.</p>
                    </div>
                {/if}

                <div class="form-group">
                    <label for="observacion_edit">
                        Observación 
                        {#if $asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida}
                            (requerida para corrección)
                        {:else}
                            (opcional)
                        {/if}
                    </label>
                    <textarea
                        id="observacion_edit"
                        bind:value={$observacionEdit}
                        placeholder={$asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida 
                            ? "Explique el motivo de la corrección (ej: 'Error en marcación original', 'Horario corregido por supervisor')"
                            : "Motivo de la corrección (ej: 'Agente olvidó marcar')"}
                        rows="3"
                    ></textarea>
                </div>

                <!-- Sección para especificar hora -->
                <div class="hora-especifica-section">
                    <div class="checkbox-group">
                        <input
                            type="checkbox"
                            id="usar_hora_especifica"
                            bind:checked={$usarHoraEspecifica}
                        />
                        <label for="usar_hora_especifica">
                            {#if $asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida}
                                Corregir horas existentes
                            {:else}
                                Especificar hora real de entrada/salida
                            {/if}
                        </label>
                    </div>

                    {#if $usarHoraEspecifica}
                        <div class="horas-grid">
                            <div class="form-group">
                                <label for="hora_entrada_input">
                                    🕐 Hora de entrada
                                    {#if $asistenciaEditando.hora_entrada}
                                        <span class="actual-time">(Actual: {asistenciasController.formatTime($asistenciaEditando.hora_entrada)})</span>
                                    {/if}
                                </label>
                                <input
                                    type="time"
                                    id="hora_entrada_input"
                                    bind:value={$horaEntrada}
                                    placeholder="HH:MM"
                                />
                                <small class="help-text">
                                    {#if $asistenciaEditando.hora_entrada}
                                        Nueva hora de entrada a registrar
                                    {:else}
                                        Solo se usará si marcas entrada
                                    {/if}
                                </small>
                            </div>

                            <div class="form-group">
                                <label for="hora_salida_input">
                                    🕔 Hora de salida
                                    {#if $asistenciaEditando.hora_salida}
                                        <span class="actual-time">(Actual: {asistenciasController.formatTime($asistenciaEditando.hora_salida)})</span>
                                    {/if}
                                </label>
                                <input
                                    type="time"
                                    id="hora_salida_input"
                                    bind:value={$horaSalida}
                                    placeholder="HH:MM"
                                />
                                <small class="help-text">
                                    {#if $asistenciaEditando.hora_salida}
                                        Nueva hora de salida a registrar
                                    {:else}
                                        Solo se usará si marcas salida
                                    {/if}
                                </small>
                            </div>
                        </div>
                    {/if}
                </div>
            </div>

            <div class="modal-footer">
                <button
                    class="btn-cancelar"
                    on:click={() => asistenciasController.cerrarModal()}
                >
                    Cancelar
                </button>
                
                {#if $asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida}
                    <!-- Botones para corregir asistencia existente -->
                    <button
                        class="btn-corregir"
                        on:click={handleCorregirAsistencia}
                        disabled={!$usarHoraEspecifica || 
                                 (!$horaEntrada && !$horaSalida) ||
                                 !$observacionEdit.trim()}
                    >
                        ✏️ Aplicar Corrección
                    </button>
                {:else}
                    <!-- Botones para marcar nueva asistencia -->
                    <button
                        class="btn-marcar-entrada"
                        on:click={handleMarcarEntrada}
                    >
                        🕐 Marcar Entrada
                    </button>
                    <button
                        class="btn-marcar-salida"
                        on:click={handleMarcarSalida}
                        disabled={!$asistenciaEditando.hora_entrada}
                    >
                        🕐 Marcar Salida
                    </button>
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    .admin-container {
        width: 100%;
        max-width: 1600px;
        margin: 0 auto;
        padding: 1rewm 0;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .header {
        position: relative;
        background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
        color: white;
        padding: 30px 40px;
        margin-bottom: 30px;
        border-radius: 28px;
        overflow: hidden;
        text-align: center;
        box-shadow:
            0 0 0 1px rgba(255, 255, 255, 0.1) inset,
            0 10px 30px rgba(30, 64, 175, 0.4);
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
        font-size: 30px;
        letter-spacing: 0.2px;
        position: relative;
        padding-bottom: 12px;
        overflow: hidden;
        display: inline-block;
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

    /* Filtros */
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
        grid-template-columns: 1fr auto auto;
        gap: 1rem;
        align-items: end;
        margin-bottom: 1rem;
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
    .form-group select,
    .form-group textarea {
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
    .form-group select:focus,
    .form-group textarea:focus {
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

    /* Resumen */
    .resumen-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .resumen-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }

    .resumen-card.total {
        border-left-color: #667eea;
    }

    .resumen-card.presentes {
        border-left-color: #28a745;
    }

    .resumen-card.ausentes {
        border-left-color: #dc3545;
    }

    .resumen-card.sin-salida {
        border-left-color: #ffc107;
    }

    .resumen-card.automaticas {
        border-left-color: #17a2b8;
    }

    .resumen-card .numero {
        font-size: 2.5rem;
        font-weight: 700;
        color: #333;
    }

    .resumen-card .label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }

    /* Tabs */
    .tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .tabs button {
        padding: 0.75rem 1.5rem;
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        color: #666;
        transition: all 0.3s ease;
    }

    .tabs button:hover {
        border-color: #667eea;
        color: #667eea;
    }

    .tabs button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }

    /* Tabla */
    .table-container {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    th {
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }

    td {
        padding: 1rem;
        border-bottom: 1px solid #f0f0f0;
    }

    tbody tr:hover {
        background: #f8f9fa;
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
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
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

    /* Modal */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        backdrop-filter: blur(4px);
    }

    .modal-content {
        background: white;
        border-radius: 16px;
        max-width: 600px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px 16px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .modal-header h2 {
        margin: 0;
        font-size: 1.5rem;
    }

    .btn-close {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        font-size: 2rem;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    }

    .btn-close:hover {
        background: rgba(255, 255, 255, 0.3);
    }

    .modal-body {
        padding: 2rem;
    }

    .agente-info {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }

    .agente-info strong {
        font-size: 1.2rem;
        color: #333;
    }

    .dni-info,
    .fecha-info {
        color: #666;
        font-size: 0.9rem;
    }

    .horario-esperado {
        background: linear-gradient(135deg, #fff7e6 0%, #fff3dc 100%);
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }

    .horario-esperado h3 {
        margin: 0 0 1rem 0;
        color: #856404;
        font-size: 1.1rem;
    }

    .horario-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .horario-item {
        display: flex;
        flex-direction: column;
    }

    .horario-label {
        font-weight: 600;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }

    .horario-valor {
        font-family: "Courier New", monospace;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .horario-valor.esperado {
        color: #ff6f00;
    }

    .estado-actual {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }

    .estado-actual h3 {
        margin: 0 0 1rem 0;
        color: #333;
        font-size: 1.1rem;
    }

    .estado-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .estado-item {
        display: flex;
        flex-direction: column;
    }

    .estado-label {
        font-weight: 600;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }

    .estado-valor {
        font-family: "Courier New", monospace;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .estado-valor.marcado {
        color: #28a745;
    }

    .estado-valor.sin-marcar {
        color: #dc3545;
    }

    .observaciones-previas {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }

    .observaciones-previas strong {
        color: #856404;
    }

    .observaciones-previas p {
        margin: 0.5rem 0 0 0;
        color: #333;
    }

    .info-correccion {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border: 1px solid #90caf9;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .info-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        color: #1565c0;
    }

    .info-icon {
        font-size: 1.2rem;
    }

    .info-correccion p {
        margin: 0.5rem 0;
        color: #333;
        line-height: 1.4;
    }

    .info-correccion p:first-of-type {
        margin-top: 0;
    }

    .info-correccion p:last-of-type {
        margin-bottom: 0;
        font-weight: 600;
        color: #d32f2f;
    }

    .modal-footer {
        padding: 1.5rem 2rem;
        border-top: 1px solid #e0e0e0;
        display: flex;
        gap: 1rem;
        justify-content: flex-end;
    }

    .modal-footer button {
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .btn-cancelar {
        background: #e0e0e0;
        color: #333;
    }

    .btn-cancelar:hover {
        background: #d0d0d0;
    }

    .btn-marcar-entrada {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }

    .btn-marcar-entrada:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
    }

    .btn-marcar-salida {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
    }

    .btn-marcar-salida:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(23, 162, 184, 0.4);
    }

    .btn-corregir {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        color: white;
    }

    .btn-corregir:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
    }

    .actual-time {
        font-weight: 400;
        color: #666;
        font-size: 0.85rem;
        margin-left: 0.5rem;
    }

    .modal-footer button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
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

        .horario-grid,
        .estado-grid {
            grid-template-columns: 1fr;
        }

        .modal-footer {
            flex-direction: column;
        }

        .modal-footer button {
            width: 100%;
        }
    }

    /* Estilos para hora específica */
    .hora-especifica-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        border-left: 4px solid #17a2b8;
    }

    .checkbox-group {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .checkbox-group input[type="checkbox"] {
        width: 18px;
        height: 18px;
        accent-color: #17a2b8;
    }

    .checkbox-group label {
        font-weight: 600;
        color: #333;
        cursor: pointer;
        margin-bottom: 0;
    }

    .horas-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
    }

    .help-text {
        color: #666;
        font-size: 0.8rem;
        margin-top: 0.25rem;
        font-style: italic;
    }

    @media (max-width: 768px) {
        .horas-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
