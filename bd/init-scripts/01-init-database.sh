#!/bin/bash
# ========================================================================
# Script de Inicialización de Base de Datos - Sistema GIGA
# Fecha: 27 de Noviembre 2025
# Descripción: Ejecuta scripts SQL consolidados en orden correcto
# ========================================================================

set -e  # Salir si cualquier comando falla

echo "========================================"
echo "Inicializando Base de Datos GIGA"
echo "========================================"

# Directorio de scripts
SCRIPT_DIR="$(dirname "$0")"

# Función para ejecutar SQL
run_sql() {
    local file=$1
    local description=$2
    echo ""
    echo ">>> Ejecutando: $description"
    echo "    Archivo: $(basename $file)"
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$file"
    if [ $? -eq 0 ]; then
        echo "    ✓ Completado exitosamente"
    else
        echo "    ✗ Error al ejecutar"
        return 1
    fi
}

# ========================================================================
# Ejecución de Scripts en Orden
# ========================================================================

# 1. Tablas finales (29 tablas consolidadas)
run_sql "$SCRIPT_DIR/01-tables-final.sql" \
    "Creación de tablas finales (29 tablas)"

# 2. Funciones y triggers
run_sql "$SCRIPT_DIR/02-functions-final.sql" \
    "Funciones, triggers y validaciones"

# 3. Datos iniciales
run_sql "$SCRIPT_DIR/03-seed-data.sql" \
    "Datos iniciales organizacionales"

# 4. Datos históricos para desarrollo
run_sql "$SCRIPT_DIR/04-historical-data.sql" \
    "Datos históricos para testing"

run_sql "$SCRIPT_DIR/05-incidencias.sql" \
    "Tablas incidencias"

run_sql "$SCRIPT_DIR/fix-plus.sql" \
    "Arreglo logica plus"

run_sql "$SCRIPT_DIR/sesion-activa.sql" \
    "Tabla para sesiones concurrentes"
    
run_sql "$SCRIPT_DIR/08-create-notificaciones.sql" \
    "Tabla de notificaciones"


# ========================================================================
# Finalización
# ========================================================================

echo ""
echo "========================================"
echo "Base de Datos Inicializada Correctamente"
echo "========================================"
echo ""
echo "Resumen de scripts ejecutados:"
echo "  1. Tablas finales (29 tablas)"
echo "  2. Funciones y triggers (completo)"
echo "  3. Datos organizacionales (roles, áreas, agentes)"
echo "  4. Datos históricos (cronogramas, guardias, asistencias)"
echo "  5. Tablas incidencias"
echo "  6. Arreglo logica plus"
echo "  7. Tabla para sesiones concurrentes"
echo ""
echo "IMPORTANTE: Después de iniciar Django, ejecutar:"
echo "  docker exec giga-django python manage.py migrate"
echo ""
echo "========================================"