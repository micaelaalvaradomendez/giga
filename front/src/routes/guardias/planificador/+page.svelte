<script>
  import { onMount } from 'svelte';
  import SelectorAgentes from '$lib/components/cronograma/SelectorAgentes.svelte';
  import ResumenHoras from '$lib/components/cronograma/ResumenHoras.svelte';
  import CalendarioGuardias from '$lib/components/cronograma/CalendarioGuardias.svelte';
  import ModalAsignacion from '$lib/components/cronograma/ModalAsignacion.svelte';
  import ToastRedirect from '$lib/components/cronograma/ToastRedirect.svelte';

  import { personasService, guardiasService } from '$lib/services.js';


  let loading = false;
  let error = '';
  let subordinados = [];
  let seleccionados = new Set();
  let desde = '';
  let hasta = '';
  let horasTotales = '';
  let paso = 'seleccion';  
  let agentesElegidos = [];
  let dias = [];
  let asignaciones = {};


  let showModal = false;
  let modalDia = '';
  let modalAgenteId = '';
  let modalHoras = '';


  let toastVisible = false;

  const toId = v => String(v);
  const fmt = (d) => d.toISOString().slice(0,10);

  function construirDias(desdeStr, hastaStr) {
    const res = [];
    const start = new Date(desdeStr + "T00:00:00");
    const end = new Date(hastaStr + "T00:00:00");
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      res.push(new Date(d));
    }
    return res;
  }

  const fetchSubordinados = async () => {
    loading = true; error = '';
    try {
      const { data } = await personasService.getSubordinados();
      subordinados = (Array.isArray(data) ? data : []).map(s => ({ ...s, id: String(s.id) }));
    } catch (e) {
      error = 'No se pudieron cargar los subordinados';
    } finally {
      loading = false;
    }
  };
  onMount(fetchSubordinados);

  const toggleSeleccion = (id) => {
    const sid = toId(id);
    if (seleccionados.has(sid)) seleccionados.delete(sid);
    else seleccionados.add(sid);
    seleccionados = new Set(seleccionados); 
  };

  const rangoValido = () => !!desde && !!hasta && new Date(desde) <= new Date(hasta);
  const horasValidas = () => { const n = Number(horasTotales); return !Number.isNaN(n) && n > 0; };
  const puedeContinuar = () => rangoValido() && seleccionados.size > 0 && horasValidas();

  const continuar = () => {
    if (!puedeContinuar()) { error = 'Completá los datos para continuar'; return; }
    agentesElegidos = subordinados.filter(s => seleccionados.has(toId(s.id)));
    dias = construirDias(desde, hasta);
    asignaciones = {};
    paso = 'detalle';
  };

  const totalAsignado = () => {
    let t = 0;
    for (const k in asignaciones) (asignaciones[k] || []).forEach(a => t += Number(a.horas) || 0);
    return t;
  };
  const horasRestantes = () => Math.max(0, Number(horasTotales || 0) - totalAsignado());

  const agentesDisponibles = (diaStr, incluirId = null) => {
    const ya = new Set((asignaciones[diaStr] || []).map(a => toId(a.agenteId)));
    if (incluirId != null) ya.delete(toId(incluirId));
    return (agentesElegidos || []).filter(a => !ya.has(toId(a.id)));
  };

  function handleAbrirModal(diaStr) {
    modalDia = diaStr;
    const disp = agentesDisponibles(diaStr);
    modalAgenteId = toId(disp[0]?.id ?? '');
    modalHoras = '';
    showModal = true;
  }
  function handleEditarAsignacion({ detail }) {
    const { diaStr, asign } = detail;
    modalDia = diaStr;
    modalAgenteId = toId(asign.agenteId);
    modalHoras = String(asign.horas ?? '');
    showModal = true;
  }
  function handleEliminarAsignacion({ detail }) {
    const { diaStr, agenteId } = detail;
    const id = toId(agenteId);
    const list = asignaciones[diaStr] || [];
    asignaciones = { ...asignaciones, [diaStr]: list.filter(a => toId(a.agenteId) !== id) };
  }

  function guardarAsignacion() {
    const h = Number(modalHoras);
    const id = toId(modalAgenteId);
    if (!id) { error = 'Seleccioná un agente'; return; }
    if (!h || h <= 0) { error = 'Ingresá horas válidas'; return; }
    if (h > horasRestantes()) { error = 'No hay horas suficientes disponibles'; return; }
    error = '';
    const list = asignaciones[modalDia] ? [...asignaciones[modalDia]] : [];
    const idx = list.findIndex(x => toId(x.agenteId) === id);
    if (idx >= 0) list[idx] = { agenteId: id, horas: h };
    else list.push({ agenteId: id, horas: h });
    asignaciones = { ...asignaciones, [modalDia]: list };
    showModal = false;
  }

  async function confirmarPlan() {
    try {
      const payload = { desde, hasta, horas_totales: Number(horasTotales), asignaciones: [] };
      const mapAg = new Map(agentesElegidos.map(a => [toId(a.id), a]));
      for (const dia in asignaciones) {
        for (const a of asignaciones[dia]) {
          const ag = mapAg.get(toId(a.agenteId));
          if (!ag) continue;
          payload.asignaciones.push({ fecha: dia, usuario_id: ag.usuario_id, horas: Number(a.horas) });
        }
      }
      const { data } = await guardiasService.planificar(payload);
      toastVisible = true; 
    } catch (e) {
      alert(e?.response?.data?.detail || 'Error al crear el cronograma');
    }
  }
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
          <input class="input" id="desde" type="date" bind:value={desde} />
        </div>
        <div class="campo">
          <label for="hasta">Hasta</label>
          <input class="input" id="hasta" type="date" bind:value={hasta} min={desde || undefined} />
        </div>
        <div class="campo">
          <label for="horasTotales">Horas totales a distribuir</label>
          <div class="row gap">
            <input class="input input-number" id="horasTotales" type="number" min="0" step="0.5" bind:value={horasTotales} placeholder="Ej: 120" />
            <span class="sufijo">h</span>
          </div>
        </div>
      </div>

      <SelectorAgentes
        {loading}
        {error}
        {subordinados}
        {seleccionados}
        clase = "mt"
        on:toggle={(e)=>toggleSeleccion(e.detail)}
      />

      <div class="acciones">
        <button class="btn" on:click={continuar} disabled={!puedeContinuar()}>Continuar</button>
      </div>
    </div>

  {:else}
    <div class="panel card">
      <ResumenHoras
        {desde} {hasta}
        {horasTotales}
        asignadas={totalAsignado()}
        restantes={horasRestantes()}
      />

      <CalendarioGuardias
        {dias}
        {asignaciones}
        {agentesElegidos}
        on:abrirModal={(e)=>handleAbrirModal(e.detail.diaStr)}
        on:editarAsignacion={handleEditarAsignacion}
        on:eliminarAsignacion={handleEliminarAsignacion}
      />

      <div class="acciones acciones-cal">
        <button class="btn" on:click={() => paso='seleccion'}>Volver</button>
        <button class="btn" on:click={confirmarPlan} disabled={horasRestantes() < 0}>Confirmar</button>
      </div>

      {#if showModal}
        <ModalAsignacion
          dia={modalDia}
          agentes={agentesDisponibles(modalDia, modalAgenteId)}
          bind:agenteId={modalAgenteId}
          bind:horas={modalHoras}
          restantes={horasRestantes()}
          on:guardar={() => guardarAsignacion()}
          on:cerrar={() => (showModal=false)}
        />
      {/if}
    </div>
  {/if}
</section>

{#if toastVisible}
  <ToastRedirect mensaje="Cronograma creado correctamente" destino="/inicio" />
{/if}

<style>
.guardias-wrap { max-width: 1000px; margin: 0 auto; padding: 1.25rem; font-family: Verdana, Geneva, Tahoma, sans-serif; }
.head h1 { font-size: 1.6rem; margin: 0 0 .25rem 0; color: #1e40af; }
.head p { margin: 0 0 1rem 0; color: #475569; font-size: .95rem; }
.panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1rem; width: 100%; }
.card { display: grid; gap: 1.25rem; }
.grid2 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2rem; }
.campo { margin-bottom: 1rem; }
label { font-weight: 600; color: #334155; display: block; margin-bottom: .5rem; }
.input { border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 12px; padding: .6rem .85rem; font-size: .95rem; width: 100%; }
.input-number { max-width: 220px; }
.sufijo { align-self: center; color: #475569; font-weight: 600; margin-left: .25rem; }
.row { display: flex; align-items: center; gap: .75rem; }
.btn { background: #1e40af; color: #fff; border: 0; border-radius: 10px; padding: .65rem 1rem; cursor: pointer; }
.btn:disabled { background: #94a3b8; cursor: not-allowed; }
.acciones { display: flex; justify-content: flex-end; gap: .6rem; }
.acciones-cal { margin-top: 1rem; }
@media (max-width: 900px) { .grid2 { grid-template-columns: 1fr; } }
</style>
