#!/usr/bin/env bash
# Compatible con Windows/Linux/Mac
# Script de inicialización de la base de datos

set -e

echo "🚀 Iniciando configuración de base de datos GIGA..."

# Esperar a que la base de datos esté lista
echo "⏳ Esperando a que la base de datos esté disponible..."
python /wait_for_db.py

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Verificar si ya existen datos (para evitar duplicados)
echo "Verificando si la base de datos ya tiene datos..."
USUARIOS_COUNT=$(python manage.py shell -c "
from personas.models import Usuario
print(Usuario.objects.count())
" | tail -1)

if [ "$USUARIOS_COUNT" -eq "0" ]; then
    echo "Cargando datos iniciales..."
    # Cargar el fixture principal que contiene todos los datos necesarios
    python manage.py loaddata /app/data_backup/initial_data.json
    
    echo "Datos iniciales cargados correctamente!"
else
    echo "La base de datos ya contiene datos. Saltando carga inicial."
fi

echo "Configuración completada. Iniciando servidor..."

# Iniciar el servidor Django
exec python manage.py runserver 0.0.0.0:8000