#!/usr/bin/env python
"""
Management command para archivar incidencias cerradas antiguas.
Mueve incidencias cerradas/resueltas más antiguas de N meses a la tabla incidencia_archivo.
"""
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Archiva incidencias cerradas/resueltas antiguas (> N meses) a la tabla incidencia_archivo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months',
            type=int,
            default=12,
            help='Archivar incidencias cerradas más antiguas de MONTHS meses (default: 12)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar conteo sin archivar'
        )

    def handle(self, *args, **options):
        months = options['months']
        dry_run = options['dry_run']
        
        try:
            with connection.cursor() as cursor:
                # Primero verificar si la tabla de archivo existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'incidencia_archivo'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    self.stdout.write(self.style.ERROR(
                        'La tabla incidencia_archivo no existe. '
                        'Ejecute el script 07-retention-optimization.sql primero.'
                    ))
                    return
                
                # Contar registros candidatos
                cursor.execute("""
                    SELECT COUNT(*) FROM incidencia 
                    WHERE estado IN ('cerrada', 'resuelta')
                      AND fecha_resolucion < CURRENT_TIMESTAMP - INTERVAL '%s months'
                """, [months])
                count = cursor.fetchone()[0]
                
                self.stdout.write(self.style.WARNING(
                    f'Incidencias cerradas/resueltas candidatas (> {months} meses): {count}'
                ))
                
                if dry_run:
                    self.stdout.write(self.style.NOTICE('Dry run: no se archivaron incidencias.'))
                    return
                
                if count == 0:
                    self.stdout.write(self.style.SUCCESS('No hay incidencias para archivar.'))
                    return
                
                # Ejecutar función de archivo
                cursor.execute("SELECT * FROM archivar_incidencias(%s)", [months])
                result = cursor.fetchone()
                
                if result:
                    archivados, eliminados = result
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Archivados: {archivados} incidencias, Eliminadas de tabla principal: {eliminados}'
                    ))
                    logger.info(f'archivar_incidencias ejecutado: archivados={archivados}, eliminados={eliminados}')
                else:
                    self.stdout.write(self.style.WARNING('No se obtuvieron resultados de la función.'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al archivar incidencias: {str(e)}'))
            logger.exception('Error ejecutando archivar_incidencias')
            raise
