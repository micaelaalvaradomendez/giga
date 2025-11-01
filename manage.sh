#!/bin/bash

# ===========================================
# SCRIPT DE GESTIÓN DE GIGA
# ===========================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función de ayuda
show_help() {
    cat << EOF
🚀 GIGA - Sistema de Gestión Docker

USO:
    ./manage.sh [COMANDO] [OPCIONES]

COMANDOS:
    dev             Iniciar entorno de desarrollo
    prod            Iniciar entorno de producción
    stop            Detener todos los servicios
    restart         Reiniciar todos los servicios
    build           Construir todas las imágenes
    logs            Ver logs de los servicios
    shell           Acceder al shell del backend
    db-shell        Acceder al shell de PostgreSQL
    migrate         Ejecutar migraciones de Django
    collectstatic   Recopilar archivos estáticos
    pnpm            Ejecutar comandos pnpm en el frontend
    clean           Limpiar volúmenes y contenedores
    status          Ver estado de los servicios
    help            Mostrar esta ayuda

EJEMPLOS:
    ./manage.sh dev                 # Iniciar desarrollo
    ./manage.sh prod                # Iniciar producción
    ./manage.sh logs backend        # Ver logs del backend
    ./manage.sh pnpm install        # Instalar dependencias con pnpm
    ./manage.sh migrate             # Ejecutar migraciones
    ./manage.sh clean               # Limpiar todo

EOF
}

# Verificar si Docker está disponible
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado o no está en el PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose no está instalado"
        exit 1
    fi
}

# Verificar archivo .env
check_env() {
    if [ ! -f .env ]; then
        log_warning "Archivo .env no encontrado, creando desde .env.example..."
        cp .env.example .env
        log_success "Archivo .env creado. Por favor, revisa y ajusta las configuraciones."
    fi
}

# Función para desarrollo
dev_start() {
    log_info "Iniciando entorno de desarrollo..."
    check_env
    docker-compose -f docker-compose.dev.yml up --build -d
    log_success "Entorno de desarrollo iniciado"
    log_info "Frontend: http://localhost:5173"
    log_info "Backend: http://localhost:8000"
    log_info "Base de datos: localhost:5434"
}

# Función para producción
prod_start() {
    log_info "Iniciando entorno de producción..."
    check_env
    docker-compose -f docker-compose.prod.yml up --build -d
    log_success "Entorno de producción iniciado"
    log_info "Aplicación: http://localhost"
}

# Función para detener servicios
stop_services() {
    log_info "Deteniendo todos los servicios..."
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    log_success "Servicios detenidos"
}

# Función para reiniciar
restart_services() {
    log_info "Reiniciando servicios..."
    stop_services
    if [ "$1" = "prod" ]; then
        prod_start
    else
        dev_start
    fi
}

# Función para construir imágenes
build_images() {
    log_info "Construyendo imágenes Docker..."
    docker-compose -f docker-compose.dev.yml build --no-cache
    log_success "Imágenes construidas"
}

# Función para ver logs
show_logs() {
    local service=${1:-}
    if [ -n "$service" ]; then
        log_info "Mostrando logs de: $service"
        docker-compose -f docker-compose.dev.yml logs -f "$service" 2>/dev/null || \
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    else
        log_info "Mostrando logs de todos los servicios"
        docker-compose -f docker-compose.dev.yml logs -f 2>/dev/null || \
        docker-compose -f docker-compose.prod.yml logs -f
    fi
}

# Función para shell del backend
backend_shell() {
    log_info "Accediendo al shell del backend..."
    docker-compose -f docker-compose.dev.yml exec backend python manage.py shell 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
}

# Función para shell de la DB
db_shell() {
    log_info "Accediendo al shell de PostgreSQL..."
    docker-compose -f docker-compose.dev.yml exec db psql -U giga_user -d giga 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml exec db psql -U giga_user -d giga
}

# Función para migraciones
run_migrations() {
    log_info "Ejecutando migraciones de Django..."
    docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
    log_success "Migraciones completadas"
}

# Función para collectstatic
collect_static() {
    log_info "Recopilando archivos estáticos..."
    docker-compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
    log_success "Archivos estáticos recopilados"
}

# Función para comandos pnpm
run_pnpm() {
    local cmd="$*"
    log_info "Ejecutando: pnpm $cmd"
    docker-compose -f docker-compose.dev.yml exec frontend pnpm $cmd 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml exec frontend pnpm $cmd
}

# Función para limpiar
clean_all() {
    log_warning "¿Estás seguro de que quieres limpiar todos los volúmenes y contenedores? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Limpiando contenedores, volúmenes e imágenes..."
        stop_services
        docker system prune -af --volumes
        log_success "Limpieza completada"
    else
        log_info "Operación cancelada"
    fi
}

# Función para ver estado
show_status() {
    log_info "Estado de los servicios:"
    echo ""
    docker-compose -f docker-compose.dev.yml ps 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml ps
}

# Script principal
main() {
    check_docker
    
    case "${1:-help}" in
        "dev")
            dev_start
            ;;
        "prod")
            prod_start
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services "$2"
            ;;
        "build")
            build_images
            ;;
        "logs")
            show_logs "$2"
            ;;
        "shell")
            backend_shell
            ;;
        "db-shell")
            db_shell
            ;;
        "migrate")
            run_migrations
            ;;
        "collectstatic")
            collect_static
            ;;
        "pnpm")
            shift
            run_pnpm "$@"
            ;;
        "clean")
            clean_all
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Comando desconocido: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"