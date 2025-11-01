#!/bin/bash

# Script para gestionar la base de datos PostgreSQL aislada
# Uso: ./switch-database.sh [start|stop|restart|status|logs|reset]

set -e

ACTION=${1:-start}
CURRENT_DIR=$(pwd)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${YELLOW}Uso:${NC} ./switch-database.sh [start|stop|restart|status|logs|reset]"
    echo ""
    echo -e "${BLUE}Acciones disponibles:${NC}"
    echo "  - start    : Inicia la base de datos PostgreSQL"
    echo "  - stop     : Detiene la base de datos"
    echo "  - restart  : Reinicia la base de datos"
    echo "  - status   : Muestra el estado actual"
    echo "  - logs     : Muestra los logs de la base de datos"
    echo "  - reset    : Elimina todos los datos y reinicia desde cero"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  ./switch-database.sh start"
    echo "  ./switch-database.sh logs"
    echo "  ./switch-database.sh reset"
}

# Validar acción
case $ACTION in
    start|stop|restart|status|logs|reset)
        echo -e "${GREEN}✓ Acción válida: $ACTION${NC}"
        ;;
    *)
        echo -e "${RED}Error: Acción no válida: $ACTION${NC}"
        print_usage
        exit 1
        ;;
esac

# Verificar que estemos en el directorio correcto
if [ ! -d "db" ]; then
    echo -e "${RED}Error: No se encuentra el directorio 'db'. Ejecuta este script desde la raíz del proyecto.${NC}"
    exit 1
fi

echo -e "${BLUE}=== Gestión de Base de Datos PostgreSQL ===${NC}"

case $ACTION in
    start)
        echo -e "${YELLOW}🚀 Iniciando base de datos PostgreSQL...${NC}"
        
        # Verificar si ya está corriendo
        if docker ps | grep -q "giga_database"; then
            echo -e "${YELLOW}⚠️  La base de datos ya está corriendo${NC}"
            docker ps | grep giga_database
            exit 0
        fi
        
        # Crear .env si no existe
        if [ ! -f db/.env ]; then
            cp db/.env.example db/.env
            echo -e "${GREEN}✓ Creado archivo db/.env${NC}"
        fi
        
        # Iniciar base de datos
        cd db && docker-compose up -d
        
        echo -e "${YELLOW}⏳ Esperando que la base de datos esté lista...${NC}"
        sleep 15
        
        # Verificar estado
        if docker ps | grep -q "giga_database"; then
            echo -e "${GREEN}✅ Base de datos PostgreSQL iniciada correctamente${NC}"
            echo -e "${BLUE}Puerto:${NC} 5432"
            echo -e "${BLUE}Conexión:${NC} psql -h localhost -p 5432 -U giga_user giga"
        else
            echo -e "${RED}❌ Error al iniciar la base de datos${NC}"
            exit 1
        fi
        ;;
        
    stop)
        echo -e "${YELLOW}🛑 Deteniendo base de datos PostgreSQL...${NC}"
        cd db && docker-compose down
        echo -e "${GREEN}✅ Base de datos detenida${NC}"
        ;;
        
    restart)
        echo -e "${YELLOW}🔄 Reiniciando base de datos PostgreSQL...${NC}"
        cd db && docker-compose restart
        echo -e "${GREEN}✅ Base de datos reiniciada${NC}"
        ;;
        
    status)
        echo -e "${BLUE}📊 Estado de la base de datos:${NC}"
        if docker ps | grep -q "giga_database"; then
            echo -e "${GREEN}✅ RUNNING${NC}"
            docker ps | grep giga_database
            echo ""
            echo -e "${BLUE}Información de conexión:${NC}"
            echo "Host: localhost"
            echo "Puerto: 5432"
            echo "Base de datos: giga"
            echo "Usuario: giga_user"
        else
            echo -e "${RED}❌ STOPPED${NC}"
        fi
        ;;
        
    logs)
        echo -e "${BLUE}📋 Logs de la base de datos:${NC}"
        cd db && docker-compose logs -f
        ;;
        
    reset)
        echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará TODOS los datos de la base de datos${NC}"
        echo -e "${YELLOW}¿Estás seguro? Escribe 'CONFIRMAR' para continuar:${NC}"
        read -p "" confirm
        if [ "$confirm" = "CONFIRMAR" ]; then
            echo -e "${YELLOW}🗑️  Eliminando datos y reiniciando...${NC}"
            cd db
            docker-compose down -v
            docker volume rm giga_db_data 2>/dev/null || true
            docker volume rm giga_db_logs 2>/dev/null || true
            docker-compose up -d
            echo -e "${GREEN}✅ Base de datos reiniciada desde cero${NC}"
        else
            echo -e "${BLUE}Operación cancelada${NC}"
        fi
        ;;
esac