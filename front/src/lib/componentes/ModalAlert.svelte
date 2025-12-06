<script>
    import { fade, scale } from "svelte/transition";
    import { createEventDispatcher } from "svelte";

    export let show = false;
    export let type = "info"; // 'info', 'success', 'warning', 'error'
    export let title = "";
    export let message = "";
    export let duration = 0; // 0 = no auto-close
    export let showConfirmButton = true;
    export let confirmText = "Aceptar";
    export let showCancelButton = false;
    export let cancelText = "Cancelar";

    let timer;

    $: if (show && duration > 0) {
        clearTimeout(timer);
        timer = setTimeout(() => {
            show = false;
        }, duration);
    }

    function confirm() {
        dispatch("confirm");
        show = false;
    }

    function cancel() {
        dispatch("cancel");
        show = false;
    }

    function close() {
        dispatch("close");
        show = false;
    }

    const dispatch = createEventDispatcher();
</script>

{#if show}
    <div class="modal-overlay" transition:fade>
        <div class="modal-alert" transition:scale={{ duration: 200, start: 0.9 }}>
            <div class="alert-content">
                <div class="alert-icon {type}">
                    {#if type === "success"}
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    {:else if type === "warning"}
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                    {:else if type === "error"}
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="15" y1="9" x2="9" y2="15"></line>
                            <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                    {:else}
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="16" x2="12" y2="12"></line>
                            <line x1="12" y1="8" x2="12.01" y2="8"></line>
                        </svg>
                    {/if}
                </div>
                
                <h3 class="alert-title">{title}</h3>
                <p class="alert-message">{message}</p>

                <div class="alert-actions">
                    {#if showCancelButton}
                        <button class="btn-cancel" on:click={cancel}>
                            {cancelText}
                        </button>
                    {/if}
                    {#if showConfirmButton}
                        <button class="btn-confirm" on:click={confirm}>
                            {confirmText}
                        </button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(2px);
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .modal-alert {
        background: white;
        border-radius: 20px;
        width: 400px;
        max-width: 90vw;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        overflow: hidden;
        padding: 2rem;
        text-align: center;
    }

    .alert-content {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .alert-icon {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
        border: 4px solid transparent;
    }

    .alert-icon svg {
        width: 40px;
        height: 40px;
    }

    .alert-icon.success {
        color: #10b981;
        border-color: #d1fae5;
        background-color: #ecfdf5;
    }

    .alert-icon.warning {
        color: #f59e0b;
        border-color: #fde68a;
        background-color: #fffbeb;
    }

    .alert-icon.error {
        color: #ef4444;
        border-color: #fee2e2;
        background-color: #fef2f2;
    }

    .alert-icon.info {
        color: #3b82f6;
        border-color: #dbeafe;
        background-color: #eff6ff;
    }

    .alert-title {
        margin: 0 0 0.5rem 0;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
    }

    .alert-message {
        margin: 0 0 2rem 0;
        color: #6b7280;
        font-size: 1rem;
        line-height: 1.5;
    }

    .alert-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        width: 100%;
    }

    .btn-confirm,
    .btn-cancel {
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 1rem;
        min-width: 120px;
    }

    .btn-confirm {
        background: #3b82f6;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
    }

    .btn-confirm:hover {
        background: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px -1px rgba(59, 130, 246, 0.6);
    }

    .btn-cancel {
        background: #f3f4f6;
        color: #4b5563;
    }

    .btn-cancel:hover {
        background: #e5e7eb;
    }
</style>
