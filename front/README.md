# Frontend - Sistema GIGA

## Descripción
Frontend desarrollado en **SvelteKit** con **JavaScript** que consume la API REST del backend Django. 
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

## Instalación y Configuración

### Requisitos Previos
- **Node.js 18+** 
- **npm** (incluido con Node.js)

#### **Linux (Ubuntu/Debian)**
```bash
# Actualizar repositorios
sudo apt update

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalación
node --version
npm --version
```

#### **macOS**
```bash
# Con Homebrew
brew install node

# Verificar instalación
node --version
npm --version
```

#### **Windows**
1. Descargar e instalar [Node.js](https://nodejs.org/en/download/) desde el sitio oficial
2. Verificar instalación en PowerShell/CMD:
```cmd
node --version
npm --version
```

### Configuración del Entorno

#### Variables de Entorno

##### **Linux / macOS**
```bash
# Crear archivo .env
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000/api
EOF
```

##### **Windows (PowerShell)**
```powershell
# Crear archivo .env
@"
VITE_API_URL=http://localhost:8000/api
"@ | Out-File -FilePath .env -Encoding utf8
```

##### **Windows (CMD)**
```cmd
# Crear archivo .env
echo VITE_API_URL=http://localhost:8000/api > .env
```

### Instalación de Dependencias

#### Todos los sistemas
```bash
# Instalar dependencias del proyecto
npm install

# Verificar que las dependencias se instalaron correctamente
npm list --depth=0
```

## Ejecutar en Desarrollo

### Iniciar Servidor de Desarrollo

#### **Linux / macOS**
```bash
# Iniciar servidor de desarrollo
npm run dev

# Frontend disponible en: http://localhost:5173
```

#### **Windows (PowerShell/CMD)**
```cmd
# Iniciar servidor de desarrollo
npm run dev

# Frontend disponible en: http://localhost:5173
```

### Otros Comandos Útiles

#### Todos los sistemas
```bash
# Build para producción
npm run build

# Vista previa de build de producción
npm run preview

# Limpiar node_modules y reinstalar

rm -rf node_modules package-lock.json  # Linux/macOS

rmdir /s node_modules && del package-lock.json  # Windows CMD

npm install # Ambos
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
- Manejo de estados globales
- Validación de formularios

## Dependencias Principales

- **@sveltejs/kit**: Framework Svelte
- **svelte**: Core de Svelte
- **axios**: Cliente HTTP
- **vite**: Build tool y dev server

## Próximos Pasos

1. **Conectar con backend**: Asegurarse que backend esté ejecutándose en puerto 8000
2. **Implementar autenticación**: Login/logout completo
3. **Crear páginas CRUD**: Para cada módulo del sistema
4. **Diseñar UI/UX**: Interfaz moderna y responsive
5. **Testing**: Pruebas unitarias y de integración

El frontend está preparado para desarrollo y listo para conectar con el backend Django.