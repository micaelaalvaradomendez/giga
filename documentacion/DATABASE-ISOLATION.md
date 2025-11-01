# 🗄️ Base de Datos Aislada - Guía de Uso

## 📋 Resumen de Cambios

Hemos **aislado completamente la base de datos PostgreSQL** del backend en una carpeta dedicada `db/`. Esto permite:

✅ **Independencia total** entre la base de datos y el backend  
✅ **Gestión simplificada** de la base de datos  
✅ **Configuración centralizada** en un solo lugar  
✅ **Fácil mantenimiento** y backups  
✅ **Escalabilidad** para futuros cambios  

## 🏗️ Nueva Estructura

```
giga/
├── back/               # Backend Django (sin dependencias de BD)
├── front/              # Frontend SvelteKit  
├── db/                 # 🆕 Base de datos aislada
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── postgresql.conf
│   ├── pg_hba.conf
│   ├── init/
│   └── README.md
├── scripts/            # Scripts de gestión
└── docker-compose.dev.yml  # Compose principal actualizado
```

## 🚀 Cómo Usar

### 1. Gestión de Base de Datos

```bash
# Script principal de gestión
./scripts/switch-database.sh start    # Iniciar BD
./scripts/switch-database.sh stop     # Detener BD  
./scripts/switch-database.sh status   # Ver estado
./scripts/switch-database.sh logs     # Ver logs
./scripts/switch-database.sh reset    # Reiniciar desde cero
```

### 2. Desarrollo Normal

```bash
# Iniciar todo el entorno (como antes)
docker-compose -f docker-compose.dev.yml up -d

# La BD se inicia automáticamente como servicio "giga-db"
```

### 3. Solo Base de Datos

```bash
# Solo la base de datos (independiente del backend)
cd db
docker-compose up -d
```

## 🔧 Configuración

### Backend (Django)
El backend ahora se conecta a `giga-db` en lugar de `db`:

```python
# back/giga/settings.py
DATABASES = {
    'default': {
        'HOST': 'giga-db',  # 🆕 Nuevo nombre de servicio
        # ... resto igual
    }
}
```

### Variables de Entorno
Las mismas variables de siempre, pero ahora más organizadas:

```bash
DB_NAME=giga
DB_USER=giga_user  
DB_PASSWORD=giga_pass
DB_HOST=giga-db     # 🆕 Nuevo nombre
DB_PORT=5432
```

## 🎯 Beneficios de esta Estructura

### ✅ Para el Backend
- **Sin dependencias** de configuración de BD
- **Más limpio** y enfocado en la lógica de negocio
- **Fácil testing** con diferentes BDs

### ✅ Para la Base de Datos  
- **Configuración centralizada** en `db/`
- **Fácil backup** y restauración
- **Monitoreo independiente**
- **Escalabilidad** (cluster, replicas, etc.)

### ✅ Para DevOps
- **Deploy independiente** de BD y backend
- **Configuración específica** por ambiente
- **Gestión simplificada** de servicios

## 🔄 Migración desde la Estructura Anterior

### ¿Qué cambió?
1. **Nombre del servicio**: `db` → `giga-db`
2. **Configuración**: Movida de `docker-compose.dev.yml` a `db/docker-compose.yml`
3. **Gestión**: Nuevo script `scripts/switch-database.sh`

### ¿Qué sigue igual?
1. **Datos**: Se mantienen todos los datos existentes
2. **Conexiones**: Mismo usuario, contraseña, puerto
3. **Funcionamiento**: La aplicación funciona exactamente igual

## 🛠️ Comandos Útiles

### Conexión Directa a la BD
```bash
# Desde host
psql -h localhost -p 5432 -U giga_user giga

# Desde contenedor  
docker exec -it giga_database psql -U giga_user giga
```

### Backup y Restore
```bash
# Backup
docker exec giga_database pg_dump -U giga_user giga > backup.sql

# Restore
cat backup.sql | docker exec -i giga_database psql -U giga_user giga
```

### Monitoring
```bash
# Ver estado
docker ps | grep giga_database

# Ver recursos
docker stats giga_database

# Ver logs
docker logs giga_database -f
```

## 🚨 Importante

### Para desarrollo actual:
- **Nada cambia** en tu flujo de trabajo diario
- **Mismos comandos** de `docker-compose`
- **Misma funcionalidad** de la aplicación

### Para nuevas implementaciones:
- **Usar `giga-db`** como host en nuevas configuraciones
- **Scripts en `scripts/`** para gestión de BD
- **Configuración en `db/`** para cambios de BD

## 📝 Próximos Pasos

1. **Probar** la nueva configuración
2. **Migrar datos** si es necesario  
3. **Actualizar scripts** de deploy si los tienes
4. **Documentar** cambios específicos de tu proyecto

¿Todo claro? ¡La base de datos ahora está completamente aislada y lista para cualquier cambio futuro! 🎉