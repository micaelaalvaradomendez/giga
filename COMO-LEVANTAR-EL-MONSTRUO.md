# 🐉 CÓMO LEVANTAR EL MONSTRUO GIGA

## 📋 PREREQUISITOS

### Para Windows:
1. **Docker Desktop**: Descargar e instalar desde https://www.docker.com/products/docker-desktop
2. **Git**: https://git-scm.com/download/win
3. **Asegúrate de que Docker Desktop esté corriendo** (ícono en la bandeja del sistema)

### Para Linux/Mac:
1. **Docker**: `sudo apt install docker.io` (Ubuntu) o usar el instalador oficial
2. **Docker Compose**: `sudo apt install docker-compose`
3. **Git**: `sudo apt install git`

## 🚀 PASOS PARA LEVANTAR EL SISTEMA

### 1. Clonar el proyecto
```bash
git clone https://github.com/tu-usuario/giga.git
cd giga
```

### 2. Configurar variables de entorno
```bash
# Copiar el archivo de configuración
cp .env.example .env

# Para desarrollo básico, no necesitas cambiar nada
# Para producción, edita las contraseñas y claves secretas
```

### 3. LEVANTAR EN DESARROLLO (Recomendado para empezar)

#### En Windows:
```cmd
# Abrir PowerShell o CMD en la carpeta del proyecto
manage.bat dev
```

#### En Linux/Mac:
```bash
# Dar permisos al script
chmod +x manage.sh

# Iniciar desarrollo
./manage.sh dev
```

### 4. ¡LISTO! 🎉

Después de unos minutos (la primera vez tarda más porque descarga e instala todo):

- **Frontend**: http://localhost:5173 ← **USAR ESTA URL**
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Base de Datos**: localhost:5434

### 5. Datos de prueba

El sistema crea automáticamente:
- **Usuario admin**: `admin` / `admin123`
- **Base de datos**: Con datos de ejemplo
- **Roles**: Administrador, Agente, etc.

## 🔧 COMANDOS ÚTILES

### Windows (manage.bat):
```cmd
manage.bat dev          # Iniciar desarrollo
manage.bat stop         # Detener todo
manage.bat logs         # Ver qué está pasando
manage.bat logs backend # Ver logs del backend
manage.bat shell        # Entrar al backend
manage.bat status       # Ver estado de los servicios
manage.bat clean        # Limpiar todo (si algo se rompe)
```

### Linux/Mac (manage.sh):
```bash
./manage.sh dev          # Iniciar desarrollo
./manage.sh stop         # Detener todo
./manage.sh logs         # Ver qué está pasando
./manage.sh logs backend # Ver logs del backend
./manage.sh shell        # Entrar al backend
./manage.sh status       # Ver estado de los servicios
./manage.sh clean        # Limpiar todo (si algo se rompe)
```

## 🎯 ARQUITECTURA DEL MONSTRUO

```
📱 TU NAVEGADOR
    ↓ http://localhost:5173
🎨 FRONTEND (SvelteKit + pnpm)
    ↓ /api/* 
🐍 BACKEND (Django + PostgreSQL)
    ↓ Datos
💾 BASE DE DATOS (PostgreSQL)
```

### En desarrollo:
- **Frontend**: Puerto 5173 (acceso directo)
- **Backend**: Puerto 8000 (API)
- **Base de Datos**: Puerto 5434

### En producción:
```
📱 TU NAVEGADOR
    ↓ http://localhost (puerto 80)
🌐 NGINX (Proxy Reverso)
    ├─ / → 🎨 FRONTEND
    ├─ /api → 🐍 BACKEND  
    └─ /admin → 🐍 DJANGO ADMIN
```

## 🚨 SOLUCIÓN DE PROBLEMAS

### "Docker no está instalado"
- **Windows**: Instalar Docker Desktop y asegurarse de que esté corriendo
- **Linux**: `sudo apt install docker.io docker-compose`

### "Puerto ocupado"
```bash
# Ver qué está usando el puerto
netstat -tulpn | grep :5173
netstat -tulpn | grep :8000

# Matar proceso si es necesario
sudo kill -9 <PID>
```

### "No se puede conectar a Docker"
- **Windows**: Reiniciar Docker Desktop
- **Linux**: `sudo systemctl start docker`

### "Error de permisos"
```bash
# Linux - Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Luego cerrar sesión y volver a entrar
```

### "El frontend no se conecta al backend"
1. Verificar que ambos estén corriendo: `./manage.sh status`
2. Ver logs: `./manage.sh logs`
3. Verificar variables de entorno en `.env`

### "Problemas con pnpm"
```bash
# Limpiar cache
./manage.sh pnpm store prune

# Reinstalar dependencias
./manage.sh pnpm install --force
```

### "La base de datos no tiene datos"
```bash
# Recrear desde cero
./manage.sh clean
./manage.sh dev
```

### "Todo está roto"
```bash
# REINICIO COMPLETO (borra todo)
./manage.sh clean

# Volver a empezar
./manage.sh dev
```

## 📊 MONITOREO

### Ver el estado de todo:
```bash
./manage.sh status
```

### Ver logs en tiempo real:
```bash
./manage.sh logs
```

### Entrar al backend:
```bash
./manage.sh shell
```

### Entrar a la base de datos:
```bash
./manage.sh db-shell
```

## 🎮 MODO PRODUCCIÓN

⚠️ **Solo usar cuando todo funcione en desarrollo**

### 1. Configurar producción:
```bash
# Editar .env
DEBUG=0
SECRET_KEY=una-clave-muy-segura-y-larga-aqui
DB_PASSWORD=contraseña-super-segura
NODE_ENV=production
```

### 2. Levantar producción:
```bash
# Windows
manage.bat prod

# Linux/Mac  
./manage.sh prod
```

### 3. Acceder:
- **Todo a través de**: http://localhost
- **API**: http://localhost/api
- **Admin**: http://localhost/admin

## 💡 CONSEJOS PRO

### Para desarrollo:
1. **Siempre usar**: `./manage.sh dev` (no producción)
2. **Frontend**: http://localhost:5173 (tiene hot-reload)
3. **Ver logs**: `./manage.sh logs` si algo falla
4. **Reiniciar solo un servicio**: `docker-compose -f docker-compose.dev.yml restart frontend`

### Para debugging:
1. **Ver todos los logs**: `./manage.sh logs`
2. **Ver logs específicos**: `./manage.sh logs backend`
3. **Entrar al contenedor**: `./manage.sh shell`
4. **Estado de los servicios**: `./manage.sh status`

### Comandos útiles de Docker:
```bash
# Ver contenedores corriendo
docker ps

# Ver uso de recursos
docker stats

# Ver logs de un contenedor específico
docker logs giga_frontend_dev

# Entrar a un contenedor manualmente
docker exec -it giga_backend_dev bash
```

## ✅ CHECKLIST DE VERIFICACIÓN

Después de `./manage.sh dev`, verificar:

- [ ] `docker ps` muestra 3 contenedores corriendo
- [ ] http://localhost:5173 carga el frontend
- [ ] http://localhost:8000/api/auth/check-session/ responde JSON
- [ ] http://localhost:8000/admin permite login con admin/admin123
- [ ] No hay errores en `./manage.sh logs`

## 🆘 PEDIR AYUDA

Si nada funciona:

1. Ejecutar: `./manage.sh logs > logs.txt`
2. Enviar el archivo `logs.txt`
3. Mencionar:
   - Sistema operativo (Windows/Linux/Mac)
   - Versión de Docker: `docker --version`
   - Qué comando ejecutaste
   - Qué error apareció

---

**¡El monstruo está domado! 🐉✅**