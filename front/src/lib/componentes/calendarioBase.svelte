<script>
    import { createEventDispatcher, onMount } from "svelte";
    export let feriados = [];
    export let guardias = [];
    const dispatch = createEventDispatcher();
    var dayNames = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
    let monthNames = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ];
    let headers = [];
    let now = new Date();
    let year = now.getFullYear();
    let month = now.getMonth();
    var days = [];
    // Variables para el modal de guardias
    let showGuardiasModal = false;
    let guardiasModalData = {
        fecha: null,
        guardias: [],
    };
    // Función para verificar si una fecha es feriado
    function esFeriado(fecha) {
        if (!feriados || feriados.length === 0) return false;
        const fechaStr = fecha.toISOString().split("T")[0];
        return feriados.some((feriado) => {
            // Verificar si la fecha está dentro del rango fecha_inicio - fecha_fin
            return (
                fechaStr >= feriado.fecha_inicio &&
                fechaStr <= feriado.fecha_fin
            );
        });
    }
    // Función para obtener feriados de una fecha específica (puede haber múltiples)
    function getFeriados(fecha) {
        if (!feriados || feriados.length === 0) return [];
        const fechaStr = fecha.toISOString().split("T")[0];
        return feriados.filter((feriado) => {
            // Verificar si la fecha está dentro del rango fecha_inicio - fecha_fin
            return (
                fechaStr >= feriado.fecha_inicio &&
                fechaStr <= feriado.fecha_fin
            );
        });
    }
    // Función para obtener el primer feriado de una fecha específica (compatibilidad)
    function getFeriado(fecha) {
        const feriadosEnFecha = getFeriados(fecha);
        return feriadosEnFecha.length > 0 ? feriadosEnFecha[0] : null;
    }
    // Función para verificar si una fecha tiene guardia
    function tieneGuardia(fecha) {
        if (!guardias || guardias.length === 0) return false;
        const fechaStr = fecha.toISOString().split("T")[0];
        return guardias.some((guardia) => {
            // Verificar si la guardia incluye esta fecha
            if (guardia.fecha === fechaStr) {
                return true;
            }
            // Verificar si es una guardia multi-día que se inició el día anterior
            if (
                guardia.es_multiples_dias ||
                guardia.hora_inicio > guardia.hora_fin
            ) {
                const fechaGuardia = new Date(guardia.fecha);
                const fechaSiguiente = new Date(fechaGuardia);
                fechaSiguiente.setDate(fechaSiguiente.getDate() + 1);
                return fechaSiguiente.toISOString().split("T")[0] === fechaStr;
            }
            return false;
        });
    }
    // Función para obtener las guardias de una fecha específica
    function getGuardias(fecha) {
        if (!guardias || guardias.length === 0) return [];
        const fechaStr = fecha.toISOString().split("T")[0];
        return guardias.filter((guardia) => {
            // Verificar si la guardia incluye esta fecha
            if (guardia.fecha === fechaStr) {
                return true;
            }
            // Verificar si es una guardia multi-día que se inició el día anterior
            if (
                guardia.es_multiples_dias ||
                guardia.hora_inicio > guardia.hora_fin
            ) {
                const fechaGuardia = new Date(guardia.fecha);
                const fechaSiguiente = new Date(fechaGuardia);
                fechaSiguiente.setDate(fechaSiguiente.getDate() + 1);
                return fechaSiguiente.toISOString().split("T")[0] === fechaStr;
            }
            return false;
        });
    }
    $: month, year, initContent();
    function initContent() {
        headers = dayNames;
        initMonth();
    }
    function initMonth() {
        days = [];
        let monthAbbrev = monthNames[month].slice(0, 3);
        let nextMonthAbbrev = monthNames[(month + 1) % 12].slice(0, 3);
        var firstDay = new Date(year, month, 1).getDay();
        var daysInThisMonth = new Date(year, month + 1, 0).getDate();
        var daysInLastMonth = new Date(year, month, 0).getDate();
        var prevMonth = month == 0 ? 11 : month - 1;
        let today = new Date();
        // Días del mes anterior
        for (let i = daysInLastMonth - firstDay; i < daysInLastMonth; i++) {
            let d = new Date(
                prevMonth == 11 ? year - 1 : year,
                prevMonth,
                i + 1,
            );
            days.push({
                name: "" + (i + 1),
                enabled: false,
                date: d,
                isToday: false,
                isFeriado: false,
                feriado: null,
                tieneGuardia: false,
                guardias: [],
            });
        }
        // Días del mes actual
        for (let i = 0; i < daysInThisMonth; i++) {
            let d = new Date(year, month, i + 1);
            let isToday =
                d.getDate() == today.getDate() &&
                d.getMonth() == today.getMonth() &&
                d.getFullYear() == today.getFullYear();
            let isFeriadoDay = esFeriado(d);
            let feriadoData = isFeriadoDay ? getFeriado(d) : null;
            let feriadosData = isFeriadoDay ? getFeriados(d) : [];
            let tieneGuardiaDay = tieneGuardia(d);
            let guardiasData = tieneGuardiaDay ? getGuardias(d) : [];
            if (i == 0) {
                days.push({
                    name: monthAbbrev + " " + (i + 1),
                    enabled: true,
                    date: d,
                    isToday: isToday,
                    isFeriado: isFeriadoDay,
                    feriado: feriadoData,
                    feriados: feriadosData,
                    tieneGuardia: tieneGuardiaDay,
                    guardias: guardiasData,
                });
            } else {
                days.push({
                    name: "" + (i + 1),
                    enabled: true,
                    date: d,
                    isToday: isToday,
                    isFeriado: isFeriadoDay,
                    feriado: feriadoData,
                    feriados: feriadosData,
                    tieneGuardia: tieneGuardiaDay,
                    guardias: guardiasData,
                });
            }
        }
        // Días del mes siguiente
        for (let i = 0; days.length % 7; i++) {
            let d = new Date(
                month == 11 ? year + 1 : year,
                (month + 1) % 12,
                i + 1,
            );
            if (i == 0) {
                days.push({
                    name: nextMonthAbbrev + " " + (i + 1),
                    enabled: false,
                    date: d,
                    isToday: false,
                    isFeriado: false,
                    feriado: null,
                    tieneGuardia: false,
                    guardias: [],
                });
            } else {
                days.push({
                    name: "" + (i + 1),
                    enabled: false,
                    date: d,
                    isToday: false,
                    isFeriado: false,
                    feriado: null,
                    tieneGuardia: false,
                    guardias: [],
                });
            }
        }
    }
    function dayClick(day) {
        if (!day.enabled) return;
        dispatch("dayclick", {
            date: day.date,
            isFeriado: day.isFeriado,
            feriado: day.feriado, // Primer feriado (compatibilidad)
            feriados: day.feriados || [], // Todos los feriados del día
            tieneGuardia: day.tieneGuardia,
            guardias: day.guardias,
        });
    }
    function showAllGuardias(fecha, guardias) {
        guardiasModalData = {
            fecha: fecha,
            guardias: guardias,
        };
        showGuardiasModal = true;
    }
    function closeGuardiasModal() {
        showGuardiasModal = false;
        guardiasModalData = {
            fecha: null,
            guardias: [],
        };
    }
    function formatFecha(fecha) {
        if (!fecha) return "";
        const date = new Date(fecha);
        return date.toLocaleDateString("es-ES", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
        });
    }
    function next() {
        month++;
        if (month == 12) {
            year++;
            month = 0;
        }
    }
    function prev() {
        if (month == 0) {
            month = 11;
            year--;
        } else {
            month--;
        }
    }
</script>
<div class="calendar-container">
    <div class="calendar-header">
        <h1>
            <button on:click={() => year--}>&lt;&lt;</button>
            <button on:click={() => prev()}>&lt;</button>
            {monthNames[month]}
            {year}
            <button on:click={() => next()}>&gt;</button>
            <button on:click={() => year++}>&gt;&gt;</button>
        </h1>
    </div>
    <div class="calendar-grid-wrapper">
        <div class="calendar-grid">
            <div class="calendar-header-row">
                {#each headers as header}
                    <div class="calendar-header-cell">{header}</div>
                {/each}
            </div>
            <div class="calendar-body">
                {#each days as day}
                    <div
                        class="calendar-day"
                        class:disabled={!day.enabled}
                        class:today={day.isToday}
                        class:feriado={day.isFeriado}
                        class:guardia={day.tieneGuardia}
                        on:click={() => dayClick(day)}
                        on:keydown={(e) => e.key === "Enter" && dayClick(day)}
                        role="button"
                        tabindex="0"
                    >
                        <div class="day-number">{day.name}</div>
                        {#if day.isFeriado}
                            <div class="feriado-info">
                                {#if day.feriados && day.feriados.length > 0}
                                    <!-- Mostrar todos los feriados -->
                                    {#each day.feriados as feriado}
                                        <div class="feriado-item">
                                            <div class="feriado-nombre">
                                                {feriado.nombre}
                                            </div>
                                            {#if feriado.es_multiples_dias}
                                                <div class="feriado-duracion">
                                                    {feriado.duracion_dias} días
                                                </div>
                                            {/if}
                                            <div class="feriado-tipo">
                                                {feriado.tipo_feriado}
                                            </div>
                                        </div>
                                    {/each}
                                {:else if day.feriado}
                                    <!-- Compatibilidad con formato anterior -->
                                    <div class="feriado-item">
                                        <div class="feriado-nombre">
                                            {day.feriado.nombre}
                                        </div>
                                        {#if day.feriado.es_multiples_dias}
                                            <div class="feriado-duracion">
                                                {day.feriado.duracion_dias} días
                                            </div>
                                        {/if}
                                        <div class="feriado-tipo">
                                            {day.feriado.tipo_feriado}
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        {/if}
                        {#if day.tieneGuardia && day.guardias.length > 0}
                            <div class="guardias-info">
                                {#each day.guardias.slice(0, 1) as guardia}
                                    <div class="guardia-item">
                                        <div class="guardia-tipo">
                                            <span class="g-icon">🚨</span>
                                            <span class="g-text">{guardia.tipo || "Guardia"}</span>
                                        </div>
                                        <div class="guardia-horario">
                                            {guardia.hora_inicio?.slice(0, 5)} -
                                            {guardia.hora_fin?.slice(0, 5)}
                                        </div>
                                        {#if guardia.es_multiples_dias || guardia.hora_inicio > guardia.hora_fin}
                                            <div class="guardia-duracion">
                                                2 días
                                            </div>
                                        {/if}
                                        {#if guardia.agente_nombre}
                                            <div class="guardia-agente">
                                                {guardia.agente_nombre}
                                            </div>
                                        {/if}
                                        {#if guardia.cantidad && guardia.cantidad > 1}
                                            <div class="guardia-cantidad">
                                                ({guardia.cantidad} agentes)
                                            </div>
                                        {/if}
                                    </div>
                                {/each}
                                {#if day.guardias.length > 1}
                                    <div
                                        class="guardias-more"
                                        on:click={() =>
                                            showAllGuardias(
                                                day.date,
                                                day.guardias,
                                            )}
                                        on:keydown={(e) =>
                                            e.key === "Enter" &&
                                            showAllGuardias(
                                                day.date,
                                                day.guardias,
                                            )}
                                        role="button"
                                        tabindex="0"
                                    >
                                        +{day.guardias.length - 1} más
                                    </div>
                                {/if}
                            </div>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    </div>
</div>
<!-- Modal de Guardias -->
{#if showGuardiasModal}
    <div
        class="modal-overlay"
        on:click={closeGuardiasModal}
        on:keydown={(e) => e.key === "Escape" && closeGuardiasModal()}
        role="button"
        tabindex="0"
    >
        <div
            class="modal-content"
            on:click|stopPropagation
            on:keydown|stopPropagation
            role="dialog"
            tabindex="-1"
        >
            <div class="modal-header">
                <h3>Guardias del día</h3>
                <button
                    class="modal-close"
                    on:click={closeGuardiasModal}
                    aria-label="Cerrar modal">×</button
                >
            </div>
            <div class="modal-body">
                <p class="modal-fecha">
                    {formatFecha(guardiasModalData.fecha)}
                </p>
                <div class="guardias-list">
                    {#each guardiasModalData.guardias as guardia, index}
                        <div class="guardia-detail">
                            <div class="guardia-header">
                                <span class="guardia-numero">#{index + 1}</span>
                                <span class="guardia-tipo-modal"
                                    >🚨 {guardia.tipo || "Guardia"}</span
                                >
                            </div>
                            <div class="guardia-info-modal">
                                <div class="guardia-horario-modal">
                                    <strong>Horario:</strong>
                                    {guardia.hora_inicio?.slice(0, 5)} - {guardia.hora_fin?.slice(
                                        0,
                                        5,
                                    )}
                                    {#if guardia.es_multiples_dias || guardia.hora_inicio > guardia.hora_fin}
                                        <span class="guardia-duracion-modal"
                                            >(2 días)</span
                                        >
                                    {/if}
                                </div>
                                {#if guardia.agente_nombre}
                                    <div class="guardia-agente-modal">
                                        <strong>Agente:</strong>
                                        {guardia.agente_nombre}
                                        {guardia.agente_apellido || ""}
                                    </div>
                                {/if}
                                {#if guardia.area_nombre}
                                    <div class="guardia-area-modal">
                                        <strong>Área:</strong>
                                        {guardia.area_nombre}
                                    </div>
                                {/if}
                                {#if guardia.observaciones}
                                    <div class="guardia-observaciones-modal">
                                        <strong>Observaciones:</strong>
                                        {guardia.observaciones}
                                    </div>
                                {/if}
                                {#if guardia.cantidad && guardia.cantidad > 1}
                                    <div class="guardia-cantidad-modal">
                                        <strong>Agentes:</strong>
                                        {guardia.cantidad} agentes
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
{/if}
<style>
    :global(*) {
        color-scheme: light only !important;
        -webkit-color-scheme: light !important;
    }
    .calendar-container {
        width: 100%;
        margin: auto;
        overflow: hidden;
        box-shadow: none;
        border-radius: 12px;
        background: transparent;
        border: none;
        max-width: 100%;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        box-sizing: border-box;
        min-width: 0;
    }
    @media (min-width: 768px) {
        .calendar-container {
            border-radius: 16px;
        }
    }
    @media (min-width: 1200px) {
        .calendar-container {
            max-width: 1200px;
        }
    }
    .calendar-header {
        text-align: center;
        padding: 12px 8px;
        background: linear-gradient(
            135deg,
            rgba(231, 144, 67, 0.85) 0%,
            rgba(255, 139, 50, 0.85) 100%
        ) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        color: white !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        box-shadow:
            inset 0 1px 2px rgba(255, 255, 255, 0.3),
            0 2px 10px rgba(231, 144, 67, 0.2);
    }
    @media (min-width: 640px) {
        .calendar-header {
            padding: 16px 0;
        }
    }
    @media (min-width: 768px) {
        .calendar-header {
            padding: 20px 0;
            border-radius: 16px;
        }
    }
    .calendar-header h1 {
        margin: 0;
        font-size: 13px;
        color: white !important;
    }
    @media (min-width: 640px) {
        .calendar-header h1 {
            font-size: 20px;
        }
    }
    @media (min-width: 768px) {
        .calendar-header h1 {
            font-size: 22px;
        }
    }
    .calendar-header button {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 4px 6px;
        color: white !important;
        cursor: pointer;
        outline: 0;
        border-radius: 4px;
        margin: 0 2px;
        transition: all 0.2s ease;
        font-size: 11px;
    }
    @media (min-width: 640px) {
        .calendar-header button {
            padding: 8px 12px;
            border-radius: 8px;
            margin: 0 5px;
            font-size: 16px;
        }
    }
    .calendar-header button:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    .calendar-grid-wrapper {
        overflow-x: auto;
        width: 100%;
        scrollbar-width: thin;
        scrollbar-color: #c1c7cd #f1f3f4;
    }
    .calendar-grid-wrapper::-webkit-scrollbar {
        height: 8px; 
        display: block;
    }
    .calendar-grid-wrapper::-webkit-scrollbar-track {
        background: #f1f3f4;
        border-radius: 4px;
    }
    .calendar-grid-wrapper::-webkit-scrollbar-thumb {
        background-color: #c1c7cd;
        border-radius: 4px;
        border: 2px solid #f1f3f4;
    }
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 0;
        background: transparent;
        padding: 0;
        min-width: 280px; 
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    }
    .calendar-header-row {
        display: contents;
    }
    .calendar-header-cell {
        text-align: center;
        font-weight: bold;
        padding: 6px 2px;
        margin: 1px;
        background: linear-gradient(
            135deg,
            rgba(142, 182, 228, 0.5) 0%,
            rgba(61, 151, 255, 0.45) 100%
        ) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        color: rgba(0, 0, 0, 0.63) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.062);
        border-radius: 6px;
        box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.3);
        font-size: 10px;
    }
    @media (min-width: 640px) {
        .calendar-header-cell {
            padding: 12px 8px;
            margin: 3px;
            border-radius: 10px;
            font-size: 13px;
        }
    }
    @media (min-width: 768px) {
        .calendar-header-cell {
            padding: 15px;
            margin: 4px;
            border-radius: 12px;
            font-size: 14px;
        }
    }
    .calendar-body {
        display: contents;
    }
    .calendar-day {
        text-align: left;
        padding: 3px;
        background: white !important;
        background-color: #ffffff !important;
        min-height: 50px;
        transition: all 0.2s ease;
        border: 1px solid #f0f0f0;
        border-radius: 6px;
        margin: 1px;
        display: flex;
        flex-direction: column;
        position: relative;
        box-sizing: border-box;
        min-width: 0;
        width: 100%;
        max-width: 100%;
    }
    @media (min-width: 480px) {
        .calendar-day {
            min-height: 80px;
            padding: 6px;
            margin: 3px;
        }
    }
    @media (min-width: 640px) {
        .calendar-day {
            min-height: 100px;
            padding: 8px;
            margin: 4px;
            border-radius: 10px;
        }
    }
    @media (min-width: 768px) {
        .calendar-day {
            min-height: 120px;
            border-radius: 12px;
        }
    }
    .calendar-day:not(.disabled):hover {
        background: #fef6ee;
        cursor: pointer;
        border-color: #e79043;
        transform: scale(1.02);
    }
    .calendar-day.disabled {
        background: rgba(250, 250, 250, 0.5) !important;
        color: rgba(204, 204, 204, 0.6) !important;
        border-radius: 8px;
        border-color: rgba(240, 240, 240, 0.5);
        opacity: 0.6;
    }
    @media (min-width: 640px) {
        .calendar-day.disabled {
            border-radius: 12px;
        }
    }
    .calendar-day.today {
        background: #e7904396 !important;
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }
    @media (min-width: 640px) {
        .calendar-day.today {
            border-radius: 12px;
        }
    }
    .calendar-day.today:hover {
        background: #f07f29c7;
        transform: scale(1.02);
    }
    .calendar-day.feriado {
        background: #ffe6e6 !important;
        border-color: #ff9999 !important;
        border-radius: 8px;
    }
    @media (min-width: 640px) {
        .calendar-day.feriado {
            border-radius: 12px;
        }
    }
    .calendar-day.feriado:hover {
        background: #ffcccc !important;
        transform: scale(1.02);
    }
    .calendar-day.today.feriado {
        background: linear-gradient(
            135deg,
            #e65c5c 0%,
            #cc0000 100%
        ) !important;
        border: none;
        border-radius: 8px;
    }
    @media (min-width: 640px) {
        .calendar-day.today.feriado {
            border-radius: 12px;
        }
    }
    .day-number {
        font-weight: 600;
        margin-bottom: 1px;
        color: rgba(0, 0, 0, 0.63) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.062);
        font-size: 10px;
    }
    @media (min-width: 640px) {
        .day-number {
            margin-bottom: 4px;
            font-size: 14px;
        }
    }
    .feriado-info {
        font-size: 0.5rem;
        line-height: 1.1;
        flex-grow: 1;
    }
    @media (min-width: 640px) {
        .feriado-info {
            font-size: 0.75rem;
        }
    }
    .feriado-item {
        margin-bottom: 1px;
        padding: 1px;
        border-left: 1px solid #d63384;
        padding-left: 2px;
    }
    .feriado-item:last-child {
        margin-bottom: 0;
    }
    .feriado-nombre {
        font-weight: 500;
        color: #d63384 !important;
        margin-bottom: 1px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 0.5rem;
    }
    @media (min-width: 640px) {
        .feriado-nombre {
            font-size: 0.7rem;
        }
    }
    .feriado-duracion {
        font-size: 0.45rem;
        color: #28a745 !important;
        font-weight: 600;
        margin-bottom: 0px;
    }
    @media (min-width: 640px) {
        .feriado-duracion {
            font-size: 0.65rem;
        }
    }
    .feriado-tipo {
        font-size: 0.45rem;
        color: #6c757d !important;
        font-style: italic;
        display: none;
    }
    @media (min-width: 640px) {
        .feriado-tipo {
            font-size: 0.65rem;
        }
    }
    .calendar-day.today .feriado-nombre {
        color: white !important;
    }
    .calendar-day.today .feriado-duracion {
        color: #90ee90 !important;
    }
    .calendar-day.today .feriado-tipo {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    .calendar-day.guardia {
        background: #e6f3ff !important;
        border-color: #4a90e2 !important;
        border-radius: 8px;
    }
    @media (min-width: 640px) {
        .calendar-day.guardia {
            border-radius: 12px;
        }
    }
    .calendar-day.guardia:hover {
        background: #cce7ff !important;
        transform: scale(1.02);
    }
    .calendar-day.today.guardia {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        border: none;
        border-radius: 12px;
    }
    .calendar-day.feriado.guardia {
        background: #ffe0e6;
        border-color: #dc3545;
        border-radius: 12px;
    }
    .guardias-info {
        font-size: 0.75rem;
        line-height: 1.2;
        flex-grow: 1;
        margin-top: 2px;
    }
    .guardia-item {
        margin-bottom: 2px;
        padding: 2px 4px;
        background: rgba(37, 99, 235, 0.1);
        border-radius: 4px;
        border-left: 3px solid #2563eb;
    }
    .guardia-tipo {
        font-weight: 500;
        color: #2563eb;
        font-size: 0.7rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    @media (max-width: 768px) {
        .g-text { display: none; }
        .guardia-horario { display: none; }
        .guardia-agente { display: none; }
        .guardia-duracion { display: none !important; }
        .guardia-cantidad { display: none; }
        .guardia-item {
            justify-content: center;
            text-align: center;
            padding: 2px 0;
        }
        .guardia-tipo {
            justify-content: center;
            font-size: 1rem; 
        }
    }
    .guardia-horario {
        font-size: 0.65rem;
        color: #475569;
        font-style: italic;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .guardia-agente {
        font-size: 0.65rem;
        color: #374151;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .guardia-cantidad {
        font-size: 0.6rem;
        color: #2563eb;
        font-weight: 600;
        background: rgba(37, 99, 235, 0.2);
        padding: 1px 4px;
        border-radius: 8px;
    }
    .guardia-duracion {
        font-size: 0.6rem;
        color: #dc2626;
        font-weight: 600;
        margin-bottom: 1px;
    }
    .guardias-more {
        font-size: 0.65rem;
        color: #6366f1;
        font-weight: 600;
        text-align: center;
        padding: 2px 4px;
        background: rgba(99, 102, 241, 0.15);
        border-radius: 4px;
        margin-top: 2px;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    .guardias-more:hover {
        background: rgba(99, 102, 241, 0.25);
    }
    .calendar-day.today .guardia-tipo {
        color: white;
    }
    .calendar-day.today .guardia-horario,
    .calendar-day.today .guardia-agente {
        color: rgba(255, 255, 255, 0.8);
    }
    .calendar-day.today .guardia-cantidad {
        background-color: rgba(255, 255, 255, 0.3);
        color: white;
    }
    .calendar-day.today .guardia-item {
        background-color: rgba(255, 255, 255, 0.2);
        border-left-color: white;
    }
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .modal-content {
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        background: #f9fafb;
    }
    .modal-header h3 {
        margin: 0;
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 600;
    }
    .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        color: #6b7280;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 4px;
        transition: background-color 0.2s ease;
    }
    .modal-close:hover {
        background-color: #e5e7eb;
        color: #374151;
    }
    .modal-body {
        padding: 1.5rem;
        overflow-y: auto;
        flex: 1;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    .modal-body::-webkit-scrollbar {
        display: none;
    }
    .modal-fecha {
        font-size: 1.1rem;
        color: #374151;
        margin-bottom: 1.5rem;
        text-align: center;
        background: #f3f4f6;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 500;
        text-transform: capitalize;
    }
    .guardias-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .guardia-detail {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
        background: #fefefe;
    }
    .guardia-header {
        background: #f8fafc;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .guardia-numero {
        background: #6366f1;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        min-width: 24px;
        text-align: center;
    }
    .guardia-tipo-modal {
        font-weight: 600;
        color: #374151;
        font-size: 0.95rem;
    }
    .guardia-info-modal {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .guardia-horario-modal,
    .guardia-agente-modal,
    .guardia-area-modal,
    .guardia-observaciones-modal,
    .guardia-cantidad-modal {
        font-size: 0.9rem;
        color: #374151;
    }
    .guardia-duracion-modal {
        color: #dc2626;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .guardia-info-modal strong {
        color: #1f2937;
        font-weight: 600;
    }
    @media (max-width: 480px) {
        .calendar-grid {
            gap: 0;
        }
        .calendar-day:not(.disabled):hover {
            transform: scale(1);
        }
    }
    @media (max-width: 640px) {
        .modal-content {
            width: 95%;
            max-height: 90vh;
        }
        .modal-header {
            padding: 1rem;
        }
        .modal-body {
            padding: 1rem;
        }
        .guardia-info-modal {
            padding: 0.75rem;
        }
    }
</style>
