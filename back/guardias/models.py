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
    """Gestión de feriados con soporte para múltiples días y múltiples feriados por fecha"""
    
    id_feriado = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    es_nacional = models.BooleanField(default=False)
    es_provincial = models.BooleanField(default=False)
    es_local = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'feriado'
        ordering = ['fecha_inicio', 'fecha_fin', 'nombre']
        
    def clean(self):
        """Validación de fechas"""
        from django.core.exceptions import ValidationError
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError('La fecha fin debe ser mayor o igual a la fecha inicio')
    
    def __str__(self):
        if self.es_multiples_dias:
            return f"{self.nombre} ({self.fecha_inicio} → {self.fecha_fin})"
        return f"{self.nombre} ({self.fecha_inicio})"
    
    @property
    def es_multiples_dias(self):
        """True si el feriado abarca más de un día"""
        return self.fecha_inicio != self.fecha_fin
    
    @property
    def duracion_dias(self):
        """Cantidad de días que dura el feriado"""
        return (self.fecha_fin - self.fecha_inicio).days + 1
    
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
    
    def incluye_fecha(self, fecha):
        """Verifica si una fecha específica está dentro del rango del feriado"""
        return self.fecha_inicio <= fecha <= self.fecha_fin
    
    @classmethod
    def feriados_en_fecha(cls, fecha):
        """Obtiene todos los feriados que incluyen una fecha específica"""
        return cls.objects.filter(
            fecha_inicio__lte=fecha,
            fecha_fin__gte=fecha,
            activo=True
        )
    
    @classmethod
    def feriados_en_rango(cls, fecha_inicio, fecha_fin):
        """Obtiene feriados que intersectan con un rango de fechas"""
        return cls.objects.filter(
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio,
            activo=True
        )
    
    @classmethod
    def es_feriado(cls, fecha):
        """Verifica si una fecha es feriado (compatibilidad con código existente)"""
        return cls.feriados_en_fecha(fecha).exists()
    
    def get_fechas_incluidas(self):
        """Retorna lista de todas las fechas incluidas en este feriado"""
        from datetime import date, timedelta
        fechas = []
        fecha_actual = self.fecha_inicio
        while fecha_actual <= self.fecha_fin:
            fechas.append(fecha_actual)
            fecha_actual += timedelta(days=1)
        return fechas


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


    # Campos para asociar guardias a los cronogramas
    anio = models.IntegerField(blank=True, null=True)
    mes = models.IntegerField(blank=True, null=True)
    fecha_desde = models.DateField(blank=True, null=True)
    fecha_hasta = models.DateField(blank=True, null=True)
    
    # Campos de aprobación jerárquica
    creado_por_rol = models.CharField(max_length=50, blank=True, null=True)  # jefatura, director, administrador
    creado_por_id = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='creado_por_id', blank=True, null=True, related_name='cronogramas_creados')
    aprobado_por_id = models.ForeignKey('personas.Agente', models.DO_NOTHING, db_column='aprobado_por_id', blank=True, null=True, related_name='cronogramas_aprobados')

    class Meta:
        managed = False
        db_table = 'cronograma'
        
    def __str__(self):
        return f"Cronograma {self.tipo} - {self.fecha_aprobacion}"
    
    @property
    def requiere_aprobacion(self):
        """Verifica si el cronograma requiere aprobación según el rol del creador"""
        if not self.creado_por_rol:
            return True  # Por defecto, requiere aprobación
        return self.creado_por_rol.lower() in ['jefatura', 'director']
    
    @property
    def puede_aprobar_rol(self):
        """Retorna qué roles pueden aprobar este cronograma"""
        if not self.creado_por_rol:
            return ['administrador']
        
        rol_lower = self.creado_por_rol.lower()
        if rol_lower == 'jefatura':
            return ['director', 'administrador']
        elif rol_lower == 'director':
            return ['administrador']
        elif rol_lower == 'administrador':
            return []  # Ya está auto-aprobado
        return ['administrador']


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
    
    @property
    def es_multiples_dias(self):
        """True si la guardia se extiende a múltiples días"""
        return self.hora_inicio > self.hora_fin
    
    @property
    def fecha_fin_real(self):
        """Retorna la fecha de fin real de la guardia"""
        from datetime import timedelta
        if self.es_multiples_dias:
            return self.fecha + timedelta(days=1)
        return self.fecha
    
    @property
    def duracion_dias(self):
        """Cantidad de días que dura la guardia"""
        if self.es_multiples_dias:
            return 2  # Por ahora solo soportamos guardias de 2 días max
        return 1
    
    def incluye_fecha(self, fecha):
        """Verifica si una fecha específica está dentro del rango de la guardia"""
        if self.es_multiples_dias:
            return fecha in [self.fecha, self.fecha_fin_real]
        return fecha == self.fecha
    
    def get_fechas_incluidas(self):
        """Retorna lista de todas las fechas incluidas en esta guardia"""
        if self.es_multiples_dias:
            return [self.fecha, self.fecha_fin_real]
        return [self.fecha]
    
    @classmethod
    def guardias_en_fecha(cls, fecha):
        """Obtiene todas las guardias que incluyen una fecha específica"""
        from datetime import timedelta
        # Guardias que inician en esa fecha
        guardias_inicio = cls.objects.filter(fecha=fecha)
        # Guardias que inician el día anterior y se extienden (hora_inicio > hora_fin)
        fecha_anterior = fecha - timedelta(days=1)
        guardias_extension = cls.objects.filter(
            fecha=fecha_anterior,
            hora_inicio__gt=models.F('hora_fin')
        )
        return guardias_inicio.union(guardias_extension)


class NotaGuardia(models.Model):
    """Notas personales de agentes sobre sus guardias"""
    id_nota = models.BigAutoField(primary_key=True)
    id_guardia = models.ForeignKey(Guardia, models.CASCADE, db_column='id_guardia', related_name='notas')
    id_agente = models.ForeignKey('personas.Agente', models.CASCADE, db_column='id_agente')
    nota = models.TextField(blank=True, null=True)
    fecha_nota = models.DateTimeField(auto_now_add=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'nota_guardia'
        unique_together = (('id_guardia', 'id_agente'),)
        
    def __str__(self):
        return f"Nota {self.id_agente} - Guardia {self.id_guardia}"


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


class HoraCompensacion(models.Model):
    """Registro de horas de compensación por emergencias que exceden el límite reglamentario"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('pagada', 'Pagada/Compensada'),
    ]
    
    TIPO_COMPENSACION_CHOICES = [
        ('pago', 'Pago Adicional'),
        ('franco', 'Franco Compensatorio'),
        ('plus', 'Plus Adicional'),
    ]
    
    MOTIVO_CHOICES = [
        ('siniestro', 'Siniestro/Accidente'),
        ('emergencia', 'Emergencia Operativa'),
        ('operativo', 'Operativo Especial'),
        ('refuerzo', 'Refuerzo de Seguridad'),
        ('otro', 'Otro Motivo'),
    ]
    
    id_hora_compensacion = models.BigAutoField(primary_key=True)
    
    # Relaciones principales
    id_agente = models.ForeignKey('personas.Agente', models.CASCADE, db_column='id_agente', related_name='horas_compensacion')
    id_guardia = models.ForeignKey(Guardia, models.CASCADE, db_column='id_guardia', related_name='horas_compensacion', blank=True, null=True)
    id_cronograma = models.ForeignKey(Cronograma, models.CASCADE, db_column='id_cronograma', related_name='horas_compensacion')
    
    # Información de la compensación
    fecha_servicio = models.DateField(help_text="Fecha en que se prestó el servicio")
    hora_inicio_programada = models.TimeField(help_text="Hora de inicio programada de la guardia")
    hora_fin_programada = models.TimeField(help_text="Hora de fin programada de la guardia") 
    hora_fin_real = models.TimeField(help_text="Hora real de finalización del servicio")
    
    horas_programadas = models.DecimalField(max_digits=4, decimal_places=2, help_text="Horas programadas originalmente")
    horas_efectivas = models.DecimalField(max_digits=4, decimal_places=2, help_text="Horas realmente trabajadas")
    horas_extra = models.DecimalField(max_digits=4, decimal_places=2, help_text="Horas extra trabajadas")
    
    # Motivo y justificación
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES, default='emergencia')
    descripcion_motivo = models.TextField(help_text="Descripción detallada del motivo de la extensión")
    numero_acta = models.CharField(max_length=50, blank=True, null=True, help_text="Número de acta o expediente relacionado")
    
    # Estado y aprobación
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    tipo_compensacion = models.CharField(max_length=20, choices=TIPO_COMPENSACION_CHOICES, default='plus')
    
    # Información de aprobación
    solicitado_por = models.ForeignKey('personas.Agente', models.CASCADE, db_column='solicitado_por', related_name='compensaciones_solicitadas')
    aprobado_por = models.ForeignKey('personas.Agente', models.CASCADE, db_column='aprobado_por', related_name='compensaciones_aprobadas', blank=True, null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    observaciones_aprobacion = models.TextField(blank=True, null=True)
    
    # Cálculos automáticos
    valor_hora_extra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor por hora extra calculado")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Monto total de compensación")
    
    # Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'hora_compensacion'
        unique_together = (('id_agente', 'fecha_servicio', 'id_cronograma'),)
        ordering = ['-fecha_servicio', '-creado_en']
        
    def __str__(self):
        return f"Compensación {self.id_agente} - {self.fecha_servicio} ({self.horas_extra}h extra)"
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar que las horas extra sean positivas
        if self.horas_extra <= 0:
            raise ValidationError("Las horas extra deben ser mayor a 0")
        
        # Validar que la hora fin real sea posterior a la programada
        if self.hora_fin_real <= self.hora_fin_programada:
            raise ValidationError("La hora fin real debe ser posterior a la programada")
        
        # Validar que no se exceda un límite razonable (ej: 8 horas extra máximo)
        if self.horas_extra > 8:
            raise ValidationError("No se pueden registrar más de 8 horas extra por servicio")
    
    def save(self, *args, **kwargs):
        """Cálculos automáticos antes de guardar"""
        from datetime import datetime, time
        
        if self.hora_inicio_programada and self.hora_fin_programada:
            # Asegurar que trabajamos con objetos time
            inicio = self.hora_inicio_programada
            if isinstance(inicio, datetime):
                inicio = inicio.time()
            
            fin = self.hora_fin_programada
            if isinstance(fin, datetime):
                fin = fin.time()
            
            # Calcular horas programadas
            delta = (fin.hour * 60 + fin.minute) - (inicio.hour * 60 + inicio.minute)
            self.horas_programadas = Decimal(str(delta / 60))
        
        if self.hora_inicio_programada and self.hora_fin_real:
            # Asegurar que trabajamos con objetos time
            inicio = self.hora_inicio_programada
            if isinstance(inicio, datetime):
                inicio = inicio.time()
                
            fin = self.hora_fin_real
            if isinstance(fin, datetime):
                fin = fin.time()
            
            # Calcular horas efectivas
            delta = (fin.hour * 60 + fin.minute) - (inicio.hour * 60 + inicio.minute)
            if delta < 0:  # Cruzó medianoche
                delta += 24 * 60
            self.horas_efectivas = Decimal(str(delta / 60))
            
            # Calcular horas extra si tenemos horas programadas
            if self.horas_programadas:
                self.horas_extra = self.horas_efectivas - self.horas_programadas
        
        super().save(*args, **kwargs)
    
    @property
    def puede_aprobar(self):
        """Verifica si la compensación puede ser aprobada"""
        return self.estado == 'pendiente'
    
    @property
    def esta_vencida(self):
        """Verifica si la solicitud está vencida (más de 30 días)"""
        from datetime import timedelta
        
        # Manejar fechas con y sin timezone
        fecha_solicitud = self.fecha_solicitud
        if timezone.is_aware(fecha_solicitud):
            fecha_actual = timezone.now()
        else:
            # Si la fecha_solicitud no tiene timezone, usar datetime naive
            from datetime import datetime
            fecha_actual = datetime.now()
            
        return (fecha_actual - fecha_solicitud).days > 30
    
    def aprobar(self, aprobado_por_agente, observaciones=None):
        """Aprueba la compensación"""
        if not self.puede_aprobar:
            raise ValueError("Esta compensación no puede ser aprobada")
        
        self.estado = 'aprobada'
        self.aprobado_por = aprobado_por_agente
        self.fecha_aprobacion = timezone.now()
        self.observaciones_aprobacion = observaciones
        self.save()
    
    def rechazar(self, rechazado_por_agente, observaciones):
        """Rechaza la compensación"""
        if not self.puede_aprobar:
            raise ValueError("Esta compensación no puede ser rechazada")
        
        self.estado = 'rechazada'
        self.aprobado_por = rechazado_por_agente
        self.fecha_aprobacion = timezone.now()
        self.observaciones_aprobacion = observaciones
        self.save()
    
    @classmethod
    def crear_desde_guardia_extendida(cls, guardia, hora_fin_real, motivo, descripcion, solicitado_por):
        """Crea automáticamente una compensación desde una guardia extendida"""
        compensacion = cls(
            id_agente=guardia.id_agente,
            id_guardia=guardia,
            id_cronograma=guardia.id_cronograma,
            fecha_servicio=guardia.fecha,
            hora_inicio_programada=guardia.hora_inicio,
            hora_fin_programada=guardia.hora_fin,
            hora_fin_real=hora_fin_real,
            motivo=motivo,
            descripcion_motivo=descripcion,
            solicitado_por=solicitado_por,
        )
        compensacion.save()
        return compensacion
    
    @classmethod
    def resumen_mensual_agente(cls, agente, mes, anio):
        """Resumen de compensaciones del mes para un agente"""
        compensaciones = cls.objects.filter(
            id_agente=agente,
            fecha_servicio__month=mes,
            fecha_servicio__year=anio,
            estado='aprobada'
        )
        
        return {
            'total_horas_extra': sum(c.horas_extra for c in compensaciones),
            'total_compensaciones': compensaciones.count(),
            'monto_total': sum(c.monto_total or Decimal('0') for c in compensaciones),
            'por_motivo': {}
        }
