#!/bin/bash

# Script de utilidades para la base de datos GIGA PostgreSQL
# Uso: ./db-utils.sh [comando] [opciones]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
DB_CONTAINER="giga-postgres"
DB_NAME="giga"
DB_USER="giga_user"
DB_PASSWORD="giga2025"
BACKUP_DIR="./backups"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🐘 GIGA PostgreSQL Database Utils${NC}"
    echo ""
    echo "Uso: $0 [comando] [opciones]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start          - Iniciar los servicios de base de datos"
    echo "  stop           - Detener los servicios de base de datos"
    echo "  restart        - Reiniciar los servicios"
    echo "  status         - Mostrar estado de los servicios"
    echo "  logs           - Mostrar logs de PostgreSQL"
    echo "  shell          - Conectar a PostgreSQL (psql)"
    echo "  backup         - Crear backup de la base de datos"
    echo "  restore [file] - Restaurar backup desde archivo"
    echo "  reset          - Resetear base de datos (⚠️  DESTRUCTIVO)"
    echo "  admin          - Iniciar PgAdmin (puerto 8080)"
    echo "  build          - Construir imagen de Docker"
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

# Función para iniciar servicios
start_services() {
    echo -e "${BLUE}🚀 Iniciando servicios de base de datos...${NC}"
    docker-compose up -d postgres
    echo -e "${GREEN}✅ Servicios iniciados${NC}"
    
    # Esperar a que la base de datos esté lista
    echo -e "${YELLOW}⏳ Esperando a que PostgreSQL esté listo...${NC}"
    timeout 60 bash -c 'until docker exec $0 pg_isready -U $1 -d $2; do sleep 2; done' $DB_CONTAINER $DB_USER $DB_NAME
    echo -e "${GREEN}✅ PostgreSQL está listo${NC}"
}

# Función para detener servicios
stop_services() {
    echo -e "${BLUE}🛑 Deteniendo servicios de base de datos...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para mostrar logs
show_logs() {
    echo -e "${BLUE}📋 Logs de PostgreSQL:${NC}"
    docker-compose logs -f postgres
}

# Función para conectar a la base de datos
connect_db() {
    echo -e "${BLUE}🔗 Conectando a PostgreSQL...${NC}"
    docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
}

# Función para crear backup
create_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/giga_backup_$timestamp.sql"
    
    echo -e "${BLUE}💾 Creando backup...${NC}"
    mkdir -p $BACKUP_DIR
    
    docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $backup_file
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup creado: $backup_file${NC}"
        
        # Comprimir el backup
        gzip $backup_file
        echo -e "${GREEN}✅ Backup comprimido: $backup_file.gz${NC}"
    else
        echo -e "${RED}❌ Error al crear backup${NC}"
        exit 1
    fi
}

# Función para restaurar backup
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        echo -e "${RED}❌ Debes especificar el archivo de backup${NC}"
        echo "Uso: $0 restore <archivo_backup>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Archivo de backup no encontrado: $backup_file${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}⚠️  ¿Estás seguro de restaurar el backup? Esto sobrescribirá los datos actuales.${NC}"
    read -p "Escribe 'YES' para continuar: " confirm
    
    if [ "$confirm" != "YES" ]; then
        echo -e "${BLUE}❌ Restauración cancelada${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}📥 Restaurando backup...${NC}"
    
    # Si el archivo está comprimido, descomprimirlo temporalmente
    if [[ $backup_file == *.gz ]]; then
        zcat $backup_file | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
    else
        cat $backup_file | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup restaurado correctamente${NC}"
    else
        echo -e "${RED}❌ Error al restaurar backup${NC}"
        exit 1
    fi
}

# Función para resetear la base de datos
reset_database() {
    echo -e "${RED}⚠️  PELIGRO: Esto eliminará TODOS los datos de la base de datos${NC}"
    echo -e "${YELLOW}¿Estás seguro de que quieres resetear la base de datos?${NC}"
    read -p "Escribe 'DELETE_ALL_DATA' para continuar: " confirm
    
    if [ "$confirm" != "DELETE_ALL_DATA" ]; then
        echo -e "${BLUE}❌ Reseteo cancelado${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}🗑️  Reseteando base de datos...${NC}"
    docker-compose down -v
    docker-compose up -d postgres
    
    echo -e "${GREEN}✅ Base de datos reseteada${NC}"
}

# Función para iniciar PgAdmin
start_admin() {
    echo -e "${BLUE}🎛️  Iniciando PgAdmin...${NC}"
    docker-compose --profile admin up -d pgadmin
    echo -e "${GREEN}✅ PgAdmin disponible en: http://localhost:8080${NC}"
    echo -e "${YELLOW}📧 Usuario: admin@giga.local${NC}"
    echo -e "${YELLOW}🔑 Contraseña: admin2025${NC}"
}

# Función para construir imagen
build_image() {
    echo -e "${BLUE}🔨 Construyendo imagen de PostgreSQL...${NC}"
    docker-compose build postgres
    echo -e "${GREEN}✅ Imagen construida${NC}"
}

# Función para mostrar estado
show_status() {
    echo -e "${BLUE}📊 Estado de los servicios:${NC}"
    docker-compose ps
    echo ""
    
    if docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME 2>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL está funcionando correctamente${NC}"
    else
        echo -e "${RED}❌ PostgreSQL no está disponible${NC}"
    fi
}

# Main script
case "$1" in
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
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    shell)
        check_docker
        connect_db
        ;;
    backup)
        check_docker
        create_backup
        ;;
    restore)
        check_docker
        restore_backup "$2"
        ;;
    reset)
        check_docker
        reset_database
        ;;
    admin)
        check_docker
        start_admin
        ;;
    build)
        check_docker
        build_image
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