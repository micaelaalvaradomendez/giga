/**
 * @file asistenciasController.js
 * @description Controlador para la gestión de asistencias en el panel de administración.
 * Maneja la lógica de negocio relacionada con asistencias, licencias y correcciones.
 */

import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';

class AsistenciasController {
	constructor() {
		// ========== STORES ==========
		this.agente = writable(null);
		this.loading = writable(true);
		this.areas = writable([]);
		this.asistencias = writable([]);
		this.licencias = writable([]);
		this.resumen = writable(null);

		// Filtros
		this.fechaSeleccionada = writable(new Date().toISOString().split('T')[0]);
		this.areaSeleccionada = writable('');
		this.tabActiva = writable('todas'); // 'todas', 'completas', 'sin_salida', 'sin_entrada', 'salidas_auto', 'licencias'

		// Modal de corrección
		this.modalCorreccion = writable(false);
		this.asistenciaEditando = writable(null);
		this.observacionEdit = writable('');

		// Campos para hora específica
		this.horaEntrada = writable('');
		this.horaSalida = writable('');
		this.usarHoraEspecifica = writable(false);

		// ========== DERIVED STORES ==========
		// Filtrar asistencias según la tab activa
		this.asistenciasFiltradas = derived(
			[this.asistencias, this.tabActiva],
			([$asistencias, $tabActiva]) => {
				if ($tabActiva === 'salidas_auto') {
					return $asistencias.filter((a) => a.marcacion_salida_automatica);
				}
				return $asistencias;
			}
		);
	}

	// ========== INICIALIZACIÓN ==========
	async init() {
		console.log('🚀 Inicializando asistenciasController...');

		try {
			this.loading.set(true);

			// Verificar sesión
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

			this.agente.set(sessionData.user);

			// Verificar permisos
			const roles = sessionData.user.roles || [];
			const roleNames = roles.map((r) => r.nombre);

			if (
				!roleNames.some((nombre) =>
					['Administrador', 'Director', 'Jefatura'].includes(nombre)
				)
			) {
				goto('/inicio');
				return;
			}

			// Cargar datos iniciales
			await this.cargarAreas();
			await this.cargarDatos();

			console.log('✅ asistenciasController inicializado correctamente');
		} catch (error) {
			console.error('❌ Error inicializando asistenciasController:', error);
			throw new Error('Error al inicializar el controlador de asistencias');
		} finally {
			this.loading.set(false);
		}
	}

	// ========== CARGA DE DATOS ==========
	async cargarAreas() {
		try {
			const response = await fetch('/api/personas/catalogs/areas/', {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				const areasData = data.data?.results || data.results || data;
				this.areas.set(areasData);
				console.log('✅ Áreas cargadas:', areasData.length);
			}
		} catch (error) {
			console.error('Error al cargar áreas:', error);
		}
	}

	async cargarDatos() {
		this.loading.set(true);
		try {
			await Promise.all([
				this.cargarAsistencias(),
				this.cargarResumen(),
				this.cargarLicencias()
			]);
		} catch (error) {
			console.error('Error al cargar datos:', error);
		} finally {
			this.loading.set(false);
		}
	}

	async cargarAsistencias() {
		try {
			let fecha, area, tab;
			this.fechaSeleccionada.subscribe((value) => (fecha = value))();
			this.areaSeleccionada.subscribe((value) => (area = value))();
			this.tabActiva.subscribe((value) => (tab = value))();

			let asistenciasData = [];

			if (tab === 'todas') {
				// Para "todas", cargar asistencias registradas + ausentes
				const urlAsistencias = `/api/asistencia/admin/listar/?fecha_desde=${fecha}&fecha_hasta=${fecha}${area ? `&area_id=${area}` : ''}`;
				const urlAusentes = `/api/asistencia/admin/listar/?fecha_desde=${fecha}&fecha_hasta=${fecha}&estado=sin_entrada${area ? `&area_id=${area}` : ''}`;

				console.log('🔍 Cargando todas las asistencias con URLs:', urlAsistencias, urlAusentes);

				const [responseAsistencias, responseAusentes] = await Promise.all([
					fetch(urlAsistencias, { credentials: 'include' }),
					fetch(urlAusentes, { credentials: 'include' })
				]);

				if (responseAsistencias.ok && responseAusentes.ok) {
					const dataAsistencias = await responseAsistencias.json();
					const dataAusentes = await responseAusentes.json();
					
					// Combinar ambos arrays
					asistenciasData = [
						...(dataAsistencias.data || []),
						...(dataAusentes.data || [])
					];
				}
			} else {
				// Para tabs específicas, usar el filtro correspondiente
				let url = `/api/asistencia/admin/listar/?fecha_desde=${fecha}&fecha_hasta=${fecha}`;

				if (area) {
					url += `&area_id=${area}`;
				}

				if (tab !== 'licencias' && tab !== 'salidas_auto') {
					const estadoMap = {
						completas: 'completa',
						sin_salida: 'sin_salida',
						sin_entrada: 'sin_entrada'
					};
					if (estadoMap[tab]) {
						url += `&estado=${estadoMap[tab]}`;
					}
				}

				console.log('🔍 Cargando asistencias con URL:', url);

				const response = await fetch(url, {
					credentials: 'include'
				});

				if (response.ok) {
					const data = await response.json();
					asistenciasData = data.data || [];
				}
			}

			this.asistencias.set(asistenciasData);
			console.log(`✅ Asistencias cargadas (tab: ${tab}):`, asistenciasData.length, 'registros');
		} catch (error) {
			console.error('Error al cargar asistencias:', error);
		}
	}

	async cargarResumen() {
		try {
			let fecha, area;
			this.fechaSeleccionada.subscribe((value) => (fecha = value))();
			this.areaSeleccionada.subscribe((value) => (area = value))();

			let url = `/api/asistencia/admin/resumen/?fecha=${fecha}`;

			if (area) {
				url += `&area_id=${area}`;
			}

			const response = await fetch(url, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				this.resumen.set(data.data);
			}
		} catch (error) {
			console.error('Error al cargar resumen:', error);
		}
	}

	async cargarLicencias() {
		try {
			let fecha, area;
			this.fechaSeleccionada.subscribe((value) => (fecha = value))();
			this.areaSeleccionada.subscribe((value) => (area = value))();

			let url = `/api/asistencia/admin/licencias/?fecha=${fecha}`;

			if (area) {
				url += `&area_id=${area}`;
			}

			const response = await fetch(url, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				this.licencias.set(data.data || []);
			}
		} catch (error) {
			console.error('Error al cargar licencias:', error);
		}
	}

	// ========== GESTIÓN DE MODAL ==========
	abrirModalCorreccion(asistencia) {
		this.asistenciaEditando.set(asistencia);
		this.observacionEdit.set('');
		
		// Si ya tiene horas marcadas, pre-llenar los campos para permitir edición
		if (asistencia.hora_entrada || asistencia.hora_salida) {
			this.horaEntrada.set(asistencia.hora_entrada || '');
			this.horaSalida.set(asistencia.hora_salida || '');
			this.usarHoraEspecifica.set(true);
		} else {
			this.horaEntrada.set('');
			this.horaSalida.set('');
			this.usarHoraEspecifica.set(false);
		}
		
		this.modalCorreccion.set(true);
	}

	cerrarModal() {
		this.modalCorreccion.set(false);
		this.asistenciaEditando.set(null);
		this.observacionEdit.set('');
		this.horaEntrada.set('');
		this.horaSalida.set('');
		this.usarHoraEspecifica.set(false);
	}

	// ========== MARCACIÓN DE ASISTENCIA ==========
	async marcarEntrada(horaEspecifica = null) {
		let asistencia, observacion, usarHora, horaEntrada;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.horaEntrada.subscribe((value) => (horaEntrada = value))();

		if (!asistencia || !asistencia.agente_dni) {
			return {
				success: false,
				message: 'No se puede marcar entrada sin DNI del agente'
			};
		}

		if (asistencia.hora_entrada) {
			const confirmar = confirm('Este agente ya tiene entrada marcada. ¿Desea marcar nuevamente?');
			if (!confirmar) {
				return { success: false, message: 'Operación cancelada' };
			}
		}

		try {
			const requestBody = {
				dni: asistencia.agente_dni,
				tipo_marcacion: 'entrada',
				observacion: observacion || 'Marcación corregida por administrador'
			};

			// Agregar hora específica si se proporciona
			if (horaEspecifica) {
				requestBody.hora_especifica = horaEspecifica;
			} else if (usarHora && horaEntrada) {
				requestBody.hora_especifica = horaEntrada;
			}

			const response = await fetch('/api/asistencia/marcar/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(requestBody)
			});

			const data = await response.json();

			if (response.ok && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Entrada marcada correctamente' };
			} else {
				return {
					success: false,
					message: '❌ Error: ' + (data.message || 'No se pudo marcar la entrada')
				};
			}
		} catch (error) {
			console.error('Error al marcar entrada:', error);
			return { success: false, message: '❌ Error de conexión' };
		}
	}

	async marcarSalida(horaEspecifica = null) {
		let asistencia, observacion, usarHora, horaSalida;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.horaSalida.subscribe((value) => (horaSalida = value))();

		if (!asistencia || !asistencia.agente_dni) {
			return {
				success: false,
				message: 'No se puede marcar salida sin DNI del agente'
			};
		}

		if (!asistencia.hora_entrada) {
			return {
				success: false,
				message: 'El agente debe tener una entrada marcada antes de marcar salida'
			};
		}

		if (asistencia.hora_salida) {
			const confirmar = confirm('Este agente ya tiene salida marcada. ¿Desea marcar nuevamente?');
			if (!confirmar) {
				return { success: false, message: 'Operación cancelada' };
			}
		}

		try {
			const requestBody = {
				dni: asistencia.agente_dni,
				tipo_marcacion: 'salida',
				observacion: observacion || 'Marcación corregida por administrador'
			};

			// Agregar hora específica si se proporciona
			if (horaEspecifica) {
				requestBody.hora_especifica = horaEspecifica;
			} else if (usarHora && horaSalida) {
				requestBody.hora_especifica = horaSalida;
			}

			const response = await fetch('/api/asistencia/marcar/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(requestBody)
			});

			const data = await response.json();

			if (response.ok && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Salida marcada correctamente' };
			} else {
				return {
					success: false,
					message: '❌ Error: ' + (data.message || 'No se pudo marcar la salida')
				};
			}
		} catch (error) {
			console.error('Error al marcar salida:', error);
			return { success: false, message: '❌ Error de conexión' };
		}
	}

	// ========== CORRECCIÓN DE ASISTENCIA EXISTENTE ==========
	async corregirAsistencia() {
		let asistencia, observacion, usarHora, horaEntrada, horaSalida;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.horaEntrada.subscribe((value) => (horaEntrada = value))();
		this.horaSalida.subscribe((value) => (horaSalida = value))();

		if (!asistencia || !asistencia.id_asistencia) {
			return {
				success: false,
				message: 'No se puede corregir: información de asistencia inválida'
			};
		}

		if (!usarHora) {
			return {
				success: false,
				message: 'Debe especificar las horas para corregir la asistencia'
			};
		}

		if (!horaEntrada && !horaSalida) {
			return {
				success: false,
				message: 'Debe especificar al menos una hora (entrada o salida)'
			};
		}

		// Validar observación para correcciones
		if ((asistencia.hora_entrada || asistencia.hora_salida) && !observacion.trim()) {
			return {
				success: false,
				message: 'Debe proporcionar una observación al corregir una asistencia existente'
			};
		}

		// Validar que la hora de salida sea posterior a la de entrada
		if (horaEntrada && horaSalida && horaEntrada >= horaSalida) {
			return {
				success: false,
				message: 'La hora de salida debe ser posterior a la hora de entrada'
			};
		}

		const confirmar = confirm(
			'¿Está seguro que desea corregir esta asistencia? Esta acción quedará registrada en el sistema.'
		);
		if (!confirmar) {
			return { success: false, message: 'Operación cancelada' };
		}

		try {
			const requestBody = {
				observacion: observacion || 'Corrección realizada por administrador'
			};

			// Solo enviar las horas que se han especificado
			if (horaEntrada) {
				requestBody.hora_entrada = horaEntrada;
			}
			if (horaSalida) {
				requestBody.hora_salida = horaSalida;
			}

			const response = await fetch(`/api/asistencia/admin/corregir/${asistencia.id_asistencia}/`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(requestBody)
			});

			const data = await response.json();

			if (response.ok && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Asistencia corregida correctamente' };
			} else {
				return {
					success: false,
					message: '❌ Error: ' + (data.message || 'No se pudo corregir la asistencia')
				};
			}
		} catch (error) {
			console.error('Error al corregir asistencia:', error);
			return { success: false, message: '❌ Error de conexión' };
		}
	}

	// ========== UTILIDADES ==========
	formatTime(time) {
		if (!time) return '--:--';
		return time.substring(0, 5);
	}

	formatDate(dateStr) {
		const date = new Date(dateStr + 'T00:00:00');
		return date.toLocaleDateString('es-AR', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric'
		});
	}

	getEstadoBadge(asistencia) {
		if (asistencia.hora_entrada && asistencia.hora_salida) {
			return { text: 'Completa', class: 'badge-success' };
		} else if (asistencia.hora_entrada && !asistencia.hora_salida) {
			return { text: 'Sin salida', class: 'badge-warning' };
		} else {
			return { text: 'Sin entrada', class: 'badge-error' };
		}
	}

	limpiarFiltros() {
		this.areaSeleccionada.set('');
		this.cargarDatos();
		console.log('🧹 Filtros limpiados');
	}

	// ========== GESTIÓN DE FILTROS ==========
	setFecha(fecha) {
		this.fechaSeleccionada.set(fecha);
		this.cargarDatos();
	}

	setArea(area) {
		this.areaSeleccionada.set(area);
		this.cargarDatos();
	}

	setTabActiva(tab) {
		this.tabActiva.set(tab);
		this.cargarDatos();
	}

	// ========== RECARGAR ==========
	async recargar() {
		await this.cargarDatos();
	}
}

// Crear instancia única (singleton)
export const asistenciasController = new AsistenciasController();
