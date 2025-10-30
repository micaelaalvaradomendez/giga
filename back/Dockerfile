# Etapa base
FROM python:3.11-slim AS base

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r django && useradd -r -g django django

# Crear directorios necesarios
RUN mkdir -p /app /app/logs /app/staticfiles /app/media
WORKDIR /app

# Etapa de dependencias
FROM base AS dependencies

# Instalar pip actualizado
RUN pip install --upgrade pip

# Copiar y instalar requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Etapa de desarrollo
FROM dependencies AS development

# Cambiar propiedad de directorios
RUN chown -R django:django /app
USER django

# Copiar código fuente
COPY --chown=django:django . .

# Copiar y preparar scripts de Docker
COPY --chown=django:django docker/entrypoint.sh /entrypoint.sh
COPY --chown=django:django docker/init_db.sh /init_db.sh
COPY --chown=django:django docker/wait_for_db.py /wait_for_db.py

# Cambiar a root temporalmente para modificar permisos
USER root
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh
RUN sed -i 's/\r$//' /init_db.sh && chmod +x /init_db.sh
RUN chmod +x /wait_for_db.py

# Volver al usuario django
USER django

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# Comando por defecto
CMD ["/init_db.sh"]

# Etapa de producción
FROM dependencies AS production

# Instalar gunicorn para producción
RUN pip install gunicorn

# Cambiar propiedad de directorios
RUN chown -R django:django /app
USER django

# Copiar código fuente
COPY --chown=django:django . .

# Copiar scripts
COPY --chown=django:django docker/entrypoint.sh /entrypoint.sh
COPY --chown=django:django docker/production-entrypoint.sh /production-entrypoint.sh

# Cambiar a root para permisos
USER root
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh
RUN sed -i 's/\r$//' /production-entrypoint.sh && chmod +x /production-entrypoint.sh

# Volver al usuario django
USER django

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer puerto
EXPOSE 8000

# Comando de producción
CMD ["/production-entrypoint.sh"]

