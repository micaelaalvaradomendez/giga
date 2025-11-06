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
};

// SERVICIOS PARA REPORTES
export const reportesService = {
  getReportes: () => api.get('/reportes/reportes/'),
  createReporte: (data) => api.post('/reportes/reportes/', data),
  getNotificaciones: () => api.get('/reportes/notificaciones/'),
  createNotificacion: (data) => api.post('/reportes/notificaciones/', data),
};

// SERVICIOS PARA CONVENIO IA
export const convenioIaService = {
  getConvenios: () => api.get('/convenio-ia/convenios/'),
  getConsultas: () => api.get('/convenio-ia/consultas/'),
  consultarConvenio: (pregunta) => api.post('/convenio-ia/consultar/', { pregunta }),
};

// SERVICIOS PARA AUDITORÍA
export const auditoriaService = {
  getParametros: () => api.get('/auditoria/parametros/'),
  getRegistrosAuditoria: () => api.get('/auditoria/registros/'),
};