#!/usr/bin/env python
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import cleanup_sessions

logger = logging.getLogger(__name__)
_scheduler = None

def start_scheduler():
    """
    Inicia un scheduler en background que ejecuta cleanup_sessions una vez al día.
    Control por variable de entorno SCHEDULER_ENABLED (default 'true').
    Evitar múltiples arranques: guarda el objeto en _scheduler.
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
        # Programar tarea diaria a las 03:00 (UTC local ajustar si hace falta)
        scheduler.add_job(
            _run_cleanup,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup_sessions_daily',
            replace_existing=True,
            max_instances=1
        )
        scheduler.start()
        _scheduler = scheduler
        logger.info('Scheduler iniciado: job cleanup_sessions_daily programado.')
    except Exception as e:
        logger.exception(f'Error iniciando scheduler: {e}')

def _run_cleanup():
    try:
        cleanup_sessions(days=7, dry_run=False)
    except Exception:
        logger.exception('Error ejecutando cleanup_sessions desde scheduler.')
