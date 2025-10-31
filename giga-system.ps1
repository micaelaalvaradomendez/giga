#Requires -Version 5.1

<#
.SYNOPSIS
    Script de gestión integral del sistema GIGA para Windows
    
.DESCRIPTION
    Maneja Frontend (Svelte) + Backend (Django) + BD (PostgreSQL) + Nginx
    Compatible con PowerShell 5.1+ y PowerShell Core
    
.PARAMETER Command
    Comando a ejecutar (build, start, stop, restart, status, logs, dev, etc.)
    
.PARAMETER Service
    Servicio específico para comandos como logs (postgres, backend, frontend, nginx, all)
    
.EXAMPLE
    .\giga-system.ps1 dev
    Inicia el modo desarrollo completo
    
.EXAMPLE
    .\giga-system.ps1 logs backend
    Muestra los logs del backend Django
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('build', 'start', 'stop', 'restart', 'status', 'logs', 'dev', 
                 'build-db', 'build-backend', 'build-frontend', 'build-nginx',
                 'migrate', 'db-shell', 'db-backup', 'shell-backend', 'shell-frontend',
                 'health', 'urls', 'clean', 'help')]
    [string]$Command = 'help',
    
    [Parameter(Position = 1)]
    [ValidateSet('postgres', 'db', 'bd', 'backend', 'django', 'frontend', 'svelte', 'nginx', 'proxy', 'all')]
    [string]$Service = 'all'
)

# Configurar codificación UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Colores para output
$Colors = @{
    Red    = "`e[91m"
    Green  = "`e[92m"
    Yellow = "`e[93m"
    Blue   = "`e[94m"
    Purple = "`e[95m"
    Cyan   = "`e[96m"
    Reset  = "`e[0m"
}

# Función para escribir texto con color
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = 'Reset'
    )
    Write-Host "$($Colors[$Color])$Text$($Colors.Reset)"
}

# Función para verificar si estamos en el directorio correcto
function Test-ProjectRoot {
    if (-not (Test-Path "docker-compose.yml")) {
        Write-ColorText "❌ Error: No se encontró docker-compose.yml" -Color Red
        Write-ColorText "Asegúrate de ejecutar este script desde el directorio raíz del proyecto GIGA" -Color Yellow
        exit 1
    }
}

# Función para verificar Docker
function Test-Docker {
    try {
        $null = docker info 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker no responde"
        }
    }
    catch {
        Write-ColorText "❌ Docker no está corriendo" -Color Red
        Write-ColorText "Por favor, inicia Docker Desktop y vuelve a intentar" -Color Yellow
        exit 1
    }
}

# Función para mostrar ayuda
function Show-Help {
    Write-ColorText "🚀 GIGA - Sistema Completo" -Color Blue
    Write-ColorText "Frontend (Svelte) + Backend (Django) + BD (PostgreSQL) + Nginx" -Color Purple
    Write-Host ""
    Write-Host "Uso: .\giga-system.ps1 [comando] [opciones]"
    Write-Host ""
    Write-ColorText "Comandos principales:" -Color Cyan
    Write-Host "  build          - Construir todas las imágenes"
    Write-Host "  start          - Iniciar todos los servicios"
    Write-Host "  stop           - Detener todos los servicios"
    Write-Host "  restart        - Reiniciar todos los servicios"
    Write-Host "  status         - Estado de todos los servicios"
    Write-Host "  logs [servicio] - Ver logs (postgres/backend/frontend/nginx/all)"
    Write-Host "  dev            - Modo desarrollo completo"
    Write-Host ""
    Write-ColorText "Comandos por servicio:" -Color Cyan
    Write-Host "  build-db       - Solo base de datos"
    Write-Host "  build-backend  - Solo backend Django"
    Write-Host "  build-frontend - Solo frontend Svelte"
    Write-Host "  build-nginx    - Solo Nginx"
    Write-Host ""
    Write-ColorText "Comandos de base de datos:" -Color Cyan
    Write-Host "  db-shell       - Conectar a PostgreSQL"
    Write-Host "  db-backup      - Crear backup de BD"
    Write-Host "  migrate        - Ejecutar migraciones Django"
    Write-Host ""
    Write-ColorText "Comandos de desarrollo:" -Color Cyan
    Write-Host "  shell-backend  - Shell del contenedor Django"
    Write-Host "  shell-frontend - Shell del contenedor Svelte"
    Write-Host "  clean          - Limpiar volúmenes y contenedores"
    Write-Host ""
    Write-ColorText "Utilidades:" -Color Cyan
    Write-Host "  health         - Verificar salud de servicios"
    Write-Host "  urls           - Mostrar URLs de acceso"
    Write-Host "  help           - Mostrar esta ayuda"
    Write-Host ""
}

# Función para mostrar URLs de acceso
function Show-URLs {
    Write-ColorText "🌐 URLs de acceso:" -Color Blue
    Write-ColorText "Frontend (Aplicación principal): http://localhost" -Color Green
    Write-ColorText "Backend API: http://localhost/api" -Color Green
    Write-ColorText "Django Admin: http://localhost/admin" -Color Green
    Write-ColorText "Nginx Status: http://localhost:8080/nginx_status" -Color Green
    Write-ColorText "Nginx Info: http://localhost:8080/info" -Color Green
    Write-ColorText "Health Check: http://localhost/health" -Color Green
    Write-Host ""
    Write-ColorText "Puertos directos (para desarrollo):" -Color Yellow
    Write-ColorText "PostgreSQL: localhost:5432" -Color Yellow
    Write-ColorText "Django (directo): localhost:8000 (si está expuesto)" -Color Yellow
    Write-ColorText "Svelte (directo): localhost:3000 (si está expuesto)" -Color Yellow
}

# Función para verificar salud de servicios
function Test-ServicesHealth {
    Write-ColorText "🏥 Verificando salud de servicios..." -Color Blue
    
    $services = @('giga-postgres', 'giga-django', 'giga-frontend', 'giga-nginx')
    
    foreach ($service in $services) {
        $running = docker ps --filter "name=$service" --filter "status=running" --format "{{.Names}}" 2>$null
        
        if ($running -eq $service) {
            try {
                $health = docker inspect --format='{{.State.Health.Status}}' $service 2>$null
                
                switch ($health) {
                    'healthy' {
                        Write-ColorText "✅ $service`: Saludable" -Color Green
                    }
                    'unhealthy' {
                        Write-ColorText "❌ $service`: No saludable" -Color Red
                    }
                    'starting' {
                        Write-ColorText "⏳ $service`: Iniciando..." -Color Yellow
                    }
                    default {
                        Write-ColorText "ℹ️  $service`: Corriendo (sin healthcheck)" -Color Blue
                    }
                }
            }
            catch {
                Write-ColorText "ℹ️  $service`: Corriendo (sin healthcheck)" -Color Blue
            }
        }
        else {
            Write-ColorText "❌ $service`: No está corriendo" -Color Red
        }
    }
}

# Función para construir todas las imágenes
function Build-AllImages {
    Test-Docker
    Write-ColorText "🔨 Construyendo todas las imágenes..." -Color Blue
    
    docker-compose build --parallel
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "❌ Error al construir imágenes" -Color Red
        exit 1
    }
    
    Write-ColorText "✅ Todas las imágenes construidas" -Color Green
}

# Función para iniciar todos los servicios
function Start-AllServices {
    Test-Docker
    Write-ColorText "🚀 Iniciando todos los servicios..." -Color Blue
    
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "❌ Error al iniciar servicios" -Color Red
        exit 1
    }
    
    Write-ColorText "⏳ Esperando a que los servicios estén listos..." -Color Yellow
    Start-Sleep -Seconds 15
    
    Test-ServicesHealth
    Write-Host ""
    Show-URLs
}

# Función para detener todos los servicios
function Stop-AllServices {
    Test-Docker
    Write-ColorText "🛑 Deteniendo todos los servicios..." -Color Blue
    docker-compose down
    Write-ColorText "✅ Servicios detenidos" -Color Green
}

# Función para reiniciar todos los servicios
function Restart-AllServices {
    Stop-AllServices
    Write-ColorText "⏳ Esperando 3 segundos..." -Color Yellow
    Start-Sleep -Seconds 3
    Start-AllServices
}

# Función para mostrar estado
function Show-Status {
    Test-Docker
    docker-compose ps
    Write-Host ""
    Test-ServicesHealth
}

# Función para mostrar logs
function Show-Logs {
    param([string]$ServiceName = 'all')
    
    Test-Docker
    
    switch ($ServiceName.ToLower()) {
        { $_ -in @('postgres', 'db', 'bd') } {
            Write-ColorText "📋 Logs de PostgreSQL:" -Color Blue
            docker-compose logs -f postgres
        }
        { $_ -in @('backend', 'django') } {
            Write-ColorText "📋 Logs de Django Backend:" -Color Blue
            docker-compose logs -f backend
        }
        { $_ -in @('frontend', 'svelte') } {
            Write-ColorText "📋 Logs de Svelte Frontend:" -Color Blue
            docker-compose logs -f frontend
        }
        { $_ -in @('nginx', 'proxy') } {
            Write-ColorText "📋 Logs de Nginx:" -Color Blue
            docker-compose logs -f nginx
        }
        default {
            Write-ColorText "📋 Logs de todos los servicios:" -Color Blue
            docker-compose logs -f
        }
    }
}

# Función para modo desarrollo
function Start-DevMode {
    Test-Docker
    Write-ColorText "🚀 Iniciando modo desarrollo completo..." -Color Blue
    
    # Construir si es necesario
    Build-AllImages
    
    # Iniciar servicios
    Start-AllServices
    
    Write-ColorText "✅ Modo desarrollo activo" -Color Green
    Write-ColorText "📋 Siguiendo logs... (Ctrl+C para salir sin detener servicios)" -Color Blue
    
    # Mostrar logs en tiempo real
    docker-compose logs -f
}

# Función para ejecutar migraciones
function Invoke-Migrations {
    Test-Docker
    Write-ColorText "🔄 Ejecutando migraciones de Django..." -Color Blue
    
    docker-compose exec backend python manage.py migrate
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "❌ Error al ejecutar migraciones" -Color Red
        exit 1
    }
    
    Write-ColorText "✅ Migraciones completadas" -Color Green
}

# Función para shell de base de datos
function Connect-DatabaseShell {
    Test-Docker
    Write-ColorText "🗃️  Conectando a PostgreSQL..." -Color Blue
    docker-compose exec postgres psql -U giga_user -d giga
}

# Función para backup de base de datos
function New-DatabaseBackup {
    Test-Docker
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "giga_backup_$timestamp.sql"
    
    Write-ColorText "💾 Creando backup de base de datos..." -Color Blue
    
    docker-compose exec postgres pg_dump -U giga_user giga > $backupFile
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "❌ Error al crear backup" -Color Red
        exit 1
    }
    
    Write-ColorText "✅ Backup creado: $backupFile" -Color Green
}

# Función para limpiar sistema
function Clear-System {
    Write-ColorText "⚠️  Esto eliminará contenedores, volúmenes y redes no utilizados" -Color Yellow
    
    $confirm = Read-Host "¿Continuar? (y/N)"
    if ($confirm.ToLower() -ne 'y') {
        Write-ColorText "❌ Limpieza cancelada" -Color Blue
        return
    }
    
    Test-Docker
    Write-ColorText "🧹 Limpiando sistema..." -Color Blue
    
    docker-compose down -v --remove-orphans
    docker system prune -f
    docker volume prune -f
    
    Write-ColorText "✅ Sistema limpiado" -Color Green
}

# Función para construir servicios específicos
function Build-Service {
    param([string]$ServiceName)
    
    Test-Docker
    docker-compose build $ServiceName
}

# Función para shell de contenedores
function Connect-ServiceShell {
    param([string]$ServiceName, [string]$Shell = 'bash')
    
    Test-Docker
    docker-compose exec $ServiceName $Shell
}

# Verificar directorio del proyecto
Test-ProjectRoot

# Ejecutar comando principal
switch ($Command.ToLower()) {
    'build' { Build-AllImages }
    'start' { Start-AllServices }
    'stop' { Stop-AllServices }
    'restart' { Restart-AllServices }
    'status' { Show-Status }
    'logs' { Show-Logs -ServiceName $Service }
    'dev' { Start-DevMode }
    'build-db' { Build-Service -ServiceName 'postgres' }
    'build-backend' { Build-Service -ServiceName 'backend' }
    'build-frontend' { Build-Service -ServiceName 'frontend' }
    'build-nginx' { Build-Service -ServiceName 'nginx' }
    'migrate' { Invoke-Migrations }
    'db-shell' { Connect-DatabaseShell }
    'db-backup' { New-DatabaseBackup }
    'shell-backend' { Connect-ServiceShell -ServiceName 'backend' -Shell 'bash' }
    'shell-frontend' { Connect-ServiceShell -ServiceName 'frontend' -Shell 'sh' }
    'health' { Test-ServicesHealth }
    'urls' { Show-URLs }
    'clean' { Clear-System }
    'help' { Show-Help }
    default { Show-Help }
}