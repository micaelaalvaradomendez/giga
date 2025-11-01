# 🐋 Ejecución con Docker - Nueva Arquitectura de Microservicios

## 📋 Requisitos
- Docker Desktop 4.0+ (Windows/macOS) o Docker Engine + Docker Compose (Linux)
- Git para clonar el repositorio

## 🚀 Setup Completo (Nueva Arquitectura)

### **⚡ Modo Desarrollo (Recomendado)**

```bash
# 1. Clonar y preparar entorno
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga
cp .env.example .env  # Ajustar variables si es necesario

# 2. 🔥 IMPORTANTE: Iniciar BD aislada PRIMERO
cd db
docker-compose up -d
cd ..

# 3. Levantar aplicación completa
docker-compose -f docker-compose.dev.yml up -d --build

# 4. Verificar que todo esté funcionando
docker ps  # Deberías ver 3 contenedores: giga_db_dev, giga_backend_dev, giga_frontend_dev
```

### **🏭 Modo Producción (Con Nginx)**

```bash
# Levantar stack completo incluyendo proxy Nginx
docker-compose up -d --build
```

## 🌐 URLs de Acceso

### Desarrollo
| Servicio | URL | Puerto |
|----------|-----|--------|
| **Frontend (App)** | http://localhost:5173 | 5173 |
| **Backend API** | http://localhost:8000 | 8000 |
| **Admin Django** | http://localhost:8000/admin | 8000 |
| **PostgreSQL** | localhost:5434 | 5434 |

### Producción  
| Servicio | URL | Puerto |
|----------|-----|--------|
| **Aplicación Web** | http://localhost | 80 |
| **API** | http://localhost/api | 80 |
| **Admin** | http://localhost/admin | 80 |

## 🏗️ Arquitectura de Servicios

### **🔥 Base de Datos Aislada** (`db/`)
```yaml
Servicio: giga-db / giga_db_dev
Imagen: PostgreSQL 16-alpine personalizada
Puerto: 5434 (desarrollo) | interno (producción)  
Volúmenes: giga_db_data_dev, giga_db_logs_dev
Configuración: postgresql.conf, pg_hba.conf optimizados
```
**Características:**
- ✅ **Independiente** del backend Django
- ✅ **Persistencia** garantizada en volúmenes Docker
- ✅ **Optimizada** para el stack de aplicación
- ✅ **Aislada** en red Docker propia

### **⚙️ Backend Django** (`back/`)
```yaml
Servicio: backend / giga_backend_dev  
Framework: Django 5.2.7 + DRF
Puerto: 8000
Conexión DB: giga-db:5432 (interna)
```
**Características:**
- ❌ **SIN base de datos propia** 
- ✅ **Solo API REST** + Admin Django
- ✅ **Hot-reload** en desarrollo
- ✅ **Migraciones** van a BD externa únicamente

### **🎨 Frontend SvelteKit** (`front/`)
```yaml
Servicio: frontend / giga_frontend_dev
Framework: SvelteKit + Vite  
Puerto: 5173
Hot-reload: Activado en desarrollo
```

### **🔄 Proxy Nginx** (solo producción)
```yaml
Servicio: nginx
Puerto: 80, 443
Función: Proxy reverso, archivos estáticos
```

## ⚡ Comandos Útiles

### **Estado y Logs**
```bash
# Ver todos los contenedores
docker ps

# Estado específico por entorno  
docker-compose -f docker-compose.dev.yml ps    # Desarrollo
docker-compose ps                                # Producción  
cd db && docker-compose ps                       # Solo BD

# Logs en tiempo real
docker logs -f giga_backend_dev     # Backend
docker logs -f giga_frontend_dev    # Frontend  
docker logs -f giga_db_dev          # Base de datos

# Logs con timestamp
docker logs --timestamps giga_backend_dev
```

### **Gestión de Servicios**
```bash
# Reiniciar servicios específicos (desarrollo)
docker-compose -f docker-compose.dev.yml restart backend
docker-compose -f docker-compose.dev.yml restart frontend

# Reiniciar base de datos
cd db && docker-compose restart && cd ..

# Parar todo el stack
docker-compose -f docker-compose.dev.yml down
cd db && docker-compose down

# Parar y ELIMINAR volúmenes (⚠️ BORRA DATOS)
docker-compose -f docker-compose.dev.yml down -v
cd db && docker-compose down -v
```

### **Rebuild y Actualización**
```bash
# Reconstruir después de cambios en Dockerfile o dependencias
docker-compose -f docker-compose.dev.yml up -d --build

# Rebuild solo un servicio  
docker-compose -f docker-compose.dev.yml up -d --build backend
docker-compose -f docker-compose.dev.yml up -d --build frontend

# Reset completo del entorno
docker-compose -f docker-compose.dev.yml down -v
cd db && docker-compose down -v && docker-compose up -d
cd .. && docker-compose -f docker-compose.dev.yml up -d --build
```

## 🔧 Configuración Avanzada

### **Variables de Entorno (.env)**
```env
# Base de datos
DB_NAME=giga
DB_USER=giga_user
DB_PASSWORD=giga_pass
DB_HOST=giga-db  # ⚠️ Nombre del contenedor, NO localhost

# Django
SECRET_KEY=tu-clave-secreta-segura
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Frontend  
VITE_API_BASE=http://localhost:8000
```

### **Puertos Personalizados**
Si los puertos están ocupados, editar en `docker-compose.dev.yml`:
```yaml
# Ejemplo: cambiar frontend de 5173 a 3000
frontend:
  ports:
    - "3000:5173"  # host:contenedor
    
# Ejemplo: cambiar BD de 5434 a 5435  
giga-db:
  ports:
    - "5435:5432"
```

### **Redes Docker**
```bash
# Ver redes creadas
docker network ls | grep giga

# Inspeccionar red de desarrollo
docker network inspect giga_giga_dev_network

# Conectar contenedor manualmente
docker network connect giga_giga_dev_network mi_contenedor
```

## 🚨 Solución de Problemas

### **Backend no conecta a BD**
```bash
# 1. ¿Está la BD corriendo?
cd db && docker-compose ps
# Si está DOWN: docker-compose up -d

# 2. ¿Están en la misma red?
docker inspect giga_backend_dev | grep NetworkMode
docker inspect giga_db_dev | grep NetworkMode  

# 3. Test de conectividad
docker exec giga_backend_dev ping giga-db
```

### **Puerto ya en uso**
```bash
# Linux/macOS: ver qué usa el puerto
sudo lsof -i :5173
sudo netstat -tulpn | grep :5173

# Windows: 
netstat -ano | findstr :5173

# Cambiar puerto en docker-compose.dev.yml y relanzar
```

### **Problemas de permisos (Linux)**
```bash
# Dar permisos a Docker sin sudo
sudo usermod -aG docker $USER
# Logout y login para aplicar cambios

# Si persisten problemas de permisos con volúmenes
sudo chown -R $USER:$USER ./db/
sudo chown -R $USER:$USER ./back/
sudo chown -R $USER:$USER ./front/
```

### **Datos corruptos o perdidos**
```bash
# Reset completo con restore de backup
docker-compose -f docker-compose.dev.yml down -v
cd db && docker-compose down -v

# Rebuild desde cero
cd db && docker-compose up -d
sleep 15  # Esperar que PostgreSQL esté listo
cd .. && docker-compose -f docker-compose.dev.yml up -d --build backend

# Restaurar datos desde backup
docker exec giga_backend_dev python manage.py migrate
docker exec giga_backend_dev python manage.py loaddata /app/data_backup/personas_data.json
docker exec giga_backend_dev python manage.py loaddata /app/data_backup/asistencia_data.json

# Levantar frontend
docker-compose -f docker-compose.dev.yml up -d frontend
```

## 📊 Monitoreo y Métricas

### **Salud de Servicios**
```bash
# Health checks
docker exec giga_db_dev pg_isready -U giga_user -d giga
docker exec giga_backend_dev python manage.py check --deploy
curl -f http://localhost:5173/ # Frontend
curl -f http://localhost:8000/api/ # Backend API
```

### **Uso de Recursos**
```bash
# CPU y RAM por contenedor
docker stats

# Espacio en disco
docker system df
docker system df -v  # Detallado

# Limpieza de espacio
docker system prune -f
docker volume prune -f  # ⚠️ ELIMINA volúmenes no usados
```

## 🎯 Mejores Prácticas

### **Desarrollo**
- ✅ Usar siempre `docker-compose.dev.yml` para desarrollo
- ✅ Levantar BD aislada ANTES que el backend
- ✅ No hacer `docker-compose down -v` sin backup de datos
- ✅ Usar logs para debugear problemas de conectividad

### **Producción**  
- ✅ Usar `docker-compose.yml` (incluye Nginx)
- ✅ Configurar SSL en Nginx para HTTPS
- ✅ Variables de entorno seguras (no defaults)
- ✅ Backups regulares de la BD aislada

### **Seguridad**
- ✅ Cambiar `SECRET_KEY` en producción
- ✅ `DEBUG=False` en producción
- ✅ Configurar firewall para puertos expuestos
- ✅ Usar secretos Docker para credenciales DB

