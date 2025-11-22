import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';
import { personasService, guardiasService } from '$lib/services.js';

/**
 * Controller para el planificador de guardias
 * Maneja wizard multi-paso, validaciones, verificación de conflictos y modo edición
 */
class PlanificadorGuardiasController {
	constructor() {
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
		console.log('🔄 Inicializando PlanificadorGuardiasController...');
		
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
				console.log('✅ Controller inicializado en modo edición');
				return;
			}
		}
		
		await this.cargarAreas();
		console.log('✅ Controller inicializado en modo creación');
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
			const areasData = response.data?.results || response.data?.data?.results || [];
			this.areas.set(areasData);
			
			console.log('✅ Áreas cargadas:', areasData.length);
		} catch (e) {
			this.error.set('Error al cargar las áreas');
			console.error('❌ Error cargando áreas:', e);
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
			
			console.log('✅ Cronograma cargado para editar:', cronograma);
			
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
			
			console.log('✅ Guardias del cronograma:', guardias.length);
			
			if (guardias.length > 0) {
				// Tomar datos de la primera guardia
				const primeraGuardia = guardias[0];
				this.fechaInicio.set(primeraGuardia.fecha);
				this.horaInicio.set(primeraGuardia.hora_inicio);
				this.horaFin.set(primeraGuardia.hora_fin);
				
				// Pre-seleccionar agentes
				const agentesIds = [...new Set(guardias.map(g => g.id_agente))];
				this.agentesSeleccionados.set(new Set(agentesIds));
				
				console.log('✅ Agentes pre-seleccionados:', agentesIds.length);
			}
		} catch (e) {
			this.error.set('Error al cargar el cronograma');
			console.error('❌ Error cargando cronograma:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga los agentes del área seleccionada
	 */
	async cargarAgentesDeArea() {
		let areaId;
		this.areaSeleccionada.subscribe(a => areaId = a)();
		
		if (!areaId) {
			this.agentesDisponibles.set([]);
			return;
		}

		try {
			this.loading.set(true);
			this.error.set('');
			
			let token;
			this.token.subscribe(t => token = t)();
			
			const response = await personasService.getAgentesByArea(areaId, token);
			let agentes = response.data?.results || response.data || [];
			
			// Filtrar solo agentes activos
			agentes = agentes.filter(a => a.activo === true);
			
			this.agentesDisponibles.set(agentes);
			console.log('✅ Agentes del área cargados:', agentes.length);
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
	 * Toggle de selección de agente con verificación de disponibilidad
	 * @param {number} agenteId - ID del agente
	 */
	async toggleAgente(agenteId) {
		let seleccionados;
		this.agentesSeleccionados.subscribe(s => seleccionados = s)();
		
		console.log('🔍 DEBUG - Toggle agente:', {
			agenteId,
			agenteIdType: typeof agenteId,
			seleccionadosAntes: Array.from(seleccionados),
			seleccionadosSize: seleccionados.size
		});
		
		const nuevoSet = new Set(seleccionados);
		
		if (nuevoSet.has(agenteId)) {
			// Deseleccionar
			nuevoSet.delete(agenteId);
			console.log('🔍 DEBUG - Deseleccionando agente:', agenteId);
			
			let conflictos;
			this.agentesConConflicto.subscribe(c => conflictos = c)();
			const nuevosConflictos = new Set(conflictos);
			nuevosConflictos.delete(agenteId);
			this.agentesConConflicto.set(nuevosConflictos);
		} else {
			// Seleccionar y verificar conflictos
			nuevoSet.add(agenteId);
			console.log('🔍 DEBUG - Seleccionando agente:', agenteId);
			
			const tieneConflicto = await this.verificarDisponibilidadAgente(agenteId);
			if (tieneConflicto) {
				let conflictos;
				this.agentesConConflicto.subscribe(c => conflictos = c)();
				const nuevosConflictos = new Set(conflictos);
				nuevosConflictos.add(agenteId);
				this.agentesConConflicto.set(nuevosConflictos);
			}
		}
		
		console.log('🔍 DEBUG - Agentes después del toggle:', {
			nuevoSetSize: nuevoSet.size,
			nuevoSetArray: Array.from(nuevoSet)
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
			
			// Validar que sea fin de semana (sábado=6, domingo=0)
			const diaSemana = fechaInicioDate.getDay();
			if (diaSemana !== 0 && diaSemana !== 6) {
				errores.push('Las guardias solo pueden programarse en fines de semana (sábado y domingo)');
			}
		}
		
		return {
			valido: errores.length === 0,
			errores
		};
	}

	/**
	 * Avanza al paso 2 (selección de agentes)
	 */
	async avanzarPaso2() {
		const validacion = this.validarPaso1();
		
		if (!validacion.valido) {
			this.error.set(validacion.errores.join('. '));
			return;
		}
		
		this.error.set('');
		await this.cargarAgentesDeArea();
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
				fecha: fechaInicio, // Backend espera 'fecha' no 'fecha_inicio'
				fecha_inicio: fechaInicio, // Mantener para compatibilidad
				hora_inicio: horaInicio,
				fecha_fin: fechaFin || fechaInicio,
				hora_fin: horaFin,
				observaciones: observaciones.trim(),
				agentes: agentesArray,
				agente_id: this._obtenerAgenteActual()
			};
			
			console.log('🔍 DEBUG - Agentes seleccionados:', {
				seleccionadosSet: agentesSeleccionados,
				seleccionadosSetSize: agentesSeleccionados.size,
				agentesArray,
				agentesArrayLength: agentesArray.length
			});
			
			console.log('📤 Guardando cronograma:', payload);
			
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
			
			console.log('✅ Cronograma guardado:', response.data);
			
			// Redirigir a aprobaciones después de 1.5 segundos
			setTimeout(() => {
				goto('/paneladmin/guardias/aprobaciones');
			}, 1500);
			
		} catch (e) {
			const mensaje = e.response?.data?.message || e.message || 'Error al guardar el cronograma';
			this.error.set(mensaje);
			this.mostrarToast(mensaje, 'error');
			console.error('❌ Error guardando cronograma:', e);
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
