<script>
  function construirDias(desdeStr, hastaStr) {
    const res = [];
    const start = new Date(desdeStr + "T00:00:00");
    const end = new Date(hastaStr + "T00:00:00");
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      res.push(new Date(d));
    }
    return res;
  }
  import { onMount } from 'svelte';
  import { personasService } from '$lib/services.js';

  let loading = false;
  let error = '';
  let subordinados = [];
  let seleccionados = new Set();
  let desde = '';
  let hasta = '';
  let horasTotales = '';
  // Paso actual y estado del calendario
  let paso = 'seleccion';
  let agentesElegidos = [];
  let dias = [];
  let asignaciones = {}; // { 'YYYY-MM-DD': [ { agenteId, horas } ] }
  let showModal = false;
  let modalDia = '';
  let modalAgenteId = '';
  let modalHoras = '';

  const fetchSubordinados = async () => {
    loading = true;
    error = '';
    try {
      const { data } = await personasService.getSubordinados();
      subordinados = Array.isArray(data) ? data : [];
    } catch (e) {
      error = 'No se pudieron cargar los subordinados';
    } finally {
      loading = false;
    }
  };

  onMount(fetchSubordinados);

  const toggleSeleccion = (id) => {
    if (seleccionados.has(id)) seleccionados.delete(id);
    else seleccionados.add(id);
    // Forzar reactividad creando un nuevo Set
    seleccionados = new Set(seleccionados);
  };

  const rangoValido = () => {
    if (!desde || !hasta) return false;
    return new Date(desde) <= new Date(hasta);
  };
  const continuar = () => {
    const elegidos = subordinados.filter(s => seleccionados.has(s.id));
    if (!rangoValido()) {
      error = 'El rango de fechas no es válido';
      return;
    }
    const horas = Number(horasTotales);
    if (!horas || horas <= 0) {
      error = 'Ingresá las horas totales a distribuir';
      return;
    }
    agentesElegidos = elegidos;
    dias = construirDias(desde, hasta);
    asignaciones = {};
    paso = 'detalle';
  };

  const horasValidas = () => {
    const n = Number(horasTotales);
    return !Number.isNaN(n) && n > 0;
  };

  const horasPromedio = () => {
    const n = Number(horasTotales);
    const cant = seleccionados.size || 0;
    if (!horasValidas() || cant === 0) return null;
    return (n / cant).toFixed(2);
  };

  const puedeContinuar = () => rangoValido() && seleccionados.size > 0 && horasValidas();
  // Utilidades para el paso de detalle
  const fmt = (d) => d.toISOString().slice(0,10);

  const totalAsignado = () => { let t=0; for (const k in asignaciones) (asignaciones[k]||[]).forEach(a=>t+=Number(a.horas)||0); return t; };
  const horasRestantes = () => Math.max(0, Number(horasTotales||0) - totalAsignado());
  const abrirModal = (diaStr) => { modalDia=diaStr; modalAgenteId=(agentesElegidos[0]?.id)||''; modalHoras=''; showModal=true; };
  const cerrarModal = () => { showModal=false; };
  const guardarAsignacion = () => {
    const h=Number(modalHoras);
    if(!modalAgenteId){ error='Seleccioná un agente'; return;}
    if(!h||h<=0){ error='Ingresá horas válidas'; return;}
    if(h>horasRestantes()){ error='No hay horas suficientes disponibles'; return;}
    error='';
    const list=asignaciones[modalDia]?[...asignaciones[modalDia]]:[];
    const idx=list.findIndex(x=>x.agenteId===modalAgenteId);
    if(idx>=0) list[idx]={agenteId:modalAgenteId, horas:h}; else list.push({agenteId:modalAgenteId, horas:h});
    asignaciones={...asignaciones, [modalDia]:list};
    showModal=false;
  };
  const eliminarAsignacion = (diaStr, agenteId) => { const list=asignaciones[diaStr]||[]; asignaciones={...asignaciones, [diaStr]: list.filter(a=>a.agenteId!==agenteId)}; };
</script>

<section class="guardias-wrap">
  <header class="head">
    <h1>Planificación de Guardias</h1>
    <p>Elegí un período y los agentes a planificar</p>
  </header>
  {#if paso === 'seleccion'}

  <div class="panel card">
    <div class="grid2">
      <div class="campo">
        <label for="desde">Desde</label>
        <input class="input" id="desde" lang="es-AR" type="date" bind:value={desde} />
        <small class="desc">Formato: dd/mm/aaaa</small>
      </div>
      <div class="campo">
        <label for="hasta">Hasta</label>
        <input class="input" id="hasta" lang="es-AR" type="date" bind:value={hasta} min={desde || undefined} />
        <small class="desc">Formato: dd/mm/aaaa</small>
      </div>
      <div class="campo">
        <label for="horasTotales">Horas totales a distribuir</label>
        <div class="row gap">
          <input class="input input-number" id="horasTotales" type="number" min="0" step="0.5" bind:value={horasTotales} placeholder="Ej: 120" />
          <span class="sufijo">h</span>
        </div>
        <small class='desc'>&nbsp;</small>
      </div>
    </div>

    <div class="campo">
      <div class="row between">
        <label>Subordinados</label>
        <small>{seleccionados.size}/{subordinados.length} seleccionados</small>
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
              <input type="checkbox" checked={seleccionados.has(s.id)} on:change={() => toggleSeleccion(s.id)} />
              <div class="datos">
                <div class="nombre">{s.apellido}, {s.nombre}</div>
                {#if s.areas?.length}
                  <div class="areas">{s.areas.map(a => a.nombre).join(' Â· ')}</div>
                {/if}
              </div>
            </label>
          {/each}
        </div>
      {/if}
    </div>


    <div class="acciones">
      <button class="btn" on:click={continuar} disabled={!puedeContinuar()}>Continuar</button>
    </div>
</div>
  {:else}
  <div class="panel card">
    <div class="resumen">
      <div><b>Periodo:</b> {desde} → {hasta}</div>
      <div><b>Horas totales:</b> {horasTotales}</div>
      <div><b>Asignadas:</b> {totalAsignado()} | <b>Restantes:</b> {horasRestantes()}</div>
    </div>
    <div class="cal">
      <div class="dow">Lun</div><div class="dow">Mar</div><div class="dow">Mié</div><div class="dow">Jue</div><div class="dow">Vie</div><div class="dow">Sáb</div><div class="dow">Dom</div>
      {#if dias.length}
        {#each Array(((dias[0].getDay() + 6) % 7)).fill(0) as _}
          <div class="empty"></div>
        {/each}
      {/if}
      {#each dias as d (d.toISOString())}
        <div class="day" on:click={() => abrirModal(fmt(d))}>
          <div class="dnum">{d.getDate()}</div>
          <div class="alist">
            {#each (asignaciones[fmt(d)] || []) as a}
              <div class="tag">
                <span>{agentesElegidos.find(x => x.id === a.agenteId)?.apellido?.slice(0,12) || 'Agente'}</span>
                <span class="hrs">{a.horas}h</span>
                <button class="rm" on:click|stopPropagation={() => eliminarAsignacion(fmt(d), a.agenteId)}>×</button>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
    <div class="acciones">
      <button class="btn" on:click={() => paso='seleccion'}>Volver</button>
      <button class="btn" disabled={horasRestantes() > 0}>Confirmar</button>
    </div>

    {#if showModal}
      <div class="modal-backdrop" on:click={cerrarModal}></div>
      <div class="modal">
        <h3>Asignar horas - {modalDia}</h3>
        <div class="campo">
          <label>Agente</label>
          <select class="input" bind:value={modalAgenteId}>
            {#each agentesElegidos as a}
              <option value={a.id}>{a.apellido}, {a.nombre}</option>
            {/each}
          </select>
        </div>
        <div class="campo">
          <label>Horas</label>
          <input class="input" type="number" min="0" step="0.5" bind:value={modalHoras} placeholder="Ej: 6" />
          <small class="desc">Restantes: {horasRestantes()} h</small>
        </div>
        <div class="acciones">
          <button class="btn" on:click={guardarAsignacion}>Guardar</button>
          <button class="btn" on:click={cerrarModal} type="button">Cancelar</button>
        </div>
      </div>
    {/if}
  </div>
  {/if}
</section>

<style>
  .guardias-wrap { max-width: 1100px; margin: 0 auto; padding: 1.5rem; font-family: Verdana, Geneva, Tahoma, sans-serif; }
  .head h1 { font-size: 1.6rem; margin: 0 0 0.25rem 0; color: #1e40af; }
  .head p { margin: 0 0 1rem 0; color: #475569; font-size: 0.95rem; }

  .panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1.25rem; }
  .card { display: grid; gap: 1rem; transition: box-shadow 0.2s ease, border-color 0.2s ease; }
  .card:hover { border-color: #bfdbfe; box-shadow: 0 8px 24px rgba(30, 64, 175, 0.12); }
  
  .grid2 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.5rem; align-items: start; }
  .campo { margin-bottom: 1rem; }
  label { font-weight: 600; color: #334155; display: block; margin-bottom: .5rem; }
  .input { box-sizing: border-box; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 12px; padding: .6rem .85rem; font-size: .95rem; width: 100%; transition: border-color .15s ease, box-shadow .15s ease, background .15s ease; box-shadow: inset 0 1px 2px rgba(0,0,0,.04); }
  .input:focus { outline: none; border-color: #60a5fa; box-shadow: 0 0 0 3px rgba(59,130,246,.15); background: #fff; }
  .input::placeholder { color: #94a3b8; }
  .input-number { max-width: 220px; }
  .sufijo { align-self: center; color: #475569; font-weight: 600; margin-left: .25rem; }
  .desc { color: #94a3b8; display: block; margin-top: .35rem; min-height: 1.1rem; }

  .row { display: flex; align-items: center; gap: .75rem; }
  .between { justify-content: space-between; }
  .gap { gap: .75rem; }

  .lista { display: grid; grid-template-columns: 1fr; gap: .5rem; max-height: 380px; overflow: auto; border: 1px solid #e5e7eb; border-radius: 8px; padding: .5rem; }
  .item { display: grid; grid-template-columns: 22px 1fr; align-items: center; gap: .5rem; padding: .4rem .5rem; border-radius: 6px; }
  .item:hover { background: #f8fafc; }
  .item input { width: 16px; height: 16px; }
  .datos { display: grid; gap: 2px; }
  .nombre { color: #0f172a; }
  .areas { color: #64748b; font-size: .85rem; }

  .acciones { display: flex; justify-content: flex-end; padding-top: .5rem; }
  .btn { background: #1e40af; color: #fff; border: 0; border-radius: 10px; padding: .65rem 1rem; cursor: pointer; box-shadow: 0 2px 0 rgba(0,0,0,0.06); }
  .btn:disabled { background: #94a3b8; cursor: not-allowed; }

  .placeholder { color: #64748b; font-size: .95rem; padding: .5rem; }
  .error { color: #b91c1c; background: #fef2f2; border: 1px solid #fecaca; padding: .5rem; border-radius: 6px; }
  .hint { color: #64748b; }

  @media (max-width: 900px) { .grid2 { grid-template-columns: 1fr; } }

  /* Calendario */
  .resumen { display: flex; gap: 1rem; flex-wrap: wrap; color: #0f172a; margin-bottom: .5rem; }
  .cal { display: grid; grid-template-columns: repeat(7, 1fr); gap: .5rem; }
  .dow { text-align: center; font-weight: 700; color: #334155; padding: .25rem 0; }
  .empty { border: 1px dashed #e5e7eb; border-radius: 8px; min-height: 80px; opacity: .4; }
  .day { border: 1px solid #e5e7eb; border-radius: 10px; min-height: 120px; padding: .5rem; display: grid; grid-template-rows: auto 1fr; gap: .25rem; background: #fff; cursor: pointer; }
  .day:hover { border-color: #93c5fd; box-shadow: 0 4px 12px rgba(30,64,175,.12); }
  .dnum { font-weight: 700; color: #1e293b; }
  .alist { display: grid; gap: .25rem; align-content: start; }
  .tag { display: grid; grid-template-columns: 1fr auto auto; align-items: center; gap: .35rem; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; border-radius: 8px; padding: .15rem .35rem; font-size: .85rem; }
  .tag .hrs { color: #0f172a; font-weight: 700; }
  .rm { background: transparent; border: 0; color: #64748b; cursor: pointer; font-weight: 700; }

  /* Modal */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.4); }
  .modal { position: fixed; left: 50%; top: 15%; transform: translateX(-50%); width: min(500px, 92vw); background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; box-shadow: 0 20px 60px rgba(0,0,0,.25); display: grid; gap: .75rem; }
</style>






