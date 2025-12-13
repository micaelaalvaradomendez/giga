# Generated migration for adding performance indices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0003_sesionactiva'),
    ]

    operations = [
        # Add composite indices for Agente lookups (these can be used for single-column queries too)
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_agente_cuil_activo ON agente(cuil, activo);
                CREATE INDEX IF NOT EXISTS idx_agente_dni_activo ON agente(dni, activo);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS idx_agente_cuil_activo;
                DROP INDEX IF EXISTS idx_agente_dni_activo;
            """
        ),
        # Add indices for SesionActiva
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS idx_sesion_activa_agente ON sesion_activa(id_agente, activa);
                CREATE INDEX IF NOT EXISTS idx_sesion_activa_session_key ON sesion_activa(session_key);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS idx_sesion_activa_agente;
                DROP INDEX IF EXISTS idx_sesion_activa_session_key;
            """
        ),
    ]
