# Backend - Sistema GIGA

## Descripción
Backend desarrollado en **Django** con **Django REST Framework** que proporciona una API REST completa para el Sistema de Gestión Integral de Guardias y Asistencias (GIGA). La base de datos utilizada es **PostgreSQL**.
Está preparado para desarrollo y listo para integrar con el frontend **SvelteKit**.

## Arquitectura del Proyecto

### Estructura de Apps

El proyecto está dividido en 6 aplicaciones Django, cada una basada en los paquetes del diagrama UML:

#### 1. **personas** - Gestión de Personal
**Propósito**: Manejo de agentes, áreas organizacionales, roles y cuentas de acceso.

**Modelos principales**:
- `Area`: Áreas de la organización con código, nombre y descripción
- `Agente`: Empleados con legajo, datos personales y área asignada
- `Rol`: Roles del sistema con permisos JSON
- `CuentaAcceso`: Cuentas de acceso vinculadas a agentes con roles

**Endpoints**:
- `/api/personas/agentes/` - CRUD de agentes
- `/api/personas/areas/` - CRUD de áreas
- `/api/personas/roles/` - CRUD de roles
- `/api/personas/cuentas-acceso/` - CRUD de cuentas

#### 2. **asistencia** - Control de Asistencia
**Propósito**: Registro y control de asistencia diaria, marcas de entrada/salida, licencias y novedades.

**Modelos principales**:
- `Asistencia`: Registro diario con estado (presente, ausente, tardanza, etc.)
- `Marca`: Marcas individuales de entrada/salida con validación
- `LicenciaONovedad`: Clase abstracta base para solicitudes
- `Licencia`: Licencias (vacaciones, enfermedad, personal, estudio)
- `Novedad`: Novedades (médica, familiar, capacitación)
- `Adjunto`: Archivos adjuntos a licencias/novedades

**Endpoints**:
- `/api/asistencia/asistencias/` - CRUD de asistencias
- `/api/asistencia/marcas/` - CRUD de marcas
- `/api/asistencia/licencias/` - CRUD de licencias
- `/api/asistencia/novedades/` - CRUD de novedades

#### 3. **guardias** - Sistema de Guardias
**Propósito**: Gestión de cronogramas de guardias, asignación de turnos y cálculo de plus.

**Modelos principales**:
- `CronogramaGuardias`: Cronogramas mensuales por área
- `Guardia`: Guardias individuales (operativas/administrativas)
- `HorasGuardias`: Resumen mensual de horas por agente
- `Feriado`: Días feriados que afectan guardias
- `ReglaPlus`: Reglas para cálculo de plus salarial
- `AsignacionPlus`: Asignaciones calculadas de plus

**Endpoints**:
- `/api/guardias/cronogramas/` - CRUD de cronogramas
- `/api/guardias/guardias/` - CRUD de guardias
- `/api/guardias/horas-guardias/` - Consulta de resúmenes
- `/api/guardias/feriados/` - CRUD de feriados

#### 4. **auditoria** - Auditoría y Parámetros
**Propósito**: Registro de auditoría del sistema y configuración de parámetros operativos.

**Modelos principales**:
- `ParametrosControlHorario`: Configuración de ventanas de marcación y tolerancias
- `RegistroAuditoria`: Log completo de todas las acciones del sistema

**Endpoints**:
- `/api/auditoria/parametros/` - CRUD de parámetros
- `/api/auditoria/registros/` - Consulta de registros (solo lectura)

#### 5. **reportes** - Reportes y Notificaciones
**Propósito**: Generación de reportes y sistema de notificaciones por email.

**Modelos principales**:
- `Reporte`: Reportes generados (individual, área, dirección, consolidado)
- `Notificacion`: Notificaciones del sistema y usuarios
- `PlantillaCorreo`: Plantillas para emails automáticos
- `EnvioLoteNotificaciones`: Envíos masivos de notificaciones

**Endpoints**:
- `/api/reportes/reportes/` - CRUD de reportes
- `/api/reportes/notificaciones/` - CRUD de notificaciones
- `/api/reportes/plantillas-correo/` - CRUD de plantillas

#### 6. **convenio_ia** - IA para Convenios
**Propósito**: Sistema de consultas inteligentes sobre convenios colectivos de trabajo.

**Modelos principales**:
- `Convenio`: Convenios colectivos con versionado
- `IndiceConvenio`: Índices de búsqueda (BM25/Embeddings)
- `ConsultaConvenio`: Historial de consultas con respuestas

**Endpoints**:
- `/api/convenio-ia/convenios/` - CRUD de convenios
- `/api/convenio-ia/consultas/` - Historial de consultas
- `/api/convenio-ia/consultar/` - Endpoint para realizar consultas

## Configuración Técnica

### Base de Datos
- **Motor**: PostgreSQL 12+
- **Encoding**: UTF-8
- **Configuración**: Conexiones persistentes y health checks habilitados

### Autenticación y Permisos
- **Django REST Framework** con autenticación por Token y Sesión
- **Permisos**: IsAuthenticated por defecto
- **CORS**: Configurado para frontend en puerto 5173

### APIs y Serialización
- **Paginación**: 20 elementos por página
- **Serializers**: Incluyen información relacionada (nombres, etc.)
- **Response Format**: JSON estándar

### Logging y Auditoría
- **Logs**: Almacenados en `logs/django.log`
- **Auditoría**: Registro automático de todas las operaciones CRUD
- **Timezone**: America/Argentina/Buenos_Aires

## Variables de Entorno

El archivo `.env` debe contener:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta
DB_NAME=giga
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Instalación y Configuración

### Requisitos Previos

#### 🐧 **Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install python3-dev postgresql postgresql-contrib build-essential
```

#### 🍎 **macOS**
```bash
brew install python postgresql
```

#### 🪟 **Windows**
- Instalar [Python 3.13+](https://www.python.org/downloads/windows/) ✅
- Instalar [PostgreSQL 12+](https://www.postgresql.org/download/windows/) ✅
- Instalar [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) ✅

### Configuración del Entorno

#### 🐧 **Linux / 🍎 macOS**
```bash
# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 🪟 **Windows (PowerShell)**
```powershell
# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

#### 🪟 **Windows (CMD)**
```cmd
# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

## Comandos Importantes

### Desarrollo (todos los sistemas)
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear app nueva
python manage.py startapp nombre_app

# Shell interactivo de Django
python manage.py shell

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Base de Datos PostgreSQL

#### 🐧 **Linux**
```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql

# Acceder a PostgreSQL
sudo -u postgres psql
```

#### 🍎 **macOS**
```bash
# Iniciar PostgreSQL
brew services start postgresql

# Acceder a PostgreSQL
psql postgres
```

#### 🪟 **Windows**
```cmd
# Acceder a PostgreSQL
psql -U postgres
```

#### Crear Base de Datos (todos los sistemas)
```sql
CREATE DATABASE giga;
\l
\q
```

## Estado del Desarrollo

### Completado
- Estructura completa de modelos base
- APIs REST básicas para todas las apps
- Configuración de base de datos PostgreSQL
- Sistema de autenticación
- Configuración CORS
- Serializers con información relacionada
- Entorno virtual configurado

### Pendiente (Para Desarrollo)
- Definir modelos finales según `documentacion/db.puml`
- Crear migraciones (NO creadas intencionalmente)
- Implementar lógica de negocio específica

## Dependencias Principales

- **Django 5.2.7**: Framework web
- **djangorestframework**: API REST
- **psycopg2-binary**: Conector PostgreSQL
- **django-cors-headers**: Manejo de CORS
- **python-decouple**: Variables de entorno

## 🎯 Próximos Pasos

1. **Revisar diseño**: `../documentacion/db.puml`
2. **Leer guía**: `../documentacion/integracionDB.md`
3. **Definir modelos** según el diseño
4. **Crear migraciones**: `python manage.py makemigrations`
5. **Aplicar migraciones**: `python manage.py migrate`

# Admin (borrar cuando vayamaos a entregar esta app)

Usuario: admin
Correo: seradmin2025@mail.com
clave: 123456
