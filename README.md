# Sistema de Control Horario y Guardias

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
│  │   Endpoints     │  │   Django        │  │   Datos MySQL   │ │
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
- **MySQL 8.x** - Base de datos
- **Python 3.13** - Lenguaje de programación

### Frontend
- **SvelteKit** - Framework frontend moderno
- **JavaScript** - Lenguaje de programación (100% JavaScript, sin TypeScript)
- **Axios** - Cliente HTTP
- **Vite** - Build tool y servidor de desarrollo

### Dependencias Adicionales
- **django-cors-headers** - Manejo de CORS
- **mysqlclient** - Driver MySQL
- **python-decouple** - Variables de entorno

## Requisitos Previos

### Sistema
- **Python 3.13+**
- **Node.js 18+**
- **MySQL 8.0+**
- **Git**

### Dependencias del Sistema (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3-dev default-libmysqlclient-dev build-essential mysql-server
```

## Instalación Completa

### 1. Clonar y Configurar el Proyecto

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd giga

# Crear entorno virtual de Python
python3 -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o en Windows: .venv\Scripts\activate
```

### 2. Configurar Backend (Django)

```bash
# Ir al directorio del backend
cd back

# Instalar dependencias de Python
pip install django djangorestframework mysqlclient django-cors-headers python-decouple

# Crear archivo de variables de entorno
cat > .env << EOF
DEBUG=True
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DB_NAME=sistema_horario
DB_USER=root
DB_PASSWORD=tu-password-mysql
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
EOF

# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE sistema_horario CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 3. Configurar Frontend (SvelteKit)

```bash
# Ir al directorio del frontend
cd ../front

# Instalar dependencias de Node.js
npm install

# Crear archivo de variables de entorno
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api
EOF
```

## Ejecutar el Sistema


Ambos servidores deben estar ejecutándose simultáneamente para el funcionamiento completo del sistema.

### 1. Iniciar Backend (Terminal 1)
```bash
cd back
source .venv/bin/activate  # Activar entorno virtual
python manage.py runserver
# Backend disponible en: http://localhost:8000
```

### 2. Iniciar Frontend (Terminal 2)
```bash
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
```bash
# Verificar que MySQL esté ejecutándose
sudo systemctl status mysql

# Reiniciar MySQL si es necesario
sudo systemctl restart mysql
```

### Error de permisos de Python
```bash
# Asegurarse de que el entorno virtual esté activo
source .venv/bin/activate
```

### Error CORS en el frontend
- Verificar que el backend esté ejecutándose en el puerto 8000
- Confirmar que la variable `VITE_API_URL` esté configurada correctamente

### Error de migraciones
```bash
# Resetear migraciones si es necesario
python manage.py migrate --fake-initial
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