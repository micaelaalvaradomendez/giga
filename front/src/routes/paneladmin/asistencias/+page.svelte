<script>
import { onMount } from 'svelte';
import { goto } from '$app/navigation';
import { asistenciasController } from '$lib/paneladmin/controllers';

// Obtener stores del controlador
const {
loading,
areas,
resumen,
licencias,
asistenciasFiltradas,
fechaSeleccionada,
areaSeleccionada,
tabActiva,
modalCorreccion,
asistenciaEditando,
observacionEdit
} = asistenciasController;

onMount(async () => {
console.log('🔄 Componente de asistencias montado, iniciando controlador...');
try {
await asistenciasController.init();
console.log('✅ Controlador de asistencias inicializado exitosamente');

// Recargar cuando la página vuelve a ser visible
if (typeof window !== 'undefined') {
const handleVisibilityChange = () => {
if (document.visibilityState === 'visible') {
asistenciasController.recargar();
}
};

const handleFocus = () => {
asistenciasController.recargar();
};

document.addEventListener('visibilitychange', handleVisibilityChange);
window.addEventListener('focus', handleFocus);

return () => {
document.removeEventListener('visibilitychange', handleVisibilityChange);
window.removeEventListener('focus', handleFocus);
};
}
} catch (err) {
console.error('❌ Error inicializando controlador:', err);
if (err.message.includes('no autenticado')) {
goto('/');
return;
}
}
});

// Funciones delegadas al controlador
async function handleMarcarEntrada() {
const result = await asistenciasController.marcarEntrada();
if (result.message) {
alert(result.message);
}
}

async function handleMarcarSalida() {
const result = await asistenciasController.marcarSalida();
if (result.message) {
alert(result.message);
}
}
</script>

<svelte:head>
<title>Gestión de Asistencias - Admin</title>
</svelte:head>

<div class="admin-container">
<div class="header">
<h1>Gestión de Asistencias</h1>
<p class="subtitle">Panel de administración</p>
</div>

<!-- Filtros -->
<div class="filtros-card">
<div class="filtros-grid">
<div class="form-group">
<label for="fecha">Fecha</label>
<input 
type="date" 
id="fecha" 
bind:value={$fechaSeleccionada}
on:change={() => asistenciasController.setFecha($fechaSeleccionada)}
/>
</div>

<div class="form-group">
<label for="area">Área</label>
<select 
id="area" 
bind:value={$areaSeleccionada}
on:change={() => asistenciasController.setArea($areaSeleccionada)}
>
<option value="">Todas las áreas</option>
{#each $areas as area}
<option value={area.id_area}>{area.nombre}</option>
{/each}
</select>
</div>
</div>
</div>

<!-- Resumen -->
{#if $resumen}
<div class="resumen-grid">
<div class="resumen-card total">
<div class="numero">{$resumen.total_agentes}</div>
<div class="label">Total Agentes</div>
</div>
<div class="resumen-card presentes">
<div class="numero">{$resumen.presentes}</div>
<div class="label">Presentes</div>
</div>
<div class="resumen-card ausentes">
<div class="numero">{$resumen.ausentes}</div>
<div class="label">Ausentes</div>
</div>
<div class="resumen-card sin-salida">
<div class="numero">{$resumen.sin_salida}</div>
<div class="label">Sin Salida</div>
</div>
<div class="resumen-card automaticas">
<div class="numero">{$resumen.salidas_automaticas}</div>
<div class="label">Salidas Auto</div>
</div>
</div>
{/if}

<!-- Tabs -->
<div class="tabs">
<button
class:active={$tabActiva === 'todas'}
on:click={() => asistenciasController.setTabActiva('todas')}
>
Todas
</button>
<button
class:active={$tabActiva === 'completas'}
on:click={() => asistenciasController.setTabActiva('completas')}
>
Completas
</button>
<button
class:active={$tabActiva === 'sin_salida'}
on:click={() => asistenciasController.setTabActiva('sin_salida')}
>
Sin Salida
</button>
<button
class:active={$tabActiva === 'sin_entrada'}
on:click={() => asistenciasController.setTabActiva('sin_entrada')}
>
Sin Entrada
</button>
<button
class:active={$tabActiva === 'salidas_auto'}
on:click={() => asistenciasController.setTabActiva('salidas_auto')}
>
Salidas Auto
</button>
<button
class:active={$tabActiva === 'licencias'}
on:click={() => asistenciasController.setTabActiva('licencias')}
>
Licencias
</button>
</div>

<!-- Contenido -->
{#if $loading}
<div class="loading">Cargando...</div>
{:else if $tabActiva === 'licencias'}
<!-- Lista de Licencias -->
<div class="table-container">
<table>
<thead>
<tr>
<th>Agente</th>
<th>DNI</th>
<th>Área</th>
<th>Tipo de Licencia</th>
<th>Desde</th>
<th>Hasta</th>
</tr>
</thead>
<tbody>
{#if $licencias.length === 0}
<tr>
<td colspan="6" class="empty">No hay licencias en esta fecha</td>
</tr>
{:else}
{#each $licencias as licencia}
<tr>
<td>{licencia.agente_nombre}</td>
<td>{licencia.agente_dni || 'N/A'}</td>
<td>{licencia.area_nombre || 'N/A'}</td>
<td>{licencia.tipo_licencia_descripcion}</td>
<td>{asistenciasController.formatDate(licencia.fecha_desde)}</td>
<td>{asistenciasController.formatDate(licencia.fecha_hasta)}</td>
</tr>
{/each}
{/if}
</tbody>
</table>
</div>
{:else}
<!-- Lista de Asistencias -->
<div class="table-container">
<table>
<thead>
<tr>
<th>Agente</th>
<th>DNI</th>
<th>Área</th>
<th>Entrada</th>
<th>Salida</th>
<th>Estado</th>
<th>Acciones</th>
</tr>
</thead>
<tbody>
{#if $asistenciasFiltradas.length === 0}
<tr>
<td colspan="7" class="empty">No hay registros</td>
</tr>
{:else}
{#each $asistenciasFiltradas as asistencia}
<tr>
<td>
{asistencia.agente_nombre}
{#if asistencia.es_correccion}
<span class="badge-correccion" title="Corregido por {asistencia.corregido_por_nombre}">
✏️
</span>
{/if}
</td>
<td>{asistencia.agente_dni}</td>
<td>{asistencia.area_nombre || 'N/A'}</td>
<td>
<span class="hora">{asistenciasController.formatTime(asistencia.hora_entrada)}</span>
{#if asistencia.marcacion_entrada_automatica}
<span class="badge-auto">AUTO</span>
{/if}
</td>
<td>
<span class="hora">{asistenciasController.formatTime(asistencia.hora_salida)}</span>
{#if asistencia.marcacion_salida_automatica}
<span class="badge-auto">AUTO</span>
{/if}
</td>
<td>
{#if asistencia.estado}
{@const badge = asistenciasController.getEstadoBadge(asistencia)}
<span class="badge {badge.class}">{badge.text}</span>
{/if}
</td>
<td>
<button 
class="btn-editar" 
on:click={() => asistenciasController.abrirModalCorreccion(asistencia)}
>
✏️ Corregir
</button>
</td>
</tr>
{/each}
{/if}
</tbody>
</table>
</div>
{/if}
</div>

<!-- Modal de Corrección -->
{#if $modalCorreccion && $asistenciaEditando}
<div class="modal-overlay" on:click={() => asistenciasController.cerrarModal()}>
<div class="modal-content" on:click|stopPropagation>
<div class="modal-header">
<h2>Marcar Asistencia</h2>
<button class="btn-close" on:click={() => asistenciasController.cerrarModal()}>×</button>
</div>

<div class="modal-body">
<p class="agente-info">
<strong>{$asistenciaEditando.agente_nombre}</strong><br>
<span class="dni-info">DNI: {$asistenciaEditando.agente_dni}</span><br>
<span class="fecha-info">{asistenciasController.formatDate($asistenciaEditando.fecha)}</span>
</p>

{#if $asistenciaEditando.horario_esperado_entrada || $asistenciaEditando.horario_esperado_salida}
<div class="horario-esperado">
<h3>📅 Horario Esperado</h3>
<div class="horario-grid">
<div class="horario-item">
<span class="horario-label">Entrada:</span>
<span class="horario-valor esperado">
{$asistenciaEditando.horario_esperado_entrada ? asistenciasController.formatTime($asistenciaEditando.horario_esperado_entrada) : '--:--'}
</span>
</div>
<div class="horario-item">
<span class="horario-label">Salida:</span>
<span class="horario-valor esperado">
{$asistenciaEditando.horario_esperado_salida ? asistenciasController.formatTime($asistenciaEditando.horario_esperado_salida) : '--:--'}
</span>
</div>
</div>
</div>
{/if}

<div class="estado-actual">
<h3>✅ Estado Actual</h3>
<div class="estado-grid">
<div class="estado-item">
<span class="estado-label">Entrada:</span>
<span class="estado-valor {$asistenciaEditando.hora_entrada ? 'marcado' : 'sin-marcar'}">
{$asistenciaEditando.hora_entrada ? asistenciasController.formatTime($asistenciaEditando.hora_entrada) : 'Sin marcar'}
</span>
</div>
<div class="estado-item">
<span class="estado-label">Salida:</span>
<span class="estado-valor {$asistenciaEditando.hora_salida ? 'marcado' : 'sin-marcar'}">
{$asistenciaEditando.hora_salida ? asistenciasController.formatTime($asistenciaEditando.hora_salida) : 'Sin marcar'}
</span>
</div>
</div>
</div>

<div class="form-group">
<label for="observacion_edit">Observación (opcional)</label>
<textarea
id="observacion_edit"
bind:value={$observacionEdit}
placeholder="Motivo de la corrección (ej: 'Agente olvidó marcar')"
rows="2"
></textarea>
</div>

{#if $asistenciaEditando.observaciones}
<div class="observaciones-previas">
<strong>Observaciones anteriores:</strong>
<p>{$asistenciaEditando.observaciones}</p>
</div>
{/if}
</div>

<div class="modal-footer">
<button class="btn-cancelar" on:click={() => asistenciasController.cerrarModal()}>
Cancelar
</button>
<button 
class="btn-marcar-entrada" 
on:click={handleMarcarEntrada}
disabled={$asistenciaEditando.hora_entrada}
>
🕐 Marcar Entrada
</button>
<button 
class="btn-marcar-salida" 
on:click={handleMarcarSalida}
disabled={!$asistenciaEditando.hora_entrada || $asistenciaEditando.hora_salida}
>
🕐 Marcar Salida
</button>
</div>
</div>
</div>
{/if}

<style>
.admin-container {
max-width: 1400px;
margin: 0 auto;
padding: 2rem;
}

.header {
margin-bottom: 2rem;
}

.header h1 {
font-size: 2rem;
color: #333;
margin: 0 0 0.5rem 0;
}

.subtitle {
color: #666;
margin: 0;
}

/* Filtros */
.filtros-card {
background: white;
border-radius: 12px;
padding: 1.5rem;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
margin-bottom: 2rem;
}

.filtros-grid {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
gap: 1.5rem;
}

.form-group {
display: flex;
flex-direction: column;
}

.form-group label {
font-weight: 600;
margin-bottom: 0.5rem;
color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
padding: 0.75rem;
border: 1px solid #ddd;
border-radius: 8px;
font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
outline: none;
border-color: #667eea;
}

/* Resumen */
.resumen-grid {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
gap: 1rem;
margin-bottom: 2rem;
}

.resumen-card {
background: white;
border-radius: 12px;
padding: 1.5rem;
text-align: center;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
border-left: 4px solid #667eea;
}

.resumen-card.total {
border-left-color: #667eea;
}

.resumen-card.presentes {
border-left-color: #28a745;
}

.resumen-card.ausentes {
border-left-color: #dc3545;
}

.resumen-card.sin-salida {
border-left-color: #ffc107;
}

.resumen-card.automaticas {
border-left-color: #17a2b8;
}

.resumen-card .numero {
font-size: 2.5rem;
font-weight: 700;
color: #333;
}

.resumen-card .label {
font-size: 0.9rem;
color: #666;
margin-top: 0.5rem;
}

/* Tabs */
.tabs {
display: flex;
gap: 0.5rem;
margin-bottom: 1.5rem;
flex-wrap: wrap;
}

.tabs button {
padding: 0.75rem 1.5rem;
background: white;
border: 2px solid #e0e0e0;
border-radius: 8px;
cursor: pointer;
font-weight: 600;
color: #666;
transition: all 0.3s ease;
}

.tabs button:hover {
border-color: #667eea;
color: #667eea;
}

.tabs button.active {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
border-color: transparent;
}

/* Tabla */
.table-container {
background: white;
border-radius: 12px;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
overflow: hidden;
}

table {
width: 100%;
border-collapse: collapse;
}

thead {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
}

th {
padding: 1rem;
text-align: left;
font-weight: 600;
}

td {
padding: 1rem;
border-bottom: 1px solid #f0f0f0;
}

tbody tr:hover {
background: #f8f9fa;
}

.empty {
text-align: center;
color: #999;
font-style: italic;
padding: 3rem !important;
}

.hora {
font-family: 'Courier New', monospace;
font-weight: 600;
}

.badge {
padding: 0.25rem 0.75rem;
border-radius: 12px;
font-size: 0.85rem;
font-weight: 600;
}

.badge-success {
background: #d4edda;
color: #155724;
}

.badge-warning {
background: #fff3cd;
color: #856404;
}

.badge-error {
background: #f8d7da;
color: #721c24;
}

.badge-auto {
background: #17a2b8;
color: white;
padding: 0.25rem 0.5rem;
border-radius: 4px;
font-size: 0.7rem;
margin-left: 0.5rem;
}

.badge-correccion {
margin-left: 0.5rem;
cursor: help;
}

.btn-editar {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
padding: 0.5rem 1rem;
border: none;
border-radius: 6px;
cursor: pointer;
font-weight: 600;
transition: transform 0.2s ease;
}

.btn-editar:hover {
transform: translateY(-2px);
}

.loading {
text-align: center;
padding: 3rem;
color: #666;
font-size: 1.2rem;
}

/* Modal */
.modal-overlay {
position: fixed;
top: 0;
left: 0;
right: 0;
bottom: 0;
background: rgba(0, 0, 0, 0.5);
display: flex;
align-items: center;
justify-content: center;
z-index: 1000;
backdrop-filter: blur(4px);
}

.modal-content {
background: white;
border-radius: 16px;
max-width: 600px;
width: 90%;
max-height: 90vh;
overflow-y: auto;
box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
padding: 1.5rem 2rem;
border-radius: 16px 16px 0 0;
display: flex;
justify-content: space-between;
align-items: center;
}

.modal-header h2 {
margin: 0;
font-size: 1.5rem;
}

.btn-close {
background: rgba(255, 255, 255, 0.2);
border: none;
color: white;
font-size: 2rem;
width: 40px;
height: 40px;
border-radius: 50%;
cursor: pointer;
display: flex;
align-items: center;
justify-content: center;
line-height: 1;
}

.btn-close:hover {
background: rgba(255, 255, 255, 0.3);
}

.modal-body {
padding: 2rem;
}

.agente-info {
margin-bottom: 1.5rem;
padding: 1rem;
background: #f8f9fa;
border-radius: 8px;
}

.agente-info strong {
font-size: 1.2rem;
color: #333;
}

.dni-info, .fecha-info {
color: #666;
font-size: 0.9rem;
}

.horario-esperado {
background: linear-gradient(135deg, #fff7e6 0%, #fff3dc 100%);
border-left: 4px solid #ffc107;
padding: 1rem;
border-radius: 8px;
margin-bottom: 1.5rem;
}

.horario-esperado h3 {
margin: 0 0 1rem 0;
color: #856404;
font-size: 1.1rem;
}

.horario-grid {
display: grid;
grid-template-columns: 1fr 1fr;
gap: 1rem;
}

.horario-item {
display: flex;
flex-direction: column;
}

.horario-label {
font-weight: 600;
color: #666;
font-size: 0.9rem;
margin-bottom: 0.25rem;
}

.horario-valor {
font-family: 'Courier New', monospace;
font-size: 1.2rem;
font-weight: 700;
}

.horario-valor.esperado {
color: #ff6f00;
}

.estado-actual {
background: #f8f9fa;
padding: 1rem;
border-radius: 8px;
margin-bottom: 1.5rem;
}

.estado-actual h3 {
margin: 0 0 1rem 0;
color: #333;
font-size: 1.1rem;
}

.estado-grid {
display: grid;
grid-template-columns: 1fr 1fr;
gap: 1rem;
}

.estado-item {
display: flex;
flex-direction: column;
}

.estado-label {
font-weight: 600;
color: #666;
font-size: 0.9rem;
margin-bottom: 0.25rem;
}

.estado-valor {
font-family: 'Courier New', monospace;
font-size: 1.2rem;
font-weight: 700;
}

.estado-valor.marcado {
color: #28a745;
}

.estado-valor.sin-marcar {
color: #dc3545;
}

.observaciones-previas {
background: #fff3cd;
padding: 1rem;
border-radius: 8px;
margin-top: 1rem;
}

.observaciones-previas strong {
color: #856404;
}

.observaciones-previas p {
margin: 0.5rem 0 0 0;
color: #333;
}

.modal-footer {
padding: 1.5rem 2rem;
border-top: 1px solid #e0e0e0;
display: flex;
gap: 1rem;
justify-content: flex-end;
}

.modal-footer button {
padding: 0.75rem 1.5rem;
border: none;
border-radius: 8px;
font-weight: 600;
cursor: pointer;
transition: all 0.3s ease;
}

.btn-cancelar {
background: #e0e0e0;
color: #333;
}

.btn-cancelar:hover {
background: #d0d0d0;
}

.btn-marcar-entrada {
background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
color: white;
}

.btn-marcar-entrada:hover:not(:disabled) {
transform: translateY(-2px);
box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.btn-marcar-salida {
background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
color: white;
}

.btn-marcar-salida:hover:not(:disabled) {
transform: translateY(-2px);
box-shadow: 0 4px 12px rgba(23, 162, 184, 0.4);
}

.modal-footer button:disabled {
opacity: 0.5;
cursor: not-allowed;
}

@media (max-width: 768px) {
.admin-container {
padding: 1rem;
}

.filtros-grid {
grid-template-columns: 1fr;
}

.resumen-grid {
grid-template-columns: repeat(2, 1fr);
}

.tabs {
flex-direction: column;
}

.tabs button {
width: 100%;
}

.table-container {
overflow-x: auto;
}

table {
min-width: 800px;
}

.horario-grid,
.estado-grid {
grid-template-columns: 1fr;
}

.modal-footer {
flex-direction: column;
}

.modal-footer button {
width: 100%;
}
}
</style>
