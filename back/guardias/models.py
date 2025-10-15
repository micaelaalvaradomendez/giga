from django.db import models
from django.utils.translation import gettext_lazy as _
from personas.models import Agente, Area
from datetime import date
import uuid


# ====== ENUMS DE LA APP GUARDIAS ======

class EstadoCronograma(models.TextChoices):
    BORRADOR = 'BORRADOR', _('Borrador')
    PUBLICADO = 'PUBLICADO', _('Publicado')
    CERRADO = 'CERRADO', _('Cerrado')


class TipoGuardia(models.TextChoices):
    OPERATIVA = 'OPERATIVA', _('Operativa')
    ADMINISTRATIVA = 'ADMINISTRATIVA', _('Administrativa')


class AplicaA(models.TextChoices):
    OPERATIVA = 'OPERATIVA', _('Operativa')
    ADMINISTRATIVA = 'ADMINISTRATIVA', _('Administrativa')
    AMBAS = 'AMBAS', _('Ambas')


# ====== MODELOS DE LA APP GUARDIAS ======

class CronogramaGuardias(models.Model):
    """
    Modelo para representar los cronogramas de guardias
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='cronogramas')
    periodo = models.CharField(max_length=7)  # Format: YYYY-MM
    estado = models.CharField(max_length=20, choices=EstadoCronograma.choices, default=EstadoCronograma.BORRADOR)
    publicado_en = models.DateTimeField(blank=True, null=True)
    publicado_por = models.ForeignKey(Agente, on_delete=models.SET_NULL, null=True, blank=True, related_name='cronogramas_publicados')
    
    class Meta:
        db_table = 'cronogramas_guardias'
        verbose_name = 'Cronograma de Guardias'
        verbose_name_plural = 'Cronogramas de Guardias'
        unique_together = ['area', 'periodo']

    def __str__(self):
        return f"{self.area.nombre} - {self.periodo}"

    def publicar(self):
        """Publica el cronograma"""
        pass

    def calcular_horas_total(self):
        """Calcula el total de horas del cronograma"""
        pass

    def validar_cobertura(self):
        """Valida la cobertura del cronograma"""
        pass


class Guardia(models.Model):
    """
    Modelo para representar las guardias individuales
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(CronogramaGuardias, on_delete=models.CASCADE, related_name='guardias')
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='guardias')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=20, choices=TipoGuardia.choices)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'guardias'
        verbose_name = 'Guardia'
        verbose_name_plural = 'Guardias'
        unique_together = ['cronograma', 'agente', 'fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.agente.legajo} - {self.fecha} - {self.tipo}"

    def duracion_en_horas(self):
        """Calcula la duración de la guardia en horas"""
        pass

    def superpone_con_otra_guardia(self, otra):
        """Verifica si se superpone con otra guardia"""
        pass


class HorasGuardias(models.Model):
    """
    Modelo para representar el resumen de horas de guardias por agente y período
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='horas_guardias')
    periodo = models.CharField(max_length=7)  # Format: YYYY-MM
    horas_operativas = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    horas_administrativas = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    calculado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'horas_guardias'
        verbose_name = 'Horas de Guardias'
        verbose_name_plural = 'Horas de Guardias'
        unique_together = ['agente', 'periodo']

    def __str__(self):
        return f"{self.agente.legajo} - {self.periodo}"

    def total_horas(self):
        """Calcula el total de horas"""
        pass

    def recalcular(self):
        """Recalcula las horas del período"""
        pass


class Feriado(models.Model):
    """
    Modelo para representar los feriados
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=200)
    nacional = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'feriados'
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"

    @classmethod
    def es_feriado_en(cls, fecha):
        """Verifica si una fecha es feriado"""
        pass


class ReglaPlus(models.Model):
    """
    Modelo para representar las reglas para asignación de plus
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    umbral_horas_operativa = models.DecimalField(max_digits=8, decimal_places=2)
    umbral_horas_administrativa = models.DecimalField(max_digits=8, decimal_places=2)
    aplica_a = models.CharField(max_length=20, choices=AplicaA.choices)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    prioridad = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'reglas_plus'
        verbose_name = 'Regla Plus'
        verbose_name_plural = 'Reglas Plus'

    def __str__(self):
        return self.nombre

    def evaluar(self, agente, horas, area):
        """Evalúa la regla para un agente y sus horas"""
        pass

    def es_vigente(self, en_fecha=None):
        """Verifica si la regla está vigente en una fecha"""
        pass


class AsignacionPlus(models.Model):
    """
    Modelo para representar las asignaciones de plus calculadas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='asignaciones_plus')
    periodo = models.CharField(max_length=7)  # Format: YYYY-MM
    regla_plus = models.ForeignKey(ReglaPlus, on_delete=models.CASCADE, related_name='asignaciones')
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    horas_consideradas = models.DecimalField(max_digits=8, decimal_places=2)
    motivo = models.TextField()
    calculado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'asignaciones_plus'
        verbose_name = 'Asignación Plus'
        verbose_name_plural = 'Asignaciones Plus'
        unique_together = ['agente', 'periodo', 'regla_plus']

    def __str__(self):
        return f"{self.agente.legajo} - {self.periodo} - {self.porcentaje}%"

    def generar_comprobante(self):
        """Genera un comprobante de la asignación"""
        pass

    def es_consistente_con(self, horas):
        """Verifica si es consistente con las horas calculadas"""
        pass
