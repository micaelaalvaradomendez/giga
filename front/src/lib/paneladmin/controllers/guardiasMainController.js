import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';
import { guardiasService } from '$lib/services.js';

/**
 * Controller para la vista principal de guardias (paneladmin/guardias)
 * Maneja el calendario, agrupación de guardias y modales de detalle
 */
class GuardiasMainController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}
		
		// Stores principales
		this.loading = writable(false);
		this.error = writable('');
		this.guardias = writable([]);
		this.guardiasParaCalendario = writable([]);
		this.feriados = writable([]);

		// Modal de detalle de día
		this.fechaSeleccionada = writable(null);
		this.guardiasDeFecha = writable([]);
		this.mostrarModal = writable(false);

		// Derived store para estadísticas
		this.estadisticas = derived(
			this.guardias,
			$guardias => ({
				total: $guardias.length,
				planificadas: $guardias.filter(g => g.estado === 'planificada').length,
				activas: $guardias.filter(g => g.activa).length
			})
		);
	}

	/**
	 * Inicializa el controller cargando todos los datos
	 */
	async init() {
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}
		
		await this.cargarDatos();
	}

	/**
	 * Carga guardias y feriados en paralelo
	 */
	async cargarDatos() {
		await Promise.all([
			this.cargarGuardias(),
			this.cargarFeriados()
		]);
	}

	/**
	 * Carga todas las guardias y las agrupa para el calendario
	 */
	async cargarGuardias() {
		try {
			this.loading.set(true);
			this.error.set('');

			const response = await guardiasService.getResumenGuardias('');
			const guardiasData = response.data?.guardias || [];

			this.guardias.set(guardiasData);

			// Agrupar guardias para el calendario
			this.agruparGuardias(guardiasData);

		} catch (e) {
			this.error.set('Error al cargar las guardias');
			console.error('❌ Error cargando guardias:', e);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Carga los feriados del año
	 */
	async cargarFeriados() {
		try {
			const response = await guardiasService.getFeriados();
			const feriadosData = response.data?.results || response.data || [];
			this.feriados.set(feriadosData);
		} catch (e) {
			console.error('❌ Error cargando feriados:', e);
			this.feriados.set([]);
		}
	}

	/**
	 * Calcula todas las fechas que abarca una guardia.
	 * Si la hora_fin es menor que hora_inicio, significa que cruza medianoche.
	 * 
	 * @param {string} fechaInicio - Fecha en formato YYYY-MM-DD
	 * @param {string} horaInicio - Hora en formato HH:MM:SS o HH:MM
	 * @param {string} horaFin - Hora en formato HH:MM:SS o HH:MM
	 * @returns {string[]} Array de fechas en formato YYYY-MM-DD
	 */
	calcularFechasGuardia(fechaInicio, horaInicio, horaFin) {
		const fechas = [];
		const fechaInicioDate = new Date(fechaInicio + 'T00:00:00');

		// Extraer horas (formato HH:MM:SS o HH:MM)
		const horaInicioNum = parseInt(horaInicio.split(':')[0]);
		const horaFinNum = parseInt(horaFin.split(':')[0]);

		// Agregar fecha de inicio
		fechas.push(fechaInicio);

		// Si la hora de fin es menor o igual que la hora de inicio, cruza medianoche
		if (horaFinNum <= horaInicioNum) {
			// Agregar día siguiente
			const fechaSiguiente = new Date(fechaInicioDate);
			fechaSiguiente.setDate(fechaSiguiente.getDate() + 1);
			const fechaSiguienteStr = fechaSiguiente.toISOString().split('T')[0];
			fechas.push(fechaSiguienteStr);
		}

		return fechas;
	}

	/**
	 * Agrupa las guardias por fecha, área y horario para mostrar en el calendario.
	 * Maneja guardias que cruzan medianoche.
	 * 
	 * @param {Array} guardiasData - Array de guardias a agrupar
	 */
	agruparGuardias(guardiasData) {
		// Estructura: { fecha: { 'area-hora': [guardias] } }
		const agrupadas = {};

		guardiasData.forEach(guardia => {
			// Calcular todas las fechas que abarca esta guardia
			const fechasGuardia = this.calcularFechasGuardia(
				guardia.fecha,
				guardia.hora_inicio,
				guardia.hora_fin
			);

			// Agregar la guardia a todas las fechas que abarca
			fechasGuardia.forEach(fecha => {
				if (!agrupadas[fecha]) {
					agrupadas[fecha] = {};
				}

				// Agrupar por área y hora para separar guardias de diferentes áreas/horarios
				const clave = `${guardia.area_nombre || 'sin-area'}-${guardia.hora_inicio}-${guardia.hora_fin}`;

				if (!agrupadas[fecha][clave]) {
					agrupadas[fecha][clave] = {
						area_nombre: guardia.area_nombre || 'Sin área',
						hora_inicio: guardia.hora_inicio,
						hora_fin: guardia.hora_fin,
						tipo: guardia.tipo,
						agentes: []
					};
				}

				// Solo agregar el agente si no está ya en el grupo (evitar duplicados)
				const yaExiste = agrupadas[fecha][clave].agentes.some(
					a => a.id_guardia === guardia.id_guardia
				);
				if (!yaExiste) {
					agrupadas[fecha][clave].agentes.push(guardia);
				}
			});
		});

		// Convertir a formato para el calendario
		const guardiasParaCalendarioArray = [];
		Object.keys(agrupadas).forEach(fecha => {
			Object.values(agrupadas[fecha]).forEach(grupo => {
				guardiasParaCalendarioArray.push({
					fecha,
					tipo: grupo.tipo,
					estado: 'planificada',
					area_nombre: grupo.area_nombre,
					agente_nombre: `${grupo.area_nombre} (${grupo.agentes.length} agente${grupo.agentes.length > 1 ? 's' : ''})`,
					hora_inicio: grupo.hora_inicio || '08:00:00',
					hora_fin: grupo.hora_fin || '16:00:00',
					agentes: grupo.agentes,
					cantidad: grupo.agentes.length
				});
			});
		});

		this.guardiasParaCalendario.set(guardiasParaCalendarioArray);
	}

	/**
	 * Maneja el click en un día del calendario
	 * @param {Date} date - Fecha seleccionada
	 * @param {Array} guardiasDelDia - Guardias del día (desde el componente calendario)
	 */
	handleDayClick(date, guardiasDelDia) {
		if (guardiasDelDia && guardiasDelDia.length > 0) {
			const fechaStr = date.toISOString().split('T')[0];
			this.fechaSeleccionada.set(fechaStr);

			// Buscar todas las guardias de esa fecha (incluyendo las que cruzan medianoche)
			let guardiasData;
			this.guardias.subscribe(g => guardiasData = g)();

			const guardiasFiltradas = guardiasData.filter(g => {
				const fechasGuardia = this.calcularFechasGuardia(g.fecha, g.hora_inicio, g.hora_fin);
				return fechasGuardia.includes(fechaStr);
			});

			this.guardiasDeFecha.set(guardiasFiltradas);
			this.mostrarModal.set(true);
		}
	}

	/**
	 * Cierra el modal de detalle de día
	 */
	cerrarModal() {
		this.mostrarModal.set(false);
		this.fechaSeleccionada.set(null);
		this.guardiasDeFecha.set([]);
	}

	/**
	 * Formatea una fecha en formato legible
	 * @param {string} fechaStr - Fecha en formato YYYY-MM-DD
	 * @returns {string} Fecha formateada (ej: "lunes, 21 de noviembre de 2025")
	 */
	formatearFecha(fechaStr) {
		if (!fechaStr) return '';
		const fecha = new Date(fechaStr + 'T00:00:00');
		return fecha.toLocaleDateString('es-AR', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	/**
	 * Agrupa guardias por área y horario para mostrar en el modal
	 * @param {Array} guardiasArray - Array de guardias a agrupar
	 * @returns {Object} Objeto con guardias agrupadas por "área (hora_inicio - hora_fin)"
	 */
	agruparGuardiasPorAreaHora(guardiasArray) {
		return guardiasArray.reduce((acc, g) => {
			const clave = `${g.area_nombre || 'Sin área'} (${g.hora_inicio} - ${g.hora_fin})`;
			if (!acc[clave]) acc[clave] = [];
			acc[clave].push(g);
			return acc;
		}, {});
	}

	/**
	 * Recarga todos los datos
	 */
	async recargar() {
		await this.cargarDatos();
	}
}

// Exportar singleton
export const guardiasMainController = new GuardiasMainController();
