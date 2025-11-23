<script>
    import { onMount } from "svelte";
    import { browser } from "$app/environment";
    import { goto } from "$app/navigation";
    import CalendarioBase from "$lib/componentes/calendarioBase.svelte";
    import ModalGestionFeriado from "$lib/componentes/ModalGestionFeriado.svelte";
    import { feriadosController } from "$lib/paneladmin/controllers";

    // Stores del controlador
    const { feriados, loading, error, success, modalGestionFeriado } =
        feriadosController;

    // Inicializar el controlador
    onMount(async () => {
        console.log(
            "🔄 Componente montado, iniciando controlador de feriados...",
        );
        try {
            await feriadosController.init();
            console.log("✅ Controlador de feriados inicializado exitosamente");

            // Recargar cuando la página vuelve a ser visible
            if (browser) {
                const handleVisibilityChange = () => {
                    if (document.visibilityState === "visible") {
                        feriadosController.init();
                    }
                };

                const handleFocus = () => {
                    feriadosController.init();
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
            console.error(
                "❌ Error inicializando controlador de feriados:",
                err,
            );
            if (err.message === "Usuario no autenticado") {
                goto("/");
                return;
            }
        }
    });

    function handleDayClick(event) {
        const { date, isFeriado, feriados } = event.detail;
        const selectedDate = date.toISOString().split("T")[0];
        
        // Obtener feriados existentes en la fecha
        const feriadosEnFecha = feriados || feriadosController.getFeriadosByDate(selectedDate);
        
        // Siempre abrir modal en modo creación para permitir múltiples feriados
        // El modal mostrará los feriados existentes como información
        feriadosController.openModal(selectedDate, null);
    }

    function closeModal() {
        feriadosController.closeModal();
    }
</script>

<div class="admin-page-container">
    <div class="page-header">
        <h1>Gestión de Feriados</h1>
        {#if $error}
            <div class="error-message">{$error}</div>
        {/if}
        {#if $success}
            <div class="success-message">{$success}</div>
        {/if}
    </div>

    <div class="calendar-wrapper">
        {#if $loading}
            <div class="loading">Cargando feriados...</div>
        {:else}
            <CalendarioBase feriados={$feriados} on:dayclick={handleDayClick} />
        {/if}
    </div>
</div>

<ModalGestionFeriado
    bind:isOpen={$modalGestionFeriado.isOpen}
    feriado={$modalGestionFeriado.feriado}
    selectedDate={$modalGestionFeriado.selectedDate}
    isSaving={$modalGestionFeriado.isSaving}
    isDeleting={$modalGestionFeriado.isDeleting}
    existingFeriados={$modalGestionFeriado.existingFeriados || []}
    {feriadosController}
    on:close={closeModal}
/>

<style>
    .admin-page-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .page-header {
        position: relative;
        background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
        color: white;
        padding: 30px 40px;
        max-width: 1200px;
        border-radius: 28px;
        overflow: hidden;
        text-align: center;
        box-shadow:
            0 0 0 1px rgba(255, 255, 255, 0.1) inset,
            0 10px 30px rgba(30, 64, 175, 0.4);
    }

    .page-header::before {
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

    .error-message {
        background-color: #fee;
        color: #c33;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #fcc;
        margin-top: 0.5rem;
        width: 100%;
    }

    .success-message {
        background-color: #efe;
        color: #363;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #cfc;
        margin-top: 0.5rem;
        width: 100%;
    }

    .loading {
        text-align: center;
        padding: 2rem;
        font-style: italic;
        color: #666;
    }

    .page-header h1 {
        margin: 10px;
        font-weight: 800;
        font-size: 30px;
        letter-spacing: 0.2px;
        font-family:
            "Segoe UI",
            system-ui,
            -apple-system,
            "Inter",
            "Roboto",
            "Helvetica Neue",
            Arial,
            sans-serif;
        position: relative;
        padding-bottom: 12px;
        overflow: hidden;
        display: inline-block;
    }

    .page-header h1::after {
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

    .calendar-wrapper {
        width: 100%;
        margin-top: 20px;
    }
</style>
