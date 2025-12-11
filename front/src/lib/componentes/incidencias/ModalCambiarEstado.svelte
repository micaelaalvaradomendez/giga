<script>
	import FormModal from "./FormModal.svelte";

	export let show = false;
	export let incidenciaSeleccionada = null;
	export let estadosDisponibles = [];
	export let nuevoEstado = "";
	export let comentarioEstado = "";
	export let cambiandoEstado = false;
	export let onClose = () => {};
	export let onSubmit = () => {};
</script>

<FormModal
	{show}
	title="Cambiar Estado - {incidenciaSeleccionada?.numero || ''}"
	{onClose}
	{onSubmit}
	submitText="Cambiar Estado"
	isSubmitting={cambiandoEstado}
>
	<div class="estado-actual-info">
		<p>
			<strong>Estado actual:</strong>
			<span class="badge badge-{incidenciaSeleccionada?.estado}">
				{incidenciaSeleccionada?.estado_display ||
					incidenciaSeleccionada?.estado}
			</span>
		</p>
	</div>

	<div class="form-group">
		<label for="nuevo-estado">Nuevo Estado *</label>
		<select
			id="nuevo-estado"
			bind:value={nuevoEstado}
			disabled={cambiandoEstado}
			required
		>
			{#each estadosDisponibles as estado}
				<option value={estado.value}>{estado.label}</option>
			{/each}
		</select>
	</div>

	<div class="form-group">
		<label for="comentario-estado">Comentario (opcional)</label>
		<textarea
			id="comentario-estado"
			bind:value={comentarioEstado}
			placeholder="Agregue un comentario sobre el cambio de estado..."
			rows="3"
			disabled={cambiandoEstado}
		></textarea>
	</div>
</FormModal>

<style>
	.estado-actual-info {
		background: #f8fafc;
		padding: 1rem;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
		margin-bottom: 1.5rem;
	}

	.estado-actual-info p {
		margin: 0;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.95rem;
	}

	.estado-actual-info strong {
		font-weight: 500;
	}

	/* Badge styles para los estados */
	:global(.badge) {
		padding: 0.35rem 0.85rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	:global(.badge-abierta) {
		background: linear-gradient(135deg, #3b82f6, #2563eb);
		color: white;
	}

	:global(.badge-en_proceso) {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
	}

	:global(.badge-pendiente_informacion) {
		background: linear-gradient(135deg, #eab308, #ca8a04);
		color: white;
	}

	:global(.badge-resuelta) {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
	}

	:global(.badge-cerrada) {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
	}

	/* Responsive */
	@media (max-width: 480px) {
		.estado-actual-info p {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.5rem;
		}
	}
</style>
