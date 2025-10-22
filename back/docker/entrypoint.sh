#!/usr/bin/env sh
set -e

echo "Waiting for database $DB_HOST:$DB_PORT..."
python /wait_for_db.py

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting Django on 0.0.0.0:8000"
python manage.py runserver 0.0.0.0:8000

