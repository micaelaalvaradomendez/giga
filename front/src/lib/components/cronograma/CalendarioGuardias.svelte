<script>
  import { createEventDispatcher } from 'svelte';
  export let dias = [];                 
  export let asignaciones = {};         
  export let agentesElegidos = [];      
  const dispatch = createEventDispatcher();
  const fmt = (d) => d.toISOString().slice(0,10);
  const weekdayOffset = (d) => (d.getDay() + 6) % 7; // lunes=0

  const nombreAgente = (id) => {
    const a = agentesElegidos.find(x => String(x.id) === String(id));
    return a ? a.apellido : 'Agente';
  };
</script>

<div class="cal">
  <div class="dow">Lun</div><div class="dow">Mar</div><div class="dow">Mié</div>
  <div class="dow">Jue</div><div class="dow">Vie</div><div class="dow">Sáb</div><div class="dow">Dom</div>

  {#if dias.length}
    {#each Array(weekdayOffset(dias[0])).fill(0) as _}
      <div class="empty"></div>
    {/each}
  {/if}

  {#each dias as d (d.toISOString())}
    <div class="day" on:click={() => dispatch('abrirModal', { diaStr: fmt(d) })}>
      <div class="dnum">{d.getDate()}</div>
      <div class="alist">
        {#each (asignaciones[fmt(d)] || []) as a}
          <div class="tag" on:click|stopPropagation={() => dispatch('editarAsignacion', { diaStr: fmt(d), asign: a })}>
            <span>{nombreAgente(a.agenteId)?.slice(0,12)}</span>
            <span class="hrs">{a.horas}h</span>
            <button class="rm" on:click|stopPropagation={() => dispatch('eliminarAsignacion', { diaStr: fmt(d), agenteId: a.agenteId })}>×</button>
          </div>
        {/each}
      </div>
    </div>
  {/each}
</div>

<style>
.cal { display: grid; grid-template-columns: repeat(7, 1fr); gap: .25rem; }
.dow { text-align: center; font-weight: 700; color: #334155; padding: .2rem 0; font-size: .9rem; }
.empty { border: 1px dashed #e5e7eb; border-radius: 8px; min-height: 80px; opacity: .4; }
.day { border: 1px solid #e5e7eb; border-radius: 10px; min-height: 84px; padding: .35rem; display: grid; grid-template-rows: auto 1fr; gap: .2rem; background: #fff; cursor: pointer; }
.day:hover { border-color: #93c5fd; box-shadow: 0 4px 12px rgba(30,64,175,.12); }
.dnum { font-weight: 700; color: #1e293b; }
.alist { display: grid; gap: .25rem; align-content: start; }
.tag { display: grid; grid-template-columns: 1fr auto auto; align-items: center; gap: .35rem; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; border-radius: 8px; padding: .15rem .35rem; font-size: .85rem; }
.tag .hrs { color: #0f172a; font-weight: 700; }
.rm { background: transparent; border: 0; color: #64748b; cursor: pointer; font-weight: 700; }
</style>
