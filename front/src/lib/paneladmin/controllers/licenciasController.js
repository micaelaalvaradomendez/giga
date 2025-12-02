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
    [licencias, filtros, usuario],
    ([$licencias, $filtros, $usuario]) => {
        let resultado = [...$licencias];

        // 🔒 FILTRO JERÁRQUICO: Solo mostrar licencias de roles inferiores
        if ($usuario) {
            const usuarioRol = $usuario.roles?.[0]?.nombre || $usuario.rol_nombre || 'Agente';
            const usuarioId = $usuario.id_agente;
            console.log('🔍 Filtrando licencias para rol:', usuarioRol, 'ID:', usuarioId);
            
            resultado = resultado.filter(licencia => {
                const puedeVer = puedeVerLicenciaDeRol(licencia.agente_rol, usuarioRol);
                if (!puedeVer) {
                    console.log(`🚫 ${usuarioRol} NO puede ver licencia de ${licencia.agente_rol} (${licencia.agente_nombre})`);
                }
                return puedeVer;
            });
            
            // FILTRO ADICIONAL: Agente y Agente Avanzado solo ven sus propias licencias
            if (usuarioRol.toLowerCase() === 'agente' || usuarioRol.toLowerCase() === 'agente avanzado') {
                console.log('🔒 Aplicando filtro restricto: solo licencias del usuario actual');
                resultado = resultado.filter(licencia => {
                    const esPropia = licencia.id_agente === usuarioId;
                    if (!esPropia) {
                        console.log(`🚫 Agente no puede ver licencia de otro agente:`, licencia.id_agente, 'vs', usuarioId);
                    }
                    return esPropia;
                });
            }
            
            console.log(`✅ Licencias filtradas: ${resultado.length} de ${$licencias.length} totales`);
        }

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
        soloSuArea: false,
        puedeAsignarSoloAgentes: false // Nuevo permiso para Agente Avanzado
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
            permisos.puedeAprobar = true; // Puede aprobar: Jefatura, Agente Avanzado, Agente de su área
            permisos.puedeRechazar = true;
            permisos.puedeAsignar = true;
            permisos.soloSuArea = true;
            break;
        
        case 'Jefatura':
            permisos.puedeCrear = true;
            permisos.puedeAprobar = true; // Puede aprobar: Agente Avanzado, Agente de su área
            permisos.puedeRechazar = true;
            permisos.puedeAsignar = true;
            permisos.soloSuArea = true;
            break;
        
        case 'Agente Avanzado':
            permisos.puedeCrear = true; // Solo puede solicitar licencia
            permisos.puedeAsignar = false; // NO puede asignar licencias
            permisos.soloSuArea = true;
            break;
            
        case 'Agente':
            permisos.puedeCrear = true; // Solo puede solicitar licencia
            permisos.soloSuArea = true;
            break;
    }

    return permisos;
}

/**
 * Determina quién puede aprobar una licencia según la jerarquía
 */
export function puedeAprobarLicencia(licencia, usuarioRol, usuarioArea) {
    // Solo licencias pendientes pueden ser aprobadas
    if (licencia.estado !== 'pendiente') {
        return false;
    }

    // Administrador puede aprobar todo
    if (usuarioRol === 'Administrador') {
        return true;
    }

    // Verificar que la licencia es del área del usuario (excepto administrador)
    if (licencia.id_agente_area !== usuarioArea) {
        return false;
    }

    if (usuarioRol === 'Director') {
        // Director puede aprobar licencias de Jefatura, Agente Avanzado y Agente de su área
        const rolesQueAprueba = ['Jefatura', 'Agente Avanzado', 'Agente'];
        return rolesQueAprueba.includes(licencia.agente_rol);
    }

    if (usuarioRol === 'Jefatura') {
        // Jefatura puede aprobar licencias de Agente Avanzado y Agente de su área
        const rolesQueAprueba = ['Agente Avanzado', 'Agente'];
        return rolesQueAprueba.includes(licencia.agente_rol);
    }

    // Agente Avanzado y Agente NO pueden aprobar licencias
    return false;
}

/**
 * Determina si el usuario puede asignar licencia a un agente específico
 */
export function puedeAsignarAAgente(agenteRol, usuarioRol, agenteArea, usuarioArea) {
    // Administrador puede asignar a cualquiera
    if (usuarioRol === 'Administrador') {
        return true;
    }

    // Verificar que el agente es del área del usuario (excepto administrador)
    if (agenteArea !== usuarioArea) {
        return false;
    }

    if (usuarioRol === 'Director') {
        // Director puede asignar a Jefatura, Agente Avanzado y Agente de su área
        const rolesQueAsigna = ['Jefatura', 'Agente Avanzado', 'Agente'];
        return rolesQueAsigna.includes(agenteRol);
    }

    if (usuarioRol === 'Jefatura') {
        // Jefatura puede asignar a Agente Avanzado y Agente de su área
        const rolesQueAsigna = ['Agente Avanzado', 'Agente'];
        return rolesQueAsigna.includes(agenteRol);
    }

    if (usuarioRol === 'Agente Avanzado') {
        // Agente Avanzado solo puede asignar a Agente de su área
        return agenteRol === 'Agente';
    }

    // Agente NO puede asignar licencias
    return false;
}

/**
 * Determina qué roles puede ver cada usuario según la jerarquía
 */
export function puedeVerLicenciaDeRol(licenciaRol, usuarioRol) {
    // Administrador puede ver todo
    if (usuarioRol === 'Administrador') {
        return true;
    }

    // Director puede ver licencias de: Director (propias), Jefatura, Agente Avanzado, Agente
    if (usuarioRol === 'Director') {
        const rolesQueVe = ['Director', 'Jefatura', 'Agente Avanzado', 'Agente'];
        return rolesQueVe.includes(licenciaRol);
    }

    // Jefatura puede ver licencias de: Jefatura (propias), Agente Avanzado, Agente
    if (usuarioRol === 'Jefatura') {
        const rolesQueVe = ['Jefatura', 'Agente Avanzado', 'Agente'];
        return rolesQueVe.includes(licenciaRol);
    }

    // Agente Avanzado puede ver licencias de: Agente Avanzado (propias), Agente
    if (usuarioRol === 'Agente Avanzado') {
        const rolesQueVe = ['Agente Avanzado', 'Agente'];
        return rolesQueVe.includes(licenciaRol);
    }

    // Agente solo puede ver sus propias licencias
    if (usuarioRol === 'Agente') {
        return licenciaRol === 'Agente';
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
        console.log('📊 Cargando licencias con parámetros:', parametros);
        const response = await asistenciaService.getLicencias(parametros);
        console.log('📊 Respuesta completa de licencias:', response);
        
        if (response?.data?.success) {
            const licenciasData = response.data.data || [];
            console.log('📊 Licencias procesadas:', licenciasData.length, licenciasData);
            
            // Debug: mostrar la primera licencia completa
            if (licenciasData.length > 0) {
                console.log('🔍 Primera licencia (estructura completa):', JSON.stringify(licenciasData[0], null, 2));
            }
            
            licencias.set(licenciasData);
        } else {
            throw new Error(response?.data?.message || 'Error al cargar licencias');
        }
    } catch (err) {
        console.error('❌ Error cargando licencias:', err);
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
            id_agente: datosAsignacion.id_agente,
            id_tipo_licencia: datosAsignacion.id_tipo_licencia,
            fecha_desde: datosAsignacion.fecha_desde,
            fecha_hasta: datosAsignacion.fecha_hasta,
            observaciones: datosAsignacion.observaciones || '',
            justificacion: datosAsignacion.justificacion || '',
            estado: 'pendiente' // Las licencias asignadas quedan pendientes de aprobación
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
        console.error('Detalles del error:', err?.response?.data);
        console.error('Status del error:', err?.response?.status);
        const errorMsg = err?.response?.data?.message || err.message || 'Error de conexión';
        error.set(errorMsg);
        return { success: false, error: errorMsg, response: err.response };
    } finally {
        loading.set(false);
    }
}

/**
 * Eliminar licencia
 */
export async function eliminarLicencia(idLicencia) {
    try {
        loading.set(true);
        error.set(null);

        const response = await asistenciaService.deleteLicencia(idLicencia);

        if (response?.status === 200 || response?.status === 204 || response?.data?.success) {
            // Recargar licencias después de eliminar
            await cargarLicencias();
            return { success: true };
        } else {
            const errorMsg = response?.data?.message || 'Error al eliminar la licencia';
            error.set(errorMsg);
            return { success: false, error: errorMsg };
        }
    } catch (err) {
        console.error('Error eliminando licencia:', err);
        console.error('Detalles del error:', err?.response?.data);
        console.error('Status del error:', err?.response?.status);
        const errorMsg = err?.response?.data?.message || err.message || 'Error de conexión';
        error.set(errorMsg);
        return { success: false, error: errorMsg };
    } finally {
        loading.set(false);
    }
}
