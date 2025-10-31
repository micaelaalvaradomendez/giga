from django.db import models


class TipoLicencia(models.Model):
    id_tipo_licencia = models.BigAutoField(primary_key=True)
    codigo = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_licencia'
        
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class ParteDiario(models.Model):
    id_parte_diario = models.BigAutoField(primary_key=True)
    fecha_parte = models.DateField()
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente')

    class Meta:
        managed = False
        db_table = 'parte_diario'
        
    def __str__(self):
        return f"Parte {self.fecha_parte} - {self.id_agente}"


class Licencia(models.Model):
    id_licencia = models.BigAutoField(primary_key=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    id_tipo_licencia = models.ForeignKey(TipoLicencia, models.DO_NOTHING, db_column='id_tipo_licencia')
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente')

    class Meta:
        managed = False
        db_table = 'licencia'
        
    def __str__(self):
        return f"Licencia {self.id_tipo_licencia} - {self.id_agente}"


class Asistencia(models.Model):
    id_asistencia = models.BigAutoField(primary_key=True)
    tipo = models.CharField(max_length=50)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    es_correccion = models.BooleanField(blank=True, null=True)
    creado_por = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='creado_por')
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente', related_name='asistencia_id_agente_set')
    id_parte_diario = models.ForeignKey(ParteDiario, models.DO_NOTHING, db_column='id_parte_diario')

    class Meta:
        managed = False
        db_table = 'asistencia'
        
    def __str__(self):
        return f"Asistencia {self.tipo} - {self.id_agente}"
