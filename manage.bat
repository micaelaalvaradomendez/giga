@echo off
REM ===========================================
REM SCRIPT DE GESTIÓN DE GIGA PARA WINDOWS
REM ===========================================

setlocal enabledelayedexpansion

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose no está disponible
    echo Asegúrate de que Docker Desktop esté ejecutándose
    pause
    exit /b 1
)

REM Función de ayuda
if "%1"=="help" goto :show_help
if "%1"=="" goto :show_help

REM Verificar archivo .env
if not exist .env (
    echo ⚠️  Archivo .env no encontrado, creando desde .env.example...
    copy .env.example .env
    echo ✅ Archivo .env creado. Por favor, revisa y ajusta las configuraciones.
)

REM Comandos principales
if "%1"=="dev" goto :dev_start
if "%1"=="prod" goto :prod_start
if "%1"=="stop" goto :stop_services
if "%1"=="restart" goto :restart_services
if "%1"=="build" goto :build_images
if "%1"=="logs" goto :show_logs
if "%1"=="shell" goto :backend_shell
if "%1"=="db-shell" goto :db_shell
if "%1"=="migrate" goto :run_migrations
if "%1"=="pnpm" goto :run_pnpm
if "%1"=="clean" goto :clean_all
if "%1"=="status" goto :show_status

echo ❌ Comando desconocido: %1
goto :show_help

:show_help
echo.
echo 🚀 GIGA - Sistema de Gestión Docker (Windows)
echo.
echo USO:
echo     manage.bat [COMANDO] [OPCIONES]
echo.
echo COMANDOS:
echo     dev             Iniciar entorno de desarrollo
echo     prod            Iniciar entorno de producción
echo     stop            Detener todos los servicios
echo     restart         Reiniciar todos los servicios
echo     build           Construir todas las imágenes
echo     logs            Ver logs de los servicios
echo     shell           Acceder al shell del backend
echo     db-shell        Acceder al shell de PostgreSQL
echo     migrate         Ejecutar migraciones de Django
echo     pnpm            Ejecutar comandos pnpm en el frontend
echo     clean           Limpiar volúmenes y contenedores
echo     status          Ver estado de los servicios
echo     help            Mostrar esta ayuda
echo.
echo EJEMPLOS:
echo     manage.bat dev                 # Iniciar desarrollo
echo     manage.bat prod                # Iniciar producción
echo     manage.bat logs backend        # Ver logs del backend
echo     manage.bat pnpm install        # Instalar dependencias con pnpm
echo.
goto :end

:dev_start
echo ℹ️  Iniciando entorno de desarrollo...
docker-compose -f docker-compose.dev.yml up --build -d
if %errorlevel% equ 0 (
    echo ✅ Entorno de desarrollo iniciado
    echo ℹ️  Frontend: http://localhost:5173
    echo ℹ️  Backend: http://localhost:8000
    echo ℹ️  Base de datos: localhost:5434
) else (
    echo ❌ Error al iniciar el entorno de desarrollo
)
goto :end

:prod_start
echo ℹ️  Iniciando entorno de producción...
docker-compose -f docker-compose.prod.yml up --build -d
if %errorlevel% equ 0 (
    echo ✅ Entorno de producción iniciado
    echo ℹ️  Aplicación: http://localhost
) else (
    echo ❌ Error al iniciar el entorno de producción
)
goto :end

:stop_services
echo ℹ️  Deteniendo todos los servicios...
docker-compose -f docker-compose.dev.yml down 2>nul
docker-compose -f docker-compose.prod.yml down 2>nul
docker-compose down 2>nul
echo ✅ Servicios detenidos
goto :end

:restart_services
echo ℹ️  Reiniciando servicios...
call :stop_services
if "%2"=="prod" (
    call :prod_start
) else (
    call :dev_start
)
goto :end

:build_images
echo ℹ️  Construyendo imágenes Docker...
docker-compose -f docker-compose.dev.yml build --no-cache
echo ✅ Imágenes construidas
goto :end

:show_logs
if "%2"=="" (
    echo ℹ️  Mostrando logs de todos los servicios...
    docker-compose -f docker-compose.dev.yml logs -f 2>nul || docker-compose -f docker-compose.prod.yml logs -f
) else (
    echo ℹ️  Mostrando logs de: %2
    docker-compose -f docker-compose.dev.yml logs -f %2 2>nul || docker-compose -f docker-compose.prod.yml logs -f %2
)
goto :end

:backend_shell
echo ℹ️  Accediendo al shell del backend...
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell 2>nul || docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
goto :end

:db_shell
echo ℹ️  Accediendo al shell de PostgreSQL...
docker-compose -f docker-compose.dev.yml exec db psql -U giga_user -d giga 2>nul || docker-compose -f docker-compose.prod.yml exec db psql -U giga_user -d giga
goto :end

:run_migrations
echo ℹ️  Ejecutando migraciones de Django...
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate 2>nul || docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
echo ✅ Migraciones completadas
goto :end

:run_pnpm
echo ℹ️  Ejecutando: pnpm %2 %3 %4 %5
docker-compose -f docker-compose.dev.yml exec frontend pnpm %2 %3 %4 %5 2>nul || docker-compose -f docker-compose.prod.yml exec frontend pnpm %2 %3 %4 %5
goto :end

:clean_all
echo ⚠️  ¿Estás seguro de que quieres limpiar todos los volúmenes y contenedores? (S/N):
set /p response=
if /i "%response%"=="S" (
    echo ℹ️  Limpiando contenedores, volúmenes e imágenes...
    call :stop_services
    docker system prune -af --volumes
    echo ✅ Limpieza completada
) else (
    echo ℹ️  Operación cancelada
)
goto :end

:show_status
echo ℹ️  Estado de los servicios:
echo.
docker-compose -f docker-compose.dev.yml ps 2>nul || docker-compose -f docker-compose.prod.yml ps
goto :end

:end
pause