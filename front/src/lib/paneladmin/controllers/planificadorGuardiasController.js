import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';
import { personasService, guardiasService } from '$lib/services.js';

/**
 * Controller para el planificador de guardias
 * Maneja wizard multi-paso, validaciones, verificación de conflictos y modo edición
 */
class PlanificadorGuardiasController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}
		
		// Stores de navegación y estado general
		this.loading = writable(false);
		this.error = writable('');
		this.success = writable('');
		this.paso = writable(1);
		this.token = writable(null);

		// Stores del formulario - Paso 1
		this.nombre = writable('');
		this.tipo = writable('regular');
		this.areaSeleccionada = writable(null);
		this.fechaInicio = writable('');
		this.horaInicio = writable('08:00');
		this.fechaFin = writable('');
		this.horaFin = writable('16:00');
		this.observaciones = writable('');

		// Stores de datos
		this.areas = writable([]);
		this.agentesDisponibles = writable([]);
		this.agentesSeleccionados = writable(new Set());
		this.agentesConConflicto = writable(new Set());

		// Toast notifications
		this.toastVisible = writable(false);
		this.toastMensaje = writable('');
		this.toastTipo = writable('success');

		// Modo edición
		this.modoEdicion = writable(false);
		this.cronogramaId = writable(null);
	}

	/**
	 * Inicializa el controller
	 * @param {URLSearchParams} urlParams - Parámetros de la URL para detectar modo edición
	 */
	async init(urlParams = null) {
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}

		this.resetFormulario();

		const token = localStorage.getItem('token');
		this.token.set(token);

		// Verificar modo edición
		if (urlParams) {
			const editarId = urlParams.get('editar');
			if (editarId) {
				this.modoEdicion.set(true);
				this.cronogramaId.set(editarId);
				await this.cargarAreas();
				await this.cargarCronogramaParaEditar(editarId);
				return;
			}
		}

		await this.cargarAreas();
	}

	/**
	 * Carga las áreas disponibles
	 */
	async cargarAreas() {
		try {
			this.loading.set(true);
			this.error.set('');

			let token;
			this.token.subscribe(t => token = t)();

			const response = await personasService.getAreas(token);
			const responseData = response.data;

			let areasData = [];
			if (responseData.success && responseData.data?.results) areasData = responseData.data.results;
			else if (responseData.data?.results) areasData = responseData.data.results;
			else if (responseData.results) areasData = responseData.results;
			else if (Array.isArray(responseData)) areasData = responseData;

			const agente = JSON.parse(localStorage.getItem('user') || '{}');
			const idAreaAgente = agente?.id ?? 0;

			if (idAreaAgente !== 0) {
				areasData = areasData.filter(a => a.id_area === Number(idAreaAgente));
				this.areaSeleccionada.set(Number(idAreaAgente));
			}

			this.areas.set(areasData);
		} catch (e) {
			this.error.set('Error al cargar las áreas');
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga un cronograma existente para editar
	 * @param {string|number} id - ID del cronograma
	 */
	async cargarCronogramaParaEditar(id) {
		try {
			this.loading.set(true);
			this.error.set('');

			let token;
			this.token.subscribe(t => token = t)();

			// Cargar cronograma
			const responseCronograma = await guardiasService.getCronograma(id, token);
			const cronograma = responseCronograma.data;

			

			// Pre-llenar formulario
			this.nombre.set(cronograma.nombre || '');
			this.tipo.set(cronograma.tipo || 'regular');
			this.areaSeleccionada.set(cronograma.id_area);
			this.observaciones.set(cronograma.observaciones || '');

			// Cargar agentes del área primero
			await this.cargarAgentesDeArea();

			// Cargar guardias del cronograma
			const responseGuardias = await guardiasService.getResumenGuardias(`id_cronograma=${id}`, token);
			const guardias = responseGuardias.data?.guardias || [];

			

			if (guardias.length > 0) {
				// Tomar datos de la primera guardia
				const primeraGuardia = guardias[0];
				this.fechaInicio.set(primeraGuardia.fecha);
				this.horaInicio.set(primeraGuardia.hora_inicio);
				this.horaFin.set(primeraGuardia.hora_fin);

				// Pre-seleccionar agentes
				const agentesIds = [...new Set(guardias.map(g => g.id_agente))];
				this.agentesSeleccionados.set(new Set(agentesIds));

				
			}
		} catch (e) {
			this.error.set('Error al cargar el cronograma');
			console.error('❌ Error cargando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga los agentes del área seleccionada y filtra los disponibles
	 */
	async cargarAgentesDeArea() {
		let areaId, fechaInicio, fechaFin, horaInicio, horaFin, token;
		this.areaSeleccionada.subscribe(a => areaId = a)();
		this.fechaInicio.subscribe(f => fechaInicio = f)();
		this.fechaFin.subscribe(f => fechaFin = f)();
		this.horaInicio.subscribe(h => horaInicio = h)();
		this.horaFin.subscribe(h => horaFin = h)();
		this.token.subscribe(t => token = t)();

		if (!areaId) {
			this.agentesDisponibles.set([]);
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');

			const response = await personasService.getAgentesByArea(areaId, token);
			let agentes = response.data?.results || response.data || [];

			// Filtrar solo agentes activos
			agentes = agentes.filter(a => a.activo === true);

			// Si tenemos fecha y horario, filtrar agentes que NO tienen conflictos ni licencias
			if (fechaInicio && horaInicio && horaFin) {
				try {
					const fechaFinalGuardia = fechaFin || fechaInicio;
					const agentesIds = agentes.map(a => a.id_agente);

					// 1. Verificar conflictos con guardias en batch (1 sola llamada)
					const disponibilidadResponse = await guardiasService.verificarDisponibilidadBatch(
						agentesIds,
						fechaInicio,
						fechaFinalGuardia,
						token
					);

					const disponibilidadMap = new Map();
					if (disponibilidadResponse.data?.resultados) {
						disponibilidadResponse.data.resultados.forEach(r => {
							disponibilidadMap.set(r.agente_id, r.disponible);
						});
					}

					// 2. Verificar licencias (aún se hace individual, pero más rápido que antes)
					const agentesDisponibles = [];
					for (const agente of agentes) {
						// Verificar disponibilidad de guardias desde el batch
						const disponibleGuardias = disponibilidadMap.get(agente.id_agente) !== false;

						if (!disponibleGuardias) {
							
							continue;
						}

						// Verificar licencias
						try {
							const estaEnLicencia = await this.verificarLicenciasAgente(agente.id_agente, fechaInicio, fechaFinalGuardia);
							if (estaEnLicencia) {
								
								continue;
							}
						} catch (e) {
							console.warn(`⚠️ Error verificando licencias del agente ${agente.id_agente}:`, e);
							// En caso de error, incluir el agente
						}

						agentesDisponibles.push(agente);
					}

					this.agentesDisponibles.set(agentesDisponibles);
					`);
				} catch (error) {
					console.error('❌ Error verificando disponibilidad:', error);
					// En caso de error, mostrar todos los agentes
					this.agentesDisponibles.set(agentes);
				}
			} else {
				// Sin fecha/horario, mostrar todos los agentes activos
				this.agentesDisponibles.set(agentes);
				
			}
		} catch (e) {
			this.error.set('Error al cargar los agentes');
			console.error('❌ Error cargando agentes:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Verifica conflictos para todos los agentes seleccionados
	 */
	async verificarConflictosAgentes() {
		let seleccionados;
		this.agentesSeleccionados.subscribe(s => seleccionados = s)();

		const conflictos = new Set();
		for (const agenteId of seleccionados) {
			const tieneConflicto = await this.verificarDisponibilidadAgente(agenteId);
			if (tieneConflicto) {
				conflictos.add(agenteId);
			}
		}
		this.agentesConConflicto.set(conflictos);
	}

	/**
	 * Maneja el cambio de área
	 */
	async handleAreaChange() {
		// Limpiar agentes seleccionados al cambiar de área
		this.agentesSeleccionados.set(new Set());
		this.agentesConConflicto.set(new Set());

		await this.cargarAgentesDeArea();
	}

	/**
	 * Maneja el cambio de fecha u horario (requiere recargar agentes disponibles)
	 */
	async handleFechaHorarioChange() {
		let paso;
		this.paso.subscribe(p => paso = p)();

		// Si estamos en el paso 2, recargar agentes considerando nuevas fechas y licencias
		if (paso === 2) {
			// Limpiar selecciones ya que la disponibilidad puede haber cambiado
			this.agentesSeleccionados.set(new Set());
			this.agentesConConflicto.set(new Set());

			
			await this.cargarAgentesDeArea();
		}
	}

	/**
	 * Toggle de selección de agente con verificación de disponibilidad
	 * @param {number} agenteId - ID del agente
	 */
	async toggleAgente(agenteId) {
		let seleccionados;
		this.agentesSeleccionados.subscribe(s => seleccionados = s)();

		,
			seleccionadosSize: seleccionados.size
		});

		const nuevoSet = new Set(seleccionados);

		if (nuevoSet.has(agenteId)) {
			// Deseleccionar
			nuevoSet.delete(agenteId);
			

			let conflictos;
			this.agentesConConflicto.subscribe(c => conflictos = c)();
			const nuevosConflictos = new Set(conflictos);
			nuevosConflictos.delete(agenteId);
			this.agentesConConflicto.set(nuevosConflictos);
		} else {
			// Seleccionar y verificar conflictos
			nuevoSet.add(agenteId);
			

			const tieneConflicto = await this.verificarDisponibilidadAgente(agenteId);
			if (tieneConflicto) {
				let conflictos;
				this.agentesConConflicto.subscribe(c => conflictos = c)();
				const nuevosConflictos = new Set(conflictos);
				nuevosConflictos.add(agenteId);
				this.agentesConConflicto.set(nuevosConflictos);
			}
		}

		});

		this.agentesSeleccionados.set(nuevoSet);
	}

	/**
	 * Verifica disponibilidad de un agente en las fechas/horas seleccionadas
	 * @param {number} agenteId - ID del agente
	 * @returns {Promise<boolean>} - true si tiene conflicto
	 */
	async verificarDisponibilidadAgente(agenteId) {
		let fechaInicio, horaInicio, fechaFin, horaFin, token, cronogramaId;
		this.fechaInicio.subscribe(f => fechaInicio = f)();
		this.horaInicio.subscribe(h => horaInicio = h)();
		this.fechaFin.subscribe(f => fechaFin = f)();
		this.horaFin.subscribe(h => horaFin = h)();
		this.token.subscribe(t => token = t)();
		this.cronogramaId.subscribe(c => cronogramaId = c)();

		if (!fechaInicio || !horaInicio) {
			return false;
		}

		try {
			// Verificar disponibilidad para la fecha de inicio
			const response = await guardiasService.verificarDisponibilidad(agenteId, fechaInicio, token);
			return !response.data?.disponible; // Devolver true si NO está disponible (hay conflicto)
		} catch (e) {
			console.error('❌ Error verificando disponibilidad:', e);
			return false;
		}
	}

	/**
	 * Verifica si un agente tiene licencias aprobadas durante el período especificado
	 * @param {number} agenteId - ID del agente
	 * @param {string} fechaInicio - Fecha de inicio (YYYY-MM-DD)
	 * @param {string} fechaFin - Fecha de fin (YYYY-MM-DD)
	 * @returns {Promise<boolean>} - true si está en licencia
	 */
	async verificarLicenciasAgente(agenteId, fechaInicio, fechaFin) {
		try {
			// Importar asistenciaService si no está disponible
			const { asistenciaService } = await import('$lib/services.js');

			// Consultar licencias del agente en el rango de fechas
			const params = {
				id_agente: agenteId,
				fecha_desde: fechaInicio,
				fecha_hasta: fechaFin,
				estado: 'aprobada' // Solo considerar licencias aprobadas
			};

			const response = await asistenciaService.getLicencias(params);

			if (response?.data?.success && response.data.data) {
				const licencias = response.data.data;

				// Verificar si hay licencias que se superponen con el período de la guardia
				const tieneConflicto = licencias.some(licencia => {
					const licenciaInicio = new Date(licencia.fecha_desde);
					const licenciaFin = new Date(licencia.fecha_hasta);
					const guardiaInicio = new Date(fechaInicio);
					const guardiaFin = new Date(fechaFin);

					// Verificar superposición de fechas
					const haySuperposicion = licenciaInicio <= guardiaFin && licenciaFin >= guardiaInicio;

					if (haySuperposicion) {
						
					}

					return haySuperposicion;
				});

				return tieneConflicto;
			}

			return false;
		} catch (e) {
			console.error('❌ Error verificando licencias del agente:', e);
			// En caso de error, asumir que no está en licencia para no bloquear innecesariamente
			return false;
		}
	}

	/**
	 * Valida el paso 1 del wizard
	 * @returns {Object} - { valido: boolean, errores: string[] }
	 */
	validarPaso1() {
		const errores = [];

		let nombre, areaSeleccionada, fechaInicio, horaInicio, horaFin;
		this.nombre.subscribe(n => nombre = n)();
		this.areaSeleccionada.subscribe(a => areaSeleccionada = a)();
		this.fechaInicio.subscribe(f => fechaInicio = f)();
		this.horaInicio.subscribe(h => horaInicio = h)();
		this.horaFin.subscribe(h => horaFin = h)();

		if (!nombre || nombre.trim() === '') {
			errores.push('El nombre del cronograma es obligatorio');
		}

		if (!areaSeleccionada) {
			errores.push('Debe seleccionar un área');
		}

		if (!fechaInicio) {
			errores.push('Debe seleccionar una fecha de inicio');
		}

		if (!horaInicio) {
			errores.push('Debe seleccionar una hora de inicio');
		}

		if (!horaFin) {
			errores.push('Debe seleccionar una hora de fin');
		}

		// Validar fechas
		if (fechaInicio) {
			const hoy = new Date();
			hoy.setHours(0, 0, 0, 0);
			const fechaInicioDate = new Date(fechaInicio + 'T00:00:00');

			if (fechaInicioDate < hoy) {
				errores.push('La fecha de inicio no puede ser en el pasado');
			}
		}

		return {
			valido: errores.length === 0,
			errores
		};
	}

	/**
	 * Valida que la fecha sea fin de semana o feriado
	 * @returns {Promise<Object>} - { valido: boolean, errores: string[] }
	 */
	async validarDiaPermitido() {
		const errores = [];

		let fechaInicio, token;
		this.fechaInicio.subscribe(f => fechaInicio = f)();
		this.token.subscribe(t => token = t)();

		if (!fechaInicio) {
			return { valido: true, errores: [] };
		}

		try {
			const fechaDate = new Date(fechaInicio + 'T00:00:00');
			const diaSemana = fechaDate.getDay();
			const nombresDias = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];

			`);

			// Si es fin de semana (sábado=6, domingo=0), está permitido
			if (diaSemana === 0 || diaSemana === 6) {
				
				return { valido: true, errores: [] };
			}

			// Si no es fin de semana, verificar si es feriado
			
			const verificacionFeriado = await guardiasService.verificarFeriado({ fecha: fechaInicio }, token);

			

			if (verificacionFeriado.data?.es_feriado) {
				
				const feriados = verificacionFeriado.data.feriados || [];
				if (feriados.length > 0) {
					.join(', '));
				}
				return { valido: true, errores: [] };
			} else {
				
				errores.push('Las guardias solo pueden programarse en fines de semana (sábado y domingo) o feriados');
				return { valido: false, errores };
			}

		} catch (e) {
			console.error('❌ Error verificando feriado:', e);
			console.error('❌ Detalles del error:', e.response?.data || e.message);

			// En caso de error, permitir la creación pero con advertencia
			console.warn('⚠️ No se pudo verificar feriados, permitiendo creación con advertencia');
			const fechaDate = new Date(fechaInicio + 'T00:00:00');
			const diaSemana = fechaDate.getDay();

			if (diaSemana !== 0 && diaSemana !== 6) {
				// Si no es fin de semana y no pudimos verificar feriados, permitir pero con advertencia
				console.warn('⚠️ Permitiendo creación de guardia a pesar del error en verificación de feriados');
				return { valido: true, errores: [] }; // Cambiado para permitir la creación
			}

			return { valido: true, errores: [] };
		}
	}

	/**
	 * Avanza al paso 2 (selección de agentes)
	 */
	async avanzarPaso2() {
		// Validación básica
		const validacion = this.validarPaso1();

		if (!validacion.valido) {
			this.error.set(validacion.errores.join('. '));
			return;
		}

		// Validación de día permitido (fin de semana o feriado)
		const validacionDia = await this.validarDiaPermitido();

		if (!validacionDia.valido) {
			this.error.set(validacionDia.errores.join('. '));
			return;
		}

		this.error.set('');

		// Cargar agentes disponibles considerando fecha y horario
		await this.cargarAgentesDeArea();

		// Limpiar selecciones previas ya que los agentes pueden haber cambiado
		this.agentesSeleccionados.set(new Set());
		this.agentesConConflicto.set(new Set());

		this.paso.set(2);
	}

	/**
	 * Vuelve al paso 1
	 */
	volverPaso1() {
		this.paso.set(1);
		this.error.set('');
	}

	/**
	 * Guarda o actualiza el cronograma de guardias
	 */
	async guardarGuardia() {
		let agentesSeleccionados;
		this.agentesSeleccionados.subscribe(s => agentesSeleccionados = s)();

		if (agentesSeleccionados.size === 0) {
			this.error.set('Debe seleccionar al menos un agente');
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');

			let token, modoEdicion, cronogramaId, nombre, tipo, areaSeleccionada;
			let fechaInicio, horaInicio, fechaFin, horaFin, observaciones;

			this.token.subscribe(t => token = t)();
			this.modoEdicion.subscribe(m => modoEdicion = m)();
			this.cronogramaId.subscribe(c => cronogramaId = c)();
			this.nombre.subscribe(n => nombre = n)();
			this.tipo.subscribe(t => tipo = t)();
			this.areaSeleccionada.subscribe(a => areaSeleccionada = a)();
			this.fechaInicio.subscribe(f => fechaInicio = f)();
			this.horaInicio.subscribe(h => horaInicio = h)();
			this.fechaFin.subscribe(f => fechaFin = f)();
			this.horaFin.subscribe(h => horaFin = h)();
			this.observaciones.subscribe(o => observaciones = o)();

			const agentesArray = Array.from(agentesSeleccionados);

			const payload = {
				nombre: nombre.trim(),
				tipo,
				id_area: areaSeleccionada,
				fecha: fechaInicio, //para buscar cronograma 
				fecha_desde: fechaInicio,
				hora_inicio: horaInicio,
				fecha_hasta: fechaFin || fechaInicio,
				hora_fin: horaFin,
				observaciones: observaciones.trim(),
				agentes: agentesArray,
				agente_id: this._obtenerAgenteActual()
			};

			

			let response;
			if (modoEdicion && cronogramaId) {
				// Actualizar cronograma existente con guardias
				response = await guardiasService.actualizarConGuardias(cronogramaId, payload, token);
				this.mostrarToast('Cronograma actualizado exitosamente', 'success');
			} else {
				// Crear nuevo cronograma con guardias
				response = await guardiasService.crearGuardia(payload, token);
				this.mostrarToast('Cronograma creado exitosamente', 'success');
			}

			// Redirigir a aprobaciones después de 1.5 segundos
			setTimeout(() => {
				goto('/paneladmin/guardias/aprobaciones');
			}, 1500);

		} catch (e) {
			const mensaje = e.response?.data?.message || e.message || 'Error al guardar el cronograma';
			this.error.set(mensaje);
			this.mostrarToast(mensaje, 'error');
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Obtiene el ID del agente actual desde localStorage
	 * @returns {number} ID del agente actual
	 */
	_obtenerAgenteActual() {
		try {
			const user = JSON.parse(localStorage.getItem('agente') || '{}');
			return user.id_agente || user.id || 1; // Fallback a ID 1 si no hay usuario
		} catch (e) {
			console.warn('⚠️ No se pudo obtener usuario de localStorage:', e);
			return 1; // Fallback
		}
	}

	/**
	 * Muestra un toast de notificación
	 * @param {string} mensaje - Mensaje a mostrar
	 * @param {string} tipo - Tipo de toast: 'success', 'error', 'info'
	 */
	mostrarToast(mensaje, tipo = 'success') {
		this.toastMensaje.set(mensaje);
		this.toastTipo.set(tipo);
		this.toastVisible.set(true);

		setTimeout(() => {
			this.toastVisible.set(false);
		}, 3000);
	}

	/**
	 * Cancela y vuelve a la página anterior
	 */
	async cancelar() {
		goto('/paneladmin/guardias');
	}

	/**
	 * Reinicia el formulario
	 */
	resetFormulario() {
		this.paso.set(1);
		this.nombre.set('');
		this.tipo.set('regular');
		this.areaSeleccionada.set(null);
		this.fechaInicio.set('');
		this.horaInicio.set('08:00');
		this.fechaFin.set('');
		this.horaFin.set('16:00');
		this.observaciones.set('');
		this.agentesSeleccionados.set(new Set());
		this.agentesConConflicto.set(new Set());
		this.modoEdicion.set(false);
		this.cronogramaId.set(null);
		this.error.set('');
		this.success.set('');
	}
}

// Exportar singleton
export const planificadorGuardiasController = new PlanificadorGuardiasController();
