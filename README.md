# 🚀 GIGA - Sistema de Gestión Integral

Sistema completo de gestión para Protección Civil con frontend moderno, backend robusto y base de datos optimizada.

## ⚡ Inicio Rápido

### 1️⃣ Requisitos Previos

**Windows / macOS / Linux:**
- [Docker](https://docs.docker.com/get-docker/) (versión 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (versión 2.0+)
- [Git](https://git-scm.com/downloads)

### 2️⃣ Clonar el Proyecto

```bash
git clone <repository-url>
cd giga
```

### 3️⃣ Levantar el Sistema Completo

#### Opción A: Script Automatizado (Recomendado)

```bash
# Linux/macOS
./giga-system.sh dev

# Windows (PowerShell)
.\giga-system.ps1 dev

```

### Opción 2: Command Prompt (CMD)
```cmd
# Navegar al directorio del proyecto
cd C:\ruta\a\tu\proyecto\giga

# Ejecutar el script
giga-system.bat dev
```

#### Opción B: Docker Compose Manual

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4️⃣ Acceder al Sistema

Una vez iniciado, el sistema estará disponible en:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| 🌐 **Aplicación Principal** | [http://localhost](http://localhost) | Sistema completo via Nginx |
| 🎨 **Frontend** | [http://localhost:3000](http://localhost:3000) | Interfaz Svelte |
| ⚙️ **Backend API** | [http://localhost:8000](http://localhost:8000) | Django REST API |
| 📊 **Admin Django** | [http://localhost:8000/admin](http://localhost:8000/admin) | Panel administrativo |
| 📈 **Monitoreo** | [http://localhost:8080](http://localhost:8080) | Métricas Nginx |

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   Base de       │
│   (Svelte)      │◄──►│    (Django)      │◄──►│   Datos         │
│   Puerto 3000   │    │   Puerto 8000    │    │   (PostgreSQL)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                       ▲
         │                        │                       │
         └────────────────────────┼───────────────────────┘
                                  ▼
                    ┌─────────────────────────────┐
                    │         Nginx               │
                    │    (Proxy Reverso)          │
                    │     Puerto 80/8080          │
                    └─────────────────────────────┘
```

## 🎯 Funcionalidades Principales

### 👥 **Gestión de Personas** ✅ 
- Registro y administración de agentes
- Asignación de roles y áreas
- Perfiles completos con datos personales
- Autenticación con CUIL + DNI

### 📋 **Sistema de Guardias** 🚧
- Cronogramas de guardias automatizados
- Asignación de turnos
- Resúmenes mensuales

### ⏰ **Control de Asistencias** 🚧
- Registro de entradas y salidas
- Gestión de licencias
- Partes diarios de trabajo

### 📊 **Auditoría** 🚧
- Registro completo de cambios
- Trazabilidad de operaciones
- Logs de sistema

## 🔐 **Credenciales de Acceso**

El sistema usa **CUIL + DNI** para autenticación:

| Agente | CUIL | DNI (Contraseña) | Rol |
|--------|------|------------------|-----|
| Tayra Aguila | `27123456784` | `12345678` | Administrador |
| Micaela Alvarado | `27234567894` | `23456789` | Administrador |
| Cristian Garcia | `27345678904` | `34567890` | Director |
| Leandro Gomez | `27456789014` | `45678901` | Jefatura |
| Teresa Criniti | `27567890124` | `56789012` | Agente Avanzado |
| Pamela Frers | `27678901234` | `67890123` | Agente |

## 🛠️ **Credenciales de Servicios de Desarrollo**

Credenciales para acceder a los servicios adicionales en el entorno de desarrollo local. **No usar en producción.**

### MinIO (Almacenamiento de Objetos)

- **URL:** `http://localhost:9090`
- **Usuario:** `giga-user`
- **Contraseña:** `giga-password-change-me`

### n8n (Motor de Automatización)

- **URL:** `http://localhost:5678`
- **Nota:** La autenticación está deshabilitada por defecto en el entorno de desarrollo. No es necesario iniciar sesión.
- **Datos de la cuenta 'owner' (si se reactiva la autenticación):**
  - **Nombre:** `Admin`
  - **Apellido:** `Giga`
  - **Email:** `admin@giga.com`
  - **Contraseña:** `Admin123`

## 🛠️ Comandos de Gestión

### Script Principal Linux (`giga-system.sh`)

```bash
# Desarrollo completo
./giga-system.sh dev

# Gestión de servicios
./giga-system.sh start    # Iniciar todos
./giga-system.sh stop     # Detener todos
./giga-system.sh restart  # Reiniciar todos
./giga-system.sh status   # Ver estado

# Logs
./giga-system.sh logs              # Todos los logs
./giga-system.sh logs backend      # Solo Django
./giga-system.sh logs frontend     # Solo Svelte
./giga-system.sh logs postgres     # Solo BD

# Construcción selectiva
./giga-system.sh build-backend     # Solo backend
./giga-system.sh build-frontend    # Solo frontend
./giga-system.sh build-nginx       # Solo nginx

# Base de datos
./giga-system.sh db-shell          # Conectar a PostgreSQL
./giga-system.sh migrate           # Ejecutar migraciones

# Desarrollo
./giga-system.sh shell-backend     # Shell Django
./giga-system.sh shell-frontend    # Shell Svelte
```
### Script Principal windows (`giga-system.sh`)

```bash
# Desarrollo completo
.\giga-system.ps1 dev

# Ver logs específicos
.\giga-system.ps1 logs backend
.\giga-system.ps1 logs postgres

# Gestión básica
.\giga-system.ps1 start
.\giga-system.ps1 stop
.\giga-system.ps1 status

# Base de datos
.\giga-system.ps1 migrate
.\giga-system.ps1 db-shell
```

### Docker Compose Directo

```bash
# Ver servicios
docker-compose ps

# Logs específicos
docker-compose logs -f [servicio]

# Reiniciar servicio específico
docker-compose restart [servicio]

# Ejecutar comandos en contenedor
docker-compose exec backend python manage.py shell
docker-compose exec frontend npm run build
```

## 📊 Database First Strategy

El sistema utiliza una **estrategia Database First**:

- ✅ **Preserva** la base de datos existente
- ✅ **No modifica** estructuras de tablas existentes
- ✅ **Permite** operaciones CRUD completas
- ✅ **Mantiene** integridad referencial
- ✅ **Optimiza** consultas con JOINs eficientes

```python
# Todos los modelos Django están marcados como:
class Meta:
    managed = False  # Django NO administra la tabla
    db_table = 'tabla_existente'
```

## 🚨 Solución de Problemas

### Problema: Puertos en uso
```bash
# Ver qué proceso usa el puerto
lsof -i :80    # Linux/macOS
netstat -an | findstr :80  # Windows

# Cambiar puertos en docker-compose.yml
```

### Problema: Contenedores no inician
```bash
# Ver logs de error
docker-compose logs [servicio]

# Reconstruir sin caché
docker-compose build --no-cache

# Limpiar volúmenes
docker-compose down -v
```

### Problema: Base de datos no conecta
```bash
# Verificar estado PostgreSQL
docker-compose exec postgres pg_isready -U giga_user -d giga

# Reiniciar solo la base de datos
docker-compose restart postgres
```

## 📁 Estructura del Proyecto

```
giga/
├── 📁 back/                 # Backend Django
│   ├── 📁 personas/         # App gestión personas
│   ├── 📁 guardias/         # App gestión guardias
│   ├── 📁 asistencia/       # App control asistencias
│   ├── 📁 auditoria/        # App sistema auditoría
│   └── 📄 manage.py
├── 📁 front/                # Frontend Svelte
│   ├── 📁 src/
│   ├── 📄 package.json
│   └── 📄 vite.config.js
├── 📁 bd/                   # Scripts base de datos
│   └── 📁 init-scripts/
├── 📁 nginx/                # Configuración proxy
│   └── 📄 nginx.conf
├── 📄 docker-compose.yml    # Orquestación principal
├── 📄 giga-system.sh        # Script de gestión
└── 📄 README.md            
``

**💡 Tip:** Para un desarrollo óptimo, usa `./giga-system.sh dev` que incluye hot-reload automático y logs en tiempo real.

**🆘 Soporte:** Si encuentras problemas, revisa los logs con `./giga-system.sh logs` o abre un issue en el repositorio.
