<script>
  import { createEventDispatcher } from 'svelte';
  export let dia = '';
  export let agentes = [];      
  export let agenteId = '';
  export let horas = '';
  export let restantes = 0;
  const dispatch = createEventDispatcher();
</script>

<div class="modal-backdrop" on:click={() => dispatch('cerrar')}></div>
<div class="modal">
  <h3>Asignar horas - {dia}</h3>

  <div class="campo">
    <label>Agente</label>
    <select class="input" bind:value={agenteId}>
      {#each agentes as a}
        <option value={String(a.id)}>{a.apellido}, {a.nombre}</option>
      {/each}
    </select>
  </div>

  <div class="campo">
    <label>Horas</label>
    <input class="input" type="number" min="0" step="0.5" bind:value={horas} placeholder="Ej: 6" />
    <small class="desc">Restantes: {restantes} h</small>
  </div>

  <div class="acciones">
    <button class="btn" on:click={() => dispatch('guardar')}>Guardar</button>
    <button class="btn secundario" on:click={() => dispatch('cerrar')} type="button">Cancelar</button>
  </div>
</div>

<style>
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 40; }
.modal { position: fixed; left: 50%; top: 15%; transform: translateX(-50%); width: min(500px, 92vw); background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; box-shadow: 0 20px 60px rgba(0,0,0,.25); display: grid; gap: .75rem; z-index: 41; }
.campo { margin-bottom: .5rem; }
.input { box-sizing: border-box; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 12px; padding: .6rem .85rem; font-size: .95rem; width: 100%; }
.desc { color: #94a3b8; display: block; margin-top: .35rem; min-height: 1.1rem; }
.acciones { display: flex; justify-content: flex-end; gap: .6rem; padding-top: .6rem; }
.btn { background: #1e40af; color: #fff; border: 0; border-radius: 10px; padding: .55rem .9rem; cursor: pointer; }
.btn.secundario { background: #94a3b8; }
</style>
