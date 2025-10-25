from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Exporta todos los datos de la base de datos a fixtures JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='data_backup',
            help='Directorio donde guardar los fixtures (por defecto: data_backup)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Modelos a exportar en orden correcto
        models_to_export = [
            # Personas
            ('personas.rol', f'{output_dir}/roles_{timestamp}.json'),
            ('personas.area', f'{output_dir}/areas_{timestamp}.json'),
            ('personas.usuario', f'{output_dir}/usuarios_{timestamp}.json'),
            ('personas.agente', f'{output_dir}/agentes_{timestamp}.json'),
            ('personas.agenterol', f'{output_dir}/asignaciones_{timestamp}.json'),
            
            # Asistencia
            ('asistencia.tipolicencia', f'{output_dir}/tipos_licencia_{timestamp}.json'),
            ('asistencia.licencia', f'{output_dir}/licencias_{timestamp}.json'),
            ('asistencia.marca', f'{output_dir}/marcas_{timestamp}.json'),
            ('asistencia.partediario', f'{output_dir}/partes_diarios_{timestamp}.json'),
            
            # Guardias
            ('guardias.feriado', f'{output_dir}/feriados_{timestamp}.json'),
            ('guardias.reglaplus', f'{output_dir}/reglas_plus_{timestamp}.json'),
        ]
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando exportación de datos...')
        )
        
        for model, output_file in models_to_export:
            try:
                self.stdout.write(f'Exportando {model}...')
                call_command('dumpdata', model, format='json', indent=4, output=output_file)
                self.stdout.write(
                    self.style.SUCCESS(f'   {model} → {output_file}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'    Error exportando {model}: {e}')
                )
        
        # Crear un archivo completo con todos los datos
        complete_file = f'{output_dir}/complete_backup_{timestamp}.json'
        try:
            self.stdout.write('Creando backup completo...')
            call_command('dumpdata', 
                        'personas', 'asistencia', 'guardias', 'auditoria',
                        format='json', 
                        indent=4, 
                        output=complete_file,
                        exclude=['contenttypes', 'auth.permission', 'sessions']
            )
            self.stdout.write(
                self.style.SUCCESS(f'   Backup completo → {complete_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   Error creando backup completo: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n Exportación completada en: {output_dir}/')
        )
        self.stdout.write(' Para versionar estos datos:')
        self.stdout.write(f'   git add {output_dir}/')
        self.stdout.write('   git commit -m "feat: actualizar datos de la base de datos"')
        self.stdout.write('   git push')