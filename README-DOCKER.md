# 🚀 GIGA - Sistema de Gestión con Docker

Sistema de gestión integral con arquitectura de microservicios usando Docker, Nginx, Django y SvelteKit.

## 📋 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Prerequisitos](#-prerequisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Desarrollo](#-desarrollo)
- [Producción](#-producción)
- [Comandos Útiles](#-comandos-útiles)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Configuración](#-configuración)
- [Troubleshooting](#-troubleshooting)

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│     NGINX       │    │   SvelteKit     │    │    Django       │
│  (Proxy/Load)   │◄──►│   (Frontend)    │◄──►│   (Backend)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Static/Media  │    │   Node Modules  │    │   PostgreSQL    │
│    (Volumes)    │    │   (pnpm cache)  │    │   (Database)    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tecnologías

### Backend
- **Django 4.x**: Framework web de Python
- **PostgreSQL 16**: Base de datos relacional
- **Gunicorn**: Servidor WSGI para producción
- **Django REST Framework**: API RESTful

### Frontend
- **SvelteKit**: Framework de JavaScript
- **Vite**: Bundler y servidor de desarrollo
- **pnpm**: Gestor de paquetes (más rápido que npm)
- **Tailwind CSS**: Framework de CSS

### DevOps
- **Docker & Docker Compose**: Contenedorización
- **Nginx**: Proxy reverso y servidor web
- **Multi-stage builds**: Optimización de imágenes

## 📋 Prerequisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git

## ⚡ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/giga.git
cd giga
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuraciones (opcional para desarrollo)
nano .env
```

### 3. Iniciar en modo desarrollo

```bash
# Dar permisos al script de gestión
chmod +x manage.sh

# Iniciar entorno de desarrollo
./manage.sh dev
```

## 🎮 Uso

### Script de Gestión

El proyecto incluye un script de gestión `manage.sh` que simplifica todas las operaciones:

```bash
# Ver ayuda completa
./manage.sh help

# Comandos principales
./manage.sh dev          # Iniciar desarrollo
./manage.sh prod         # Iniciar producción
./manage.sh stop         # Detener servicios
./manage.sh restart      # Reiniciar servicios
./manage.sh status       # Ver estado
```

### Acceso a los Servicios

#### Desarrollo
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Base de Datos**: localhost:5434

#### Producción
- **Aplicación**: http://localhost
- **Admin Django**: http://localhost/admin
- **API**: http://localhost/api

## 🔧 Desarrollo

### Iniciar entorno de desarrollo

```bash
./manage.sh dev
```

Esto inicia:
- PostgreSQL en puerto 5434
- Django en puerto 8000 con hot-reload
- SvelteKit en puerto 5173 con HMR
- Volúmenes montados para desarrollo en tiempo real

### Comandos de desarrollo útiles

```bash
# Ver logs en tiempo real
./manage.sh logs
./manage.sh logs backend    # Solo backend
./manage.sh logs frontend   # Solo frontend

# Acceder al shell de Django
./manage.sh shell

# Ejecutar migraciones
./manage.sh migrate

# Comandos pnpm en el frontend
./manage.sh pnpm install
./manage.sh pnpm run build
./manage.sh pnpm add axios

# Acceder a la base de datos
./manage.sh db-shell
```

### Estructura para desarrollo

```bash
# Archivos que se sincronizan automáticamente:
./back/          # Código Django
./front/         # Código SvelteKit
./nginx/conf.d/  # Configuración Nginx
```

## 🚀 Producción

### Configuración de producción

1. **Actualizar variables de entorno**:

```bash
# En .env
DEBUG=0
SECRET_KEY=tu-clave-super-segura-aqui
DB_PASSWORD=contraseña-muy-segura
NODE_ENV=production
```

2. **Configurar dominio** (opcional):

```bash
# En nginx/conf.d/default.conf
server_name tudominio.com www.tudominio.com;
```

3. **Configurar SSL** (recomendado):

```bash
# Agregar certificados SSL
mkdir -p nginx/ssl
# Copiar certificados a nginx/ssl/
```

### Iniciar producción

```bash
./manage.sh prod
```

Esto inicia:
- PostgreSQL optimizado
- Django con Gunicorn
- SvelteKit pre-compilado
- Nginx como proxy reverso
- Volúmenes persistentes para datos

### Comandos de producción

```bash
# Recopilar archivos estáticos
./manage.sh collectstatic

# Ver logs de producción
./manage.sh logs

# Reiniciar solo producción
./manage.sh restart prod
```

## 📁 Estructura del Proyecto

```
giga/
├── 📁 back/                    # Backend Django
│   ├── 📁 docker/              # Scripts de Docker
│   ├── 📁 giga/                # Configuración Django
│   ├── 📁 personas/            # App de usuarios
│   ├── 📁 asistencia/          # App de asistencias
│   ├── 📁 guardias/            # App de guardias
│   ├── 📄 Dockerfile           # Multi-stage build
│   └── 📄 requirements.txt     # Dependencias Python
├── 📁 front/                   # Frontend SvelteKit
│   ├── 📁 src/                 # Código fuente
│   │   ├── 📁 routes/          # Páginas
│   │   ├── 📁 lib/             # Componentes y utilidades
│   │   └── 📄 app.html         # Template base
│   ├── 📄 Dockerfile           # Multi-stage build
│   ├── 📄 package.json         # Configuración Node.js
│   └── 📄 pnpm-lock.yaml       # Lock file de pnpm
├── 📁 nginx/                   # Configuración Nginx
│   ├── 📁 conf.d/              # Configuraciones de sitio
│   ├── 📄 Dockerfile           # Imagen Nginx
│   └── 📄 nginx.conf           # Configuración principal
├── 📄 docker-compose.yml       # Compose principal (con Nginx)
├── 📄 docker-compose.dev.yml   # Desarrollo (sin Nginx)
├── 📄 docker-compose.prod.yml  # Producción completa
├── 📄 manage.sh                # Script de gestión
├── 📄 .env.example             # Variables de entorno
└── 📄 README.md                # Documentación
```

## ⚙️ Configuración

### Variables de Entorno

Archivo `.env`:

```bash
# Base de datos
DB_NAME=giga
DB_USER=giga_user
DB_PASSWORD=tu_password_seguro

# Django
SECRET_KEY=tu_secret_key_muy_largo
DEBUG=1  # 0 para producción

# Frontend
NODE_ENV=development  # production para producción
VITE_API_BASE=http://localhost/api
```

### Configuración de Nginx

Archivo `nginx/conf.d/default.conf`:

- **Puerto 80**: Aplicación principal
- **Rutas /api/**: Backend Django
- **Rutas /admin/**: Admin Django
- **Rutas /static/ y /media/**: Archivos estáticos
- **Resto**: Frontend SvelteKit

### Personalizar configuración

```bash
# Modificar Nginx
nano nginx/conf.d/default.conf

# Modificar Django settings
nano back/giga/settings.py

# Modificar Vite config
nano front/vite.config.js
```

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Error de permisos

```bash
# Dar permisos al script
chmod +x manage.sh

# Problema con volúmenes
./manage.sh clean
./manage.sh dev
```

#### 2. Puerto ocupado

```bash
# Verificar puertos en uso
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :5173

# Cambiar puertos en docker-compose.*.yml
```

#### 3. Problemas con pnpm

```bash
# Limpiar cache de pnpm
./manage.sh pnpm store prune

# Reinstalar dependencias
./manage.sh pnpm install --force
```

#### 4. Base de datos no conecta

```bash
# Ver logs de la base de datos
./manage.sh logs db

# Recrear volúmenes
./manage.sh clean
```

### Logs y Debugging

```bash
# Logs generales
./manage.sh logs

# Logs específicos
./manage.sh logs backend
./manage.sh logs frontend
./manage.sh logs nginx
./manage.sh logs db

# Logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f
```

### Performance

#### Optimizaciones para producción

1. **Usar builds optimizados**
2. **Configurar Nginx caching**
3. **Usar CDN para estáticos**
4. **Configurar SSL/TLS**

#### Monitoreo

```bash
# Ver recursos utilizados
docker stats

# Ver estado de servicios
./manage.sh status
```

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `./manage.sh logs`
2. Verifica la configuración en `.env`
3. Intenta limpiar y reiniciar: `./manage.sh clean && ./manage.sh dev`

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**¡Listo para usar! 🎉**

Para empezar: `./manage.sh dev` y ve a http://localhost:5173