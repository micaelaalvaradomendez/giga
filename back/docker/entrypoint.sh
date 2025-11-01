#!/usr/bin/env bash
# Compatible con Windows/Linux/Mac

set -e

echo "🚀 Iniciando entrypoint de Django..."

# Verificar variables de entorno necesarias
if [ -z "$DB_HOST" ]; then
    export DB_HOST="db"
fi
if [ -z "$DB_PORT" ]; then
    export DB_PORT="5432"
fi

echo "⏳ Esperando base de datos $DB_HOST:$DB_PORT..."
python /wait_for_db.py

echo "📊 Aplicando migraciones..."
python manage.py migrate --noinput

echo "👤 Creando superusuario si no existe..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@giga.local',
        password='admin123',
        first_name='Admin',
        last_name='System'
    )
    print("✅ Superusuario creado: admin/admin123")
else:
    print("✅ Superusuario ya existe")
EOF

echo "🔥 Iniciando Django en 0.0.0.0:8000"
python manage.py runserver 0.0.0.0:8000

