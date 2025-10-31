#!/bin/bash
set -e

# Script de inicialización para la base de datos GIGA
echo "Iniciando configuración de base de datos GIGA..."

# Conectar como postgres y ejecutar configuración inicial
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

echo "Base de datos GIGA configurada correctamente!"
echo "Conexión disponible en: postgresql://giga_user:giga2025@localhost:5432/giga"