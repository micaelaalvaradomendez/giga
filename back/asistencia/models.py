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
    estado = models.CharField(max_length=50, default='pendiente')  # 'pendiente', 'aprobada', 'rechazada'
    id_tipo_licencia = models.ForeignKey(TipoLicencia, models.DO_NOTHING, db_column='id_tipo_licencia')
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente', related_name='licencias')
    
    # Campos de gestión y aprobación
    observaciones = models.TextField(blank=True, null=True)
    justificacion = models.TextField(blank=True, null=True)
    
    # Campos de aprobación
    aprobada_por = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='aprobada_por', blank=True, null=True, related_name='licencias_aprobadas')
    fecha_aprobacion = models.DateField(blank=True, null=True)
    observaciones_aprobacion = models.TextField(blank=True, null=True)
    
    # Campos de rechazo
    rechazada_por = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='rechazada_por', blank=True, null=True, related_name='licencias_rechazadas')
    fecha_rechazo = models.DateField(blank=True, null=True)
    motivo_rechazo = models.TextField(blank=True, null=True)
    
    # Campos de auditoría
    solicitada_por = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='solicitada_por', blank=True, null=True, related_name='licencias_solicitadas')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'licencia'
        ordering = ['-creado_en']
        
    def __str__(self):
        return f"Licencia {self.id_tipo_licencia} - {self.id_agente} ({self.estado})"
    
    @property
    def dias_licencia(self):
        """Calcula la cantidad de días de la licencia"""
        if self.fecha_desde and self.fecha_hasta:
            return (self.fecha_hasta - self.fecha_desde).days + 1
        return 0


class Asistencia(models.Model):
    id_asistencia = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    hora_entrada = models.TimeField(blank=True, null=True)
    hora_salida = models.TimeField(blank=True, null=True)
    marcacion_entrada_automatica = models.BooleanField(default=False)
    marcacion_salida_automatica = models.BooleanField(default=False)
    es_correccion = models.BooleanField(default=False)
    corregido_por = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='corregido_por', blank=True, null=True, related_name='asistencias_corregidas')
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente', related_name='asistencias')
    id_area = models.ForeignKey('personas.Area', models.DO_NOTHING, db_column='id_area', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'asistencia'
        unique_together = (('id_agente', 'fecha'),)
        ordering = ['-fecha', '-hora_entrada']
        
    def __str__(self):
        return f"Asistencia {self.fecha} - {self.id_agente}"
    
    @property
    def estado(self):
        """Retorna el estado de la asistencia"""
        if self.hora_entrada and self.hora_salida:
            return 'completa'
        elif self.hora_entrada and not self.hora_salida:
            return 'sin_salida'
        else:
            return 'sin_entrada'


class IntentoMarcacionFraudulenta(models.Model):
    id_intento = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    dni_ingresado = models.CharField(max_length=20)
    id_agente_sesion = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente_sesion', related_name='intentos_fraudulentos_realizados')
    id_agente_dni = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente_dni', blank=True, null=True, related_name='intentos_fraudulentos_recibidos')
    tipo_intento = models.CharField(max_length=50)  # 'entrada', 'salida'
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'intento_marcacion_fraudulenta'
        ordering = ['-fecha', '-hora']
        
    def __str__(self):
        return f"Intento fraudulento {self.fecha} - Agente {self.id_agente_sesion} usó DNI {self.dni_ingresado}"
