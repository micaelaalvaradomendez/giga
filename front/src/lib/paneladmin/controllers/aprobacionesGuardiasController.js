import { writable, derived } from 'svelte/store';
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

		// Filtros
		this.areas = writable([]);
		this.filtroArea = writable('');
		this.filtroTipo = writable('');
		this.filtroEstado = writable('');
		this.busqueda = writable('');

		// Stores derivados para cronogramas filtrados
		this.cronogramasPendientesFiltrados = derived(
			[this.cronogramasPendientes, this.filtroArea, this.filtroTipo, this.filtroEstado, this.busqueda],
			([$cronogramas, $area, $tipo, $estado, $busqueda]) => {
				return this._filtrarCronogramas($cronogramas, $area, $tipo, $estado, $busqueda);
			}
		);

		this.cronogramasAprobadasFiltradas = derived(
			[this.cronogramasAprobadas, this.filtroArea, this.filtroTipo, this.filtroEstado, this.busqueda],
			([$cronogramas, $area, $tipo, $estado, $busqueda]) => {
				return this._filtrarCronogramas($cronogramas, $area, $tipo, $estado, $busqueda);
			}
		);
	}

	/**
	 * Inicializa el controller
	 */
	async init() {
		console.log('🔄 Inicializando AprobacionesGuardiasController...');

		try {
			// Use isAuthenticated check (checkSession already called in +layout.svelte)
			if (!AuthService.isAuthenticated()) {
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
					this.cargarAprobadas(),
					this.cargarAreas()
				]);
			}
		} catch (e) {
			this.error.set('Error cargando datos iniciales');
			console.error('❌ Error cargando datos:', e);
		}
	}

	/**
	 * Carga cronogramas pendientes de aprobación (generadas)
	 */
	async cargarPendientes() {
		try {
			this.loading.set(true);
			this.error.set('');

			let token;
			this.token.subscribe(t => token = t)();

			console.log('🔍 Cargando cronogramas pendientes...');
			const response = await guardiasService.getCronogramasPendientes(token);
			const todosCronogramas = response.data?.results || response.data || [];

			// Filtrar cronogramas que NO están publicados (pendientes, aprobados, generados, etc.)
			const pendientes = todosCronogramas.filter(cronograma =>
				cronograma.estado !== 'publicada' && cronograma.estado !== 'rechazada'
			);

			this.cronogramasPendientes.set(pendientes);

			console.log('✅ Cronogramas pendientes cargados:', pendientes.length, 'de', todosCronogramas.length, 'totales');
		} catch (e) {
			this.error.set('Error al cargar los cronogramas pendientes');
			console.error('❌ Error cargando pendientes:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga cronogramas aprobados (publicadas)
	 */
	async cargarAprobadas() {
		try {
			this.loading.set(true);
			this.error.set('');

			let token;
			this.token.subscribe(t => token = t)();

			console.log('🔍 Cargando cronogramas publicadas...');
			const response = await guardiasService.getCronogramasAprobadas(token);
			console.log('📦 Respuesta getCronogramasAprobadas:', response);

			const aprobadas = response.data?.results || response.data || [];
			this.cronogramasAprobadas.set(aprobadas);

			console.log('✅ Cronogramas publicadas cargadas:', aprobadas.length);
		} catch (e) {
			this.error.set('Error al cargar los cronogramas publicados');
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
			this.error.set('');

			let token;
			this.token.subscribe(t => token = t)();

			console.log('🔍 Cargando guardias del cronograma:', cronograma.id_cronograma);
			console.log('📋 Cronograma seleccionado:', {
				id: cronograma.id_cronograma,
				estado: cronograma.estado,
				total_guardias: cronograma.total_guardias,
				area: cronograma.area_nombre
			});

			// Cargar guardias usando el nuevo endpoint específico
			const response = await guardiasService.getGuardiasPorCronograma(cronograma.id_cronograma, token);

			console.log('📦 Respuesta del servidor:', response);

			// Manejar diferentes formatos de respuesta
			let guardias = [];
			if (response.data) {
				if (Array.isArray(response.data)) {
					guardias = response.data;
				} else if (response.data.guardias && Array.isArray(response.data.guardias)) {
					guardias = response.data.guardias;
				} else if (response.data.results && Array.isArray(response.data.results)) {
					guardias = response.data.results;
				}
			}

			console.log('✅ Guardias procesadas:', guardias.length);
			console.log('📊 Primeras 2 guardias:', guardias.slice(0, 2));

			this.cronogramaSeleccionado.set(cronograma);
			this.guardiasDelCronograma.set(guardias);
			this.mostrarModal.set(true);

			if (guardias.length === 0) {
				console.log('⚠️ No se encontraron guardias para el cronograma', cronograma.id_cronograma);
				console.log('🔍 Posibles causas:');
				console.log('  - Estado del cronograma:', cronograma.estado);
				console.log('  - Guardias inactivas');
				console.log('  - Error en el filtrado del backend');
			}

		} catch (e) {
			console.error('❌ Error completo cargando detalles:', e);
			console.error('❌ Respuesta del servidor:', e.response?.data);
			console.error('❌ Status:', e.response?.status);

			const mensaje = e.response?.data?.message || e.response?.data?.error || 'Error al cargar los detalles del cronograma';
			this.error.set(mensaje);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Aprueba y publica un cronograma
	 * @param {Object} cronograma - Cronograma a aprobar
	 */
	async aprobar(cronograma) {
		if (!confirm('¿Está seguro de aprobar y publicar este cronograma? Los agentes serán notificados.')) {
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');

			let token, agenteActual;
			this.token.subscribe(t => token = t)();
			this.agenteActual.subscribe(a => agenteActual = a)();

			// Usar el endpoint de aprobación correcto
			const payload = {
				agente_id: agenteActual?.id_agente || 1  // Fallback al agente 1
			};

			await guardiasService.aprobarCronograma(cronograma.id_cronograma, payload, token);

			alert('Cronograma aprobado y publicado exitosamente');
			await this.cargarDatos();

			console.log('✅ Cronograma aprobado y publicado:', cronograma.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || e.response?.data?.error || 'Error al aprobar el cronograma';
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

			let agenteActual;
			this.agenteActual.subscribe(a => agenteActual = a)();

			await guardiasService.rechazarCronograma(
				cronogramaARechazar.id_cronograma,
				{
					motivo: motivoRechazo.trim(),
					agente_id: agenteActual?.id_agente || 1
				},
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
	 * Cierra el modal de rechazo
	 */
	cerrarModalRechazo() {
		this.mostrarModalRechazo.set(false);
		this.cronogramaARechazar.set(null);
		this.motivoRechazo.set('');
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
	 * Carga las áreas disponibles para filtros
	 */
	async cargarAreas() {
		try {
			console.log('🔄 Cargando áreas para filtros...');
			let token;
			this.token.subscribe(t => token = t)();
			console.log('🔑 Token:', token ? 'Disponible' : 'No disponible');

			const response = await personasService.getAreas(token);
			console.log('📦 Respuesta completa áreas:', response);

			// Axios devuelve la respuesta en response.data
			let areas = [];
			const responseData = response.data;

			if (responseData.success && responseData.data && responseData.data.results) {
				areas = responseData.data.results;
			} else if (responseData.data && responseData.data.results) {
				areas = responseData.data.results;
			} else if (responseData.results) {
				areas = responseData.results;
			} else if (Array.isArray(responseData)) {
				areas = responseData;
			} else {
				console.log('📊 Estructura inesperada de respuesta:', responseData);
			}

			console.log('✅ Áreas procesadas:', areas.length, 'áreas encontradas');
			console.log('📋 Primeras 3 áreas:', areas.slice(0, 3));

			this.areas.set(areas);
		} catch (e) {
			console.error('❌ Error cargando áreas para filtros:', e);
			console.error('❌ Respuesta del servidor:', e.response?.data);
			console.error('❌ Status:', e.response?.status);
		}
	}

	/**
	 * Filtra cronogramas según los criterios seleccionados
	 * @private
	 */
	_filtrarCronogramas(cronogramas, area, tipo, estado, busqueda) {
		return cronogramas.filter(c => {
			// Filtro por área
			if (area && c.id_area !== parseInt(area)) return false;

			// Filtro por tipo
			if (tipo && c.tipo !== tipo) return false;

			// Filtro por estado
			if (estado && c.estado !== estado) return false;

			// Filtro por búsqueda (nombre del cronograma o área)
			if (busqueda) {
				const termino = busqueda.toLowerCase();
				const nombre = (c.nombre || '').toLowerCase();
				const areaNombre = (c.area_nombre || '').toLowerCase();
				if (!nombre.includes(termino) && !areaNombre.includes(termino)) return false;
			}

			return true;
		});
	}

	/**
	 * Limpia todos los filtros
	 */
	limpiarFiltros() {
		this.filtroArea.set('');
		this.filtroTipo.set('');
		this.filtroEstado.set('');
		this.busqueda.set('');
	}

	/**
	 * Funcionalidad para despublicar un cronograma publicado
	 * @param {Object} cronograma - Cronograma a despublicar
	 */
	async despublicar(cronograma) {
		if (!confirm('¿Está seguro de despublicar este cronograma? Volverá al estado "pendiente" y podrá editarse o eliminarse.')) {
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');

			let token, agenteActual;
			this.token.subscribe(t => token = t)();
			this.agenteActual.subscribe(a => agenteActual = a)();

			const payload = {
				agente_id: agenteActual?.id_agente || 1
			};

			await guardiasService.despublicarCronograma(cronograma.id_cronograma, payload, token);

			alert('Cronograma despublicado exitosamente. Ahora está pendiente y puede editarse o eliminarse.');
			await this.cargarDatos();

			console.log('✅ Cronograma despublicado:', cronograma.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || e.response?.data?.error || 'Error al despublicar el cronograma';
			this.error.set(mensaje);
			alert(mensaje);
			console.error('❌ Error despublicando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Elimina un cronograma que está en estado pendiente
	 * @param {Object} cronograma - Cronograma a eliminar
	 */
	async eliminar(cronograma) {
		if (cronograma.estado !== 'pendiente') {
			alert('Solo se pueden eliminar cronogramas en estado pendiente.');
			return;
		}

		if (!confirm(`¿Está seguro de eliminar el cronograma "${cronograma.nombre}"? Esta acción no se puede deshacer.`)) {
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');

			let token, agenteActual;
			this.token.subscribe(t => token = t)();
			this.agenteActual.subscribe(a => agenteActual = a)();

			const payload = {
				agente_id: agenteActual?.id_agente || 1
			};

			await guardiasService.eliminarCronograma(cronograma.id_cronograma, payload, token);

			alert('Cronograma eliminado exitosamente.');
			await this.cargarDatos();

			console.log('✅ Cronograma eliminado:', cronograma.id_cronograma);
		} catch (e) {
			const mensaje = e.response?.data?.message || e.response?.data?.error || 'Error al eliminar el cronograma';
			this.error.set(mensaje);
			alert(mensaje);
			console.error('❌ Error eliminando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
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
