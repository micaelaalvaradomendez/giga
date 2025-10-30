#!/bin/bash

# Script de entrada para producción

set -e

echo "🚀 Iniciando aplicación Django en modo producción..."

# Esperar a que la base de datos esté disponible
echo "⏳ Esperando conexión a la base de datos..."
python /wait_for_db.py

# Ejecutar migraciones
echo "📊 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='System'
    )
    print("✅ Superusuario creado: admin/admin123")
else:
    print("✅ Superusuario ya existe")
EOF

echo "🎯 Iniciando servidor Gunicorn..."

# Iniciar Gunicorn
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile /app/logs/gunicorn-access.log \
    --error-logfile /app/logs/gunicorn-error.log \
    giga.wsgi:application