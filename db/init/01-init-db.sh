#!/bin/bash
# Script de inicialización de la base de datos PostgreSQL
set -e

echo "🐘 Iniciando configuración de PostgreSQL para GIGA..."

# Configurar timezone
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Configurar timezone para Argentina
    SET timezone TO 'America/Argentina/Buenos_Aires';
    ALTER DATABASE $POSTGRES_DB SET timezone TO 'America/Argentina/Buenos_Aires';
    
    -- Crear extensiones útiles
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "unaccent";
    
    -- Mostrar información de la base de datos
    SELECT current_database(), current_user, version();
    SELECT 'Database initialized successfully' as status;
EOSQL

echo "✅ Base de datos PostgreSQL inicializada correctamente"