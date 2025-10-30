<script>
  export let desde = '';
  export let hasta = '';
  export let horasTotales = '';
  export let asignadas = 0;
  export let restantes = 0;
</script>

<div class="resumen">
  <div><b>Periodo:</b> {desde} → {hasta}</div>
  <div><b>Horas totales:</b> {horasTotales}</div>
  <div><b>Asignadas:</b> {asignadas} | <b>Restantes:</b> {restantes}</div>
</div>

<style>
.resumen { display: flex; gap: 1rem; flex-wrap: wrap; color: #0f172a; margin-bottom: .5rem; }
</style>
