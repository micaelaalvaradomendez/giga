from django.db import models


class Auditoria(models.Model):
    id_auditoria = models.BigAutoField(primary_key=True)
    pk_afectada = models.BigIntegerField()
    nombre_tabla = models.CharField(max_length=100)
    creado_en = models.DateTimeField(blank=True, null=True)
    valor_previo = models.JSONField(blank=True, null=True)
    valor_nuevo = models.JSONField(blank=True, null=True)
    accion = models.CharField(max_length=50)
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria'
        
    def __str__(self):
        return f"{self.accion} en {self.nombre_tabla} (ID: {self.pk_afectada})"
