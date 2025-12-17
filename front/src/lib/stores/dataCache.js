import { writable, derived, get } from 'svelte/store';

/**
 * Global Data Cache Store
 * 
 * Centraliza el almacenamiento de datos compartidos entre múltiples páginas
 * con sistema de caché inteligente basado en timestamps para evitar cargas duplicadas.
 * 
 * Características:
 * - Cache con Time To Live (TTL) configurable
 * - Validación automática de datos obsoletos
 * - Carga única compartida entre componentes
 * - Reducción de llamadas API redundantes
 */

const CACHE_TTL = {
feriados: 5 * 60 * 1000, // 5 minutos
areas: 10 * 60 * 1000, // 10 minutos
organigrama: 10 * 60 * 1000, // 10 minutos
guardias: 2 * 60 * 1000, // 2 minutos (más dinámico)
};

// Estructura de datos en caché
function createCachedStore(initialValue = null) {
return writable({
initialValue,
null,
g: false,
null
});
}

// Stores de datos cacheados
export const feriadosCache = createCachedStore([]);
export const areasCache = createCachedStore([]);
export const organigramaCache = createCachedStore(null);

// Store de estado de carga general
export const cacheLoading = writable(false);

/**
 * Verifica si los datos en caché están obsoletos
 */
function isCacheStale(timestamp, ttl) {
if (!timestamp) return true;
const now = Date.now();
return (now - timestamp) > ttl;
}

/**
 * Carga feriados desde API o caché
 */
export async function loadFeriados(forceRefresh = false) {
const cache = get(feriadosCache);

// Si no forzamos refresh y el caché es válido, retornar datos existentes
if (!forceRefresh && !isCacheStale(cache.timestamp, CACHE_TTL.feriados) && cache.data?.length > 0) {
sole.log('✅ Usando feriados desde caché', { 
t: cache.data.length,
Math.round((Date.now() - cache.timestamp) / 1000) + 's'
 cache.data;
}

// Evitar múltiples cargas simultáneas
if (cache.loading) {
sole.log('⏳ Carga de feriados ya en progreso, esperando...');
Esperar a que termine la carga actual con timeout
 new Promise((resolve, reject) => {
st timeout = setTimeout(() => {
subscribe();
ew Error('Timeout esperando carga de feriados'));
30000); // 30 segundos timeout
st unsubscribe = feriadosCache.subscribe((value) => {
(!value.loading) {
subscribe();
(value.error) {
ew Error(value.error));
else if (value.data) {
else {
ew Error('No se pudieron cargar los feriados'));

try {
=> ({ ...s, loading: true, error: null }));
sole.log('🔄 Cargando feriados desde API...');
st { guardiasService } = await import('$lib/services.js');
st response = await guardiasService.getFeriados();
st data = response.data?.results || response.data || [];
Date.now(),
g: false,
null
sole.log('✅ Feriados cargados y cacheados', { count: data.length });
 data;
} catch (error) {
sole.error('❌ Error cargando feriados:', error);
=> ({ 

g: false, 
error.message || 'Error al cargar feriados'
error;
}
}

/**
 * Carga áreas desde API o caché
 */
export async function loadAreas(forceRefresh = false) {
const cache = get(areasCache);

if (!forceRefresh && !isCacheStale(cache.timestamp, CACHE_TTL.areas) && cache.data?.length > 0) {
sole.log('✅ Usando áreas desde caché', { 
t: cache.data.length,
Math.round((Date.now() - cache.timestamp) / 1000) + 's'
 cache.data;
}

if (cache.loading) {
sole.log('⏳ Carga de áreas ya en progreso, esperando...');
 new Promise((resolve, reject) => {
st timeout = setTimeout(() => {
subscribe();
ew Error('Timeout esperando carga de áreas'));
30000); // 30 segundos timeout
st unsubscribe = areasCache.subscribe((value) => {
(!value.loading) {
subscribe();
(value.error) {
ew Error(value.error));
else if (value.data) {
else {
ew Error('No se pudieron cargar las áreas'));

try {
=> ({ ...s, loading: true, error: null }));
sole.log('🔄 Cargando áreas desde API...');
st { personasService } = await import('$lib/services.js');
st response = await personasService.getAreas();
st data = response.data?.results || response.data || [];
Date.now(),
g: false,
null
sole.log('✅ Áreas cargadas y cacheadas', { count: data.length });
 data;
} catch (error) {
sole.error('❌ Error cargando áreas:', error);
=> ({ 

g: false, 
error.message || 'Error al cargar áreas'
error;
}
}

/**
 * Carga organigrama desde API o caché
 */
export async function loadOrganigrama(forceRefresh = false) {
const cache = get(organigramaCache);

if (!forceRefresh && !isCacheStale(cache.timestamp, CACHE_TTL.organigrama) && cache.data) {
sole.log('✅ Usando organigrama desde caché', { 
Math.round((Date.now() - cache.timestamp) / 1000) + 's'
 cache.data;
}

if (cache.loading) {
sole.log('⏳ Carga de organigrama ya en progreso, esperando...');
 new Promise((resolve, reject) => {
st timeout = setTimeout(() => {
subscribe();
ew Error('Timeout esperando carga de organigrama'));
30000); // 30 segundos timeout
st unsubscribe = organigramaCache.subscribe((value) => {
 if (!value.loading) {
subscribe();
(value.error) {
ew Error(value.error));
else if (value.data) {
else {
ew Error('No se pudo cargar el organigrama'));

try {
igramaCache.update(s => ({ ...s, loading: true, error: null }));
sole.log('🔄 Cargando organigrama desde API...');
st { organigramaService } = await import('$lib/services.js');
st response = await organigramaService.getOrganigrama();
data = null;
Validar explícitamente que success es true
(response.data && response.data.success === true) {
= {
: response.data.data.version,
response.data.data.actualizado_en,
: response.data.data.creado_por,
igrama: response.data.data.estructura,
igramaCache.set({
Date.now(),
g: false,
null
sole.log('✅ Organigrama cargado y cacheado');
 data;
} catch (error) {
sole.error('❌ Error cargando organigrama:', error);
igramaCache.update(s => ({ 

g: false, 
error.message || 'Error al cargar organigrama'
error;
}
}

/**
 * Invalida el caché de un recurso específico
 */
export function invalidateCache(resource) {
switch(resource) {
'feriados':
=> ({ ...s, timestamp: null }));
sole.log('🧹 Caché de feriados invalidado');
'areas':
=> ({ ...s, timestamp: null }));
sole.log('🧹 Caché de áreas invalidado');
'organigrama':
igramaCache.update(s => ({ ...s, timestamp: null }));
sole.log('🧹 Caché de organigrama invalidado');
'all':
=> ({ ...s, timestamp: null }));
=> ({ ...s, timestamp: null }));
igramaCache.update(s => ({ ...s, timestamp: null }));
sole.log('🧹 Todo el caché invalidado');
}

/**
 * Limpia completamente el caché
 */
export function clearCache() {
feriadosCache.set({ data: [], timestamp: null, loading: false, error: null });
areasCache.set({ data: [], timestamp: null, loading: false, error: null });
organigramaCache.set({ data: null, timestamp: null, loading: false, error: null });
console.log('🧹 Caché completamente limpiado');
}

/**
 * Stores derivados para acceso fácil a datos
 */
export const feriados = derived(feriadosCache, $cache => $cache.data || []);
export const areas = derived(areasCache, $cache => $cache.data || []);
export const organigrama = derived(organigramaCache, $cache => $cache.data);

/**
 * Stores derivados para estado de carga
 */
export const feriadosLoading = derived(feriadosCache, $cache => $cache.loading);
export const areasLoading = derived(areasCache, $cache => $cache.loading);
export const organigramaLoading = derived(organigramaCache, $cache => $cache.loading);
