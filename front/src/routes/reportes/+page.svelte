<script>
  import { onMount } from "svelte";
  import { guardiasService, personasService } from "$lib/services.js";
  import MultiSelect from "./MultiSelect.svelte";
  const hoy = new Date();
  const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1).toISOString().slice(0, 10);
  const finMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0).toISOString().slice(0, 10);
  const ROLES = {
    ADMIN: "administrador",
    DIRECTOR: "director",
    JEFATURA: "jefatura",
    AGENTE: "agente",
  };
  let tipoReporte = "individual";
  let fecha_desde = inicioMes;
  let fecha_hasta = finMes;
  let area = "";
  let areaSeleccionadas = [];
  let agente = "";
  let agentesSeleccionados = [];
  let tipo_guardia = "";
  let areas = [];
  let agentes = [];
  let resultado = null;
  let cargando = false;
  let exportando = false;
  let error = "";
  let mensaje = "";
  let rolActual = "";
  let areaUsuario = "";
  onMount(async () => {
    try {
      const claves = ["user", "usuario", "currentUser"];
      for (const key of claves) {
        const raw = localStorage.getItem(key);
        if (raw) {
          const u = JSON.parse(raw);
          rolActual = (u.roles?.[0]?.nombre || "").toLowerCase();
          areaUsuario = u.area?.id || u.area?.id_area || "";
          break;
        }
      }
    } catch (e) {
      console.warn("No se pudo leer el usuario de localStorage:", e);
    }
    try {
      const [areasRes, agentesRes] = await Promise.all([
        personasService.getAreas(),
        personasService.getAgentes(),
      ]);
      areas = areasRes.data?.data?.results || areasRes.data?.results || areasRes.data || [];
      agentes = agentesRes.data?.results || agentesRes.data?.data?.results || agentesRes.data || [];
    } catch (e) {
      console.warn("No se pudieron cargar áreas/agentes:", e);
    }
    if ([ROLES.JEFATURA, ROLES.DIRECTOR].includes(rolActual)) {
      area = areaUsuario || "";
    }
    if (rolActual === ROLES.AGENTE) {
      tipoReporte = "individual";
    }
  });
  function setTipoReporte(valor) {
    tipoReporte = valor;
    mensaje = "";
    error = "";
    resultado = null;
    if (valor === "general") {
      agente = "";
    }
  }
  function toInt(v) {
    const n = Number(v);
    return Number.isFinite(n) ? n : undefined;
  }
  function _buildAreas() {
    if (tipoReporte === "general" && (rolActual === ROLES.ADMIN || rolActual === ROLES.DIRECTOR)) {
      const arr = (areaSeleccionadas || []).map((a) => toInt(a)).filter(Boolean);
      return arr.length ? arr : undefined;
    }
    const single = rolActual === ROLES.JEFATURA ? areaUsuario : area;
    const val = toInt(single);
    return val ? [val] : undefined;
  }
  function _buildAgentes() {
    if (tipoReporte === "general") {
      let arr = (agentesSeleccionados || []).map((a) => toInt(a)).filter(Boolean);
      if (rolActual === ROLES.ADMIN || rolActual === ROLES.DIRECTOR) {
        const allowedAreas = (areaSeleccionadas || []).map((a) => toInt(a)).filter(Boolean);
        if (allowedAreas.length) {
          arr = arr.filter((id) => {
            const ag = agentes.find((a) => (a.id_agente || a.id) === id);
            const agArea = ag?.id_area || ag?.id_area_id;
            return ag && allowedAreas.includes(agArea);
          });
        }
      }
      return arr.length ? arr : undefined;
    }
    const val = toInt(agente);
    return val ? [val] : undefined;
  }
  function _puedeMostrarAgente(ag) {
    if (tipoReporte === "general" && (rolActual === ROLES.ADMIN || rolActual === ROLES.DIRECTOR)) {
      if (areaSeleccionadas && areaSeleccionadas.length) {
        return areaSeleccionadas.some((a) => toInt(a) === (ag.id_area || ag.id_area_id));
      }
    }
    if (rolActual === ROLES.JEFATURA) {
      return (ag.id_area || ag.id_area_id) === toInt(areaUsuario);
    }
    if (!areaSeleccionadas.length && !area) return true;
    const areaSel = toInt(area);
    return !areaSel || (ag.id_area || ag.id_area_id) === areaSel;
  }
  async function generar() {
    if (tipoReporte === "individual" && !_buildAgentes()) {
      error = "Selecciona un agente para el reporte individual";
      return;
    }
    cargando = true;
    error = "";
    mensaje = "";
    resultado = null;
    const body = {
      fecha_desde,
      fecha_hasta,
      area: _buildAreas(),
      agente: _buildAgentes(),
      tipo_guardia: tipo_guardia || undefined,
    };
    if (rolActual === ROLES.AGENTE) {
      body.area = undefined;
      body.agente = undefined;
    } else if (rolActual === ROLES.JEFATURA) {
      body.area = areaUsuario;
    } else if (rolActual === ROLES.DIRECTOR) {
      body.area = area || areaUsuario;
    }
    try {
      if (tipoReporte === "individual") {
        const res = await guardiasService.getReporteIndividual(body);
        resultado = res.data;
      } else {
        const res = await guardiasService.getReporteGeneral(body);
        resultado = res.data;
      }
      mensaje = "Reporte generado.";
    } catch (e) {
      console.error(e);
      error = e?.response?.data?.error || e?.message || "No se pudo generar el reporte";
    } finally {
      cargando = false;
    }
  }
  async function exportar(formato) {
    exportando = true;
    error = "";
    mensaje = "";
    const body = {
      tipo_reporte: tipoReporte,
      fecha_desde,
      fecha_hasta,
      area: _buildAreas(),
      agente: _buildAgentes(),
      tipo_guardia: tipo_guardia || undefined,
    };
    if (rolActual === ROLES.AGENTE) {
      body.area = undefined;
      body.agente = undefined;
    } else if (rolActual === ROLES.JEFATURA) {
      body.area = areaUsuario;
    } else if (rolActual === ROLES.DIRECTOR) {
      body.area = area || areaUsuario;
    }
    try {
      let response;
      if (formato === "pdf") {
        response = await guardiasService.exportarReportePDF(body);
      } else if (formato === "xlsx") {
        response = await guardiasService.exportarReporteExcel(body);
      } else {
        response = await guardiasService.exportarReporteCSV(body);
      }
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      const ts = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
      link.href = url;
      link.download = `GIGA_${tipoReporte}_${ts}.${formato === "xlsx" ? "xlsx" : formato}`;
      link.click();
      window.URL.revokeObjectURL(url);
      mensaje = `Exportado como ${formato.toUpperCase()}`;
    } catch (e) {
      console.error(e);
      error = e?.response?.data?.error || e?.message || "No se pudo exportar";
    } finally {
      exportando = false;
    }
  }
  $: optionsAreas = (areas || []).map((a) => ({ value: a.id_area || a.id, label: a.nombre }));
  $: optionsAgentes = (agentes || [])
    .filter((ag) => _puedeMostrarAgente(ag))
    .map((ag) => ({ value: ag.id_agente || ag.id, label: `${ag.nombre} ${ag.apellido}` }));
</script>
<svelte:head>
  <title>Reportes | GIGA</title>
</svelte:head>
<div class="wrapper">
  <header>
    <div>
      <p class="eyebrow">Reportes de Guardias</p>
      <h1>Vista previa y exportación</h1>
      <p class="muted">Usa filtros y genera el reporte individual o general. Los permisos se validan en backend según tu sesión.</p>
    </div>
    <div class="actions">
      <button class="secondary" on:click={() => exportar("csv")} disabled={exportando || cargando}>Exportar CSV</button>
      <button class="secondary" on:click={() => exportar("xlsx")} disabled={exportando || cargando}>Exportar Excel</button>
      <button class="primary" on:click={() => exportar("pdf")} disabled={exportando || cargando}>Exportar PDF</button>
    </div>
  </header>
  {#if mensaje}
    <div class="alert success">{mensaje}</div>
  {/if}
  {#if error}
    <div class="alert error">{error}</div>
  {/if}
  <section class="card">
    <div class="form-grid">
      <div class="field">
        <label>Tipo de reporte</label>
        <div class="radio-row">
          <label><input type="radio" name="tipo" value="individual" checked={tipoReporte === "individual"} on:change={() => setTipoReporte("individual")} /> Individual</label>
          {#if rolActual !== ROLES.AGENTE}
            <label><input type="radio" name="tipo" value="general" checked={tipoReporte === "general"} on:change={() => setTipoReporte("general")} /> General por área</label>
          {/if}
        </div>
      </div>
      <div class="field">
        <label>Fecha desde</label>
        <input type="date" bind:value={fecha_desde} />
      </div>
      <div class="field">
        <label>Fecha hasta</label>
        <input type="date" bind:value={fecha_hasta} />
      </div>
      {#if rolActual !== ROLES.AGENTE}
        <div class="field">
          <label>Área {rolActual === ROLES.JEFATURA ? "(fija)" : "(opcional)"} {tipoReporte === "general" && (rolActual === ROLES.ADMIN || rolActual === ROLES.DIRECTOR) ? "(múltiple)" : ""}</label>
          {#if tipoReporte === "general" && (rolActual === ROLES.ADMIN || rolActual === ROLES.DIRECTOR)}
            <MultiSelect options={optionsAreas} bind:value={areaSeleccionadas} placeholder="Seleccionar áreas" />
          {:else}
            <select bind:value={area} disabled={rolActual === ROLES.JEFATURA || tipoReporte === "individual"}>
              <option value="">(sin área)</option>
              {#each areas as a}
                <option value={a.id_area || a.id}>{a.nombre}</option>
              {/each}
            </select>
          {/if}
        </div>
        <div class="field">
          <label>Agente {tipoReporte === "individual" ? "(requerido)" : "(opcional)"} {tipoReporte === "general" ? "(múltiple)" : ""}</label>
          {#if tipoReporte === "general"}
            <MultiSelect options={optionsAgentes} bind:value={agentesSeleccionados} placeholder="Seleccionar agentes" />
          {:else}
            <select bind:value={agente} disabled={rolActual === ROLES.AGENTE}>
              <option value="">(sin agente)</option>
              {#each agentes as ag}
                {#if _puedeMostrarAgente(ag)}
                  <option value={ag.id_agente || ag.id}>{ag.nombre} {ag.apellido}</option>
                {/if}
              {/each}
            </select>
          {/if}
        </div>
      {/if}
      <div class="field" style="grid-column: 1 / -1;">
        <label>Tipo de guardia (opcional)</label>
        <input type="text" placeholder="Ej: nocturna" bind:value={tipo_guardia} />
      </div>
    </div>
    <div class="form-actions">
      <button class="primary" on:click={generar} disabled={cargando}>
        {#if cargando}Generando...{/if}
        {#if !cargando}Generar reporte{/if}
      </button>
    </div>
  </section>
  {#if resultado}
    <section class="card">
      <h3>Vista previa</h3>
      {#if tipoReporte === "individual"}
        <div class="preview-grid">
          <div class="mini-card">
            <p class="label">Agente</p>
            <p class="value">{resultado.agente?.nombre} {resultado.agente?.apellido} ({resultado.agente?.legajo})</p>
          </div>
          <div class="mini-card">
            <p class="label">Área</p>
            <p class="value">{resultado.agente?.area || "N/D"}</p>
          </div>
          <div class="mini-card">
            <p class="label">Período</p>
            <p class="value">{resultado.filtros?.fecha_desde} - {resultado.filtros?.fecha_hasta}</p>
          </div>
          <div class="mini-card">
            <p class="label">Horas totales</p>
            <p class="value">{resultado.totales?.horas_efectivas ?? resultado.totales?.total_horas ?? "-"}</p>
          </div>
        </div>
        <div class="list-preview">
          <p class="label">Resumen días</p>
          <ul>
            {#each (resultado.dias || []).slice(0, 5) as d}
              <li>
                <span>{d.fecha} · {d.dia_semana}</span>
                <span class="muted">{d.horario_guardia_inicio && d.horario_guardia_fin ? `${d.horario_guardia_inicio}-${d.horario_guardia_fin}` : "Sin horario"}</span>
              </li>
            {/each}
            {#if (resultado.dias || []).length > 5}
              <li class="muted">... y {(resultado.dias || []).length - 5} más</li>
            {/if}
          </ul>
        </div>
      {:else}
        <div class="preview-grid">
          <div class="mini-card">
            <p class="label">Áreas</p>
            <p class="value">
              {#if areaSeleccionadas.length}
                {areaSeleccionadas.map((id) => optionsAreas.find((o) => String(o.value) === String(id))?.label).filter(Boolean).join(", ")}
              {:else}
                (según permisos)
              {/if}
            </p>
          </div>
          <div class="mini-card">
            <p class="label">Período</p>
            <p class="value">{resultado.filtros?.fecha_desde} - {resultado.filtros?.fecha_hasta}</p>
          </div>
          <div class="mini-card">
            <p class="label">Agentes incluidos</p>
            <p class="value">{resultado.totales?.agentes ?? (resultado.agentes || []).length}</p>
          </div>
          <div class="mini-card">
            <p class="label">Horas total</p>
            <p class="value">{resultado.totales?.horas ?? resultado.totales?.total_horas ?? "-"}</p>
          </div>
        </div>
        <div class="list-preview">
          <p class="label">Agentes (vista breve)</p>
          <ul>
            {#each (resultado.agentes || []).slice(0, 8) as ag}
              <li>
                <div>
                  <strong>{ag.nombre_completo}</strong> <span class="muted">· Legajo {ag.legajo}</span>
                </div>
                <span class="muted">{ag.area || "Sin área"} · {ag.total_horas ?? 0} h</span>
              </li>
            {/each}
            {#if (resultado.agentes || []).length > 8}
              <li class="muted">... y {(resultado.agentes || []).length - 8} más</li>
            {/if}
          </ul>
        </div>
      {/if}
    </section>
  {/if}
</div>
<style>
  .wrapper { max-width: 1180px; margin: 0 auto; padding: 32px 24px 48px; display: flex; flex-direction: column; gap: 20px; }
  header { display: flex; justify-content: space-between; gap: 16px; align-items: center; flex-wrap: wrap; }
  .actions { display: flex; gap: 10px; flex-wrap: wrap; }
  .eyebrow { text-transform: uppercase; letter-spacing: 0.08em; font-size: 12px; color: #6b7280; }
  h1 { margin: 6px 0; font-size: 26px; color: #0f172a; }
  .muted { color: #6b7280; }
  .card { background: #fff; border: 1px solid #dde3ed; border-radius: 12px; padding: 20px; box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06); }
  .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px 18px; align-items: flex-start; }
  .field { display: flex; flex-direction: column; gap: 6px; }
  .field label { font-weight: 700; color: #0f172a; font-size: 14px; }
  .field input, .field select { padding: 12px; border: 1px solid #d6dce7; border-radius: 10px; font-size: 14px; background: #f9fafb; }
  .field input:focus, .field select:focus, .multiselect-trigger:focus { outline: 2px solid #2f6fed; outline-offset: 1px; border-color: #2f6fed; background: #fff; }
  .radio-row { display: flex; gap: 18px; align-items: center; }
  .form-actions { margin-top: 16px; display: flex; justify-content: flex-end; }
  .primary, .secondary { padding: 11px 16px; border-radius: 10px; border: none; cursor: pointer; font-weight: 700; transition: transform 0.05s ease, box-shadow 0.1s ease, background 0.1s ease; }
  .primary { background: #2f6fed; color: #fff; box-shadow: 0 8px 16px rgba(47, 111, 237, 0.25); }
  .primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 10px 20px rgba(47, 111, 237, 0.28); }
  .secondary { background: #eef1f5; color: #0f172a; border: 1px solid #e1e5ed; }
  .secondary:hover:not(:disabled) { background: #e2e8f0; transform: translateY(-1px); }
  .primary:disabled, .secondary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
  .alert { padding: 12px 14px; border-radius: 10px; }
  .alert.success { background: #ecfdf3; color: #166534; border: 1px solid #bbf7d0; }
  .alert.error { background: #fef2f2; color: #991b1b; border: 1px solid #fecdd3; }
  .table { width: 100%; border-collapse: collapse; margin-top: 12px; }
  .table th, .table td { border: 1px solid #e5e7eb; padding: 10px; font-size: 14px; }
  .table th { background: #f8fafc; text-align: left; font-weight: 700; }
  .table-scroll { overflow-x: auto; }
  .preview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 12px; }
  .mini-card { border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; background: #f9fafb; }
  .mini-card .label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; margin-bottom: 4px; }
  .mini-card .value { font-weight: 700; color: #0f172a; }
  .list-preview ul { list-style: none; padding: 0; margin: 6px 0 0; display: flex; flex-direction: column; gap: 8px; }
  .list-preview li { padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 10px; background: #fff; display: flex; flex-direction: column; gap: 4px; }
  .multiselect { position: relative; width: 100%; }
  .multiselect-trigger { border: 1px solid #d6dce7; border-radius: 10px; background: #f9fafb; cursor: pointer; padding: 10px 12px; display: flex; align-items: flex-start; gap: 6px; width: 100%; min-height: 44px; }
  .multiselect-trigger:disabled { cursor: not-allowed; opacity: 0.6; }
  .multiselect-dropdown { position: absolute; z-index: 30; background: #fff; border: 1px solid #d6dce7; border-radius: 10px; max-height: 220px; overflow-y: auto; width: 100%; margin-top: 4px; box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08); }
  .dropdown-actions { display: flex; justify-content: flex-end; padding: 8px 10px; border-bottom: 1px solid #e5e7eb; }
  .clear-btn { background: transparent; border: none; color: #2f6fed; cursor: pointer; font-size: 13px; font-weight: 700; }
  .clear-btn:hover { text-decoration: underline; }
  .option { display: flex; align-items: center; gap: 8px; padding: 9px 12px; }
  .option:hover { background: #f3f6fb; }
  .option input { accent-color: #2f6fed; }
  .option-label { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .pill-container { display: flex; flex-wrap: wrap; gap: 6px; min-height: 24px; max-height: 72px; overflow-y: auto; align-items: flex-start; padding-right: 6px; width: 100%; }
  .pill { background: #f2f5fb; border: 1px solid #d6dce7; color: #0f172a; border-radius: 999px; padding: 4px 8px; display: inline-flex; align-items: center; gap: 6px; }
  .pill-close { border: none; background: transparent; cursor: pointer; font-weight: 700; color: #475569; }
  .placeholder { color: #6b7280; font-size: 14px; }
</style>
