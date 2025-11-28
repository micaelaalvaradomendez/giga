# Sistema GIGA - Guía de Deployment Gratuito
## Opciones para Subir el Proyecto a Producción

---

## ⚠️ ¿Por qué NO puedo usar solo GitHub Pages?

**GitHub Pages solo sirve para sitios web ESTÁTICOS** (HTML, CSS, JavaScript puro). El sistema GIGA tiene:

❌ **Backend Django** (Python) que necesita ejecutarse en un servidor  
❌ **Base de datos PostgreSQL** que necesita almacenamiento persistente  
❌ **Procesamiento del servidor** para APIs, autenticación, lógica de negocio  

**Conclusión**: GitHub Pages podría hospedar el frontend compilado, pero **NO** el backend ni la base de datos.

---

## 🎯 Opciones de Deployment Gratuito

### Comparación Rápida

| Servicio | Frontend | Backend | Base de Datos | Dificultad | **Recomendado** |
|----------|----------|---------|---------------|------------|-----------------|
| **Render.com** | ✅ Static Site | ✅ Web Service | ✅ PostgreSQL | Baja | ⭐⭐⭐⭐⭐ |
| **Railway.app** | ✅ | ✅ | ✅ PostgreSQL | Media | ⭐⭐⭐⭐ |
| **Fly.io** | ✅ | ✅ | ✅ PostgreSQL | Media-Alta | ⭐⭐⭐ |
| **PythonAnywhere** | ❌ | ✅ Django | ✅ MySQL/PostgreSQL | Media | ⭐⭐ |
| **Vercel + Supabase** | ✅ | ❌ (Serverless) | ✅ PostgreSQL | Media | ⭐⭐⭐ |
| **Netlify + Render** | ✅ | ✅ (en Render) | ✅ (en Render) | Media | ⭐⭐⭐⭐ |

---

## 🏆 OPCIÓN RECOMENDADA: Render.com (Todo en uno)

**Ventajas**:
- ✅ **Completamente gratuito** con limitaciones razonables
- ✅ **Todo en un solo lugar**: Frontend + Backend + Base de Datos
- ✅ **Auto-deploy** desde GitHub (actualización automática)
- ✅ **PostgreSQL gratuito** (90 días, luego permanece si hay actividad)
- ✅ **SSL/HTTPS** incluido
- ✅ **Fácil configuración**

**Limitaciones del Free Tier**:
- ⚠️ Servicio se "duerme" tras 15 minutos de inactividad (tarda ~30 seg en despertar)
- ⚠️ PostgreSQL gratuito por 90 días, luego requiere actividad regular
- ⚠️ 750 horas/mes de ejecución (suficiente para un servicio)
- ⚠️ Builds lentos (pero aceptable)

---

## 📝 GUÍA PASO A PASO: Deploy en Render.com

### Pre-requisitos

1. ✅ Cuenta de GitHub con el repositorio GIGA
2. ✅ Cuenta gratuita en [Render.com](https://render.com)
3. ✅ Git configurado localmente

---

### PASO 1: Preparar el Repositorio

#### 1.1. Crear archivo `render.yaml` en la raíz del proyecto

Este archivo define todos los servicios:

```yaml
# render.yaml - Configuración completa de servicios
databases:
  - name: giga-postgres
    databaseName: giga
    user: giga_user
    plan: free
    region: oregon
    postgresMajorVersion: 16

services:
  # Backend Django
  - type: web
    name: giga-backend
    env: python
    region: oregon
    plan: free
    buildCommand: |
      cd back
      pip install -r requirements.txt
      python manage.py collectstatic --no-input
    startCommand: |
      cd back
      python manage.py migrate --no-input
      gunicorn giga.wsgi:application --bind 0.0.0.0:$PORT --workers 2
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: giga-postgres
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: .onrender.com
      - key: CORS_ALLOW_ALL_ORIGINS
        value: False
      - key: CORS_ALLOWED_ORIGINS
        value: https://giga-frontend.onrender.com
    autoDeploy: true

  # Frontend SvelteKit
  - type: web
    name: giga-frontend
    env: node
    region: oregon
    plan: free
    buildCommand: |
      cd front
      npm install
      npm run build
    startCommand: |
      cd front
      node build
    envVars:
      - key: NODE_VERSION
        value: 20.10.0
      - key: VITE_API_URL
        value: https://giga-backend.onrender.com
      - key: NODE_ENV
        value: production
    autoDeploy: true
```

#### 1.2. Actualizar `back/requirements.txt`

Agregar dependencias para producción:

```txt
Django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
psycopg2-binary>=2.9.0
gunicorn>=20.1.0
whitenoise>=6.4.0
reportlab>=4.0.0
openpyxl>=3.1.0
python-decouple>=3.8  # Para variables de entorno
dj-database-url>=2.1.0  # Para parsear DATABASE_URL
```

#### 1.3. Actualizar `back/giga/settings.py`

Configurar para producción con variables de entorno:

```python
import os
from decouple import config
import dj_database_url

# SEGURIDAD
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# BASE DE DATOS
# Render.com provee DATABASE_URL automáticamente
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgresql://giga_user:giga2025@localhost:5432/giga'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# CORS
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

# ARCHIVOS ESTÁTICOS (Whitenoise)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Agregar después de SecurityMiddleware
    # ... resto de middlewares
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### 1.4. Actualizar `front/package.json`

Asegurar que el script de build esté correcto:

```json
{
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "start": "node build"
  }
}
```

#### 1.5. Crear `.gitignore` completo

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
*.env
venv/
env/

# Django
*.log
db.sqlite3
staticfiles/
media/

# Node
node_modules/
.npm
.svelte-kit/
build/
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

#### 1.6. Commitear cambios

```bash
git add .
git commit -m "Preparar proyecto para deployment en Render"
git push origin main
```

---

### PASO 2: Configurar Render.com

#### 2.1. Crear cuenta en Render

1. Ve a [https://render.com](https://render.com)
2. Click en **"Get Started"**
3. Regístrate con GitHub (recomendado)
4. Autoriza acceso a tus repositorios

#### 2.2. Opción A: Deploy automático con `render.yaml`

**Desde el Dashboard de Render**:

1. Click en **"New +"** → **"Blueprint"**
2. Conecta tu repositorio de GitHub
3. Selecciona el repositorio `giga`
4. Render detectará automáticamente el `render.yaml`
5. Click en **"Apply"**
6. Espera a que se creen los 3 servicios:
   - `giga-postgres` (Base de datos)
   - `giga-backend` (API Django)
   - `giga-frontend` (App SvelteKit)

#### 2.2. Opción B: Deploy manual (sin render.yaml)

Si prefieres configurar manualmente:

**1. Crear Base de Datos PostgreSQL**:
- New + → PostgreSQL
- Name: `giga-postgres`
- Database: `giga`
- User: `giga_user`
- Region: Oregon
- Plan: Free
- Create Database

**2. Crear Backend Django**:
- New + → Web Service
- Connect repository: `tu-usuario/giga`
- Name: `giga-backend`
- Region: Oregon
- Branch: `main`
- Root Directory: `back` (importante!)
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
- Start Command: `python manage.py migrate && gunicorn giga.wsgi:application --bind 0.0.0.0:$PORT`
- Plan: Free
- Environment Variables:
  - `DATABASE_URL`: (copiar de la BD creada)
  - `SECRET_KEY`: (generar uno aleatorio)
  - `DEBUG`: `False`
  - `ALLOWED_HOSTS`: `.onrender.com`
  - `CORS_ALLOWED_ORIGINS`: `https://giga-frontend.onrender.com`

**3. Crear Frontend SvelteKit**:
- New + → Web Service
- Same repository
- Name: `giga-frontend`
- Region: Oregon
- Root Directory: `front`
- Runtime: Node
- Build Command: `npm install && npm run build`
- Start Command: `node build`
- Plan: Free
- Environment Variables:
  - `VITE_API_URL`: `https://giga-backend.onrender.com`
  - `NODE_ENV`: `production`

---

### PASO 3: Configurar Base de Datos

#### 3.1. Obtener credenciales de PostgreSQL

En Render Dashboard → PostgreSQL → Info:

```
Host: oregon-postgres.render.com
Port: 5432
Database: giga_xxxxx
Username: giga_user
Password: [generado automáticamente]
Internal Database URL: postgresql://giga_user:...
External Database URL: postgresql://giga_user:...
```

#### 3.2. Inicializar base de datos (primera vez)

**Opción 1: Desde Render Console**:

1. Ir a `giga-backend` → Shell
2. Ejecutar comandos de inicialización:

```bash
cd /opt/render/project/src/back
python manage.py migrate
python manage.py createsuperuser --noinput --email admin@giga.com --username admin
```

**Opción 2: Conectar desde local y ejecutar scripts**:

```bash
# Instalar psql localmente (si no lo tienes)
# En Ubuntu/Debian: sudo apt install postgresql-client
# En macOS: brew install postgresql

# Conectar a la BD de Render
psql [EXTERNAL_DATABASE_URL copiado de Render]

# Luego ejecutar tus scripts SQL
\i /path/to/giga/bd/init-scripts/01-tables-final.sql
\i /path/to/giga/bd/init-scripts/02-functions-final.sql
\i /path/to/giga/bd/init-scripts/03-seed-data.sql
```

---

### PASO 4: Verificar Deployment

#### 4.1. URLs de los servicios

Después del deployment, tendrás:

- **Frontend**: `https://giga-frontend.onrender.com`
- **Backend API**: `https://giga-backend.onrender.com/api/`
- **Admin Django**: `https://giga-backend.onrender.com/admin/`

#### 4.2. Probar el sistema

1. **Verificar Backend**:
   - Ve a `https://giga-backend.onrender.com/api/personas/agentes/`
   - Deberías ver la API de Django REST Framework

2. **Verificar Frontend**:
   - Ve a `https://giga-frontend.onrender.com`
   - Deberías ver la página de login

3. **Verificar Conexión Frontend-Backend**:
   - Intenta hacer login
   - Verifica en DevTools que las requests van a `giga-backend.onrender.com`

---

### PASO 5: Configuración Post-Deploy

#### 5.1. Crear usuario administrador

Desde Render Console (`giga-backend` → Shell):

```bash
cd back
python manage.py createsuperuser
```

#### 5.2. Cargar datos iniciales

Si tienes fixtures o scripts de seed data:

```bash
python manage.py loaddata inicial_data.json
# o ejecutar tus scripts SQL personalizados
```

#### 5.3. Configurar CORS correctamente

En `back/giga/settings.py`, asegúrate de:

```python
CORS_ALLOWED_ORIGINS = [
    'https://giga-frontend.onrender.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://giga-frontend.onrender.com',
    'https://giga-backend.onrender.com',
]
```

---

## 🚀 OPCIÓN ALTERNATIVA 2: Railway.app

**Similar a Render pero con mejor free tier (temporalmente)**

### Ventajas
- ✅ $5 USD de crédito gratis mensual
- ✅ No se duerme el servicio
- ✅ Deployment más rápido

### Limitaciones
- ⚠️ Requiere tarjeta de crédito (no se cobra si no excedes $5)
- ⚠️ Free tier puede cambiar

### Despliegue en Railway

1. **Crear cuenta**: [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. **Add PostgreSQL** desde menú
4. **Add Service** → Django backend
5. **Add Service** → SvelteKit frontend
6. Railway genera URLs automáticamente

**Variables de entorno** se configuran igual que en Render.

---

## 🔄 OPCIÓN ALTERNATIVA 3: Frontend en Vercel + Backend en Render

**Para mejor performance del frontend**

### Frontend en Vercel

1. Conectar repo en [vercel.com](https://vercel.com)
2. Root Directory: `front`
3. Framework Preset: SvelteKit
4. Environment Variables:
   - `VITE_API_URL`: `https://giga-backend.onrender.com`
5. Deploy

### Backend + BD en Render

Seguir pasos de Render solo para backend y PostgreSQL.

**Ventaja**: Vercel tiene mejor CDN global para frontend.

---

## ⚙️ Configuración de Auto-Deploy

### Desde GitHub

En Render, cada servicio puede configurarse para:

✅ **Auto-deploy on push**: Se redespliega automáticamente al hacer `git push`  
✅ **Branch**: Especificar rama (main, production, etc.)  
✅ **Build filters**: Solo redesplegar si cambian archivos específicos

**Configuración**:
- Ir a Service → Settings → Build & Deploy
- Habilitar "Auto-Deploy"
- Configurar "Deploy Hook" (opcional) para deploys manuales vía webhook

---

## 🔒 Seguridad en Producción

### Checklist de Seguridad

- [ ] `DEBUG = False` en Django
- [ ] `SECRET_KEY` único y aleatorio (no el de desarrollo)
- [ ] CORS configurado solo para dominio del frontend
- [ ] HTTPS habilitado (automático en Render/Vercel)
- [ ] Variables sensibles en Environment Variables (no en código)
- [ ] `.env` files en `.gitignore`
- [ ] Passwords de BD robustos
- [ ] Rate limiting configurado
- [ ] Backups de BD programados

---

## 📊 Monitoreo y Mantenimiento

### Logs

**En Render**:
- Ir a servicio → Logs
- Ver logs en tiempo real
- Filtrar por tipo (INFO, ERROR, etc.)

**En Railway**:
- Deploy → Logs
- Logs agrupados por servicio

### Métricas

**Render**:
- Dashboard muestra:
  - Tiempo de actividad (uptime)
  - Requests por minuto
  - Tiempo de respuesta
  - Uso de memoria

### Alertas

Configurar notificaciones:
- Deploy exitoso/fallido
- Servicio caído
- Errores 500
- Uso de recursos

---

## 🆘 Troubleshooting

### Problema: "Application failed to respond"

**Causa**: Servicio tardó más de 30 segundos en iniciar.

**Solución**:
```bash
# En start command, agregar health check
gunicorn giga.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
```

### Problema: "Database connection failed"

**Causa**: `DATABASE_URL` no configurada correctamente.

**Solución**:
- Verificar que `DATABASE_URL` esté en Environment Variables
- Verificar que `psycopg2-binary` esté en `requirements.txt`
- Verificar que `dj-database-url` esté instalado

### Problema: "Static files not loading"

**Causa**: `collectstatic` no se ejecutó o Whitenoise mal configurado.

**Solución**:
```python
# settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Agregar en build command
python manage.py collectstatic --no-input
```

### Problema: "CORS errors"

**Causa**: Frontend y backend en dominios diferentes.

**Solución**:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'https://giga-frontend.onrender.com',
]
```

### Problema: "Service sleeping"

**Causa**: Free tier de Render duerme tras 15 min de inactividad.

**Solución**:
- Usar UptimeRobot (gratuito) para hacer ping cada 5 min
- Upgrade a plan pago (~$7/mes)

---

## 💰 Costos y Limitaciones

### Render Free Tier

| Recurso | Límite |
|---------|--------|
| Web Services | 750 horas/mes |
| PostgreSQL | 90 días gratis, luego con actividad |
| Bandwidth | 100 GB/mes |
| Build minutes | 500 min/mes |
| Sleep tras inactividad | 15 minutos |
| Cold start | ~30 segundos |

### Railway Free Trial

| Recurso | Límite |
|---------|--------|
| Crédito mensual | $5 USD |
| Sin sleep | ✅ |
| Bandwidth | Según uso en $5 |
| Builds | Ilimitados |

---

## ✅ Resumen - ¿Qué opción elegir?

### Para desarrollo/prueba inicial:
👉 **Render.com** (todo en uno, fácil, gratuito)

### Para producción seria (bajo presupuesto):
👉 **Railway** ($5/mes con tarjeta) o **Render Starter** ($7/mes)

### Para máximo performance:
👉 **Frontend en Vercel** + **Backend en Render** + **BD en Supabase**

### Para control total:
👉 **VPS barato** (DigitalOcean, Linode, Vultr - desde $5/mes)

---

## 📚 Recursos Adicionales

- [Documentación Render.com](https://render.com/docs)
- [Documentación Railway](https://docs.railway.app)
- [Guía Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [SvelteKit Deployment](https://kit.svelte.dev/docs/adapters)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/current/tutorial-start.html)

---

## 🎯 Próximos Pasos

1. ✅ Elegir plataforma (Render recomendado)
2. ✅ Preparar repositorio con archivos de configuración
3. ✅ Crear cuenta en plataforma elegida
4. ✅ Conectar repositorio GitHub
5. ✅ Configurar servicios (BD, Backend, Frontend)
6. ✅ Configurar variables de entorno
7. ✅ Hacer primer deploy
8. ✅ Verificar funcionamiento
9. ✅ Configurar auto-deploy
10. ✅ Configurar monitoreo

**¡Listo para producción!** 🚀
