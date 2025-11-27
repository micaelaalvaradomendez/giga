# Guía de Deploy en Nueva Computadora - Sistema GIGA

## 🚀 Pasos para Deploy Limpio

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd giga
```

### 2. Iniciar Docker (Primera Vez)
```bash
docker-compose up -d --build
```

**Esto ejecutará automáticamente:**
- ✅ Scripts SQL desde `bd/init-scripts/`:
  - `01-tables-final.sql` - Crea 29 tablas
  - `02-functions-final.sql` - Crea funciones y triggers
  - `03-seed-data.sql` - Inserta datos organizacionales
  - `04-historical-data.sql` - Genera datos históricos

- ✅ Migraciones Django automáticas (configurado en Dockerfile):
  - `python manage.py makemigrations`
  - `python manage.py migrate`
  - `python manage.py collectstatic`

### 3. Verificar que Todo Funciona

**Verificar contenedores:**
```bash
docker ps
```

Deberías ver 6 contenedores corriendo:
- giga-postgres
- giga-django
- giga-frontend
- giga-nginx
- giga-minio
- giga-n8n

**Verificar base de datos:**
```bash
docker exec giga-postgres psql -U giga_user -d giga -c "SELECT COUNT(*) FROM agente;"
docker exec giga-postgres psql -U giga_user -d giga -c "SELECT COUNT(*) FROM area;"
docker exec giga-postgres psql -U giga_user -d giga -c "SELECT COUNT(*) FROM guardia;"
```

**Verificar migraciones:**
```bash
docker exec giga-django python manage.py showmigrations
```

Todas las migraciones deben tener `[X]`.

**Verificar API:**
```bash
curl http://localhost:8000/api/personas/agentes/
```

### 4. Acceder a la Aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/
- **MinIO Console**: http://localhost:9090
- **n8n**: http://localhost:5678

---

## 🔧 Comandos Útiles

### Ver logs
```bash
docker logs giga-django
docker logs giga-frontend
docker logs giga-postgres
```

### Reiniciar servicios
```bash
docker-compose restart
docker-compose restart backend
docker-compose restart frontend
```

### Detener todo
```bash
docker-compose down
```

### Detener y limpiar volúmenes (CUIDADO: borra BD)
```bash
docker-compose down -v
```

### Reconstruir después de cambios
```bash
docker-compose up -d --build
```

---

## ⚠️ Troubleshooting

### Si el frontend no carga datos:

1. Verificar que el backend esté corriendo:
```bash
curl http://localhost:8000/api/personas/agentes/
```

2. Verificar migraciones:
```bash
docker exec giga-django python manage.py showmigrations
```

3. Si faltan migraciones, aplicarlas:
```bash
docker exec giga-django python manage.py migrate
```

### Si la BD está vacía:

Los scripts SQL se ejecutan SOLO la primera vez que se crea el volumen de PostgreSQL.

**Para reiniciar desde cero:**
```bash
docker-compose down -v  # Elimina volúmenes
docker-compose up -d --build  # Recrea todo
```

### Si hay errores de permisos:

```bash
sudo chown -R $USER:$USER ./back/staticfiles
sudo chown -R $USER:$USER ./back/media
```

---

## 📂 Estructura de Archivos Importantes

```
giga/
├── back/                      # Backend Django
│   ├── Dockerfile            # Incluye auto-migrate
│   ├── manage.py
│   └── requirements.txt
├── front/                     # Frontend SvelteKit
│   └── Dockerfile
├── bd/
│   └── init-scripts/         # Scripts SQL (auto-ejecutados)
│       ├── 01-tables-final.sql
│       ├── 02-functions-final.sql
│       ├── 03-seed-data.sql
│       └── 04-historical-data.sql
├── documentacion/
│   └── old-scripts/          # Backup scripts antiguos
├── docker-compose.yml        # Configuración orquestación
└── README.md
```

---

## ✅ Checklist de Verificación Post-Deploy

- [ ] 6 contenedores corriendo
- [ ] BD tiene datos (agentes, áreas, guardias)
- [ ] Todas las migraciones aplicadas 
- [ ] API retorna datos en `/api/personas/agentes/`
- [ ] Frontend carga en http://localhost:3000
- [ ] No hay errores en logs de Django
- [ ] No hay warnings de hot-reload en frontend

---

**Última actualización**: 27 de Noviembre 2025  
**Sistema**: GIGA - Gestión Integral de Guardias y Asistencias
