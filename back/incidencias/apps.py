from django.apps import AppConfig


class IncidenciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incidencias'
    verbose_name = 'Incidencias y Reclamos'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import incidencias.signals