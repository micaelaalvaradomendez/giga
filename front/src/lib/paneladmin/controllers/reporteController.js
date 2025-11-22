import { writable, derived } from 'svelte/store';
import { personasService, guardiasService } from '$lib/services.js';

/**
 * Controlador para la gestión de reportes de administrador
 * Centraliza toda la lógica de negocio relacionada con reportes y exportaciones
 */
class ReporteController {
	constructor() {
		// ========================================
		// STORES PRINCIPALES
		// ========================================
		
		// Estados de carga
		this.loading = writable(false);
		this.loadingFiltros = writable(true);
		this.exportando = writable(false);
		this.error = writable(null);
		this.mensaje = writable('');
		
		// Datos de filtros disponibles
		this.filtrosDisponibles = writable({
			areas: [],
			agentes: [],
			tipos_guardia: [],
			permisos_usuario: {}
		});
		
		// Filtros seleccionados
		this.filtrosSeleccionados = writable({
			fecha_desde: this._getFechaDefecto('inicio'),
			fecha_hasta: this._getFechaDefecto('fin'),
			area_id: null,
			agente_id: null,
			tipo_guardia: '',
			incluir_licencias: true,
			incluir_feriados: true
		});
		
		// Datos del reporte generado
		this.datosReporte = writable(null);
		this.tipoReporteActual = writable('individual'); // 'individual' | 'general'
		this.vistaPreviaVisible = writable(false);
		
		// Opciones de exportación
		this.opcionesExport = writable({
			formato: 'pdf',
			orientacion: 'portrait',
			incluir_graficos: false,
			incluir_estadisticas: true,
			tamaño_papel: 'A4'
		});
		
		// ========================================
		// STORES DERIVADOS
		// ========================================
		
		// Verificar si hay datos para mostrar
		this.hayDatos = derived(
			this.datosReporte,
			($datos) => $datos && Object.keys($datos).length > 0
		);
		
		// Estado de carga general
		this.cargandoGeneral = derived(
			[this.loading, this.loadingFiltros, this.exportando],
			([$loading, $loadingFiltros, $exportando]) => 
				$loading || $loadingFiltros || $exportando
		);
		
		// Validación de rango de fechas
		this.validacionFechas = derived(
			this.filtrosSeleccionados,
			($filtros) => {
				if (!$filtros.fecha_desde || !$filtros.fecha_hasta) {
					return { valido: false, mensaje: 'Fechas requeridas' };
				}
				
				const fechaDesde = new Date($filtros.fecha_desde);
				const fechaHasta = new Date($filtros.fecha_hasta);
				
				if (fechaDesde > fechaHasta) {
					return {
						valido: false,
						mensaje: 'La fecha de inicio debe ser anterior a la fecha de fin'
					};
				}
				
				const diffDias = (fechaHasta - fechaDesde) / (1000 * 60 * 60 * 24);
				if (diffDias > 365) {
					return {
						valido: false,
						mensaje: 'El rango no puede ser mayor a 1 año'
					};
				}
				
				return { valido: true, mensaje: '' };
			}
		);
		
		// Agentes filtrados por área seleccionada
		this.agentesFiltrados = derived(
			[this.filtrosDisponibles, this.filtrosSeleccionados],
			([$disponibles, $seleccionados]) => {
				console.log('🔍 Filtrando agentes por área:', {
					disponibles: $disponibles.agentes?.length || 0,
					areaSeleccionada: $seleccionados.area_id
				});
				
				if (!$disponibles.agentes || !Array.isArray($disponibles.agentes)) {
					return [];
				}
				
				// Si no hay área seleccionada, mostrar todos los agentes
				if (!$seleccionados.area_id) {
					console.log('📄 Sin área seleccionada, mostrando todos los agentes:', $disponibles.agentes.length);
					return $disponibles.agentes;
				}
				
				// Filtrar agentes por área
				const filtrados = $disponibles.agentes.filter(agente => {
					// Comparar tanto area_id como id_area para compatibilidad
					const agenteAreaId = agente.area_id || agente.id_area;
					const coincide = agenteAreaId === $seleccionados.area_id;
					
					if (!coincide && $disponibles.agentes.length < 5) { // Solo debug si hay pocos agentes
						console.log(`❌ Agente ${agente.nombre_completo} (área ${agenteAreaId}) no coincide con área seleccionada (${$seleccionados.area_id})`);
					}
					return coincide;
				});
				
				console.log('✅ Agentes filtrados:', filtrados.length, filtrados.map(a => `${a.nombre_completo} (área: ${a.area_id})`));
				return filtrados;
			}
		);
		
		// Validación de filtros - debe ir al final después de definir los otros stores
		this.puedeGenerarReporte = derived(
			[this.filtrosSeleccionados, this.tipoReporteActual, this.agentesFiltrados, this.validacionFechas],
			([$filtros, $tipo, $agentesFiltrados, $validacionFechas]) => {
				// Validar fechas primero
				if (!$validacionFechas || !$validacionFechas.valido) {
					return false;
				}
				
				const fechasValidas = $filtros.fecha_desde && $filtros.fecha_hasta;
				
				if ($tipo === 'individual') {
					// Para reportes individuales: fechas válidas, área seleccionada, agente válido
					const agenteValido = $filtros.agente_id && 
						$agentesFiltrados && $agentesFiltrados.some(agente => agente.id === $filtros.agente_id);
					return fechasValidas && $filtros.area_id && agenteValido;
				} else {
					// Para reportes generales: fechas válidas y área seleccionada
					return fechasValidas && $filtros.area_id;
				}
			}
		);
	}
	
	// ========================================
	// MÉTODOS DE INICIALIZACIÓN
	// ========================================
	
	async inicializar() {
		this.loadingFiltros.set(true);
		this.error.set(null);
		
		try {
			// Cargar filtros disponibles (usando servicios existentes)
			await this._cargarFiltrosDisponibles();
			
			// Configurar filtros por defecto
			await this._configurarFiltrosPorDefecto();
			
		} catch (error) {
			console.error('Error al inicializar reportes:', error);
			this.error.set('Error al cargar los filtros disponibles');
		} finally {
			this.loadingFiltros.set(false);
		}
	}
	
	async _cargarFiltrosDisponibles() {
		try {
			// Usar servicios existentes para obtener datos
			console.log('🔄 Cargando filtros disponibles...');
			const [areasResponse, agentesResponse] = await Promise.all([
				personasService.getAreas(),
				personasService.getAgentes()
			]);
			
			console.log('🏢 Respuesta de áreas:', areasResponse);
			console.log('👤 Respuesta de agentes:', agentesResponse);
			
			// Procesar áreas - usar el mismo patrón que usuariosController
			const areas = areasResponse.data?.data?.results || areasResponse.data?.results || [];
			
			// Procesar agentes - usar el mismo patrón que usuariosController
			const agentes = agentesResponse.data?.results || [];
			
			console.log('📋 Estructura primer agente:', agentes[0]);
			
			// Asegurar que sean arrays
			if (!Array.isArray(areas)) {
				console.warn('⚠️ Areas no es array:', areas);
			}
			if (!Array.isArray(agentes)) {
				console.warn('⚠️ Agentes no es array:', agentes);
			}
			
			// Obtener tipos de guardia (esto podríamos necesitar agregarlo al backend)
			const tipos_guardia = ['Operativas', 'Administrativas', 'Especiales']; // Por ahora hardcoded
			
			// Procesar y mapear datos
			const areasFormateadas = areas.map(area => ({
				id: area.id_area || area.id,
				nombre: area.nombre,
				nombre_completo: area.nombre_completo || area.nombre,
				nivel: area.nivel || 0
			}));
			
			const agentesFormateados = agentes
				.filter(agente => agente.activo !== false)
				.map(agente => ({
					id: agente.id_agente || agente.id,
					nombre_completo: `${agente.apellido}, ${agente.nombre}`,
					legajo: agente.legajo,
					area_id: agente.area_id || agente.id_area, // Probar ambos campos
					id_area: agente.id_area, // Mantener campo original también
					area_nombre: agente.area_nombre || 'Sin área'
				}))
				.sort((a, b) => a.nombre_completo.localeCompare(b.nombre_completo));
			
			console.log('✅ Áreas procesadas:', areasFormateadas.length, areasFormateadas);
			console.log('✅ Agentes procesados:', agentesFormateados.length);
			console.log('📋 Estructura de agentes:', agentesFormateados.slice(0, 3)); // Solo primeros 3 para debug
			
			this.filtrosDisponibles.set({
				areas: areasFormateadas,
				agentes: agentesFormateados,
				tipos_guardia: tipos_guardia,
				permisos_usuario: {
					puede_ver_todos: true, // Administrador puede ver todo
					puede_ver_equipo: true,
					solo_individual: false,
					areas_accesibles: areasFormateadas.length,
					agentes_accesibles: agentesFormateados.length
				}
			});
			
		} catch (error) {
			console.error('Error cargando filtros disponibles:', error);
			throw error;
		}
	}
	
	async _configurarFiltrosPorDefecto() {
		const filtrosDisponibles = await new Promise(resolve => {
			this.filtrosDisponibles.subscribe(resolve)();
		});
		
		this.filtrosSeleccionados.update(filtros => ({
			...filtros,
			// Si solo hay un área, seleccionarla automáticamente
			area_id: filtrosDisponibles.areas.length === 1 ? 
				filtrosDisponibles.areas[0].id : null
		}));
	}
	
	// ========================================
	// MÉTODOS DE GESTIÓN DE FILTROS
	// ========================================
	
	actualizarFiltro(campo, valor) {
		this.filtrosSeleccionados.update(filtros => ({
			...filtros,
			[campo]: valor
		}));
		
		// Limpiar datos anteriores cuando cambian filtros críticos
		if (['fecha_desde', 'fecha_hasta', 'area_id', 'agente_id'].includes(campo)) {
			this.datosReporte.set(null);
			this.vistaPreviaVisible.set(false);
		}
	}
	
	actualizarRangoFechas(fechaDesde, fechaHasta) {
		this.filtrosSeleccionados.update(filtros => ({
			...filtros,
			fecha_desde: fechaDesde,
			fecha_hasta: fechaHasta
		}));
		this.datosReporte.set(null);
		this.vistaPreviaVisible.set(false);
	}
	
	seleccionarMesActual() {
		const hoy = new Date();
		const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
		const ultimoDia = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);
		
		this.actualizarRangoFechas(
			this._formatearFecha(primerDia),
			this._formatearFecha(ultimoDia)
		);
	}
	
	seleccionarMesAnterior() {
		const hoy = new Date();
		const primerDia = new Date(hoy.getFullYear(), hoy.getMonth() - 1, 1);
		const ultimoDia = new Date(hoy.getFullYear(), hoy.getMonth(), 0);
		
		this.actualizarRangoFechas(
			this._formatearFecha(primerDia),
			this._formatearFecha(ultimoDia)
		);
	}
	
	cambiarTipoReporte(tipo) {
		this.tipoReporteActual.set(tipo);
		this.datosReporte.set(null);
		this.vistaPreviaVisible.set(false);
		this.error.set(null);
	}
	
	// ========================================
	// MÉTODOS DE GENERACIÓN DE REPORTES
	// ========================================
	
	async generarReporteIndividual() {
		return this._generarReporte('individual');
	}
	
	async generarReporteGeneral() {
		return this._generarReporte('general');
	}
	
	async _generarReporte(tipo) {
		const filtros = await this._obtenerFiltrosActuales();
		
		// Validar filtros
		const validacion = this._validarFiltros(filtros, tipo);
		if (!validacion.valido) {
			this.error.set(validacion.mensaje);
			return false;
		}
		
		this.loading.set(true);
		this.error.set(null);
		this.tipoReporteActual.set(tipo);
		
		try {
			let datos;
			if (tipo === 'individual') {
				datos = await this._generarReporteIndividualReal(filtros);
			} else {
				datos = await this._generarReporteGeneralReal(filtros);
			}
			
			this.datosReporte.set(datos);
			this.vistaPreviaVisible.set(true);
			this.mensaje.set(`Reporte ${tipo} generado exitosamente`);
			
			// Limpiar mensaje después de 3 segundos
			setTimeout(() => this.mensaje.set(''), 3000);
			
			return true;
			
		} catch (error) {
			console.error(`Error al generar reporte ${tipo}:`, error);
			this.error.set(error.message || `Error al generar reporte ${tipo}`);
			return false;
		} finally {
			this.loading.set(false);
		}
	}
	
	// ========================================
	// MÉTODOS DE EXPORTACIÓN
	// ========================================
	
	async exportarPDF() {
		return this._exportar('pdf');
	}
	
	async exportarExcel() {
		return this._exportar('excel');
	}
	
	async _exportar(formato) {
		const tipo = await this._obtenerTipoReporteActual();
		const filtros = await this._obtenerFiltrosActuales();
		const opciones = await this._obtenerOpcionesExport();
		
		this.exportando.set(true);
		this.error.set(null);
		
		try {
			// Llamar al backend para generar el archivo
			const blob = await this._exportarReporteReal(formato, tipo, filtros, opciones);
			
			// Descargar archivo
			const nombreArchivo = this._generarNombreArchivo(tipo, formato);
			this._descargarBlob(blob, nombreArchivo);
			
			this.mensaje.set(`Reporte exportado exitosamente como ${formato.toUpperCase()}`);
			
			// Limpiar mensaje después de 3 segundos
			setTimeout(() => this.mensaje.set(''), 3000);
			
			return true;
			
		} catch (error) {
			console.error(`Error al exportar como ${formato}:`, error);
			this.error.set(`Error al exportar el reporte: ${error.message}`);
			return false;
		} finally {
			this.exportando.set(false);
		}
	}
	
	// ========================================
	// MÉTODOS DE UTILIDAD
	// ========================================
	
	_validarFiltros(filtros, tipo) {
		if (!filtros.fecha_desde || !filtros.fecha_hasta) {
			return {
				valido: false,
				mensaje: 'Las fechas de inicio y fin son obligatorias'
			};
		}
		
		const fechaDesde = new Date(filtros.fecha_desde);
		const fechaHasta = new Date(filtros.fecha_hasta);
		
		if (fechaDesde > fechaHasta) {
			return {
				valido: false,
				mensaje: 'La fecha de inicio no puede ser posterior a la fecha de fin'
			};
		}
		
		const diffDias = (fechaHasta - fechaDesde) / (1000 * 60 * 60 * 24);
		if (diffDias > 365) {
			return {
				valido: false,
				mensaje: 'El rango de fechas no puede ser mayor a 1 año'
			};
		}
		
		if (tipo === 'individual' && !filtros.agente_id) {
			return {
				valido: false,
				mensaje: 'Debe seleccionar un agente para el reporte individual'
			};
		}
		
		if (tipo === 'general' && !filtros.area_id) {
			return {
				valido: false,
				mensaje: 'Debe seleccionar un área para el reporte general'
			};
		}
		
		return { valido: true };
	}
	
	_getFechaDefecto(tipo) {
		// Para demo, usar octubre 2025 donde hay datos completos de guardias (75% presentismo)
		if (tipo === 'inicio') {
			return this._formatearFecha(new Date(2025, 9, 1)); // 1 oct 2025
		} else {
			return this._formatearFecha(new Date(2025, 9, 31)); // 31 oct 2025
		}
	}
	
	_formatearFecha(fecha) {
		return fecha.toISOString().split('T')[0];
	}
	
	_generarNombreArchivo(tipo, formato) {
		const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
		const extension = formato === 'pdf' ? 'pdf' : 'xlsx';
		return `reporte_${tipo}_${timestamp}.${extension}`;
	}
	
	_descargarBlob(blob, nombreArchivo) {
		const url = window.URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.href = url;
		link.download = nombreArchivo;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		window.URL.revokeObjectURL(url);
	}
	
	async _obtenerFiltrosActuales() {
		return new Promise(resolve => {
			this.filtrosSeleccionados.subscribe(resolve)();
		});
	}
	
	async _obtenerTipoReporteActual() {
		return new Promise(resolve => {
			this.tipoReporteActual.subscribe(resolve)();
		});
	}
	
	async _obtenerOpcionesExport() {
		return new Promise(resolve => {
			this.opcionesExport.subscribe(resolve)();
		});
	}
	
	// ========================================
	// MÉTODOS DE GENERACIÓN REAL
	// ========================================
	
	async _generarReporteIndividualReal(filtros) {
		try {
			// Construir parámetros para el nuevo endpoint
			const params = new URLSearchParams({
				agente: filtros.agente_id,
				fecha_desde: filtros.fecha_desde,
				fecha_hasta: filtros.fecha_hasta,
			});
			
			console.log('📊 Generando reporte individual con:', params.toString());
			
			// Usar el nuevo endpoint que implementa la documentación
			const response = await guardiasService.getReporteIndividual(params.toString());
			const reporte = response.data;
			
			console.log('✅ Reporte individual recibido:', reporte);
			
			return {
				agente: reporte.agente,
				periodo: reporte.periodo,
				dias_mes: reporte.dias.map(dia => ({
					fecha: dia.fecha,
					dia_semana: dia.dia_semana,
					dia_mes: new Date(dia.fecha).getDate(),
					horario_habitual_inicio: dia.horario_habitual_inicio,
					horario_habitual_fin: dia.horario_habitual_fin,
					novedad: dia.novedad,
					guardia_inicio: dia.horario_guardia_inicio,
					guardia_fin: dia.horario_guardia_fin,
					horas_planificadas: dia.horas_planificadas || 0,
					horas_efectivas: dia.horas_efectivas || 0,
					motivo_guardia: dia.motivo_guardia,
					tiene_guardia: dia.tiene_guardia,
					tiene_presentismo: !!dia.horas_efectivas,
					estado_presentismo: dia.estado_asistencia
				})),
				totales: {
					total_dias_trabajados: reporte.totales.total_dias_guardia,
					total_horas_planificadas: reporte.totales.total_horas,
					total_horas_efectivas: reporte.dias.reduce((sum, dia) => sum + (dia.horas_efectivas || 0), 0),
					total_horas_guardia: reporte.totales.total_horas,
					total_horas_trabajadas: reporte.dias.reduce((sum, dia) => sum + (dia.horas_efectivas || 0), 0),
					promedio_horas_dia: reporte.totales.promedio_horas_dia,
					dias_con_presentismo: reporte.dias.filter(d => d.horas_efectivas > 0).length,
					dias_sin_presentismo: reporte.dias.filter(d => d.tiene_guardia && !d.horas_efectivas).length,
					porcentaje_presentismo: reporte.totales.total_dias_guardia > 0 ? 
						Math.round((reporte.dias.filter(d => d.horas_efectivas > 0).length / reporte.totales.total_dias_guardia) * 100) : 0
				}
			};
		} catch (error) {
			console.error('Error generando reporte individual:', error);
			throw new Error('No se pudo generar el reporte individual: ' + (error.response?.data?.error || error.message));
		}
	}
	
	async _generarReporteGeneralReal(filtros) {
		try {
			// Construir parámetros para el nuevo endpoint
			const params = new URLSearchParams({
				area: filtros.area_id,
				fecha_desde: filtros.fecha_desde,
				fecha_hasta: filtros.fecha_hasta,
			});
			
			console.log('📊 Generando reporte general con:', params.toString());
			
			// Usar el nuevo endpoint que implementa la documentación
			const response = await guardiasService.getReporteGeneral(params.toString());
			const reporte = response.data;
			
			console.log('✅ Reporte general recibido:', reporte);
			
			return {
				area_nombre: reporte.area.nombre,
				area_completa: reporte.area,
				periodo: reporte.periodo,
				dias_columnas: reporte.dias_columnas,
				agentes: reporte.agentes.map(agente => ({
					...agente,
					// Agregar estado para la vista
					estado: agente.total_horas > 0 ? 'activo' : 'sin_guardias'
				})),
				totales: reporte.totales
			};
		} catch (error) {
			console.error('Error generando reporte general:', error);
			throw new Error('No se pudo generar el reporte general: ' + (error.response?.data?.error || error.message));
		}
	}
	
	_procesarGuardiasParaDias(guardias, filtros) {
		const dias = [];
		const fechaInicio = new Date(filtros.fecha_desde);
		const fechaFin = new Date(filtros.fecha_hasta);
		
		// Crear mapa de guardias por fecha
		const guardiasMap = {};
		guardias.forEach(guardia => {
			guardiasMap[guardia.fecha] = guardia;
		});
		
		// Generar días del período
		for (let fecha = new Date(fechaInicio); fecha <= fechaFin; fecha.setDate(fecha.getDate() + 1)) {
			const fechaStr = this._formatearFecha(new Date(fecha));
			const guardia = guardiasMap[fechaStr];
			
			// Calcular horas planificadas si existe la guardia
			let horasPlanificadas = 0;
			let horasEfectivas = guardia?.horas_efectivas || 0;
			
			if (guardia && guardia.hora_inicio && guardia.hora_fin) {
				const inicio = new Date(`1970-01-01T${guardia.hora_inicio}`);
				const fin = new Date(`1970-01-01T${guardia.hora_fin}`);
				horasPlanificadas = (fin - inicio) / (1000 * 60 * 60);
			}

			dias.push({
				fecha: fechaStr,
				dia_semana: fecha.toLocaleDateString('es-AR', { weekday: 'long' }),
				dia_mes: fecha.getDate(),
				horario_habitual_inicio: '08:00',
				horario_habitual_fin: '16:00',
				guardia_inicio: guardia?.hora_inicio || null,
				guardia_fin: guardia?.hora_fin || null,
				horas_planificadas: Math.round(horasPlanificadas * 100) / 100,
				horas_efectivas: horasEfectivas,
				horas_guardia: horasPlanificadas, // backward compatibility
				tiene_guardia: !!guardia && guardia.activa,
				tiene_presentismo: !!horasEfectivas,
				estado_presentismo: horasEfectivas ? 'Registrado' : (guardia ? 'Pendiente' : 'Sin guardia'),
				observaciones: guardia?.observaciones || '',
				tipo_guardia: guardia?.tipo || null,
				estado_guardia: guardia?.estado || null
			});
		}
		
		return dias;
	}
	
	async _exportarReporteReal(formato, tipo, filtros, opciones) {
		try {
			// Construir parámetros
			const params = new URLSearchParams({
				fecha_desde: filtros.fecha_desde,
				fecha_hasta: filtros.fecha_hasta,
				incluir_licencias: filtros.incluir_licencias,
				incluir_feriados: filtros.incluir_feriados
			});
			
			if (filtros.area_id) {
				params.append('area', filtros.area_id);
			}
			
			if (filtros.agente_id && tipo === 'individual') {
				params.append('agente', filtros.agente_id);
			}
			
			if (filtros.tipo_guardia) {
				params.append('tipo_guardia', filtros.tipo_guardia);
			}
			
			// Llamar al servicio apropiado
			let response;
			if (tipo === 'individual') {
				response = await guardiasService.exportarReporteIndividual(params.toString(), formato);
			} else {
				response = await guardiasService.exportarReporteGeneral(params.toString(), formato);
			}
			
			return response.data; // Axios devuelve el blob en response.data
		} catch (error) {
			console.error('Error exportando reporte:', error);
			// Fallback temporal mientras se implementan los endpoints
			const contenido = `Reporte ${tipo} en formato ${formato}\nGenerado: ${new Date().toLocaleString()}\n\nEste es un reporte temporal.\nPróximamente se implementará la exportación completa desde el backend.`;
			return new Blob([contenido], { 
				type: formato === 'pdf' ? 'application/pdf' : 'text/plain'
			});
		}
	}
	
	// ========================================
	// MÉTODOS DE LIMPIEZA
	// ========================================
	
	limpiarDatos() {
		this.datosReporte.set(null);
		this.vistaPreviaVisible.set(false);
		this.error.set(null);
		this.mensaje.set('');
	}
	
	resetearFiltros() {
		this.filtrosSeleccionados.set({
			fecha_desde: this._getFechaDefecto('inicio'),
			fecha_hasta: this._getFechaDefecto('fin'),
			area_id: null,
			agente_id: null,
			tipo_guardia: '',
			incluir_licencias: true,
			incluir_feriados: true
		});
		this.limpiarDatos();
	}
}

// Instancia singleton para el administrador
export const reporteController = new ReporteController();
export default reporteController;
