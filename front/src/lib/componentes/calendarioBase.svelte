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

    // Función para verificar si una fecha es feriado
    function esFeriado(fecha) {
        if (!feriados || feriados.length === 0) return false;
        const fechaStr = fecha.toISOString().split('T')[0];
        return feriados.some(feriado => feriado.fecha === fechaStr);
    }

    // Función para obtener el feriado de una fecha específica
    function getFeriado(fecha) {
        if (!feriados || feriados.length === 0) return null;
        const fechaStr = fecha.toISOString().split('T')[0];
        return feriados.find(feriado => feriado.fecha === fechaStr) || null;
    }

    // Función para verificar si una fecha tiene guardia
    function tieneGuardia(fecha) {
        if (!guardias || guardias.length === 0) return false;
        const fechaStr = fecha.toISOString().split('T')[0];
        return guardias.some(guardia => guardia.fecha === fechaStr);
    }

    // Función para obtener las guardias de una fecha específica
    function getGuardias(fecha) {
        if (!guardias || guardias.length === 0) return [];
        const fechaStr = fecha.toISOString().split('T')[0];
        return guardias.filter(guardia => guardia.fecha === fechaStr);
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
        
        dispatch('dayclick', {
            date: day.date,
            isFeriado: day.isFeriado,
            feriado: day.feriado,
            tieneGuardia: day.tieneGuardia,
            guardias: day.guardias
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
                    on:keydown={(e) => e.key === 'Enter' && dayClick(day)}
                    role="button"
                    tabindex="0"
                >
                    <div class="day-number">{day.name}</div>
                    {#if day.isFeriado && day.feriado}
                        <div class="feriado-info">
                            <div class="feriado-descripcion">{day.feriado.descripcion}</div>
                            <div class="feriado-tipo">{day.feriado.tipo_feriado}</div>
                        </div>
                    {/if}
                    {#if day.tieneGuardia && day.guardias.length > 0}
                        <div class="guardias-info">
                            {#each day.guardias as guardia}
                                <div class="guardia-item">
                                    <div class="guardia-tipo">🚨 {guardia.tipo || 'Guardia'}</div>
                                    <div class="guardia-horario">{guardia.hora_inicio?.slice(0,5)} - {guardia.hora_fin?.slice(0,5)}</div>
                                    {#if guardia.agente_nombre}
                                        <div class="guardia-agente">{guardia.agente_nombre}</div>
                                    {/if}
                                    {#if guardia.cantidad && guardia.cantidad > 1}
                                        <div class="guardia-cantidad">({guardia.cantidad} agentes)</div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    </div>
</div>

<style>
    .calendar-container {
        width: 100%;
        margin: auto;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-radius: 15px;
        background: #fff;
        max-width: 1200px;
    }
    .calendar-header {
        text-align: center;
        padding: 20px 0;
        background: #e79043;
        color: white;
        border-bottom: 1px solid rgba(166, 168, 179, 0.12);
    }
    .calendar-header h1 {
        margin: 0;
        font-size: 22px;
    }
    .calendar-header button {
        background: transparent;
        border: 1px solid white;
        padding: 8px 12px;
        color: white;
        cursor: pointer;
        outline: 0;
        border-radius: 5px;
        margin: 0 5px;
        transition: background-color 0.3s;
    }
    .calendar-header button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 1px;
        background-color: #ddd;
        padding: 1px;
    }
    .calendar-header-row {
        display: contents;
    }
    .calendar-header-cell {
        text-align: center;
        font-weight: bold;
        padding: 15px;
        background-color: #f2f2f2;
    }
    .calendar-body {
        display: contents;
    }
    .calendar-day {
        text-align: left;
        padding: 8px;
        background-color: white;
        min-height: 120px;
        transition: background-color 0.3s;
        border: 1px solid transparent;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    
    .calendar-day:not(.disabled):hover {
        background-color: #ebd4ab;
        cursor: pointer;
    }
    
    .calendar-day.disabled {
        background-color: #f9f9f9;
        color: #ccc;
    }
    
    .calendar-day.today {
        background-color: #e79043;
        color: white;
        font-weight: bold;
    }

    .calendar-day.today:hover {
        background-color: #dfb28a;
    }

    .calendar-day.feriado {
        background-color: #ffe6e6;
        border-color: #ff9999;
    }

    .calendar-day.feriado:hover {
        background-color: #ffcccc;
    }

    .calendar-day.today.feriado {
        background-color: #e65c5c;
        border-color: #cc0000;
    }

    .day-number {
        font-weight: 600;
        margin-bottom: 4px;
    }

    .feriado-info {
        font-size: 0.75rem;
        line-height: 1.2;
        flex-grow: 1;
    }

    .feriado-descripcion {
        font-weight: 500;
        color: #d63384;
        margin-bottom: 2px;
        word-wrap: break-word;
        hyphens: auto;
    }

    .feriado-tipo {
        font-size: 0.65rem;
        color: #6c757d;
        font-style: italic;
    }

    .calendar-day.today .feriado-descripcion {
        color: white;
    }

    .calendar-day.today .feriado-tipo {
        color: rgba(255, 255, 255, 0.8);
    }

    /* Estilos para guardias */
    .calendar-day.guardia {
        background-color: #e6f3ff;
        border-color: #4a90e2;
    }

    .calendar-day.guardia:hover {
        background-color: #cce7ff;
    }

    .calendar-day.today.guardia {
        background-color: #2563eb;
        border-color: #1d4ed8;
    }

    .calendar-day.feriado.guardia {
        background-color: #ffe0e6;
        border-color: #dc3545;
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
        background-color: rgba(37, 99, 235, 0.1);
        border-radius: 3px;
        border-left: 3px solid #2563eb;
    }

    .guardia-tipo {
        font-weight: 500;
        color: #2563eb;
        font-size: 0.7rem;
    }

    .guardia-horario {
        font-size: 0.65rem;
        color: #475569;
        font-style: italic;
    }

    .guardia-agente {
        font-size: 0.65rem;
        color: #374151;
        font-weight: 500;
    }

    .guardia-cantidad {
        font-size: 0.6rem;
        color: #6b7280;
        font-weight: 600;
        background-color: rgba(37, 99, 235, 0.2);
        padding: 1px 4px;
        border-radius: 8px;
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
</style>
