#!/usr/bin/env python
"""
Management command para archivar registros de auditoría antiguos.
Mueve registros más antiguos de N meses a la tabla auditoria_archivo.
"""
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Archiva registros de auditoría antiguos (> N meses) a la tabla auditoria_archivo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months',
            type=int,
            default=6,
            help='Archivar auditorías más antiguas de MONTHS meses (default: 6)'
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
                        WHERE table_name = 'auditoria_archivo'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    self.stdout.write(self.style.ERROR(
                        'La tabla auditoria_archivo no existe. '
                        'Ejecute el script 07-retention-optimization.sql primero.'
                    ))
                    return
                
                # Contar registros candidatos
                cursor.execute("""
                    SELECT COUNT(*) FROM auditoria 
                    WHERE creado_en < CURRENT_TIMESTAMP - INTERVAL '%s months'
                """, [months])
                count = cursor.fetchone()[0]
                
                self.stdout.write(self.style.WARNING(
                    f'Registros de auditoría candidatos (> {months} meses): {count}'
                ))
                
                if dry_run:
                    self.stdout.write(self.style.NOTICE('Dry run: no se archivaron registros.'))
                    return
                
                if count == 0:
                    self.stdout.write(self.style.SUCCESS('No hay registros para archivar.'))
                    return
                
                # Ejecutar función de archivo
                cursor.execute("SELECT * FROM archivar_auditorias(%s)", [months])
                result = cursor.fetchone()
                
                if result:
                    archivados, eliminados = result
                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Archivados: {archivados} registros, Eliminados de tabla principal: {eliminados}'
                    ))
                    logger.info(f'archivar_auditorias ejecutado: archivados={archivados}, eliminados={eliminados}')
                else:
                    self.stdout.write(self.style.WARNING('No se obtuvieron resultados de la función.'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al archivar auditorías: {str(e)}'))
            logger.exception('Error ejecutando archivar_auditorias')
            raise
