# Presentación GIGA

Presentación interactiva 3D del Sistema de Gestión Integral de Guardias y Asistencia (GIGA) desarrollado para la UNTDF.

## 🚀 Despliegue en Railway

### Opción 1: Desde la interfaz web de Railway

1. Ve a [Railway.app](https://railway.app)
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta este repositorio
5. Railway detectará automáticamente el `package.json` y desplegará

### Opción 2: Desde Railway CLI

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Desplegar
railway up
```

## 🏃 Ejecución Local

```bash
# Instalar dependencias
npm install

# Iniciar servidor
npm start

# Abrir en navegador
# http://localhost:3000
```

## 📁 Estructura

- `index.html` - Estructura principal
- `styles.css` - Estilos y animaciones 3D
- `script.js` - Lógica de presentación y datos
- `server.js` - Servidor Express para producción
- `imagenes/` - Recursos (QR, etc.)

## 🎯 Características

- Presentación 3D interactiva con órbitas
- 7 slides orbitales + modal hero con 3 pestañas
- 100% responsive
- Animaciones suaves
- Click fuera para cerrar modales
