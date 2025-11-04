<script>
    import { createEventDispatcher, onMount } from "svelte";

    export let feriados = [];

    const dayNames = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
    const monthNames = [
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

    const dispatch = createEventDispatcher();

    let now = new Date();
    let year = now.getFullYear();
    let month = now.getMonth();
    
    let days = [];
    let feriadosMap = new Map();

    // Función para obtener la fecha en formato YYYY-MM-DD, ignorando la zona horaria
    function toISODateString(date) {
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    }

    // Bloque reactivo: se ejecuta cada vez que la prop 'feriados' cambia
    $: {
        feriadosMap.clear();
        if (feriados && feriados.length > 0) {
            for (const feriado of feriados) {
                feriadosMap.set(feriado.fecha, feriado.descripcion);
            }
        }
        if (days.length > 0) {
            initMonth(); // Redibuja el calendario si ya estaba visible
        }
    }

    // Bloque reactivo: se ejecuta cuando 'month' o 'year' cambian
    $: month, year, initMonth();

    onMount(() => {
        initMonth();
    });

    function initMonth() {
        days = [];
        const firstDayOfMonth = new Date(year, month, 1);
        const firstDayOfWeek = firstDayOfMonth.getDay();
        const daysInThisMonth = new Date(year, month + 1, 0).getDate();
        const prevMonthDate = new Date(year, month, 0);
        const daysInLastMonth = prevMonthDate.getDate();
        let today = new Date();

        // Días del mes anterior
        for (let i = firstDayOfWeek; i > 0; i--) {
            const dayNum = daysInLastMonth - i + 1;
            let d = new Date(
                prevMonthDate.getFullYear(),
                prevMonthDate.getMonth(),
                dayNum,
            );
            days.push({ name: String(dayNum), enabled: false, date: d });
        }

        // Días del mes actual
        for (let i = 1; i <= daysInThisMonth; i++) {
            const d = new Date(year, month, i);
            const dateString = toISODateString(d);
            const isToday = toISODateString(today) === dateString;
            const esFeriado = feriadosMap.has(dateString);

            days.push({
                name: String(i),
                enabled: true,
                date: d,
                isToday: isToday,
                isFeriado: esFeriado,
                feriadoNombre: esFeriado ? feriadosMap.get(dateString) : null,
            });
        }

        // Días del mes siguiente
        const nextMonthDate = new Date(year, month + 1, 1);
        while (days.length % 7 !== 0) {
            const dayNum = days.length - (firstDayOfWeek + daysInThisMonth) + 1;
            const d = new Date(nextMonthDate.getFullYear(), nextMonthDate.getMonth(), dayNum);
            days.push({ name: String(dayNum), enabled: false, date: d });
        }
    }

    function next() {
        month++;
        if (month == 12) {
            year++;
            month = 0;
        }
    }
    function prev() {
        month--;
        if (month === -1) {
            year--;
            month = 11;
        }
    }

    function handleDayClick(day) {
        if (!day.enabled) return; // No hacer nada en días deshabilitados

        // Despachar (emitir) el evento 'dayclick' con la información del día
        dispatch('dayclick', {
            date: day.date,
            isFeriado: day.isFeriado,
            feriado: day.isFeriado ? feriados.find(f => f.fecha === toISODateString(day.date)) : null
        });
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
            {#each dayNames as header}
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
                    on:click={() => handleDayClick(day)}
                >
                    <div class="day-number">{day.name}</div>
                    {#if day.isFeriado}
                        <div class="feriado-name">{day.feriadoNombre}</div>
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
        padding: 10px;
        background-color: white;
        min-height: 100px;
        transition: background-color 0.3s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
    }
    .calendar-day.today .day-number {
        font-weight: bold;
    }
    .day-number {
        align-self: flex-start;
        font-size: 0.9rem;
    }
    .feriado {
        background-color: #b3e5fc;
        border: 1px solid #81d4fa;
    }
    .feriado-name {
        font-size: 0.85rem; 
        font-weight: 600; 
        color: #01579b; 
        align-self: center;
        text-align: center;
        padding: 3px 5px;
        background-color: rgba(255, 255, 255, 0.6);
        border-radius: 5px;
    }
</style>
