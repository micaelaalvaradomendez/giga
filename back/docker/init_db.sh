#!/bin/bash

# Script de inicialización de la base de datos
# Este script se ejecuta automáticamente cuando se inicia el contenedor backend

echo "Iniciando configuración de base de datos..."

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté disponible..."
python docker/wait_for_db.py

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
    
    # Cargar fixtures en orden correcto
    echo "   → Cargando roles básicos..."
    python manage.py loaddata personas/fixtures/roles_basicos.json
    
    echo "   → Cargando área básica..."
    python manage.py loaddata personas/fixtures/area_basica.json
    
    echo "   → Cargando usuarios y agentes..."
    python manage.py loaddata personas/fixtures/usuarios_agentes.json
    
    echo "   → Cargando asignaciones de roles..."
    python manage.py loaddata personas/fixtures/asignacion_roles.json
    
    echo "   → Cargando tipos de licencia..."
    python manage.py loaddata asistencia/fixtures/tipos_licencia.json
    
    echo "   → Cargando licencias básicas..."
    python manage.py loaddata asistencia/fixtures/licencias_basicas.json
    
    echo "Datos iniciales cargados correctamente!"
else
    echo "La base de datos ya contiene datos. Saltando carga inicial."
fi

echo "Configuración completada. Iniciando servidor..."

# Iniciar el servidor Django
exec python manage.py runserver 0.0.0.0:8000