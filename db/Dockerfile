# PostgreSQL Database Service
# Este es el servicio de base de datos aislado del backend

FROM postgres:16-alpine

# Variables de entorno
ENV POSTGRES_DB=giga
ENV POSTGRES_USER=giga_user
ENV POSTGRES_PASSWORD=giga_pass

# Configuración de timezone para Argentina
ENV TZ=America/Argentina/Buenos_Aires

# Copiar scripts de inicialización
COPY init/ /docker-entrypoint-initdb.d/

# Configuración adicional de PostgreSQL
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

# Exponer puerto
EXPOSE 5432

# Configurar comando con configuraciones personalizadas
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf", "-c", "hba_file=/etc/postgresql/pg_hba.conf"]