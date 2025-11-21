#!/bin/bash
set -e

# Script maestro de inicialización para la base de datos GIGA
echo "=========================================="
echo "INICIANDO CONFIGURACIÓN DE BASE DE DATOS GIGA"
echo "=========================================="

# Directorio donde están los scripts
SCRIPT_DIR="/docker-entrypoint-initdb.d"

# Función para ejecutar scripts SQL
execute_sql_file() {
    local file=$1
    local filename=$(basename "$file")
    echo ""
    echo "▶ Ejecutando: $filename"
    echo "----------------------------------------"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$file"
    if [ $? -eq 0 ]; then
        echo "✓ $filename ejecutado correctamente"
    else
        echo "✗ Error ejecutando $filename"
        exit 1
    fi
}

# 1. Configuración inicial de la base de datos
echo ""
echo "PASO 1: Configuración inicial de la base de datos"
echo "----------------------------------------"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Configurar base de datos con locale argentino
    ALTER DATABASE giga SET timezone TO 'America/Argentina/Buenos_Aires';
    
    -- Crear extensiones necesarias
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "unaccent";
    
    -- Configurar búsqueda en texto
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Otorgar permisos completos al usuario
    GRANT ALL PRIVILEGES ON DATABASE giga TO giga_user;
    GRANT ALL ON SCHEMA public TO giga_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO giga_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO giga_user;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO giga_user;
    
    -- Configurar permisos por defecto para futuros objetos
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO giga_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO giga_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO giga_user;
EOSQL
echo "✓ Configuración inicial completada"

# 2. Ejecutar scripts en orden específico
echo ""
echo "PASO 2: Ejecutando scripts de inicialización en orden"
echo "=========================================="

# Lista de scripts en el orden que deben ejecutarse
SCRIPTS=(
    "02-setup-functions.sql"
    "03-create-tables.sql"
    "04-functions-triggers.sql"
    "05-seed-data.sql"
    "06-add-approval-tracking.sql"
    "07-add-nota-guardia.sql"
    "08-refactor-asistencia.sql"
    "09-django-tables.sql"
)

# Ejecutar cada script en orden
for script in "${SCRIPTS[@]}"; do
    script_path="$SCRIPT_DIR/$script"
    if [ -f "$script_path" ]; then
        execute_sql_file "$script_path"
    else
        echo "⚠ ADVERTENCIA: No se encontró $script"
    fi
done

# 3. Verificar la instalación
echo ""
echo "PASO 3: Verificando instalación"
echo "=========================================="
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Contar tablas creadas
    SELECT 'Total de tablas: ' || COUNT(*) as info FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    -- Contar funciones creadas
    SELECT 'Total de funciones: ' || COUNT(*) as info FROM information_schema.routines WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';
    
    -- Contar triggers creados
    SELECT 'Total de triggers: ' || COUNT(*) as info FROM information_schema.triggers WHERE trigger_schema = 'public';
    
    -- Mostrar tablas principales
    SELECT 'Tablas principales:' as info;
    SELECT '  - ' || table_name as tabla FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE' 
    ORDER BY table_name;
EOSQL

echo ""
echo "=========================================="
echo "✓ BASE DE DATOS GIGA CONFIGURADA CORRECTAMENTE"
echo "=========================================="
echo "Conexión disponible en: postgresql://giga_user:giga2025@localhost:5432/giga"
echo ""