<script>
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { API_BASE_URL } from "$lib/api.js";
	import LoadingSpinner from "$lib/componentes/LoadingSpinner.svelte";

	let dni = "";
	let loading = false;
	let loadingEstado = true; // Indicador de carga inicial
	let mensaje = null;
	let mensajeTipo = null; // 'success', 'error', 'info'
	let estado = {
		tiene_entrada: false,
		tiene_salida: false,
		hora_entrada: null,
		hora_salida: null,
		puede_marcar_entrada: true,
		puede_marcar_salida: false,
	};
	let agente = null;

	onMount(async () => {
		// Verificar sesión
		try {
			const sessionResponse = await fetch(
				`${API_BASE_URL}/personas/auth/check-session/`,
				{
					credentials: "include",
				},
			);

			if (!sessionResponse.ok) {
				goto("/");
				return;
			}

			const sessionData = await sessionResponse.json();

			if (!sessionData.authenticated) {
				goto("/");
				return;
			}

			agente = sessionData.user;

			// Cargar estado de asistencia
			await cargarEstado();
		} catch (error) {
			console.error("Error al verificar sesión:", error);
			goto("/");
		}
	});

	async function cargarEstado() {
		try {
			const response = await fetch(`${API_BASE_URL}/asistencia/estado/`, {
				credentials: "include",
			});

			if (response.ok) {
				const data = await response.json();
				if (data.success) {
					estado = data.data;
				}
			}
		} catch (error) {
			console.error("Error al cargar estado:", error);
		} finally {
			loadingEstado = false;
		}
	}

	async function marcarAsistencia() {
		if (!dni.trim()) {
			mostrarMensaje("Por favor ingrese su DNI", "error");
			return;
		}

		loading = true;
		mensaje = null;

		try {
			const response = await fetch(`${API_BASE_URL}/asistencia/marcar/`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				credentials: "include",
				body: JSON.stringify({ dni: dni.trim() }),
			});

			const data = await response.json();

			if (data.success) {
				mostrarMensaje(data.message, "success");
				dni = "";
				await cargarEstado();
			} else {
				if (data.tipo === "error_dni") {
					mostrarMensaje(
						"⚠️ " +
							data.message +
							" - Este intento ha sido registrado en auditoría",
						"error",
					);
				} else if (data.tipo === "ya_completo") {
					mostrarMensaje(data.message, "info");
				} else if (data.tipo === "dia_no_laborable") {
					mostrarMensaje("📅 " + data.message, "info");
				} else {
					mostrarMensaje(data.message, "error");
				}
			}
		} catch (error) {
			console.error("Error al marcar asistencia:", error);
			mostrarMensaje("Error de conexión. Intente nuevamente.", "error");
		} finally {
			loading = false;
		}
	}

	function mostrarMensaje(texto, tipo) {
		mensaje = texto;
		mensajeTipo = tipo;

		setTimeout(() => {
			mensaje = null;
			mensajeTipo = null;
		}, 5000);
	}

	function formatTime(time) {
		if (!time) return "--:--";
		return time.substring(0, 5);
	}
</script>

<svelte:head>
	<title>Asistencia - Sistema GIGA</title>
</svelte:head>

<div class="asistencia-container">
	<div class="header">
		<h1>Registro de Asistencia</h1>
		{#if agente}
			<p class="agente-info">
				{agente.nombre}
				{agente.apellido}
			</p>
			{#if agente.horario_entrada || agente.horario_salida}
				<div class="horario-asignado">
					<span class="horario-label">Tu horario:</span>
					<span class="horario-value">
						{agente.horario_entrada || "--:--"} - {agente.horario_salida ||
							"--:--"}
					</span>
				</div>
			{/if}
		{/if}
	</div>

	<!-- Estado actual -->
	{#if loadingEstado}
		<div class="estado-card">
			<LoadingSpinner message="Cargando estado de asistencia..." />
		</div>
	{:else if estado.es_dia_no_laborable}
		<div class="estado-card no-laborable">
			<h2>Día No Laborable</h2>
			<div class="mensaje-no-laborable">
				<div class="icono-grande">🏖️</div>
				<p>Hoy es <strong>{estado.motivo_no_laborable}</strong></p>
				<p>No se registra asistencia en este día.</p>
			</div>
		</div>
	{:else}
		<div class="estado-card">
			<h2>📊 Estado de Hoy</h2>
			<div class="estado-grid">
				<div
					class="estado-item {estado.tiene_entrada
						? 'activo'
						: 'inactivo'}"
				>
					<div class="icono">
						{#if estado.tiene_entrada}
							✅
						{:else}
							⏹️
						{/if}
					</div>
					<div class="info">
						<span class="label">Entrada</span>
						<span class="hora"
							>{formatTime(estado.hora_entrada)}</span
						>
					</div>
				</div>

				<div
					class="estado-item {estado.tiene_salida
						? 'activo'
						: 'inactivo'}"
				>
					<div class="icono">
						{#if estado.tiene_salida}
							✅
						{:else}
							⏹️
						{/if}
					</div>
					<div class="info">
						<span class="label">Salida</span>
						<span class="hora"
							>{formatTime(estado.hora_salida)}</span
						>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<div class="content-grid">
		<!-- Formulario de marcación -->
		{#if !loadingEstado && !estado.es_dia_no_laborable && (estado.puede_marcar_entrada || estado.puede_marcar_salida)}
			<div class="marcacion-card">
				<h2>
					{#if estado.puede_marcar_entrada}
						🟢 Marcar Entrada
					{:else if estado.puede_marcar_salida}
						🟠 Marcar Salida
					{/if}
				</h2>

				<form on:submit|preventDefault={marcarAsistencia}>
					<div class="form-group">
						<label for="dni">Ingrese su DNI</label>
						<input
							type="text"
							id="dni"
							bind:value={dni}
							placeholder="Ej: 12345678"
							disabled={loading}
							maxlength="8"
							pattern="[0-9]*"
							inputmode="numeric"
							autocomplete="off"
						/>
						<p class="hint">El DNI debe coincidir con su usuario</p>
					</div>

					<button
						type="submit"
						class="btn-marcar {estado.puede_marcar_entrada
							? 'entrada'
							: 'salida'}"
						disabled={loading}
					>
						{#if loading}
							Registrando...
						{:else if estado.puede_marcar_entrada}
							Marcar Entrada
						{:else}
							Marcar Salida
						{/if}
					</button>
				</form>
			</div>
		{:else if !loadingEstado}
			<div class="completado-card">
				<div class="icono-grande">✅</div>
				<h2>Asistencia Completa</h2>
				<p>Ya has registrado tu entrada y salida de hoy.</p>
				<div class="horarios">
					<div>
						<strong>Entrada:</strong>
						{formatTime(estado.hora_entrada)}
					</div>
					<div>
						<strong>Salida:</strong>
						{formatTime(estado.hora_salida)}
					</div>
				</div>
			</div>
		{/if}

		<!-- Información adicional -->
		<div class="info-card">
			<h3>ℹ Información Importante</h3>
			<ul>
				<li>Debe marcar su entrada al llegar al trabajo.</li>
				<li>Debe marcar su salida antes de retirarse.</li>
				<li>Solo puede realizar una entrada y una salida por día.</li>
				<li>El DNI ingresado debe coincidir con su usuario.</li>
				<li>
					Si no marca salida, el sistema la registrará automáticamente
					a las <strong>22:00</strong>.
				</li>
				<li>
					Cualquier intento de marcación con DNI incorrecto quedará
					registrado.
				</li>
			</ul>
		</div>
	</div>

	<!-- Mensaje -->
	{#if mensaje}
		<div class="mensaje {mensajeTipo}">
			{mensaje}
		</div>
	{/if}
</div>

<style>
	.asistencia-container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem 1rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.header {
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 16px 12px;
		max-width: 100%;
		border-radius: 16px;
		overflow: hidden;
		text-align: center;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 10px 30px rgba(30, 64, 175, 0.4);
		margin-bottom: 20px;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
		box-sizing: border-box;
		width: 100%;
	}

	@media (min-width: 640px) {
		.header {
			padding: 20px 24px;
			border-radius: 20px;
			margin-bottom: 24px;
		}
	}

	@media (min-width: 768px) {
		.header {
			padding: 25px 30px;
			border-radius: 24px;
			margin-bottom: 28px;
		}
	}

	@media (min-width: 1024px) {
		.header {
			padding: 30px 40px;
			max-width: 1200px;
			border-radius: 28px;
			margin-bottom: 30px;
		}
	}

	.header::before {
		content: "";
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-image: linear-gradient(
				90deg,
				rgba(255, 255, 255, 0.03) 1px,
				transparent 1px
			),
			linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
		background-size: 50px 50px;
		animation: moveLines 20s linear infinite;
	}

	.header h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 20px;
		letter-spacing: 0.2px;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: block;
		max-width: 100%;
		word-wrap: break-word;
	}

	@media (min-width: 480px) {
		.header h1 {
			font-size: 24px;
		}
	}

	@media (min-width: 640px) {
		.header h1 {
			font-size: 28px;
			display: inline-block;
		}
	}

	@media (min-width: 768px) {
		.header h1 {
			font-size: 32px;
		}
	}

	@media (min-width: 1024px) {
		.header h1 {
			font-size: 35px;
		}
	}

	.header h1::after {
		content: "";
		position: absolute;
		width: 40%;
		height: 3px;
		bottom: 0;
		left: 0;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(255, 255, 255, 0.9),
			transparent
		);
		animation: moveLine 2s linear infinite;
	}

	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
	}

	.agente-info {
		color: #0d47a1;
		font-weight: 600;
		font-size: 20px;
		margin-top: 0.5rem;
		margin-bottom: 10px;
		padding: 0.5rem 1rem;
		background: #e3f2fd;
		border-radius: 8px;
		display: inline-flex;
	}

	.horario-asignado {
		padding: 0.5rem 1rem;
		background: #e3f2fd;
		border-radius: 8px;
		display: inline-flex;
	}

	.horario-label {
		color: #014488;
		font-weight: 600;
		margin-right: 0.5rem;
	}

	.horario-value {
		font-weight: 600;
		font-size: 1.1rem;
		color: #0d47a1;
	}

	/* Estado Card */
	.estado-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		margin-bottom: 1.5rem;
	}

	.estado-card h2 {
		font-size: 25px;
		color: #1a1a1a;
		margin-bottom: 1rem;
		text-align: center;
	}

	.estado-card.no-laborable {
		background: linear-gradient(135deg, #e3f2fd 0%, #f1f8e9 100%);
		border: 2px solid #4caf50;
	}

	.mensaje-no-laborable {
		text-align: center;
		padding: 2rem;
	}

	.icono-grande {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.mensaje-no-laborable p {
		font-size: 1.2rem;
		margin-bottom: 0.5rem;
		color: #2e7d32;
	}

	.mensaje-no-laborable strong {
		color: #1b5e20;
		font-weight: 600;
	}

	.estado-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		max-width: 800px;
		margin: 0 auto;
	}

	.estado-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1.5rem;
		border-radius: 8px;
		background: #f8f8f8;
	}

	.estado-item.activo {
		background: #e8f5e9;
		border: 2px solid #4caf50;
	}

	.estado-item.inactivo {
		background: #f5f5f5;
		border: 2px solid #e0e0e0;
	}

	.estado-item .icono {
		font-size: 2.5rem;
	}

	.estado-item .info {
		display: flex;
		flex-direction: column;
		flex: 1;
	}

	.estado-item .label {
		font-size: 0.9rem;
		color: #666;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.estado-item .hora {
		font-size: 2rem;
		font-weight: bold;
		color: #1a1a1a;
	}

	/* Mensajes */
	.mensaje {
		margin-top: 30px;
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1.5rem;
		font-weight: 500;
		text-align: center;
	}

	.mensaje.success {
		background: #e8f5e9;
		color: #2e7d32;
		border: 2px solid #4caf50;
	}

	.mensaje.error {
		background: #ffebee;
		color: #c62828;
		border: 2px solid #f44336;
	}

	.mensaje.info {
		background: #e3f2fd;
		color: #1565c0;
		border: 2px solid #2196f3;
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}

	/* Marcación Card */
	.marcacion-card {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}

	.marcacion-card h2 {
		font-size: 1.3rem;
		color: #1a1a1a;
		margin-bottom: 1.5rem;
		text-align: center;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	.form-group label {
		display: block;
		font-weight: 600;
		color: #1a1a1a;
		margin-bottom: 0.5rem;
	}

	.form-group input {
		width: 100%;
		padding: 0.75rem;
		font-size: 1rem;
		border: 2px solid #e0e0e0;
		border-radius: 8px;
		transition: border-color 0.2s;
	}

	.form-group input:focus {
		outline: none;
		border-color: #2196f3;
	}

	.form-group input:disabled {
		background: #f5f5f5;
		cursor: not-allowed;
	}

	.hint {
		font-size: 0.85rem;
		color: #ff6b35;
		margin-top: 0.5rem;
	}

	.btn-marcar {
		width: 100%;
		padding: 1rem;
		font-size: 1.1rem;
		font-weight: 600;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-marcar.entrada {
		background: #4caf50;
		color: white;
		transform: translateY(-2px);
	}

	.btn-marcar.entrada:hover:not(:disabled) {
		background: #45a049;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
	}

	.btn-marcar.salida {
		background: #ff9800;
		color: white;
		transform: translateY(-2px);
	}

	.btn-marcar.salida:hover:not(:disabled) {
		background: #fb8c00;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
	}

	.btn-marcar:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	/* Completado Card */
	.completado-card {
		background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
		border-radius: 12px;
		padding: 2rem;
		text-align: center;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}

	.icono-grande {
		font-size: 4rem;
		margin-bottom: 1rem;
	}

	.completado-card h2 {
		color: #2e7d32;
		margin-bottom: 0.5rem;
	}

	.completado-card p {
		color: #666;
		margin-bottom: 1rem;
	}

	.horarios {
		display: flex;
		justify-content: center;
		gap: 2rem;
		font-size: 1.1rem;
		color: #1a1a1a;
	}

	/* Info Card */
	.info-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		border-left: 4px solid #ff9800;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}

	.info-card h3 {
		color: #e65100;
		margin-bottom: 1rem;
	}

	.info-card ul {
		list-style: none;
		padding: 0;
	}

	.info-card li {
		color: #5d4037;
		margin-bottom: 0.5rem;
		padding-left: 1.5rem;
		position: relative;
		line-height: 1.5;
	}

	.info-card li::before {
		content: "•";
		position: absolute;
		left: 0.5rem;
		color: #ff9800;
		font-weight: bold;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: 1fr;
		}

		.estado-grid {
			grid-template-columns: 1fr;
		}

		.horarios {
			flex-direction: column;
			gap: 0.5rem;
		}
	}
</style>
