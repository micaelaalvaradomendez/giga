# Sistema GIGA - Resolución de Errores de Inicialización de Entorno Docker
## 🎯 Objetivo
Documentar y resolver la cadena de errores que impedía el correcto inicio y el estado healthy de los servicios de PostgreSQL y Django (Backend) en el entorno local de Docker Compose.

Resultado: Todos los servicios principales están operativos y la aplicación es accesible en http://localhost.

## 🛠️ 1. Correcciones en PostgreSQL y Scripts SQL
Problema  - Descripción, Solución - Archivos Modificados
- Formato de Línea (CRLF) 
- - Los scripts de Linux (.sh y .sql) usaban terminaciones de línea de Windows (CRLF), lo que causaba errores de sintaxis en el contenedor
- - - .gitattributes (Añadido * text=auto eol=lf) y 01-init-database.sh (Convertido a formato LF)

- Errores de Datos en INSERT
- - Fallos en 03-seed-data.sql por violaciones a restricciones NOT NULL o columnas inexistentes.
- - 1: Se agregó la columna vigente_desde con valor NOW() en parametros_area y reglas_plus.Solución 
- - 2: Se eliminó la referencia a la columna descripcion en reglas_plus.
- - - 03-seed-data.sqlSolución 
## 🛠️ 2. Correcciones en Django (Backend)
Problema  - Descripción, Solución - Archivos Modificados
- Módulos Faltantes
- - Múltiples ModuleNotFoundError (ej. django_extensions, django_filters) en la inicialización del Backend.
- - - requirements.txt (Se agregaron django-extensions y django-filter).
- Conflicto de Migraciones
- - El Backend falló al migrar por primera vez (DuplicateTable) porque las tablas ya existían por el script SQL.
- - - N/A (Solución de ejecución manual)

## ⚙️ 3. Guía de Inicialización Limpia (Comandos)
Para levantar el entorno después de aplicar las correcciones (o si se desea inicializar la DB desde cero), se debe seguir esta secuencia:

### 1 Limpiar la base de datos local y reconstruir el backend:
- Bash
- docker compose down
- docker volume rm giga_postgres_data
- docker compose up -d --build

### 2 Sincronizar Migraciones de Django: Esto resuelve el conflicto de tablas existentes (evitando el error DuplicateTable).
- Bash
- docker exec giga-django python manage.py migrate --fake-initial

### 3 Verificación Final: La aplicación debería estar accesible en http://localhost

## 4 Historial de Commits (fix/postgres-init-data)
- Esta es la secuencia de commits que documenta la solución completa:

- Fix: Inicialización de Docker: Formato LF y .gitattributes.

- Fix: 03-seed-data.sql. Corregidos errores de 'vigente_desde' y 'descripcion'.

- Fix: Añadida dependencia 'django-extensions' para resolver ModuleNotFoundError...

- Fix: Añadida dependencia 'django-filter' para resolver el segundo ModuleNotFoundError...

- Fix: Forzado reconocimiento de migraciones básicas con --fake-initial.

