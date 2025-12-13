/**
 * @file asistenciasController.js
 * @description Controlador para la gestión de asistencias en el panel de administración.
 * Maneja la lógica de negocio relacionada con asistencias, licencias y correcciones.
 */

import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';
import { API_BASE_URL } from '$lib/api.js';
import { AuthService } from '$lib/login/authService.js';

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
			const response = await fetch(`${API_BASE_URL}/personas/catalogs/areas/`, {
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

					console.log('📊 Datos cargados:', {
						asistencias_registradas: dataAsistencias.data?.length || 0,
						ausentes: dataAusentes.data?.length || 0,
						primer_ausente: dataAusentes.data?.[0]
					});

					// Combinar ambos arrays
					asistenciasData = [
						...(dataAsistencias.data || []),
						...(dataAusentes.data || [])
					];

					// Verificar estructura de primer ausente si existe
					if (dataAusentes.data && dataAusentes.data.length > 0) {
						console.log('🔍 Estructura del primer ausente:', dataAusentes.data[0]);
					}
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

		console.log('📝 Abriendo modal para asistencia (normalizada):', {
			id_asistencia: asistenciaNormalizada.id_asistencia,
			agente_nombre: asistenciaNormalizada.agente_nombre,
			agente_dni: asistenciaNormalizada.agente_dni,
			id_agente: asistenciaNormalizada.id_agente,
			tiene_entrada: !!asistenciaNormalizada.hora_entrada,
			tiene_salida: !!asistenciaNormalizada.hora_salida,
			fecha: asistenciaNormalizada.fecha,
			area_nombre: asistenciaNormalizada.area_nombre,
			estructura_original: asistencia,
			estructura_normalizada: asistenciaNormalizada
		});

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

			console.log('⏰ Activando modo hora específica:', {
				entrada_prellenada: horaEntradaFormatted,
				salida_prellenada: horaSalidaFormatted
			});
		} else {
			// Si se desactiva el checkbox, limpiar los campos
			this.horaEntrada.set('');
			this.horaSalida.set('');

			console.log('🔄 Desactivando modo hora específica');
		}
	}

	// ========== MARCACIÓN DE ASISTENCIA ==========
	async marcarEntrada(horaEspecifica = null) {
		let asistencia, observacion, usarHora, horaEntrada;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();
		this.usarHoraEspecifica.subscribe((value) => (usarHora = value))();
		this.horaEntrada.subscribe((value) => (horaEntrada = value))();

		console.log('🕐 Marcando entrada:', {
			agente: asistencia?.agente_nombre,
			dni: asistencia?.agente_dni,
			id_agente: asistencia?.id_agente,
			fecha: asistencia?.fecha,
			usar_hora: usarHora,
			hora_entrada: horaEntrada,
			hora_especifica: horaEspecifica,
			observacion: observacion,
			asistencia_completa: asistencia
		});

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
				message: `Error: El agente ${asistencia.agente_nombre || 'desconocido'} no tiene DNI registrado`
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

			console.log('📤 Enviando petición de marcación:', requestBody);

			const response = await fetch(`${API_BASE_URL}/asistencia/marcar/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(requestBody)
			});

			const data = await response.json();
			console.log('📥 Respuesta del servidor:', { status: response.status, data });

			if (response.ok && data.success) {
				this.cerrarModal();
				await this.cargarDatos();
				return { success: true, message: '✅ Entrada marcada correctamente' };
			} else {
				console.error('❌ Error en marcación:', { status: response.status, data });
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

		console.log('🚪 Intentando marcar salida:', {
			asistencia_id: asistencia?.id_asistencia,
			agente: asistencia?.agente_nombre,
			dni: asistencia?.agente_dni,
			id_agente: asistencia?.id_agente,
			fecha: asistencia?.fecha,
			tiene_entrada: !!asistencia?.hora_entrada,
			tiene_salida: !!asistencia?.hora_salida,
			usar_hora: usarHora,
			hora_salida: horaSalida,
			asistencia_completa: asistencia
		});

		if (!asistencia) {
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

			console.log('📤 Enviando petición de marcación salida:', requestBody);

			const response = await fetch(`${API_BASE_URL}/asistencia/marcar/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(requestBody)
			});

			const data = await response.json();
			console.log('📥 Respuesta del servidor (salida):', { status: response.status, data });

			if (response.ok && data.success) {
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

		console.log('🔧 Iniciando corrección de asistencia:', {
			asistencia_id: asistencia?.id_asistencia,
			tiene_entrada: !!asistencia?.hora_entrada,
			tiene_salida: !!asistencia?.hora_salida,
			usarHora,
			horaEntrada,
			horaSalida,
			observacion
		});

		if (!asistencia) {
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
			console.log('📝 Sin asistencia previa, creando nuevas marcaciones...');

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
					const resultado_entrada = await this.marcarEntrada(horaEntrada);

					if (!resultado_entrada.success) {
						return resultado_entrada;
					}
					resultado_final.messages.push('Entrada creada');

					// IMPORTANTE: Recargar datos después de crear la entrada para tener el id_asistencia
					if (horaSalida) {
						console.log('🔄 Recargando datos después de crear entrada...');
						await this.cargarAsistencias();

						// Buscar la asistencia recién creada
						let asistenciasActuales;
						this.asistencias.subscribe(value => asistenciasActuales = value)();

						const asistenciaActualizada = asistenciasActuales.find(a =>
							a.agente_dni === asistencia.agente_dni &&
							a.fecha === asistencia.fecha &&
							a.hora_entrada !== null
						);

						if (asistenciaActualizada) {
							console.log('✅ Asistencia actualizada encontrada:', asistenciaActualizada);
							this.asistenciaEditando.set(asistenciaActualizada);
						} else {
							console.warn('⚠️ No se encontró la asistencia actualizada');
						}
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

		// ========== CORRECCIÓN DE ASISTENCIA EXISTENTE ==========
		console.log('🔧 Corrigiendo asistencia existente con ID:', asistencia.id_asistencia);

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

		const confirmar = confirm(
			'¿Está seguro que desea corregir esta asistencia? Esta acción quedará registrada en el sistema.'
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

			console.log('📤 Enviando solicitud de corrección:', {
				url: `/api/asistencia/admin/corregir/${asistencia.id_asistencia}/`,
				body: requestBody
			});

			const response = await fetch(`/api/asistencia/admin/corregir/${asistencia.id_asistencia}/`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify(requestBody)
			});

			const data = await response.json();
			console.log('📥 Respuesta del servidor (corrección):', { status: response.status, data });

			if (response.ok && data.success) {
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

	// ========== MARCAR COMO AUSENTE ==========
	async marcarComoAusente() {
		let asistencia, observacion;
		this.asistenciaEditando.subscribe((value) => (asistencia = value))();
		this.observacionEdit.subscribe((value) => (observacion = value))();

		console.log('❌ Marcando como ausente:', {
			asistencia_id: asistencia?.id_asistencia,
			agente: asistencia?.agente_nombre,
			tenia_entrada: !!asistencia?.hora_entrada,
			tenia_salida: !!asistencia?.hora_salida
		});

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

		const confirmar = confirm(
			`¿Está seguro que desea marcar a ${asistencia.agente_nombre} como AUSENTE?\n\n` +
			'Esta acción eliminará su presentismo para el día de hoy y quedará registrada en el sistema.'
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
			const response = await fetch(`/api/asistencia/admin/marcar-ausente/${asistencia.id_asistencia}/`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					observacion: observacion.trim()
				})
			});

			const data = await response.json();
			console.log('📥 Respuesta marcar ausente:', { status: response.status, data });

			if (response.ok && data.success) {
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
