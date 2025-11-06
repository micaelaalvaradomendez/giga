from django.db import models


class Auditoria(models.Model):
    id_auditoria = models.BigAutoField(primary_key=True)
    pk_afectada = models.BigIntegerField(blank=True, null=True)
    nombre_tabla = models.CharField(max_length=100, blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    valor_previo = models.JSONField(blank=True, null=True)
    valor_nuevo = models.JSONField(blank=True, null=True)
    accion = models.CharField(max_length=50)
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente', blank=True, null=True)
    # Campo adicional (detalle se almacena en valor_nuevo como JSON)
    # fecha_hora no existe en la tabla real - usar creado_en

    class Meta:
        managed = False
        db_table = 'auditoria'
        
    @property
    def id(self):
        """Alias para compatibilidad"""
        return self.id_auditoria
        
    def __str__(self):
        if self.nombre_tabla and self.pk_afectada:
            return f"{self.accion} en {self.nombre_tabla} (ID: {self.pk_afectada})"
        return f"{self.accion} - {self.detalle[:50] if self.detalle else ''}"
