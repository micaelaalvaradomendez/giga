#!/bin/bash
# Script para auditar esquema BD vs Modelos Django

echo "=== AUDITORÍA DE ESQUEMA: Django Models vs PostgreSQL ==="
echo ""

# Lista de tablas críticas a verificar
TABLES=("feriado" "nota_guardia" "guardia" "cronograma" "asistencia" "licencia" "hora_compensacion" "agente" "agente_rol" "area")

for table in "${TABLES[@]}"; do
    echo "========================================"
    echo "Tabla: $table"
    echo "========================================"
    docker exec giga-postgres psql -U giga_user -d giga -c "\d $table" 2>/dev/null || echo "❌ Tabla NO existe"
    echo ""
done

echo "=== VERIFICACIÓN COMPLETADA ===" 
