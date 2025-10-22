# 🔧 Guía de Solución de Problemas - Sistema GIGA

## 🚨 Problema: "El login no funciona después del git pull"

### Causa
Archivos de configuración críticos están en `.gitignore` y no se transfieren con git.

### ✅ Solución Rápida
```bash
# Ejecutar el script de configuración automática
./setup.sh
```

### 🔍 Solución Manual Paso a Paso

#### 1. **Verificar archivos `.env` necesarios**
```bash
# Archivo .env principal (raíz del proyecto)
cp .env.example .env

# Archivo .env del backend
cp back/.env.example back/.env
```

#### 2. **Crear directorio de logs**
```bash
mkdir -p back/logs
touch back/logs/django.log
```

#### 3. **Recrear base de datos con usuarios**
```bash
# Detener servicios
docker-compose down -v

# Reconstruir y iniciar
docker-compose up -d --build

# Esperar 10 segundos para que inicie la BD
sleep 10

# Ejecutar migraciones
docker-compose exec back python manage.py migrate

# Crear usuarios de prueba (usar script setup.sh o crear manualmente)
```

## 🔑 Usuarios de Prueba Predeterminados

Si necesitas crear los usuarios manualmente:

```bash
docker-compose exec back python manage.py shell
```

Luego ejecutar en el shell de Django:
```python
from personas.models import Usuario, Agente, Area, Rol, AgenteRol

# Crear área
area_admin, _ = Area.objects.get_or_create(
    codigo="ADMIN",
    defaults={'nombre': 'Administración General'}
)

# Crear roles
rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador")

# Crear usuario de prueba
usuario = Usuario.objects.create_user(
    username='Tayra Aguila',
    email='tayra.aguila@giga.gov.ar',
    password='12345678',
    first_name='Tayra',
    last_name='Aguila',
    cuil='27123456784'
)

# Crear agente
agente = Agente.objects.create(
    usuario=usuario,
    dni='12345678',
    apellido='Aguila',
    nombre='Tayra',
    fecha_nac='1990-01-01',
    email='tayra.aguila@giga.gov.ar',
    categoria_revista='A1',
    agrupacion='EPU'
)

# Asignar rol
AgenteRol.objects.create(
    usuario=usuario,
    rol=rol_admin,
    area=area_admin
)

print("Usuario creado exitosamente")
```

## 🛠️ Otros Problemas Comunes

### Error: "Puerto 8000 ya está en uso"
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000

# Matar proceso si es necesario
sudo kill -9 <PID>

# O cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### Error: "Puerto 5173 ya está en uso"
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :5173

# O cambiar puerto en docker-compose.yml
ports:
  - "5174:5173"  # Cambiar 5173 por 5174
```

### Error: "Cannot connect to Docker"
```bash
# Iniciar Docker (Linux)
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar
newgrp docker
```

### Error: "CSRF Failed" en el frontend
✅ **Ya solucionado** - El sistema tiene middleware personalizado para deshabilitar CSRF en APIs.

### Error: "CORS" al hacer peticiones
✅ **Ya solucionado** - CORS configurado para `localhost:5173`.

### Error: "Database connection failed"
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Ver logs de la base de datos
docker-compose logs db

# Reiniciar servicios
docker-compose restart
```

### Error: "Migration failed"
```bash
# Limpiar y recrear base de datos
docker-compose down -v
docker-compose up -d
sleep 10
docker-compose exec back python manage.py migrate
```

## 📊 Verificar que Todo Funciona

### 1. **Verificar servicios corriendo**
```bash
docker-compose ps
```
Todos los servicios deben mostrar estado `Up`.

### 2. **Verificar frontend**
Abrir http://localhost:5173 - debe mostrar página de login.

### 3. **Verificar backend**
```bash
curl http://localhost:8000/api/auth/login/
```
Debe devolver error de método (405 o similar), no error de conexión.

### 4. **Verificar login**
- Ir a http://localhost:5173
- CUIL: `27-12345678-4`
- Contraseña: `12345678`
- Debe redirigir a página de inicio con datos del usuario.

## 📞 Contacto para Soporte

Si los problemas persisten:
1. Ejecutar `docker-compose logs > logs_completos.txt`
2. Compartir el archivo de logs
3. Describir pasos exactos que llevaron al error

## 🔄 Comandos de Limpieza Total

En caso de problemas graves, limpiar completamente:
```bash
# CUIDADO: Esto borra TODA la base de datos
docker-compose down -v
docker system prune -f
docker volume prune -f

# Luego ejecutar setup nuevamente
./setup.sh
```