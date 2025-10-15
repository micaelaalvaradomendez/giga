from django.db import models
from django.utils.translation import gettext_lazy as _
from personas.models import Agente
import uuid


# ====== ENUMS DE LA APP ASISTENCIA ======

class EstadoAsistencia(models.TextChoices):
    PRESENTE = 'PRESENTE', _('Presente')
    AUSENTE = 'AUSENTE', _('Ausente')
    TARDANZA = 'TARDANZA', _('Tardanza')
    SALIDA_TEMPRANA = 'SALIDA_TEMPRANA', _('Salida Temprana')


class TipoMarca(models.TextChoices):
    ENTRADA = 'ENTRADA', _('Entrada')
    SALIDA = 'SALIDA', _('Salida')


class TipoLicencia(models.TextChoices):
    VACACIONES = 'VACACIONES', _('Vacaciones')
    ENFERMEDAD = 'ENFERMEDAD', _('Enfermedad')
    PERSONAL = 'PERSONAL', _('Personal')
    ESTUDIO = 'ESTUDIO', _('Estudio')


class CategoriaNovedad(models.TextChoices):
    MEDICA = 'MEDICA', _('Médica')
    FAMILIAR = 'FAMILIAR', _('Familiar')
    CAPACITACION = 'CAPACITACION', _('Capacitación')


class EstadoSolicitud(models.TextChoices):
    PENDIENTE = 'PENDIENTE', _('Pendiente')
    APROBADA = 'APROBADA', _('Aprobada')
    RECHAZADA = 'RECHAZADA', _('Rechazada')


# ====== MODELOS DE LA APP ASISTENCIA ======

class Asistencia(models.Model):
    """
    Modelo para representar la asistencia diaria de los agentes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    hora_entrada = models.TimeField(blank=True, null=True)
    hora_salida = models.TimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=EstadoAsistencia.choices)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'asistencias'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['agente', 'fecha']

    def __str__(self):
        return f"{self.agente.legajo} - {self.fecha}"

    def calcular_horas_trabajadas(self):
        """Calcula las horas trabajadas en el día"""
        pass

    def es_completa(self):
        """Verifica si la asistencia está completa"""
        pass


class Marca(models.Model):
    """
    Modelo para representar las marcas de entrada y salida
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE, related_name='marcas')
    tipo = models.CharField(max_length=10, choices=TipoMarca.choices)
    hora = models.TimeField()
    dispositivo = models.CharField(max_length=100, blank=True, null=True)
    validada = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'marcas'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return f"{self.asistencia.agente.legajo} - {self.tipo} - {self.hora}"

    def validar(self):
        """Valida la marca"""
        pass

    def es_consistente(self):
        """Verifica si la marca es consistente"""
        pass


class LicenciaONovedad(models.Model):
    """
    Modelo abstracto base para licencias y novedades
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='licencias_novedades')
    desde = models.DateField()
    hasta = models.DateField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE)
    solicitado_en = models.DateTimeField(auto_now_add=True)
    aprobado_por = models.ForeignKey(Agente, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprobaciones')
    aprobado_en = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        abstract = True

    def duracion_en_dias(self):
        """Calcula la duración en días"""
        pass

    def superpone_con_periodo(self, desde, hasta):
        """Verifica si se superpone con otro período"""
        pass

    def aprobar(self, usuario):
        """Aprueba la solicitud"""
        pass

    def rechazar(self, usuario, motivo_rechazo):
        """Rechaza la solicitud"""
        pass


class Licencia(LicenciaONovedad):
    """
    Modelo para representar las licencias de los agentes
    """
    tipo = models.CharField(max_length=20, choices=TipoLicencia.choices)
    remunerada = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'licencias'
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'

    def __str__(self):
        return f"{self.agente.legajo} - {self.tipo} - {self.desde} al {self.hasta}"

    def es_justificada(self):
        """Verifica si la licencia está justificada"""
        pass


class Novedad(LicenciaONovedad):
    """
    Modelo para representar las novedades de los agentes
    """
    categoria = models.CharField(max_length=20, choices=CategoriaNovedad.choices)
    urgente = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'novedades'
        verbose_name = 'Novedad'
        verbose_name_plural = 'Novedades'

    def __str__(self):
        return f"{self.agente.legajo} - {self.categoria} - {self.desde} al {self.hasta}"

    def requiere_aprobacion(self):
        """Verifica si la novedad requiere aprobación"""
        pass


class Adjunto(models.Model):
    """
    Modelo para representar adjuntos de licencias y novedades
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    licencia = models.ForeignKey(Licencia, on_delete=models.CASCADE, related_name='adjuntos', blank=True, null=True)
    novedad = models.ForeignKey(Novedad, on_delete=models.CASCADE, related_name='adjuntos', blank=True, null=True)
    nombre = models.CharField(max_length=255)
    ruta_archivo = models.FileField(upload_to='adjuntos/')
    tipo = models.CharField(max_length=50)
    tamaño = models.BigIntegerField()
    
    class Meta:
        db_table = 'adjuntos'
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'

    def __str__(self):
        return self.nombre

    def validar_formato(self):
        """Valida el formato del archivo"""
        pass
