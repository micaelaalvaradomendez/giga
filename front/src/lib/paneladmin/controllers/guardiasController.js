import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';
import { guardiasService, personasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la gestión del módulo de Guardias
 * Centraliza la lógica de negocio del sistema de planificación de guardias
 * 
 * Funcionalidades:
 * - Planificador: Calendario semanal/mensual para planificar guardias
 * - Asignar Guardias: Gestión de turnos y coberturas
 * - Disponibilidad: Registro de ausencias y preferencias
 * - Aprobaciones: Revisar y publicar guardias planificadas
 */
class GuardiasController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}
		
		// ==========================================
		// STORES PRINCIPALES
		// ==========================================
		
		// Cronogramas
		this.cronogramas = writable([]);
		this.cronogramaActual = writable(null);
		
		// Guardias
		this.guardias = writable([]);
		this.guardiaActual = writable(null);
		
		// Agentes (subordinados para planificación)
		this.subordinados = writable([]);
		this.agentesSeleccionados = writable(new Set());
		
		// ==========================================
		// PLANIFICADOR
		// ==========================================
		
		// Estado del planificador
		this.planificadorPaso = writable('seleccion'); // 'seleccion' | 'detalle'
		this.rangoFechas = writable({ desde: '', hasta: '' });
		this.horasTotales = writable('');
		this.dias = writable([]);
		this.asignaciones = writable({});
		
		// Store derivado para calcular horas asignadas
		this.horasAsignadas = derived(
			this.asignaciones,
			($asignaciones) => {
				let total = 0;
				for (const dia in $asignaciones) {
					const asignacionesDia = $asignaciones[dia] || [];
					asignacionesDia.forEach(a => {
						total += Number(a.horas) || 0;
					});
				}
				return total;
			}
		);
		
		// Store derivado para horas restantes
		this.horasRestantes = derived(
			[this.horasTotales, this.horasAsignadas],
			([$horasTotales, $horasAsignadas]) => {
				return Math.max(0, Number($horasTotales || 0) - $horasAsignadas);
			}
		);
		
		// ==========================================
		// ESTADO GENERAL
		// ==========================================
		
		this.loading = writable(false);
		this.error = writable(null);
		this.mensaje = writable(null);
		
		// Filtros
		this.filtros = writable({
			anio: new Date().getFullYear(),
			mes: new Date().getMonth() + 1,
			area: null,
			agente: null,
			estado: null,
			tipo: null
		});
		
		this.initialized = false;
	}
	
	// ==========================================
	// INICIALIZACIÓN
	// ==========================================
	
	/**
	 * Inicializa el controlador cargando datos iniciales
	 */
	async init() {
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}
		
		if (this.initialized) return;
		
		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}
		
		try {
			this.loading.set(true);
			this.error.set(null);
			
			// Cargar subordinados para planificación
			await this.loadSubordinados();
			
			this.initialized = true;
		} catch (error) {
			console.error('Error inicializando controlador de guardias:', error);
			this.error.set('Error al inicializar el módulo de guardias');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	// ==========================================
	// PLANIFICADOR - Gestión de Cronogramas
	// ==========================================
	
	/**
	 * Carga subordinados del jefe autenticado
	 */
	async loadSubordinados() {
		try {
			const response = await personasService.getAgentes();
			const subordinadosData = Array.isArray(response.data) ? response.data : [];
			
			// Normalizar IDs como strings
			const subordinadosNormalizados = subordinadosData.map(s => ({
				...s,
				id: String(s.id)
			}));
			
			this.subordinados.set(subordinadosNormalizados);
		} catch (error) {
			console.error('Error cargando subordinados:', error);
			this.error.set('No se pudieron cargar los agentes subordinados');
			throw error;
		}
	}
	
	/**
	 * Alterna la selección de un agente para planificación
	 */
	toggleSeleccionAgente(agenteId) {
		this.agentesSeleccionados.update(seleccionados => {
			const sid = String(agenteId);
			const newSet = new Set(seleccionados);
			
			if (newSet.has(sid)) {
				newSet.delete(sid);
			} else {
				newSet.add(sid);
			}
			
			return newSet;
		});
	}
	
	/**
	 * Establece el rango de fechas para planificación
	 */
	setRangoFechas(desde, hasta) {
		this.rangoFechas.set({ desde, hasta });
		
		// Construir array de días
		if (desde && hasta) {
			const dias = this.construirDias(desde, hasta);
			this.dias.set(dias);
		}
	}
	
	/**
	 * Construye un array de fechas entre desde y hasta
	 */
	construirDias(desdeStr, hastaStr) {
		const resultado = [];
		const start = new Date(desdeStr + 'T00:00:00');
		const end = new Date(hastaStr + 'T00:00:00');
		
		for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
			resultado.push(new Date(d));
		}
		
		return resultado;
	}
	
	/**
	 * Establece las horas totales a distribuir
	 */
	setHorasTotales(horas) {
		this.horasTotales.set(horas);
	}
	
	/**
	 * Avanza al paso de detalle del planificador
	 */
	continuarPlanificacion() {
		this.planificadorPaso.set('detalle');
		// Limpiar asignaciones previas
		this.asignaciones.set({});
	}
	
	/**
	 * Vuelve al paso de selección
	 */
	volverSeleccion() {
		this.planificadorPaso.set('seleccion');
	}
	
	/**
	 * Agrega o actualiza una asignación de horas para un agente en un día
	 */
	agregarAsignacion(diaStr, agenteId, horas) {
		this.asignaciones.update(asignacionesActuales => {
			const nuevasAsignaciones = { ...asignacionesActuales };
			const asignacionesDia = nuevasAsignaciones[diaStr] || [];
			
			const indice = asignacionesDia.findIndex(
				a => String(a.agenteId) === String(agenteId)
			);
			
			if (indice >= 0) {
				// Actualizar existente
				asignacionesDia[indice] = { agenteId: String(agenteId), horas };
			} else {
				// Agregar nueva
				asignacionesDia.push({ agenteId: String(agenteId), horas });
			}
			
			nuevasAsignaciones[diaStr] = asignacionesDia;
			return nuevasAsignaciones;
		});
	}
	
	/**
	 * Elimina una asignación de un agente en un día
	 */
	eliminarAsignacion(diaStr, agenteId) {
		this.asignaciones.update(asignacionesActuales => {
			const nuevasAsignaciones = { ...asignacionesActuales };
			const asignacionesDia = nuevasAsignaciones[diaStr] || [];
			
			nuevasAsignaciones[diaStr] = asignacionesDia.filter(
				a => String(a.agenteId) !== String(agenteId)
			);
			
			return nuevasAsignaciones;
		});
	}
	
	/**
	 * Confirma y envía el cronograma planificado al backend
	 */
	async confirmarPlanificacion(agentesElegidos) {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			// Obtener valores actuales
			let rango, horas, asignacionesActuales;
			this.rangoFechas.subscribe(v => rango = v)();
			this.horasTotales.subscribe(v => horas = v)();
			this.asignaciones.subscribe(v => asignacionesActuales = v)();
			
			// Construir payload
			const payload = {
				desde: rango.desde,
				hasta: rango.hasta,
				horas_totales: Number(horas),
				asignaciones: []
			};
			
			// Mapear agentes por ID
			const mapAgentes = new Map(agentesElegidos.map(a => [String(a.id), a]));
			
			// Construir asignaciones
			for (const dia in asignacionesActuales) {
				const asignacionesDia = asignacionesActuales[dia];
				
				for (const asign of asignacionesDia) {
					const agente = mapAgentes.get(String(asign.agenteId));
					
					if (agente && agente.usuario_id) {
						payload.asignaciones.push({
							fecha: dia,
							usuario_id: agente.usuario_id,
							horas: Number(asign.horas)
						});
					}
				}
			}
			
			// Enviar al backend
			const response = await guardiasService.planificar(payload);
			
			this.mensaje.set('Cronograma creado correctamente');
			
			// Limpiar estado del planificador
			this.resetearPlanificador();
			
			return response.data;
			
		} catch (error) {
			console.error('Error confirmando planificación:', error);
			const mensajeError = error?.response?.data?.detail || 'Error al crear el cronograma';
			this.error.set(mensajeError);
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	/**
	 * Resetea el estado del planificador
	 */
	resetearPlanificador() {
		this.planificadorPaso.set('seleccion');
		this.rangoFechas.set({ desde: '', hasta: '' });
		this.horasTotales.set('');
		this.dias.set([]);
		this.asignaciones.set({});
		this.agentesSeleccionados.set(new Set());
	}
	
	// ==========================================
	// CRONOGRAMAS
	// ==========================================
	
	/**
	 * Carga todos los cronogramas con filtros opcionales
	 */
	async loadCronogramas(filtros = {}) {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const params = new URLSearchParams();
			if (filtros.area) params.append('area', filtros.area);
			if (filtros.estado) params.append('estado', filtros.estado);
			if (filtros.tipo) params.append('tipo', filtros.tipo);
			
			const url = `/guardias/cronogramas/?${params.toString()}`;
			const response = await guardiasService.getCronogramas();
			
			const cronogramasData = response.data?.results || response.data || [];
			this.cronogramas.set(cronogramasData);
			
		} catch (error) {
			console.error('Error cargando cronogramas:', error);
			this.error.set('Error al cargar los cronogramas');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	/**
	 * Carga un cronograma específico por ID
	 */
	async loadCronograma(id) {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const response = await guardiasService.getCronograma(id);
			this.cronogramaActual.set(response.data);
			
			return response.data;
		} catch (error) {
			console.error('Error cargando cronograma:', error);
			this.error.set('Error al cargar el cronograma');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	/**
	 * Aprueba un cronograma
	 */
	async aprobarCronograma(id) {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const response = await guardiasService.aprobarCronograma(id);
			this.mensaje.set('Cronograma aprobado exitosamente');
			
			// Recargar cronogramas
			await this.loadCronogramas();
			
			return response.data;
		} catch (error) {
			console.error('Error aprobando cronograma:', error);
			this.error.set('Error al aprobar el cronograma');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	/**
	 * Publica un cronograma aprobado
	 */
	async publicarCronograma(id) {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const response = await guardiasService.publicarCronograma(id);
			this.mensaje.set('Cronograma publicado exitosamente');
			
			// Recargar cronogramas
			await this.loadCronogramas();
			
			return response.data;
		} catch (error) {
			console.error('Error publicando cronograma:', error);
			this.error.set('Error al publicar el cronograma');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	// ==========================================
	// GUARDIAS
	// ==========================================
	
	/**
	 * Carga todas las guardias
	 */
	async loadGuardias() {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const response = await guardiasService.getGuardias();
			const guardiasData = response.data?.results || response.data || [];
			this.guardias.set(guardiasData);
			
		} catch (error) {
			console.error('Error cargando guardias:', error);
			this.error.set('Error al cargar las guardias');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	/**
	 * Obtiene el resumen de guardias por período
	 */
	async getResumenGuardias(filtros = {}) {
		try {
			this.loading.set(true);
			this.error.set(null);
			
			const params = new URLSearchParams();
			if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
			if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
			if (filtros.agente) params.append('agente', filtros.agente);
			if (filtros.area) params.append('area', filtros.area);
			
			const response = await guardiasService.getResumenGuardias(params.toString());
			return response.data;
			
		} catch (error) {
			console.error('Error obteniendo resumen de guardias:', error);
			this.error.set('Error al obtener el resumen de guardias');
			throw error;
		} finally {
			this.loading.set(false);
		}
	}
	
	// ==========================================
	// UTILIDADES
	// ==========================================
	
	/**
	 * Formatea una fecha para mostrar
	 */
	formatearFecha(fecha) {
		if (!fecha) return '';
		
		const d = new Date(fecha);
		if (isNaN(d.getTime())) return fecha;
		
		const opciones = { day: '2-digit', month: '2-digit', year: 'numeric' };
		return d.toLocaleDateString('es-AR', opciones);
	}
	
	/**
	 * Formatea una hora para mostrar
	 */
	formatearHora(hora) {
		if (!hora) return '';
		return hora.slice(0, 5); // HH:MM
	}
	
	/**
	 * Obtiene el nombre completo de un agente
	 */
	getNombreAgente(agenteId, agentes) {
		const agente = agentes.find(a => String(a.id) === String(agenteId));
		if (!agente) return 'Agente';
		return `${agente.apellido}, ${agente.nombre}`;
	}
	
	/**
	 * Limpia los mensajes de error y éxito
	 */
	limpiarMensajes() {
		this.error.set(null);
		this.mensaje.set(null);
	}
	
	/**
	 * Actualiza los filtros
	 */
	actualizarFiltros(nuevosFiltros) {
		this.filtros.update(filtrosActuales => ({
			...filtrosActuales,
			...nuevosFiltros
		}));
	}
}

// Exportar instancia singleton
export const guardiasController = new GuardiasController();
