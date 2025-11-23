<script>
  import { guardiasService, personasService } from "$lib/services.js";
  import { onMount } from "svelte";

  // Estado del componente
  let compensaciones = [];
  let cargando = false;
  let error = null;
  let mostrandoFormulario = false;
  let token = null;

  // Debug: verificar que el script se esté ejecutando
  console.log("Script de compensaciones inicializado");

  // Datos para nueva compensación
  let nuevaCompensacion = {
    id_guardia: "",
    hora_fin_real: "",
    motivo: "emergencia",
    descripcion_motivo: "",
    numero_acta: "",
    solicitado_por: "",
  };

  // Datos para los filtros del formulario
  let areas = [];
  let agentes = [];
  let guardias = [];
  let areaSeleccionada = "";
  let agenteSeleccionado = "";
  let guardiaSeleccionada = "";
  let cargandoAreas = false;
  let cargandoAgentes = false;
  let cargandoGuardias = false;

  // Filtros para la lista de compensaciones
  let filtroAreaLista = "";
  let filtroEstadoLista = "";

  // Modal de detalles
  let mostrandoDetalles = false;
  let compensacionSeleccionada = null;

  // Opciones para el formulario
  const motivosCompensacion = [
    { value: "siniestro", label: "Siniestro/Accidente" },
    { value: "emergencia", label: "Emergencia Operativa" },
    { value: "operativo", label: "Operativo Especial" },
    { value: "refuerzo", label: "Refuerzo de Seguridad" },
    { value: "otro", label: "Otro Motivo" },
  ];

  onMount(async () => {
    console.log("Componente compensaciones montado, iniciando carga...");
    // Obtener token de sesión
    token = localStorage.getItem("token");

    try {
      await cargarCompensaciones();
      await cargarAreas();
      console.log("Carga inicial completada");
    } catch (err) {
      console.error("Error en carga inicial:", err);
    }
  });

  async function cargarCompensaciones() {
    cargando = true;
    error = null;
    try {
      const response = await guardiasService.getCompensaciones("", token);
      console.log("Respuesta completa compensaciones:", response);

      // Manejar diferentes estructuras de respuesta (incluyendo response.data.data.results)
      let datos = [];
      if (response.data?.data?.results) {
        datos = response.data.data.results;
      } else if (response.data?.results) {
        datos = response.data.results;
      } else if (response.success && response.data && response.data.results) {
        datos = response.data.results;
      } else if (response.results) {
        datos = response.results;
      } else if (Array.isArray(response.data)) {
        datos = response.data;
      } else if (Array.isArray(response)) {
        datos = response;
      } else {
        datos = [];
      }

      compensaciones = datos;
      console.log("Compensaciones cargadas:", compensaciones);
    } catch (err) {
      console.error("Error cargando compensaciones:", err);
      error =
        "Error al cargar compensaciones: " +
        (err.response?.data?.message || err.message || "Error desconocido");
      compensaciones = [];
    } finally {
      cargando = false;
    }
  }

  async function cargarAreas() {
    cargandoAreas = true;
    try {
      const response = await personasService.getAreas(token);
      console.log("Respuesta completa de áreas:", response);

      // Manejar diferentes estructuras de respuesta (incluyendo response.data.data.results)
      let datos = [];
      if (response.data?.data?.results) {
        datos = response.data.data.results;
      } else if (response.data?.results) {
        datos = response.data.results;
      } else if (response.success && response.data && response.data.results) {
        datos = response.data.results;
      } else if (response.results) {
        datos = response.results;
      } else if (Array.isArray(response.data)) {
        datos = response.data;
      } else if (Array.isArray(response)) {
        datos = response;
      } else {
        console.log('📊 Estructura inesperada de respuesta áreas compensaciones:', response);
        datos = [];
      }

      areas = datos;
      console.log("✅ Áreas procesadas en compensaciones:", areas.length);
      console.log("📋 Primeras 3 áreas:", areas.slice(0, 3));

      console.log("Áreas procesadas:", areas);
    } catch (err) {
      console.error("Error cargando áreas:", err);
      areas = [];
    } finally {
      cargandoAreas = false;
    }
  }

  async function cargarAgentes() {
    if (!areaSeleccionada) {
      agentes = [];
      return;
    }

    cargandoAgentes = true;
    try {
      const response = await personasService.getAgentesByArea(
        areaSeleccionada,
        token,
      );
      console.log("Respuesta completa de agentes:", response);

      // Manejar diferentes estructuras de respuesta (incluyendo response.data.data.results)
      let datos = [];
      if (response.data?.data?.results) {
        datos = response.data.data.results;
      } else if (response.data?.results) {
        datos = response.data.results;
      } else if (response.success && response.data && response.data.results) {
        datos = response.data.results;
      } else if (response.results) {
        datos = response.results;
      } else if (Array.isArray(response.data)) {
        datos = response.data;
      } else if (Array.isArray(response)) {
        datos = response;
      } else {
        datos = [];
      }

      agentes = datos;
      console.log("Agentes procesados:", agentes);
      // Limpiar selección de agente cuando cambia el área
      agenteSeleccionado = "";
      guardias = [];
      guardiaSeleccionada = "";
    } catch (err) {
      console.error("Error cargando agentes:", err);
      agentes = [];
    } finally {
      cargandoAgentes = false;
    }
  }

  async function cargarGuardias() {
    if (!agenteSeleccionado) {
      guardias = [];
      return;
    }

    cargandoGuardias = true;
    try {
      // Cargar guardias del agente - últimas guardias realizadas
      const response = await guardiasService.getGuardiasAgente(
        agenteSeleccionado,
        token,
      );
      console.log("Respuesta completa de guardias:", response);

      // Manejar diferentes estructuras de respuesta (incluyendo response.data.data.results)
      let datos = [];
      if (response.guardias && Array.isArray(response.guardias)) {
        datos = response.guardias;
      } else if (response.data?.data?.guardias) {
        datos = response.data.data.guardias;
      } else if (response.data?.data?.results) {
        datos = response.data.data.results;
      } else if (response.data?.guardias) {
        datos = response.data.guardias;
      } else if (response.data?.results) {
        datos = response.data.results;
      } else if (response.success && response.data && response.data.guardias) {
        datos = response.data.guardias;
      } else if (response.success && response.data && response.data.results) {
        datos = response.data.results;
      } else if (response.results) {
        datos = response.results;
      } else if (Array.isArray(response.data)) {
        datos = response.data;
      } else if (Array.isArray(response)) {
        datos = response;
      } else {
        datos = [];
      }

      guardias = datos;
      console.log("Guardias procesadas:", guardias);
      console.log("Total guardias encontradas:", guardias.length);
      
      // Filtrar guardias que ya tienen compensación
      await filtrarGuardiasConCompensacion();
      
      // Limpiar selección de guardia cuando cambia el agente
      guardiaSeleccionada = "";
    } catch (err) {
      console.error("Error cargando guardias:", err);
      guardias = [];
    } finally {
      cargandoGuardias = false;
    }
  }

  async function filtrarGuardiasConCompensacion() {
    if (guardias.length === 0) return;
    
    try {
      // Verificar cuáles guardias ya tienen compensación
      const guardiasIds = guardias.map(g => g.id_guardia);
      console.log('🔍 Verificando compensaciones para guardias:', guardiasIds);
      
      // Cargar todas las compensaciones para verificar cuáles guardias ya las tienen
      const compensacionesResponse = await guardiasService.getCompensaciones('', token);
      console.log('📝 Respuesta completa compensaciones para filtro:', compensacionesResponse);
      
      // Extraer los datos correctamente según la estructura de respuesta
      let todasCompensaciones = [];
      if (compensacionesResponse.data?.data?.results) {
        todasCompensaciones = compensacionesResponse.data.data.results;
      } else if (compensacionesResponse.data?.results) {
        todasCompensaciones = compensacionesResponse.data.results;
      } else if (Array.isArray(compensacionesResponse.data)) {
        todasCompensaciones = compensacionesResponse.data;
      }
      
      console.log('📋 Compensaciones extraídas:', todasCompensaciones);
      
      // Verificar que sea un array antes de hacer map
      if (!Array.isArray(todasCompensaciones)) {
        console.warn('⚠️ todasCompensaciones no es un array:', typeof todasCompensaciones, todasCompensaciones);
        return; // Salir si no es un array válido
      }
      
      // Extraer IDs de guardias que ya tienen compensación
      const guardiasConCompensacion = todasCompensaciones
        .map(comp => comp.id_guardia?.id_guardia || comp.id_guardia)
        .filter(Boolean);
      
      console.log('🚫 Guardias con compensación existente:', guardiasConCompensacion);
      
      // Filtrar guardias que NO tienen compensación
      const guardiasSinCompensacion = guardias.filter(guardia => 
        !guardiasConCompensacion.includes(guardia.id_guardia)
      );
      
      console.log('✅ Guardias disponibles para compensación:', guardiasSinCompensacion.length, 'de', guardias.length);
      
      guardias = guardiasSinCompensacion;
      
    } catch (err) {
      console.error('❌ Error verificando compensaciones existentes:', err);
      // En caso de error, mantener todas las guardias
    }
  }

  // Funciones reactivas para cargar datos cuando cambian las selecciones
  $: if (areaSeleccionada) cargarAgentes();
  $: if (agenteSeleccionado) cargarGuardias();

  // Compensaciones filtradas
  $: compensacionesFiltradas = compensaciones.filter((comp) => {
    // Filtro por área - necesitamos buscar el área de la guardia
    if (filtroAreaLista && comp.id_area !== parseInt(filtroAreaLista)) {
      return false;
    }
    // Filtro por estado
    if (filtroEstadoLista && comp.estado !== filtroEstadoLista) {
      return false;
    }
    return true;
  });

  async function crearCompensacion() {
    if (
      !guardiaSeleccionada ||
      !nuevaCompensacion.hora_fin_real ||
      !nuevaCompensacion.descripcion_motivo
    ) {
      alert("Por favor complete todos los campos obligatorios");
      return;
    }

    cargando = true;
    error = null;

    try {
      const guardiaData = guardias.find(
        (g) => g.id_guardia == guardiaSeleccionada,
      );

      const compensacionData = {
        hora_fin_real: nuevaCompensacion.hora_fin_real,
        motivo: nuevaCompensacion.motivo,
        descripcion_motivo: nuevaCompensacion.descripcion_motivo,
        numero_acta: nuevaCompensacion.numero_acta || "",
        solicitado_por: parseInt(
          nuevaCompensacion.solicitado_por || agenteSeleccionado,
        ),
      };

      console.log("Enviando compensación desde guardia:", guardiaSeleccionada, compensacionData);

      const response = await guardiasService.createCompensacionFromGuardia(
        guardiaSeleccionada,
        compensacionData,
        token,
      );
      console.log("Compensación creada:", response);

      // Limpiar formulario
      nuevaCompensacion = {
        id_guardia: "",
        hora_fin_real: "",
        motivo: "emergencia",
        descripcion_motivo: "",
        numero_acta: "",
        solicitado_por: "",
      };
      areaSeleccionada = "";
      agenteSeleccionado = "";
      guardiaSeleccionada = "";
      agentes = [];
      guardias = [];

      mostrandoFormulario = false;
      await cargarCompensaciones();
      alert("Compensación creada exitosamente");
    } catch (err) {
      console.error("Error completo creando compensación:", err);
      console.error("Respuesta del servidor:", err.response?.data);
      console.error("Status:", err.response?.status);

      const mensaje =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        "Error desconocido";
      error = "Error al crear compensación: " + mensaje;
      alert("Error: " + mensaje);
    } finally {
      cargando = false;
    }
  }

  function formatearFecha(fecha) {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleDateString("es-AR");
  }

  function formatearHora(hora) {
    if (!hora) return "-";
    return hora.slice(0, 5); // HH:MM
  }

  function verDetalles(compensacion) {
    compensacionSeleccionada = compensacion;
    mostrandoDetalles = true;
    console.log("Ver detalles de compensación:", compensacion);
  }

  function cerrarDetalles() {
    mostrandoDetalles = false;
    compensacionSeleccionada = null;
  }

  async function aprobarCompensacion(compensacion) {
    if (!confirm("¿Está seguro de aprobar esta compensación?")) {
      return;
    }

    try {
      cargando = true;
      error = null;

      console.log("Compensación a aprobar:", compensacion);

      // Identificar el ID correcto de la compensación
      const compensacionId =
        compensacion.id_hora_compensacion ||
        compensacion.id_compensacion ||
        compensacion.id ||
        compensacion.pk;
      console.log("ID de compensación:", compensacionId);

      if (!compensacionId) {
        throw new Error("No se pudo identificar el ID de la compensación");
      }

      const response = await guardiasService.aprobarCompensacion(
        compensacionId,
        { aprobado_por: 1 }, // TODO: Obtener del agente actual
        token,
      );

      await cargarCompensaciones();
      alert("Compensación aprobada exitosamente");
      console.log("Compensación aprobada:", response);
    } catch (err) {
      console.error("Error aprobando compensación:", err);
      const mensaje =
        err.response?.data?.message || err.message || "Error desconocido";
      error = "Error al aprobar compensación: " + mensaje;
      alert("Error: " + mensaje);
    } finally {
      cargando = false;
    }
  }

  async function rechazarCompensacion(compensacion) {
    const motivo = prompt("Ingrese el motivo del rechazo:");
    if (!motivo || !motivo.trim()) {
      return;
    }

    try {
      cargando = true;
      error = null;

      console.log("Compensación a rechazar:", compensacion);

      // Identificar el ID correcto de la compensación
      const compensacionId =
        compensacion.id_hora_compensacion ||
        compensacion.id_compensacion ||
        compensacion.id ||
        compensacion.pk;
      console.log("ID de compensación:", compensacionId);

      if (!compensacionId) {
        throw new Error("No se pudo identificar el ID de la compensación");
      }

      const response = await guardiasService.rechazarCompensacion(
        compensacionId,
        {
          motivo_rechazo: motivo.trim(),
          rechazado_por: 1, // TODO: Obtener del agente actual
        },
        token,
      );

      await cargarCompensaciones();
      alert("Compensación rechazada");
      console.log("Compensación rechazada:", response);
    } catch (err) {
      console.error("Error rechazando compensación:", err);
      const mensaje =
        err.response?.data?.message || err.message || "Error desconocido";
      error = "Error al rechazar compensación: " + mensaje;
      alert("Error: " + mensaje);
    } finally {
      cargando = false;
    }
  }
</script>

<svelte:head>
  <title>Compensaciones por Horas Extra - GIGA</title>
</svelte:head>

<div class="compensaciones-container">
  <div class="header">
    <h1>⏱️ Compensaciones por Horas Extra</h1>
    <p class="descripcion">
      Gestión de horas de compensación por emergencias que exceden el límite de
      10 horas por guardia
    </p>
    <button class="btn-nuevo" on:click={() => (mostrandoFormulario = true)}>
      ➕ Nueva Compensación
    </button>
  </div>

  <!-- Información explicativa -->
  <div class="info-explicativa">
    <h3>💡 ¿Qué son las Compensaciones?</h3>
    <div class="explicacion-grid">
      <div class="explicacion-item">
        <h4>🚨 Situaciones de Emergencia</h4>
        <p>
          Cuando una guardia se extiende más allá de las 10 horas reglamentarias
          debido a emergencias, accidentes, operativos especiales o situaciones
          imprevistas.
        </p>
      </div>
      <div class="explicacion-item">
        <h4>⏰ Registro de Horas Extra</h4>
        <p>
          Se documentan las horas adicionales trabajadas, el motivo de la
          extensión y se solicita la compensación correspondiente.
        </p>
      </div>
      <div class="explicacion-item">
        <h4>✅ Proceso de Aprobación</h4>
        <p>
          Las compensaciones deben ser aprobadas por superiores jerárquicos
          antes de ser incluidas en el cálculo de plus salarial.
        </p>
      </div>
    </div>
  </div>

  <!-- Errores -->
  {#if error}
    <div class="alert alert-error">
      ⚠️ {error}
    </div>
  {/if}

  <!-- Formulario nueva compensación -->
  {#if mostrandoFormulario}
    <div class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>Nueva Compensación por Horas Extra</h2>
          <button
            class="btn-close"
            on:click={() => (mostrandoFormulario = false)}>×</button
          >
        </div>

        <form on:submit|preventDefault={crearCompensacion} class="modal-body">
          <div class="paso-selector">
            <h3>Paso 1: Seleccionar Área</h3>
            <div class="campo">
              <label for="area">Área *</label>
              <select
                bind:value={areaSeleccionada}
                required
                disabled={cargandoAreas}
              >
                <option value="">
                  {cargandoAreas ? "Cargando áreas..." : "Seleccione un área"}
                </option>
                {#each areas as area}
                  <option value={area.id_area}>{area.nombre}</option>
                {/each}
                <!-- Debug: Mostrar cantidad de áreas -->
                {#if areas.length === 0 && !cargandoAreas}
                  <option disabled>No hay áreas disponibles</option>
                {/if}
              </select>
            </div>
          </div>

          {#if areaSeleccionada}
            <div class="paso-selector">
              <h3>Paso 2: Seleccionar Agente</h3>
              <div class="campo">
                <label for="agente">Agente *</label>
                <select
                  bind:value={agenteSeleccionado}
                  required
                  disabled={cargandoAgentes}
                >
                  <option value="">
                    {cargandoAgentes
                      ? "Cargando agentes..."
                      : "Seleccione un agente"}
                  </option>
                  {#each agentes as agente}
                    <option value={agente.id_agente}>
                      {agente.apellido}, {agente.nombre} (Leg: {agente.legajo})
                    </option>
                  {/each}
                </select>
              </div>
            </div>
          {/if}

          {#if agenteSeleccionado}
            <div class="paso-selector">
              <h3>Paso 3: Seleccionar Guardia</h3>
              <div class="campo">
                <label for="guardia">Guardia que Necesita Compensación *</label>
                <select
                  bind:value={guardiaSeleccionada}
                  required
                  disabled={cargandoGuardias}
                >
                  <option value="">
                    {cargandoGuardias
                      ? "Cargando guardias..."
                      : "Seleccione una guardia"}
                  </option>
                  {#each guardias as guardia}
                    <option value={guardia.id_guardia}>
                      {formatearFecha(guardia.fecha)} - {formatearHora(
                        guardia.hora_inicio,
                      )} a {formatearHora(guardia.hora_fin)}
                      {#if guardia.cronograma_nombre}
                        ({guardia.cronograma_nombre})
                      {/if}
                    </option>
                  {/each}
                </select>
                {#if guardias.length === 0 && !cargandoGuardias && agenteSeleccionado}
                  <small class="text-warning"
                    >Este agente no tiene guardias registradas recientes</small
                  >
                {/if}
              </div>
            </div>
          {/if}

          {#if guardiaSeleccionada}
            <div class="paso-selector">
              <h3>Paso 4: Detalles de la Compensación</h3>

              <div class="campo">
                <label for="hora_fin_real">Hora Real de Finalización *</label>
                <input
                  type="time"
                  bind:value={nuevaCompensacion.hora_fin_real}
                  required
                />
                <small
                  >Hora en que realmente terminó el servicio (debe exceder las
                  10 horas)</small
                >
              </div>

              <div class="campo">
                <label for="motivo">Motivo de la Emergencia *</label>
                <select bind:value={nuevaCompensacion.motivo} required>
                  {#each motivosCompensacion as motivo}
                    <option value={motivo.value}>{motivo.label}</option>
                  {/each}
                </select>
              </div>

              <div class="campo">
                <label for="descripcion_motivo">Descripción del Motivo *</label>
                <textarea
                  bind:value={nuevaCompensacion.descripcion_motivo}
                  required
                  rows="3"
                  placeholder="Describa detalladamente qué situación causó que se extendiera el horario..."
                ></textarea>
              </div>

              <div class="campo">
                <label for="numero_acta">Número de Acta (Opcional)</label>
                <input
                  type="text"
                  bind:value={nuevaCompensacion.numero_acta}
                  placeholder="Si existe un expediente o acta relacionada"
                />
              </div>

              <div class="campo">
                <label for="solicitado_por">Solicitado por *</label>
                <select bind:value={nuevaCompensacion.solicitado_por} required>
                  <option value=""
                    >Seleccione quién solicita la compensación</option
                  >
                  {#if agenteSeleccionado}
                    <option value={agenteSeleccionado} selected>
                      {agentes.find((a) => a.id_agente == agenteSeleccionado)
                        ?.apellido},
                      {agentes.find((a) => a.id_agente == agenteSeleccionado)
                        ?.nombre} (El mismo agente)
                    </option>
                  {/if}
                  {#each agentes.filter((a) => a.id_agente != agenteSeleccionado) as agente}
                    <option value={agente.id_agente}>
                      {agente.apellido}, {agente.nombre} (Leg: {agente.legajo})
                    </option>
                  {/each}
                </select>
                <small
                  >Agente que solicita la compensación (puede ser diferente al
                  que realizó la guardia)</small
                >
              </div>
            </div>
          {/if}

          <div class="modal-footer">
            <button
              type="button"
              class="btn-cancelar"
              on:click={() => (mostrandoFormulario = false)}
            >
              Cancelar
            </button>
            <button type="submit" class="btn-guardar" disabled={cargando}>
              {cargando ? "Guardando..." : "Crear Compensación"}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <!-- Lista de compensaciones -->
  <div class="lista-compensaciones">
    <div class="lista-header">
      <h2>Compensaciones Registradas ({compensaciones.length})</h2>

      <!-- Filtros para la lista -->
      <div class="filtros-lista">
        <div class="filtro-grupo">
          <label for="filtro-area-lista">Filtrar por Área:</label>
          <select id="filtro-area-lista" bind:value={filtroAreaLista}>
            <option value="">Todas las áreas</option>
            {#each areas as area}
              <option value={area.id_area}>{area.nombre}</option>
            {/each}
          </select>
        </div>

        <div class="filtro-grupo">
          <label for="filtro-estado-lista">Estado:</label>
          <select id="filtro-estado-lista" bind:value={filtroEstadoLista}>
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendiente</option>
            <option value="aprobada">Aprobada</option>
            <option value="rechazada">Rechazada</option>
          </select>
        </div>

        <button
          class="btn-recargar"
          on:click={cargarCompensaciones}
          disabled={cargando}
        >
          🔄 Recargar
        </button>
      </div>
    </div>

    {#if cargando}
      <div class="loading">
        <div class="spinner"></div>
        Cargando compensaciones...
      </div>
    {:else if compensacionesFiltradas.length === 0}
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>
          {#if compensaciones.length === 0}
            No hay compensaciones registradas
          {:else}
            No hay compensaciones que coincidan con los filtros
          {/if}
        </h3>
        <p>
          {#if compensaciones.length === 0}
            Cuando se registre una compensación por horas extra aparecerá aquí
          {:else}
            Intente cambiar los filtros para ver más resultados
          {/if}
        </p>
      </div>
    {:else}
      <div class="table-container">
        <table class="compensaciones-table">
          <thead>
            <tr>
              <th>Agente</th>
              <th>Fecha</th>
              <th>Horas Extra</th>
              <th>Motivo</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each compensacionesFiltradas as compensacion}
              <tr>
                <td>
                  <div class="agente-info">
                    <strong
                      >ID: {compensacion.id_agente ||
                        compensacion.agente_id ||
                        "N/A"}</strong
                    >
                    {#if compensacion.agente_nombre}
                      <br /><small
                        >{compensacion.agente_apellido}, {compensacion.agente_nombre}</small
                      >
                    {/if}
                  </div>
                </td>
                <td>{formatearFecha(compensacion.fecha_servicio)}</td>
                <td>
                  <span class="horas-badge">
                    {compensacion.horas_extra || "N/A"}h
                  </span>
                  {#if compensacion.hora_fin_real}
                    <br /><small
                      >Finalizó: {formatearHora(
                        compensacion.hora_fin_real,
                      )}</small
                    >
                  {/if}
                </td>
                <td>
                  <span class="motivo-badge"
                    >{compensacion.motivo || "N/A"}</span
                  >
                  {#if compensacion.numero_acta}
                    <br /><small>Acta: {compensacion.numero_acta}</small>
                  {/if}
                </td>
                <td>
                  <span
                    class="estado-badge estado-{compensacion.estado ||
                      'pendiente'}"
                  >
                    {compensacion.estado || "Pendiente"}
                  </span>
                </td>
                <td>
                  <div class="acciones-grupo">
                    <button
                      class="btn-small btn-ver"
                      on:click={() => verDetalles(compensacion)}
                    >
                      👁️ Ver
                    </button>
                    {#if compensacion.estado === "pendiente"}
                      <button
                        class="btn-small btn-aprobar"
                        on:click={() => aprobarCompensacion(compensacion)}
                      >
                        ✅ Aprobar
                      </button>
                      <button
                        class="btn-small btn-rechazar"
                        on:click={() => rechazarCompensacion(compensacion)}
                      >
                        ❌ Rechazar
                      </button>
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<!-- Modal de detalles de compensación -->
{#if mostrandoDetalles && compensacionSeleccionada}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal-overlay" on:click={cerrarDetalles}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-detalles" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Detalles de Compensación</h2>
        <button class="btn-close" on:click={cerrarDetalles}>×</button>
      </div>

      <div class="modal-body">
        <div class="detalle-seccion">
          <h3>Información General</h3>
          <div class="detalle-grid">
            <div class="detalle-item">
              <label>ID Compensación:</label>
              <span
                >{compensacionSeleccionada.id_hora_compensacion ||
                  compensacionSeleccionada.id_compensacion ||
                  compensacionSeleccionada.id ||
                  "N/A"}</span
              >
            </div>
            <div class="detalle-item">
              <label>Estado:</label>
              <span
                class="estado-badge estado-{compensacionSeleccionada.estado ||
                  'pendiente'}"
              >
                {compensacionSeleccionada.estado || "Pendiente"}
              </span>
            </div>
            <div class="detalle-item">
              <label>Fecha de Solicitud:</label>
              <span
                >{formatearFecha(
                  compensacionSeleccionada.fecha_solicitud ||
                    compensacionSeleccionada.created_at,
                )}</span
              >
            </div>
            <div class="detalle-item">
              <label>Solicitado por:</label>
              <span>ID: {compensacionSeleccionada.solicitado_por || "N/A"}</span
              >
            </div>
          </div>
        </div>

        <div class="detalle-seccion">
          <h3>Detalles de la Guardia</h3>
          <div class="detalle-grid">
            <div class="detalle-item">
              <label>ID Guardia:</label>
              <span>{compensacionSeleccionada.id_guardia || "N/A"}</span>
            </div>
            <div class="detalle-item">
              <label>Agente:</label>
              <span>
                {#if compensacionSeleccionada.agente_nombre}
                  {compensacionSeleccionada.agente_apellido}, {compensacionSeleccionada.agente_nombre}
                {:else}
                  ID: {compensacionSeleccionada.id_agente ||
                    compensacionSeleccionada.agente_id ||
                    "N/A"}
                {/if}
              </span>
            </div>
            <div class="detalle-item">
              <label>Fecha de Servicio:</label>
              <span
                >{formatearFecha(compensacionSeleccionada.fecha_servicio)}</span
              >
            </div>
            <div class="detalle-item">
              <label>Hora Real de Fin:</label>
              <span
                >{formatearHora(compensacionSeleccionada.hora_fin_real)}</span
              >
            </div>
          </div>
        </div>

        <div class="detalle-seccion">
          <h3>Motivo y Justificación</h3>
          <div class="detalle-grid">
            <div class="detalle-item detalle-full">
              <label>Tipo de Motivo:</label>
              <span class="motivo-badge"
                >{compensacionSeleccionada.motivo || "N/A"}</span
              >
            </div>
            <div class="detalle-item detalle-full">
              <label>Descripción del Motivo:</label>
              <div class="descripcion-texto">
                {compensacionSeleccionada.descripcion_motivo ||
                  "Sin descripción"}
              </div>
            </div>
            {#if compensacionSeleccionada.numero_acta}
              <div class="detalle-item detalle-full">
                <label>Número de Acta:</label>
                <span>{compensacionSeleccionada.numero_acta}</span>
              </div>
            {/if}
          </div>
        </div>

        <div class="detalle-seccion">
          <h3>Cálculo de Horas</h3>
          <div class="detalle-grid">
            <div class="detalle-item">
              <label>Horas Extra Calculadas:</label>
              <span class="horas-badge">
                {compensacionSeleccionada.horas_extra ||
                  "Pendiente de cálculo"}h
              </span>
            </div>
            {#if compensacionSeleccionada.monto_compensacion}
              <div class="detalle-item">
                <label>Monto de Compensación:</label>
                <span class="monto-badge">
                  ${compensacionSeleccionada.monto_compensacion}
                </span>
              </div>
            {/if}
          </div>
        </div>

        {#if compensacionSeleccionada.estado !== "pendiente"}
          <div class="detalle-seccion">
            <h3>Estado de Aprobación</h3>
            <div class="detalle-grid">
              {#if compensacionSeleccionada.aprobado_por}
                <div class="detalle-item">
                  <label>Aprobado por:</label>
                  <span>ID: {compensacionSeleccionada.aprobado_por}</span>
                </div>
              {/if}
              {#if compensacionSeleccionada.fecha_aprobacion}
                <div class="detalle-item">
                  <label>Fecha de Aprobación:</label>
                  <span
                    >{formatearFecha(
                      compensacionSeleccionada.fecha_aprobacion,
                    )}</span
                  >
                </div>
              {/if}
              {#if compensacionSeleccionada.motivo_rechazo}
                <div class="detalle-item detalle-full">
                  <label>Motivo de Rechazo:</label>
                  <div class="descripcion-texto rechazo">
                    {compensacionSeleccionada.motivo_rechazo}
                  </div>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn-cancelar" on:click={cerrarDetalles}>Cerrar</button>

        {#if compensacionSeleccionada.estado === "pendiente"}
          <button
            class="btn-guardar btn-aprobar"
            on:click={() => {
              aprobarCompensacion(compensacionSeleccionada);
              cerrarDetalles();
            }}
            disabled={cargando}
          >
            ✅ Aprobar Compensación
          </button>
          <button
            class="btn-cancelar btn-rechazar"
            on:click={() => {
              rechazarCompensacion(compensacionSeleccionada);
              cerrarDetalles();
            }}
            disabled={cargando}
          >
            ❌ Rechazar Compensación
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .compensaciones-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #e2e8f0;
  }

  .header h1 {
    color: #2d3748;
    margin: 0 0 10px 0;
    font-size: 28px;
  }

  .descripcion {
    color: #718096;
    font-size: 14px;
    margin: 0;
    max-width: 600px;
  }

  /* Información explicativa */
  .info-explicativa {
    background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%);
    border: 1px solid #d4edda;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .info-explicativa h3 {
    color: #155724;
    margin-bottom: 15px;
    font-size: 1.2rem;
  }

  .explicacion-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
  }

  .explicacion-item {
    background: white;
    padding: 15px;
    border-radius: 6px;
    border-left: 4px solid #28a745;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .explicacion-item h4 {
    color: #155724;
    margin-bottom: 8px;
    font-size: 1rem;
  }

  .explicacion-item p {
    color: #333;
    font-size: 0.9rem;
    line-height: 1.4;
    margin: 0;
  }

  .btn-nuevo {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .btn-nuevo:hover {
    background: #2563eb;
    transform: translateY(-1px);
  }

  .alert {
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-weight: 500;
  }

  .alert-error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    margin: 0;
    color: #1f2937;
    font-size: 20px;
  }

  .btn-close {
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #6b7280;
    padding: 4px;
    border-radius: 4px;
  }

  .btn-close:hover {
    background: #f3f4f6;
  }

  .modal-body {
    padding: 24px;
  }

  .paso-selector {
    margin-bottom: 24px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
  }

  .paso-selector h3 {
    margin: 0 0 12px 0;
    color: #1e40af;
    font-size: 16px;
    font-weight: 600;
  }

  .campo {
    margin-bottom: 20px;
  }

  .campo label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    color: #374151;
    font-size: 14px;
  }

  .campo input,
  .campo select,
  .campo textarea {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.2s;
  }

  .campo input:focus,
  .campo select:focus,
  .campo textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .campo small {
    display: block;
    margin-top: 4px;
    color: #6b7280;
    font-size: 12px;
  }

  .text-warning {
    color: #d97706 !important;
    font-weight: 500;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 24px;
    border-top: 1px solid #e5e7eb;
  }

  .btn-cancelar,
  .btn-guardar,
  .btn-small,
  .btn-ver {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-cancelar {
    background: #6b7280;
    color: white;
  }

  .btn-cancelar:hover {
    background: #4b5563;
  }

  .btn-guardar {
    background: #10b981;
    color: white;
  }

  .btn-guardar:hover:not(:disabled) {
    background: #059669;
  }

  .btn-guardar:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .lista-compensaciones {
    margin-top: 40px;
  }

  .lista-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    gap: 20px;
    flex-wrap: wrap;
  }

  .lista-header h2 {
    color: #374151;
    margin: 0;
    font-size: 20px;
  }

  .filtros-lista {
    display: flex;
    gap: 15px;
    align-items: end;
    flex-wrap: wrap;
  }

  .filtro-grupo {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 150px;
  }

  .filtro-grupo label {
    font-size: 12px;
    font-weight: 600;
    color: #4b5563;
  }

  .filtro-grupo select {
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    background: white;
  }

  .btn-recargar {
    padding: 8px 16px;
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    height: fit-content;
  }

  .btn-recargar:hover:not(:disabled) {
    background: #e5e7eb;
  }

  .btn-recargar:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: #6b7280;
    font-size: 16px;
    gap: 12px;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 3px solid #e5e7eb;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #6b7280;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .empty-state h3 {
    margin: 0 0 8px 0;
    color: #374151;
  }

  .empty-state p {
    margin: 0;
    font-size: 14px;
  }

  .table-container {
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: white;
  }

  .compensaciones-table {
    width: 100%;
    border-collapse: collapse;
  }

  .compensaciones-table th {
    background: #f9fafb;
    padding: 16px;
    text-align: left;
    font-weight: 600;
    color: #374151;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }

  .compensaciones-table td {
    padding: 16px;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }

  .compensaciones-table tbody tr:hover {
    background: #f9fafb;
  }

  .agente-info strong {
    display: block;
    color: #374151;
  }

  .agente-info small {
    color: #6b7280;
    font-size: 12px;
  }

  .horas-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 12px;
  }

  .motivo-badge {
    display: inline-block;
    background: #f3f4f6;
    color: #374151;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
    text-transform: capitalize;
  }

  .estado-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;
  }

  .estado-pendiente {
    background: #fef3c7;
    color: #92400e;
  }

  .estado-aprobada {
    background: #d1fae5;
    color: #065f46;
  }

  .estado-rechazada {
    background: #fee2e2;
    color: #991b1b;
  }

  .btn-small {
    padding: 6px 12px;
    font-size: 12px;
  }

  .btn-ver {
    background: #3b82f6;
    color: white;
  }

  .btn-ver:hover {
    background: #2563eb;
  }

  .acciones-grupo {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn-aprobar {
    background: #10b981;
    color: white;
  }

  .btn-aprobar:hover {
    background: #059669;
  }

  .btn-rechazar {
    background: #ef4444;
    color: white;
  }

  .btn-rechazar:hover {
    background: #dc2626;
  }

  /* Modal de detalles */
  .modal-detalles {
    background: white;
    border-radius: 12px;
    max-width: 800px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    border: 2px solid #e5e7eb;
  }

  .detalle-seccion {
    margin-bottom: 24px;
    padding: 20px;
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
  }

  .detalle-seccion h3 {
    margin: 0 0 16px 0;
    color: #1e40af;
    font-size: 18px;
    font-weight: 700;
  }

  .detalle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }

  .detalle-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .detalle-item.detalle-full {
    grid-column: 1 / -1;
  }

  .detalle-item label {
    font-weight: 600;
    color: #4b5563;
    font-size: 14px;
  }

  .detalle-item span {
    color: #111827;
    font-size: 14px;
  }

  .descripcion-texto {
    padding: 12px;
    background: white;
    border-radius: 6px;
    border: 1px solid #d1d5db;
    color: #374151;
    font-size: 14px;
    line-height: 1.5;
    white-space: pre-wrap;
  }

  .descripcion-texto.rechazo {
    background: #fef2f2;
    border-color: #fecaca;
    color: #991b1b;
  }

  .monto-badge {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
  }

  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
    }

    .btn-nuevo {
      align-self: flex-start;
    }

    .modal {
      width: 95%;
      margin: 10px;
    }

    .compensaciones-table {
      font-size: 12px;
    }

    .compensaciones-table th,
    .compensaciones-table td {
      padding: 12px;
    }
  }
</style>
