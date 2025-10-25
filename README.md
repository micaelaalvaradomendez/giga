# GIGA - Sistema de Gestión Integral de Guardias y Asistencias

Sistema web para la gestión de recursos humanos, control de asistencia y guardias desarrollado con **Django REST Framework** (backend) y **SvelteKit** (frontend).

## Inicio Rápido

### Setup Automático
```bash
# Clonar repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# Levantar sistema (carga datos automáticamente)
sudo docker-compose up -d --build
```

### Si hay problemas después de `git pull`
```bash
./normalize_repo.sh
sudo docker-compose down -v && sudo docker-compose up -d --build
```

## URLs del Sistema

| Servicio | URL |
|----------|-----|
| **Aplicación Web** | http://localhost:5173 |
| **API Backend** | http://localhost:8000/api/ |
| **Admin Django** | http://localhost:8000/admin |

## Comandos Esenciales

```bash
# Ver estado de contenedores
sudo docker ps

# Ver logs si hay problemas
sudo docker logs giga_back
sudo docker logs giga_front

# Reiniciar servicios
sudo docker-compose restart

# Reset completo (si algo se rompe)
sudo docker-compose down -v
sudo docker-compose up -d --build

# Verificar datos cargados
docker exec giga_back python manage.py shell -c "
from personas.models import Usuario
print(f'Usuarios en sistema: {Usuario.objects.count()}')
"
```

## Gestión de Datos

### Datos Automáticos
Al hacer `docker compose up` se cargan automáticamente:
- **6 usuarios** con roles (Tayra y Micaela como Administradores)
- **5 roles** del sistema (Administrador, Director, Jefatura, Agente Avanzado, Agente)
- **1 área** organizacional (Secretaría de Protección Civil)
- **Licencias de ejemplo** para cada usuario

### Sincronizar Cambios
```bash
# Crear backup después de modificar datos
docker exec giga_back python manage.py export_data
git add data_backup/ && git commit -m "Update: nuevos datos"

# Después de git pull, los datos se actualizan automáticamente
docker-compose down && docker-compose up -d
```

## Tecnologías

- **Backend**: Django 5.2.7 + PostgreSQL 16
- **Frontend**: SvelteKit + JavaScript
- **Contenedores**: Docker + Docker Compose

## Funcionalidades

- **Personas**: Gestión de personal, áreas y roles
- **Asistencia**: Control horario y licencias
- **Guardias**: Sistema de turnos y cronogramas
- **Reportes**: Informes y notificaciones
- **Auditoría**: Trazabilidad de cambios
- **Convenio IA**: Consultas inteligentes sobre convenios

## Solución de Problemas

- **Backend no inicia**: `./normalize_repo.sh && docker-compose down -v && docker-compose up -d --build`
- **Puerto ocupado**: Cambiar puertos en `docker-compose.yml`
- **Login no funciona**: `docker-compose restart back`
- **Más ayuda**: Ver [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)

## Requisitos

- **Docker** y **Docker Compose**
- **Git**

### Instalar Docker
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: `sudo apt install docker.io docker-compose`


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

