# Guía de Solución de Problemas con Docker - GIGA

## Diagnóstico Rápido

### Estado de los Servicios
```bash
# Ver estado de contenedores
docker ps

# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs back    # Backend
docker-compose logs db      # Base de datos
docker-compose logs front   # Frontend
```

## Problemas Comunes

### 1. **Error CRLF en Windows** (Típico después de git pull)

**Síntomas**: 
- El backend no inicia después de `git pull`
- Error `/bin/sh^M: bad interpreter`
- El setup.sh se queda colgado

**Causa**: Line endings CRLF de Windows en archivos `.sh`

**Solución**:
```bash
# Rebuild sin cache para aplicar conversión CRLF→LF
docker compose down -v
docker compose build --no-cache back
docker compose up -d

# Ver logs para confirmar
docker logs -f giga_back
```

**Prevención**: El repositorio ya tiene `.gitattributes` configurado. Una sola vez ejecutar:
```bash
./normalize_repo.sh
git commit -m "chore: enforce LF endings via .gitattributes"
```

### 2. **Error de Autenticación - No se puede hacer login**

**Síntomas**: 
- 403 Forbidden en login
- Error CSRF
- Usuario/contraseña no válidos

**Soluciones**:
```bash
# 1. Verificar que existen usuarios de prueba
docker-compose exec back python manage.py shell -c "
from personas.models import Usuario
print('Usuarios:', Usuario.objects.count())
for u in Usuario.objects.all()[:3]:
    print(f'- CUIL: {u.cuil}, Activo: {u.is_active}')
"

# 2. Crear usuario de prueba si no existe
docker-compose exec back python manage.py shell -c "
from personas.models import Usuario
from django.contrib.auth.hashers import make_password
usuario, created = Usuario.objects.get_or_create(
    cuil='27-12345678-4',
    defaults={
        'password': make_password('12345678'),
        'email': 'admin@giga.com',
        'is_active': True,
        'is_staff': True,
        'is_superuser': True
    }
)
print(f'Usuario creado: {created}')
"

# 3. Verificar CORS y CSRF settings
docker-compose logs back | grep -i "cors\|csrf"
```

### 3. **Base de Datos no conecta**

**Síntomas**:
- `could not connect to server`
- `database "giga_db" does not exist`

**Soluciones**:
```bash
# 1. Verificar que PostgreSQL esté corriendo
docker-compose ps db

# 2. Ver logs de la base de datos
docker-compose logs db

# 3. Recrear base de datos
docker-compose down -v
docker-compose up -d db
# Esperar que esté ready
docker-compose up -d back
```

### 4. **Puerto ocupado**

**Síntomas**:
- `port already in use`
- `bind: address already in use`

**Soluciones**:
```bash
# Ver qué proceso usa el puerto
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :5173

# Matar proceso (cambiar PID)
sudo kill -9 <PID>

# O cambiar puertos en docker-compose.yml
```

### 5. **Frontend no carga**

**Síntomas**:
- Página en blanco
- Error de conexión API

**Soluciones**:
```bash
# 1. Verificar variables de entorno del frontend
cat .env | grep VITE_API_BASE

# 2. Verificar que backend responde
curl http://localhost:8000/api/personas/

# 3. Ver logs del frontend
docker-compose logs front
```

## Reset Completo

Si nada funciona, reset completo:

```bash
# 1. Parar y eliminar todo
docker-compose down -v
docker system prune -f

# 2. Ejecutar setup nuevamente
./setup.sh
```

## Consultar Base de Datos

### Acceso directo a PostgreSQL
```bash
# Conectar a la base de datos
docker-compose exec db psql -U giga_user -d giga_db

# Consultas útiles:
\dt                              # Listar tablas
SELECT * FROM personas_usuario;  # Ver usuarios
SELECT * FROM django_session;   # Ver sesiones activas
\q                              # Salir
```

### Via Django Shell
```bash
# Acceder al shell de Django
docker-compose exec back python manage.py shell

# Consultas en Python:
from personas.models import Usuario
Usuario.objects.all()
Usuario.objects.filter(is_active=True)
```

## Si Nada Funciona

1. **Copia logs completos**:
   ```bash
   docker-compose logs > debug_logs.txt
   ```

2. **Verifica versiones**:
   ```bash
   docker --version
   docker-compose --version
   git --version
   ```

3. **Estado del sistema**:
   ```bash
   df -h          # Espacio en disco
   free -h        # Memoria RAM
   docker system df # Espacio Docker
   ```

4. **Contacta al equipo** con los logs y la información del sistema.