import { createApiClient } from './api.js';

// SERVICIOS PARA PERSONAS
export const personasService = {
  // Agentes
  getAllAgentes: (token = null) => createApiClient(token).get('/personas/agentes/'),
  getAgente: (id, token = null) => createApiClient(token).get(`/personas/agentes/${id}/`),
  createAgente: (data, token = null) => createApiClient(token).post('/personas/agentes/', data),
  updateAgente: (id, data, token = null) => createApiClient(token).put(`/personas/agentes/${id}/`, data),
  deleteAgente: (id, token = null) => createApiClient(token).delete(`/personas/agentes/${id}/`),

  // Áreas
  getAreas: (token = null) => createApiClient(token).get('/personas/areas/'),
  getArea: (id, token = null) => createApiClient(token).get(`/personas/areas/${id}/`),
  createArea: (data, token = null) => createApiClient(token).post('/personas/areas/', data),
  updateArea: (id, data, token = null) => createApiClient(token).put(`/personas/areas/${id}/`, data),
  deleteArea: (id, token = null) => createApiClient(token).delete(`/personas/areas/${id}/`),

  // Roles
  getRoles: (token = null) => createApiClient(token).get('/personas/roles/'),
  getRol: (id, token = null) => createApiClient(token).get(`/personas/roles/${id}/`),
  createRol: (data, token = null) => createApiClient(token).post('/personas/roles/', data),
  updateRol: (id, data, token = null) => createApiClient(token).put(`/personas/roles/${id}/`, data),
  deleteRol: (id, token = null) => createApiClient(token).delete(`/personas/roles/${id}/`),
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