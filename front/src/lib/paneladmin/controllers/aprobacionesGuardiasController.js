import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import { guardiasService, personasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controller para aprobaciones de guardias
 * Maneja workflow de aprobación, rechazo y publicación de cronogramas
 */
class AprobacionesGuardiasController {
	constructor() {
		// Stores de estado
		this.loading = writable(false);
		this.error = writable('');
		this.cronogramasPendientes = writable([]);
		this.cronogramasAprobadas = writable([]);
		this.tabActiva = writable('pendientes');
		this.agenteActual = writable(null);
		this.rolAgente = writable('');
		this.token = writable(null);
		
		// Modal de detalles
		this.mostrarModal = writable(false);
		this.cronogramaSeleccionado = writable(null);
		this.guardiasDelCronograma = writable([]);
		
		// Modal de rechazo
		this.mostrarModalRechazo = writable(false);
		this.motivoRechazo = writable('');
		this.cronogramaARechazar = writable(null);
	}

	/**
	 * Inicializa el controller
	 */
	async init() {
		console.log('🔄 Inicializando AprobacionesGuardiasController...');
		
		try {
			const sessionCheck = await AuthService.checkSession();
			
			if (!sessionCheck.authenticated) {
				goto('/');
				return;
			}
			
			const token = localStorage.getItem('token');
			this.token.set(token);
			
			await this.cargarDatos();
			console.log('✅ Controller de aprobaciones inicializado');
		} catch (err) {
			console.error('❌ Error verificando sesión:', err);
			goto('/');
		}
	}

	/**
	 * Carga datos iniciales (agente actual, pendientes y aprobadas)
	 */
	async cargarDatos() {
		try {
			let token;
			this.token.subscribe(t => token = t)();
			
			const responseAgentes = await personasService.getAllAgentes(token);
			const agentes = responseAgentes.data?.results || responseAgentes.data || [];
			
			// Obtener agente de la sesión actual
			const user = JSON.parse(localStorage.getItem('agente') || '{}');
			const agenteActual = agentes.find(a => a.id_agente === user.id_agente) || agentes[0];
			
			this.agenteActual.set(agenteActual);
			
			if (agenteActual) {
				await Promise.all([
					this.cargarPendientes(),
					this.cargarAprobadas()
				]);
			}
		} catch (e) {
			this.error.set('Error cargando datos iniciales');
			console.error('❌ Error cargando datos:', e);
		}
	}

	/**
	 * Carga cronogramas pendientes de aprobación
	 */
	async cargarPendientes() {
		try {
			this.loading.set(true);
			this.error.set('');
			
			let token;
			this.token.subscribe(t => token = t)();
			
			const response = await guardiasService.getCronogramasPendientes(token);
			const pendientes = response.data || [];
			this.cronogramasPendientes.set(pendientes);
			
			console.log('✅ Cronogramas pendientes cargados:', pendientes.length);
		} catch (e) {
			this.error.set('Error al cargar los cronogramas pendientes');
			console.error('❌ Error cargando pendientes:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga cronogramas aprobados
	 */
	async cargarAprobadas() {
		try {
			this.loading.set(true);
			this.error.set('');
			
			let token;
			this.token.subscribe(t => token = t)();
			
			const response = await guardiasService.getCronogramasAprobadas(token);
			const aprobadas = response.data || [];
			this.cronogramasAprobadas.set(aprobadas);
			
			console.log('✅ Cronogramas aprobadas cargadas:', aprobadas.length);
		} catch (e) {
			this.error.set('Error al cargar los cronogramas aprobados');
			console.error('❌ Error cargando aprobadas:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Muestra los detalles de un cronograma
	 * @param {Object} cronograma - Cronograma a mostrar
	 */
	async verDetalles(cronograma) {
		try {
			this.loading.set(true);
			
			let token;
			this.token.subscribe(t => token = t)();
			
			const response = await guardiasService.getResumenGuardias(`id_cronograma=${cronograma.id_cronograma}`, token);
			const guardias = response.data?.guardias || [];
			
			this.cronogramaSeleccionado.set(cronograma);
			this.guardiasDelCronograma.set(guardias);
			this.mostrarModal.set(true);
			
			console.log('✅ Detalles del cronograma cargados:', guardias.length, 'guardias');
		} catch (e) {
			this.error.set('Error al cargar los detalles');
			console.error('❌ Error cargando detalles:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Aprueba un cronograma
	 * @param {Object} cronograma - Cronograma a aprobar
	 */
	async aprobar(cronograma) {
		if (!confirm('¿Está seguro de aprobar este cronograma?')) {
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');
			
			let token;
			this.token.subscribe(t => token = t)();
			
			await guardiasService.aprobarCronograma(cronograma.id_cronograma, token);
			
			alert('Cronograma aprobado exitosamente');
			await this.cargarDatos();
			
			console.log('✅ Cronograma aprobado:', cronograma.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || 'Error al aprobar el cronograma';
			this.error.set(mensaje);
			alert(mensaje);
			console.error('❌ Error aprobando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Inicia el proceso de rechazo de un cronograma
	 * @param {Object} cronograma - Cronograma a rechazar
	 */
	iniciarRechazo(cronograma) {
		this.cronogramaARechazar.set(cronograma);
		this.motivoRechazo.set('');
		this.mostrarModalRechazo.set(true);
	}

	/**
	 * Confirma y ejecuta el rechazo de un cronograma
	 */
	async confirmarRechazo() {
		let cronogramaARechazar, motivoRechazo;
		this.cronogramaARechazar.subscribe(c => cronogramaARechazar = c)();
		this.motivoRechazo.subscribe(m => motivoRechazo = m)();
		
		if (!motivoRechazo.trim()) {
			alert('Debe ingresar un motivo de rechazo');
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');
			
			let token;
			this.token.subscribe(t => token = t)();
			
			await guardiasService.rechazarCronograma(
				cronogramaARechazar.id_cronograma, 
				{ motivo: motivoRechazo.trim() }, 
				token
			);
			
			this.mostrarModalRechazo.set(false);
			alert('Cronograma rechazado');
			await this.cargarDatos();
			
			console.log('✅ Cronograma rechazado:', cronogramaARechazar.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || 'Error al rechazar el cronograma';
			this.error.set(mensaje);
			alert(mensaje);
			console.error('❌ Error rechazando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Publica un cronograma aprobado
	 * @param {Object} cronograma - Cronograma a publicar
	 */
	async publicar(cronograma) {
		if (!confirm('¿Está seguro de publicar este cronograma? Los agentes serán notificados.')) {
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');
			
			let token;
			this.token.subscribe(t => token = t)();
			
			await guardiasService.publicarCronograma(cronograma.id_cronograma, token);
			
			alert('Cronograma publicado exitosamente');
			await this.cargarDatos();
			
			console.log('✅ Cronograma publicado:', cronograma.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || 'Error al publicar el cronograma';
			this.error.set(mensaje);
			alert(mensaje);
			console.error('❌ Error publicando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Cierra el modal de detalles
	 */
	cerrarModal() {
		this.mostrarModal.set(false);
		this.cronogramaSeleccionado.set(null);
		this.guardiasDelCronograma.set([]);
	}

	/**
	 * Redirige a editar un cronograma
	 * @param {Object} cronograma - Cronograma a editar
	 */
	async editarCronograma(cronograma) {
		goto(`/paneladmin/guardias/planificador?editar=${cronograma.id_cronograma}`);
	}

	/**
	 * Elimina una guardia individual
	 * @param {Object} guardia - Guardia a eliminar
	 */
	async eliminarGuardia(guardia) {
		if (!confirm('¿Está seguro de eliminar esta guardia?')) {
			return;
		}

		try {
			this.loading.set(true);
			
			let token;
			this.token.subscribe(t => token = t)();
			
			await guardiasService.deleteGuardia(guardia.id_guardia, token);
			
			alert('Guardia eliminada exitosamente');
			
			// Recargar detalles del cronograma
			let cronogramaSeleccionado;
			this.cronogramaSeleccionado.subscribe(c => cronogramaSeleccionado = c)();
			if (cronogramaSeleccionado) {
				await this.verDetalles(cronogramaSeleccionado);
			}
			
			await this.cargarDatos();
			
			console.log('✅ Guardia eliminada:', guardia.id_guardia);
		} catch (e) {
			const mensaje = e.response?.data?.message || 'Error al eliminar la guardia';
			alert(mensaje);
			console.error('❌ Error eliminando guardia:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Elimina un cronograma completo
	 * @param {Object} cronograma - Cronograma a eliminar
	 */
	async eliminarCronograma(cronograma) {
		if (!confirm('¿Está seguro de eliminar este cronograma? Se eliminarán todas las guardias asociadas.')) {
			return;
		}

		try {
			this.loading.set(true);
			
			let token;
			this.token.subscribe(t => token = t)();
			
			await guardiasService.deleteCronograma(cronograma.id_cronograma, token);
			
			alert('Cronograma eliminado exitosamente');
			this.cerrarModal();
			await this.cargarDatos();
			
			console.log('✅ Cronograma eliminado:', cronograma.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || 'Error al eliminar el cronograma';
			alert(mensaje);
			console.error('❌ Error eliminando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Formatea una fecha a formato legible
	 * @param {string} fechaStr - Fecha en formato YYYY-MM-DD
	 * @returns {string} - Fecha formateada
	 */
	formatearFecha(fechaStr) {
		if (!fechaStr) return '';
		try {
			const fecha = new Date(fechaStr + 'T00:00:00');
			return fecha.toLocaleDateString('es-AR', {
				day: '2-digit',
				month: '2-digit',
				year: 'numeric'
			});
		} catch (e) {
			return fechaStr;
		}
	}

	/**
	 * Formatea una hora a formato HH:MM
	 * @param {string} horaStr - Hora en formato HH:MM:SS
	 * @returns {string} - Hora formateada HH:MM
	 */
	formatearHora(horaStr) {
		if (!horaStr) return '';
		return horaStr.substring(0, 5);
	}

	/**
	 * Cambia la tab activa
	 * @param {string} tab - Tab a activar: 'pendientes' o 'aprobadas'
	 */
	cambiarTab(tab) {
		this.tabActiva.set(tab);
	}

	/**
	 * Recarga todos los datos
	 */
	async recargar() {
		console.log('🔄 Recargando datos de aprobaciones...');
		await this.cargarDatos();
	}
}

// Exportar singleton
export const aprobacionesGuardiasController = new AprobacionesGuardiasController();
