FROM nginx:1.25-alpine

# Instalar curl para healthcheck
RUN apk add --no-cache curl

# Crear directorios necesarios
RUN mkdir -p /var/log/nginx /var/www/static /var/www/media

# Copiar configuración personalizada
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Exponer puertos
EXPOSE 80 443

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]