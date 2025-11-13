import { createApiClient } from './api.js';

// SERVICIOS PARA PERSONAS
export const personasService = {
  // Agentes
  getAllAgentes: (token = null) => createApiClient(token).get('/personas/agentes/'),
  getAgentes: (token = null) => createApiClient(token).get('/personas/agentes/'), // Alias para consistencia
  getAgente: (id, token = null) => createApiClient(token).get(`/personas/agentes/${id}/`),
  createAgente: (data, token = null) => createApiClient(token).post('/personas/agentes/create/', data),
  updateAgente: (id, data, token = null) => createApiClient(token).patch(`/personas/agentes/${id}/update/`, data),
  deleteAgente: (id, token = null) => createApiClient(token).delete(`/personas/agentes/${id}/delete/`),

  	// Crear agente con rol asignado
	async createAgenteConRol(agenteData) {
		try {
			console.log('Datos enviados a createAgente:', agenteData);
			// Primero crear el agente
			const response = await this.createAgente(agenteData);
			console.log('Respuesta del agente creado:', response);
			
			if (response && response.usuario && agenteData.rol_id) {
				// Luego asignar el rol usando el usuario_id del agente creado
				const asignacionData = {
					usuario: response.usuario,  // Usar el ID del usuario, no del agente
					rol: agenteData.rol_id,
					area: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', // ID por defecto del área: Secretaría de Protección Civil
				};
				
				console.log('Datos de asignación:', asignacionData);
				await this.createAsignacion(asignacionData);
			}
			
			return response;
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

  // Novedades
  getNovedades: () => api.get('/asistencia/novedades/'),
  getNovedad: (id) => api.get(`/asistencia/novedades/${id}/`),
  createNovedad: (data) => api.post('/asistencia/novedades/', data),
  updateNovedad: (id, data) => api.put(`/asistencia/novedades/${id}/`, data),
};

// SERVICIOS PARA GUARDIAS
export const guardiasService = {
  // Cronogramas
  getCronogramas: () => api.get('/guardias/cronogramas/'),
  getCronograma: (id) => api.get(`/guardias/cronogramas/${id}/`),
  createCronograma: (data) => api.post('/guardias/cronogramas/', data),
  updateCronograma: (id, data) => api.put(`/guardias/cronogramas/${id}/`, data),

  // Guardias
  getGuardias: () => api.get('/guardias/guardias/'),
  getGuardia: (id) => api.get(`/guardias/guardias/${id}/`),
  createGuardia: (data) => api.post('/guardias/guardias/', data),
  updateGuardia: (id, data) => api.put(`/guardias/guardias/${id}/`, data),

  // Feriados
  getFeriados: () => api.get('/guardias/feriados/'),
  createFeriado: (data) => api.post('/guardias/feriados/', data),
  updateFeriado: (id, data) => api.put(`/guardias/feriados/${id}/`, data),
  deleteFeriado: (id) => api.delete(`/guardias/feriados/${id}/`),
};

/* SERVICIOS PARA REPORTES
export const reportesService = {
  getReportes: () => api.get('/reportes/reportes/'),
  createReporte: (data) => api.post('/reportes/reportes/', data),
  getNotificaciones: () => api.get('/reportes/notificaciones/'),
  createNotificacion: (data) => api.post('/reportes/notificaciones/', data),
};*/

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
  getParametros: () => api.get('/auditoria/parametros/'),
  getRegistrosAuditoria: () => api.get('/auditoria/registros/'),
};