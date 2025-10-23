# GIGA - Sistema de Gestión Integral de Guardias y Asistencias

Sistema web para la gestión de recursos humanos, control de asistencia y guardias desarrollado con **Django REST Framework** (backend) y **SvelteKit** (frontend).

## Inicio Rápido con Docker

### **NUEVO**: Setup Automático (Sin Problemas)

```bash
# 1. Clonar el repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# 2. Ejecutar setup automático
chmod +x setup.sh normalize_repo.sh
./setup.sh
```

**¿Problemas después de `git pull`?** (Típico en Windows):
```bash
# Solo ejecutar una vez si el backend no levanta
./normalize_repo.sh
git add . && git commit -m "fix: normalize line endings"
docker compose down -v && docker compose up -d --build
```

El setup automáticamente:
- Configura line endings (Windows/Linux)
- Crea archivos `.env` necesarios
- Construye contenedores sin conflictos
- Ejecuta migraciones de base de datos
- Crea usuarios de prueba
- Inicia todos los servicios

### Credenciales de Prueba

| CUIL | Contraseña | Rol |
|------|------------|-----|
| `27-12345678-4` | `12345678` | Administrador |
| `27-23456789-4` | `admin123` | Director |
| `27-34567890-4` | `admin123` | Jefatura |
| `27-45678901-4` | `admin123` | Agente Avanzado |
| `27-56789012-4` | `admin123` | Agente |
| `27-67890123-4` | `admin123` | Agente |

### Configuración Manual (Alternativa)

Si prefieres configurar paso a paso:

```bash
# 1. Preparar el entorno
chmod +x setup.sh normalize_repo.sh
./normalize_repo.sh  # Solo la primera vez

# 2. Configurar variables de entorno
cp .env.example .env
cp back/.env.example back/.env

# 3. Levantar servicios
docker-compose up -d --build

# 4. Ejecutar migraciones y crear usuarios
docker-compose exec back python manage.py migrate
# (Ver setup.sh para crear usuarios de prueba)
```

### Si Algo No Funciona

**Backend no levanta después de `git pull`**:
```bash
./normalize_repo.sh
docker compose down -v && docker compose build --no-cache && docker compose up -d
```

**Primera vez o problemas de permisos**:
```bash
chmod +x setup.sh normalize_repo.sh
sudo usermod -aG docker $USER  # Linux: agregar usuario a docker
# Reiniciar sesión después del usermod
```

**Puerto ocupado** - cambiar en `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Backend
  - "5174:5173"  # Frontend
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

## URLs de Acceso

| Servicio | URL | 
|----------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000/api/ |
| **Admin Django** | http://localhost:8000/admin |

## Comandos Útiles

```bash
# Ver si todo funciona
docker-compose ps

# Ver logs si hay problemas
docker-compose logs -f back    # Backend
docker-compose logs -f front   # Frontend

# Parar todo
docker-compose down

# Limpiar y reiniciar (si algo se rompe)
docker-compose down -v
docker-compose up -d --build
```

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

Si necesitas más ayuda, revisa [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) que tiene soluciones paso a paso para problemas comunes.

## Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request