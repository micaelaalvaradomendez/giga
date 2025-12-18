import { browser } from '$app/environment';
import { writable, derived } from 'svelte/store';
import { personasService } from '$lib/services.js';
import AuthService from '$lib/login/authService.js';

/**
 * Controlador para la visualización del organigrama organizacional
 * Centraliza toda la lógica de negocio relacionada con la estructura organizacional
 */
class OrganigramaController {
	constructor() {
		// Prevenir inicialización en SSR
		if (!browser) {
			return;
		}

		// Stores principales
		this.agentes = writable([]);
		this.areas = writable([]);
		this.roles = writable([]);
		this.loading = writable(true);
		this.error = writable(null);

		// Stores para filtros y vista
		this.vistaActual = writable('jerarquica'); // 'jerarquica', 'areas', 'roles'
		this.filtroArea = writable('');
		this.filtroRol = writable('');
		this.busqueda = writable('');


		this.estructuraOrganizacional = derived(
			[this.agentes, this.areas, this.roles, this.vistaActual, this.filtroArea, this.filtroRol, this.busqueda],
			([$agentes, $areas, $roles, $vistaActual, $filtroArea, $filtroRol, $busqueda]) => {
				if (!$agentes || !Array.isArray($agentes)) return {};

				let agentesFiltrados = [...$agentes];

				if ($busqueda.trim()) {
					const termino = $busqueda.toLowerCase();
					agentesFiltrados = agentesFiltrados.filter(agente =>
						agente.nombre?.toLowerCase().includes(termino) ||
						agente.apellido?.toLowerCase().includes(termino) ||
						agente.legajo?.toLowerCase().includes(termino) ||
						agente.email?.toLowerCase().includes(termino)
					);
				}

				if ($filtroArea) {
					agentesFiltrados = agentesFiltrados.filter(agente =>
						agente.area_id === parseInt($filtroArea)
					);
				}

				if ($filtroRol) {
					agentesFiltrados = agentesFiltrados.filter(agente =>
						agente.roles && agente.roles.some(rol => rol.id === parseInt($filtroRol))
					);
				}

				switch ($vistaActual) {
					case 'areas':
						return this.organizarPorAreas(agentesFiltrados, $areas);
					case 'roles':
						return this.organizarPorRoles(agentesFiltrados, $roles);
					case 'jerarquica':
					default:
						return this.organizarJerarquicamente(agentesFiltrados, $areas, $roles);
				}
			}
		);

		this.agentesParaSelect = derived(this.agentes, ($agentes) => {
			if (!Array.isArray($agentes)) return [];
			return $agentes
				.filter(a => a.activo !== false)
				.map(a => ({
					id: a.id_agente || a.id,
					nombre_completo: `${a.apellido}, ${a.nombre}`,
					legajo: a.legajo || "",
					email: a.email || "",
					telefono: a.telefono || "",
					area_id: a.area_id || a.id_area || null,
				}))
				.sort((a, b) => a.nombre_completo.localeCompare(b.nombre_completo));
		});

		this.agenteById = derived(this.agentesParaSelect, ($list) => {
			const m = new Map();
			for (const a of $list) m.set(a.id, a);
			return m;
		});

		this.estadisticas = derived(
			[this.agentes, this.areas, this.roles],
			([$agentes, $areas, $roles]) => {
				if (!$agentes || !Array.isArray($agentes)) {
					return {
						totalAgentes: 0,
						totalAreas: 0,
						totalRoles: 0,
						agentesPorArea: {},
						agentesPorRol: {},
						sinRol: 0,
						sinArea: 0
					};
				}

				const agentesPorArea = {};
				const agentesPorRol = {};
				let sinRol = 0;
				let sinArea = 0;

				$agentes.forEach(agente => {
					if (agente.area_id) {
						const area = $areas.find(a => a.id_area === agente.area_id);
						const areaNombre = area ? area.nombre : `Área ${agente.area_id}`;
						agentesPorArea[areaNombre] = (agentesPorArea[areaNombre] || 0) + 1;
					} else {
						sinArea++;
					}

					if (agente.roles && agente.roles.length > 0) {
						agente.roles.forEach(rol => {
							agentesPorRol[rol.nombre] = (agentesPorRol[rol.nombre] || 0) + 1;
						});
					} else {
						sinRol++;
					}
				});

				return {
					totalAgentes: $agentes.length,
					totalAreas: $areas.length,
					totalRoles: $roles.length,
					agentesPorArea,
					agentesPorRol,
					sinRol,
					sinArea
				};
			}
		);
	}

	async init() {
		// Prevenir ejecución en SSR
		if (!browser) {
			return;
		}

		if (!AuthService.isAuthenticated()) {
			throw new Error('Usuario no autenticado');
		}

		await this.cargarDatos();
	}

	async cargarDatos() {
		try {
			this.loading.set(true);
			this.error.set(null);

			const [agentesResponse, areasResponse, rolesResponse] = await Promise.all([
				personasService.getAgentes(),
				personasService.getAreas(),
				personasService.getRoles()
			]);

			const normalize = r =>
				r?.data?.data?.results ||
				r?.data?.results ||
				r?.results ||
				r?.data ||
				[];

			const agentesData = normalize(agentesResponse);
			this.agentes.set(Array.isArray(agentesData) ? agentesData : []);

			const areasData = normalize(areasResponse);
			this.areas.set(Array.isArray(areasData) ? areasData : []);

			const rolesData = normalize(rolesResponse);
			this.roles.set(Array.isArray(rolesData) ? rolesData : []);

		} catch (error) {

			let errorMessage = 'Error al cargar datos del organigrama: ';
			if (error.response?.status === 401) {
				throw new Error('Sesión expirada');
			} else if (error.response?.status === 403) {
				errorMessage += 'No tienes permisos para acceder a esta información.';
			} else {
				errorMessage += (error.response?.data?.message || error.message);
			}

			this.error.set(errorMessage);
			throw error;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * Organizar agentes jerárquicamente
	 */
	organizarJerarquicamente(agentes, areas, roles) {
		const estructura = {
			tipo: 'jerarquica',
			nodos: [],
			relaciones: []
		};

		// Separar por roles jerárquicos
		const administradores = agentes.filter(a =>
			a.roles && a.roles.some(r => r.nombre.toLowerCase().includes('administrador'))
		);
		const jefes = agentes.filter(a =>
			a.roles && a.roles.some(r => r.nombre.toLowerCase().includes('jefe'))
		);
		const agentesComunes = agentes.filter(a =>
			!a.roles || !a.roles.some(r =>
				r.nombre.toLowerCase().includes('administrador') ||
				r.nombre.toLowerCase().includes('jefe')
			)
		);

		// Crear nodos jerárquicos
		estructura.nodos = [
			{
				nivel: 1,
				titulo: 'Administradores',
				agentes: administradores,
				color: '#e74c3c'
			},
			{
				nivel: 2,
				titulo: 'Jefes',
				agentes: jefes,
				color: '#f39c12'
			},
			{
				nivel: 3,
				titulo: 'Agentes',
				agentes: agentesComunes,
				color: '#3498db'
			}
		];

		return estructura;
	}

	/**
	 * Organizar agentes por áreas
	 */
	organizarPorAreas(agentes, areas) {
		const estructura = {
			tipo: 'areas',
			nodos: [],
			sinAsignar: []
		};

		const sinArea = agentes.filter(a => !a.area_id);
		estructura.sinAsignar = sinArea;

		areas.forEach(area => {
			const agentesDelArea = agentes.filter(a => a.area_id === area.id_area);
			if (agentesDelArea.length > 0) {
				estructura.nodos.push({
					area: area,
					agentes: agentesDelArea,
					total: agentesDelArea.length,
					color: this.getColorForArea(area.id_area)
				});
			}
		});

		// Ordenar por cantidad de agentes
		estructura.nodos.sort((a, b) => b.total - a.total);

		return estructura;
	}

	/**
	 * Organizar agentes por roles
	 */
	organizarPorRoles(agentes, roles) {
		const estructura = {
			tipo: 'roles',
			nodos: [],
			sinAsignar: []
		};

		const sinRol = agentes.filter(a => !a.roles || a.roles.length === 0);
		estructura.sinAsignar = sinRol;

		roles.forEach(rol => {
			const agentesDelRol = agentes.filter(a =>
				a.roles && a.roles.some(r => r.id === rol.id_rol || r.id === rol.id)
			);
			if (agentesDelRol.length > 0) {
				estructura.nodos.push({
					rol: rol,
					agentes: agentesDelRol,
					total: agentesDelRol.length,
					color: this.getColorForRol(rol.id_rol || rol.id)
				});
			}
		});

		// Ordenar por cantidad de agentes
		estructura.nodos.sort((a, b) => b.total - a.total);

		return estructura;
	}

	/**
	 * Obtener color para un área específica
	 */
	getColorForArea(areaId) {
		const colores = [
			'#3498db', '#e74c3c', '#2ecc71', '#f39c12',
			'#9b59b6', '#1abc9c', '#34495e', '#e67e22'
		];
		return colores[areaId % colores.length];
	}

	/**
	 * Obtener color para un rol específico
	 */
	getColorForRol(rolId) {
		const colores = [
			'#e74c3c', '#f39c12', '#3498db', '#2ecc71',
			'#9b59b6', '#1abc9c', '#34495e', '#e67e22'
		];
		return colores[rolId % colores.length];
	}

	/**
	 * Cambiar vista del organigrama
	 */
	cambiarVista(nuevaVista) {
		if (['jerarquica', 'areas', 'roles'].includes(nuevaVista)) {
			this.vistaActual.set(nuevaVista);
		}
	}

	/**
	 * Limpiar todos los filtros
	 */
	limpiarFiltros() {
		this.filtroArea.set('');
		this.filtroRol.set('');
		this.busqueda.set('');
	}


	/**
	 * Exportar organigrama (para futuras funcionalidades)
	 */
	async exportarOrganigrama(formato = 'json') {
		try {
			// Esta función se puede expandir para exportar a diferentes formatos
			const estructura = await new Promise((resolve) => {
				this.estructuraOrganizacional.subscribe(value => {
					resolve(value);
				})();
			});

			if (formato === 'json') {
				return JSON.stringify(estructura, null, 2);
			}

			// Agregar más formatos en el futuro (PDF, PNG, etc.)
			return estructura;
		} catch (error) {
			throw error;
		}
	}
}

// Exportar una instancia única (singleton)
export const organigramaController = new OrganigramaController();