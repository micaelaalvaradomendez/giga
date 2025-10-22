# GIGA - Sistema de Gestión Integral de Guardias y Asistencias

Sistema web para la gestión de recursos humanos, control de asistencia y guardias desarrollado con **Django REST Framework** (backend) y **SvelteKit** (frontend).

## ⚡ Inicio Rápido con Docker

```bash
# 1. Clonar el repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar todos los servicios
docker-compose up -d --build

# 4. ¡Listo! Acceder a:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Admin Django: http://localhost:8000/admin
```

## Funcionalidades

- **Personas**: Gestión de personal, áreas y roles
- **Asistencia**: Control horario y licencias  
- **Guardias**: Sistema de turnos y cronogramas
- **Reportes**: Informes y notificaciones
- **Auditoría**: Trazabilidad de cambios
- **Convenio IA**: Consultas inteligentes sobre convenios

## Stack Tecnológico

- **Backend**: Django 5.2.7 + Django REST Framework + PostgreSQL
- **Frontend**: SvelteKit + Vite + JavaScript
- **Contenedores**: Docker + Docker Compose
- **Base de datos**: PostgreSQL 16

## Requisitos

- **Docker** y **Docker Compose**
- **Git**

### Instalar Docker:
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: 
  ```bash
  # Ubuntu/Debian
  sudo apt update && sudo apt install docker.io docker-compose
  
  # CentOS/RHEL
  sudo yum install docker docker-compose
  ```

## Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f back    # Backend
docker-compose logs -f front   # Frontend
docker-compose logs -f db      # Base de datos

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes (CUIDADO: borra la BD)
docker-compose down -v

# Rebuildir los contenedores
docker-compose up -d --build

# Ejecutar comandos Django
docker-compose exec back python manage.py createsuperuser
docker-compose exec back python manage.py makemigrations
docker-compose exec back python manage.py migrate
```

## URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:5173 | Aplicación web principal |
| **Backend API** | http://localhost:8000/api/ | API REST |
| **Admin Django** | http://localhost:8000/admin | Panel de administración |
| **Base de datos** | `localhost:5434` | PostgreSQL (para clientes externos) |

## Estructura del Proyecto

```
giga/
├── docker-compose.yml         # Configuración Docker
├── .env.example              # Plantilla variables de entorno
├── DOCKER.md                 # Documentación Docker
├── back/                     # Backend Django
│   ├── Dockerfile
│   ├── personas/                # Gestión de personal
│   ├── asistencia/              # Control horario
│   ├── guardias/                # Sistema de guardias
│   ├── auditoria/               # Auditoría
│   ├── reportes/                # Reportes
│   └── convenio_ia/             # IA Convenios
├── front/                    # Frontend SvelteKit
│   ├── Dockerfile
│   └── src/routes/              # Páginas web
└── documentacion/            # Diseño y documentación
    ├── db.puml                  # Diseño de base de datos
    └── integracionDB.md         # Guía de implementación
```

## Solución de Problemas

### Puerto ocupado
```bash
# Si el puerto está en uso, cambiar en docker-compose.yml:
ports:
  - "8001:8000"  # Backend
  - "5174:5173"  # Frontend
  - "5435:5432"  # Base de datos
```

### Permisos en Linux
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión
```

### Limpiar Docker
```bash
# Si algo no funciona, limpiar y reiniciar
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

## Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request