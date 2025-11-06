# Panel de Administración - Arquitectura Refactorizada

Este directorio contiene la nueva arquitectura del panel de administración, separando la lógica de negocio de la presentación para mejorar la mantenibilidad y reutilización del código.

## 📁 Estructura de Directorios

```
src/lib/paneladmin/
├── controllers/          # Controladores de lógica de negocio
│   ├── usuariosController.js
│   ├── rolesController.js
│   ├── parametrosController.js
│   ├── organigramaController.js
│   └── index.js
├── stores/              # Stores compartidos (reservado para futuro uso)
├── utils/               # Utilidades y funciones comunes
│   └── common.js
├── constants.js         # Constantes y configuraciones
└── README.md           # Esta documentación
```

## 🎯 Principios de Diseño

### Separación de Responsabilidades
- **Controladores**: Manejan la lógica de negocio y el estado
- **Componentes**: Solo se encargan de la presentación y eventos de UI
- **Utilidades**: Funciones reutilizables para validación, formateo, etc.
- **Constantes**: Valores fijos y configuraciones centralizadas

### Manejo de Estado Reactivo
- Uso de Svelte stores para estado reactivo
- Stores derivados para datos calculados
- Patrón singleton para controladores

### Gestión de Errores Estandarizada
- Manejo consistente de errores de API
- Mensajes de error descriptivos y localizados
- Logging centralizado para debugging

## 🔧 Controladores

### UsuariosController (`usuariosController.js`)
Gestiona la lógica de negocio para la administración de usuarios/agentes.

**Características principales:**
- CRUD completo de agentes
- Filtrado y búsqueda avanzada
- Gestión de roles de usuarios
- Validación de datos
- Manejo de modales y estados de UI

**Stores expuestos:**
- `agentes`: Lista de agentes
- `agentesFiltrados`: Agentes filtrados según criterios
- `estadisticas`: Estadísticas calculadas
- `modalStates`: Estados de modales

**Métodos principales:**
```javascript
// Inicialización
await usuariosController.init()

// Operaciones CRUD
await usuariosController.cargarAgentes()
await usuariosController.guardarCambiosAgente(agente, formData)
await usuariosController.crearNuevoAgente(formData)
await usuariosController.confirmarEliminacionAgente(agente)

// Gestión de UI
usuariosController.verAgente(agente)
usuariosController.editarAgente(agente)
usuariosController.limpiarFiltros()
```

### RolesController (`rolesController.js`)
Gestiona la asignación y administración de roles de usuarios.

**Características principales:**
- Gestión de asignaciones de roles
- Prevención de auto-modificación de roles
- Filtrado por área y búsqueda
- Validación de permisos

### ParametrosController (`parametrosController.js`)
Gestiona los parámetros del sistema (áreas y agrupaciones).

**Características principales:**
- CRUD de áreas y agrupaciones
- Gestión de horarios por área/agrupación
- Validación de eliminaciones (agentes asignados)
- Filtrado independiente por tipo

### OrganigramaController (`organigramaController.js`)
Gestiona la visualización del organigrama organizacional.

**Características principales:**
- Múltiples vistas del organigrama (jerárquica, por áreas, por roles)
- Cálculo de estadísticas organizacionales
- Filtrado avanzado
- Generación de estructuras de datos para visualización

## 📊 Uso en Componentes

### Migración desde el patrón anterior

**Antes (en el componente .svelte):**
```javascript
<script>
  import { onMount } from 'svelte';
  import { personasService } from '$lib/services.js';
  
  let agentes = [];
  let loading = true;
  let error = null;
  
  onMount(async () => {
    try {
      const response = await personasService.getAgentes();
      agentes = response.data.results;
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  });
  
  async function eliminarAgente(id) {
    try {
      await personasService.deleteAgente(id);
      agentes = agentes.filter(a => a.id !== id);
    } catch (err) {
      alert(err.message);
    }
  }
</script>
```

**Después (usando controlador):**
```javascript
<script>
  import { onMount } from 'svelte';
  import { usuariosController } from '$lib/paneladmin/controllers';
  
  // Acceso directo a los stores del controlador
  $: agentes = $usuariosController.agentesFiltrados;
  $: loading = $usuariosController.loading;
  $: error = $usuariosController.error;
  
  onMount(async () => {
    try {
      await usuariosController.init();
    } catch (err) {
      // El controlador maneja el error automáticamente
      console.error('Error inicializando:', err);
    }
  });
  
  async function eliminarAgente(agente) {
    try {
      const result = await usuariosController.confirmarEliminacionAgente(agente);
      if (result.success) {
        // Notificación de éxito manejada por el controlador
      }
    } catch (err) {
      // Error manejado y mostrado por el controlador
      alert(err.message);
    }
  }
</script>
```

### Beneficios de la nueva arquitectura

1. **Código más limpio**: Los componentes se enfocan solo en la presentación
2. **Reutilización**: La lógica puede reutilizarse en múltiples componentes
3. **Testabilidad**: Los controladores pueden probarse independientemente
4. **Mantenibilidad**: Cambios en la lógica de negocio no afectan la UI
5. **Consistencia**: Comportamiento uniforme en toda la aplicación

## 🛠️ Utilidades

### Validaciones (`utils/common.js`)
```javascript
import { validations } from '$lib/paneladmin/utils/common.js';

// Validar email
const isValid = validations.isValidEmail('usuario@ejemplo.com');

// Validar DNI argentino
const isDniValid = validations.isValidDNI('12345678');

// Validar CUIL/CUIT
const isCuilValid = validations.isValidCUIL('20-12345678-9');
```

### Formateo de datos
```javascript
import { formatters } from '$lib/paneladmin/utils/common.js';

// Formatear nombre completo
const fullName = formatters.fullName('Juan', 'Pérez');

// Formatear DNI con puntos
const formattedDni = formatters.formatDNI('12345678'); // "12.345.678"

// Formatear fecha
const formattedDate = formatters.formatDate('2024-01-15');
```

### Manejo de errores
```javascript
import { errorUtils } from '$lib/paneladmin/utils/common.js';

try {
  await apiCall();
} catch (error) {
  const message = errorUtils.extractErrorMessage(error);
  console.error(message);
}
```

## 📋 Constantes

Todas las constantes están centralizadas en `constants.js`:

```javascript
import { 
  APP_CONFIG, 
  THEME_COLORS, 
  SYSTEM_MESSAGES,
  FORM_CONFIG 
} from '$lib/paneladmin/constants.js';

// Configuración de la app
console.log(APP_CONFIG.APP_NAME); // "GIGA"

// Colores del tema
const primaryColor = THEME_COLORS.PRIMARY; // "#e79043"

// Mensajes del sistema
alert(SYSTEM_MESSAGES.SUCCESS.CREATED); // "Registro creado exitosamente"

// Validaciones de formulario
const minLength = FORM_CONFIG.MIN_NAME_LENGTH; // 2
```

## 🚀 Próximos Pasos

### Implementación Gradual
1. **Fase 1** ✅: Crear controladores y estructura base
2. **Fase 2**: Migrar página de usuarios
3. **Fase 3**: Migrar página de roles  
4. **Fase 4**: Migrar página de parámetros
5. **Fase 5**: Migrar página de organigrama
6. **Fase 6**: Optimizaciones y mejoras

### Mejoras Futuras
- [ ] Sistema de notificaciones centralizado
- [ ] Cache inteligente para datos
- [ ] Modo offline/sync
- [ ] Internacionalización (i18n)
- [ ] Temas personalizables
- [ ] Tests unitarios para controladores
- [ ] Documentación de API integrada
- [ ] Métricas y analytics

## 📚 Mejores Prácticas

### Para Desarrolladores

1. **Siempre inicializar controladores**: Llamar a `init()` antes de usar
2. **Usar stores reactivos**: Aprovechar `$:` para reactividad automática
3. **Manejar errores apropiadamente**: Usar try/catch y mostrar mensajes al usuario
4. **Validar datos**: Usar las utilidades de validación antes de enviar
5. **Mantener componentes simples**: Delegar lógica compleja a controladores
6. **Documentar cambios**: Actualizar esta documentación cuando agregues nuevas funcionalidades

### Convenciones de Código

- **Nombres de stores**: camelCase (`agentes`, `agentesFiltrados`)
- **Nombres de métodos**: camelCase con verbos (`cargarAgentes`, `eliminarAgente`)
- **Nombres de constantes**: UPPER_SNAKE_CASE (`APP_CONFIG`, `HTTP_STATUS`)
- **Comentarios**: JSDoc para funciones públicas
- **Logs**: Usar emoji y niveles apropiados (`console.log('✅ Éxito')`, `console.error('❌ Error')`)

### Performance

- Los controladores implementan lazy loading automático
- Los stores derivados se recalculan solo cuando cambian sus dependencias
- Las operaciones de red incluyen debouncing automático
- El estado se mantiene entre navegaciones dentro del panel

---

**Nota**: Esta arquitectura está diseñada para escalar y facilitar el mantenimiento a largo plazo. Si tienes dudas o sugerencias, no dudes en actualizar esta documentación.