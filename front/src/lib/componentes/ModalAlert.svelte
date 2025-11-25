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
        <div class="modal-alert" transition:scale={{ duration: 200 }}>
            <div class="alert-header alert-{type}">
                <div class="alert-icon">
                    {#if type === "success"}
                        ✅
                    {:else if type === "warning"}
                        ⚠️
                    {:else if type === "error"}
                        ❌
                    {:else}
                        ℹ️
                    {/if}
                </div>
                <h3>{title}</h3>
                <button class="alert-close" on:click={close}>×</button>
            </div>

            <div class="alert-body">
                <p>{message}</p>
            </div>

            <div class="alert-footer">
                {#if showCancelButton}
                    <button class="btn-cancel" on:click={cancel}>
                        {cancelText}
                    </button>
                {/if}
                {#if showConfirmButton}
                    <button class="btn-confirm btn-{type}" on:click={confirm}>
                        {confirmText}
                    </button>
                {/if}
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
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }

    .modal-alert {
        background: white;
        border-radius: 16px;
        width: 400px;
        max-width: 90vw;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    }

    .alert-header {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        color: white;
        position: relative;
    }

    .alert-header.alert-success {
        background: linear-gradient(135deg, #10b981, #059669);
    }

    .alert-header.alert-error {
        background: linear-gradient(135deg, #ef4444, #dc2626);
    }

    .alert-header.alert-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    .alert-header.alert-info {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    }

    .alert-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
    }

    .alert-header h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        flex: 1;
    }

    .alert-close {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        font-size: 1.5rem;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }

    .alert-close:hover {
        background: rgba(255, 255, 255, 0.3);
    }

    .alert-body {
        padding: 1.5rem;
    }

    .alert-body p {
        margin: 0;
        color: #374151;
        line-height: 1.5;
        font-size: 1rem;
    }

    .alert-footer {
        display: flex;
        gap: 0.75rem;
        justify-content: flex-end;
        padding: 1rem 1.5rem 1.5rem;
    }

    .btn-confirm,
    .btn-cancel {
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.875rem;
    }

    .btn-confirm {
        color: white;
    }

    .btn-confirm.btn-success {
        background: #10b981;
    }

    .btn-confirm.btn-error {
        background: #ef4444;
    }

    .btn-confirm.btn-warning {
        background: #f59e0b;
    }

    .btn-confirm.btn-info {
        background: #3b82f6;
    }

    .btn-confirm:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    .btn-cancel {
        background: #6b7280;
        color: white;
    }

    .btn-cancel:hover {
        background: #4b5563;
        transform: translateY(-1px);
    }
</style>
