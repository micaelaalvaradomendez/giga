# Sistema GIGA - Stack Tecnológico
## Arquitectura y Tecnologías Utilizadas

---

## 📋 Resumen Ejecutivo

El Sistema GIGA está construido sobre una **arquitectura de microservicios containerizada** utilizando tecnologías modernas y estándares de la industria. La arquitectura separa claramente el frontend, backend, base de datos y servicios auxiliares, permitiendo escalabilidad, mantenibilidad y despliegue independiente de componentes.

**Arquitectura**: Microservicios con contenedores Docker  
**Patrón**: API RESTful con SPA (Single Page Application)  
**Base de Datos**: Relacional (PostgreSQL)  
**Deployment**: Containerizado con Docker Compose

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        NGINX (Puerto 80)                     │
│                    Reverse Proxy & Load Balancer             │
└────────────┬─────────────────────────────────┬──────────────┘
             │                                 │
    ┌────────▼─────────┐              ┌───────▼──────────┐
    │   Frontend       │              │    Backend       │
    │   SvelteKit      │◄────API─────►│    Django        │
    │   (Puerto 3000)  │   REST       │  (Puerto 8000)   │
    └──────────────────┘              └─────────┬────────┘
                                               │
                                      ┌────────▼─────────┐
                                      │   PostgreSQL     │
                                      │  (Puerto 5432)   │
                                      └──────────────────┘
         ┌─────────────────────────────────────┐
         │  Servicios Auxiliares               │
         │  - MinIO (Object Storage)           │
         │  - n8n (Workflow Automation)        │
         └─────────────────────────────────────┘
```

---

## 🎨 Frontend

### SvelteKit 2.47.1
**Propósito**: Framework principal para construcción de la interfaz de usuario

**Características**:
- **Renderizado**: Server-Side Rendering (SSR) y Client-Side Rendering (CSR) híbrido
- **Routing**: Sistema de routing basado en archivos (`/routes`)
- **Compilación**: Código altamente optimizado mediante compilación en tiempo de build
- **Reactividad**: Reactivity nativa sin Virtual DOM
- **Performance**: Bundle size reducido comparado con frameworks tradicionales

**Justificación**: Seleccionado por su rendimiento superior, curva de aprendizaje suave y tamaño de bundle optimizado, crucial para aplicaciones gubernamentales con potencial acceso desde conexiones limitadas.

---

### Svelte 5.41.0
**Propósito**: Biblioteca de componentes reactivos core

**Características**:
- **Componentes**: Sistema de componentes reutilizables con scoped CSS
- **Stores**: Manejo de estado global reactivo
- **Transitions**: Animaciones y transiciones integradas
- **Binding**: Two-way data binding declarativo

**Uso en GIGA**:
- Componentes de UI (`/lib/componentes/`)
- Gestión de estado de aplicación
- Interactividad de formularios
- Calendarios y visualizaciones de datos

---

### Vite 7.1.10
**Propósito**: Build tool y development server

**Características**:
- **Dev Server**: Hot Module Replacement (HMR) ultra-rápido
- **Build**: Bundling optimizado con Rollup
- **ES Modules**: Soporte nativo de módulos ES6+
- **Plugin System**: Extensible mediante plugins

**Beneficios**:
- Inicio de desarrollo instantáneo (< 1 segundo)
- HMR en milisegundos
- Builds de producción optimizados

---

### Axios 1.13.1
**Propósito**: Cliente HTTP para comunicación con el backend

**Características**:
- **Promise-based**: API basada en promesas para operaciones asíncronas
- **Interceptors**: Manejo centralizado de requests/responses
- **Cancelación**: Cancelación de requests con AbortController
- **Transformaciones**: Transformación automática de datos JSON

**Implementación en GIGA**:
- Centralizado en `/lib/services.js`
- Interceptores para autenticación (headers JWT)
- Manejo de errores global
- Retry logic para requests fallidos

---

### @iconify/svelte 4.2.0
**Propósito**: Sistema de iconografía

**Características**:
- **Unificado**: Acceso a múltiples sets de iconos (Material, Heroicons, etc.)
- **On-demand**: Carga solo los iconos utilizados
- **SVG**: Renderizado SVG optimizado

**Uso**: Iconos en botones, menús, estados de aplicación

---

### TypeScript 5.9.3
**Propósito**: Type checking y autocompletado en desarrollo

**Características**:
- **Type Safety**: Detección de errores en tiempo de desarrollo
- **IntelliSense**: Autocompletado mejorado en IDEs
- **JSDoc**: Documentación de tipos inline

**Configuración**: Habilitado vía `jsconfig.json` para proyectos JavaScript

---

## ⚙️ Backend

### Django 4.2.0+
**Propósito**: Framework web principal para API y lógica de negocio

**Características**:
- **ORM**: Object-Relational Mapping para abstracción de base de datos
- **Admin**: Panel administrativo auto-generado
- **Seguridad**: Protección integrada contra CSRF, XSS, SQL Injection
- **Migrations**: Sistema de migraciones de base de datos versionadas
- **Apps**: Arquitectura modular basada en aplicaciones Django

**Estructura en GIGA**:
```
/back
├── giga/           # Proyecto principal (settings, urls)
├── personas/       # App de usuarios y roles
├── guardias/       # App de gestión de guardias
├── asistencia/     # App de asistencia y licencias
└── auditoria/      # App de auditoría
```

**Patrón Arquitectónico**: Database-First con modelos Django `managed = False`

---

### Django REST Framework 3.14.0+
**Propósito**: Construcción de API RESTful

**Características**:
- **Serializers**: Serialización/deserialización de datos a JSON
- **ViewSets**: Vistas basadas en clases para operaciones CRUD
- **Routers**: Routing automático de URLs para APIs
- **Authentication**: Sistema de autenticación extensible
- **Permissions**: Control de acceso granular por endpoint
- **Browsable API**: API navegable desde navegador (útil en desarrollo)

**Implementación en GIGA**:
- API RESTful completa expuesta en `/api/`
- Autenticación basada en sesiones y tokens
- Serializers personalizados para cada modelo
- ViewSets con custom actions (`@action`)

---

### psycopg2-binary 2.9.0+
**Propósito**: Adaptador de PostgreSQL para Python

**Características**:
- **Driver nativo**: Comunicación directa con PostgreSQL
- **Performance**: Conexiones optimizadas y pooling
- **Tipos nativos**: Soporte completo de tipos PostgreSQL
- **Binary**: Versión pre-compilada para instalación rápida

**Uso**: Conexión ORM de Django con base de datos PostgreSQL

---

### Gunicorn 20.1.0+
**Propósito**: WSGI HTTP Server para producción

**Características**:
- **Pre-fork worker model**: Múltiples procesos worker para concurrencia
- **Performance**: Manejo eficiente de requests concurrentes
- **Production-ready**: Diseñado para entornos de producción
- **Compatible**: WSGI compliant para apps Django

**Configuración típica**:
```bash
gunicorn giga.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

### django-cors-headers 4.0.0+
**Propósito**: Manejo de Cross-Origin Resource Sharing (CORS)

**Características**:
- **Middleware**: Integrado como middleware de Django
- **Configuración**: Control granular de orígenes permitidos
- **Headers**: Gestión de headers CORS automática

**Necesidad**: Permite que el frontend (puerto 3000) acceda al backend (puerto 8000) en desarrollo

---

### WhiteNoise 6.4.0+
**Propósito**: Servir archivos estáticos en producción

**Características**:
- **Middleware**: Sirve static files directamente desde Django
- **Compression**: Gzip automático de archivos estáticos
- **Caching**: Headers de caché optimizados
- **CDN-friendly**: Compatible con CDNs

**Uso**: Servir CSS, JS, imágenes compiladas del frontend

---

### ReportLab 4.0.0+
**Propósito**: Generación de documentos PDF

**Características**:
- **PDF nativo**: Creación programática de PDFs
- **Layouts**: Control total sobre diseño y formato
- **Tablas**: Generación de tablas con estilos
- **Gráficos**: Soporte para gráficos y visualizaciones

**Uso en GIGA**:
- Reportes institucionales de guardias
- Reportes de asistencia administrativa
- Comprobantes de compensaciones
- Formatos con encabezados UNTDF

---

### openpyxl 3.1.0+
**Propósito**: Lectura y escritura de archivos Excel (xlsx)

**Características**:
- **Excel 2010+**: Soporte completo de formato .xlsx
- **Estilos**: Formateo de celdas (fuentes, colores, bordes)
- **Fórmulas**: Preservación y creación de fórmulas
- **Performance**: Optimizado para archivos grandes

**Uso en GIGA**:
- Exportación de reportes a Excel
- Planillas de guardias mensuales
- Reportes de asistencia para análisis

---

## 💾 Base de Datos

### PostgreSQL 16 Alpine
**Propósito**: Sistema de gestión de base de datos relacional (RDBMS)

**Características**:
- **ACID**: Transacciones con garantías ACID completas
- **Extensiones**: PostGIS, pg_trgm, etc. (disponibles si se requieren)
- **JSON**: Soporte nativo de tipos JSON/JSONB
- **Performance**: Índices avanzados (B-tree, Hash, GiST, GIN)
- **Replicación**: Soporte de replicación master-slave
- **Alpine**: Imagen Docker ligera (< 50MB vs > 300MB)

**Configuración en GIGA**:
- **Base de datos**: `giga`
- **Usuario**: `giga_user`
- **Puerto**: 5432
- **Volumen persistente**: `postgres_data`

**Esquema**:
- 15+ tablas principales
- Foreign keys con constraints
- Índices en campos de búsqueda frecuente
- Triggers para auditoría (opcional)

**Justificación**: PostgreSQL elegido por su robustez, soporte de JSON para campos flexibles, y excelente rendimiento con datasets gubernamentales de tamaño medio.

---

## 🐳 Infraestructura y Deployment

### Docker
**Propósito**: Containerización de aplicaciones

**Características**:
- **Aislamiento**: Cada servicio en contenedor independiente
- **Portabilidad**: "Build once, run anywhere"
- **Reproducibilidad**: Entorno consistente en desarrollo/producción
- **Resource Management**: Control de CPU y memoria por contenedor

**Contenedores en GIGA**:
1. `giga-postgres` - Base de datos PostgreSQL
2. `giga-django` - Backend Django
3. `giga-frontend` - Frontend SvelteKit
4. `giga-nginx` - Reverse proxy
5. `giga-minio` - Object storage
6. `giga-n8n` - Workflow automation

---

### Docker Compose 3.8
**Propósito**: Orquestación multi-contenedor

**Características**:
- **Declarativo**: Configuración en YAML
- **Redes**: Networking automático entre servicios
- **Volúmenes**: Persistencia de datos
- **Dependencias**: Orden de inicio con `depends_on`
- **Health Checks**: Monitoreo de salud de servicios

**Servicios Definidos**:
```yaml
services:
  postgres     # Base de datos
  backend      # API Django
  frontend     # App SvelteKit
  nginx        # Reverse proxy
  minio        # Object storage
  n8n          # Workflow automation
```

**Comandos principales**:
```bash
docker-compose up -d          # Iniciar todos los servicios
docker-compose down           # Detener todos los servicios
docker-compose logs -f [service]  # Ver logs
docker-compose restart [service]  # Reiniciar servicio
```

---

### NGINX
**Propósito**: Reverse proxy y balanceador de carga

**Características**:
- **HTTP Server**: Servir contenido estático
- **Reverse Proxy**: Enrutamiento de requests a backend/frontend
- **Load Balancing**: Distribución de carga entre workers
- **SSL/TLS**: Terminación SSL (configuración futura)
- **Caching**: Caché de respuestas HTTP
- **Compression**: Gzip automático

**Configuración en GIGA**:
- **Puerto 80**: Punto de entrada principal
- **Puerto 8080**: Acceso directo a backend (desarrollo)
- **Rutas**:
  - `/api/` → Backend Django (puerto 8000)
  - `/` → Frontend SvelteKit (puerto 3000)
  - `/static/` → Archivos estáticos
  - `/media/` → Archivos subidos por usuarios

**Beneficios**:
- Single entry point para toda la aplicación
- Manejo eficiente de archivos estáticos
- Preparado para escalamiento horizontal

---

## 🔧 Servicios Auxiliares

### MinIO
**Propósito**: Object storage S3-compatible

**Características**:
- **S3 API**: Compatible con Amazon S3
- **High Performance**: Diseñado para velocidad
- **Distributed**: Soporte de clustering
- **Erasure Coding**: Protección de datos

**Uso Potencial en GIGA**:
- Almacenamiento de documentos adjuntos
- Respaldos de reportes generados
- Archivos multimedia
- Logs y auditoría extendida

**Puertos**:
- 9000: API S3
- 9090: Consola administrativa

---

### n8n
**Propósito**: Workflow automation (Similar a Zapier/Make)

**Características**:
- **Visual Workflow Editor**: Editor drag-and-drop de workflows
- **Integrations**: 200+ integraciones con servicios externos
- **Self-hosted**: Control total sobre datos
- **Webhooks**: Triggers HTTP para automatización
- **Scheduling**: Ejecución programada de workflows

**Uso Potencial en GIGA**:
- Automatización de notificaciones por email
- Integración con sistemas externos (RRHH, contabilidad)
- Generación automática de reportes periódicos
- Sincronización de datos con otros sistemas

**Puerto**: 5678 (interfaz web)

---

## 🔐 Control de Versiones y Colaboración

### Git
**Propósito**: Sistema de control de versiones distribuido

**Características**:
- **Branching**: Desarrollo paralelo con branches
- **Merging**: Integración de cambios
- **History**: Historial completo de cambios
- **Collaboration**: Trabajo en equipo eficiente

**Flujo de Trabajo**:
- `main`: Rama principal (producción)
- `develop`: Rama de desarrollo
- `feature/*`: Ramas de características
- `hotfix/*`: Correcciones urgentes

---

### GitHub
**Propósito**: Plataforma de hosting y colaboración de código

**Características**:
- **Remote Repository**: Repositorio central en la nube
- **Pull Requests**: Revisión de código antes de merge
- **Issues**: Tracking de bugs y features
- **Actions**: CI/CD automatizado (potencial uso)
- **Wiki**: Documentación del proyecto

**Repositorio GIGA**: Código compartido entre equipo de desarrollo

---

## 🛠️ Herramientas de Desarrollo

### Visual Studio Code (Inferido)
**Propósito**: IDE principal para desarrollo

**Extensiones Relevantes**:
- Svelte for VS Code
- Python
- Django
- Docker
- PostgreSQL

---

### PlantUML (Mencionado en documentación)
**Propósito**: Generación de diagramas UML

**Uso**:
- Diagramas de clases
- Diagramas de secuencia
- Documentación técnica

---

## 📊 Tecnologías por Capa

### Capa de Presentación
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Svelte | 5.41.0 | Framework UI |
| SvelteKit | 2.47.1 | Framework aplicación |
| Vite | 7.1.10 | Build tool |
| Axios | 1.13.1 | Cliente HTTP |
| @iconify/svelte | 4.2.0 | Iconos |

### Capa de Negocio
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Django | 4.2.0+ | Framework web |
| Django REST Framework | 3.14.0+ | API REST |
| Python | 3.x | Lenguaje backend |

### Capa de Datos
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| PostgreSQL | 16 Alpine | Base de datos |
| psycopg2-binary | 2.9.0+ | Driver PostgreSQL |

### Capa de Servicios
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| NGINX | Latest | Reverse proxy |
| Gunicorn | 20.1.0+ | WSGI server |
| MinIO | Latest | Object storage |
| n8n | Latest | Workflow automation |

### Infraestructura
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Docker | Latest | Containerización |
| Docker Compose | 3.8 | Orquestación |

### Utilidades
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| ReportLab | 4.0.0+ | Generación PDF |
| openpyxl | 3.1.0+ | Generación Excel |
| WhiteNoise | 6.4.0+ | Serving estáticos |
| django-cors-headers | 4.0.0+ | CORS |

---

## 🌐 Puertos y Accesos

| Servicio | Puerto | Acceso | Descripción |
|----------|--------|--------|-------------|
| **NGINX** | 80 | http://localhost | Punto de entrada principal |
| **NGINX** | 8080 | http://localhost:8080 | Acceso directo a backend |
| **Frontend** | 3000 | Interno | SvelteKit dev server |
| **Backend** | 8000 | Interno | Django dev server |
| **PostgreSQL** | 5432 | Interno/Host | Base de datos |
| **MinIO API** | 9000 | http://localhost:9000 | S3 API |
| **MinIO Console** | 9090 | http://localhost:9090 | Admin MinIO |
| **n8n** | 5678 | http://localhost:5678 | Workflow editor |

---

## 📦 Volúmenes Docker

| Volumen | Propósito | Persistencia |
|---------|-----------|--------------|
| `postgres_data` | Datos de PostgreSQL | Crítica |
| `static_volume` | Archivos estáticos compilados | Media |
| `media_volume` | Archivos subidos por usuarios | Alta |
| `frontend_node_modules` | Dependencias Node.js | No crítica |
| `minio_data` | Object storage | Alta |
| `n8n_data` | Workflows y configuración | Media |

---

## 🔄 Red Docker

**Nombre**: `giga-network`  
**Driver**: Bridge  
**Propósito**: Comunicación inter-contenedores

**Ventajas**:
- Aislamiento de red
- DNS automático (servicios accesibles por nombre)
- Seguridad mejorada
- Comunicación optimizada

---

## 🚀 Justificación del Stack

### ¿Por qué este stack?

**Separación de Concerns**:
- Frontend (Svelte) maneja solo UI/UX
- Backend (Django) maneja lógica de negocio y datos
- PostgreSQL maneja persistencia
- NGINX maneja routing y caching

**Escalabilidad**:
- Contenedores independientes permiten escalar componentes individualmente
- PostgreSQL soporta millones de registros
- NGINX puede balancear múltiples instancias de backend

**Mantenibilidad**:
- Frameworks maduros con comunidades activas
- Documentación extensa
- Patrones establecidos
- Código modular

**Performance**:
- Svelte: Bundle pequeño, runtime rápido
- Django: ORM optimizado, caché integrado
- PostgreSQL: Consultas eficientes con índices
- NGINX: Alto throughput

**Seguridad**:
- Django: Protecciones integradas contra vulnerabilidades comunes
- PostgreSQL: Row-level security, roles granulares
- Docker: Aislamiento de procesos
- NGINX: Rate limiting, protección DDoS

**Desarrollo**:
- Hot reload en frontend (Vite)
- Auto-reload en backend (Django runserver)
- Docker Compose: Entorno reproducible
- Volúmenes: Cambios reflejados instantáneamente

---

## 📝 Dependencias de Desarrollo

### Frontend
```json
{
  "@sveltejs/adapter-auto": "^7.0.0",
  "@sveltejs/adapter-node": "^5.4.0",
  "@sveltejs/kit": "^2.47.1",
  "@sveltejs/vite-plugin-svelte": "^6.2.1",
  "svelte-check": "^4.3.3",
  "typescript": "^5.9.3"
}
```

**Propósito**: Tooling de desarrollo, type checking, adapters para deployment

---

## ✅ Conclusión

El Stack Tecnológico del Sistema GIGA representa una **arquitectura moderna, escalable y mantenible** basada en:

- ✅ **Frameworks probados**: Django y SvelteKit con comunidades activas
- ✅ **Base de datos robusta**: PostgreSQL para datos relacionales complejos
- ✅ **Containerización**: Docker para portabilidad y consistencia
- ✅ **Arquitectura desacoplada**: Frontend/Backend separados con API REST
- ✅ **Servicios auxiliares**: MinIO y n8n para extensibilidad futura
- ✅ **Producción-ready**: Gunicorn, NGINX, health checks

**Nivel de Madurez**: ✅ Apto para producción gubernamental  
**Escalabilidad**: ✅ Preparado para 100+ usuarios concurrentes  
**Mantenibilidad**: ✅ Código modular con separación de concerns clara
