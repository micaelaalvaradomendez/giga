<script>
  import { createEventDispatcher } from "svelte";
  import { fade, scale } from "svelte/transition";
  export let cronograma;
  export let loading = false;
  export let motivoRechazo = "";
  const dispatch = createEventDispatcher();
  function cerrar() {
    dispatch("close");
  }
  function confirmarRechazo() {
    dispatch("confirmar", { motivo: motivoRechazo });
  }
</script>
<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="modal-overlay" on:click={cerrar} transition:fade={{ duration: 200 }}>
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div
    class="modal-content modal-rechazo"
    on:click|stopPropagation
    transition:scale={{ duration: 200, start: 0.95 }}
  >
    <div class="modal-header">
      <h3>Rechazar Cronograma</h3>
      <button class="close-button" on:click={cerrar}>&times;</button>
    </div>
    <div class="modal-body">
      <p>
        <strong>Cronograma:</strong>
        {cronograma?.area_nombre || ""} - {cronograma?.tipo || ""}
      </p>
      <div class="form-group">
        <label for="motivo">Motivo del rechazo *</label>
        <textarea
          id="motivo"
          bind:value={motivoRechazo}
          placeholder="Ingrese el motivo del rechazo..."
          rows="4"
        ></textarea>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" on:click={cerrar}> Cancelar </button>
        <button
          class="btn btn-danger"
          on:click={confirmarRechazo}
          disabled={loading || !motivoRechazo.trim()}
        >
          Confirmar Rechazo
        </button>
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
  .modal-rechazo {
    max-width: 500px;
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
  .form-group {
    margin-top: 1rem;
  }
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-weight: 600;
    font-size: 0.9rem;
  }
  textarea {
    width: 93%;
    padding: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-family: inherit;
    font-size: 0.9rem;
    resize: vertical;
    transition: all 0.2s ease;
  }
  textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1.5rem;
    padding-top: 0;
    border-top: none;
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
</style>
