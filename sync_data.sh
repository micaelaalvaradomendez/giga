#!/bin/bash

# Script para sincronizar datos después del docker compose up
echo " Sincronizando datos de la base de datos..."

# Verificar si existe backup más reciente que los datos actuales
if [ -f "data_backup/initial_data.json" ]; then
    echo " Encontrado backup de datos, verificando si necesita actualización..."
    
    # Importar datos desde el backup más reciente
    sudo docker exec giga_back python manage.py shell -c "
from django.core.management import call_command
import os
import json

# Verificar si el backup es más reciente que los datos actuales
backup_file = '/app/../data_backup/initial_data.json'
if os.path.exists(backup_file):
    print(' Restaurando datos desde backup...')
    try:
        # Limpiar datos existentes (excepto superusuarios)
        from personas.models import Usuario, Agente, AgenteRol
        from asistencia.models import Licencia, TipoLicencia
        
        # Solo limpiar si hay más de 6 usuarios (los básicos)
        user_count = Usuario.objects.count()
        if user_count > 6:
            print(f'  Limpiando datos existentes ({user_count} usuarios)...')
            Licencia.objects.all().delete()
            AgenteRol.objects.all().delete()
            Agente.objects.all().delete()
            Usuario.objects.filter(is_superuser=False).delete()
        
        # Cargar datos desde backup
        call_command('loaddata', '/app/../data_backup/initial_data.json')
        print(' Datos restaurados correctamente desde backup!')
    except Exception as e:
        print(f' Error restaurando datos: {e}')
        print(' Cargando datos básicos como fallback...')
        # Fallback a los fixtures básicos si hay error
        call_command('loaddata', 'personas/fixtures/roles_basicos.json')
        call_command('loaddata', 'personas/fixtures/area_basica.json')
        call_command('loaddata', 'personas/fixtures/usuarios_agentes.json')
        call_command('loaddata', 'personas/fixtures/asignacion_roles.json')
        call_command('loaddata', 'asistencia/fixtures/tipos_licencia.json')
        call_command('loaddata', 'asistencia/fixtures/licencias_basicas.json')
        print(' Datos básicos cargados como fallback!')
else:
    print('  No se encontró backup, usando datos por defecto')
"
    
    echo " Sincronización completada!"
else
    echo "  No se encontró backup de datos, los datos por defecto ya están cargados."
fi