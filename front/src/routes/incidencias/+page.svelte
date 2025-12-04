<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import AuthService from '$lib/login/authService.js';
  import { IncidenciasService } from '$lib/services/incidencias.js';

  let loading = true;
  let currentUser = null;
  let userRole = null;
  let incidencias = [];
  let misIncidencias = [];
  let incidenciasAsignadas = [];
  let error = null;
  let tabActiva = 'todas';
  let busqueda = '';
  let incluirCerradas = false;
  let incidenciasFiltradas = [];
  
  // Modal para ver detalles
  let showDetalleModal = false;
  let incidenciaSeleccionada = null;
  let cargandoDetalle = false;
  
  // Modal para cambiar estado
  let showCambiarEstadoModal = false;
  let cambiandoEstado = false;
  let nuevoEstado = '';
  let comentarioEstado = '';
  let estadosDisponibles = [
    { value: 'abierta', label: 'Abierta' },
    { value: 'en_proceso', label: 'En Proceso' },
    { value: 'pendiente_informacion', label: 'Información Pendiente' },
    { value: 'resuelta', label: 'Resuelta' },
    { value: 'cerrada', label: 'Cerrada' }
  ];
  
  // Modal para crear incidencia
  let showModal = false;
  let creandoIncidencia = false;
  
  // Modal para mensajes
  let showMensajeModal = false;
  let mensajeModal = { titulo: '', mensaje: '', tipo: 'success' };
  let jefesArea = [];
  let cargandoJefes = false;
  let nuevaIncidencia = {
    titulo: '',
    descripcion: '',
    prioridad: 'media',
    asignado_a_id: null
  };
  
  const incidenciasService = new IncidenciasService();

  onMount(async () => {
    try {
      // Verificar sesión
      const sessionCheck = await AuthService.checkSession();
      if (!sessionCheck.authenticated) {
        goto('/');
        return;
      }

      currentUser = sessionCheck.user;
      
      // Determinar si es agente (para simplicar lógica de UI)
      const esAgente = !currentUser?.roles?.some(r => 
        ['Administrador', 'Director', 'Jefe de Área', 'Jefatura'].includes(r.nombre)
      );
      userRole = esAgente ? 'Agente' : 'Supervisor';
      
      // Para agentes, mostrar primero sus incidencias
      if (esAgente) {
        tabActiva = 'mias';
      }

      await cargarDatos();

    } catch (error) {
      console.error('Error inicializando página:', error);
      error = error.message;
    } finally {
      loading = false;
    }
  });
  
  async function cargarDatos() {
    try {
      // Cargar datos en paralelo
      const promesas = [
        incidenciasService.obtenerIncidencias(),
        incidenciasService.obtenerMisIncidencias(),
        incidenciasService.obtenerIncidenciasAsignadas()
      ];
      
      const [todasIncidencias, misIncidenciasData, asignadasData] = await Promise.all(promesas);
      
      // Asignar datos recibidos
      incidencias = Array.isArray(todasIncidencias) ? todasIncidencias : [];
      misIncidencias = Array.isArray(misIncidenciasData) ? misIncidenciasData : [];
      incidenciasAsignadas = Array.isArray(asignadasData) ? asignadasData : [];
      
    } catch (err) {
      console.error('Error al cargar datos:', err);
      error = err.message;
    }
  }

  function cambiarTab(nuevaTab) {
    tabActiva = nuevaTab;
  }
  
  // Contadores reactivos que respetan el filtro de cerradas
  $: todasCount = incluirCerradas ? incidencias.length : incidencias.filter(inc => inc.estado !== 'cerrada').length;
  $: miasCount = incluirCerradas ? misIncidencias.length : misIncidencias.filter(inc => inc.estado !== 'cerrada').length;
  $: asignadasCount = incluirCerradas ? incidenciasAsignadas.length : incidenciasAsignadas.filter(inc => inc.estado !== 'cerrada').length;

  // Función reactiva para obtener incidencias según tab activa, búsqueda y filtro de cerradas
  $: incidenciasFiltradas = (() => {
    let incidenciasBase = [];
    
    switch(tabActiva) {
      case 'mias':
        incidenciasBase = misIncidencias || [];
        break;
      case 'asignadas':
        incidenciasBase = incidenciasAsignadas || [];
        break;
      default: // 'todas'
        incidenciasBase = incidencias || [];
    }
    
    // Filtrar incidencias cerradas si no están incluidas
    if (!incluirCerradas) {
      incidenciasBase = incidenciasBase.filter(incidencia => 
        incidencia && incidencia.estado !== 'cerrada'
      );
    }
    
    // Si no hay búsqueda, devolver incidencias base filtradas
    if (!busqueda || !busqueda.trim()) {
      return incidenciasBase;
    }
    
    // Aplicar filtro de búsqueda
    const busquedaLower = busqueda.toLowerCase().trim();
    return incidenciasBase.filter(incidencia => {
      if (!incidencia) return false;
      
      return (
        (incidencia.titulo && incidencia.titulo.toLowerCase().includes(busquedaLower)) ||
        (incidencia.descripcion && incidencia.descripcion.toLowerCase().includes(busquedaLower)) ||
        (incidencia.numero && incidencia.numero.toLowerCase().includes(busquedaLower)) ||
        (incidencia.creado_por_nombre && incidencia.creado_por_nombre.toLowerCase().includes(busquedaLower)) ||
        (incidencia.asignado_a_nombre && incidencia.asignado_a_nombre.toLowerCase().includes(busquedaLower))
      );
    });
  })();
  

  
  async function crearNuevaIncidencia() {
    showModal = true;
    await cargarJefesArea();
  }

  async function cargarJefesArea() {
    cargandoJefes = true;
    try {
      // Si es agente, buscar jefes de área. Si es jefe/director/admin, buscar agentes
      if (userRole === 'Agente') {
        const response = await incidenciasService.obtenerJefesArea();
        jefesArea = response.jefes || [];
      } else {
        // Para jefes, directores y admins: obtener agentes
        const response = await incidenciasService.obtenerAgentesArea();
        jefesArea = response.agentes || [];
      }
    } catch (error) {
      console.error('Error cargando destinatarios:', error);
      jefesArea = [];
    } finally {
      cargandoJefes = false;
    }
  }

  function cerrarModal() {
    showModal = false;
    nuevaIncidencia = {
      titulo: '',
      descripcion: '',
      prioridad: 'media',
      asignado_a_id: null
    };
    jefesArea = [];
  }



  async function guardarIncidencia() {
    if (!nuevaIncidencia.titulo.trim() || !nuevaIncidencia.descripcion.trim()) {
      alert('Por favor complete todos los campos obligatorios');
      return;
    }

    if (!nuevaIncidencia.asignado_a_id) {
      alert('Debe seleccionar un destinatario para asignar la incidencia');
      return;
    }

    creandoIncidencia = true;
    try {
      await incidenciasService.crearIncidencia(nuevaIncidencia);
      
      // Recargar datos
      await cargarDatos();
      
      // Cerrar modal y mostrar mensaje
      cerrarModal();
      mostrarMensaje('¡Éxito!', 'Incidencia creada exitosamente', 'success');
      
      // Cambiar a la tab de "mis incidencias" para mostrar la nueva
      tabActiva = 'mias';
      
    } catch (err) {
      console.error('Error al crear incidencia:', err);
      mostrarMensaje('Error', `No se pudo crear la incidencia: ${err.message}`, 'error');
    } finally {
      creandoIncidencia = false;
    }
  }

  // Funciones para modal de detalles
  async function verDetalles(incidencia) {
    cargandoDetalle = true;
    showDetalleModal = true;
    
    try {
      // Obtener detalles completos de la incidencia
      const detallesCompletos = await incidenciasService.obtenerIncidencia(incidencia.id);
      incidenciaSeleccionada = detallesCompletos;
    } catch (error) {
      console.error('Error cargando detalles:', error);
      incidenciaSeleccionada = incidencia; // Usar los datos que ya tenemos
    } finally {
      cargandoDetalle = false;
    }
  }

  function cerrarDetalleModal() {
    showDetalleModal = false;
    incidenciaSeleccionada = null;
  }

  function mostrarMensaje(titulo, mensaje, tipo = 'success') {
    mensajeModal = { titulo, mensaje, tipo };
    showMensajeModal = true;
  }

  function cerrarMensajeModal() {
    showMensajeModal = false;
  }
  
  function abrirCambiarEstadoModal() {
    showCambiarEstadoModal = true;
    nuevoEstado = incidenciaSeleccionada.estado || 'abierta';
    comentarioEstado = '';
  }
  
  function cerrarCambiarEstadoModal() {
    showCambiarEstadoModal = false;
    nuevoEstado = '';
    comentarioEstado = '';
  }
  
  async function guardarCambioEstado() {
    if (!nuevoEstado) {
      alert('Debe seleccionar un nuevo estado');
      return;
    }
    
    if (nuevoEstado === incidenciaSeleccionada.estado) {
      alert('Debe seleccionar un estado diferente al actual');
      return;
    }
    
    cambiandoEstado = true;
    try {
      // Cambiar estado
      const incidenciaActualizada = await incidenciasService.cambiarEstado(
        incidenciaSeleccionada.id, 
        nuevoEstado, 
        comentarioEstado
      );
      
      // Actualizar la incidencia seleccionada
      incidenciaSeleccionada = incidenciaActualizada;
      
      // Recargar datos
      await cargarDatos();
      
      // Cerrar modal y mostrar mensaje
      cerrarCambiarEstadoModal();
      mostrarMensaje(
        '¡Estado actualizado!', 
        `El estado de la incidencia ha sido cambiado exitosamente.`, 
        'success'
      );
      
    } catch (err) {
      console.error('Error al cambiar estado:', err);
      mostrarMensaje('Error', `No se pudo cambiar el estado: ${err.message}`, 'error');
    } finally {
      cambiandoEstado = false;
    }
  }
</script>

<svelte:head>
  <title>Incidencias - GIGA</title>
</svelte:head>

<div class="incidencias-container">
  {#if loading}
    <div class="loading-container">
      <div class="spinner"></div>
      <p>Cargando incidencias...</p>
    </div>
  {:else}
    <!-- Header elegante -->
    <div class="header">
      <h1>Incidencias</h1>
    </div>

    <!-- Contenido principal -->
    <div class="content">
      {#if error}
        <div class="error-banner">
          <p><strong>Error:</strong> {error}</p>
          <button on:click={() => window.location.reload()}>Reintentar</button>
        </div>
      {:else}


        <!-- Navegación por tabs y búsqueda -->
        <div class="tabs-container">
          <div class="tabs">
            <button 
              class="tab {tabActiva === 'todas' ? 'active' : ''}"
              on:click={() => cambiarTab('todas')}
            >
              Todas las Incidencias ({todasCount})
            </button>
            <button 
              class="tab {tabActiva === 'mias' ? 'active' : ''}"
              on:click={() => cambiarTab('mias')}
            >
              Mis Incidencias ({miasCount})
            </button>
            <button 
              class="tab {tabActiva === 'asignadas' ? 'active' : ''}"
              on:click={() => cambiarTab('asignadas')}
            >
              Asignadas a Mí ({asignadasCount})
            </button>
          </div>
          
          <div class="controls">
            <div class="search-container">
              <input
                type="text"
                placeholder="Buscar incidencias..."
                bind:value={busqueda}
                class="search-input"
              />
              <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M21.71 20.29l-3.4-3.4A9 9 0 1 0 16 18l3.4 3.4a1 1 0 0 0 1.42 0 1 1 0 0 0-.11-1.41zM11 18a7 7 0 1 1 7-7 7 7 0 0 1-7 7z"/>
              </svg>
            </div>
            
            <div class="filter-container">
              <label class="checkbox-container">
                <input
                  type="checkbox"
                  bind:checked={incluirCerradas}
                  class="checkbox-input"
                />
                <span class="checkbox-label">Incluir cerradas</span>
              </label>
            </div>
            
            <button class="btn-crear" on:click={crearNuevaIncidencia}>
              + {userRole === 'Agente' ? 'Contactar Jefatura' : 'Contactar Agente'}
            </button>
          </div>
        </div>

        <!-- Lista de incidencias -->
        <div class="incidencias-list">
          {#each incidenciasFiltradas as incidencia (incidencia?.id || incidencia?.numero || Math.random())}
            <div class="incidencia-card">
              <div class="incidencia-header">
                <div class="incidencia-numero">{incidencia.numero}</div>
                <div class="incidencia-badges">
                  {#if incidencia.estado}
                    <span class="badge badge-{incidencia.estado}">
                      {incidencia.estado_display || incidencia.estado}
                    </span>
                  {:else if incidencia.fecha_resolucion}
                    <span class="badge badge-resuelto">
                      Resuelta
                    </span>
                  {:else}
                    <span class="badge badge-pendiente">
                      Pendiente
                    </span>
                  {/if}
                  {#if incidencia.prioridad}
                    <span class="badge badge-prioridad-{incidencia.prioridad}">
                      {incidencia.prioridad_display || incidencia.prioridad}
                    </span>
                  {/if}
                </div>
              </div>
              
              <h3 class="incidencia-titulo">{incidencia.titulo}</h3>
              <p class="incidencia-descripcion">{incidencia.descripcion}</p>
              
              <div class="incidencia-footer">
                <div class="incidencia-meta">
                  <div class="meta-item">
                    <strong>Creada por:</strong> {incidencia.creado_por_nombre}
                  </div>
                  <div class="meta-item">
                    <strong>Fecha:</strong> {IncidenciasService.formatearFecha(incidencia.fecha_creacion)}
                  </div>
                  {#if incidencia.asignado_a_nombre}
                    <div class="meta-item">
                      <strong>Asignada a:</strong> {incidencia.asignado_a_nombre}
                    </div>
                  {/if}
                  {#if incidencia.area_nombre}
                    <div class="meta-item">
                      <strong>Área:</strong> {incidencia.area_nombre}
                    </div>
                  {/if}
                </div>
                
                <div class="incidencia-actions">
                  <button class="btn-secondary" on:click={() => verDetalles(incidencia)}>
                    Ver Detalles
                  </button>
                </div>
              </div>
            </div>
          {:else}
            <div class="empty-state">
              <h3>No hay incidencias</h3>
              <p>
                {#if busqueda.trim()}
                  No se encontraron incidencias que coincidan con "{busqueda}".
                {:else}
                  No se encontraron incidencias en esta categoría.
                {/if}
              </p>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<!-- Modal para crear nueva incidencia -->
{#if showModal}
  <div class="modal-overlay" on:click={cerrarModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Nueva Incidencia</h2>
        <button class="close-btn" on:click={cerrarModal}>×</button>
      </div>
      
      <form on:submit|preventDefault={guardarIncidencia}>
        <div class="form-group">
          <label for="titulo">Título *</label>
          <input
            id="titulo"
            type="text"
            bind:value={nuevaIncidencia.titulo}
            placeholder="Título de la incidencia"
            required
            disabled={creandoIncidencia}
          />
        </div>

        <div class="form-group">
          <label for="descripcion">Descripción *</label>
          <textarea
            id="descripcion"
            bind:value={nuevaIncidencia.descripcion}
            placeholder="Describe detalladamente la incidencia"
            rows="4"
            required
            disabled={creandoIncidencia}
          ></textarea>
        </div>

        <div class="form-group">
          <label for="prioridad">Prioridad *</label>
          <select
            id="prioridad"
            bind:value={nuevaIncidencia.prioridad}
            disabled={creandoIncidencia}
            required
          >
            <option value="baja">Baja</option>
            <option value="media">Media</option>
            <option value="alta">Alta</option>
            <option value="critica">Crítica</option>
          </select>
        </div>

        <!-- Selector de jefe -->
        <div class="form-group">
          <label for="asignado_a">{userRole === 'Agente' ? 'Asignar a Jefatura *' : 'Asignar a Agente *'}</label>
          {#if cargandoJefes}
            <div class="loading-jefes">Cargando {userRole === 'Agente' ? 'jefes' : 'agentes'}...</div>
          {:else if jefesArea.length > 0}
            <select
              id="asignado_a"
              bind:value={nuevaIncidencia.asignado_a_id}
              disabled={creandoIncidencia}
              required
            >
              <option value={null}>Seleccione {userRole === 'Agente' ? 'un jefe' : 'un agente'}</option>
              {#each jefesArea as jefe}
                <option value={jefe.id}>{jefe.nombre} ({jefe.rol})</option>
              {/each}
            </select>
          {:else}
            <div class="no-jefes">No hay {userRole === 'Agente' ? 'jefes' : 'agentes'} disponibles en su área</div>
          {/if}
        </div>

        <div class="modal-actions">
          <button
            type="button"
            class="btn-cancel"
            on:click={cerrarModal}
            disabled={creandoIncidencia}
          >
            Cancelar
          </button>
          <button
            type="submit"
            class="btn-save"
            disabled={creandoIncidencia}
          >
            {creandoIncidencia ? 'Creando...' : 'Crear Incidencia'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Modal para ver detalles de incidencia -->
{#if showDetalleModal && incidenciaSeleccionada}
  <div class="modal-overlay" on:click={cerrarDetalleModal}>
    <div class="modal modal-detalle" on:click|stopPropagation>
      <div class="modal-header">
        <div class="detalle-header">
          <h2>Detalle de Incidencia</h2>
          <div class="incidencia-badges">
            {#if incidenciaSeleccionada.fecha_resolucion}
              <span class="badge badge-resuelto">
                Resuelta
              </span>
            {:else}
              <span class="badge badge-pendiente">
                Pendiente
              </span>
            {/if}
          </div>
        </div>
        <button class="close-btn" on:click={cerrarDetalleModal}>×</button>
      </div>
      
      {#if cargandoDetalle}
        <div class="loading-container">
          <div class="spinner"></div>
          <p>Cargando detalles...</p>
        </div>
      {:else}
        <div class="detalle-content">
          <!-- Información principal -->
          <div class="detalle-section">
            <div class="detalle-numero">#{incidenciaSeleccionada.numero}</div>
            <h3 class="detalle-titulo">{incidenciaSeleccionada.titulo}</h3>
          </div>

          <!-- Descripción -->
          <div class="detalle-section">
            <h4>Descripción</h4>
            <div class="detalle-descripcion">
              {incidenciaSeleccionada.descripcion}
            </div>
          </div>

          <!-- Estado y prioridad -->
          {#if incidenciaSeleccionada.estado || incidenciaSeleccionada.prioridad}
            <div class="detalle-section">
              <h4>Estado y Prioridad</h4>
              <div class="estado-prioridad-container">
                {#if incidenciaSeleccionada.estado}
                  <div class="estado-actual">
                    <strong>Estado:</strong>
                    <span class="badge badge-{incidenciaSeleccionada.estado}">
                      {incidenciaSeleccionada.estado_display || incidenciaSeleccionada.estado}
                    </span>
                  </div>
                {/if}
                {#if incidenciaSeleccionada.prioridad}
                  <div class="prioridad-actual">
                    <strong>Prioridad:</strong>
                    <span class="badge badge-prioridad-{incidenciaSeleccionada.prioridad}">
                      {incidenciaSeleccionada.prioridad_display || incidenciaSeleccionada.prioridad}
                    </span>
                  </div>
                {/if}
                {#if incidenciaSeleccionada.puede_cambiar_estado}
                  <button class="btn-cambiar-estado" on:click={abrirCambiarEstadoModal}>
                    Cambiar Estado
                  </button>
                {/if}
              </div>
            </div>
          {/if}

          <!-- Información de gestión -->
          <div class="detalle-grid">
            <div class="detalle-item">
              <strong>Creada por:</strong>
              <span>{incidenciaSeleccionada.creado_por_nombre || 'No especificado'}</span>
            </div>
            
            <div class="detalle-item">
              <strong>Fecha de creación:</strong>
              <span>{IncidenciasService.formatearFecha(incidenciaSeleccionada.fecha_creacion)}</span>
            </div>

            {#if incidenciaSeleccionada.asignado_a_nombre}
              <div class="detalle-item">
                <strong>Asignada a:</strong>
                <span>{incidenciaSeleccionada.asignado_a_nombre}</span>
              </div>
            {/if}

            {#if incidenciaSeleccionada.fecha_asignacion}
              <div class="detalle-item">
                <strong>Fecha de asignación:</strong>
                <span>{IncidenciasService.formatearFecha(incidenciaSeleccionada.fecha_asignacion)}</span>
              </div>
            {/if}

            {#if incidenciaSeleccionada.area_nombre}
              <div class="detalle-item">
                <strong>Área involucrada:</strong>
                <span>{incidenciaSeleccionada.area_nombre}</span>
              </div>
            {/if}

            {#if incidenciaSeleccionada.fecha_resolucion}
              <div class="detalle-item">
                <strong>Fecha de resolución:</strong>
                <span>{IncidenciasService.formatearFecha(incidenciaSeleccionada.fecha_resolucion)}</span>
              </div>
            {/if}
          </div>

          <!-- Resolución (si existe) -->
          {#if incidenciaSeleccionada.resolucion}
            <div class="detalle-section">
              <h4>Resolución</h4>
              <div class="detalle-resolucion">
                {incidenciaSeleccionada.resolucion}
              </div>
            </div>
          {/if}

          <!-- Comentarios de seguimiento (si existen) -->
          {#if incidenciaSeleccionada.comentarios_seguimiento && incidenciaSeleccionada.comentarios_seguimiento.length > 0}
            <div class="detalle-section comentarios-section">
              <h4>Comentarios de Seguimiento</h4>
              <div class="comentarios-lista">
                {#each incidenciaSeleccionada.comentarios_seguimiento as comentario}
                  <div class="comentario-item">
                    <div class="comentario-meta">
                      <strong>{comentario.autor || 'Usuario'}</strong>
                      <span class="comentario-fecha">{IncidenciasService.formatearFecha(comentario.fecha)}</span>
                    </div>
                    <div class="comentario-texto">{comentario.comentario}</div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
{/if}

<!-- Modal de Mensajes -->
{#if showMensajeModal}
  <div class="modal-overlay" on:click={cerrarMensajeModal}>
    <div class="modal-content mensaje-modal" on:click|stopPropagation>
      <div class="mensaje-header {mensajeModal.tipo}">
        <div class="mensaje-icono">
          {#if mensajeModal.tipo === 'success'}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          {:else if mensajeModal.tipo === 'error'}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          {/if}
        </div>
        <h3>{mensajeModal.titulo}</h3>
      </div>
      
      <div class="mensaje-contenido">
        <p>{mensajeModal.mensaje}</p>
      </div>
      
      <div class="mensaje-acciones">
        <button class="btn-mensaje" on:click={cerrarMensajeModal}>
          Aceptar
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Modal para cambiar estado -->
{#if showCambiarEstadoModal && incidenciaSeleccionada}
  <div class="modal-overlay" on:click={cerrarCambiarEstadoModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Cambiar Estado - {incidenciaSeleccionada.numero}</h2>
        <button class="close-btn" on:click={cerrarCambiarEstadoModal}>×</button>
      </div>
      
      <form on:submit|preventDefault={guardarCambioEstado}>
        <div class="cambiar-estado-content">
          <div class="estado-actual-info">
            <p><strong>Estado actual:</strong> 
              <span class="badge badge-{incidenciaSeleccionada.estado}">
                {incidenciaSeleccionada.estado_display || incidenciaSeleccionada.estado}
              </span>
            </p>
          </div>
          
          <div class="form-group">
            <label for="nuevo-estado">Nuevo Estado *</label>
            <select
              id="nuevo-estado"
              bind:value={nuevoEstado}
              disabled={cambiandoEstado}
              required
            >
              {#each estadosDisponibles as estado}
                <option value={estado.value}>{estado.label}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="comentario-estado">Comentario (opcional)</label>
            <textarea
              id="comentario-estado"
              bind:value={comentarioEstado}
              placeholder="Agregue un comentario sobre el cambio de estado..."
              rows="3"
              disabled={cambiandoEstado}
            ></textarea>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn-cancel"
              on:click={cerrarCambiarEstadoModal}
              disabled={cambiandoEstado}
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="btn-save"
              disabled={cambiandoEstado || nuevoEstado === incidenciaSeleccionada.estado}
            >
              {cambiandoEstado ? 'Cambiando...' : 'Cambiar Estado'}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .incidencias-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem 2rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f4f6;
    border-top: 4px solid #3B82F6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Header elegante - igual al que te gustó */
  .header {
    position: relative;
    background: linear-gradient(135deg, #1e40afc7 0%, #3b83f6d3 100%);
    color: white;
    padding: 30px 40px;
    max-width: 1200px;
    border-radius: 28px;
    overflow: hidden;
    text-align: center;
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.1) inset,
      0 10px 30px rgba(30, 64, 175, 0.4);
    margin-bottom: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .header::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.03) 1px,
        transparent 1px
      ),
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: moveLines 20s linear infinite;
  }

  .header h1 {
    margin: 10px;
    font-weight: 800;
    font-size: 35px;
    letter-spacing: 0.2px;
    position: relative;
    padding-bottom: 12px;
    overflow: hidden;
    display: inline-block;
  }

  .header h1::after {
    content: "";
    position: absolute;
    width: 40%;
    height: 3px;
    bottom: 0;
    left: 0;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.9),
      transparent
    );
    animation: slideRight 3s ease-in-out infinite;
  }

  .header-subtitle {
    margin: 0.25rem 0 0 0;
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9rem;
    position: relative;
    z-index: 1;
  }

  .content {
    padding: 2rem 0;
  }

  .error-banner {
    background: #fee2e2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .error-banner button {
    background: #dc2626;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }



  /* Navegación por tabs y controles */
  .tabs-container {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 2rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 1rem;
  }
  
  .tabs {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .controls {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .tab {
    background: none;
    border: none;
    padding: 0.75rem 1rem;
    cursor: pointer;
    border-radius: 8px;
    color: #6b7280;
    font-weight: 500;
    transition: all 0.2s;
  }

  .tab:hover {
    background: #f3f4f6;
    color: #374151;
  }

  .tab.active {
    background: #3b82f6;
    color: white;
  }

  .search-container {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-input {
    padding: 0.75rem 2.5rem 0.75rem 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.875rem;
    width: 300px;
    transition: border-color 0.2s;
    background: white;
  }

  .search-input:focus {
    outline: none;
    border-color: #3b82f6;
  }

  .search-input::placeholder {
    color: #9ca3af;
  }

  .search-icon {
    position: absolute;
    right: 0.75rem;
    width: 18px;
    height: 18px;
    fill: #9ca3af;
    pointer-events: none;
  }

  .filter-container {
    display: flex;
    align-items: center;
    margin-left: 1rem;
  }

  .checkbox-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    user-select: none;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .checkbox-input {
    appearance: none;
    width: 18px;
    height: 18px;
    border: 2px solid #d1d5db;
    border-radius: 4px;
    background: white;
    margin-right: 0.5rem;
    cursor: pointer;
    position: relative;
    transition: all 0.2s;
  }

  .checkbox-input:checked {
    background: #3b82f6;
    border-color: #3b82f6;
  }

  .checkbox-input:checked::before {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
  }

  .checkbox-input:hover {
    border-color: #9ca3af;
  }

  .checkbox-input:checked:hover {
    background: #2563eb;
    border-color: #2563eb;
  }

  .checkbox-label {
    font-size: 0.875rem;
    color: #374151;
    font-weight: 500;
  }

  .btn-crear {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    font-family: inherit;
    font-size: 0.875rem;
  }

  .btn-crear:hover {
    background: #059669;
  }

  /* Lista de incidencias */
  .incidencias-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .incidencia-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s;
  }

  .incidencia-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .incidencia-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .incidencia-numero {
    font-family: monospace;
    font-weight: bold;
    color: #6b7280;
    font-size: 0.875rem;
  }

  .incidencia-badges {
    display: flex;
    gap: 0.5rem;
  }

  .badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .badge-resuelto { background: #d1fae5; color: #065f46; }
  .badge-pendiente { background: #fef3c7; color: #92400e; }
  
  /* Estados específicos */
  .badge-abierta { background: #dbeafe; color: #1e40af; }
  .badge-en_proceso { background: #fef3c7; color: #92400e; }
  .badge-pendiente_informacion { background: #fde68a; color: #b45309; }
  .badge-resuelta { background: #d1fae5; color: #065f46; }
  .badge-cerrada { background: #e5e7eb; color: #374151; }
  
  /* Prioridades */
  .badge-prioridad-baja { background: #ecfdf5; color: #059669; }
  .badge-prioridad-media { background: #fef3c7; color: #d97706; }
  .badge-prioridad-alta { background: #fecaca; color: #dc2626; }
  .badge-prioridad-critica { background: #7c2d12; color: white; }

  .incidencia-titulo {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
  }

  .incidencia-descripcion {
    color: #6b7280;
    margin-bottom: 1rem;
    line-height: 1.5;
  }

  .incidencia-footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
  }

  .incidencia-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    flex: 1;
  }

  .meta-item {
    font-size: 0.875rem;
    color: #6b7280;
  }

  .meta-item strong {
    color: #374151;
  }

  .incidencia-actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-secondary {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
  }

  .btn-secondary:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #6b7280;
  }

  .empty-state h3 {
    margin-bottom: 0.5rem;
    color: #374151;
  }

  /* Animaciones */
  @keyframes moveLines {
    0% {
      transform: translate(0, 0);
    }
    100% {
      transform: translate(50px, 50px);
    }
  }

  @keyframes slideRight {
    0% {
      left: -40%;
    }
    50% {
      left: 60%;
    }
    100% {
      left: -40%;
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .tabs-container {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }

    .controls {
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .search-container {
      flex: 1;
      min-width: 200px;
    }

    .search-input {
      width: 100%;
    }

    .filter-container {
      margin-left: 0;
      margin-top: 0.5rem;
    }

    .tabs {
      flex-wrap: wrap;
    }

    .tab {
      font-size: 0.75rem;
      padding: 0.5rem 0.75rem;
    }
  }

  /* Modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
    overflow-y: auto;
    padding: 1rem 0;
  }

  .modal {
    background: white;
    border-radius: 16px;
    padding: 0;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    animation: modalAppear 0.3s ease-out;
  }

  @keyframes modalAppear {
    from {
      opacity: 0;
      transform: scale(0.9) translateY(-20px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
  }

  .modal-header h2 {
    margin: 0;
    color: #374151;
    font-size: 1.25rem;
    font-weight: 500;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6b7280;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }

  .close-btn:hover {
    background: #e5e7eb;
    color: #374151;
  }

  .modal form {
    padding: 2rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 400;
    color: #4b5563;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 0.875rem;
  }

  .form-group input,
  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 0.875rem;
    transition: border-color 0.2s;
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 400;
    color: #4b5563;
  }

  .form-group input:focus,
  .form-group textarea:focus,
  .form-group select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }



  .form-group textarea {
    resize: vertical;
    min-height: 100px;
  }

  .modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
  }

  .btn-cancel,
  .btn-save {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 0.875rem;
  }

  .btn-cancel {
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
  }

  .btn-cancel:hover:not(:disabled) {
    background: #e5e7eb;
  }

  .btn-save {
    background: #3b82f6;
    color: white;
  }

  .btn-save:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn-cancel:disabled,
  .btn-save:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .loading-jefes {
    padding: 0.75rem;
    text-align: center;
    color: #6b7280;
    font-style: italic;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    background: #f9fafb;
  }

  /* Estilos específicos para modal de detalles */
  .modal-detalle {
    max-width: 900px;
    max-height: 98vh;
    height: auto;
    width: 95vw;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    flex-direction: column;
  }

  .detalle-header {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .detalle-header h2 {
    margin: 0;
  }

  .detalle-content {
    padding: 1.25rem;
    overflow-y: auto;
    flex: 1;
    max-height: calc(98vh - 80px);
    min-height: 500px;
  }

  .detalle-section {
    margin-bottom: 2rem;
  }

  .detalle-section:last-child {
    margin-bottom: 0;
  }

  .detalle-numero {
    font-size: 0.9rem;
    color: #6b7280;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }

  .detalle-titulo {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 1rem 0;
    line-height: 1.3;
  }

  .detalle-section h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 0.75rem 0;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .detalle-descripcion,
  .detalle-resolucion {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.25rem;
    line-height: 1.7;
    color: #374151;
    white-space: pre-wrap;
    word-wrap: break-word;
    min-height: 60px;
  }

  .detalle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .detalle-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 6px;
    border-left: 3px solid #3b82f6;
  }

  .detalle-item strong {
    font-size: 0.875rem;
    font-weight: 600;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .detalle-item span {
    font-size: 1rem;
    color: #1f2937;
    font-weight: 500;
  }

  .comentarios-section {
    border-top: 2px solid #e5e7eb;
    padding-top: 2rem;
    margin-top: 2rem;
  }

  .comentarios-lista {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .comentario-item {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 1.25rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .comentario-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .comentario-meta strong {
    color: #374151;
    font-weight: 500;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .comentario-fecha {
    font-size: 0.875rem;
    color: #6b7280;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 400;
  }

  .comentario-texto {
    color: #4b5563;
    line-height: 1.6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 400;
  }

  /* Estilos para estado y prioridad */
  .estado-prioridad-container {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }

  .estado-actual,
  .prioridad-actual {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .estado-actual strong,
  .prioridad-actual strong {
    font-size: 0.875rem;
    color: #374151;
  }

  .btn-cambiar-estado {
    background: #3b82f6;
    color: white;
    border: 1px solid #3b82f6;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    margin-left: auto;
    font-family: inherit;
  }

  .btn-cambiar-estado:hover {
    background: #2563eb;
    border-color: #2563eb;
  }

  /* Estilos para modal de cambio de estado */
  .cambiar-estado-content {
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .estado-actual-info {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .estado-actual-info p {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.95rem;
    font-weight: 400;
    font-family: -apple-system, BlinkMacSystemFont, "Segue UI", Roboto, sans-serif;
  }

  .estado-actual-info strong {
    font-weight: 500;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  /* Estilos para modal de mensajes */
  .mensaje-modal {
    max-width: 450px;
    width: 90%;
    background: white;
    border-radius: 16px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    overflow: hidden;
    animation: slideIn 0.3s ease-out;
  }

  .mensaje-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .mensaje-header.success {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    border-bottom: none;
  }

  .mensaje-header.error {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
    border-bottom: none;
  }

  .mensaje-icono {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
  }

  .mensaje-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 500;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .mensaje-contenido {
    padding: 1.5rem;
  }

  .mensaje-contenido p {
    margin: 0;
    font-size: 1rem;
    line-height: 1.6;
    color: #4b5563;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 400;
  }

  .mensaje-acciones {
    display: flex;
    justify-content: flex-end;
    padding: 1rem 1.5rem 1.5rem;
  }

  .btn-mensaje {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 1rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .btn-mensaje:hover {
    background: #2563eb;
  }

  .btn-mensaje:active {
    transform: translateY(0);
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: scale(0.9) translateY(-20px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  /* Responsive para modal de detalles */
  @media (max-width: 768px) {
    .modal-detalle {
      width: 98vw;
      max-width: none;
      max-height: 98vh;
      margin: 0.25rem;
    }

    .detalle-content {
      padding: 0.75rem;
      max-height: calc(98vh - 70px);
      min-height: 300px;
    }

    .detalle-grid {
      grid-template-columns: 1fr;
    }

    .detalle-header {
      flex-direction: column;
      align-items: flex-start;
    }

    .detalle-descripcion,
    .detalle-resolucion {
      padding: 1rem;
      font-size: 0.95rem;
    }

    .mensaje-modal {
      width: 95%;
      margin: 1rem;
    }

    .mensaje-contenido,
    .mensaje-acciones {
      padding: 1rem;
    }
  }
</style>