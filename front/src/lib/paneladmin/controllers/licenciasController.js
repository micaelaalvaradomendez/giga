/**
 * Controlador para la gestión de licencias
 * Maneja la lógica de aprobación jerárquica según roles
 */

import { writable, derived } from 'svelte/store';
import { asistenciaService } from '$lib/services.js';

// Stores principales
export const licencias = writable([]);
export const tiposLicencia = writable([]);
export const filtros = writable({
    fecha_desde: '',
    fecha_hasta: '',
    area_id: null,
    estado: 'todas', // 'pendiente', 'aprobada', 'rechazada', 'todas'
    tipo_licencia_id: null
});
export const loading = writable(false);
export const error = writable(null);
export const usuario = writable(null);

// Store derivado para licencias filtradas
export const licenciasFiltradas = derived(
    [licencias, filtros],
    ([$licencias, $filtros]) => {
        let resultado = [...$licencias];

        if ($filtros.fecha_desde) {
            resultado = resultado.filter(l => l.fecha_desde >= $filtros.fecha_desde);
        }

        if ($filtros.fecha_hasta) {
            resultado = resultado.filter(l => l.fecha_hasta <= $filtros.fecha_hasta);
        }

        if ($filtros.area_id) {
            resultado = resultado.filter(l => l.id_agente_area === parseInt($filtros.area_id));
        }

        if ($filtros.estado && $filtros.estado !== 'todas') {
            resultado = resultado.filter(l => l.estado === $filtros.estado);
        }

        if ($filtros.tipo_licencia_id) {
            resultado = resultado.filter(l => l.id_tipo_licencia === $filtros.tipo_licencia_id);
        }

        return resultado;
    }
);

// Store derivado para estadísticas
export const estadisticas = derived(
    [licenciasFiltradas],
    ([$licenciasFiltradas]) => {
        const total = $licenciasFiltradas.length;
        const pendientes = $licenciasFiltradas.filter(l => l.estado === 'pendiente').length;
        const aprobadas = $licenciasFiltradas.filter(l => l.estado === 'aprobada').length;
        const rechazadas = $licenciasFiltradas.filter(l => l.estado === 'rechazada').length;

        return {
            total,
            pendientes,
            aprobadas,
            rechazadas,
            porcentajeAprobacion: total > 0 ? Math.round((aprobadas / total) * 100) : 0
        };
    }
);

/**
 * Determina qué acciones puede realizar el usuario según su rol
 */
export function obtenerPermisos(rolUsuario, areaUsuario) {
    const permisos = {
        puedeCrear: false,
        puedeAprobar: false,
        puedeRechazar: false,
        puedeAsignar: false,
        puedeVerTodasAreas: false,
        soloSuArea: false
    };

    switch (rolUsuario) {
        case 'Administrador':
            permisos.puedeCrear = true;
            permisos.puedeAprobar = true;
            permisos.puedeRechazar = true;
            permisos.puedeAsignar = true;
            permisos.puedeVerTodasAreas = true;
            break;
        
        case 'Director':
            permisos.puedeCrear = true;
            permisos.puedeAprobar = true;
            permisos.puedeRechazar = true;
            permisos.puedeAsignar = true;
            permisos.soloSuArea = true;
            break;
        
        case 'Jefatura':
            permisos.puedeCrear = true;
            permisos.puedeAprobar = true;
            permisos.puedeRechazar = true;
            permisos.puedeAsignar = true;
            permisos.soloSuArea = true;
            break;
        
        case 'Agente Avanzado':
        case 'Agente':
            permisos.puedeCrear = true;
            permisos.soloSuArea = true;
            break;
    }

    return permisos;
}

/**
 * Determina quién puede aprobar una licencia según la jerarquía
 */
export function puedeAprobarLicencia(licencia, usuarioRol, usuarioArea) {
    if (usuarioRol === 'Administrador') {
        return true;
    }

    if (usuarioRol === 'Director') {
        // Director puede aprobar todo en su área
        return licencia.id_agente_area === usuarioArea;
    }

    if (usuarioRol === 'Jefatura') {
        // Jefatura puede aprobar agentes y agentes avanzados de su área
        const rolesQueAprueba = ['Agente', 'Agente Avanzado'];
        return licencia.id_agente_area === usuarioArea && 
               rolesQueAprueba.includes(licencia.agente_rol);
    }

    return false;
}

/**
 * Cargar licencias desde el servidor
 */
export async function cargarLicencias(parametros = {}) {
    loading.set(true);
    error.set(null);
    
    try {
        const response = await asistenciaService.getLicencias(parametros);
        
        if (response?.data?.success) {
            licencias.set(response.data.data || []);
        } else {
            throw new Error(response?.data?.message || 'Error al cargar licencias');
        }
    } catch (err) {
        console.error('Error cargando licencias:', err);
        error.set(err.message || 'Error al cargar licencias');
        licencias.set([]);
    } finally {
        loading.set(false);
    }
}

/**
 * Cargar tipos de licencia
 */
export async function cargarTiposLicencia() {
    try {
        const response = await asistenciaService.getTiposLicencia();
        
        if (response?.data?.success) {
            tiposLicencia.set(response.data.data || []);
        } else {
            throw new Error(response?.data?.message || 'Error al cargar tipos de licencia');
        }
    } catch (err) {
        console.error('Error cargando tipos de licencia:', err);
        error.set(err.message || 'Error al cargar tipos de licencia');
    }
}

/**
 * Crear nueva licencia
 */
export async function crearLicencia(datosLicencia) {
    try {
        const response = await asistenciaService.createLicencia(datosLicencia);
        
        if (response?.data?.success) {
            // Recargar licencias para mostrar la nueva
            await cargarLicencias();
            return { success: true, data: response.data.data };
        } else {
            throw new Error(response?.data?.message || 'Error al crear licencia');
        }
    } catch (err) {
        console.error('Error creando licencia:', err);
        return { 
            success: false, 
            error: err.response?.data?.message || err.message || 'Error al crear licencia' 
        };
    }
}

/**
 * Aprobar licencia
 */
export async function aprobarLicencia(idLicencia, observaciones = '') {
    try {
        const response = await asistenciaService.aprobarLicencia(idLicencia, {
            observaciones: observaciones
        });
        
        if (response?.data?.success) {
            await cargarLicencias();
            return { success: true };
        } else {
            throw new Error(response?.data?.message || 'Error al aprobar licencia');
        }
    } catch (err) {
        console.error('Error aprobando licencia:', err);
        return { 
            success: false, 
            error: err.response?.data?.message || err.message || 'Error al aprobar licencia' 
        };
    }
}

/**
 * Rechazar licencia
 */
export async function rechazarLicencia(idLicencia, motivoRechazo) {
    try {
        const response = await asistenciaService.rechazarLicencia(idLicencia, {
            motivo: motivoRechazo
        });
        
        if (response?.data?.success) {
            await cargarLicencias();
            return { success: true };
        } else {
            throw new Error(response?.data?.message || 'Error al rechazar licencia');
        }
    } catch (err) {
        console.error('Error rechazando licencia:', err);
        return { 
            success: false, 
            error: err.response?.data?.message || err.message || 'Error al rechazar licencia' 
        };
    }
}

/**
 * Actualizar filtros
 */
export function actualizarFiltros(nuevosFiltros) {
    filtros.update(filtrosActuales => ({
        ...filtrosActuales,
        ...nuevosFiltros
    }));
}

/**
 * Limpiar filtros
 */
export function limpiarFiltros() {
    filtros.set({
        fecha_desde: '',
        fecha_hasta: '',
        area_id: null,
        estado: 'todas',
        tipo_licencia_id: null
    });
}

/**
 * Formatear fecha para mostrar
 */
export function formatearFecha(fecha) {
    if (!fecha) return '';
    return new Date(fecha).toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Calcular días de licencia
 */
export function calcularDiasLicencia(fechaDesde, fechaHasta) {
    if (!fechaDesde || !fechaHasta) return 0;
    
    const inicio = new Date(fechaDesde);
    const fin = new Date(fechaHasta);
    const diferencia = fin.getTime() - inicio.getTime();
    
    return Math.ceil(diferencia / (1000 * 60 * 60 * 24)) + 1; // +1 porque incluye ambos días
}

/**
 * Obtener color del estado de licencia
 */
export function obtenerColorEstado(estado) {
    const colores = {
        'pendiente': '#f59e0b', // amarillo
        'aprobada': '#10b981',   // verde
        'rechazada': '#ef4444',  // rojo
        'cancelada': '#6b7280'   // gris
    };
    
    return colores[estado] || '#6b7280';
}

/**
 * Obtener icono del estado de licencia
 */
export function obtenerIconoEstado(estado) {
    const iconos = {
        'pendiente': '⏳',
        'aprobada': '✅',
        'rechazada': '❌',
        'cancelada': '⚫'
    };
    
    return iconos[estado] || '❓';
}

/**
 * Asigna una nueva licencia a un agente específico
 */
export async function asignarLicencia(datosAsignacion) {
    try {
        loading.set(true);
        error.set(null);

        const response = await asistenciaService.createLicencia({
            id_agente: datosAsignacion.agente_id,
            id_tipo_licencia: datosAsignacion.tipo_licencia_id,
            fecha_desde: datosAsignacion.fecha_desde,
            fecha_hasta: datosAsignacion.fecha_hasta,
            observaciones: datosAsignacion.observaciones || '',
            estado: 'aprobada' // Asignaciones administrativas se aprueban automáticamente
        });

        if (response?.data?.success) {
            // Actualizar el store de licencias
            cargarLicencias();
            return { success: true, data: response.data.data };
        } else {
            const errorMsg = response?.data?.message || 'Error al asignar la licencia';
            error.set(errorMsg);
            return { success: false, error: errorMsg };
        }
    } catch (err) {
        console.error('Error asignando licencia:', err);
        const errorMsg = err?.response?.data?.message || err.message || 'Error de conexión';
        error.set(errorMsg);
        return { success: false, error: errorMsg };
    } finally {
        loading.set(false);
    }
}
