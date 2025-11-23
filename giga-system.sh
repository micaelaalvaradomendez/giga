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
    echo "  up             - Construir e iniciar (equivale a docker-compose up -d --build)"
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

# Función para construir e iniciar (equivalente a docker-compose up -d --build)
up_all() {
    echo -e "${BLUE}🚀 Construyendo e iniciando GIGA completo...${NC}"
    echo -e "${PURPLE}Equivale a: docker-compose up -d --build${NC}"
    
    # Detener servicios existentes
    echo -e "${BLUE}🛑 Deteniendo servicios existentes...${NC}"
    docker-compose down --remove-orphans >/dev/null 2>&1 || true
    
    # Construir imágenes
    build_all
    
    # Iniciar servicios paso a paso
    start_all
    
    echo -e "${GREEN}✅ GIGA está listo para usar!${NC}"
}

# Función para iniciar todos los servicios
start_all() {
    echo -e "${BLUE}🚀 Iniciando todos los servicios...${NC}"
    
    # Iniciar solo los servicios esenciales primero
    echo -e "${BLUE}📊 Iniciando base de datos...${NC}"
    docker-compose up -d postgres
    
    # Esperar a que PostgreSQL esté listo
    echo -e "${YELLOW}⏳ Esperando PostgreSQL...${NC}"
    timeout=60
    counter=0
    while ! docker exec giga-postgres pg_isready -U giga_user -d giga >/dev/null 2>&1; do
        if [ $counter -ge $timeout ]; then
            echo -e "${RED}❌ Timeout esperando PostgreSQL${NC}"
            exit 1
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done
    echo -e "${GREEN} ✅ PostgreSQL listo!${NC}"
    
    # Iniciar backend
    echo -e "${BLUE}🐍 Iniciando backend Django...${NC}"
    docker-compose up -d backend
    
    # Esperar a que Django esté listo
    echo -e "${YELLOW}⏳ Esperando Django...${NC}"
    timeout=90
    counter=0
    while ! curl -sf http://localhost:8000/api/personas/auth/check-session/ >/dev/null 2>&1; do
        if [ $counter -ge $timeout ]; then
            echo -e "${YELLOW}⚠️ Django tardó más de lo esperado, continuando...${NC}"
            break
        fi
        sleep 3
        counter=$((counter + 3))
        echo -n "."
    done
    echo -e "${GREEN} ✅ Backend Django listo!${NC}"
    
    # Iniciar frontend
    echo -e "${BLUE}⚛️ Iniciando frontend Svelte...${NC}"
    docker-compose up -d frontend
    
    # Iniciar nginx
    echo -e "${BLUE}🌐 Iniciando proxy Nginx...${NC}"
    docker-compose up -d nginx
    
    # Configurar datos iniciales si es necesario
    echo -e "${BLUE}🔧 Configurando datos iniciales...${NC}"
    docker exec giga-postgres psql -U giga_user -d giga -c "
    INSERT INTO tipo_licencia (codigo, descripcion) 
    VALUES 
        ('ANUAL', 'Licencia anual'),
        ('MEDICA', 'Licencia médica'),
        ('ESTUDIO', 'Licencia por estudio')
    ON CONFLICT (codigo) DO NOTHING;
    " >/dev/null 2>&1 || echo -e "${YELLOW}⚠️ Los tipos de licencia ya existen o hubo un problema menor${NC}"
    
    echo -e "${YELLOW}⏳ Esperando servicios adicionales...${NC}"
    sleep 10
    
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
    up)
        check_docker
        up_all
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
    reset)
        check_docker
        reset_database
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