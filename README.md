# Sistema de Gestión Integral de Guardias y Asistencias (GIGA)

## Descripción del Proyecto
Sistema integral de gestión de recursos humanos, control de asistencia y guardias desarrollado con **Django REST Framework** (backend) y **SvelteKit** (frontend).

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (SvelteKit)                        │
│                     Puerto 5173                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Dashboard     │  │   Módulos       │  │   Servicios     │ │
│  │   Principal     │  │   Específicos   │  │   API           │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                            HTTP/JSON API
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (Django REST)                        │
│                     Puerto 8000                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API REST      │  │   6 Apps        │  │   Base de       │ │
│  │   Endpoints     │  │   Django        │  │   PostgreSQL    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Módulos del Sistema

### **Personas** - Gestión de Personal
- Agentes, áreas organizacionales y roles
- Cuentas de acceso con autenticación
- Estructura jerárquica organizacional

### **Asistencia** - Control Horario
- Registro diario de asistencias
- Marcas de entrada y salida
- Licencias y novedades con adjuntos
- Estados: presente, ausente, tardanza, etc.

### **Guardias** - Sistema de Turnos
- Cronogramas mensuales por área
- Asignación de guardias operativas/administrativas
- Cálculo automático de horas y plus salariales
- Gestión de feriados

### **Auditoría** - Trazabilidad
- Registro completo de todas las acciones
- Parámetros configurables del sistema
- Logs de auditoría con detalle de cambios

### **Reportes** - Información Gerencial
- Generación de reportes por agente/área/período
- Sistema de notificaciones automáticas
- Plantillas de correo personalizables
- Formatos PDF y Excel

### **Convenio IA** - Consultas Inteligentes
- Análisis de convenios colectivos de trabajo
- Consultas en lenguaje natural
- Respuestas con citas y referencias
- Índices de búsqueda BM25/Embeddings

## Tecnologías Utilizadas

### Backend
- **Django 5.2.7** - Framework web principal
- **Django REST Framework** - API REST
- **PostgreSQL 12+** - Base de datos
- **Python 3.13** - Lenguaje de programación

### Frontend
- **SvelteKit** - Framework frontend moderno
- **JavaScript** - Lenguaje de programación (100% JavaScript, sin TypeScript)
- **Axios** - Cliente HTTP
- **Vite** - Build tool y servidor de desarrollo

### Dependencias Adicionales
- **django-cors-headers** - Manejo de CORS
- **psycopg2-binary** - Driver PostgreSQL
- **python-decouple** - Variables de entorno

## Requisitos Previos

### Sistema
- **Python 3.13+**
- **Node.js 18+**
- **PostgreSQL 12+**
- **Git**

### Dependencias del Sistema

#### 🐧 **Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install python3-dev postgresql postgresql-contrib build-essential
```

#### 🐧 **Linux (CentOS/RHEL/Fedora)**
```bash
# CentOS/RHEL
sudo yum install python3-devel postgresql-devel gcc postgresql-server
# o Fedora
sudo dnf install python3-devel postgresql-devel gcc postgresql-server
```

#### 🍎 **macOS**
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install python postgresql pkg-config
```

#### 🪟 **Windows**
1. **Descargar e instalar:**
   - [Python 3.13+](https://www.python.org/downloads/windows/)
   - [Node.js 18+](https://nodejs.org/en/download/)
   - [PostgreSQL 12+](https://www.postgresql.org/download/windows/)
   - [Git](https://git-scm.com/download/win)
   - [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

2. **Configurar PATH** (añadir a las variables de entorno):
   - `C:\Python313\`
   - `C:\Python313\Scripts\`
   - `C:\Program Files\PostgreSQL\15\bin\`

## 🚀 Instalación Completa

### 1. Clonar y Configurar el Proyecto

#### 🐧 **Linux / 🍎 macOS**
```bash
# Clonar el repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# Configurar el backend
cd back
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 🪟 **Windows (PowerShell)**
```powershell
# Clonar el repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# Configurar el backend
cd back
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Crear entorno virtual de Python
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### 🪟 **Windows (CMD)**
```cmd
# Clonar el repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# Crear entorno virtual de Python
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2. Configurar Backend (Django)

#### 🐧 **Linux / 🍎 macOS**
```bash
# Ir al directorio del backend
cd back

# Instalar dependencias de Python
pip install -r requirements.txt

# O manualmente:
# pip install django djangorestframework psycopg2-binary django-cors-headers python-decouple

# El archivo .env ya está configurado para PostgreSQL
# Verificar configuración:
cat .env

# Crear base de datos PostgreSQL
sudo -u postgres psql
```

#### 🪟 **Windows (PowerShell)**
```powershell
# Ir al directorio del backend
cd back

# Instalar dependencias de Python
pip install -r requirements.txt

```

### 2. Configurar PostgreSQL

#### **Crear base de datos (todos los sistemas):**
```bash
# Acceder a PostgreSQL como usuario postgres
sudo -u postgres psql

# En el prompt de PostgreSQL, ejecutar:
CREATE DATABASE giga;
\q
```

### 3. Configurar Backend Django

#### **El archivo .env ya está configurado:**
```env
# Configuración de base de datos PostgreSQL
DB_NAME=giga
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

#### **Verificar conexión (no crear migraciones aún):**
```bash
# Linux/macOS (con entorno virtual activado)
python manage.py check

# # Windows (con entorno virtual activado)
python manage.py check
```

### 🗄️ **Desarrollo de Base de Datos**

#### **Antes de crear migraciones:**
1. **Revisa el diseño**: Consulta `/documentacion/db.puml` para el diseño completo
2. **Lee la guía de integración**: `/documentacion/integracionDB.md` 
3. **Define los modelos** en cada app según el diseño
4. **NO ejecutes** `makemigrations` hasta tener los modelos finales

#### **Comandos para desarrollo:**
```bash
# Verificar que no hay errores en los modelos (SIN crear migraciones)
python manage.py check

# Ver el SQL que generaría Django (sin ejecutar)
python manage.py sqlmigrate app_name 0001 --fake-initial

# Cuando estés listo para crear la DB real:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Configurar Frontend

# Windows
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 3. Configurar Frontend (SvelteKit)

#### 🐧 **Linux / 🍎 macOS**
```bash
# Ir al directorio del frontend
cd ../front

# Instalar dependencias de Node.js
npm install

# Crear archivo de variables de entorno
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000/api
EOF
```

#### 🪟 **Windows (PowerShell)**
```powershell
# Ir al directorio del frontend
cd ../front

# Instalar dependencias de Node.js
npm install

# Crear archivo de variables de entorno
@"
VITE_API_URL=http://localhost:8000/api
"@ | Out-File -FilePath .env -Encoding utf8
```

#### 🪟 **Windows (CMD)**
```cmd
# Ir al directorio del frontend
cd ../front

# Instalar dependencias de Node.js
npm install

# Crear archivo de variables de entorno
echo VITE_API_URL=http://localhost:8000/api > .env
```

## Ejecutar el Sistema

> **💡 Importante:** Ambos servidores deben estar ejecutándose simultáneamente para el funcionamiento completo del sistema.

### 1. Iniciar Backend

#### 🐧 **Linux / 🍎 macOS**
```bash
# Terminal 1
cd back
source venv/bin/activate  # Activar entorno virtual
python manage.py runserver
# Backend disponible en: http://localhost:8000
```

#### 🪟 **Windows (PowerShell)**
```powershell
# Terminal 1
cd back
.venv\Scripts\Activate.ps1  # Activar entorno virtual
python manage.py runserver
# Backend disponible en: http://localhost:8000
```

#### 🪟 **Windows (CMD)**
```cmd
# Terminal 1
cd back
.venv\Scripts\activate.bat  # Activar entorno virtual
python manage.py runserver
# Backend disponible en: http://localhost:8000
```

### 2. Iniciar Frontend

#### 🐧 **Linux / 🍎 macOS**
```bash
# Terminal 2
cd front
npm run dev
# Frontend disponible en: http://localhost:5173
```

#### 🪟 **Windows (PowerShell/CMD)**
```cmd
# Terminal 2
cd front
npm run dev
# Frontend disponible en: http://localhost:5173
```

### 3. Verificar Funcionamiento

1. **Backend**: Visitar http://localhost:8000/admin (usar superusuario creado)
2. **API**: Verificar http://localhost:8000/api/personas/agentes/
3. **Frontend**: Abrir http://localhost:5173

## URLs Importantes

### Backend (Puerto 8000)
- **Admin Django**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/
- **Personas**: http://localhost:8000/api/personas/
- **Asistencia**: http://localhost:8000/api/asistencia/
- **Guardias**: http://localhost:8000/api/guardias/
- **Reportes**: http://localhost:8000/api/reportes/
- **Convenio IA**: http://localhost:8000/api/convenio-ia/
- **Auditoría**: http://localhost:8000/api/auditoria/

### Frontend (Puerto 5173)
- **Dashboard**: http://localhost:5173

## Estructura del Proyecto

```
giga/
├── back/                          # Backend Django
│   ├── manage.py
│   ├── .env                      # Variables de entorno backend
│   ├── sistema_horario/          # Configuración principal
│   ├── personas/                 # App gestión de personal
│   ├── asistencia/              # App control de asistencia
│   ├── guardias/                # App sistema de guardias
│   ├── auditoria/               # App auditoría y parámetros
│   ├── reportes/                # App reportes y notificaciones
│   ├── convenio_ia/             # App consultas IA convenios
│   ├── logs/                    # Archivos de log
│   └── media/                   # Archivos subidos
├── front/                       # Frontend SvelteKit
│   ├── package.json
│   ├── .env                     # Variables de entorno frontend
│   ├── src/
│   │   ├── lib/                 # Librerías (API, servicios)
│   │   └── routes/              # Páginas y rutas
│   └── static/                  # Archivos estáticos
├── diagrama/                    # Diagrama UML original
│   └── clases.puml
└── README.md                    # Este archivo
```

## Comandos Útiles

### Backend
```bash
# Crear nueva migración
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar shell interactivo
python manage.py shell

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Frontend
```bash
# Instalar nueva dependencia
npm install nombre-paquete

# Actualizar dependencias
npm update

# Build para producción
npm run build

# Previsualizar build de producción
npm run preview
```

## Solución de Problemas Comunes

### Error de conexión a MySQL

#### 🐧 **Linux**
```bash
# Verificar que MySQL esté ejecutándose
sudo systemctl status mysql

# Reiniciar MySQL si es necesario
sudo systemctl restart mysql

# Iniciar MySQL si no está ejecutándose
sudo systemctl start mysql
```

#### 🍎 **macOS**
```bash
# Verificar estado de MySQL
brew services list | grep mysql

# Iniciar MySQL
brew services start mysql

# Reiniciar MySQL
brew services restart mysql
```

#### 🪟 **Windows**
```cmd
# Verificar servicios (ejecutar como Administrador)
sc query MySQL80

# Iniciar MySQL
net start MySQL80

# Reiniciar MySQL
net stop MySQL80
net start MySQL80
```

### Error de entorno virtual

#### 🐧 **Linux / 🍎 macOS**
```bash
# Asegurarse de que el entorno virtual esté activo
source .venv/bin/activate
```

#### 🪟 **Windows (PowerShell)**
```powershell
# Asegurarse de que el entorno virtual esté activo
.venv\Scripts\Activate.ps1
```

#### 🪟 **Windows (CMD)**
```cmd
# Asegurarse de que el entorno virtual esté activo
.venv\Scripts\activate.bat
```

### Error CORS en el frontend
- Verificar que el backend esté ejecutándose en el puerto 8000
- Confirmar que la variable `VITE_API_URL` esté configurada correctamente

### Error de instalación de mysqlclient

#### 🐧 **Linux**
```bash
# Si falla la instalación de mysqlclient
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

#### 🍎 **macOS**
```bash
# Si falla la instalación de mysqlclient
brew install mysql-client
export PATH="/usr/local/opt/mysql-client/bin:$PATH"
pip install mysqlclient
```

#### 🪟 **Windows**
```cmd
# Alternativa si mysqlclient falla
pip install PyMySQL
# Luego añadir en settings.py:
# import pymysql
# pymysql.install_as_MySQLdb()
```

### Error de migraciones
```bash
# Resetear migraciones si es necesario (todos los sistemas)
python manage.py migrate --fake-initial
```

### Error de permisos en Windows
- Ejecutar PowerShell o CMD **como Administrador**
- Configurar política de ejecución en PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Estado de Desarrollo

### Completado
- Estructura completa del backend con 6 apps
- Modelos basados en diagrama UML
- API REST completa con todos los endpoints
- Configuración MySQL
- Frontend básico con SvelteKit
- Integración backend-frontend
- Sistema de autenticación
- Configuración CORS
- Documentación completa