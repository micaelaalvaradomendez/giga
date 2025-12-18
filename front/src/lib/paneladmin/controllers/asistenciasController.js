/**
 * @file asistenciasController.js
 * @description Controlador para la gestión de asistencias en el panel de administración.
 * Maneja la lógica de negocio relacionada con asistencias, licencias y correcciones.
 */

import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';
import { asistenciaService, personasService } from '$lib/services.js';
import { AuthService } from '$lib/login/authService.js';
import { showConfirm } from '$lib/stores/modalAlertStore.js';

class AsistenciasController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}

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
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}

		try {
			this.loading.set(true);

			// Verificar sesión desde localStorage (evita llamada redundante)
			const currentUser = AuthService.getCurrentUser();

			if (!currentUser || !AuthService.isAuthenticated()) {
				goto('/');
				return;
			}

			this.agente.set(currentUser);

			// Verificar permisos
			const roles = currentUser.roles || [];
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
			const response = await personasService.getAreas();
			const areasData = response.data?.data?.results || response.data?.results || response.data;
			this.areas.set(areasData);
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
				const paramsAsistencias = { fecha_desde: fecha, fecha_hasta: fecha };
				const paramsAusentes = { fecha_desde: fecha, fecha_hasta: fecha, estado: 'sin_entrada' };

				if (area) {
					paramsAsistencias.area_id = area;
					paramsAusentes.area_id = area;
				}

				const [responseAsistencias, responseAusentes] = await Promise.all([
					asistenciaService.getAsistenciasAdmin(paramsAsistencias),
					asistenciaService.getAsistenciasAdmin(paramsAusentes)
				]);

				const dataAsistencias = responseAsistencias.data;
				const dataAusentes = responseAusentes.data;

				

				// Filtrar ausentes que YA tienen asistencia (evitar duplicados visuales)
				// Esto protege contra latencia del backend o condiciones de carrera
				const dniConAsistencia = new Set((dataAsistencias.data || []).map(a => a.agente_dni));
				const ausentesFiltrados = (dataAusentes.data || []).filter(a => !dniConAsistencia.has(a.agente_dni));

				// Combinar arrays (asistencias reales primero)
				asistenciasData = [
					...(dataAsistencias.data || []),
					...ausentesFiltrados
				];

			} else {
				// Para tabs específicas, usar el filtro correspondiente
				const params = { fecha_desde: fecha, fecha_hasta: fecha };

				if (area) {
					params.area_id = area;
				}

				if (tab !== 'licencias' && tab !== 'salidas_auto') {
					const estadoMap = {
						completas: 'completa',
						sin_salida: 'sin_salida',
						sin_entrada: 'sin_entrada'
					};
					if (estadoMap[tab]) {
						params.estado = estadoMap[tab];
					}
				}

				const response = await asistenciaService.getAsistenciasAdmin(params);
				asistenciasData = response.data?.data || [];
			}

			this.asistencias.set(asistenciasData);
		} catch (error) {
			console.error('Error al cargar asistencias:', error);
		}
	}

	async cargarResumen() {
		try {
			let fecha, area;
			this.fechaSeleccionada.subscribe((value) => (fecha = value))();
			this.areaSeleccionada.subscribe((value) => (area = value))();

			const params = { fecha };
			if (area) {
				params.area_id = area;
			}

			const response = await asistenciaService.getResumenAdmin(params);
			this.resumen.set(response.data?.data);
		} catch (error) {
			console.error('Error al cargar resumen:', error);
		}
	}

	async cargarLicencias() {
		try {
			let fecha, area;
			this.fechaSeleccionada.subscribe((value) => (fecha = value))();
			this.areaSeleccionada.subscribe((value) => (area = value))();

			const params = { fecha };
			if (area) {
				params.area_id = area;
			}

			const response = await asistenciaService.getLicenciasAdmin(params);
			this.licencias.set(response.data?.data || []);
		} catch (error) {
			console.error('Error al cargar licencias:', error);
		}
	}

	// ========== GESTIÓN DE MODAL ==========
	abrirModalCorreccion(asistencia) {
		if (!asistencia) {
			console.error('❌ Error: Se intentó abrir modal sin datos de asistencia');
			alert('Error: No se puede abrir el modal sin información de asistencia');
			return;
		}

		// Validar que tenga los datos mínimos necesarios
		if (!asistencia.agente_dni) {
			console.error('❌ Error: Asistencia sin DNI del agente:', {
				asistencia_completa: asistencia,
				tiene_agente_dni: !!asistencia.agente_dni,
				tiene_dni: !!asistencia.dni,
				tiene_id_agente: !!asistencia.id_agente,
				keys: Object.keys(asistencia)
			});
			alert('Error: Los datos del agente están incompletos (falta DNI). No se puede proceder con la corrección.');
			return;
		}

		// Solo usar los datos tal como vienen (sin normalización excesiva)
		const asistenciaNormalizada = asistencia;

		this.asistenciaEditando.set(asistenciaNormalizada);
		this.observacionEdit.set('');

		// SIEMPRE iniciar en modo normal (sin checkbox marcado)
		// Los campos de hora se pre-llenarán solo cuando el usuario active el checkbox
		this.horaEntrada.set('');
		this.horaSalida.set('');
		this.usarHoraEspecifica.set(false);

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

	// ========== MANEJO DEL CHECKBOX ==========
	toggleHoraEspecifica() {
		let usarHora, asistencia;
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();

		if (usarHora) {
			// Si se activa el checkbox, pre-llenar con las horas actuales
			const horaEntradaFormatted = asistencia.hora_entrada ?
				asistencia.hora_entrada.substring(0, 5) : '';
			const horaSalidaFormatted = asistencia.hora_salida ?
				asistencia.hora_salida.substring(0, 5) : '';

			this.horaEntrada.set(horaEntradaFormatted);
			this.horaSalida.set(horaSalidaFormatted);

		} else {
			// Si se desactiva el checkbox, limpiar los campos
			this.horaEntrada.set('');
			this.horaSalida.set('');

		}
	}

	// ========== MARCACIÓN DE ASISTENCIA ==========
	async marcarEntrada(horaEspecifica = null, cerrarModal = true) {
		let asistencia, observacion, usarHora, horaEntrada;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.horaEntrada.subscribe((value) => (horaEntrada = value))();

		if (!asistencia) {
			return {
				success: false,
				message: 'Error: No se recibió información del agente'
			};
		}

		if (!asistencia.agente_dni) {
			console.error('❌ Falta DNI del agente:', {
				asistencia: asistencia,
				tiene_agente_dni: !!asistencia.agente_dni,
				tiene_id_agente: !!asistencia.id_agente,
				keys: Object.keys(asistencia)
			});
			return {
				success: false,
				message: `Error: El agente ${(asistencia && asistencia.agente_nombre) || 'desconocido'} no tiene DNI registrado`
			};
		}

		if (asistencia.hora_entrada) {
			const confirmar = await showConfirm(
				'Este agente ya tiene entrada marcada. ¿Desea marcar nuevamente?',
				'Confirmar re-marcación'
			);
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

			// Agregar la fecha específica de la asistencia que se está editando
			if (asistencia.fecha) {
				requestBody.fecha_especifica = asistencia.fecha;
			}

			// Agregar hora específica si se proporciona
			if (horaEspecifica) {
				requestBody.hora_especifica = horaEspecifica;
			} else if (usarHora && horaEntrada) {
				requestBody.hora_especifica = horaEntrada;
			}

			const response = await asistenciaService.marcarAsistencia(requestBody);
			const data = response.data;

			if (response.status === 200 && data.success) {
				if (cerrarModal) {
					this.cerrarModal();
				}
				await this.cargarDatos();

				// Actualizar la asistencia editando si no se cierra el modal
				if (!cerrarModal) {
					// Buscar la asistencia actualizada en el array cargado (más seguro que usar la respuesta)
					let asistenciasActuales;
					this.asistencias.subscribe(value => asistenciasActuales = value)();

					// Intentar encontrar la asistencia con el mismo DNI y fecha
					// Esto es crucial para que el siguiente paso (salida) tenga el ID correcto
					const dniBusqueda = asistencia.agente_dni;
					const fechaBusqueda = asistencia.fecha;

					const asistenciaActualizada = asistenciasActuales.find(a =>
						a.agente_dni === dniBusqueda &&
						(a.fecha === fechaBusqueda || new Date(a.fecha).toISOString().slice(0, 10) === new Date(fechaBusqueda).toISOString().slice(0, 10))
					);

					if (asistenciaActualizada) {
						
						this.asistenciaEditando.set(asistenciaActualizada);
					}
				}

				return { success: true, message: '✅ Entrada marcada correctamente' };
			} else {
				console.error('❌ Error en marcación:', data);
				let mensaje = data.message || 'No se pudo marcar la entrada';
				if (data.tipo === 'dia_no_laborable') {
					mensaje = '📅 ' + mensaje;
				}
				return {
					success: false,
					message: '❌ Error: ' + mensaje
				};
			}
		} catch (error) {
			console.error('❌ Error al marcar entrada:', error);
			return { success: false, message: '❌ Error de conexión: ' + error.message };
		}
	}

	async marcarSalida(horaEspecifica = null) {
		let asistencia, observacion, usarHora, horaSalida;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.horaSalida.subscribe((value) => (horaSalida = value))();

		

		if (!asistencia || !asistencia.id_agente) {
			console.error("❌ Error: No se recibió información del agente en marcarSalida", asistencia);
			return {
				success: false,
				message: 'Error: No se recibió información del agente'
			};
		}

		if (!asistencia.agente_dni) {
			console.error('❌ Falta DNI del agente para salida:', {
				asistencia: asistencia,
				tiene_agente_dni: !!asistencia.agente_dni,
				tiene_id_agente: !!asistencia.id_agente,
				keys: Object.keys(asistencia)
			});
			return {
				success: false,
				message: `Error: El agente ${asistencia.agente_nombre || 'desconocido'} no tiene DNI registrado`
			};
		}

		if (!asistencia.hora_entrada) {
			return {
				success: false,
				message: 'El agente debe tener una entrada marcada antes de marcar salida'
			};
		}

		if (asistencia.hora_salida) {
			const confirmar = await showConfirm(
				'Este agente ya tiene salida marcada. ¿Desea marcar nuevamente?',
				'Confirmar re-marcación'
			);
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

			// Agregar la fecha específica de la asistencia que se está editando
			if (asistencia.fecha) {
				requestBody.fecha_especifica = asistencia.fecha;
			}

			// Agregar hora específica si se proporciona
			if (horaEspecifica) {
				requestBody.hora_especifica = horaEspecifica;
			} else if (usarHora && horaSalida) {
				requestBody.hora_especifica = horaSalida;
			}

			const response = await asistenciaService.marcarAsistencia(requestBody);
			const data = response.data;

			if (response.status === 200 && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Salida marcada correctamente' };
			} else {
				console.error('❌ Error en marcación salida:', { status: response.status, data });
				let mensaje = data.message || 'No se pudo marcar la salida';
				if (data.tipo === 'dia_no_laborable') {
					mensaje = '📅 ' + mensaje;
				}
				return {
					success: false,
					message: '❌ Error: ' + mensaje
				};
			}
		} catch (error) {
			console.error('❌ Error al marcar salida:', error);
			return { success: false, message: '❌ Error de conexión: ' + error.message };
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

		

		if (!asistencia || !asistencia.id_agente) {
			console.error("❌ Error: No se recibió información del agente en corregirAsistencia", asistencia);
			return {
				success: false,
				message: 'Error: No se recibió información del agente'
			};
		}

		if (!asistencia.agente_dni) {
			console.error('❌ Falta DNI del agente para corrección:', asistencia);
			return {
				success: false,
				message: `Error: El agente ${asistencia.agente_nombre || 'desconocido'} no tiene DNI registrado`
			};
		}

		// CASO ESPECIAL: Si no tiene ID de asistencia, significa que no tiene marcaciones previas
		// En este caso, usar los métodos de marcación en lugar de corrección
		if (!asistencia.id_asistencia) {

			if (!usarHora) {
				return {
					success: false,
					message: 'Debe especificar las horas para crear la asistencia'
				};
			}

			if (!horaEntrada && !horaSalida) {
				return {
					success: false,
					message: 'Debe especificar al menos una hora (entrada o salida)'
				};
			}

			// Validar formato de horas
			const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
			if (horaEntrada && !timeRegex.test(horaEntrada)) {
				return {
					success: false,
					message: 'Formato de hora de entrada inválido. Use HH:MM (ej: 08:30)'
				};
			}

			if (horaSalida && !timeRegex.test(horaSalida)) {
				return {
					success: false,
					message: 'Formato de hora de salida inválido. Use HH:MM (ej: 17:30)'
				};
			}

			// Validar que la hora de salida sea posterior a la de entrada
			if (horaEntrada && horaSalida && horaEntrada >= horaSalida) {
				return {
					success: false,
					message: 'La hora de salida debe ser posterior a la hora de entrada'
				};
			}

			// Crear marcaciones secuencialmente
			try {
				let resultado_final = { success: true, messages: [] };

				// Marcar entrada si se especifica
				if (horaEntrada) {
					// Temporalmente setear la observación
					this.observacionEdit.set(observacion || 'Marcación creada por administrador');

					// Llamar a marcarEntrada pero NO CERRAR EL MODAL si vamos a marcar salida después
					const cerrarAlFinal = !horaSalida;
					const resultado_entrada = await this.marcarEntrada(horaEntrada, cerrarAlFinal);

					if (!resultado_entrada.success) {
						return resultado_entrada;
					}
					resultado_final.messages.push('Entrada creada');

					// Actualizar manualmente el store para que el siguiente paso (salida) pase la validación
					// Esto simula que la asistencia ya tiene entrada marcada
					if (horaSalida) {
						this.asistenciaEditando.update(a => ({
							...a,
							hora_entrada: horaEntrada,
							// Intentamos mantener el ID si existe, o confiamos en que marcarSalida use DNI
							id_asistencia: a.id_asistencia || null
						}));
						
					}
				}

				// Marcar salida si se especifica (solo si también hay entrada)
				if (horaSalida) {
					if (!horaEntrada) {
						return {
							success: false,
							message: 'No se puede crear salida sin entrada previa'
						};
					}

					// Actualizar la observación
					this.observacionEdit.set(observacion || 'Marcación creada por administrador');
					const resultado_salida = await this.marcarSalida(horaSalida);

					if (!resultado_salida.success) {
						return resultado_salida;
					}
					resultado_final.messages.push('Salida creada');
				}

				return {
					success: true,
					message: '✅ ' + resultado_final.messages.join(' y ') + ' correctamente'
				};

			} catch (error) {
				console.error('❌ Error creando marcaciones:', error);
				return {
					success: false,
					message: '❌ Error creando marcaciones: ' + error.message
				};
			}
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

		// Validar formato de horas
		const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
		if (horaEntrada && !timeRegex.test(horaEntrada)) {
			return {
				success: false,
				message: 'Formato de hora de entrada inválido. Use HH:MM (ej: 08:30)'
			};
		}

		if (horaSalida && !timeRegex.test(horaSalida)) {
			return {
				success: false,
				message: 'Formato de hora de salida inválido. Use HH:MM (ej: 17:30)'
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

		const confirmar = await showConfirm(
			'¿Está seguro que desea corregir esta asistencia? Esta acción quedará registrada en el sistema.',
			'Confirmar corrección'
		);
		if (!confirmar) {
			return { success: false, message: 'Operación cancelada' };
		}

		try {
			const requestBody = {
				observacion: observacion.trim() || 'Corrección realizada por administrador'
			};

			// Solo enviar las horas que se han especificado
			if (horaEntrada) {
				requestBody.hora_entrada = horaEntrada;
			}
			if (horaSalida) {
				requestBody.hora_salida = horaSalida;
			}

			;

			const response = await asistenciaService.corregirAsistencia(asistencia.id_asistencia, requestBody);
			const data = response.data;

			if (response.status === 200 && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Asistencia corregida correctamente' };
			} else {
				console.error('❌ Error del servidor (corrección):', { status: response.status, data });
				return {
					success: false,
					message: '❌ Error: ' + (data.message || 'No se pudo corregir la asistencia')
				};
			}
		} catch (error) {
			console.error('❌ Error al corregir asistencia:', error);
			return { success: false, message: '❌ Error de conexión: ' + error.message };
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

	// ========== MARCAR COMO AUSENTE ==========
	async marcarComoAusente() {
		let asistencia, observacion;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();

		if (!asistencia) {
			return {
				success: false,
				message: 'Error: No se recibió información del agente'
			};
		}

		if (!asistencia.id_asistencia) {
			return {
				success: false,
				message: 'No se puede marcar como ausente un agente sin registros previos'
			};
		}

		const confirmar = await showConfirm(
			`¿Está seguro que desea marcar a ${asistencia.agente_nombre} como AUSENTE?\n\n` +
			'Esta acción eliminará su presentismo para el día de hoy y quedará registrada en el sistema.',
			'Confirmar ausencia'
		);

		if (!confirmar) {
			return { success: false, message: 'Operación cancelada' };
		}

		if (!observacion.trim()) {
			const motivo = prompt(
				'MOTIVO OBLIGATORIO: Explique por qué se marca como ausente\n' +
				'(ej: "No se presentó a trabajar", "Abandono de puesto sin aviso")'
			);

			if (!motivo || !motivo.trim()) {
				return {
					success: false,
					message: 'Debe proporcionar un motivo para marcar como ausente'
				};
			}

			this.observacionEdit.set(motivo.trim());
			observacion = motivo.trim();
		}

		try {
			const response = await asistenciaService.marcarAusente(asistencia.id_asistencia, {
				observacion: observacion.trim()
			});
			const data = response.data;

			if (response.status === 200 && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Agente marcado como ausente correctamente' };
			} else {
				console.error('❌ Error marcando ausente:', { status: response.status, data });
				return {
					success: false,
					message: '❌ Error: ' + (data.message || 'No se pudo marcar como ausente')
				};
			}
		} catch (error) {
			console.error('❌ Error al marcar ausente:', error);
			return { success: false, message: '❌ Error de conexión: ' + error.message };
		}
	}

	// ========== RECARGAR ==========
	async recargar() {
		await this.cargarDatos();
	}
}

// Crear instancia única (singleton)
export const asistenciasController = new AsistenciasController();
