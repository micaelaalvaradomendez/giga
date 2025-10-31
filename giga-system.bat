@echo off
REM Script de gestión integral del sistema GIGA para Windows
REM Maneja Frontend (Svelte) + Backend (Django) + BD (PostgreSQL) + Nginx

setlocal enabledelayedexpansion

REM Configurar codificación UTF-8
chcp 65001 >nul

REM Colores ANSI para Windows 10+
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

REM Verificar si estamos en el directorio correcto
if not exist "docker-compose.yml" (
    echo %RED%❌ Error: No se encontró docker-compose.yml%NC%
    echo %YELLOW%Asegúrate de ejecutar este script desde el directorio raíz del proyecto GIGA%NC%
    pause
    exit /b 1
)

REM Función principal
if "%1"=="" goto :show_help
if "%1"=="help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="build" goto :build_all
if "%1"=="start" goto :start_all
if "%1"=="stop" goto :stop_all
if "%1"=="restart" goto :restart_all
if "%1"=="status" goto :status_all
if "%1"=="logs" goto :show_logs
if "%1"=="dev" goto :dev_mode
if "%1"=="build-db" goto :build_db
if "%1"=="build-backend" goto :build_backend
if "%1"=="build-frontend" goto :build_frontend
if "%1"=="build-nginx" goto :build_nginx
if "%1"=="migrate" goto :run_migrations
if "%1"=="db-shell" goto :db_shell
if "%1"=="db-backup" goto :db_backup
if "%1"=="shell-backend" goto :shell_backend
if "%1"=="shell-frontend" goto :shell_frontend
if "%1"=="health" goto :check_health
if "%1"=="urls" goto :show_urls
if "%1"=="clean" goto :clean_system

echo %RED%❌ Comando no reconocido: %1%NC%
echo.
goto :show_help

:show_help
echo %BLUE%🚀 GIGA - Sistema Completo%NC%
echo %PURPLE%Frontend (Svelte) + Backend (Django) + BD (PostgreSQL) + Nginx%NC%
echo.
echo Uso: %0 [comando] [opciones]
echo.
echo %CYAN%Comandos principales:%NC%
echo   build          - Construir todas las imágenes
echo   start          - Iniciar todos los servicios
echo   stop           - Detener todos los servicios
echo   restart        - Reiniciar todos los servicios
echo   status         - Estado de todos los servicios
echo   logs [servicio] - Ver logs (postgres/backend/frontend/nginx/all)
echo   dev            - Modo desarrollo completo
echo.
echo %CYAN%Comandos por servicio:%NC%
echo   build-db       - Solo base de datos
echo   build-backend  - Solo backend Django
echo   build-frontend - Solo frontend Svelte
echo   build-nginx    - Solo Nginx
echo.
echo %CYAN%Comandos de base de datos:%NC%
echo   db-shell       - Conectar a PostgreSQL
echo   db-backup      - Crear backup de BD
echo   migrate        - Ejecutar migraciones Django
echo.
echo %CYAN%Comandos de desarrollo:%NC%
echo   shell-backend  - Shell del contenedor Django
echo   shell-frontend - Shell del contenedor Svelte
echo   clean          - Limpiar volúmenes y contenedores
echo.
echo %CYAN%Utilidades:%NC%
echo   health         - Verificar salud de servicios
echo   urls           - Mostrar URLs de acceso
echo   help           - Mostrar esta ayuda
echo.
goto :end

:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Docker no está corriendo%NC%
    echo %YELLOW%Por favor, inicia Docker Desktop y vuelve a intentar%NC%
    pause
    exit /b 1
)
goto :eof

:show_urls
echo %BLUE%🌐 URLs de acceso:%NC%
echo %GREEN%Frontend (Aplicación principal): http://localhost%NC%
echo %GREEN%Backend API: http://localhost/api%NC%
echo %GREEN%Django Admin: http://localhost/admin%NC%
echo %GREEN%Nginx Status: http://localhost:8080/nginx_status%NC%
echo %GREEN%Nginx Info: http://localhost:8080/info%NC%
echo %GREEN%Health Check: http://localhost/health%NC%
echo.
echo %YELLOW%Puertos directos (para desarrollo):%NC%
echo %YELLOW%PostgreSQL: localhost:5432%NC%
echo %YELLOW%Django (directo): localhost:8000 (si está expuesto)%NC%
echo %YELLOW%Svelte (directo): localhost:3000 (si está expuesto)%NC%
goto :end

:check_health
echo %BLUE%🏥 Verificando salud de servicios...%NC%

for %%s in (giga-postgres giga-django giga-frontend giga-nginx) do (
    docker ps --filter "name=%%s" --filter "status=running" | find "%%s" >nul
    if !errorlevel! equ 0 (
        for /f %%h in ('docker inspect --format="{{.State.Health.Status}}" %%s 2^>nul') do (
            if "%%h"=="healthy" (
                echo %GREEN%✅ %%s: Saludable%NC%
            ) else if "%%h"=="unhealthy" (
                echo %RED%❌ %%s: No saludable%NC%
            ) else if "%%h"=="starting" (
                echo %YELLOW%⏳ %%s: Iniciando...%NC%
            ) else (
                echo %BLUE%ℹ️  %%s: Corriendo (sin healthcheck)%NC%
            )
        )
    ) else (
        echo %RED%❌ %%s: No está corriendo%NC%
    )
)
goto :end

:build_all
call :check_docker
echo %BLUE%🔨 Construyendo todas las imágenes...%NC%
docker-compose build --parallel
if errorlevel 1 (
    echo %RED%❌ Error al construir imágenes%NC%
    pause
    exit /b 1
)
echo %GREEN%✅ Todas las imágenes construidas%NC%
goto :end

:start_all
call :check_docker
echo %BLUE%🚀 Iniciando todos los servicios...%NC%
docker-compose up -d
if errorlevel 1 (
    echo %RED%❌ Error al iniciar servicios%NC%
    pause
    exit /b 1
)

echo %YELLOW%⏳ Esperando a que los servicios estén listos...%NC%
timeout /t 15 /nobreak >nul

call :check_health
echo.
call :show_urls
goto :end

:stop_all
call :check_docker
echo %BLUE%🛑 Deteniendo todos los servicios...%NC%
docker-compose down
echo %GREEN%✅ Servicios detenidos%NC%
goto :end

:restart_all
call :check_docker
call :stop_all
echo %YELLOW%⏳ Esperando 3 segundos...%NC%
timeout /t 3 /nobreak >nul
call :start_all
goto :end

:status_all
call :check_docker
docker-compose ps
echo.
call :check_health
goto :end

:show_logs
call :check_docker
set service=%2
if "%service%"=="" set service=all

if "%service%"=="postgres" goto :logs_postgres
if "%service%"=="db" goto :logs_postgres
if "%service%"=="bd" goto :logs_postgres
if "%service%"=="backend" goto :logs_backend
if "%service%"=="django" goto :logs_backend
if "%service%"=="frontend" goto :logs_frontend
if "%service%"=="svelte" goto :logs_frontend
if "%service%"=="nginx" goto :logs_nginx
if "%service%"=="proxy" goto :logs_nginx
goto :logs_all

:logs_postgres
echo %BLUE%📋 Logs de PostgreSQL:%NC%
docker-compose logs -f postgres
goto :end

:logs_backend
echo %BLUE%📋 Logs de Django Backend:%NC%
docker-compose logs -f backend
goto :end

:logs_frontend
echo %BLUE%📋 Logs de Svelte Frontend:%NC%
docker-compose logs -f frontend
goto :end

:logs_nginx
echo %BLUE%📋 Logs de Nginx:%NC%
docker-compose logs -f nginx
goto :end

:logs_all
echo %BLUE%📋 Logs de todos los servicios:%NC%
docker-compose logs -f
goto :end

:dev_mode
call :check_docker
echo %BLUE%🚀 Iniciando modo desarrollo completo...%NC%

REM Construir si es necesario
call :build_all

REM Iniciar servicios
call :start_all

echo %GREEN%✅ Modo desarrollo activo%NC%
echo %BLUE%📋 Siguiendo logs... (Ctrl+C para salir sin detener servicios)%NC%

REM Mostrar logs en tiempo real
docker-compose logs -f
goto :end

:build_db
call :check_docker
docker-compose build postgres
goto :end

:build_backend
call :check_docker
docker-compose build backend
goto :end

:build_frontend
call :check_docker
docker-compose build frontend
goto :end

:build_nginx
call :check_docker
docker-compose build nginx
goto :end

:run_migrations
call :check_docker
echo %BLUE%🔄 Ejecutando migraciones de Django...%NC%
docker-compose exec backend python manage.py migrate
if errorlevel 1 (
    echo %RED%❌ Error al ejecutar migraciones%NC%
    pause
    exit /b 1
)
echo %GREEN%✅ Migraciones completadas%NC%
goto :end

:db_shell
call :check_docker
echo %BLUE%🗃️  Conectando a PostgreSQL...%NC%
docker-compose exec postgres psql -U giga_user -d giga
goto :end

:db_backup
call :check_docker
REM Generar timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%%dt:~12,2%"
set "backup_file=giga_backup_%timestamp%.sql"

echo %BLUE%💾 Creando backup de base de datos...%NC%
docker-compose exec postgres pg_dump -U giga_user giga > "%backup_file%"
if errorlevel 1 (
    echo %RED%❌ Error al crear backup%NC%
    pause
    exit /b 1
)
echo %GREEN%✅ Backup creado: %backup_file%%NC%
goto :end

:shell_backend
call :check_docker
docker-compose exec backend bash
goto :end

:shell_frontend
call :check_docker
docker-compose exec frontend sh
goto :end

:clean_system
echo %YELLOW%⚠️  Esto eliminará contenedores, volúmenes y redes no utilizados%NC%
set /p confirm="¿Continuar? (y/N): "
if /i not "%confirm%"=="y" (
    echo %BLUE%❌ Limpieza cancelada%NC%
    goto :end
)

call :check_docker
echo %BLUE%🧹 Limpiando sistema...%NC%
docker-compose down -v --remove-orphans
docker system prune -f
docker volume prune -f
echo %GREEN%✅ Sistema limpiado%NC%
goto :end

:end
pause