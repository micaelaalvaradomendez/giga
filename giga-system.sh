#!/bin/bash

# Script de gestión integral del sistema GIGA
# Maneja Frontend (Svelte) + Backend (Django) + BD (PostgreSQL) + Nginx

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🚀 GIGA - Sistema Completo${NC}"
    echo -e "${PURPLE}Frontend (Svelte) + Backend (Django) + BD (PostgreSQL) + Nginx${NC}"
    echo ""
    echo "Uso: $0 [comando] [opciones]"
    echo ""
    echo -e "${CYAN}Comandos principales:${NC}"
    echo "  build          - Construir todas las imágenes"
    echo "  start          - Iniciar todos los servicios"
    echo "  stop           - Detener todos los servicios"
    echo "  restart        - Reiniciar todos los servicios"
    echo "  status         - Estado de todos los servicios"
    echo "  logs [servicio] - Ver logs (postgres/backend/frontend/nginx/all)"
    echo "  dev            - Modo desarrollo completo"
    echo ""
    echo -e "${CYAN}Comandos por servicio:${NC}"
    echo "  build-db       - Solo base de datos"
    echo "  build-backend  - Solo backend Django"
    echo "  build-frontend - Solo frontend Svelte"
    echo "  build-nginx    - Solo Nginx"
    echo ""
    echo -e "${CYAN}Comandos de base de datos:${NC}"
    echo "  db-shell       - Conectar a PostgreSQL"
    echo "  db-backup      - Crear backup de BD"
    echo "  db-restore     - Restaurar backup"
    echo "  migrate        - Ejecutar migraciones Django"
    echo ""
    echo -e "${CYAN}Comandos de desarrollo:${NC}"
    echo "  shell-backend  - Shell del contenedor Django"
    echo "  shell-frontend - Shell del contenedor Svelte"
    echo "  test           - Ejecutar tests"
    echo "  clean          - Limpiar volúmenes y contenedores"
    echo ""
    echo -e "${CYAN}Utilidades:${NC}"
    echo "  health         - Verificar salud de servicios"
    echo "  urls          - Mostrar URLs de acceso"
    echo "  help          - Mostrar esta ayuda"
    echo ""
}

# Función para verificar Docker
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker no está corriendo${NC}"
        exit 1
    fi
}

# Función para mostrar URLs de acceso
show_urls() {
    echo -e "${BLUE}🌐 URLs de acceso:${NC}"
    echo -e "${GREEN}Frontend (Aplicación principal): http://localhost${NC}"
    echo -e "${GREEN}Backend API: http://localhost/api${NC}"
    echo -e "${GREEN}Django Admin: http://localhost/admin${NC}"
    echo -e "${GREEN}Nginx Status: http://localhost:8080/nginx_status${NC}"
    echo -e "${GREEN}Nginx Info: http://localhost:8080/info${NC}"
    echo -e "${GREEN}Health Check: http://localhost/health${NC}"
    echo ""
    echo -e "${YELLOW}Puertos directos (para desarrollo):${NC}"
    echo -e "${YELLOW}PostgreSQL: localhost:5432${NC}"
    echo -e "${YELLOW}Django (directo): localhost:8000 (si está expuesto)${NC}"
    echo -e "${YELLOW}Svelte (directo): localhost:3000 (si está expuesto)${NC}"
}

# Función para verificar salud de servicios
check_health() {
    echo -e "${BLUE}🏥 Verificando salud de servicios...${NC}"
    
    services=("giga-postgres" "giga-django" "giga-frontend" "giga-nginx")
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q $service; then
            health=$(docker inspect --format='{{.State.Health.Status}}' $service 2>/dev/null || echo "no-healthcheck")
            case $health in
                "healthy")
                    echo -e "${GREEN}✅ $service: Saludable${NC}"
                    ;;
                "unhealthy")
                    echo -e "${RED}❌ $service: No saludable${NC}"
                    ;;
                "starting")
                    echo -e "${YELLOW}⏳ $service: Iniciando...${NC}"
                    ;;
                "no-healthcheck")
                    echo -e "${BLUE}ℹ️  $service: Corriendo (sin healthcheck)${NC}"
                    ;;
            esac
        else
            echo -e "${RED}❌ $service: No está corriendo${NC}"
        fi
    done
}

# Función para construir todas las imágenes
build_all() {
    echo -e "${BLUE}🔨 Construyendo todas las imágenes...${NC}"
    docker-compose build --parallel
    echo -e "${GREEN}✅ Todas las imágenes construidas${NC}"
}

# Función para iniciar todos los servicios
start_all() {
    echo -e "${BLUE}🚀 Iniciando todos los servicios...${NC}"
    docker-compose up -d
    
    echo -e "${YELLOW}⏳ Esperando a que los servicios estén listos...${NC}"
    sleep 15
    
    check_health
    echo ""
    show_urls
}

# Función para detener todos los servicios
stop_all() {
    echo -e "${BLUE}🛑 Deteniendo todos los servicios...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para mostrar logs
show_logs() {
    service=${1:-"all"}
    
    case $service in
        "postgres"|"db"|"bd")
            echo -e "${BLUE}📋 Logs de PostgreSQL:${NC}"
            docker-compose logs -f postgres
            ;;
        "backend"|"django")
            echo -e "${BLUE}📋 Logs de Django Backend:${NC}"
            docker-compose logs -f backend
            ;;
        "frontend"|"svelte")
            echo -e "${BLUE}📋 Logs de Svelte Frontend:${NC}"
            docker-compose logs -f frontend
            ;;
        "nginx"|"proxy")
            echo -e "${BLUE}📋 Logs de Nginx:${NC}"
            docker-compose logs -f nginx
            ;;
        "all"|*)
            echo -e "${BLUE}📋 Logs de todos los servicios:${NC}"
            docker-compose logs -f
            ;;
    esac
}

# Función para modo desarrollo
dev_mode() {
    echo -e "${BLUE}🚀 Iniciando modo desarrollo completo...${NC}"
    
    # Construir si es necesario
    build_all
    
    # Iniciar servicios
    start_all
    
    echo -e "${GREEN}✅ Modo desarrollo activo${NC}"
    echo -e "${BLUE}📋 Siguiendo logs... (Ctrl+C para salir sin detener servicios)${NC}"
    
    # Mostrar logs en tiempo real
    docker-compose logs -f
}

# Función para ejecutar migraciones
run_migrations() {
    echo -e "${BLUE}🔄 Ejecutando migraciones de Django...${NC}"
    docker-compose exec backend python manage.py migrate
    echo -e "${GREEN}✅ Migraciones completadas${NC}"
}

# Función para acceder a shell de PostgreSQL
db_shell() {
    echo -e "${BLUE}🗃️  Conectando a PostgreSQL...${NC}"
    docker-compose exec postgres psql -U giga_user -d giga
}

# Función para backup de BD
db_backup() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="giga_backup_$timestamp.sql"
    
    echo -e "${BLUE}💾 Creando backup de base de datos...${NC}"
    docker-compose exec postgres pg_dump -U giga_user giga > "$backup_file"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup creado: $backup_file${NC}"
    else
        echo -e "${RED}❌ Error al crear backup${NC}"
        exit 1
    fi
}

# Función para limpiar sistema
clean_system() {
    echo -e "${YELLOW}⚠️  Esto eliminará contenedores, volúmenes y redes no utilizados${NC}"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🧹 Limpiando sistema...${NC}"
        docker-compose down -v --remove-orphans
        docker system prune -f
        docker volume prune -f
        echo -e "${GREEN}✅ Sistema limpiado${NC}"
    else
        echo -e "${BLUE}❌ Limpieza cancelada${NC}"
    fi
}

# Main script
case "$1" in
    build)
        check_docker
        build_all
        ;;
    start)
        check_docker
        start_all
        ;;
    stop)
        check_docker
        stop_all
        ;;
    restart)
        check_docker
        stop_all
        sleep 3
        start_all
        ;;
    status)
        check_docker
        docker-compose ps
        echo ""
        check_health
        ;;
    logs)
        check_docker
        show_logs "$2"
        ;;
    dev)
        check_docker
        dev_mode
        ;;
    build-db)
        check_docker
        docker-compose build postgres
        ;;
    build-backend)
        check_docker
        docker-compose build backend
        ;;
    build-frontend)
        check_docker
        docker-compose build frontend
        ;;
    build-nginx)
        check_docker
        docker-compose build nginx
        ;;
    migrate)
        check_docker
        run_migrations
        ;;
    db-shell)
        check_docker
        db_shell
        ;;
    db-backup)
        check_docker
        db_backup
        ;;
    shell-backend)
        check_docker
        docker-compose exec backend bash
        ;;
    shell-frontend)
        check_docker
        docker-compose exec frontend sh
        ;;
    health)
        check_docker
        check_health
        ;;
    urls)
        show_urls
        ;;
    clean)
        check_docker
        clean_system
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando no reconocido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac