#!/usr/bin/env python
from django.core.management.base import BaseCommand
from personas.tasks import cleanup_sessions
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Limpia sesiones inactivas/antiguas: borra sesion_activa y entradas django_session asociadas.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Eliminar sesiones inactivas y con ultimo_acceso older than DAYS (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='No borra nada, solo muestra conteo'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        result = cleanup_sessions(days=days, dry_run=dry_run)

        self.stdout.write(self.style.WARNING(f"Sesiones candidatas: {result['candidatas']}"))
        if dry_run:
            self.stdout.write(self.style.NOTICE('Dry run: no se eliminaron filas.'))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Borradas {result['sesion_activa_deleted']} filas de sesion_activa y {result['django_session_deleted']} filas de django_session (aprox)."
        ))
        logger.info('cleanup_sessions command ejecutado.')
