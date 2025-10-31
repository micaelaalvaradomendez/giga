# PostgreSQL 16 con configuración específica para GIGA
FROM postgres:16-alpine

# Configurar variables de entorno
ENV POSTGRES_DB=giga
ENV POSTGRES_USER=giga_user
ENV POSTGRES_PASSWORD=giga2025
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Configurar locale para Argentina
ENV LANG=es_AR.UTF-8
ENV LC_ALL=es_AR.UTF-8
ENV LC_COLLATE=es_AR.UTF-8
ENV LC_CTYPE=es_AR.UTF-8

# Crear directorios necesarios
RUN mkdir -p /docker-entrypoint-initdb.d
RUN mkdir -p /var/lib/postgresql/data

# Copiar scripts de inicialización
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Copiar configuraciones personalizadas
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

# Exponer puerto PostgreSQL
EXPOSE 5432

# Configurar permisos
RUN chown -R postgres:postgres /var/lib/postgresql/data
RUN chmod 700 /var/lib/postgresql/data