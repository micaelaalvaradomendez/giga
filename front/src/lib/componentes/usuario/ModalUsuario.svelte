<script>
	import { createEventDispatcher } from "svelte";
	import AuthService from "../../login/authService.js";

	export let isOpen = false;
	export let user = null;

	const dispatch = createEventDispatcher();

	function cerrarModal() {
		dispatch("cerrar");
	}

	function editarPerfil() {
		dispatch("editarPerfil");
	}

	function cerrarSesion() {
		dispatch("cerrarSesion");
	}

	function formatCuil(cuil) {
		if (!cuil) return "N/A";
		return AuthService.formatCuil(cuil);
	}

	function formatearHoraLogin(fechaHora) {
		if (!fechaHora) return "N/A";
		try {
			const fecha = new Date(fechaHora);
			const horas = fecha.getHours().toString().padStart(2, "0");
			const minutos = fecha.getMinutes().toString().padStart(2, "0");
			return `${horas}:${minutos}`;
		} catch (e) {
			return "N/A";
		}
	}

	function formatearFechaLogin(fechaHora) {
		if (!fechaHora) return "N/A";
		try {
			const fecha = new Date(fechaHora);
			return fecha.toLocaleDateString("es-AR", {
				day: "2-digit",
				month: "2-digit",
				year: "numeric",
			});
		} catch (e) {
			return "N/A";
		}
	}

	function getRoleBadgeClass(rol) {
		const roleClasses = {
			Administrador: "role-admin",
			Director: "role-director",
			Jefatura: "role-jefatura",
			"Agente Avanzado": "role-agente-avanzado",
			Agente: "role-agente",
		};
		return roleClasses[rol] || "role-default";
	}
</script>

{#if isOpen && user}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="modal-overlay" on:click={cerrarModal}>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="modal-content" on:click|stopPropagation>
			<div class="modal-header">
				<div class="avatar-container">
					<div class="avatar-circle">
						{user.first_name
							?.charAt(0)
							.toUpperCase()}{user.last_name
							?.charAt(0)
							.toUpperCase()}
					</div>
				</div>
				<button class="btn-close" on:click={cerrarModal}>×</button>
			</div>

			<div class="modal-body">
				<h2 class="nombre-usuario">{user.nombre_completo}</h2>

				<div class="info-grid">
					<div class="info-item">
						<span class="icon">📧</span>
						<div class="info-content">
							<span class="info-label">Email</span>
							<span class="info-value">{user.email}</span>
						</div>
					</div>

					<div class="info-item">
						<span class="icon">🆔</span>
						<div class="info-content">
							<span class="info-label">CUIL</span>
							<span class="info-value"
								>{formatCuil(user.cuil)}</span
							>
						</div>
					</div>

					{#if user.area}
						<div class="info-item">
							<span class="icon">🏢</span>
							<div class="info-content">
								<span class="info-label">Área</span>
								<span class="info-value"
									>{typeof user.area === "object"
										? user.area.nombre
										: user.area}</span
								>
							</div>
						</div>
					{/if}

					{#if user.roles && user.roles.length > 0}
						<div class="info-item roles-item">
							<span class="icon">👤</span>
							<div class="info-content">
								<span class="info-label">Roles</span>
								<div class="roles-badges">
									{#each user.roles as role}
										<span
											class="role-badge {getRoleBadgeClass(
												role.nombre,
											)}"
										>
											{role.nombre}
										</span>
									{/each}
								</div>
							</div>
						</div>
					{/if}

					{#if user.last_login}
						<div class="info-item">
							<span class="icon">🕐</span>
							<div class="info-content">
								<span class="info-label">Última sesión</span>
								<span class="info-value">
									{formatearFechaLogin(user.last_login)} - {formatearHoraLogin(
										user.last_login,
									)}
								</span>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<div class="modal-footer">
				<button class="btn-secondary" on:click={editarPerfil}>
					✏️ Editar Perfil
				</button>
				<button class="btn-danger" on:click={cerrarSesion}>
					🚪 Cerrar Sesión
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 10000;
		backdrop-filter: blur(4px);
	}

	.modal-content {
		background: white;
		border-radius: 16px;
		width: 90%;
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s ease-out;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.modal-header {
		position: relative;
		padding: 2rem 2rem 1rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 16px 16px 0 0;
	}

	.avatar-container {
		margin-bottom: 1rem;
	}

	.avatar-circle {
		width: 80px;
		height: 80px;
		border-radius: 50%;
		background: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2rem;
		font-weight: bold;
		color: #667eea;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		border: 3px solid rgba(255, 255, 255, 0.3);
	}

	.btn-close {
		position: absolute;
		top: 1rem;
		right: 1rem;
		background: rgba(255, 255, 255, 0.2);
		border: none;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		font-size: 2rem;
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
		font-weight: 300;
	}

	.btn-close:hover {
		transform: scale(1.2) rotate(90deg);
		color: rgba(255, 255, 255, 0.8);
	}

	.modal-body {
		padding: 2rem;
	}

	.nombre-usuario {
		text-align: center;
		font-size: 1.75rem;
		font-weight: 700;
		color: #1a1a1a;
		margin: 0 0 1.5rem 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		position: relative;
		padding-bottom: 0.75rem;
	}

	.nombre-usuario::after {
		content: "";
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 60px;
		height: 3px;
		background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
		border-radius: 2px;
	}

	.info-grid {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.info-item {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 12px;
		transition: all 0.2s;
	}

	.info-item:hover {
		background: #e9ecef;
		transform: translateX(4px);
	}

	.icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}

	.info-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.info-label {
		font-size: 0.75rem;
		color: #6c757d;
		text-transform: uppercase;
		font-weight: 600;
		letter-spacing: 0.5px;
	}

	.info-value {
		font-size: 18px;
		color: #1a1a1a;
		font-weight: 500;
	}

	.roles-item {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 12px;
		transition: all 0.2s;
	}

	.roles-item:hover {
		background: #e9ecef;
		transform: translateX(4px);
	}

	.roles-item .icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}
	.roles-item .info-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.roles-badges {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		width: 100%;
	}

	.role-badge {
		padding: 0.5rem 1rem;
		border-radius: 20px;
		font-size: 0.85rem;
		font-weight: 600;
		color: white;
		display: inline-block;
		white-space: nowrap;
	}

	.role-admin {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
	}

	.role-director {
		background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
	}

	.role-jefatura {
		background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
	}

	.role-agente-avanzado {
		background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
	}

	.role-agente {
		background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
		color: #333;
	}

	.role-default {
		background: #6c757d;
	}

	.modal-footer {
		padding: 1.5rem 2rem;
		display: flex;
		gap: 1rem;
		border-top: 1px solid #e9ecef;
	}

	.btn-secondary,
	.btn-danger {
		flex: 1;
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 8px;
		font-size: 18px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.btn-secondary {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.btn-secondary:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}

	.btn-danger {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
		color: white;
	}

	.btn-danger:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
	}

	@media (max-width: 768px) {
		.modal-content {
			width: 95%;
			margin: 1rem;
		}

		.modal-footer {
			flex-direction: column;
		}
	}
</style>
