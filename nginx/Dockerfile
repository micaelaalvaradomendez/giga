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

# Crear script de healthcheck mejorado
RUN echo '#!/bin/bash\n\
# Esperar un poco para que nginx termine de inicializarse\n\
sleep 2\n\
# Intentar 3 veces antes de fallar\n\
for i in {1..3}; do\n\
  if curl -sf http://localhost/health >/dev/null 2>&1; then\n\
    echo "healthy"\n\
    exit 0\n\
  fi\n\
  sleep 1\n\
done\n\
echo "unhealthy"\n\
exit 1\n\
' > /usr/local/bin/healthcheck.sh && chmod +x /usr/local/bin/healthcheck.sh

# Configurar usuario y permisos
RUN chown -R nginx:nginx /var/log/nginx /var/cache/nginx /etc/nginx

# Exponer puertos
EXPOSE 80 8080

# Healthcheck mejorado con más tiempo de inicio
HEALTHCHECK --interval=30s --timeout=15s --start-period=30s --retries=5 \
    CMD /usr/local/bin/healthcheck.sh

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]