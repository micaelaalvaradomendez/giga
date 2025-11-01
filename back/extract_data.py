#!/usr/bin/env python
"""
Script para extraer todos los datos de la base de datos PostgreSQL
y generar archivos JSON para cada modelo.
"""
import os
import sys
import django
from django.core import serializers
from django.apps import apps
import json
from django.core.serializers.json import DjangoJSONEncoder

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giga.settings')
django.setup()

def extraer_datos_modelo(modelo_class):
    """Extrae todos los datos de un modelo y los convierte a JSON"""
    try:
        queryset = modelo_class.objects.all()
        data = []
        
        for obj in queryset:
            # Usar el serializador JSON de Django
            serialized = serializers.serialize('json', [obj])
            obj_data = json.loads(serialized)[0]
            data.append(obj_data)
        
        return data
    except Exception as e:
        print(f"Error extrayendo datos de {modelo_class.__name__}: {e}")
        return []

def main():
    """Función principal para extraer todos los datos"""
    # Directorio de destino
    output_dir = '/tmp/data_export'
    os.makedirs(output_dir, exist_ok=True)
    
    # Apps de Django a procesar
    apps_to_process = [
        'personas', 
        'asistencia', 
        'guardias', 
        'auditoria', 
        'reportes', 
        'convenio_ia'
    ]
    
    total_registros = 0
    
    for app_name in apps_to_process:
        try:
            app_config = apps.get_app_config(app_name)
            models = app_config.get_models()
            
            app_data = {}
            app_total = 0
            
            print(f"\n=== Extrayendo datos de la app: {app_name} ===")
            
            for model in models:
                model_name = model.__name__
                print(f"Procesando modelo: {model_name}...")
                
                # Extraer datos del modelo
                datos = extraer_datos_modelo(model)
                cantidad = len(datos)
                
                if cantidad > 0:
                    app_data[model_name] = datos
                    app_total += cantidad
                    print(f"  ✓ {model_name}: {cantidad} registros")
                else:
                    print(f"  - {model_name}: Sin datos")
            
            # Guardar datos de la app
            if app_data:
                archivo_json = os.path.join(output_dir, f'{app_name}_data.json')
                with open(archivo_json, 'w', encoding='utf-8') as f:
                    json.dump(app_data, f, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder)
                
                print(f"✓ Guardado: {archivo_json} ({app_total} registros)")
                total_registros += app_total
            else:
                print(f"- No hay datos para guardar en {app_name}")
                
        except Exception as e:
            print(f"Error procesando app {app_name}: {e}")
    
    # Resumen final
    print(f"\n=== RESUMEN ===")
    print(f"Total de registros extraídos: {total_registros}")
    print(f"Archivos JSON generados en: {output_dir}")
    
    # Generar resumen de extracción
    resumen = {
        'fecha_extraccion': str(django.utils.timezone.now()),
        'total_registros': total_registros,
        'apps_procesadas': apps_to_process,
        'directorio_salida': output_dir
    }
    
    archivo_resumen = os.path.join(output_dir, 'extraccion_resumen.json')
    with open(archivo_resumen, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder)
    
    print(f"✓ Resumen guardado: {archivo_resumen}")

if __name__ == '__main__':
    main()