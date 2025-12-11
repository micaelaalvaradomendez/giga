#!/usr/bin/env python
"""
Management command para mostrar estadísticas de uso de espacio en la base de datos.
Útil para monitorear el crecimiento de tablas y planificar retención.
"""
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Muestra estadísticas de uso de espacio de las tablas principales del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostrar estadísticas detalladas incluyendo índices'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        
        try:
            with connection.cursor() as cursor:
                # Estadísticas de tablas principales
                self.stdout.write(self.style.HTTP_INFO('\n📊 ESTADÍSTICAS DE TABLAS PRINCIPALES\n'))
                self.stdout.write('=' * 80)
                
                cursor.execute("""
                    SELECT 
                        relname as tabla,
                        n_live_tup as filas_vivas,
                        n_dead_tup as filas_muertas,
                        pg_size_pretty(pg_total_relation_size(relid)) as tamano_total,
                        pg_size_pretty(pg_relation_size(relid)) as tamano_datos,
                        last_vacuum::date as ultimo_vacuum,
                        last_autovacuum::date as ultimo_autovacuum
                    FROM pg_stat_user_tables
                    WHERE relname IN (
                        'auditoria', 'auditoria_archivo', 
                        'incidencia', 'incidencia_archivo',
                        'sesion_activa', 'django_session',
                        'asistencia', 'guardia', 'licencia',
                        'agente', 'area', 'cronograma'
                    )
                    ORDER BY pg_total_relation_size(relid) DESC
                """)
                
                rows = cursor.fetchall()
                
                self.stdout.write(f'\n{"Tabla":<25} {"Filas":<12} {"Muertas":<10} {"Tamaño":<12} {"Datos":<12} {"Vacuum":<12}')
                self.stdout.write('-' * 80)
                
                for row in rows:
                    tabla, filas, muertas, tamano, datos, vacuum, auto_vacuum = row
                    vacuum_str = str(vacuum) if vacuum else 'N/A'
                    self.stdout.write(
                        f'{tabla:<25} {filas:<12} {muertas:<10} {tamano:<12} {datos:<12} {vacuum_str:<12}'
                    )
                
                # Estadísticas de sesiones
                self.stdout.write(self.style.HTTP_INFO('\n\n🔐 ESTADÍSTICAS DE SESIONES\n'))
                self.stdout.write('=' * 60)
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE activa = true) as activas,
                        COUNT(*) FILTER (WHERE activa = false) as inactivas,
                        COUNT(*) FILTER (WHERE ultimo_acceso < NOW() - INTERVAL '7 days') as antiguas_7d
                    FROM sesion_activa
                """)
                sa_stats = cursor.fetchone()
                
                cursor.execute("SELECT COUNT(*) FROM django_session")
                ds_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM django_session WHERE expire_date < NOW()")
                ds_expired = cursor.fetchone()[0]
                
                self.stdout.write(f'\nSesionActiva:')
                self.stdout.write(f'  Total: {sa_stats[0]}')
                self.stdout.write(f'  Activas: {sa_stats[1]}')
                self.stdout.write(f'  Inactivas: {sa_stats[2]}')
                self.stdout.write(f'  Antiguas (>7 días): {sa_stats[3]}')
                self.stdout.write(f'\nDjango Sessions:')
                self.stdout.write(f'  Total: {ds_count}')
                self.stdout.write(f'  Expiradas: {ds_expired}')
                
                # Estadísticas de auditoría
                self.stdout.write(self.style.HTTP_INFO('\n\n📝 ESTADÍSTICAS DE AUDITORÍA\n'))
                self.stdout.write('=' * 60)
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE creado_en >= NOW() - INTERVAL '30 days') as ultimos_30d,
                        COUNT(*) FILTER (WHERE creado_en >= NOW() - INTERVAL '6 months') as ultimos_6m,
                        COUNT(*) FILTER (WHERE creado_en < NOW() - INTERVAL '6 months') as archivables,
                        MIN(creado_en)::date as registro_mas_antiguo
                    FROM auditoria
                """)
                audit_stats = cursor.fetchone()
                
                # Verificar si existe tabla archivo
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'auditoria_archivo'
                    )
                """)
                archivo_exists = cursor.fetchone()[0]
                
                archived_count = 0
                if archivo_exists:
                    cursor.execute("SELECT COUNT(*) FROM auditoria_archivo")
                    archived_count = cursor.fetchone()[0]
                
                self.stdout.write(f'\nAuditoría principal:')
                self.stdout.write(f'  Total: {audit_stats[0]}')
                self.stdout.write(f'  Últimos 30 días: {audit_stats[1]}')
                self.stdout.write(f'  Últimos 6 meses: {audit_stats[2]}')
                self.stdout.write(f'  Archivables (>6 meses): {audit_stats[3]}')
                self.stdout.write(f'  Registro más antiguo: {audit_stats[4]}')
                self.stdout.write(f'\nAuditoría archivo:')
                self.stdout.write(f'  Total archivadas: {archived_count}')
                
                # Estadísticas de incidencias
                self.stdout.write(self.style.HTTP_INFO('\n\n🎫 ESTADÍSTICAS DE INCIDENCIAS\n'))
                self.stdout.write('=' * 60)
                
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'incidencia'
                    )
                """)
                incidencia_exists = cursor.fetchone()[0]
                
                if incidencia_exists:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(*) FILTER (WHERE estado IN ('abierta', 'en_proceso', 'pendiente_informacion')) as abiertas,
                            COUNT(*) FILTER (WHERE estado IN ('cerrada', 'resuelta')) as cerradas,
                            COUNT(*) FILTER (WHERE estado IN ('cerrada', 'resuelta') AND fecha_resolucion < NOW() - INTERVAL '12 months') as archivables
                        FROM incidencia
                    """)
                    inc_stats = cursor.fetchone()
                    
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'incidencia_archivo'
                        )
                    """)
                    inc_archivo_exists = cursor.fetchone()[0]
                    
                    inc_archived = 0
                    if inc_archivo_exists:
                        cursor.execute("SELECT COUNT(*) FROM incidencia_archivo")
                        inc_archived = cursor.fetchone()[0]
                    
                    self.stdout.write(f'\nIncidencias principal:')
                    self.stdout.write(f'  Total: {inc_stats[0]}')
                    self.stdout.write(f'  Abiertas/En proceso: {inc_stats[1]}')
                    self.stdout.write(f'  Cerradas/Resueltas: {inc_stats[2]}')
                    self.stdout.write(f'  Archivables (>12 meses): {inc_stats[3]}')
                    self.stdout.write(f'\nIncidencias archivo:')
                    self.stdout.write(f'  Total archivadas: {inc_archived}')
                else:
                    self.stdout.write('  Tabla incidencia no existe')
                
                if detailed:
                    # Mostrar índices
                    self.stdout.write(self.style.HTTP_INFO('\n\n🔍 ÍNDICES DE TABLAS PRINCIPALES\n'))
                    self.stdout.write('=' * 80)
                    
                    cursor.execute("""
                        SELECT 
                            tablename,
                            indexname,
                            pg_size_pretty(pg_relation_size(indexrelid)) as size
                        FROM pg_indexes
                        JOIN pg_class ON pg_class.relname = indexname
                        WHERE tablename IN (
                            'auditoria', 'incidencia', 'sesion_activa', 
                            'django_session', 'asistencia', 'guardia'
                        )
                        ORDER BY tablename, pg_relation_size(indexrelid) DESC
                    """)
                    
                    current_table = None
                    for row in cursor.fetchall():
                        if row[0] != current_table:
                            current_table = row[0]
                            self.stdout.write(f'\n{current_table}:')
                        self.stdout.write(f'  {row[1]} ({row[2]})')
                
                self.stdout.write('\n')
                self.stdout.write(self.style.SUCCESS('✅ Estadísticas generadas correctamente'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al obtener estadísticas: {str(e)}'))
            logger.exception('Error en db_stats')
            raise
