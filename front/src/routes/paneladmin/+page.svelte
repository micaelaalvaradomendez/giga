<script>
	import { onMount } from "svelte";
	const modules = [
		{
			name: "Usuarios",
			path: "/paneladmin/usuarios",
			description: "Gestionar personal y usuarios",
		},
		{
			name: "Organigrama",
			path: "/paneladmin/organigrama",
			description: "Definir áreas y jerarquías",
		},
		{
			name: "Roles",
			path: "/paneladmin/roles",
			description: "Configurar roles de acceso",
		},
		{
			name: "Asistencias",
			path: "/paneladmin/asistencias",
			description: "Revisar registros de asistencia",
		},
		{
			name: "Licencias(en proceso)",
			path: "/paneladmin/licencias",
			description: "Administrar licencias y novedades",
		},
		{
			name: "Guardias",
			path: "/paneladmin/guardias",
			description: "Planificar guardias y turnos",
		},
		{
			name: "Feriados",
			path: "/paneladmin/feriados",
			description: "Gestionar días no laborables",
		},
		{
			name: "Reportes (proceso)",
			path: "/paneladmin/reportes",
			description: "Generar informes del sistema",
		},
		{
			name: "Parámetros",
			path: "/paneladmin/parametros",
			description:
				"Ajustar la configuración global de Areas y hora de entrada y salida general",
		},
		{
			name: "Auditoría",
			path: "/paneladmin/auditoria",
			description: "Rastrear cambios en el sistema",
		},
	];

	onMount(() => {
		const cards = document.querySelectorAll(".module-card");
		const container = document.querySelector(".modules-space");

		// Mueve las variables en cada card según la posición del mouse
		container.addEventListener("mousemove", (e) => {
			for (const card of cards) {
				const rect = card.getBoundingClientRect();
				const x = e.clientX - rect.left;
				const y = e.clientY - rect.top;
				card.style.setProperty("--mouse-x", `${x}px`);
				card.style.setProperty("--mouse-y", `${y}px`);
			}
		});
	});
</script>

<div class="dashboard-welcome">
	<h1>Panel de Administración GIGA</h1>
</div>

<div class="modules-space">
	{#each modules as module}
		<div class="module-card">
			<div class="module-info">
				<div class="text-content">
					<h2>{module.name}</h2>
					<p>{module.description}</p>
				</div>
				<button
					on:click={() => (window.location.href = module.path)}
					aria-label="Abrir módulo"
				>
					<div class="button-box">
						<span class="button-elem">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
							>
								<path
									d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
								></path>
							</svg>
						</span>
						<span class="button-elem">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
							>
								<path
									d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
								></path>
							</svg>
						</span>
					</div>
				</button>
			</div>
		</div>
	{/each}
</div>

<style>
	.dashboard-welcome {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		position: relative;
		background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
		color: white;
		padding: 30px 20px;
		margin: 5px auto 25px auto;
		max-width: 1200px;
		border-radius: 28px;
		overflow: hidden;
		text-align: center;
		box-shadow:
			0 0 0 1px rgba(255, 255, 255, 0.1) inset,
			0 20px 60px rgba(30, 64, 175, 0.4);
	}

	.dashboard-welcome::before {
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

	.dashboard-welcome h1 {
		margin: 10px;
		font-weight: 800;
		font-size: 30px;
		letter-spacing: 0.2px;
		font-family:
			"Segoe UI",
			system-ui,
			-apple-system,
			"Inter",
			"Roboto",
			"Helvetica Neue",
			Arial,
			sans-serif;
		position: relative;
		padding-bottom: 12px;
		overflow: hidden;
		display: inline-block;
	}

	.dashboard-welcome h1::after {
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

	.modules-space {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		width: 90%;
		display: grid;
		margin-top: 50px;
		margin-right: auto;
		margin-left: auto;
		grid-template-rows: repeat(3, 1fr);
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
	}

	.module-card {
		--color: 25 90% 60%;
		display: flex;
		flex-direction: column;
		position: relative;
		overflow: hidden;
		justify-content: flex-start;
		align-items: flex-start;
		background-color: rgba(255, 255, 255, 0.08);
		border: 2.3px solid hsl(var(--color) / 0.2);
		border-radius: 10px;
		padding: 1.25rem 1.5rem;
		text-decoration: none;
		color: inherit;
		transition: all 0.3s ease;
		min-height: 100px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
		isolation: isolate;
	}

	.module-card::before {
		content: "";
		position: absolute;
		inset: 0;
		z-index: 0;
		pointer-events: none;
		border-radius: inherit;
		background: radial-gradient(
			500px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
			hsl(var(--color) / 0.4),
			rgba(255, 255, 255, 0.03) 40%,
			transparent 70%
		);

		opacity: 0;
		transition:
			opacity 0.28s ease,
			transform 0.28s ease;
		transform: scale(1.05);
	}

	.module-card:hover::before {
		opacity: 1;
		transform: scale(1);
	}

	.module-card:hover {
		transform: translateY(-8px);
		cursor: pointer;
	}

	.module-card .module-info {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
		width: 100%;
		height: 100%;
	}

	.module-info .text-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.module-info h2 {
		font-size: 1.3rem;
		margin: 0;
		font-weight: 600;
		color: #2c3e50;
		line-height: 1.2;
	}

	.module-info p {
		font-size: 0.9rem;
		color: #6c757d;
		line-height: 1.3;
		margin: 0;
	}

	.module-info button {
		display: block;
		position: relative;
		width: 56px;
		height: 56px;
		margin: 0;
		overflow: hidden;
		outline: none;
		background-color: transparent;
		cursor: pointer;
		border: 0;
		flex-shrink: 0;
	}

	.module-info button:before,
	.module-info button:after {
		content: "";
		position: absolute;
		border-radius: 50%;
		inset: 7px;
	}

	.module-info button:before {
		border: 4px solid #a39e98;
		transition:
			opacity 0.4s cubic-bezier(0.77, 0, 0.175, 1) 80ms,
			transform 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) 80ms;
	}

	.module-info button:after {
		border: 4px solid #e0981b;
		transform: scale(1.3);
		transition:
			opacity 0.4s cubic-bezier(0.165, 0.84, 0.44, 1),
			transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
		opacity: 0;
	}

	.module-info button:hover:before,
	.module-info button:focus:before {
		opacity: 1;
		transform: scale(1);
		transition:
			opacity 0.4s cubic-bezier(0.77, 0, 0.175, 1) 80ms,
			transform 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) 80ms;
	}

	.module-info button:hover:after,
	.module-info button:focus:after {
		opacity: 1;
		transform: scale(1);
		transition:
			opacity 0.4s cubic-bezier(0.77, 0, 0.175, 1) 80ms,
			transform 0.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) 80ms;
	}

	.button-box {
		display: flex;
		position: absolute;
		top: 0;
		left: 0;
	}

	.button-elem {
		display: block;
		width: 20px;
		height: 20px;
		margin: 17px 18px 0 18px;
		fill: #24201c;
	}

	.button-elem svg {
		width: 100%;
		height: 100%;
		fill: inherit;
	}

	.module-info button:hover .button-elem {
		fill: #533e19;
	}

	.module-info button:hover .button-box,
	.module-info button:focus .button-box {
		transition: 0.4s;
		transform: translateX(-56px);
	}

	@keyframes moveLine {
		0% {
			left: -40%;
		}
		100% {
			left: 100%;
		}
	}

	@media (max-width: 768px) {
		.modules-space {
			grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		}
		.module-card {
			padding: 1rem;
			min-height: 140px;
		}
		.module-info h2 {
			font-size: 1.1rem;
		}

		.module-info p {
			font-size: 0.85rem;
		}

		.dashboard-welcome {
			margin: -2rem -1rem 2rem -1rem;
			padding: 1.5rem;
		}

		.dashboard-welcome h1 {
			font-size: 2rem;
		}
	}
</style>
