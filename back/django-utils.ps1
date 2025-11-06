# Script de utilidades para GIGA Django Backend
# Uso: .\django-utils.ps1 [comando] [opciones]

param(
    [string]$Command = "",
    [string]$Options = ""
)

# Configuración
$DJANGO_CONTAINER = "giga-django"
$DB_CONTAINER = "giga-postgres"
$PROJECT_NAME = "giga"

# Función para mostrar ayuda
function Show-Help {
    Write-Host "🐍 GIGA Django Backend Utils" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Uso: .\django-utils.ps1 [comando] [opciones]"
    Write-Host ""
    Write-Host "Comandos de Docker:"
    Write-Host "  build          - Construir imagen de Django"
    Write-Host "  start          - Iniciar servicios (Django + BD)"
    Write-Host "  stop           - Detener servicios"
    Write-Host "  restart        - Reiniciar servicios"
    Write-Host "  logs           - Ver logs de Django"
    Write-Host "  shell          - Acceder a shell de Django"
    Write-Host "  status         - Estado de contenedores"
    Write-Host ""
    Write-Host "Comandos de Django:"
    Write-Host "  migrate        - Ejecutar migraciones"
    Write-Host "  makemigrations - Crear nuevas migraciones"
    Write-Host "  shell-django   - Shell de Django (manage.py shell)"
    Write-Host "  createsuperuser - Crear superusuario"
    Write-Host "  collectstatic  - Recopilar archivos estáticos"
    Write-Host "  test           - Ejecutar tests"
    Write-Host ""
    Write-Host "Comandos de Base de Datos:"
    Write-Host "  inspectdb      - Generar modelos desde BD externa"
    Write-Host "  dbshell        - Conectar a PostgreSQL"
    Write-Host "  resetdb        - Resetear base de datos (⚠️ DESTRUCTIVO)"
    Write-Host ""
    Write-Host "Comandos de Desarrollo:"
    Write-Host "  dev            - Modo desarrollo (build + start + logs)"
    Write-Host "  check          - Verificar configuración Django"
    Write-Host "  requirements   - Actualizar requirements.txt"
    Write-Host "  help           - Mostrar esta ayuda"
    Write-Host ""
}

# Función para verificar si Docker está corriendo
function Test-Docker {
    try {
        $null = docker info 2>$null
        return $true
    }
    catch {
        Write-Host "❌ Docker no está corriendo" -ForegroundColor Red
        exit 1
    }
}

# Función para construir la imagen
function Build-Image {
    Write-Host "🔨 Construyendo imagen de Django..." -ForegroundColor Blue
    docker-compose build django
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Imagen construida" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al construir imagen" -ForegroundColor Red
        exit 1
    }
}

# Función para iniciar servicios
function Start-Services {
    Write-Host "🚀 Iniciando servicios..." -ForegroundColor Blue
    docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al iniciar servicios" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Verificar estado de BD
    $dbReady = docker exec $DB_CONTAINER pg_isready -U giga_user -d giga 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL está listo" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL no está disponible" -ForegroundColor Red
        return
    }
    
    # Verificar Django
    $djangoReady = docker exec $DJANGO_CONTAINER python manage.py check --database default 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Django está funcionando correctamente" -ForegroundColor Green
        Write-Host "🌐 Django disponible en: http://localhost:8000" -ForegroundColor Blue
    } else {
        Write-Host "❌ Django tiene problemas" -ForegroundColor Red
    }
}

# Función para detener servicios
function Stop-Services {
    Write-Host "🛑 Deteniendo servicios..." -ForegroundColor Blue
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Servicios detenidos" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al detener servicios" -ForegroundColor Red
    }
}

# Función para mostrar logs
function Show-Logs {
    Write-Host "📋 Logs de Django:" -ForegroundColor Blue
    docker-compose logs -f django
}

# Función para acceder a shell
function Access-Shell {
    Write-Host "🐚 Accediendo a shell de contenedor Django..." -ForegroundColor Blue
    docker exec -it $DJANGO_CONTAINER bash
}

# Función para Django shell
function Invoke-DjangoShell {
    Write-Host "🐍 Iniciando Django shell..." -ForegroundColor Blue
    docker exec -it $DJANGO_CONTAINER python manage.py shell
}

# Función para ejecutar migraciones
function Invoke-Migrations {
    Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor Blue
    docker exec $DJANGO_CONTAINER python manage.py migrate
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migraciones aplicadas correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al aplicar migraciones" -ForegroundColor Red
        exit 1
    }
}

# Función para crear migraciones
function New-Migrations {
    Write-Host "📝 Creando migraciones..." -ForegroundColor Blue
    docker exec $DJANGO_CONTAINER python manage.py makemigrations
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migraciones creadas" -ForegroundColor Green
    } else {
        Write-Host "⚠️ No hay cambios para migrar" -ForegroundColor Yellow
    }
}

# Función para inspeccionar BD y generar modelos
function Get-DatabaseModels {
    Write-Host "🔍 Inspeccionando base de datos externa..." -ForegroundColor Blue
    Write-Host "📋 Esto generará modelos Python basados en las tablas existentes" -ForegroundColor Yellow
    Write-Host "📋 Los modelos tendrán managed = False para no alterar la BD" -ForegroundColor Yellow
    
    # Crear directorio para modelos si no existe
    docker exec $DJANGO_CONTAINER mkdir -p /app/generated_models
    
    # Generar modelos
    docker exec $DJANGO_CONTAINER python manage.py inspectdb | Out-File -FilePath "generated_models.py" -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Modelos generados en generated_models.py" -ForegroundColor Green
        Write-Host "📝 Revisa el archivo y adapta según necesites" -ForegroundColor Blue
        Write-Host "📝 Los modelos están marcados como managed = False" -ForegroundColor Blue
    } else {
        Write-Host "❌ Error al generar modelos" -ForegroundColor Red
        exit 1
    }
}

# Función para acceder a shell de BD
function Connect-DatabaseShell {
    Write-Host "🗃️ Conectando a PostgreSQL..." -ForegroundColor Blue
    docker exec -it $DB_CONTAINER psql -U giga_user -d giga
}

# Función para crear superusuario
function New-SuperUser {
    Write-Host "👤 Creando superusuario..." -ForegroundColor Blue
    docker exec -it $DJANGO_CONTAINER python manage.py createsuperuser
}

# Función para verificar configuración
function Test-DjangoConfig {
    Write-Host "🔍 Verificando configuración de Django..." -ForegroundColor Blue
    docker exec $DJANGO_CONTAINER python manage.py check
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Configuración correcta" -ForegroundColor Green
    } else {
        Write-Host "❌ Hay problemas en la configuración" -ForegroundColor Red
        exit 1
    }
}

# Función para modo desarrollo
function Start-DevMode {
    Write-Host "🚀 Iniciando modo desarrollo..." -ForegroundColor Blue
    Build-Image
    Start-Services
    Write-Host "✅ Servicios iniciados en modo desarrollo" -ForegroundColor Green
    Write-Host "📋 Siguiendo logs... (Ctrl+C para salir)" -ForegroundColor Blue
    Show-Logs
}

# Función para mostrar estado
function Show-Status {
    Write-Host "📊 Estado de los servicios:" -ForegroundColor Blue
    docker-compose ps
    Write-Host ""
    
    # Verificar Django
    $djangoCheck = docker exec $DJANGO_CONTAINER python manage.py check --database default 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Django está funcionando correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Django no está disponible" -ForegroundColor Red
    }
    
    # Verificar BD
    $dbReady = docker exec $DB_CONTAINER pg_isready -U giga_user -d giga 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL está funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL no está disponible" -ForegroundColor Red
    }
}

# Función para resetear BD
function Reset-Database {
    Write-Host "⚠️ PELIGRO: Esto eliminará TODOS los datos de la base de datos" -ForegroundColor Red
    Write-Host "¿Estás seguro de que quieres resetear la base de datos?" -ForegroundColor Yellow
    $confirm = Read-Host "Escribe 'RESET_DB' para continuar"
    
    if ($confirm -ne "RESET_DB") {
        Write-Host "❌ Reseteo cancelado" -ForegroundColor Blue
        exit 0
    }
    
    Write-Host "🗑️ Reseteando base de datos..." -ForegroundColor Blue
    docker-compose down -v
    docker-compose up -d postgres
    
    if ($LASTEXITCODE -eq 0) {
        # Esperar a que la BD esté lista
        Start-Sleep -Seconds 15
        Write-Host "✅ Base de datos reseteada" -ForegroundColor Green
        Write-Host "📋 Ejecuta 'migrate' para aplicar migraciones de Django" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Error al resetear base de datos" -ForegroundColor Red
    }
}

# Función para recopilar archivos estáticos
function Invoke-CollectStatic {
    Write-Host "📁 Recopilando archivos estáticos..." -ForegroundColor Blue
    docker exec $DJANGO_CONTAINER python manage.py collectstatic --noinput
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Archivos estáticos recopilados" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al recopilar archivos estáticos" -ForegroundColor Red
    }
}

# Función para ejecutar tests
function Invoke-Tests {
    Write-Host "🧪 Ejecutando tests..." -ForegroundColor Blue
    docker exec $DJANGO_CONTAINER python manage.py test
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tests completados" -ForegroundColor Green
    } else {
        Write-Host "❌ Algunos tests fallaron" -ForegroundColor Red
    }
}

# Función para mostrar comando de requirements
function Show-RequirementsCommand {
    Write-Host "📦 Para actualizar requirements.txt:" -ForegroundColor Blue
    Write-Host "Ejecutar en el contenedor Django:" -ForegroundColor Yellow
    Write-Host "docker exec $DJANGO_CONTAINER pip freeze > requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O usar el shell del contenedor:" -ForegroundColor Yellow
    Write-Host ".\django-utils.ps1 shell" -ForegroundColor Cyan
    Write-Host "pip freeze > requirements.txt" -ForegroundColor Cyan
}

# Script principal
if ([string]::IsNullOrEmpty($Command)) {
    Show-Help
    exit 0
}

# Verificar Docker para todos los comandos excepto help y requirements
if ($Command -ne "help" -and $Command -ne "requirements") {
    Test-Docker
}

switch ($Command.ToLower()) {
    "build" {
        Build-Image
    }
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Stop-Services
        Start-Services
    }
    "logs" {
        Show-Logs
    }
    "shell" {
        Access-Shell
    }
    "shell-django" {
        Invoke-DjangoShell
    }
    "migrate" {
        Invoke-Migrations
    }
    "makemigrations" {
        New-Migrations
    }
    "inspectdb" {
        Get-DatabaseModels
    }
    "dbshell" {
        Connect-DatabaseShell
    }
    "createsuperuser" {
        New-SuperUser
    }
    "check" {
        Test-DjangoConfig
    }
    "dev" {
        Start-DevMode
    }
    "status" {
        Show-Status
    }
    "resetdb" {
        Reset-Database
    }
    "collectstatic" {
        Invoke-CollectStatic
    }
    "test" {
        Invoke-Tests
    }
    "requirements" {
        Show-RequirementsCommand
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Comando no reconocido: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}