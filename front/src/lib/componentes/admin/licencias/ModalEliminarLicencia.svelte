<script>
	import { createEventDispatcher } from 'svelte';
	import { formatearFecha } from '$lib/paneladmin/controllers/licenciasController.js';

	export let show = false;
	export let licencia = null;
	export let eliminando = false;

	const dispatch = createEventDispatcher();

	function cancelar() {
		dispatch('cancelar');
	}

	function confirmar() {
		dispatch('confirmar');
	}
</script>

{#if show && licencia}
	<div class="modal-backdrop">
		<div class="modal-contenido">
			<div class="modal-header">
				<h5>🗑️ Eliminar Licencia</h5>
				<button type="button" class="btn-close" on:click={cancelar}>&times;</button>
			</div>
			<div class="modal-body">
				<p>
					¿Estás seguro de que deseas eliminar la licencia de <strong>{licencia.agente_nombre}</strong>?
				</p>
				<div class="licencia-info">
					<div class="info-row">
						<strong>Tipo:</strong>
						{licencia.tipo_licencia_descripcion || "Sin tipo"}
					</div>
					<div class="info-row">
						<strong>Período:</strong>
						{formatearFecha(licencia.fecha_desde)} al {formatearFecha(licencia.fecha_hasta)}
					</div>
					<div class="info-row">
						<strong>Estado:</strong> {licencia.estado}
					</div>
					<div class="info-row">
						<strong>Días:</strong>
						{licencia.dias_licencia}
					</div>
				</div>
				<p class="warning-text">
					⚠️ Esta acción no se puede deshacer y eliminará permanentemente la licencia del sistema.
				</p>
				<div class="modal-footer">
					<button class="btn-secondary" on:click={cancelar}>
						Cancelar
					</button>
					<button
						class="btn-danger"
						on:click={confirmar}
						disabled={eliminando}
					>
						{eliminando ? "Eliminando..." : "Eliminar Licencia"}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000;
		backdrop-filter: blur(4px);
	}

	.modal-contenido {
		background: white;
		border-radius: 16px;
		max-width: 500px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
	}

	.modal-header {
		background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
		color: white;
		padding: 1.5rem 2rem;
		border-radius: 16px 16px 0 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.modal-header h5 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 700;
	}

	.btn-close {
		background: none;
		border: none;
		color: white;
		font-size: 25px;
		cursor: pointer;
		padding: 0;
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		transition: all 0.3s ease;
	}

	.btn-close:hover {
		background: rgba(255, 255, 255, 0.2);
	}

	.modal-body {
		padding: 2rem;
	}

	.licencia-info {
		background: #f8fafc;
		padding: 16px;
		border-radius: 8px;
		margin: 16px 0;
		text-align: left;
		border: 1px solid #e2e8f0;
	}

	.info-row {
		margin-bottom: 0.5rem;
		color: #475569;
		font-size: 0.95rem;
	}

	.warning-text {
		color: #d97706;
		font-size: 14px;
		font-weight: 500;
		margin-top: 1rem;
		text-align: center;
	}

	.modal-footer {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
		margin-top: 2rem;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
	}

	.btn-secondary:hover {
		background: #5a6268;
		transform: translateY(-2px);
	}

	.btn-danger {
		background: #dc3545;
		color: white;
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 16px;
	}

	.btn-danger:hover:not(:disabled) {
		background: #c82333;
		transform: translateY(-2px);
	}

	.btn-danger:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}
</style>
