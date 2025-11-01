#!/bin/bash
# GIGA - Comando Universal de Inicio
# Funciona en: Windows (Git Bash) | Linux | macOS
# Uso: ./start.sh

echo "🚀 GIGA - Iniciando sistema..."
echo "💻 Compatible con: Windows | Linux | macOS"
echo ""

# Función para mostrar progress
show_progress() {
    echo "⏳ $1..."
}

# Función para mostrar éxito
show_success() {
    echo "✅ $1"
}

# Función para mostrar error
show_error() {
    echo "❌ $1"
    exit 1
}

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    show_error "Docker no está instalado. Instalar desde: https://www.docker.com/products/docker-desktop/"
fi

# Verificar que Docker está corriendo
if ! docker info &> /dev/null; then
    show_error "Docker no está corriendo. Iniciarlo y volver a ejecutar este script."
fi

show_success "Docker detectado y funcionando"

# Ir al directorio del script (por si se ejecuta desde otro lugar)
cd "$(dirname "$0")"

show_progress "Limpiando configuración anterior"

# Parar y limpiar contenedores anteriores
cd db
docker-compose down -v &> /dev/null
cd ..
docker-compose -f docker-compose.dev.yml down -v &> /dev/null

show_success "Configuración anterior limpiada"

show_progress "Iniciando base de datos PostgreSQL"

# Iniciar base de datos aislada
cd db
docker-compose up -d

if [ $? -ne 0 ]; then
    show_error "Error iniciando base de datos"
fi

cd ..

show_success "Base de datos iniciada"
show_progress "Esperando que la base de datos esté lista (15 segundos)"

# Esperar que PostgreSQL esté listo
sleep 15

show_progress "Iniciando backend Django y frontend SvelteKit"

# Levantar aplicación completa
docker-compose -f docker-compose.dev.yml up -d --build

if [ $? -ne 0 ]; then
    show_error "Error iniciando aplicación"
fi

show_success "Aplicación iniciada"

echo ""
echo "🎉 ¡GIGA está listo!"
echo ""
echo "📱 Abrir en navegador:"
echo "   • App:   http://localhost:5173"
echo "   • Admin: http://localhost:8000/admin"
echo "   • API:   http://localhost:8000/api/"
echo ""
echo "👤 Login de prueba:"
echo "   • Usuario: admin"
echo "   • Password: admin123"
echo ""
echo "🔧 Ver logs:"
echo "   • Backend:  docker logs -f giga_backend_dev"
echo "   • Frontend: docker logs -f giga_frontend_dev"
echo ""
echo "⚠️  Si algo falla: ejecutar este script nuevamente"
echo "💡 Más ayuda: ver README.md"