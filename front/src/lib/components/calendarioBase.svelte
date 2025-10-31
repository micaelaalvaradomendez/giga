<script>
    import { createEventDispatcher, onMount } from "svelte";

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
    let eventText = "Click an item or date";

    var days = [];

    function randInt(max) {
        return Math.floor(Math.random() * max) + 1;
    }

    var items = [];

    function initMonthItems() {
        let y = year;
        let m = month;
        let d1 = new Date(y, m, randInt(7) + 7);
        items = [
            {
                title: "11:00 Task Early in month",
                className: "task--primary",
                date: new Date(y, m, randInt(6)),
                len: randInt(4) + 1,
            },
            {
                title: "7:30 Wk 2 tasks",
                className: "task--warning",
                date: d1,
                len: randInt(4) + 2,
            },
            {
                title: "Overlapping Stuff (isBottom:true)",
                date: d1,
                className: "task--info",
                len: 4,
                isBottom: true,
            },
            {
                title: "10:00 More Stuff to do",
                date: new Date(y, m, randInt(7) + 14),
                className: "task--info",
                len: randInt(4) + 1,
                detailHeader: "Difficult",
                detailContent: "But not especially so",
            },
            {
                title: "All day task",
                date: new Date(y, m, randInt(7) + 21),
                className: "task--danger",
                len: 1,
                vlen: 2,
            },
        ];

        for (let i of items) {
            let rc = findRowCol(i.date);
            if (rc == null) {
                console.log("didn`t find date for ", i);
                console.log(i.date);
                console.log(days);
                i.startCol = i.startRow = 0;
            } else {
                i.startCol = rc.col;
                i.startRow = rc.row;
            }
        }
    }

    $: month, year, initContent();

    function initContent() {
        headers = dayNames;
        initMonth();
        initMonthItems();
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
            });
        }
        for (let i = 0; i < daysInThisMonth; i++) {
            let d = new Date(year, month, i + 1);
            let isToday =
                d.getDate() == today.getDate() &&
                d.getMonth() == today.getMonth() &&
                d.getFullYear() == today.getFullYear();
            if (i == 0)
                days.push({
                    name: monthAbbrev + " " + (i + 1),
                    enabled: true,
                    date: d,
                    isToday: isToday,
                });
            else
                days.push({
                    name: "" + (i + 1),
                    enabled: true,
                    date: d,
                    isToday: isToday,
                });
        }
        for (let i = 0; days.length % 7; i++) {
            let d = new Date(
                month == 11 ? year + 1 : year,
                (month + 1) % 12,
                i + 1,
            );
            if (i == 0)
                days.push({
                    name: nextMonthAbbrev + " " + (i + 1),
                    enabled: false,
                    date: d,
                    isToday: false,
                });
            else
                days.push({
                    name: "" + (i + 1),
                    enabled: false,
                    date: d,
                    isToday: false,
                });
        }
    }

    function findRowCol(dt) {
        for (let i = 0; i < days.length; i++) {
            let d = days[i].date;
            if (
                d.getYear() === dt.getYear() &&
                d.getMonth() === dt.getMonth() &&
                d.getDate() === dt.getDate()
            )
                return { row: Math.floor(i / 7) + 2, col: (i % 7) + 1 };
        }
        return null;
    }

    function itemClick(e) {
        eventText =
            "itemClick " +
            JSON.stringify(e) +
            " localtime=" +
            e.date.toString();
    }
    function dayClick(e) {
        eventText =
            "onDayClick " +
            JSON.stringify(e) +
            " localtime=" +
            e.date.toString();
    }
    function headerClick(e) {
        eventText = "onHheaderClick " + JSON.stringify(e);
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
        {eventText}
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
                >
                    {day.name}
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
        text-align: center;
        padding: 20px 10px;
        background-color: white;
        min-height: 120px;
        transition: background-color 0.3s;
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
</style>
