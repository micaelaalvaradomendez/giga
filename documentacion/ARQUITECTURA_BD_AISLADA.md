# 🏗️ Nueva Arquitectura: Base de Datos Aislada

## 🎯 Concepto Principal

**El backend Django NO tiene base de datos propia**. Toda la gestión de datos se hace a través de una base de datos PostgreSQL aislada en su propio contenedor.

## 🔥 ¿Por qué esta arquitectura?

### ❌ **Problema con la arquitectura anterior:**
- Backend tenía BD embebida → Acoplamiento fuerte
- Migraciones mezcladas con lógica de aplicación
- Difícil escalar y mantener
- Datos dispersos entre servicios

### ✅ **Ventajas de la nueva arquitectura:**
- **Separación clara**: BD independiente del backend
- **Escalabilidad**: Cada servicio escala por separado
- **Mantenimiento**: Backup/restore centralizados
- **Desarrollo**: Hot-reload sin afectar datos
- **Monitoreo**: Métricas de BD independientes

## 📋 Estructura de Servicios

### **1. Base de Datos Aislada** (`db/`)
```yaml
📁 db/
├── docker-compose.yml      # ⚡ Servicio PostgreSQL independiente
├── Dockerfile             # Imagen personalizada PostgreSQL 16
├── postgresql.conf        # Configuración optimizada
├── pg_hba.conf           # Políticas de autenticación
└── init/                 # Scripts de inicialización automática
```

**Responsabilidades:**
- ✅ Almacenar TODOS los datos del sistema
- ✅ Gestionar conexiones y performance
- ✅ Ejecutar scripts de inicialización
- ✅ Persistir datos en volúmenes Docker

**Comando de inicio:**
```bash
cd db && docker-compose up -d
```

### **2. Backend Django** (`back/`)
```python
# back/giga/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'giga-db',  # ⚡ Apunta al contenedor de BD
        'NAME': 'giga',
        'USER': 'giga_user',
        'PASSWORD': 'giga_pass',
        'PORT': '5432',
    }
}
```

**Responsabilidades:**
- ❌ **NO crear tablas propias**
- ✅ Conectar a BD externa únicamente
- ✅ Ejecutar lógica de negocio
- ✅ Proveer API REST
- ✅ Ejecutar migraciones **hacia BD externa**

### **3. Frontend SvelteKit** (`front/`)
**Responsabilidades:**
- ✅ Interfaz de usuario
- ✅ Consumir API del backend
- ❌ **NO acceder directamente a BD**

## 🔄 Flujo de Migraciones

### **⚠️ IMPORTANTE: ¿Dónde van las migraciones?**

```bash
# ❌ INCORRECTO: El backend NO crea BD propia
# Las migraciones NO van a una BD local del contenedor backend

# ✅ CORRECTO: Las migraciones van a la BD aislada
docker exec giga_backend_dev python manage.py migrate
#                                                    ↓
#                                            Va a giga-db:5432
#                                     (contenedor PostgreSQL aislado)
```

### **Proceso paso a paso:**

1. **Iniciar BD aislada:**
```bash
cd db && docker-compose up -d
# Crea contenedor 'giga_database' con PostgreSQL 16
# IP interna: giga-db (nombre del servicio)
# Puerto interno: 5432
```

2. **Iniciar backend (conecta a BD externa):**
```bash
cd .. && docker-compose -f docker-compose.dev.yml up -d backend  
# Backend se conecta a giga-db:5432
# settings.py apunta a HOST='giga-db'
```

3. **Ejecutar migraciones (van a BD externa):**
```bash
docker exec giga_backend_dev python manage.py migrate
# Crea tablas en giga-db PostgreSQL
# NO en el contenedor del backend
```

## 🔍 Verificación de la Arquitectura

### **¿Cómo verificar que funciona correctamente?**

#### **1. BD aislada está corriendo:**
```bash
cd db && docker-compose ps
# Debe mostrar: giga_database ... Up ... 5432/tcp
```

#### **2. Backend NO tiene BD propia:**
```bash
# ❌ Esto NO debería funcionar (no hay BD en el contenedor backend)
docker exec giga_backend_dev ls /var/lib/postgresql/
# Error: directorio no existe

# ✅ Verificar conexión a BD externa
docker exec giga_backend_dev python manage.py dbshell
# Debe conectar a PostgreSQL de giga-db
```

#### **3. Migraciones van a BD externa:**
```bash
# Ejecutar migración
docker exec giga_backend_dev python manage.py migrate

# Verificar tablas en BD aislada (NO en backend)
docker exec giga_db_dev psql -U giga_user -d giga -c "\dt"
# Debe mostrar tablas Django creadas
```

#### **4. Datos persistentes en BD aislada:**
```bash
# Crear usuario desde backend
docker exec giga_backend_dev python manage.py shell -c "
from personas.models import Usuario
u = Usuario.objects.create_user('test', 'test@test.com', 'password123')
print(f'Usuario creado: {u.id}')
"

# Verificar datos en BD aislada directamente
docker exec giga_db_dev psql -U giga_user -d giga -c "
SELECT id, username, email FROM personas_usuario WHERE username='test';
"
# Debe mostrar el usuario creado
```

## 🚨 Señales de Configuración Incorrecta

### **❌ Problemas que indican mala configuración:**

#### **Backend intenta crear BD propia:**
```bash
# Si ves esto, hay error de configuración
docker logs giga_backend_dev | grep "sqlite"
docker logs giga_backend_dev | grep "db.sqlite3"
# ↑ El backend NO debe usar SQLite
```

#### **Migraciones no se reflejan en BD aislada:**
```bash
# Ejecutar migración
docker exec giga_backend_dev python manage.py migrate

# Verificar en BD aislada - si no hay tablas, hay error
docker exec giga_db_dev psql -U giga_user -d giga -c "\dt"
# Debe mostrar todas las tablas Django
```

#### **Backend no puede conectar a BD:**
```bash
# Error común: backend inicia antes que BD
docker logs giga_backend_dev | grep "could not connect"
docker logs giga_backend_dev | grep "connection refused"

# Solución: Asegurar que BD esté corriendo PRIMERO
cd db && docker-compose up -d
sleep 15  # Esperar que PostgreSQL esté listo
cd .. && docker-compose -f docker-compose.dev.yml restart backend
```

## 📊 Diagrama de la Nueva Arquitectura

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend          │    │   Backend           │    │   Base de Datos     │
│   (SvelteKit)       │    │   (Django)          │    │   (PostgreSQL)      │
│                     │    │                     │    │                     │
│ http://localhost    │    │ ❌ NO DB propia     │    │ ✅ ÚNICA fuente     │
│ :5173               │◄──►│ ✅ Solo API + Admin │◄──►│    de datos         │
│                     │    │ ✅ Conecta a BD ext │    │                     │
│ Container:          │    │                     │    │ Container:          │
│ giga_frontend_dev   │    │ Container:          │    │ giga_db_dev         │
└─────────────────────┘    │ giga_backend_dev    │    │ (db/docker-compose) │
                           └─────────────────────┘    └─────────────────────┘
                                      │                          ▲
                                      │ settings.py              │
                                      │ HOST='giga-db'           │
                                      │ PORT=5432                │
                                      └──────────────────────────┘
                                           Red Docker Interna
                                         (giga_dev_network)

📡 COMUNICACIÓN:
├── Frontend ↔ Backend: HTTP REST API (puerto 8000)
├── Backend ↔ BD: PostgreSQL protocol (puerto 5432 interno)  
└── ❌ Frontend ↔ BD: NO hay conexión directa
```

## ✅ Checklist de Configuración Correcta

- [ ] **BD aislada iniciada:** `cd db && docker-compose ps`
- [ ] **Backend sin BD propia:** No hay SQLite ni PostgreSQL embebido
- [ ] **Settings.py correcto:** `HOST='giga-db'` (nombre del servicio)
- [ ] **Migraciones funcionan:** `python manage.py migrate` ejecuta sin errores
- [ ] **Datos persistentes:** Crear/leer datos funciona correctamente
- [ ] **Conexión estable:** Backend se reconecta automáticamente a BD
- [ ] **Red Docker:** Ambos contenedores en `giga_dev_network`

## 🎯 Comandos de Verificación Final

```bash
# 1. Estado completo del sistema
docker ps | grep giga
# Debe mostrar: giga_db_dev, giga_backend_dev, giga_frontend_dev

# 2. Test de conectividad completa
docker exec giga_backend_dev python manage.py check --database=default
# Debe pasar todas las verificaciones

# 3. Test de escritura/lectura BD
docker exec giga_backend_dev python manage.py shell -c "
from personas.models import Usuario
count = Usuario.objects.count()
print(f'✅ BD funcional: {count} usuarios en sistema')
"

# 4. Verificar que datos están en BD aislada (NO en backend)
docker exec giga_db_dev psql -U giga_user -d giga -c "
SELECT 'BD aislada funcionando: ' || COUNT(*) || ' usuarios' FROM personas_usuario;
"
```

¡Con esta configuración, el backend Django actúa **únicamente como API**, mientras que **toda la gestión de datos está centralizada en la base de datos aislada**! 🎉