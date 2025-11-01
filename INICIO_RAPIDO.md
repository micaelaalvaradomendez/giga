# ⚡ Guía de Inicio Rápido - GIGA

## 🎯 Para desarrolladores nuevos en el proyecto

### **30 segundos para levantar el sistema:**

```bash
# 1. Clonar repositorio
git clone https://github.com/micaelaalvaradomendez/giga.git
cd giga

# 2. 🔥 Iniciar BD aislada (PRIMERO Y MÁS IMPORTANTE)
cd db && docker-compose up -d && cd ..

# 3. Levantar aplicación completa  
docker-compose -f docker-compose.dev.yml up -d --build

# 4. ¡Listo! Abrir en navegador
# Frontend: http://localhost:5173
# Admin:    http://localhost:8000/admin
```

### **¿Todo funcionando?** ✅
- Deberías ver 3 contenedores corriendo: `docker ps`
- Frontend carga en http://localhost:5173
- Backend responde en http://localhost:8000/api/
- Hay 6 usuarios precargados con datos de ejemplo

---

## 🔧 Comandos que vas a usar TODO el tiempo

### **Ver qué está pasando:**
```bash
docker ps                                    # ¿Qué contenedores están corriendo?
docker logs -f giga_backend_dev             # Logs del backend en vivo
docker logs -f giga_frontend_dev            # Logs del frontend en vivo
```

### **Reiniciar cuando algo no funciona:**
```bash
docker-compose -f docker-compose.dev.yml restart backend    # Solo el backend
docker-compose -f docker-compose.dev.yml restart frontend   # Solo el frontend
cd db && docker-compose restart && cd ..                    # Solo la BD
```

### **Reset completo (cuando todo se rompe):**
```bash
# ⚠️ CUIDADO: Esto borra todos los datos
docker-compose -f docker-compose.dev.yml down -v
cd db && docker-compose down -v
cd .. && cd db && docker-compose up -d
cd .. && docker-compose -f docker-compose.dev.yml up -d --build
```

---

## 🏗️ ¿Cómo está armado esto?

### **🔥 Lo más importante que tenés que entender:**

**El backend Django NO tiene base de datos propia**. 

```
Frontend (SvelteKit) ←→ Backend (Django API) ←→ BD PostgreSQL (aislada)
    :5173                     :8000                :5434 (solo dev)
```

### **3 contenedores independientes:**
1. **`giga_db_dev`** - PostgreSQL aislada (en `db/`)
2. **`giga_backend_dev`** - Django REST API (en `back/`)  
3. **`giga_frontend_dev`** - SvelteKit (en `front/`)

### **⚠️ Orden de arranque CRÍTICO:**
1. **Primero BD** (`cd db && docker-compose up -d`)
2. **Luego Backend** (conecta a BD externa)
3. **Finalmente Frontend** (consume API del backend)

---

## 🎯 Casos de uso comunes

### **Desarrollo normal:**
```bash
# Solo esto, el hot-reload hace el resto
# Frontend: Editar archivos en front/src/ → auto-refresh
# Backend: Editar archivos en back/ → auto-restart
```

### **Cambié algo en requirements.txt o package.json:**
```bash
# Rebuild solo lo necesario
docker-compose -f docker-compose.dev.yml up -d --build backend   # Backend
docker-compose -f docker-compose.dev.yml up -d --build frontend  # Frontend
```

### **Agregué un modelo nuevo en Django:**
```bash
# Crear y aplicar migraciones (van a la BD aislada)
docker exec giga_backend_dev python manage.py makemigrations
docker exec giga_backend_dev python manage.py migrate
```

### **Quiero ver qué hay en la base de datos:**
```bash
# Acceso directo a PostgreSQL
docker exec -it giga_db_dev psql -U giga_user -d giga

# O ver usuarios desde Django
docker exec giga_backend_dev python manage.py shell -c "
from personas.models import Usuario
for u in Usuario.objects.all():
    print(f'{u.username} - {u.email}')
"
```

---

## 🚨 Soluciones a problemas típicos

### **"No me levanta el backend"**
```bash
# 1. ¿Está la BD corriendo PRIMERO?
cd db && docker-compose ps
# Si no: docker-compose up -d

# 2. Reiniciar backend DESPUÉS de que la BD esté lista
cd .. && docker-compose -f docker-compose.dev.yml restart backend
```

### **"Error de puerto ocupado"**
```bash
# Ver qué está usando el puerto
sudo lsof -i :5173  # Frontend
sudo lsof -i :8000  # Backend
sudo lsof -i :5434  # Base de datos

# Cambiar puertos en docker-compose.dev.yml si es necesario
```

### **"No carga la página de login"**
```bash
# Verificar que hay usuarios en el sistema
docker exec giga_backend_dev python manage.py shell -c "
from personas.models import Usuario
print(f'Usuarios: {Usuario.objects.count()}')
"

# Si no hay usuarios, cargar datos de ejemplo
docker exec giga_backend_dev python manage.py loaddata /app/data_backup/personas_data.json
```

### **"Los cambios no se reflejan"**
```bash
# Frontend: Verificar que el hot-reload está funcionando
docker logs giga_frontend_dev | grep "Local:"

# Backend: Reiniciar si el auto-reload no funciona  
docker-compose -f docker-compose.dev.yml restart backend
```

---

## 📚 Documentación adicional

- **[README.md](README.md)** - Documentación completa del proyecto
- **[DOCKER.md](DOCKER.md)** - Guía avanzada de Docker
- **[ARQUITECTURA_BD_AISLADA.md](ARQUITECTURA_BD_AISLADA.md)** - Por qué usamos BD aislada
- **[data_backup/](data_backup/)** - Estructura y datos de la BD

---

## 🎉 ¿Todo claro?

Si llegaste hasta acá y todo funciona, ya estás listo para desarrollar. Los puntos clave:

1. ✅ **BD aislada primero** - siempre
2. ✅ **Hot-reload automático** - editar y listo  
3. ✅ **3 contenedores independientes** - cada uno hace lo suyo
4. ✅ **Migraciones van a BD externa** - no al contenedor backend

**¿Dudas?** Revisar los logs con `docker logs -f <contenedor>` - ahí está todo.

---

*Happy coding! 🚀*