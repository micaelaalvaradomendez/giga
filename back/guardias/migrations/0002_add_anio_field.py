from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guardias', '0001_initial'),
    ]

    operations = [
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
    ]
