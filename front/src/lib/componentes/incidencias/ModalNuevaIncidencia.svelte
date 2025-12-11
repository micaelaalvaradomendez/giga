<script>
	import FormModal from "./FormModal.svelte";

	export let show = false;
	export let userRole = "";
	export let nuevaIncidencia = {};
	export let jefesArea = [];
	export let cargandoJefes = false;
	export let creandoIncidencia = false;
	export let onClose = () => {};
	export let onSubmit = () => {};
</script>

<FormModal
	{show}
	title="Nueva Incidencia"
	{onClose}
	{onSubmit}
	submitText="Crear Incidencia"
	isSubmitting={creandoIncidencia}
>
	<div class="form-group">
		<label for="titulo">Título *</label>
		<input
			id="titulo"
			type="text"
			bind:value={nuevaIncidencia.titulo}
			placeholder="Título de la incidencia"
			required
			disabled={creandoIncidencia}
		/>
	</div>

	<div class="form-group">
		<label for="descripcion">Descripción *</label>
		<textarea
			id="descripcion"
			bind:value={nuevaIncidencia.descripcion}
			placeholder="Describe detalladamente la incidencia"
			rows="4"
			required
			disabled={creandoIncidencia}
		></textarea>
	</div>

	<div class="form-group">
		<label for="prioridad">Prioridad *</label>
		<select
			id="prioridad"
			bind:value={nuevaIncidencia.prioridad}
			disabled={creandoIncidencia}
			required
		>
			<option value="baja">Baja</option>
			<option value="media">Media</option>
			<option value="alta">Alta</option>
			<option value="critica">Crítica</option>
		</select>
	</div>

	<!-- Selector de jefe -->
	<div class="form-group">
		<label for="asignado_a">
			{userRole === "Agente"
				? "Asignar a Jefatura *"
				: "Asignar a Agente *"}
		</label>
		{#if cargandoJefes}
			<div class="loading-jefes">
				Cargando {userRole === "Agente" ? "jefes" : "agentes"}...
			</div>
		{:else if jefesArea.length > 0}
			<select
				id="asignado_a"
				bind:value={nuevaIncidencia.asignado_a_id}
				disabled={creandoIncidencia}
				required
			>
				<option value={null}>
					Seleccione {userRole === "Agente" ? "un jefe" : "un agente"}
				</option>
				{#each jefesArea as jefe}
					<option value={jefe.id}>{jefe.nombre} ({jefe.rol})</option>
				{/each}
			</select>
		{:else}
			<div class="no-jefes">
				No hay {userRole === "Agente" ? "jefes" : "agentes"} disponibles
				en su área
			</div>
		{/if}
	</div>
</FormModal>

<style>
	.loading-jefes {
		padding: 0.75rem;
		text-align: center;
		color: #6b7280;
		font-style: italic;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		background: #f9fafb;
	}

	.no-jefes {
		padding: 0.75rem;
		text-align: center;
		color: #dc2626;
		border: 2px solid #fecaca;
		border-radius: 8px;
		background: #fee2e2;
		font-weight: 500;
	}

	/* Responsive */
	@media (max-width: 480px) {
		.loading-jefes,
		.no-jefes {
			font-size: 0.875rem;
			padding: 0.65rem;
		}
	}
</style>
