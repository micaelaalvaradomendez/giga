from django.apps import AppConfig
import logging
import sys

logger = logging.getLogger(__name__)

class PersonasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "personas"

    def ready(self):
        # Iniciar scheduler solo en proceso de servidor (evitar comandos manage.py como migrate)
        try:
            # Evitar ejecución en procesos de migración/collectstatic/tests:
            disallowed = ['makemigrations', 'migrate', 'collectstatic', 'test', 'shell', 'loaddata']
            if len(sys.argv) > 1 and sys.argv[1] in disallowed:
                logger.debug('No se inicia scheduler (comando manage.py detectado).')
                return

            # IMPORT TARDÍO para no cargar APScheduler en contextos no web
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception:
            logger.exception('Error al iniciar el scheduler en ready() de PersonasConfig.')
