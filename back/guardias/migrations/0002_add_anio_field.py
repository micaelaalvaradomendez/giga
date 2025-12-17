# Generated migration to add anio field to cronograma table

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
    ]
