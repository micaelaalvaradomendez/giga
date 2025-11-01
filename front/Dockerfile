# Etapa de desarrollo
FROM node:20-alpine AS development

# Instalar pnpm globalmente
RUN npm install -g pnpm

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S nodejs
RUN adduser -S svelte -u 1001 -G nodejs

WORKDIR /app

# Cambiar propiedad del directorio de trabajo
RUN chown -R svelte:nodejs /app
USER svelte

# Copiar archivos de configuración de pnpm
COPY --chown=svelte:nodejs package.json pnpm-lock.yaml* ./

# Instalar dependencias con pnpm
RUN pnpm install --frozen-lockfile

# Copiar el resto de los archivos
COPY --chown=svelte:nodejs . .

# Exponer puerto
EXPOSE 5173

# Comando de desarrollo
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Etapa de producción
FROM node:20-alpine AS production

# Instalar pnpm
RUN npm install -g pnpm

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S svelte -u 1001 -G nodejs

WORKDIR /app

# Cambiar propiedad del directorio de trabajo
RUN chown -R svelte:nodejs /app
USER svelte

# Copiar archivos de configuración
COPY --chown=svelte:nodejs package.json pnpm-lock.yaml* ./

# Instalar solo dependencias de producción
RUN pnpm install --frozen-lockfile --prod

# Copiar código fuente
COPY --chown=svelte:nodejs . .

# Construir la aplicación
RUN pnpm run build

# Exponer puerto
EXPOSE 3000

# Comando de producción
CMD ["pnpm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]

