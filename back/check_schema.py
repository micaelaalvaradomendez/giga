import os
import django
from django.apps import apps
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "giga.settings")
django.setup()

def check_schema():
    print("=== INICIANDO AUDITORÍA DE ESQUEMA ===")
    
    # Obtener todas las tablas de la BD
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name, column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'public';
        """)
        db_columns = {}
        for row in cursor.fetchall():
            table_name = row[0]
            col_name = row[1]
            if table_name not in db_columns:
                db_columns[table_name] = {}
            db_columns[table_name][col_name] = {
                'type': row[2],
                'nullable': row[3] == 'YES'
            }

    print(f"Tablas en BD encontradas: {len(db_columns)}")
    
    models = apps.get_models()
    errors = []
    
    for model in models:
        if model._meta.proxy:
            continue
            
        table_name = model._meta.db_table
        print(f"\nVerificando modelo: {model.__name__} (Tabla: {table_name})")
        
        if table_name not in db_columns:
            # Ignorar tablas de django/auth si no están (aunque deberían estar)
            if 'django' in table_name or 'auth' in table_name:
                continue
            msg = f"❌ TABLA FALTANTE: {table_name} (Modelo: {model.__name__})"
            print(msg)
            errors.append(msg)
            continue
            
        # Verificar campos
        for field in model._meta.fields:
            col_name = field.column
            if col_name not in db_columns[table_name]:
                msg = f"❌ COLUMNA FALTANTE: {table_name}.{col_name} (Campo: {field.name})"
                print(msg)
                errors.append(msg)
            else:
                # Verificación básica de nullabilidad
                db_nullable = db_columns[table_name][col_name]['nullable']
                model_nullable = field.null
                
                # Nota: Django CharField(blank=True) no implica null=True en BD, pero null=True sí.
                if model_nullable and not db_nullable and not field.primary_key:
                     # Excepción: campos que son PK suelen ser NOT NULL en BD pero null=False en Django
                     msg = f"⚠️ DISCREPANCIA NULL: {table_name}.{col_name} -> Django: null={model_nullable}, BD: nullable={db_nullable}"
                     print(msg)

    print("\n=== RESUMEN DE ERRORES ===")
    if errors:
        for err in errors:
            print(err)
    else:
        print("✅ No se encontraron errores críticos de esquema (tablas/columnas faltantes).")

if __name__ == "__main__":
    check_schema()
