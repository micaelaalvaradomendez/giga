<script>
  import { createEventDispatcher } from 'svelte';
  export let loading = false;
  export let error = '';
  export let clase = '';
  export let subordinados = [];
  export let seleccionados = new Set();
  const dispatch = createEventDispatcher();

  const toggle = (id) => dispatch('toggle', id);
</script>

<div class={"bloque " + clase}>
  <div class="row between">
    <label>Subordinados</label>
  </div>

  {#if loading}
    <div class="placeholder">Cargando subordinados...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if subordinados.length === 0}
    <div class="placeholder">No se encontraron subordinados.</div>
  {:else}
    <div class="lista">
      {#each subordinados as s}
        <label class="item">
          <input type="checkbox" checked={seleccionados.has(String(s.id))} on:change={() => toggle(String(s.id))} />
          <div class="datos">
            <div class="nombre">{s.apellido}, {s.nombre}</div>
            {#if s.areas?.length}
              <div class="areas">{s.areas.map(a => a.nombre).join(' · ')}</div>
            {/if}
          </div>
        </label>
      {/each}
    </div>
  {/if}
</div>

<style>
.lista { margin-top: .5rem; display: grid; grid-template-columns: 1fr; gap: .5rem; max-height: 380px; overflow: auto; border: 1px solid #e5e7eb; border-radius: 8px; padding: .4rem; }
.item { display: grid; grid-template-columns: 22px 1fr; align-items: center; gap: .5rem; padding: .4rem .5rem; border-radius: 6px; }
.item:hover { background: #f8fafc; }
.bloque { margin-top: .75rem; }
.item input { width: 16px; height: 16px; }
.datos { display: grid; gap: 2px; }
.nombre { color: #0f172a; }
.areas { color: #64748b; font-size: .85rem; }
.placeholder { color: #64748b; font-size: .95rem; padding: .4rem; }
.error { color: #b91c1c; background: #fef2f2; border: 1px solid #fecaca; padding: .4rem; border-radius: 6px; }
.row { display: flex; align-items: center; justify-content: space-between; }
</style>
