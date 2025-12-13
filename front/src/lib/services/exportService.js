/**
 * Servicio de Exportación de Reportes - GIGA System
 * Maneja la generación de PDFs y CSVs/Excel con formato institucional
 */

import { createApiClient } from '../api.js';
import { browser } from '$app/environment';

// Cliente API específico para exportaciones
const apiClient = createApiClient();

// ========================
// UTILIDADES DE FORMATEO
// ========================

/**
 * Formatea fechas al formato DD/MM/YYYY
 */
export function formatearFecha(fecha) {
    if (!fecha) return '';
    
    const d = new Date(fecha);
    const dia = String(d.getDate()).padStart(2, '0');
    const mes = String(d.getMonth() + 1).padStart(2, '0');
    const año = d.getFullYear();
    
    return `${dia}/${mes}/${año}`;
}

/**
 * Formatea fecha y hora para generación de reportes
 */
export function formatearFechaHora(fecha = new Date()) {
    const d = new Date(fecha);
    
    const dia = String(d.getDate()).padStart(2, '0');
    const mes = String(d.getMonth() + 1).padStart(2, '0');
    const año = d.getFullYear();
    
    const horas = String(d.getHours()).padStart(2, '0');
    const minutos = String(d.getMinutes()).padStart(2, '0');
    
    return `${dia}/${mes}/${año} ${horas}:${minutos} hs`;
}

/**
 * Genera nombre de archivo para exportaciones
 */
export function generarNombreArchivo(tipoReporte, extension, filtros) {
    const fechaActual = new Date();
    const timestamp = fechaActual.toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
    
    // Mapear tipos de reportes a nombres descriptivos
    const nombresReportes = {
        individual: 'reporte_individual',
        general: 'reporte_general',
        horas_trabajadas: 'guardias_compensaciones',
        parte_diario: 'parte_diario_mensual',
        resumen_licencias: 'resumen_licencias',
        calculo_plus: 'calculo_plus_guardias',
        incumplimiento_normativo: 'incumplimiento_normativo'
    };
    
    const nombreBase = nombresReportes[tipoReporte] || 'reporte';
    
    // Agregar período si existe
    let sufijo = '';
    if (filtros.fecha_desde && filtros.fecha_hasta) {
        const desde = filtros.fecha_desde.replace(/-/g, '');
        const hasta = filtros.fecha_hasta.replace(/-/g, '');
        sufijo = `_${desde}_${hasta}`;
    }
    
    return `GIGA_${nombreBase}${sufijo}_${timestamp}.${extension}`;
}

/**
 * Formatea descripción de filtros para incluir en reporte
 */
export function formatearFiltrosAplicados(filtros, tipoReporte) {
    const descripcionFiltros = [];
    
    // Período
    if (filtros.fecha_desde && filtros.fecha_hasta) {
        const desde = formatearFecha(filtros.fecha_desde);
        const hasta = formatearFecha(filtros.fecha_hasta);
        descripcionFiltros.push(`Período: ${desde} al ${hasta}`);
    }
    
    // Área
    if (filtros.area_nombre) {
        descripcionFiltros.push(`Área: ${filtros.area_nombre}`);
    } else if (tipoReporte !== 'individual') {
        descripcionFiltros.push('Área: Todas las áreas');
    }
    
    // Agente (solo para reporte individual)
    if (tipoReporte === 'individual' && filtros.agente_nombre) {
        descripcionFiltros.push(`Agente: ${filtros.agente_nombre}`);
        if (filtros.agente_legajo) {
            descripcionFiltros.push(`Legajo: ${filtros.agente_legajo}`);
        }
    }
    
    // Tipo de guardia
    if (filtros.tipo_guardia) {
        descripcionFiltros.push(`Tipo de guardia: ${filtros.tipo_guardia}`);
    }
    
    // Opciones adicionales
    const opciones = [];
    if (filtros.incluir_licencias) opciones.push('Licencias');
    if (filtros.incluir_feriados) opciones.push('Feriados');
    if (opciones.length > 0) {
        descripcionFiltros.push(`Incluye: ${opciones.join(', ')}`);
    }
    
    return descripcionFiltros.join(' • ');
}

// ========================
// CONFIGURACIÓN DE PDFs
// ========================

/**
 * Configuración base para PDFs institucionales
 */
const PDF_CONFIG = {
    format: 'A4',
    orientation: 'portrait',
    margin: {
        top: 20,
        right: 15,
        bottom: 20,
        left: 15
    },
    header: {
        height: 60,
        logo: '/logos/logo-untdf.png', // Ruta al logo institucional
        institucion: '2025 - UNTDF - Ushuaia - Tierra del Fuego'
    },
    footer: {
        height: 40,
        firmas: {
            jefe_area: 'Jefe de Área',
            rrhh_liquidacion: 'RR.HH./Liquidación'
        }
    },
    fonts: {
        header: { size: 16, weight: 'bold' },
        subheader: { size: 12, weight: 'normal' },
        body: { size: 10, weight: 'normal' },
        small: { size: 8, weight: 'normal' }
    },
    colors: {
        primary: '#2c3e50',
        secondary: '#34495e',
        accent: '#3498db',
        success: '#27ae60',
        warning: '#f39c12',
        danger: '#e74c3c'
    }
};

/**
 * Configuración específica por tipo de reporte
 */
const PDF_REPORTES_CONFIG = {
    individual: {
        titulo: 'Planilla Individual de Guardias',
        columnas: ['Fecha', 'Día', 'Horario Habitual', 'Horario Guardia', 'Horas', 'Motivo'],
        orientacion: 'portrait'
    },
    general: {
        titulo: 'Planilla General/Preventiva',
        columnas: ['Agente', 'Legajo'],
        orientacion: 'landscape' // Para incluir todos los días del mes
    },
    horas_trabajadas: {
        titulo: 'Reporte de Guardias y Compensaciones',
        columnas: ['Agente', 'Legajo', 'Horas Programadas', 'Horas Efectivas', 'Guardias F/F', 'Total'],
        orientacion: 'portrait'
    },
    parte_diario: {
        titulo: 'Parte Diario/Mensual Consolidado',
        columnas: ['Fecha', 'Agente', 'Ingreso', 'Egreso', 'Horas Trabajadas', 'Novedades'],
        orientacion: 'portrait'
    },
    resumen_licencias: {
        titulo: 'Resumen de Licencias',
        columnas: ['Agente', 'Art. 32.1', 'Art. 32.2', 'Art. 33', 'Días Utilizados', 'Días Disponibles'],
        orientacion: 'portrait'
    },
    calculo_plus: {
        titulo: 'Cálculo Plus por Guardias',
        columnas: ['Agente', 'CUIL', 'Área', 'Horas Guardia', 'Tipo Plus', 'Motivo'],
        orientacion: 'portrait'
    },
    incumplimiento_normativo: {
        titulo: 'Reporte de Incumplimiento Normativo',
        columnas: ['Agente', 'Fecha/Semana', 'Problema Detectado', 'Norma Incumplida', 'Gravedad'],
        orientacion: 'portrait'
    }
};

// ========================
// SERVICIOS DE EXPORTACIÓN
// ========================

/**
 * Exporta reporte como PDF con formato institucional
 */
export async function exportarPDF(tipoReporte, datosReporte, filtros) {
    try {
        console.log('🔄 Iniciando exportación PDF...', { tipoReporte, filtros });
        
        if (!browser) {
            throw new Error('La exportación PDF solo está disponible en el navegador');
        }
        
        // Preparar datos para envío al backend (flatten, sin anidar filtros)
        const payload = {
            tipo_reporte: tipoReporte,
            fecha_desde: filtros?.fecha_desde,
            fecha_hasta: filtros?.fecha_hasta,
            area: filtros?.area_id ?? filtros?.area,
            agente: filtros?.agente_id ?? filtros?.agente,
            tipo_guardia: filtros?.tipo_guardia,
            configuracion: {
                ...PDF_CONFIG,
                reporte_especifico: PDF_REPORTES_CONFIG[tipoReporte]
            },
            metadatos: {
                fecha_generacion: new Date().toISOString(),
                usuario_generacion: 'Usuario Actual', // TODO: Obtener del store de auth
                filtros_aplicados: formatearFiltrosAplicados(filtros, tipoReporte)
            }
        };
        
        // Llamar al endpoint de generación de PDF
        const response = await apiClient.post('/guardias/guardias/exportar_pdf/', payload, {
            responseType: 'blob'
        });
        
        // Crear y descargar archivo
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.download = generarNombreArchivo(tipoReporte, 'pdf', filtros);
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
        
        console.log('✅ PDF exportado exitosamente');
        return {
            exito: true,
            archivo: link.download,
            mensaje: `PDF generado: ${link.download}`
        };
        
    } catch (error) {
        console.error('❌ Error al exportar PDF:', error);
        throw new Error(`Error al generar PDF: ${error.message}`);
    }
}

/**
 * Exporta reporte como CSV/Excel
 */
export async function exportarCSV(tipoReporte, datosReporte, filtros, formato = 'csv') {
    try {
        console.log('🔄 Iniciando exportación CSV/Excel...', { tipoReporte, formato, filtros });
        
        if (!browser) {
            throw new Error('La exportación CSV/Excel solo está disponible en el navegador');
        }
        
        const payload = {
            tipo_reporte: tipoReporte,
            filtros: filtros,
            formato: formato,
            configuracion: {
                incluir_cabeceras: true,
                incluir_totales: true,
                separador: formato === 'csv' ? ',' : null
            }
        };
        
        // Llamar al endpoint de generación de CSV/Excel
        const endpoint = formato === 'xlsx' ? '/guardias/guardias/exportar_excel/' : '/guardias/guardias/exportar_csv/';
        const mimeType = formato === 'xlsx' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'text/csv';
        
        const response = await apiClient.post(endpoint, payload, {
            responseType: 'blob'
        });
        
        // Crear y descargar archivo
        const blob = new Blob([response.data], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.download = generarNombreArchivo(tipoReporte, formato, filtros);
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
        
        console.log(`✅ ${formato.toUpperCase()} exportado exitosamente`);
        return {
            exito: true,
            archivo: link.download,
            mensaje: `${formato.toUpperCase()} generado: ${link.download}`
        };
        
    } catch (error) {
        console.error(`❌ Error al exportar ${formato.toUpperCase()}:`, error);
        throw new Error(`Error al generar ${formato.toUpperCase()}: ${error.message}`);
    }
}

/**
 * Exporta reporte como Excel (wrapper para CSV con formato xlsx)
 */
export async function exportarExcel(tipoReporte, datosReporte, filtros) {
    return exportarCSV(tipoReporte, datosReporte, filtros, 'xlsx');
}

// ========================
// VALIDACIONES Y HELPERS
// ========================

/**
 * Valida que los datos sean exportables
 */
export function validarDatosExportacion(tipoReporte, datosReporte) {
    if (!tipoReporte) {
        throw new Error('Tipo de reporte es requerido');
    }
    
    if (!datosReporte) {
        throw new Error('No hay datos para exportar');
    }
    
    // Validaciones específicas por tipo
    switch (tipoReporte) {
        case 'individual':
            if (!datosReporte.agente) {
                throw new Error('Datos de agente requeridos para reporte individual');
            }
            break;
            
        case 'general':
            if (!datosReporte.agentes || datosReporte.agentes.length === 0) {
                throw new Error('No hay agentes para exportar en reporte general');
            }
            break;
            
        default:
            // Validación genérica
            if (!datosReporte.periodo) {
                throw new Error('Período de reporte es requerido');
            }
    }
    
    return true;
}

/**
 * Obtiene configuración específica para un tipo de reporte
 */
export function obtenerConfiguracionReporte(tipoReporte) {
    return PDF_REPORTES_CONFIG[tipoReporte] || PDF_REPORTES_CONFIG.general;
}

/**
 * Formatea datos para exportación según tipo de reporte
 */
export function formatearDatosParaExportacion(tipoReporte, datosReporte) {
    // Esta función prepara los datos en el formato específico que necesita cada reporte
    // Se implementará según las necesidades específicas de cada tipo de reporte
    
    return {
        tipo: tipoReporte,
        datos_originales: datosReporte,
        datos_formateados: datosReporte, // Por ahora, pasar datos tal como están
        timestamp: new Date().toISOString()
    };
}

// ========================
// EXPORTACIONES POR DEFECTO
// ========================
export default {
    exportarPDF,
    exportarCSV,
    exportarExcel,
    formatearFecha,
    formatearFechaHora,
    generarNombreArchivo,
    validarDatosExportacion,
    obtenerConfiguracionReporte
};
