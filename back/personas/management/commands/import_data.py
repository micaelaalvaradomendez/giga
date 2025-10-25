from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Importa datos desde fixtures JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='data_backup',
            help='Directorio donde están los fixtures (por defecto: data_backup)'
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Importar los fixtures más recientes automáticamente'
        )

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        
        if not os.path.exists(data_dir):
            self.stdout.write(
                self.style.ERROR(f' El directorio {data_dir} no existe')
            )
            return
        
        if options['latest']:
            # Buscar el archivo de backup más reciente
            backup_files = [f for f in os.listdir(data_dir) if f.startswith('complete_backup_') and f.endswith('.json')]
            if not backup_files:
                self.stdout.write(
                    self.style.ERROR(' No se encontraron archivos de backup')
                )
                return
            
            latest_file = sorted(backup_files)[-1]
            backup_path = os.path.join(data_dir, latest_file)
            
            self.stdout.write(
                self.style.SUCCESS(f' Importando desde: {backup_path}')
            )
            
            try:
                call_command('loaddata', backup_path)
                self.stdout.write(
                    self.style.SUCCESS('Datos importados correctamente!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importando datos: {e}')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('Archivos disponibles en {}:'.format(data_dir))
            )
            for f in sorted(os.listdir(data_dir)):
                if f.endswith('.json'):
                    self.stdout.write(f'  - {f}')
            
            self.stdout.write('\n Para importar automáticamente el más reciente:')
            self.stdout.write('   python manage.py import_data --latest')