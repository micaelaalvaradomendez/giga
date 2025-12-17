<script>
    import { createEventDispatcher } from "svelte";
    import { aprobacionesGuardiasController } from "$lib/paneladmin/controllers";
    import { fade, scale } from "svelte/transition";
    export let cronograma; // cronogramaSeleccionado
    export let guardias = []; // guardiasDelCronograma
    export let loading = false;
    const dispatch = createEventDispatcher();
    function cerrar() {
        dispatch("close");
    }
    function eliminarGuardia(guardia) {
        dispatch("eliminarGuardia", guardia);
    }
    function eliminarCronograma(cronograma) {
        dispatch("eliminarCronograma", cronograma);
    }
</script>
<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
    class="modal-overlay"
    on:click={cerrar}
    transition:fade={{ duration: 200 }}
>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div
        class="modal-content"
        on:click|stopPropagation
        transition:scale={{ duration: 200, start: 0.95 }}
    >
        <div class="modal-header">
            <h3>Detalles del Cronograma</h3>
            <button class="close-button" on:click={cerrar}>&times;</button>
        </div>
        <div class="modal-body">
            <div class="detalle-seccion">
                <h4>Información General</h4>
                <div class="info-row">
                    <span class="label">Área:</span>
                    <span class="value"
                        >{cronograma?.area_nombre || "Sin área"}</span
                    >
                </div>
                <div class="info-row">
                    <span class="label">Tipo:</span>
                    <span class="value">{cronograma?.tipo || "-"}</span>
                </div>
                <div class="info-row">
                    <span class="label">Estado:</span>
                    <span class="value">
                        <span class="badge badge-{cronograma?.estado}">
                            {cronograma?.estado}
                        </span>
                    </span>
                </div>
            </div>
            <div class="detalle-seccion">
                <h4>Guardias Asignadas ({guardias.length})</h4>
                {#if guardias.length > 0}
                    <div class="guardias-tabla">
                        <table>
                            <thead>
                                <tr>
                                    <th>Agente</th>
                                    <th>Fecha</th>
                                    <th>Horario</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each guardias as guardia}
                                    <tr>
                                        <td>{guardia.agente_nombre}</td>
                                        <td>
                                            {aprobacionesGuardiasController.formatearFecha(
                                                guardia.fecha,
                                            )}
                                        </td>
                                        <td>
                                            {aprobacionesGuardiasController.formatearHora(
                                                guardia.hora_inicio,
                                            )} -
                                            {aprobacionesGuardiasController.formatearHora(
                                                guardia.hora_fin,
                                            )}
                                        </td>
                                        <td>
                                            <span
                                                class="badge-mini badge-{guardia.estado}"
                                            >
                                                {guardia.estado}
                                            </span>
                                        </td>
                                        <td>
                                            {#if cronograma?.estado !== "publicada"}
                                                {@const hoy = new Date()}
                                                {@const fechaGuardia = new Date(guardia.fecha + 'T00:00:00')}
                                                {#if fechaGuardia >= hoy}
                                                    <button
                                                        class="btn-icon btn-danger-icon"
                                                        on:click={() =>
                                                            eliminarGuardia(guardia)}
                                                        disabled={loading}
                                                        title="Eliminar guardia"
                                                    >
                                                        🗑️
                                                    </button>
                                                {:else}
                                                    <span class="text-muted" title="No se puede eliminar una guardia que ya ocurrió">-</span>
                                                {/if}
                                            {:else}
                                                <span class="text-muted" title="No se pueden eliminar guardias de un cronograma publicado">-</span>
                                            {/if}
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {:else}
                    <p class="text-muted">No hay guardias asignadas</p>
                {/if}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" on:click={cerrar}
                    >Cerrar</button
                >
                {#if cronograma && (cronograma.estado === "pendiente" || cronograma.estado === "aprobada")}
                    <button
                        class="btn btn-danger"
                        on:click={() => eliminarCronograma(cronograma)}
                        disabled={loading}
                    >
                        🗑️ Eliminar Cronograma
                    </button>
                {/if}
            </div>
        </div>
    </div>
</div>
<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    }
    .modal-content {
        background: white;
        border-radius: 16px;
        max-width: 800px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        border: none;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .modal-content::-webkit-scrollbar {
        display: none;
    }
    .modal-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px 16px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: none;
    }
    .modal-header h3 {
        margin: 0;
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .close-button {
        background: none;
        border: none;
        color: white;
        font-size: 25px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.3s ease;
    }
    .close-button:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
    }
    .modal-body {
        padding: 2rem;
    }
    .detalle-seccion {
        margin-bottom: 2rem;
        padding: 1.25rem;
        background: #f9fafb;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    .detalle-seccion:last-child {
        margin-bottom: 0;
    }
    .detalle-seccion h4 {
        margin: 0 0 1rem 0;
        color: #374151;
        font-size: 1rem;
        font-weight: 700;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    .info-row {
        display: flex;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .info-row:last-child {
        border-bottom: none;
    }
    .info-row .label {
        color: #64748b;
        font-size: 0.9rem;
        margin-right: 10px;
        font-weight: 600;
        min-width: 80px;
    }
    .info-row .value {
        color: #111827;
        font-size: 0.9rem;
    }
    .guardias-tabla {
        overflow-x: auto;
        background: white;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    thead {
        background: linear-gradient(
            135deg,
            rgba(142, 182, 228, 0.15) 0%,
            rgba(61, 151, 255, 0.1) 100%
        );
    }
    th,
    td {
        padding: 0.75rem;
        text-align: left;
        font-size: 0.9rem;
    }
    th {
        font-weight: 700;
        color: #1e40af;
        border-bottom: 2px solid #3b82f6;
    }
    td {
        color: #111827;
        border-bottom: 1px solid #f3f4f6;
    }
    tbody tr:hover {
        background: #f9fafb;
        transition: background 0.2s ease;
    }
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: capitalize;
    }
    .badge-pendiente {
        background: #fef3c7;
        color: #92400e;
    }
    .badge-aprobada {
        background: #d1fae5;
        color: #065f46;
    }
    .badge-publicada {
        background: #dbeafe;
        color: #1e40af;
    }
    .badge-rechazada {
        background: #fee2e2;
        color: #991b1b;
    }
    .badge-mini {
        padding: 0.25rem 0.6rem;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: capitalize;
    }
    .badge-mini.badge-planificada {
        background: #dbeafe;
        color: #1e40af;
    }
    .badge-mini.badge-confirmada {
        background: #e0f2fe;
        color: #0284c7;
    }
    .badge-mini.badge-completada {
        background: #dcfce7;
        color: #16a34a;
    }
    .badge-mini.badge-cancelada {
        background: #fee2e2;
        color: #dc2626;
    }
    .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }
    .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
    .btn-secondary {
        background: #6c757d;
        color: white;
    }
    .btn-secondary:hover:not(:disabled) {
        background: #5a6268;
        transform: translateY(-2px);
    }
    .btn-danger {
        background: #ef4444;
        color: white;
    }
    .btn-danger:hover:not(:disabled) {
        background: #dc2626;
        transform: translateY(-2px);
    }
    .btn-icon {
        padding: 0.4rem 0.6rem;
        font-size: 1rem;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        background: transparent;
    }
    .btn-icon:hover:not(:disabled) {
        transform: scale(1.1);
    }
    .btn-danger-icon {
        color: #ef4444;
    }
    .btn-danger-icon:hover:not(:disabled) {
        background: #fee2e2;
    }
    .text-muted {
        color: #9ca3af;
        font-style: italic;
        font-size: 0.95rem;
    }
    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-top: 1.5rem;
        padding-top: 0;
        border-top: none;
    }
</style>
