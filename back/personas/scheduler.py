#!/usr/bin/env python
"""
Scheduler para tareas de mantenimiento del sistema GIGA.
Incluye limpieza de sesiones y archivado de datos antiguos.
"""
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import cleanup_sessions, archive_old_audits, archive_old_incidencias

logger = logging.getLogger(__name__)
_scheduler = None


def start_scheduler():
    """
    Inicia un scheduler en background con tareas de mantenimiento:
    - cleanup_sessions: diario a las 03:00 - limpia sesiones inactivas
    - archive_audits: semanal (domingo 04:00) - archiva auditorías > 6 meses
    - archive_incidencias: mensual (día 1, 04:30) - archiva incidencias cerradas > 12 meses
    
    Control por variable de entorno SCHEDULER_ENABLED (default 'true').
    """
    global _scheduler
    enabled = os.environ.get('SCHEDULER_ENABLED', 'true').lower()
    if enabled not in ('1', 'true', 'yes'):
        logger.info('Scheduler deshabilitado por SCHEDULER_ENABLED env var.')
        return

    if _scheduler is not None:
        logger.debug('Scheduler ya iniciado, saltando start.')
        return

    try:
        scheduler = BackgroundScheduler()
        
        # Tarea diaria: limpieza de sesiones a las 03:00
        scheduler.add_job(
            _run_cleanup,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup_sessions_daily',
            replace_existing=True,
            max_instances=1
        )
        
        # Tarea semanal: archivado de auditorías (domingo a las 04:00)
        scheduler.add_job(
            _run_archive_audits,
            trigger=CronTrigger(day_of_week='sun', hour=4, minute=0),
            id='archive_audits_weekly',
            replace_existing=True,
            max_instances=1
        )
        
        # Tarea mensual: archivado de incidencias (día 1 a las 04:30)
        scheduler.add_job(
            _run_archive_incidencias,
            trigger=CronTrigger(day=1, hour=4, minute=30),
            id='archive_incidencias_monthly',
            replace_existing=True,
            max_instances=1
        )
        
        scheduler.start()
        _scheduler = scheduler
        logger.info(
            'Scheduler iniciado: cleanup_sessions_daily, '
            'archive_audits_weekly, archive_incidencias_monthly programados.'
        )
    except Exception as e:
        logger.exception(f'Error iniciando scheduler: {e}')


def _run_cleanup():
    """Ejecuta limpieza de sesiones inactivas."""
    try:
        result = cleanup_sessions(days=7, dry_run=False)
        logger.info(f'cleanup_sessions completado: {result}')
    except Exception:
        logger.exception('Error ejecutando cleanup_sessions desde scheduler.')


def _run_archive_audits():
    """Ejecuta archivado de auditorías antiguas."""
    try:
        result = archive_old_audits(months=6, dry_run=False)
        logger.info(f'archive_old_audits completado: {result}')
    except Exception:
        logger.exception('Error ejecutando archive_old_audits desde scheduler.')


def _run_archive_incidencias():
    """Ejecuta archivado de incidencias cerradas antiguas."""
    try:
        result = archive_old_incidencias(months=12, dry_run=False)
        logger.info(f'archive_old_incidencias completado: {result}')
    except Exception:
        logger.exception('Error ejecutando archive_old_incidencias desde scheduler.')
