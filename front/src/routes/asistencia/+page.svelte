<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let dni = '';
	let loading = false;
	let mensaje = null;
	let mensajeTipo = null; // 'success', 'error', 'info'
	let estado = {
		tiene_entrada: false,
		tiene_salida: false,
		hora_entrada: null,
		hora_salida: null,
		puede_marcar_entrada: true,
		puede_marcar_salida: false
	};
	let agente = null;

	onMount(async () => {
		// Verificar sesión
		try {
			const sessionResponse = await fetch('/api/personas/auth/check-session/', {
				credentials: 'include'
			});

			if (!sessionResponse.ok) {
				goto('/');
				return;
			}

			const sessionData = await sessionResponse.json();
			
			if (!sessionData.authenticated) {
				goto('/');
				return;
			}

			agente = sessionData.user;

			// Cargar estado de asistencia
			await cargarEstado();
		} catch (error) {
			console.error('Error al verificar sesión:', error);
			goto('/');
		}
	});

	async function cargarEstado() {
		try {
			const response = await fetch('/api/asistencia/estado/', {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				if (data.success) {
					estado = data.data;
				}
			}
		} catch (error) {
			console.error('Error al cargar estado:', error);
		}
	}

	async function marcarAsistencia() {
		if (!dni.trim()) {
			mostrarMensaje('Por favor ingrese su DNI', 'error');
			return;
		}

		loading = true;
		mensaje = null;

		try {
			const response = await fetch('/api/asistencia/marcar/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({ dni: dni.trim() })
			});

			const data = await response.json();

			if (data.success) {
				mostrarMensaje(data.message, 'success');
				dni = '';
				await cargarEstado();
			} else {
				if (data.tipo === 'error_dni') {
					mostrarMensaje(
						'⚠️ ' + data.message + ' - Este intento ha sido registrado en auditoría',
						'error'
					);
				} else if (data.tipo === 'ya_completo') {
					mostrarMensaje(data.message, 'info');
				} else {
					mostrarMensaje(data.message, 'error');
				}
			}
		} catch (error) {
			console.error('Error al marcar asistencia:', error);
			mostrarMensaje('Error de conexión. Intente nuevamente.', 'error');
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
		if (!time) return '--:--';
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
						{agente.horario_entrada || '--:--'} - {agente.horario_salida || '--:--'}
					</span>
				</div>
			{/if}
		{/if}
	</div>

	<!-- Estado actual -->
	<div class="estado-card">
		<h2>Estado de Hoy</h2>
		<div class="estado-grid">
			<div class="estado-item {estado.tiene_entrada ? 'activo' : 'inactivo'}">
				<div class="icono">
					{#if estado.tiene_entrada}
						✅
					{:else}
						⏹️
					{/if}
				</div>
				<div class="info">
					<span class="label">Entrada</span>
					<span class="hora">{formatTime(estado.hora_entrada)}</span>
				</div>
			</div>

			<div class="estado-item {estado.tiene_salida ? 'activo' : 'inactivo'}">
				<div class="icono">
					{#if estado.tiene_salida}
						✅
					{:else}
						⏹️
					{/if}
				</div>
				<div class="info">
					<span class="label">Salida</span>
					<span class="hora">{formatTime(estado.hora_salida)}</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Mensaje -->
	{#if mensaje}
		<div class="mensaje {mensajeTipo}">
			{mensaje}
		</div>
	{/if}

	<!-- Formulario de marcación -->
	{#if estado.puede_marcar_entrada || estado.puede_marcar_salida}
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
					<p class="hint"> El DNI debe coincidir con su usuario</p>
				</div>

				<button
					type="submit"
					class="btn-marcar {estado.puede_marcar_entrada ? 'entrada' : 'salida'}"
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
	{:else}
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
		<h3>ℹInformación Importante</h3>
		<ul>
			<li>Debe marcar su entrada al llegar al trabajo.</li>
			<li>Debe marcar su salida antes de retirarse.</li>
			<li>Solo puede realizar una entrada y una salida por día.</li>
			<li>El DNI ingresado debe coincidir con su usuario.</li>
			<li>
				Si no marca salida, el sistema la registrará automáticamente a las <strong>22:00</strong>.
			</li>
			<li>Cualquier intento de marcación con DNI incorrecto quedará registrado.</li>
		</ul>
	</div>
</div>

<style>
	.asistencia-container {
		max-width: 600px;
		margin: 0 auto;
		padding: 2rem 1rem;
	}

	.header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.header h1 {
		font-size: 2rem;
		color: #1a1a1a;
		margin-bottom: 0.5rem;
	}

	.agente-info {
		color: #666;
		font-size: 1.1rem;
	}

	.horario-asignado {
		margin-top: 0.5rem;
		padding: 0.5rem 1rem;
		background: #e3f2fd;
		border-radius: 8px;
		display: inline-block;
	}

	.horario-label {
		color: #1976d2;
		font-weight: 500;
		margin-right: 0.5rem;
	}

	.horario-value {
		color: #0d47a1;
		font-weight: 600;
		font-size: 1.1rem;
	}

	/* Estado Card */
	.estado-card {
		background: white;
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 1.5rem;
	}

	.estado-card h2 {
		font-size: 1.2rem;
		color: #1a1a1a;
		margin-bottom: 1rem;
	}

	.estado-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.estado-item {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
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
		font-size: 2rem;
	}

	.estado-item .info {
		display: flex;
		flex-direction: column;
	}

	.estado-item .label {
		font-size: 0.9rem;
		color: #666;
	}

	.estado-item .hora {
		font-size: 1.5rem;
		font-weight: bold;
		color: #1a1a1a;
	}

	/* Mensajes */
	.mensaje {
		padding: 1rem;
		border-radius: 8px;
		margin-bottom: 1.5rem;
		font-weight: 500;
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

	/* Marcación Card */
	.marcacion-card {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 1.5rem;
	}

	.marcacion-card h2 {
		font-size: 1.3rem;
		color: #1a1a1a;
		margin-bottom: 1.5rem;
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
	}

	.btn-marcar.entrada:hover:not(:disabled) {
		background: #45a049;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
	}

	.btn-marcar.salida {
		background: #ff9800;
		color: white;
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
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 1.5rem;
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
		background: #fff3e0;
		border-radius: 12px;
		padding: 1.5rem;
		border-left: 4px solid #ff9800;
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
	}

	.info-card li::before {
		content: '•';
		position: absolute;
		left: 0.5rem;
		color: #ff9800;
		font-weight: bold;
	}

	/* Responsive */
	@media (max-width: 600px) {
		.estado-grid {
			grid-template-columns: 1fr;
		}

		.horarios {
			flex-direction: column;
			gap: 0.5rem;
		}
	}
</style>
