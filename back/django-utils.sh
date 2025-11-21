#!/bin/bash

# Script de utilidades para GIGA Django Backend
# Uso: ./django-utils.sh [comando] [opciones]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
DJANGO_CONTAINER="giga-django"
DB_CONTAINER="giga-postgres"
PROJECT_NAME="giga"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🐍 GIGA Django Backend Utils${NC}"
    echo ""
    echo "Uso: $0 [comando] [opciones]"
    echo ""
    echo "Comandos de Docker:"
    echo "  build          - Construir imagen de Django"
    echo "  start          - Iniciar servicios (Django + BD)"
    echo "  stop           - Detener servicios"
    echo "  restart        - Reiniciar servicios"
    echo "  logs           - Ver logs de Django"
    echo "  shell          - Acceder a shell de Django"
    echo "  status         - Estado de contenedores"
    echo ""
    echo "Comandos de Django:"
    echo "  migrate        - Ejecutar migraciones"
    echo "  makemigrations - Crear nuevas migraciones"
    echo "  shell-django   - Shell de Django (manage.py shell)"
    echo "  createsuperuser - Crear superusuario"
    echo "  collectstatic  - Recopilar archivos estáticos"
    echo "  test           - Ejecutar tests"
    echo ""
    echo "Comandos de Base de Datos:"
    echo "  inspectdb      - Generar modelos desde BD externa"
    echo "  dbshell        - Conectar a PostgreSQL"
    echo "  resetdb        - Resetear base de datos (⚠️ DESTRUCTIVO)"
    echo ""
    echo "Comandos de Desarrollo:"
    echo "  dev            - Modo desarrollo (build + start + logs)"
    echo "  check          - Verificar configuración Django"
    requirements   - Actualizar requirements.txt"
    echo ""
    echo "Comandos de Asistencias:"
    echo "  marcar-salidas - Marcar salidas automáticas (22:00)"
    echo ""
    echo "  help           - Mostrar esta ayuda"
    echo ""
}

# Función para verificar si Docker está corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker no está corriendo${NC}"
        exit 1
    fi
}

# Función para construir la imagen
build_image() {
    echo -e "${BLUE}🔨 Construyendo imagen de Django...${NC}"
    docker-compose build django
    echo -e "${GREEN}✅ Imagen construida${NC}"
}

# Función para iniciar servicios
start_services() {
    echo -e "${BLUE}🚀 Iniciando servicios...${NC}"
    docker-compose up -d
    
    echo -e "${YELLOW}⏳ Esperando a que los servicios estén listos...${NC}"
    sleep 10
    
    # Verificar estado de BD
    if docker exec $DB_CONTAINER pg_isready -U giga_user -d giga 2>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL está listo${NC}"
    else
        echo -e "${RED}❌ PostgreSQL no está disponible${NC}"
        return 1
    fi
    
    # Verificar Django
    if docker exec $DJANGO_CONTAINER python manage.py check --database default 2>/dev/null; then
        echo -e "${GREEN}✅ Django está funcionando correctamente${NC}"
        echo -e "${BLUE}🌐 Django disponible en: http://localhost:8000${NC}"
    else
        echo -e "${RED}❌ Django tiene problemas${NC}"
        return 1
    fi
}

# Función para detener servicios
stop_services() {
    echo -e "${BLUE}🛑 Deteniendo servicios...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para mostrar logs
show_logs() {
    echo -e "${BLUE}📋 Logs de Django:${NC}"
    docker-compose logs -f django
}

# Función para acceder a shell
access_shell() {
    echo -e "${BLUE}🐚 Accediendo a shell de contenedor Django...${NC}"
    docker exec -it $DJANGO_CONTAINER bash
}

# Función para Django shell
django_shell() {
    echo -e "${BLUE}🐍 Iniciando Django shell...${NC}"
    docker exec -it $DJANGO_CONTAINER python manage.py shell
}

# Función para ejecutar migraciones
run_migrations() {
    echo -e "${BLUE}🔄 Ejecutando migraciones...${NC}"
    docker exec $DJANGO_CONTAINER python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Migraciones aplicadas correctamente${NC}"
    else
        echo -e "${RED}❌ Error al aplicar migraciones${NC}"
        exit 1
    fi
}

# Función para crear migraciones
make_migrations() {
    echo -e "${BLUE}📝 Creando migraciones...${NC}"
    docker exec $DJANGO_CONTAINER python manage.py makemigrations
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Migraciones creadas${NC}"
    else
        echo -e "${YELLOW}⚠️ No hay cambios para migrar${NC}"
    fi
}

# Función para inspeccionar BD y generar modelos
inspect_database() {
    echo -e "${BLUE}🔍 Inspeccionando base de datos externa...${NC}"
    echo -e "${YELLOW}📋 Esto generará modelos Python basados en las tablas existentes${NC}"
    echo -e "${YELLOW}📋 Los modelos tendrán managed = False para no alterar la BD${NC}"
    
    # Crear directorio para modelos si no existe
    docker exec $DJANGO_CONTAINER mkdir -p /app/generated_models
    
    # Generar modelos
    docker exec $DJANGO_CONTAINER python manage.py inspectdb > generated_models.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Modelos generados en generated_models.py${NC}"
        echo -e "${BLUE}📝 Revisa el archivo y adapta según necesites${NC}"
        echo -e "${BLUE}📝 Los modelos están marcados como managed = False${NC}"
    else
        echo -e "${RED}❌ Error al generar modelos${NC}"
        exit 1
    fi
}

# Función para acceder a shell de BD
database_shell() {
    echo -e "${BLUE}🗃️  Conectando a PostgreSQL...${NC}"
    docker exec -it $DB_CONTAINER psql -U giga_user -d giga
}

# Función para crear superusuario
create_superuser() {
    echo -e "${BLUE}👤 Creando superusuario...${NC}"
    docker exec -it $DJANGO_CONTAINER python manage.py createsuperuser
}

# Función para verificar configuración
check_config() {
    echo -e "${BLUE}🔍 Verificando configuración de Django...${NC}"
    docker exec $DJANGO_CONTAINER python manage.py check
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Configuración correcta${NC}"
    else
        echo -e "${RED}❌ Hay problemas en la configuración${NC}"
        exit 1
    fi
}

# Función para modo desarrollo
dev_mode() {
    echo -e "${BLUE}🚀 Iniciando modo desarrollo...${NC}"
    build_image
    start_services
    echo -e "${GREEN}✅ Servicios iniciados en modo desarrollo${NC}"
    echo -e "${BLUE}📋 Siguiendo logs... (Ctrl+C para salir)${NC}"
    show_logs
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose ps
    echo ""
    
    # Verificar Django
    if docker exec $DJANGO_CONTAINER python manage.py check --database default 2>/dev/null; then
        echo -e "${GREEN}✅ Django está funcionando correctamente${NC}"
    else
        echo -e "${RED}❌ Django no está disponible${NC}"
    fi
    
    # Verificar BD
    if docker exec $DB_CONTAINER pg_isready -U giga_user -d giga 2>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL está funcionando${NC}"
    else
        echo -e "${RED}❌ PostgreSQL no está disponible${NC}"
    fi
}

# Función para resetear BD
reset_database() {
    echo -e "${RED}⚠️  PELIGRO: Esto eliminará TODOS los datos de la base de datos${NC}"
    echo -e "${YELLOW}¿Estás seguro de que quieres resetear la base de datos?${NC}"
    read -p "Escribe 'RESET_DB' para continuar: " confirm
    
    if [ "$confirm" != "RESET_DB" ]; then
        echo -e "${BLUE}❌ Reseteo cancelado${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}🗑️  Reseteando base de datos...${NC}"
    docker-compose down -v
    docker-compose up -d postgres
    
    # Esperar a que la BD esté lista
    sleep 15
    
    echo -e "${GREEN}✅ Base de datos reseteada${NC}"
    echo -e "${YELLOW}📋 Ejecuta 'migrate' para aplicar migraciones de Django${NC}"
}

# Main script
case "$1" in
    build)
        check_docker
        build_image
        ;;
    start)
        check_docker
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        stop_services
        start_services
        ;;
    logs)
        check_docker
        show_logs
        ;;
    shell)
        check_docker
        access_shell
        ;;
    shell-django)
        check_docker
        django_shell
        ;;
    migrate)
        check_docker
        run_migrations
        ;;
    makemigrations)
        check_docker
        make_migrations
        ;;
    inspectdb)
        check_docker
        inspect_database
        ;;
    dbshell)
        check_docker
        database_shell
        ;;
    createsuperuser)
        check_docker
        create_superuser
        ;;
    check)
        check_docker
        check_config
        ;;
    dev)
        check_docker
        dev_mode
        ;;
    status)
        check_docker
        show_status
        ;;
    resetdb)
        check_docker
        reset_database
        ;;
    collectstatic)
        check_docker
        docker exec $DJANGO_CONTAINER python manage.py collectstatic --noinput
        ;;
    test)
        check_docker
        docker exec $DJANGO_CONTAINER python manage.py test
        ;;
    requirements)
        echo "# Ejecutar en el contenedor Django:"
        echo "pip freeze > requirements.txt"
        ;;
    marcar-salidas)
        check_docker
        echo -e "${BLUE}⏰ Ejecutando marcación automática de salidas...${NC}"
        RESPONSE=$(docker exec $DJANGO_CONTAINER curl -s -X POST http://localhost:8000/api/asistencia/cron/marcar-salidas/ \
            -H "Content-Type: application/json" \
            -d '{"auth_key":"GIGA_CRON_KEY_2025"}')
        
        if echo "$RESPONSE" | grep -q '"success":true'; then
            MARCADAS=$(echo "$RESPONSE" | grep -o '"total_marcadas":[0-9]*' | cut -d':' -f2)
            echo -e "${GREEN}✅ Se marcaron $MARCADAS salidas automáticas${NC}"
        else
            echo -e "${RED}❌ Error al marcar salidas${NC}"
            echo "$RESPONSE"
        fi
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