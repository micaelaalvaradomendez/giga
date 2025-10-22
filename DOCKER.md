Ejecución con Docker

Requisitos
- Docker Desktop 4.0+ (Windows/macOS) o Docker Engine (Linux)

Pasos
1) Duplicar variables de entorno:
   - PowerShell: `Copy-Item .env.example .env`
   - Linux/macOS: `cp .env.example .env`

2) Construir y levantar servicios:
   - `docker compose up -d --build`

3) Acceder
- Backend (Django): `http://localhost:8000`
- Frontend (Vite/SvelteKit): `http://localhost:5173`
- Base de datos (Postgres): `localhost:5432`

Servicios
- `db` (PostgreSQL 16): credenciales en `.env` (`DB_NAME`, `DB_USER`, `DB_PASSWORD`). Datos persistentes en el volumen `pgdata`.
- `back` (Django): corre con recarga en caliente, aplica migraciones automáticamente y expone el puerto `8000`.
- `front` (Vite dev server): expone `5173` y monta el código para hot reload.

Comandos útiles
- Ver logs: `docker compose logs -f back` (o `front`, `db`)
- Reiniciar un servicio: `docker compose restart back`
- Apagar todo: `docker compose down`
- Apagar y borrar volúmenes (incluye DB): `docker compose down -v`

Notas
- Edita `.env` para cambiar usuario/clave de Postgres, `SECRET_KEY` de Django, etc.
- En Windows, si 5432 ya está en uso, cambia el mapeo de puertos en `docker-compose.yml`.
- Si agregas dependencias nuevas en `back/requirements.txt` o `front/package.json`, reconstruye con `--build`.

