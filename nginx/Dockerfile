# Dockerfile para Nginx - Proxy Reverso GIGA
FROM nginx:1.25-alpine

# Instalar herramientas adicionales
RUN apk add --no-cache \
    curl \
    bash \
    && rm -rf /var/cache/apk/*

# Crear directorio para logs personalizados
RUN mkdir -p /var/log/nginx/giga

# Copiar configuración personalizada
COPY nginx.conf /etc/nginx/nginx.conf

# Crear script de healthcheck
RUN echo '#!/bin/bash' > /usr/local/bin/healthcheck.sh && \
    echo 'curl -f http://localhost/health || exit 1' >> /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# Configurar usuario y permisos
RUN chown -R nginx:nginx /var/log/nginx /var/cache/nginx /etc/nginx

# Exponer puertos
EXPOSE 80 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]