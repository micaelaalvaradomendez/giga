# Script de utilidades para la base de datos GIGA PostgreSQL
# Uso: .\db-utils.ps1 [comando] [opciones]

param(
    [string]$Command = "",
    [string]$BackupFile = ""
)

# Configuración
$DB_CONTAINER = "giga-postgres"
$DB_NAME = "giga"
$DB_USER = "giga_user"
$DB_PASSWORD = "giga2025"
$BACKUP_DIR = ".\backups"

# Función para mostrar ayuda
function Show-Help {
    Write-Host "🐘 GIGA PostgreSQL Database Utils" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Uso: .\db-utils.ps1 [comando] [opciones]"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  start          - Iniciar los servicios de base de datos"
    Write-Host "  stop           - Detener los servicios de base de datos"
    Write-Host "  restart        - Reiniciar los servicios"
    Write-Host "  status         - Mostrar estado de los servicios"
    Write-Host "  logs           - Mostrar logs de PostgreSQL"
    Write-Host "  shell          - Conectar a PostgreSQL (psql)"
    Write-Host "  backup         - Crear backup de la base de datos"
    Write-Host "  restore [file] - Restaurar backup desde archivo"
    Write-Host "  reset          - Resetear base de datos (⚠️  DESTRUCTIVO)"
    Write-Host "  admin          - Iniciar PgAdmin (puerto 8080)"
    Write-Host "  build          - Construir imagen de Docker"
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

# Función para iniciar servicios
function Start-Services {
    Write-Host "🚀 Iniciando servicios de base de datos..." -ForegroundColor Blue
    docker-compose up -d postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Servicios iniciados" -ForegroundColor Green
        
        # Esperar a que la base de datos esté lista
        Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
        
        $timeout = 60
        $elapsed = 0
        do {
            Start-Sleep -Seconds 2
            $elapsed += 2
            $ready = docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME 2>$null
        } while ($LASTEXITCODE -ne 0 -and $elapsed -lt $timeout)
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL está listo" -ForegroundColor Green
        } else {
            Write-Host "❌ Timeout esperando a PostgreSQL" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Error al iniciar servicios" -ForegroundColor Red
        exit 1
    }
}

# Función para detener servicios
function Stop-Services {
    Write-Host "🛑 Deteniendo servicios de base de datos..." -ForegroundColor Blue
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Servicios detenidos" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al detener servicios" -ForegroundColor Red
    }
}

# Función para mostrar logs
function Show-Logs {
    Write-Host "📋 Logs de PostgreSQL:" -ForegroundColor Blue
    docker-compose logs -f postgres
}

# Función para conectar a la base de datos
function Connect-Database {
    Write-Host "🔗 Conectando a PostgreSQL..." -ForegroundColor Blue
    docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
}

# Función para crear backup
function New-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$BACKUP_DIR\giga_backup_$timestamp.sql"
    
    Write-Host "💾 Creando backup..." -ForegroundColor Blue
    
    # Crear directorio si no existe
    if (!(Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }
    
    # Crear backup
    docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME | Out-File -FilePath $backupFile -Encoding UTF8
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $backupFile)) {
        Write-Host "✅ Backup creado: $backupFile" -ForegroundColor Green
        
        # Comprimir el backup
        try {
            Compress-Archive -Path $backupFile -DestinationPath "$backupFile.zip" -Force
            Remove-Item $backupFile -Force
            Write-Host "✅ Backup comprimido: $backupFile.zip" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Backup creado pero no se pudo comprimir: $backupFile" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Error al crear backup" -ForegroundColor Red
        exit 1
    }
}

# Función para restaurar backup
function Restore-Backup {
    param([string]$BackupFile)
    
    if ([string]::IsNullOrEmpty($BackupFile)) {
        Write-Host "❌ Debes especificar el archivo de backup" -ForegroundColor Red
        Write-Host "Uso: .\db-utils.ps1 restore <archivo_backup>"
        exit 1
    }
    
    if (!(Test-Path $BackupFile)) {
        Write-Host "❌ Archivo de backup no encontrado: $BackupFile" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "⚠️  ¿Estás seguro de restaurar el backup? Esto sobrescribirá los datos actuales." -ForegroundColor Yellow
    $confirm = Read-Host "Escribe 'YES' para continuar"
    
    if ($confirm -ne "YES") {
        Write-Host "❌ Restauración cancelada" -ForegroundColor Blue
        exit 0
    }
    
    Write-Host "📥 Restaurando backup..." -ForegroundColor Blue
    
    # Si el archivo está comprimido, descomprimirlo temporalmente
    if ($BackupFile.EndsWith(".zip")) {
        $tempDir = "$env:TEMP\giga_restore_$(Get-Random)"
        Expand-Archive -Path $BackupFile -DestinationPath $tempDir -Force
        $sqlFile = Get-ChildItem -Path $tempDir -Filter "*.sql" | Select-Object -First 1
        
        if ($sqlFile) {
            Get-Content $sqlFile.FullName | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
            Remove-Item $tempDir -Recurse -Force
        } else {
            Write-Host "❌ No se encontró archivo SQL en el backup comprimido" -ForegroundColor Red
            Remove-Item $tempDir -Recurse -Force
            exit 1
        }
    } else {
        Get-Content $BackupFile | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backup restaurado correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al restaurar backup" -ForegroundColor Red
        exit 1
    }
}

# Función para resetear la base de datos
function Reset-Database {
    Write-Host "⚠️  PELIGRO: Esto eliminará TODOS los datos de la base de datos" -ForegroundColor Red
    Write-Host "¿Estás seguro de que quieres resetear la base de datos?" -ForegroundColor Yellow
    $confirm = Read-Host "Escribe 'DELETE_ALL_DATA' para continuar"
    
    if ($confirm -ne "DELETE_ALL_DATA") {
        Write-Host "❌ Reseteo cancelado" -ForegroundColor Blue
        exit 0
    }
    
    Write-Host "🗑️  Reseteando base de datos..." -ForegroundColor Blue
    docker-compose down -v
    docker-compose up -d postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de datos reseteada" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al resetear base de datos" -ForegroundColor Red
    }
}

# Función para iniciar PgAdmin
function Start-Admin {
    Write-Host "🎛️  Iniciando PgAdmin..." -ForegroundColor Blue
    docker-compose --profile admin up -d --no-deps pgadmin
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PgAdmin disponible en: http://localhost:8081" -ForegroundColor Green
        Write-Host "📧 Usuario: admin@giga.dev" -ForegroundColor Yellow
        Write-Host "🔑 Contraseña: admin2025" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Error al iniciar PgAdmin" -ForegroundColor Red
    }
}

# Función para construir imagen
function Build-Image {
    Write-Host "🔨 Construyendo imagen de PostgreSQL..." -ForegroundColor Blue
    docker-compose build postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Imagen construida" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al construir imagen" -ForegroundColor Red
    }
}

# Función para mostrar estado
function Show-Status {
    Write-Host "📊 Estado de los servicios:" -ForegroundColor Blue
    docker-compose ps
    Write-Host ""
    
    $ready = docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL está funcionando correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL no está disponible" -ForegroundColor Red
    }
}

# Script principal
if ([string]::IsNullOrEmpty($Command)) {
    Show-Help
    exit 0
}

# Verificar Docker para todos los comandos excepto help
if ($Command -ne "help") {
    Test-Docker
}

switch ($Command.ToLower()) {
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
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "shell" {
        Connect-Database
    }
    "backup" {
        New-Backup
    }
    "restore" {
        if ([string]::IsNullOrEmpty($BackupFile)) {
            Write-Host "❌ Debes especificar el archivo de backup" -ForegroundColor Red
            Write-Host "Uso: .\db-utils.ps1 restore <archivo_backup>"
            exit 1
        }
        Restore-Backup -BackupFile $BackupFile
    }
    "reset" {
        Reset-Database
    }
    "admin" {
        Start-Admin
    }
    "build" {
        Build-Image
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