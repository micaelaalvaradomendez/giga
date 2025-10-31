from django.db import models


class Cronograma(models.Model):
    id_cronograma = models.BigAutoField(primary_key=True)
    fecha_aprobacion = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    id_jefe = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_jefe')
    id_area = models.ForeignKey('personas.Area', models.DO_NOTHING, db_column='id_area')

    class Meta:
        managed = False
        db_table = 'cronograma'
        
    def __str__(self):
        return f"Cronograma {self.tipo} - {self.fecha_aprobacion}"


class Guardia(models.Model):
    id_guardia = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    activa = models.BooleanField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    horas_planificadas = models.IntegerField(blank=True, null=True)
    horas_efectivas = models.IntegerField(blank=True, null=True)
    id_cronograma = models.ForeignKey(Cronograma, models.DO_NOTHING, db_column='id_cronograma')
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente')

    class Meta:
        managed = False
        db_table = 'guardia'
        
    def __str__(self):
        return f"Guardia {self.fecha} - {self.id_agente}"


class ResumenGuardiaMes(models.Model):
    id_resumen_guardia_mes = models.BigAutoField(primary_key=True)
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente')
    mes = models.IntegerField()
    anio = models.IntegerField()
    plus20 = models.BooleanField(blank=True, null=True)
    plus40 = models.BooleanField(blank=True, null=True)
    total_horas_guardia = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resumen_guardia_mes'
        unique_together = (('id_agente', 'mes', 'anio'),)
        
    def __str__(self):
        return f"Resumen {self.mes}/{self.anio} - {self.id_agente}"
