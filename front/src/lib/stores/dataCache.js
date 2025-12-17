import { browser } from '$app/environment';
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
		data: initialValue,
		timestamp: null,
		loading: false,
		error: null
	});
}

// Stores de datos cacheados - solo crear en el cliente
export const feriadosCache = browser ? createCachedStore([]) : writable({ data: [], timestamp: null, loading: false, error: null });
export const areasCache = browser ? createCachedStore([]) : writable({ data: [], timestamp: null, loading: false, error: null });
export const organigramaCache = browser ? createCachedStore(null) : writable({ data: null, timestamp: null, loading: false, error: null });

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
	// Prevenir ejecución en SSR
	if (!browser) {
		return [];
	}
	
	const cache = get(feriadosCache);

	// Si no forzamos refresh y el caché es válido, retornar datos existentes
	if (!forceRefresh && !isCacheStale(cache.timestamp, CACHE_TTL.feriados) && cache.data?.length > 0) {
		console.log('✅ Usando feriados desde caché', {
			count: cache.data.length,
			age: Math.round((Date.now() - cache.timestamp) / 1000) + 's'
		});
		return cache.data;
	}

	// Evitar múltiples cargas simultáneas
	if (cache.loading) {
		console.log('⏳ Carga de feriados ya en progreso, esperando...');
		// Esperar a que termine la carga actual con timeout
		return new Promise((resolve, reject) => {
			const timeout = setTimeout(() => {
				unsubscribe();
				reject(new Error('Timeout esperando carga de feriados'));
			}, 30000); // 30 segundos timeout

			const unsubscribe = feriadosCache.subscribe((value) => {
				if (!value.loading) {
					clearTimeout(timeout);
					unsubscribe();
					if (value.error) {
						reject(new Error(value.error));
					} else if (value.data) {
						resolve(value.data);
					} else {
						reject(new Error('No se pudieron cargar los feriados'));
					}
				}
			});
		});
	}

	try {
		feriadosCache.update(s => ({ ...s, loading: true, error: null }));
		console.log('🔄 Cargando feriados desde API...');

		const { guardiasService } = await import('$lib/services.js');
		const response = await guardiasService.getFeriados();
		const data = response.data?.results || response.data || [];

		feriadosCache.set({
			data,
			timestamp: Date.now(),
			loading: false,
			error: null
		});

		console.log('✅ Feriados cargados y cacheados', { count: data.length });
		return data;
	} catch (error) {
		console.error('❌ Error cargando feriados:', error);
		feriadosCache.update(s => ({
			...s,
			loading: false,
			error: error.message || 'Error al cargar feriados'
		}));
		throw error;
	}
}

/**
 * Carga áreas desde API o caché
 */
export async function loadAreas(forceRefresh = false) {
	// Prevenir ejecución en SSR
	if (!browser) {
		return [];
	}
	
	const cache = get(areasCache);

	if (!forceRefresh && !isCacheStale(cache.timestamp, CACHE_TTL.areas) && cache.data?.length > 0) {
		console.log('✅ Usando áreas desde caché', {
			count: cache.data.length,
			age: Math.round((Date.now() - cache.timestamp) / 1000) + 's'
		});
		return cache.data;
	}

	if (cache.loading) {
		console.log('⏳ Carga de áreas ya en progreso, esperando...');
		return new Promise((resolve, reject) => {
			const timeout = setTimeout(() => {
				unsubscribe();
				reject(new Error('Timeout esperando carga de áreas'));
			}, 30000); // 30 segundos timeout

			const unsubscribe = areasCache.subscribe((value) => {
				if (!value.loading) {
					clearTimeout(timeout);
					unsubscribe();
					if (value.error) {
						reject(new Error(value.error));
					} else if (value.data) {
						resolve(value.data);
					} else {
						reject(new Error('No se pudieron cargar las áreas'));
					}
				}
			});
		});
	}

	try {
		areasCache.update(s => ({ ...s, loading: true, error: null }));
		console.log('🔄 Cargando áreas desde API...');

		const { personasService } = await import('$lib/services.js');
		const response = await personasService.getAreas();
		const data = response.data?.results || response.data || [];

		areasCache.set({
			data,
			timestamp: Date.now(),
			loading: false,
			error: null
		});

		console.log('✅ Áreas cargadas y cacheadas', { count: data.length });
		return data;
	} catch (error) {
		console.error('❌ Error cargando áreas:', error);
		areasCache.update(s => ({
			...s,
			loading: false,
			error: error.message || 'Error al cargar áreas'
		}));
		throw error;
	}
}

/**
 * Carga organigrama desde API o caché
 */
export async function loadOrganigrama(forceRefresh = false) {
	// Prevenir ejecución en SSR
	if (!browser) {
		return null;
	}
	
	const cache = get(organigramaCache);

	if (!forceRefresh && !isCacheStale(cache.timestamp, CACHE_TTL.organigrama) && cache.data) {
		console.log('✅ Usando organigrama desde caché', {
			age: Math.round((Date.now() - cache.timestamp) / 1000) + 's'
		});
		return cache.data;
	}

	if (cache.loading) {
		console.log('⏳ Carga de organigrama ya en progreso, esperando...');
		return new Promise((resolve, reject) => {
			const timeout = setTimeout(() => {
				unsubscribe();
				reject(new Error('Timeout esperando carga de organigrama'));
			}, 30000); // 30 segundos timeout

			const unsubscribe = organigramaCache.subscribe((value) => {
				if (!value.loading) {
					clearTimeout(timeout);
					unsubscribe();
					if (value.error) {
						reject(new Error(value.error));
					} else if (value.data) {
						resolve(value.data);
					} else {
						reject(new Error('No se pudo cargar el organigrama'));
					}
				}
			});
		});
	}

	try {
		organigramaCache.update(s => ({ ...s, loading: true, error: null }));
		console.log('🔄 Cargando organigrama desde API...');

		const { organigramaService } = await import('$lib/services.js');
		const response = await organigramaService.getOrganigrama();

		let data = null;
		// Validar explícitamente que success es true
		if (response.data && response.data.success === true) {
			data = {
				version: response.data.data.version,
				lastUpdated: response.data.data.actualizado_en,
				updatedBy: response.data.data.creado_por,
				organigrama: response.data.data.estructura,
			};
		}

		organigramaCache.set({
			data,
			timestamp: Date.now(),
			loading: false,
			error: null
		});

		console.log('✅ Organigrama cargado y cacheado');
		return data;
	} catch (error) {
		console.error('❌ Error cargando organigrama:', error);
		organigramaCache.update(s => ({
			...s,
			loading: false,
			error: error.message || 'Error al cargar organigrama'
		}));
		throw error;
	}
}

/**
 * Invalida el caché de un recurso específico
 */
export function invalidateCache(resource) {
	switch (resource) {
		case 'feriados':
			feriadosCache.update(s => ({ ...s, timestamp: null }));
			console.log('🧹 Caché de feriados invalidado');
			break;
		case 'areas':
			areasCache.update(s => ({ ...s, timestamp: null }));
			console.log('🧹 Caché de áreas invalidado');
			break;
		case 'organigrama':
			organigramaCache.update(s => ({ ...s, timestamp: null }));
			console.log('🧹 Caché de organigrama invalidado');
			break;
		case 'all':
			feriadosCache.update(s => ({ ...s, timestamp: null }));
			areasCache.update(s => ({ ...s, timestamp: null }));
			organigramaCache.update(s => ({ ...s, timestamp: null }));
			console.log('🧹 Todo el caché invalidado');
			break;
	}
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
