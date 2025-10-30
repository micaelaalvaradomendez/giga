# 🐘 Base de Datos Aislada - PostgreSQL

Este directorio contiene la configuración completamente aislada de la base de datos PostgreSQL para el proyecto GIGA.

## 📁 Estructura

```
db/
├── Dockerfile              # Imagen personalizada de PostgreSQL
├── docker-compose.yml      # Configuración del servicio de BD
├── postgresql.conf         # Configuración personalizada de PostgreSQL
├── pg_hba.conf            # Configuración de autenticación
├── .env.example           # Variables de entorno de ejemplo
├── init/                  # Scripts de inicialización
│   └── 01-init-db.sh     # Script principal de inicialización
└── README.md              # Esta documentación
```

## 🚀 Uso Rápido

### Iniciar la base de datos
```bash
cd db
docker-compose up -d
```

### Detener la base de datos
```bash
cd db
docker-compose down
```

### Ver logs
```bash
cd db
docker-compose logs -f
```

## ⚙️ Configuración

### Variables de entorno

Copia el archivo de ejemplo y ajusta según necesites:
```bash
cp .env.example .env
```

Variables disponibles:
- `DB_NAME`: Nombre de la base de datos (default: giga)
- `DB_USER`: Usuario de la base de datos (default: giga_user)
- `DB_PASSWORD`: Contraseña del usuario (default: giga_pass)
- `DB_PORT`: Puerto expuesto (default: 5432)
- `TZ`: Timezone (default: America/Argentina/Buenos_Aires)

### Configuración personalizada

- **postgresql.conf**: Configuraciones optimizadas para desarrollo
- **pg_hba.conf**: Configuración de autenticación para Docker
- **init/01-init-db.sh**: Script que se ejecuta al crear la BD

## 🔧 Características

### Extensiones incluidas
- `uuid-ossp`: Para generar UUIDs
- `pg_trgm`: Para búsquedas de texto mejoradas
- `unaccent`: Para búsquedas sin acentos

### Optimizaciones
- Configuración de memoria optimizada para desarrollo
- Timezone configurado para Argentina
- Charset UTF-8 por defecto
- Logs en español (es_AR)

## 🌐 Conexión Externa

### Desde la aplicación Django
```python
# En settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'giga',
        'USER': 'giga_user',
        'PASSWORD': 'giga_pass',
        'HOST': 'giga-db',  # Nombre del servicio
        'PORT': '5432',
    }
}
```

### Desde herramientas externas
```bash
# psql
psql -h localhost -p 5432 -U giga_user giga

# pgAdmin o similar
Host: localhost
Port: 5432
Database: giga
Username: giga_user
Password: giga_pass
```

## 📊 Monitoreo

### Ver estado del contenedor
```bash
docker ps | grep giga_database
```

### Ver uso de recursos
```bash
docker stats giga_database
```

### Conectarse al contenedor
```bash
docker exec -it giga_database bash
```

### Backup manual
```bash
# Crear backup
docker exec giga_database pg_dump -U giga_user giga > backup.sql

# Restaurar backup
cat backup.sql | docker exec -i giga_database psql -U giga_user giga
```

## 🔒 Seguridad

### En desarrollo
- Conexiones locales con trust
- Conexiones Docker con md5
- Puerto 5432 expuesto solo para desarrollo

### En producción
- Cambiar todas las contraseñas
- Configurar SSL/TLS
- Restringir conexiones por IP
- No exponer puerto públicamente

## 🐛 Troubleshooting

### La BD no inicia
```bash
# Ver logs detallados
docker-compose logs giga-db

# Verificar permisos
ls -la /var/lib/docker/volumes/

# Reiniciar desde cero
docker-compose down -v
docker-compose up -d
```

### Problemas de conexión
```bash
# Verificar que el servicio esté corriendo
docker ps | grep giga_database

# Verificar configuración de red
docker network ls
docker network inspect giga_network
```

### Rendimiento lento
```bash
# Ver configuración actual
docker exec giga_database cat /etc/postgresql/postgresql.conf

# Ver conexiones activas
docker exec giga_database psql -U giga_user giga -c "SELECT * FROM pg_stat_activity;"
```

## 🔄 Integración con el proyecto

Esta base de datos se integra automáticamente con:

- **Backend Django**: Se conecta usando el nombre de servicio `giga-db`
- **Docker Compose**: Usa la red `giga_network` para comunicación
- **Scripts de gestión**: El script `../scripts/switch-database.sh` gestiona este servicio

## 📝 Notas importantes

1. **Persistencia**: Los datos se almacenan en volúmenes Docker nombrados
2. **Networking**: Usa la red `giga_network` para comunicarse con otros servicios
3. **Backups**: No hay backups automáticos, implementar según necesidades
4. **Timezone**: Configurado para Argentina (America/Argentina/Buenos_Aires)
5. **Charset**: UTF-8 con localización en español argentino