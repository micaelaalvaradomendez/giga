<script>
	import { createEventDispatcher } from "svelte";

	export let show = false;
	export let asistencia = null;
	export let observacion = "";
	export let horaEntrada = "";
	export let horaSalida = "";
	export let usarHoraEspecifica = false;

	const dispatch = createEventDispatcher();

	function cerrar() {
		dispatch("cerrar");
	}

	function marcarEntrada() {
		dispatch("marcarEntrada");
	}

	function marcarSalida() {
		dispatch("marcarSalida");
	}

	function corregir() {
		dispatch("corregir");
	}

	function marcarAusente() {
		dispatch("marcarAusente");
	}

	function toggleHoraEspecifica() {
		dispatch("toggleHoraEspecifica");
	}

	function formatDate(fecha) {
		if (!fecha) return "-";
		return new Date(fecha).toLocaleDateString("es-AR");
	}

	function formatTime(hora) {
		if (!hora) return "--:--";
		if (typeof hora === "string") {
			return hora.substring(0, 5);
		}
		return "--:--";
	}
</script>

{#if show && asistencia}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={cerrar}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<h2>
					{#if asistencia.hora_entrada || asistencia.hora_salida}
						✏️ Corregir Asistencia
					{:else}
						➕ Marcar Asistencia
					{/if}
				</h2>
				<button class="btn-close" on:click={cerrar}>×</button>
			</div>

			<div class="modal-body">
				<p class="agente-info">
					<strong>{asistencia.agente_nombre}</strong><br />
					<span class="dni-info">DNI: {asistencia.agente_dni}</span><br />
					<span class="fecha-info">{formatDate(asistencia.fecha)}</span>
				</p>

				{#if asistencia.horario_esperado_entrada || asistencia.horario_esperado_salida}
					<div class="horario-esperado">
						<h3>📅 Horario Esperado</h3>
						<div class="horario-grid">
							<div class="horario-item">
								<span class="horario-label">Entrada:</span>
								<span class="horario-valor esperado">
									{asistencia.horario_esperado_entrada
										? formatTime(asistencia.horario_esperado_entrada)
										: "--:--"}
								</span>
							</div>
							<div class="horario-item">
								<span class="horario-label">Salida:</span>
								<span class="horario-valor esperado">
									{asistencia.horario_esperado_salida
										? formatTime(asistencia.horario_esperado_salida)
										: "--:--"}
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
							<span
								class="estado-valor {asistencia.hora_entrada
									? 'marcado'
									: 'sin-marcar'}"
							>
								{asistencia.hora_entrada
									? formatTime(asistencia.hora_entrada)
									: "Sin marcar"}
							</span>
						</div>
						<div class="estado-item">
							<span class="estado-label">Salida:</span>
							<span
								class="estado-valor {asistencia.hora_salida
									? 'marcado'
									: 'sin-marcar'}"
							>
								{asistencia.hora_salida
									? formatTime(asistencia.hora_salida)
									: "Sin marcar"}
							</span>
						</div>
					</div>
				</div>

				{#if asistencia.hora_entrada || asistencia.hora_salida}
					<div class="info-correccion">
						<div class="info-header">
							<span class="info-icon">ℹ️</span>
							<strong>Corrección de Asistencia</strong>
						</div>
						<p>
							Esta asistencia ya tiene marcaciones registradas. Puede corregir las
							horas especificando los nuevos valores.
						</p>
						<p>
							<strong>Importante:</strong> La corrección quedará registrada en el historial
							de auditoría.
						</p>
					</div>
				{/if}

				<div class="form-group">
					<label for="observacion_edit">
						Observación
						{#if asistencia.hora_entrada || asistencia.hora_salida}
							<span class="requerido">*REQUERIDA para corrección</span>
						{:else}
							(opcional)
						{/if}
					</label>
					<textarea
						id="observacion_edit"
						bind:value={observacion}
						placeholder={asistencia.hora_entrada || asistencia.hora_salida
							? "REQUERIDO: Explique el motivo de la corrección (ej: 'Error en marcación original', 'Horario corregido por supervisor')"
							: "Motivo de la corrección (ej: 'Agente olvidó marcar')"}
						rows="3"
						class={(asistencia.hora_entrada || asistencia.hora_salida) &&
						!observacion.trim()
							? "campo-requerido"
							: ""}
					></textarea>
					{#if (asistencia.hora_entrada || asistencia.hora_salida) && !observacion.trim()}
						<small class="error-text">
							⚠️ La observación es obligatoria cuando se corrigen marcaciones
							existentes
						</small>
					{/if}
				</div>

				<!-- Sección para especificar hora -->
				<div class="hora-especifica-section">
					<div class="checkbox-group">
						<input
							type="checkbox"
							id="usar_hora_especifica"
							bind:checked={usarHoraEspecifica}
							on:change={toggleHoraEspecifica}
						/>
						<label for="usar_hora_especifica">
							⏰ Especificar horas manualmente
							<small class="checkbox-help">
								{#if asistencia.hora_entrada || asistencia.hora_salida}
									Permite corregir las horas existentes
								{:else}
									Permite marcar con hora específica en lugar de la hora actual
								{/if}
							</small>
						</label>
					</div>

					{#if usarHoraEspecifica}
						<div class="horas-grid">
							<div class="form-group">
								<label for="hora_entrada_input">
									🕐 Hora de entrada
									{#if asistencia.hora_entrada}
										<span class="actual-time">
											(Actual: {formatTime(asistencia.hora_entrada)})
										</span>
									{/if}
								</label>
								<input
									type="time"
									id="hora_entrada_input"
									bind:value={horaEntrada}
									placeholder="HH:MM"
								/>
								<small class="help-text">
									{#if asistencia.hora_entrada}
										Nueva hora de entrada a registrar
									{:else}
										Solo se usará si marcas entrada
									{/if}
								</small>
							</div>

							<div class="form-group">
								<label for="hora_salida_input">
									🕔 Hora de salida
									{#if asistencia.hora_salida}
										<span class="actual-time">
											(Actual: {formatTime(asistencia.hora_salida)})
										</span>
									{/if}
								</label>
								<input
									type="time"
									id="hora_salida_input"
									bind:value={horaSalida}
									placeholder="HH:MM"
								/>
								<small class="help-text">
									{#if asistencia.hora_salida}
										Nueva hora de salida a registrar
									{:else}
										Solo se usará si marcas salida
									{/if}
								</small>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<div class="modal-footer">
				<button class="btn-cancelar" on:click={cerrar}> Cancelar </button>

				{#if usarHoraEspecifica}
					<!-- Modo corrección con horas específicas -->
					<button
						class="btn-corregir"
						on:click={corregir}
						disabled={(!horaEntrada && !horaSalida) ||
							((asistencia.hora_entrada || asistencia.hora_salida) &&
								!observacion.trim())}
						title={!horaEntrada && !horaSalida
							? "Debe especificar al menos una hora"
							: (asistencia.hora_entrada || asistencia.hora_salida) &&
								  !observacion.trim()
								? "Debe agregar una observación para corregir marcaciones existentes"
								: "Aplicar corrección"}
					>
						✏️ Aplicar Corrección
					</button>
				{:else}
					<!-- Botones para marcación normal -->
					{#if !asistencia.hora_entrada}
						<button class="btn-marcar-entrada" on:click={marcarEntrada}>
							🕐 Marcar Entrada
						</button>
					{/if}

					{#if !asistencia.hora_salida}
						<button
							class="btn-marcar-salida"
							on:click={marcarSalida}
							disabled={!asistencia.hora_entrada}
						>
							🕐 Marcar Salida
						</button>
					{/if}

					<!-- Botón para re-marcar si ya existe -->
					{#if asistencia.hora_entrada}
						<button
							class="btn-remarcar-entrada"
							on:click={marcarEntrada}
							title="Volver a marcar entrada"
						>
							🔄 Re-marcar Entrada
						</button>
					{/if}

					{#if asistencia.hora_salida}
						<button
							class="btn-remarcar-salida"
							on:click={marcarSalida}
							title="Volver a marcar salida"
						>
							🔄 Re-marcar Salida
						</button>
					{/if}

					<!-- Botón para marcar como ausente -->
					{#if asistencia.hora_entrada || asistencia.hora_salida}
						<button
							class="btn-marcar-ausente"
							on:click={marcarAusente}
							title="Marcar como ausente (elimina presentismo)"
						>
							❌ Marcar Ausente
						</button>
					{/if}
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	/* Modal Overlay & Content */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.6);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.modal-content {
		background: white;
		border-radius: 16px;
		width: 100%;
		max-width: 700px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.modal-content::-webkit-scrollbar {
		display: none;
	}

	/* Header */
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
		color: white;
		font-size: 1.5rem;
		font-weight: 600;
	}

	.btn-close {
		background: rgba(255, 255, 255, 0.2);
		border: none;
		color: white;
		font-size: 1.8rem;
		font-weight: 600;
		cursor: pointer;
		padding: 0;
		border-radius: 8px;
		transition: all 0.3s ease;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
	}

	.btn-close:hover {
		background: rgba(255, 255, 255, 0.3);
		transform: scale(1.1);
	}

	/* Modal Body */
	.modal-body {
		padding: 2rem;
	}

	.agente-info {
		background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
		padding: 1rem;
		border-radius: 10px;
		margin-bottom: 1.5rem;
		border-left: 4px solid #667eea;
	}

	.agente-info strong {
		font-size: 1.1rem;
		color: #1e293b;
	}

	.dni-info,
	.fecha-info {
		color: #64748b;
		font-size: 0.9rem;
	}

	/* Horario Esperado */
	.horario-esperado {
		background: #f8fafc;
		padding: 1rem;
		border-radius: 10px;
		margin-bottom: 1rem;
		border: 1px solid #e2e8f0;
	}

	.horario-esperado h3 {
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		color: #475569;
	}

	.horario-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
	}

	.horario-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.horario-label {
		font-size: 0.85rem;
		color: #64748b;
		font-weight: 500;
	}

	.horario-valor {
		font-size: 1.1rem;
		font-weight: 600;
		color: #1e293b;
	}

	.horario-valor.esperado {
		color: #3b82f6;
	}

	/* Estado Actual */
	.estado-actual {
		background: #f0fdf4;
		padding: 1rem;
		border-radius: 10px;
		margin-bottom: 1rem;
		border: 1px solid #bbf7d0;
	}

	.estado-actual h3 {
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		color: #166534;
	}

	.estado-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
	}

	.estado-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.estado-label {
		font-size: 0.85rem;
		color: #15803d;
		font-weight: 500;
	}

	.estado-valor {
		font-size: 1.1rem;
		font-weight: 600;
	}

	.estado-valor.marcado {
		color: #16a34a;
	}

	.estado-valor.sin-marcar {
		color: #dc2626;
		font-style: italic;
	}

	/* Info Corrección */
	.info-correccion {
		background: #fef3c7;
		padding: 1rem;
		border-radius: 10px;
		margin-bottom: 1rem;
		border-left: 4px solid #f59e0b;
	}

	.info-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.info-icon {
		font-size: 1.25rem;
	}

	.info-correccion p {
		margin: 0.5rem 0;
		font-size: 0.9rem;
		color: #78350f;
	}

	/* Form Groups */
	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
		font-size: 0.95rem;
	}

	.requerido {
		color: #dc2626;
		font-size: 0.85rem;
		font-weight: 500;
	}

	.form-group textarea,
	.form-group input[type="time"] {
		width: 100%;
		padding: 0.75rem;
		border: 2px solid #e2e8f0;
		border-radius: 8px;
		font-size: 0.95rem;
		font-family: inherit;
		transition: all 0.2s;
		box-sizing: border-box;
	}

	.form-group textarea:focus,
	.form-group input[type="time"]:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	textarea.campo-requerido {
		border-color: #fca5a5;
		background: #fef2f2;
	}

	.error-text {
		color: #dc2626;
		font-size: 0.85rem;
		margin-top: 0.25rem;
		display: block;
	}

	.help-text {
		color: #64748b;
		font-size: 0.85rem;
		margin-top: 0.25rem;
		display: block;
	}

	.actual-time {
		color: #3b82f6;
		font-size: 0.85rem;
		font-weight: normal;
	}

	/* Checkbox Group */
	.checkbox-group {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}

	.checkbox-group input[type="checkbox"] {
		margin-top: 0.25rem;
		width: 18px;
		height: 18px;
		cursor: pointer;
	}

	.checkbox-group label {
		flex: 1;
		font-weight: 600;
		color: #1e293b;
		cursor: pointer;
	}

	.checkbox-help {
		display: block;
		font-weight: normal;
		color: #64748b;
		font-size: 0.85rem;
		margin-top: 0.25rem;
	}

	.horas-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
		margin-top: 1rem;
	}

	/* Modal Footer */
	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1.5rem 2rem;
		border-top: 1px solid #e2e8f0;
		background: #f8fafc;
		border-radius: 0 0 16px 16px;
		flex-wrap: wrap;
	}

	/* Buttons */
	.modal-footer button {
		padding: 0.75rem 1.25rem;
		border: none;
		border-radius: 8px;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		font-family: inherit;
	}

	.btn-cancelar {
		background: linear-gradient(135deg, #6b7280, #4b5563);
		color: white;
	}

	.btn-cancelar:hover {
		background: linear-gradient(135deg, #4b5563, #374151);
		transform: translateY(-2px);
	}

	.btn-corregir {
		background: linear-gradient(135deg, #f59e0b, #d97706);
		color: white;
	}

	.btn-corregir:hover:not(:disabled) {
		background: linear-gradient(135deg, #d97706, #b45309);
		transform: translateY(-2px);
	}

	.btn-corregir:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-marcar-entrada,
	.btn-remarcar-entrada {
		background: linear-gradient(135deg, #10b981, #059669);
		color: white;
	}

	.btn-marcar-entrada:hover,
	.btn-remarcar-entrada:hover {
		background: linear-gradient(135deg, #059669, #047857);
		transform: translateY(-2px);
	}

	.btn-marcar-salida,
	.btn-remarcar-salida {
		background: linear-gradient(135deg, #3b82f6, #2563eb);
		color: white;
	}

	.btn-marcar-salida:hover:not(:disabled),
	.btn-remarcar-salida:hover {
		background: linear-gradient(135deg, #2563eb, #1d4ed8);
		transform: translateY(-2px);
	}

	.btn-marcar-salida:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-marcar-ausente {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
	}

	.btn-marcar-ausente:hover {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-2px);
	}

	/* Responsive */
	@media (max-width: 640px) {
		.horario-grid,
		.estado-grid,
		.horas-grid {
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
