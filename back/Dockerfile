# Django Backend - GIGA Project
# Dockerfile optimizado para Django con PostgreSQL

FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . /app/

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles /app/media

# Exponer puerto
EXPOSE 8000

# Crear usuario no-root para seguridad
RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django

# Script de entrada con migraciones automáticas
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py runserver 0.0.0.0:8000"]