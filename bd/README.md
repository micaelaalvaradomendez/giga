# 🐘 PostgreSQL Database - GIGA

Este directorio contiene la configuración completa de PostgreSQL para el proyecto GIGA.

## 📋 Configuración

### **Especificaciones**
- **PostgreSQL**: 16-alpine
- **Puerto**: 5432
- **Base de datos**: `giga`
- **Usuario**: `giga_user`
- **Contraseña**: `giga2025`
- **Codificación**: UTF-8
- **Locale**: es_AR.UTF-8 (Argentina)
- **Zona horaria**: America/Argentina/Buenos_Aires

### **Estructura del directorio**
```
bd/
├── Dockerfile                 # Imagen personalizada de PostgreSQL
├── docker-compose.yml         # Configuración de servicios
├── postgresql.conf           # Configuración de PostgreSQL
├── pg_hba.conf              # Configuración de autenticación
├── db-utils.sh              # Script de utilidades
├── .env.example             # Variables de entorno de ejemplo
├── init-scripts/            # Scripts de inicialización
│   ├── 01-init-database.sh  # Configuración inicial
│   └── 02-setup-functions.sql # Funciones y configuraciones
├── backups/                 # Directorio para backups
├── logs/                    # Logs de PostgreSQL
└── README.md               # Esta documentación
```

## 🚀 Inicio Rápido

### **1. Iniciar la base de datos**
```bash
# Usando docker-compose directamente
docker-compose up -d postgres

# O usando el script de utilidades
./db-utils.sh start
```

### **2. Verificar que funciona**
```bash
./db-utils.sh status
```

### **3. Conectar a la base de datos**
```bash
./db-utils.sh shell
```

## 🛠️ Script de Utilidades

El script `db-utils.sh` proporciona comandos fáciles para manejar la base de datos:

```bash
# Comandos básicos
./db-utils.sh start          # Iniciar servicios
./db-utils.sh stop           # Detener servicios  
./db-utils.sh restart        # Reiniciar servicios
./db-utils.sh status         # Estado de servicios
./db-utils.sh logs           # Ver logs

# Conexión y administración
./db-utils.sh shell          # Conectar con psql
./db-utils.sh admin          # Iniciar PgAdmin (puerto 8080)

# Backups
./db-utils.sh backup         # Crear backup
./db-utils.sh restore <file> # Restaurar backup

# Mantenimiento
./db-utils.sh build          # Construir imagen
./db-utils.sh reset          # Resetear DB (⚠️ DESTRUCTIVO)
./db-utils.sh help           # Ayuda completa
```

## 🔧 Configuración Manual

### **Variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar según necesidades
nano .env
```

### **Conexión desde aplicaciones**
```bash
# URL de conexión
postgresql://giga_user:giga2025@localhost:5432/giga

# Variables individuales
DB_HOST=localhost
DB_PORT=5432
DB_NAME=giga
DB_USER=giga_user
DB_PASSWORD=giga2025
```

## 🎛️ PgAdmin (Opcional)

Para administración gráfica, puedes iniciar PgAdmin:

```bash
./db-utils.sh admin
```

**Acceso:**
- **URL**: http://localhost:8080
- **Usuario**: admin@giga.local
- **Contraseña**: admin2025

**Configuración del servidor en PgAdmin:**
- **Host**: postgres (nombre del contenedor)
- **Puerto**: 5432
- **Base de datos**: giga
- **Usuario**: giga_user
- **Contraseña**: giga2025

## 💾 Backups

### **Crear backup automático**
```bash
./db-utils.sh backup
```

Los backups se guardan en `./backups/` con timestamp y se comprimen automáticamente.

### **Restaurar backup**
```bash
./db-utils.sh restore ./backups/giga_backup_20251030_150000.sql.gz
```

### **Backup programado (opcional)**
Agregar a crontab para backups automáticos:
```bash
# Backup diario a las 2:00 AM
0 2 * * * cd /ruta/al/proyecto/bd && ./db-utils.sh backup
```

## 🔒 Seguridad

### **Producción**
⚠️ **IMPORTANTE**: Antes de ir a producción:

1. **Cambiar contraseñas por defecto**
2. **Configurar `pg_hba.conf` para IPs específicas**
3. **Habilitar SSL/TLS**
4. **Configurar firewall**
5. **Establecer backups regulares**

### **Configuración de SSL (Producción)**
```bash
# Generar certificados
openssl req -new -x509 -days 365 -nodes -text -out server.crt -keyout server.key

# Configurar en postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

## 🔍 Troubleshooting

### **Problemas comunes**

**Error de conexión:**
```bash
# Verificar que el contenedor esté corriendo
docker ps | grep postgres

# Ver logs para errores
./db-utils.sh logs
```

**Error de permisos:**
```bash
# Verificar permisos de archivos
ls -la init-scripts/
chmod +x init-scripts/*.sh
```

**Puerto ocupado:**
```bash
# Verificar qué proceso usa el puerto 5432
sudo netstat -tlnp | grep :5432
```

**Resetear completamente:**
```bash
# ⚠️ CUIDADO: Elimina todos los datos
./db-utils.sh reset
```

## 📚 Extensiones Incluidas

La base de datos incluye las siguientes extensiones:

- **uuid-ossp**: Generación de UUIDs
- **pgcrypto**: Funciones criptográficas  
- **unaccent**: Búsqueda sin acentos
- **pg_trgm**: Búsqueda de texto similaridad

## 🌐 Conexión desde otras aplicaciones

### **Node.js/JavaScript**
```javascript
// Con pg
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: 'postgresql://giga_user:giga2025@localhost:5432/giga'
});

// Con Prisma
DATABASE_URL="postgresql://giga_user:giga2025@localhost:5432/giga"
```

### **Python**
```python
# Con psycopg2
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="giga",
    user="giga_user",
    password="giga2025"
)

# Con SQLAlchemy
DATABASE_URL = "postgresql://giga_user:giga2025@localhost:5432/giga"
```

### **Docker Compose (otras aplicaciones)**
```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgresql://giga_user:giga2025@postgres:5432/giga
    depends_on:
      - postgres
    networks:
      - giga-network
```

## 📝 Notas de Desarrollo

- Los scripts de inicialización se ejecutan automáticamente al crear el contenedor
- Los datos se persisten en un volumen de Docker (`postgres_data`)
- Los logs se guardan en `./logs/`
- La configuración regional está optimizada para Argentina
- El timezone se configura automáticamente para Buenos Aires

## 🤝 Contribución

Para modificar la configuración:

1. Editar archivos de configuración
2. Reconstruir imagen: `./db-utils.sh build`
3. Reiniciar servicios: `./db-utils.sh restart`

---

**🔗 Conexión rápida:**
```bash
postgresql://giga_user:giga2025@localhost:5432/giga
```