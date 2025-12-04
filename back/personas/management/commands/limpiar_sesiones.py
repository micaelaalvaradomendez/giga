"""
Comando para limpiar sesiones expiradas.
Uso: python manage.py limpiar_sesiones
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from personas.models import SesionActiva
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = 'Limpia sesiones expiradas (inactivas por más de 1 hora)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Horas de inactividad después de las cuales limpiar sesiones'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        hace_n_horas = timezone.now() - timedelta(hours=hours)
        
        # Buscar sesiones inactivas
        sesiones_expiradas = SesionActiva.objects.filter(
            ultimo_acceso__lt=hace_n_horas,
            activa=True
        )
        
        count = sesiones_expiradas.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No hay sesiones expiradas para limpiar'))
            return
        
        # Marcar como inactivas
        sesiones_expiradas.update(activa=False)
        
        # Eliminar de django_session
        session_keys = list(sesiones_expiradas.values_list('session_key', flat=True))
        Session.objects.filter(session_key__in=session_keys).delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Limpiadas {count} sesiones inactivas por más de {hours} hora(s)'
            )
        )
