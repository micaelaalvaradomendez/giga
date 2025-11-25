<script>
    import { createEventDispatcher } from "svelte";

    export let show = false;
    export let guardia = null;
    export let notaTexto = "";
    export let notaId = null;
    export let guardandoNota = false;

    const dispatch = createEventDispatcher();

    function cerrarModal() {
        dispatch("cerrar");
    }

    function guardar() {
        dispatch("guardar", { notaTexto, notaId });
    }

    function eliminar() {
        dispatch("eliminar", { notaId });
    }

    function formatearFecha(fecha) {
        const f = new Date(fecha);
        const dias = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
        const meses = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ];
        return `${dias[f.getDay()]} ${f.getDate()} ${meses[f.getMonth()]} ${f.getFullYear()}`;
    }
</script>

{#if show && guardia}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={cerrarModal}>
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="modal-glass" on:click|stopPropagation>
            <div class="modal-header">
                <h2>{notaId ? "📝 Editar nota" : "➕ Nueva nota"}</h2>
                <button class="btn-close" on:click={cerrarModal}>✕</button>
            </div>

            <div class="modal-body">
                <div class="guardia-info">
                    <p>
                        <strong>Fecha:</strong>
                        {formatearFecha(guardia.fecha)}
                    </p>
                    <p>
                        <strong>Horario:</strong>
                        {guardia.hora_inicio} - {guardia.hora_fin}
                    </p>
                    <p><strong>Tipo:</strong> {guardia.tipo}</p>
                </div>

                <label for="nota-texto">Nota personal:</label>
                <textarea
                    id="nota-texto"
                    bind:value={notaTexto}
                    placeholder="Escribe tus observaciones sobre esta guardia..."
                    rows="6"
                    disabled={guardandoNota}
                ></textarea>
            </div>

            <div class="modal-footer">
                {#if notaId}
                    <button
                        class="btn-danger"
                        on:click={eliminar}
                        disabled={guardandoNota}
                    >
                        🗑️ Eliminar
                    </button>
                {/if}
                <button
                    class="btn-secondary"
                    on:click={cerrarModal}
                    disabled={guardandoNota}
                >
                    Cancelar
                </button>
                <button
                    class="btn-primary"
                    on:click={guardar}
                    disabled={guardandoNota || !notaTexto.trim()}
                >
                    {guardandoNota ? "Guardando..." : "Guardar"}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    }

    .modal-glass {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 20px;
        max-width: 600px;
        width: 100%;
        max-height: 90vh;
        overflow: auto;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .modal-header h2 {
        margin: 0;
        color: #173263;
        font-size: 1.5rem;
    }

    .btn-close {
        background: none;
        border: none;
        color: rgba(0, 0, 0, 0.6);
        font-size: 1.5rem;
        font-weight: 600;
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        transition: color 0.3s ease;
    }

    .btn-close:hover {
        color: #000000;
    }

    .modal-body {
        padding: 2rem;
    }

    .guardia-info {
        background: rgba(23, 50, 99, 0.08);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(23, 50, 99, 0.15);
    }

    .guardia-info p {
        margin: 0.5rem 0;
        color: rgba(0, 0, 0, 0.85);
    }

    .guardia-info strong {
        color: #173263;
        font-weight: 600;
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
        color: rgba(0, 0, 0, 0.8);
        font-weight: 600;
    }

    textarea {
        width: 100%;
        padding: 1rem;
        background: rgb(255, 255, 255);
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        color: #000000;
        font-family: inherit;
        font-size: 1rem;
        resize: vertical;
        box-sizing: border-box;
    }

    textarea:focus {
        outline: none;
        border-color: #407bff;
        box-shadow: 0 0 0 3px rgba(64, 123, 255, 0.15);
    }

    textarea:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        padding: 1.5rem 2rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }

    .btn-primary,
    .btn-secondary,
    .btn-danger {
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
    }

    .btn-primary {
        background: linear-gradient(135deg, #407bff 0%, #0052cc 100%);
        color: #fff;
    }

    .btn-primary:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(64, 123, 255, 0.4);
    }

    .btn-primary:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.8);
    }

    .btn-secondary:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.15);
        color: #fff;
    }

    .btn-danger {
        background: rgba(244, 67, 54, 0.2);
        border: 1px solid rgba(244, 67, 54, 0.4);
        color: #f44336;
    }

    .btn-danger:hover:not(:disabled) {
        background: rgba(244, 67, 54, 0.3);
        transform: translateY(-2px);
    }
</style>
