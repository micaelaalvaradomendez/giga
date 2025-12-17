from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0001_initial'), 
        ('guardias', '0001_initial'),
    ]

    operations = [
        # =========================
        # Campos de período
        # =========================
        migrations.AddField(
            model_name='cronograma',
            name='anio',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='mes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='fecha_desde',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='fecha_hasta',
            field=models.DateField(blank=True, null=True),
        ),

        # =========================
        # Aprobación jerárquica
        # =========================
        migrations.AddField(
            model_name='cronograma',
            name='creado_por_rol',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                help_text='jefatura, director, administrador'
            ),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='creado_por',
            field=models.ForeignKey(
                to='personas.agente',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cronogramas_creados',
            ),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='aprobado_por',
            field=models.ForeignKey(
                to='personas.agente',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cronogramas_aprobados',
            ),
        ),
    ]
