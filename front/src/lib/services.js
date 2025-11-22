import { createApiClient, API_BASE_URL } from './api.js';

// Exportar API_BASE_URL para uso directo
export { API_BASE_URL };

// Cliente API por defecto para compatibilidad con servicios legacy
const api = createApiClient();

// SERVICIOS PARA PERSONAS
export const personasService = {
  // Agentes
  getAllAgentes: (token = null) => createApiClient(token).get('/personas/agentes/'),
  getAgentes: (token = null) => createApiClient(token).get('/personas/agentes/'), // Alias para consistencia
  getAgentesByArea: (areaId, token = null) => createApiClient(token).get(`/personas/agentes/?area=${areaId}`),
  getAgente: (id, token = null) => createApiClient(token).get(`/personas/agentes/${id}/`),
  createAgente: (data, token = null) => createApiClient(token).post('/personas/agentes/create/', data),
  updateAgente: (id, data, token = null) => createApiClient(token).patch(`/personas/agentes/${id}/update/`, data),
  deleteAgente: (id, token = null) => createApiClient(token).delete(`/personas/agentes/${id}/delete/`),

  	// Crear agente con rol asignado
	async createAgenteConRol(agenteData) {
		try {
			console.log('Datos enviados a createAgente:', agenteData);
			// El backend AgenteCreateUpdateSerializer ya maneja la asignación de rol
			// cuando se envía rol_id, por lo que no necesitamos crear asignación separada
			const response = await this.createAgente(agenteData);
			console.log('Respuesta del agente creado:', response);
			
			// Devolver la respuesta directamente - el rol ya está asignado automáticamente
			const agenteData_response = response.data?.data || response.data;
			return agenteData_response || response;
		} catch (error) {
			console.error('Error creando agente con rol:', error);
			throw error;
		}
	},

  // Áreas
  getAreas: (token = null) => createApiClient(token).get('/personas/catalogs/areas/'),
  getArea: (id, token = null) => createApiClient(token).get(`/personas/catalogs/areas/${id}/`),
  createArea: (data, token = null) => createApiClient(token).post('/personas/parametros/areas/create/', data),
  updateArea: (id, data, token = null) => createApiClient(token).put(`/personas/parametros/areas/${id}/update/`, data),
  deleteArea: (id, token = null) => createApiClient(token).delete(`/personas/parametros/areas/${id}/delete/`),
  updateAreaSchedule: (id, data, token = null) => createApiClient(token).post(`/personas/parametros/areas/${id}/schedule/`, data),

  // Roles
  getRoles: (token = null) => createApiClient(token).get('/personas/catalogs/roles/'),
  getRol: (id, token = null) => createApiClient(token).get(`/personas/catalogs/roles/${id}/`),
  createRol: (data, token = null) => createApiClient(token).post('/personas/catalogs/roles/', data),
  updateRol: (id, data, token = null) => createApiClient(token).patch(`/personas/catalogs/roles/${id}/`, data),
  deleteRol: (id, token = null) => createApiClient(token).delete(`/personas/catalogs/roles/${id}/`),

  // Asignaciones de roles
  getAsignaciones: (token = null) => createApiClient(token).get('/personas/asignaciones/'),
  createAsignacion: (data, token = null) => createApiClient(token).post('/personas/asignaciones/create/', data),
  deleteAsignacion: (id, token = null) => createApiClient(token).delete(`/personas/asignaciones/${id}/delete/`),
  
  // Cambio de roles atómico
  cambiarRolAgente: (data, token = null) => createApiClient(token).post('/personas/asignaciones/cambiar-rol/', data),
  
  // Limpieza de datos
  limpiarRolesDuplicados: (token = null) => createApiClient(token).post('/personas/asignaciones/limpiar-duplicados/'),

  // Agrupaciones organizacionales
  getAgrupaciones: (token = null) => createApiClient(token).get('/personas/parametros/agrupaciones/'),
  createAgrupacion: (data, token = null) => createApiClient(token).post('/personas/parametros/agrupaciones/create/', data),
  updateAgrupacion: (id, data, token = null) => createApiClient(token).put(`/personas/parametros/agrupaciones/${id}/update/`, data),
  deleteAgrupacion: (id, data = null, token = null) => createApiClient(token).delete(`/personas/parametros/agrupaciones/${id}/delete/`, { data }),
  updateAgrupacionSchedule: (data, token = null) => createApiClient(token).post('/personas/parametros/agrupaciones/schedule/', data),
  renameAgrupacion: (data, token = null) => createApiClient(token).post('/personas/parametros/agrupaciones/rename/', data),
};

// SERVICIOS PARA ASISTENCIA
export const asistenciaService = {
  // Asistencias
  getAsistencias: () => api.get('/asistencia/asistencias/'),
  getAsistencia: (id) => api.get(`/asistencia/asistencias/${id}/`),
  createAsistencia: (data) => api.post('/asistencia/asistencias/', data),
  updateAsistencia: (id, data) => api.put(`/asistencia/asistencias/${id}/`, data),

  // Marcas
  getMarcas: () => api.get('/asistencia/marcas/'),
  createMarca: (data) => api.post('/asistencia/marcas/', data),

  // Licencias
  getLicencias: () => api.get('/asistencia/licencias/'),
  getLicencia: (id) => api.get(`/asistencia/licencias/${id}/`),
  createLicencia: (data) => api.post('/asistencia/licencias/', data),
  updateLicencia: (id, data) => api.put(`/asistencia/licencias/${id}/`, data),
  // Tipos de licencia (ABM - nomenclador)
  getTiposLicencia: (token = null) => createApiClient(token).get('/asistencia/admin/tipos-licencia/'),
  createTipoLicencia: (data, token = null) => createApiClient(token).post('/asistencia/admin/tipos-licencia/crear/', data),
  updateTipoLicencia: (id, data, token = null) => createApiClient(token).put(`/asistencia/admin/tipos-licencia/actualizar/${id}/`, data),
  deleteTipoLicencia: (id, token = null) => createApiClient(token).delete(`/asistencia/admin/tipos-licencia/eliminar/${id}/`),

  // Novedades
  getNovedades: () => api.get('/asistencia/novedades/'),
  getNovedad: (id) => api.get(`/asistencia/novedades/${id}/`),
  createNovedad: (data) => api.post('/asistencia/novedades/', data),
  updateNovedad: (id, data) => api.put(`/asistencia/novedades/${id}/`, data),
};

// SERVICIOS PARA GUARDIAS
export const guardiasService = {
  // Cronogramas
  getCronogramas: (token = null) => createApiClient(token).get('/guardias/cronogramas/'),
  getCronogramasPendientes: (token = null) => createApiClient(token).get('/guardias/cronogramas/'),
  getCronogramasAprobadas: (token = null) => createApiClient(token).get('/guardias/cronogramas/?estado=publicada'),
  getCronograma: (id, token = null) => createApiClient(token).get(`/guardias/cronogramas/${id}/`),
  createCronograma: (data, token = null) => createApiClient(token).post('/guardias/cronogramas/', data),
  updateCronograma: (id, data, token = null) => createApiClient(token).put(`/guardias/cronogramas/${id}/`, data),
  planificar: (data, token = null) => createApiClient(token).post('/guardias/cronogramas/planificar/', data),
  aprobarCronograma: (id, data, token = null) => createApiClient(token).patch(`/guardias/cronogramas/${id}/aprobar/`, data),
  publicarCronograma: (id, token = null) => createApiClient(token).patch(`/guardias/cronogramas/${id}/publicar/`),
  crearGuardia: (data, token = null) => createApiClient(token).post('/guardias/cronogramas/crear_con_guardias/', data),
  actualizarConGuardias: (id, data, token = null) => createApiClient(token).put(`/guardias/cronogramas/${id}/actualizar_con_guardias/`, data),
  
  // Aprobaciones jerárquicas
  getPendientesAprobacion: (agenteId, token = null) => createApiClient(token).get(`/guardias/cronogramas/pendientes/?agente_id=${agenteId}`),
  rechazarCronograma: (id, data, token = null) => createApiClient(token).post(`/guardias/cronogramas/${id}/rechazar/`, data),
  deleteCronograma: (id, token = null) => createApiClient(token).delete(`/guardias/cronogramas/${id}/`),
  despublicarCronograma: (id, data, token = null) => createApiClient(token).patch(`/guardias/cronogramas/${id}/despublicar/`, data),
  eliminarCronograma: (id, data, token = null) => createApiClient(token).delete(`/guardias/cronogramas/${id}/eliminar/?agente_id=${data.agente_id}`),

  // Guardias
  getGuardias: (token = null) => createApiClient(token).get('/guardias/guardias/'),
  getGuardia: (id, token = null) => createApiClient(token).get(`/guardias/guardias/${id}/`),
  createGuardia: (data, token = null) => createApiClient(token).post('/guardias/guardias/', data),
  updateGuardia: (id, data, token = null) => createApiClient(token).put(`/guardias/guardias/${id}/`, data),
  deleteGuardia: (id, token = null) => createApiClient(token).delete(`/guardias/guardias/${id}/`),
  getResumenGuardias: (params = '', token = null) => createApiClient(token).get(`/guardias/guardias/resumen/?${params}`),
  getGuardiasAgente: (agenteId, token = null) => createApiClient(token).get(`/guardias/guardias/resumen/?agente=${agenteId}`),
  getGuardiasPorCronograma: (cronogramaId, token = null) => createApiClient(token).get(`/guardias/guardias/resumen/?id_cronograma=${cronogramaId}`),
  
  // Notas de guardias
  getNotasGuardia: (guardiaId, token = null) => createApiClient(token).get(`/guardias/guardias/${guardiaId}/notas/`),
  createNotaGuardia: (guardiaId, data, token = null) => createApiClient(token).post(`/guardias/guardias/${guardiaId}/notas/`, data),
  updateNotaGuardia: (notaId, data, token = null) => createApiClient(token).put(`/guardias/guardias/notas/${notaId}/`, data),
  deleteNotaGuardia: (notaId, agenteId, token = null) => createApiClient(token).delete(`/guardias/guardias/notas/${notaId}/?agente_id=${agenteId}`),
  
  // Verificaciones de disponibilidad
  verificarDisponibilidad: (agenteId, fecha, token = null) => createApiClient(token).get(`/guardias/guardias/verificar_disponibilidad/?agente=${agenteId}&fecha=${fecha}`),

  // Feriados
  getFeriados: (token = null) => createApiClient(token).get('/guardias/feriados/'),
  getFeriado: (id, token = null) => createApiClient(token).get(`/guardias/feriados/${id}/`),
  createFeriado: (data, token = null) => createApiClient(token).post('/guardias/feriados/', data),
  updateFeriado: (id, data, token = null) => createApiClient(token).put(`/guardias/feriados/${id}/`, data),
  deleteFeriado: (id, token = null) => createApiClient(token).delete(`/guardias/feriados/${id}/`),
  verificarFeriado: (data, token = null) => createApiClient(token).post('/guardias/feriados/verificar_fecha/', data),
  
  // Reglas de Plus
  getReglasPlus: (token = null) => createApiClient(token).get('/guardias/reglas-plus/'),
  getReglaPlus: (id, token = null) => createApiClient(token).get(`/guardias/reglas-plus/${id}/`),
  createReglaPlus: (data, token = null) => createApiClient(token).post('/guardias/reglas-plus/', data),
  updateReglaPlus: (id, data, token = null) => createApiClient(token).put(`/guardias/reglas-plus/${id}/`, data),
  deleteReglaPlus: (id, token = null) => createApiClient(token).delete(`/guardias/reglas-plus/${id}/`),
  simularReglaPlus: (id, data, token = null) => createApiClient(token).post(`/guardias/reglas-plus/${id}/simular/`, data),
  
  // Parámetros de Área
  getParametrosArea: (params = '', token = null) => createApiClient(token).get(`/guardias/parametros-area/?${params}`),
  getParametroArea: (id, token = null) => createApiClient(token).get(`/guardias/parametros-area/${id}/`),
  createParametroArea: (data, token = null) => createApiClient(token).post('/guardias/parametros-area/', data),
  updateParametroArea: (id, data, token = null) => createApiClient(token).put(`/guardias/parametros-area/${id}/`, data),
  
  // Resúmenes Mensuales
  getResumenesMensuales: (params = '', token = null) => createApiClient(token).get(`/guardias/resumen-mes/?${params}`),
  getResumenMensual: (id, token = null) => createApiClient(token).get(`/guardias/resumen-mes/${id}/`),
  calcularPlusMensual: (data, token = null) => createApiClient(token).post('/guardias/resumen-mes/calcular_mensual/', data),
  aprobarLotePlus: (data, token = null) => createApiClient(token).patch('/guardias/resumen-mes/aprobar_lote/', data),
  
  // Reportes según documentación
  getReporteIndividual: (params = '', token = null) => createApiClient(token).get(`/guardias/guardias/reporte_individual/?${params}`),
  getReporteGeneral: (params = '', token = null) => createApiClient(token).get(`/guardias/guardias/reporte_general/?${params}`),
  
  // Nuevos reportes según especificaciones
  getReporteHorasTrabajadas: (params = '', token = null) => createApiClient(token).get(`/guardias/guardias/reporte_horas_trabajadas/?${params}`),
  getReporteParteDiario: (params = '', token = null) => createApiClient(token).get(`/asistencia/reporte_parte_diario/?${params}`),
  getReporteResumenLicencias: (params = '', token = null) => createApiClient(token).get(`/asistencia/reporte_licencias/?${params}`),
  getReporteCalculoPlus: (params = '', token = null) => createApiClient(token).get(`/guardias/guardias/reporte_calculo_plus/?${params}`),
  getReporteIncumplimientoNormativo: (params = '', token = null) => createApiClient(token).get(`/guardias/guardias/reporte_incumplimiento/?${params}`),

  // Exportaciones (placeholder para futura implementación)
  exportarReporteIndividual: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/guardias/reportes/individual/?${params}&formato=${formato}`, { responseType: 'blob' }),
  exportarReporteGeneral: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/guardias/reportes/general/?${params}&formato=${formato}`, { responseType: 'blob' }),
  exportarReporteHorasTrabajadas: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/guardias/reportes/horas_trabajadas/?${params}&formato=${formato}`, { responseType: 'blob' }),
  exportarReporteParteDiario: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/asistencia/reportes/parte_diario/?${params}&formato=${formato}`, { responseType: 'blob' }),
  exportarReporteResumenLicencias: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/asistencia/reportes/licencias/?${params}&formato=${formato}`, { responseType: 'blob' }),
  exportarReporteCalculoPlus: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/guardias/reportes/calculo_plus/?${params}&formato=${formato}`, { responseType: 'blob' }),
  exportarReporteIncumplimientoNormativo: (params = '', formato = 'pdf', token = null) => 
    createApiClient(token).get(`/guardias/reportes/incumplimiento/?${params}&formato=${formato}`, { responseType: 'blob' }),
};

// SERVICIOS PARA CONVENIO IA - Conectado a N8N
export const convenioIaService = {
  // URL del webhook de N8N en modo producción
  N8N_WEBHOOK_URL: 'http://localhost:5678/webhook/3ebdf75e-f0e2-4d18-b070-498f1486d845',
  
  /**
   * Consulta al convenio usando N8N + IA
   * @param {string} pregunta - La pregunta del usuario
   * @returns {Promise} - Respuesta de la IA
   */
  async consultarConvenio(pregunta) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 70000);
      
      const response = await fetch(this.N8N_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chatInput: pregunta
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // N8N puede devolver texto plano o JSON de la IA
      const textoRespuesta = await response.text();
      
      // Intentar parsear como JSON
      try {
        const jsonResponse = JSON.parse(textoRespuesta);
        
        // Verificar que sea un objeto real (no un string, array vacío, etc.)
        if (typeof jsonResponse === 'object' && jsonResponse !== null && !Array.isArray(jsonResponse) && Object.keys(jsonResponse).length > 0) {
          
          // Si es un objeto con una sola propiedad string, extraer su valor
          const keys = Object.keys(jsonResponse);
          if (keys.length === 1 && typeof jsonResponse[keys[0]] === 'string') {
            return { respuesta: jsonResponse[keys[0]] };
          }
          
          // Para JSONs estructurados complejos, convertir a texto legible
          const formatearJson = (obj, nivel = 0) => {
            let resultado = '';
            const espacios = '  '.repeat(nivel);
            
            for (const [clave, valor] of Object.entries(obj)) {
              // Convertir claves snake_case a formato legible
              const claveFormateada = clave.replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase());
              
              if (typeof valor === 'string') {
                const valorFormateado = valor.replace(/_/g, ' ');
                if (nivel === 0) {
                  resultado += `<strong>${claveFormateada}:</strong> ${valorFormateado}\n\n`;
                } else {
                  resultado += `${espacios}    • <strong>${claveFormateada}:</strong> ${valorFormateado}\n`;
                }
              } else if (Array.isArray(valor)) {
                resultado += `${espacios}    <strong>${claveFormateada}:</strong>\n`;
                valor.forEach((item, index) => {
                  if (typeof item === 'object' && item !== null) {
                    // Si es un objeto, formatearlo recursivamente
                    resultado += `${espacios}      ${index + 1}. `;
                    const subResultado = formatearJson(item, nivel + 2);
                    // Eliminar el primer salto de línea y añadir indentación
                    resultado += subResultado.replace(/^\n/, '').replace(/\n/g, `\n${espacios}         `);
                    resultado += '\n';
                  } else {
                    // Si es un valor simple
                    resultado += `${espacios}      - ${item}\n`;
                  }
                });
                resultado += '\n';
              } else if (typeof valor === 'object' && valor !== null) {
                // Título más grande para secciones principales
                if (nivel === 0) {
                  resultado += `<h3>${claveFormateada}</h3>\n`;
                } else {
                  resultado += `${espacios}    <strong>${claveFormateada}:</strong>\n`;
                }
                resultado += formatearJson(valor, nivel + 1);
              }
            }
            return resultado;
          };
          
          return { respuesta: formatearJson(jsonResponse).trim() };
        }
      } catch (e) {
        // No es JSON válido, continuar con texto plano
      }
      
      // Es texto plano, devolver tal como viene
      return { respuesta: textoRespuesta };
      
    } catch (error) {
      console.error('Error consultando convenio:', error);
      if (error.name === 'AbortError') {
        throw new Error('Timeout: La consulta está tardando más de lo esperado. La IA podría estar procesando un archivo grande.');
      }
      throw new Error(`Error al conectar con el servicio de IA: ${error.message}`);
    }
  },


};

// SERVICIOS PARA AUDITORÍA
export const auditoriaService = {
  getParametros: (token = null) => createApiClient(token).get('/auditoria/parametros/'),
  getRegistrosAuditoria: (token = null) => createApiClient(token).get('/auditoria/registros/'),
};