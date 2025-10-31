# Dockerfile para Frontend Svelte - GIGA
FROM node:20-alpine

# Instalar herramientas adicionales
RUN apk add --no-cache \
    curl \
    bash \
    git \
    && rm -rf /var/cache/apk/*

# Habilitar pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de paquetes
COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias (sin frozen-lockfile para permitir actualizaciones)
RUN pnpm install

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/build /app/static

# Exponer puerto de desarrollo
EXPOSE 3000

# Variables de entorno
ENV NODE_ENV=development
ENV VITE_API_BASE_URL=http://localhost/api

# Crear script de healthcheck
RUN echo '#!/bin/bash' > /usr/local/bin/healthcheck.sh && \
    echo 'curl -f http://localhost:3000 || exit 1' >> /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Comando por defecto (desarrollo con HMR)
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]