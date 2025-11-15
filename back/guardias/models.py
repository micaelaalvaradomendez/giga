from django.db import models
from django.utils import timezone
from decimal import Decimal


class ReglaPlus(models.Model):
    """Reglas para cálculo automático de plus salarial por guardias"""
    id_regla_plus = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    horas_minimas_diarias = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('8.0'))
    horas_minimas_mensuales = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('160.0'))
    porcentaje_plus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.0'))
    aplica_areas_operativas = models.BooleanField(default=True)
    aplica_areas_administrativas = models.BooleanField(default=False)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'reglas_plus'
        
    def __str__(self):
        return f"{self.nombre} - {self.porcentaje_plus}%"
    
    @property
    def esta_vigente(self):
        """Verifica si la regla está vigente en la fecha actual"""
        from datetime import date
        hoy = date.today()
        return (self.vigente_desde <= hoy and 
                (self.vigente_hasta is None or self.vigente_hasta >= hoy) and 
                self.activa)


class ParametrosArea(models.Model):
    """Parámetros de control horario por área"""
    id_parametros_area = models.BigAutoField(primary_key=True)
    id_area = models.ForeignKey('personas.Area', models.DO_NOTHING, db_column='id_area')
    ventana_entrada_inicio = models.TimeField(default='07:30:00')
    ventana_entrada_fin = models.TimeField(default='09:00:00')
    ventana_salida_inicio = models.TimeField(default='16:00:00')
    ventana_salida_fin = models.TimeField(default='18:30:00')
    tolerancia_entrada_min = models.IntegerField(default=15)
    tolerancia_salida_min = models.IntegerField(default=15)
    horas_trabajo_dia = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('8.0'))
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'parametros_area'
        
    def __str__(self):
        return f"Parámetros {self.id_area.nombre} - {self.vigente_desde}"
    
    @property
    def esta_vigente(self):
        """Verifica si los parámetros están vigentes"""
        from datetime import date
        hoy = date.today()
        return (self.vigente_desde <= hoy and 
                (self.vigente_hasta is None or self.vigente_hasta >= hoy) and 
                self.activo)


class Feriado(models.Model):
    """Gestión de feriados que afectan cronogramas"""
    id_feriado = models.BigAutoField(primary_key=True)
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=200)
    es_nacional = models.BooleanField(default=False)
    es_provincial = models.BooleanField(default=False)
    es_local = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'feriado'
        ordering = ['fecha']
        
    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"
    
    @property
    def tipo_feriado(self):
        """Retorna el tipo de feriado"""
        if self.es_nacional:
            return "Nacional"
        elif self.es_provincial:
            return "Provincial"
        elif self.es_local:
            return "Local"
        return "Especial"
    
    @classmethod
    def es_feriado(cls, fecha):
        """Verifica si una fecha es feriado"""
        return cls.objects.filter(fecha=fecha, activo=True).exists()


class Cronograma(models.Model):
    id_cronograma = models.BigAutoField(primary_key=True)
    fecha_aprobacion = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    id_jefe = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_jefe')
    id_director = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_director', related_name='cronogramas_dirigidos')
    id_area = models.ForeignKey('personas.Area', models.DO_NOTHING, db_column='id_area')
    estado = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateField(blank=True, null=True)

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
    """Resumen mensual de guardias por agente - EXTENDIDO con cálculo automático de plus"""
    id_resumen_guardia_mes = models.BigAutoField(primary_key=True)
    id_agente = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='id_agente')
    mes = models.IntegerField()
    anio = models.IntegerField()
    
    # Campos existentes (legacy)
    plus20 = models.BooleanField(blank=True, null=True)
    plus40 = models.BooleanField(blank=True, null=True)
    total_horas_guardia = models.IntegerField(blank=True, null=True)
    
    # Campos nuevos para cálculo automático
    horas_efectivas = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'), blank=True, null=True)
    porcentaje_plus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'), blank=True, null=True)
    monto_calculado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado_plus = models.CharField(max_length=30, default='pendiente', blank=True, null=True)  # pendiente, aprobado, pagado
    fecha_calculo = models.DateTimeField(blank=True, null=True)
    aprobado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resumen_guardia_mes'
        unique_together = (('id_agente', 'mes', 'anio'),)
        
    def __str__(self):
        return f"Resumen {self.mes}/{self.anio} - {self.id_agente} ({self.porcentaje_plus}% plus)"
    
    @property
    def plus_aplicable(self):
        """Verifica si tiene plus aplicable basado en porcentaje calculado"""
        return self.porcentaje_plus and self.porcentaje_plus > 0
    
    @property
    def compatibilidad_legacy(self):
        """Mantiene compatibilidad con campos plus20/plus40 existentes"""
        if self.porcentaje_plus:
            if self.porcentaje_plus >= 40:
                return {'plus20': True, 'plus40': True}
            elif self.porcentaje_plus >= 20:
                return {'plus20': True, 'plus40': False}
        return {'plus20': False, 'plus40': False}
    
    def calcular_plus_automatico(self):
        """Calcula el plus automáticamente usando la función SQL"""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT calcular_plus_agente(%s, %s, %s)",
                [self.id_agente_id, self.mes, self.anio]
            )
            resultado = cursor.fetchone()
            if resultado and resultado[0]:
                self.porcentaje_plus = resultado[0]
                self.fecha_calculo = timezone.now()
                # Actualizar campos legacy para compatibilidad
                compat = self.compatibilidad_legacy
                self.plus20 = compat['plus20']
                self.plus40 = compat['plus40']
                return True
        return False
