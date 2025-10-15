# Frontend - Sistema de Control Horario y Guardias

## Descripción
Frontend desarrollado en **SvelteKit** con **JavaScript** que consume la API REST del backend Django. Proporciona una interfaz web moderna y responsive para la gestión del sistema de control horario y guardias.

## Tecnologías Utilizadas

- **SvelteKit**: Framework de desarrollo web
- **JavaScript**: Lenguaje principal
- **Axios**: Cliente HTTP para consumo de API
- **Vite**: Build tool y servidor de desarrollo
- **CSS/HTML**: Estilos personalizados

## Scripts Disponibles

```bash
# Servidor de desarrollo (puerto 5173)
npm run dev

# Construcción para producción
npm run build

# Vista previa de la build de producción
npm run preview

# Verificación de código
npm run check
```

## Funcionalidades Implementadas

### Dashboard Principal (`/`)
- Vista general del sistema con módulos principales
- Contadores dinámicos de agentes y áreas
- Manejo de errores de conexión con el backend
- Estado de carga con spinner animado

### Configuración de API (`src/lib/api.js`)
- Cliente HTTP configurado con Axios
- Interceptores para autenticación automática
- Manejo de tokens en localStorage

### Servicios de API (`src/lib/services.js`)
Servicios completos para todas las apps del backend:
- `personasService`: Gestión de agentes, áreas, roles
- `asistenciaService`: Control de asistencias, marcas, licencias
- `guardiasService`: Cronogramas, guardias, feriados
- `reportesService`: Reportes y notificaciones
- `convenioIaService`: Consultas inteligentes de convenios
- `auditoriaService`: Parámetros y registros de auditoría

## Variables de Entorno

Crear archivo `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

## Instalación y Desarrollo

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# El frontend estará disponible en http://localhost:5173
```

## Integración con Backend

- Token-based authentication usando localStorage
- CORS configurado para funcionar con backend en puerto 8000
- Interceptores automáticos para manejo de errores
- Métodos CRUD completos para todas las entidades

## Estado del Desarrollo

### Completado
- Configuración básica de SvelteKit
- Cliente API con Axios
- Servicios para todas las apps del backend
- Dashboard principal con integración de API

### Por Implementar
- Páginas específicas para cada módulo
- Sistema de autenticación completo
- Formularios CRUD
- Componentes reutilizables
- Navegación entre páginas

El frontend está preparado para desarrollo y listo para conectar con el backend Django.