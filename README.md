# GIGA - Sistema de Gestión Integral de Guardias y Asistencias

Sistema web desarrollado con **Django REST**, **SvelteKit** y **PostgreSQL aislada**.

---

## ⚡ **SÚPER FÁCIL - DOS OPCIONES**

### **Opción 1: Script automático (más fácil)**
```bash
# Después de git clone o git pull:
cd giga
./start.sh     # ✅ Windows (Git Bash) | Linux | macOS
```

### **Opción 2: Comando manual**  
```bash
# Una sola línea (copiar y pegar completa):
cd giga && cd db && docker-compose down -v && docker-compose up -d && sleep 15 && cd .. && docker-compose -f docker-compose.dev.yml down -v && docker-compose -f docker-compose.dev.yml up -d --build
```

### **¿Todo funcionando? Abrir navegador:**
- **App:** http://localhost:5173
- **Admin:** http://localhost:8000/admin  
- **API:** http://localhost:8000/api/

---

## 🎯 **Lo que hace el comando:**
1. **Entra** al directorio del proyecto
2. **Limpia** cualquier configuración anterior  
3. **Inicia** base de datos PostgreSQL aislada
4. **Espera** que la BD esté lista
5. **Levanta** backend Django + frontend SvelteKit
6. **Carga** datos de ejemplo automáticamente

---

## 🛠️ **Comandos Útiles (Si algo no funciona)**

### **Ver qué está pasando:**
```bash
docker ps                    # ¿Qué está corriendo?
docker logs giga_backend_dev # Logs del backend
docker logs giga_frontend_dev# Logs del frontend
```

### **Reiniciar solo un servicio:**
```bash
docker-compose -f docker-compose.dev.yml restart backend  # Solo backend
docker-compose -f docker-compose.dev.yml restart frontend # Solo frontend
```

### **Si nada funciona (reset total):**
```bash
# 🔄 Repetir el comando universal de arriba
cd db && docker-compose down -v && docker-compose up -d && sleep 15 && cd .. && docker-compose -f docker-compose.dev.yml down -v && docker-compose -f docker-compose.dev.yml up -d --build
```

## � **Datos Precargados**

El sistema incluye datos de ejemplo:
- **6 usuarios** (Tayra, Cristian, María, Juan, Ana, admin)
- **5 roles** (Administrador, Supervisor, Agente, etc.)
- **Licencias de prueba** para cada usuario

**Login de prueba:**
- Usuario: `admin` | Password: `admin123`
- Usuario: `tayra.aguila` | Password: `password123`

## 🛠️ Stack Tecnológico

### **Arquitectura de Microservicios**
- **Base de Datos**: PostgreSQL 16-alpine (servicio independiente)
- **Backend**: Django 5.2.7 REST API (sin BD embebida)
- **Frontend**: SvelteKit + Vite (desarrollo con hot-reload)
- **Contenedores**: Docker Compose v2 + redes aisladas
- **Proxy**: Nginx (solo en producción)

### **Ventajas de la Nueva Arquitectura**
- ✅ **BD Aislada**: PostgreSQL independiente del backend
- ✅ **Escalabilidad**: Cada servicio puede escalar independientemente  
- ✅ **Desarrollo**: Hot-reload sin afectar datos
- ✅ **Backup**: Datos centralizados en un solo lugar
- ✅ **Performance**: Conexiones persistentes optimizadas

## Funcionalidades

- **Personas**: Gestión de personal, áreas y roles
- **Asistencia**: Control horario y licencias
- **Guardias**: Sistema de turnos y cronogramas
- **Reportes**: Informes y notificaciones
- **Auditoría**: Trazabilidad de cambios
- **Convenio IA**: Consultas inteligentes sobre convenios

## � **Solución de Problemas**

### **Si algo no funciona:**
1. **Repetir el comando universal** (limpia y resetea todo)
2. **Verificar puertos libres**: 5173, 8000, 5434
3. **Verificar Docker**: `docker --version`

### **Problemas específicos:**
- **Puerto ocupado**: Cambiar números en `docker-compose.dev.yml`
- **No carga la web**: Esperar 2-3 minutos después del comando
- **Login falla**: Usuario `admin` / Password `admin123`

## 📋 **Requisitos**

**Instalar antes de empezar:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac)
- Docker Engine (Linux): `sudo apt install docker.io docker-compose-v2`
- Git: Para clonar el repositorio

**Verificar que funciona:**
```bash
docker --version     # Debe mostrar Docker 20.10+
git --version        # Cualquier versión reciente
```


## 🏗️ **Qué Incluye**

### **Módulos del Sistema:**
- � **Personas**: Gestión de empleados y roles
- 📅 **Asistencia**: Control horario y licencias  
- 🛡️ **Guardias**: Sistema de turnos
- 📊 **Reportes**: Informes automáticos
- 🔍 **Auditoría**: Registro de cambios
- 🤖 **Convenio IA**: Consultas inteligentes

### **Stack Técnico:**
- **Backend**: Django 5.2 + PostgreSQL 16
- **Frontend**: SvelteKit + hot-reload
- **Contenedores**: Docker + Docker Compose

---

## 📚 **Documentación Adicional**

Para desarrollo avanzado:
- [DOCKER.md](DOCKER.md) - Guía técnica completa
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Tutorial para desarrolladores
- [data_backup/](data_backup/) - Estructura de la base de datos

