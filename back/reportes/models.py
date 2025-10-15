from django.db import models
from django.utils.translation import gettext_lazy as _
from personas.models import Agente
from guardias.models import CronogramaGuardias
import uuid


# ====== ENUMS DE LA APP REPORTES ======

class TipoReporte(models.TextChoices):
    INDIVIDUAL = 'INDIVIDUAL', _('Individual')
    AREA = 'AREA', _('Área')
    DIRECCION = 'DIRECCION', _('Dirección')
    CONSOLIDADO = 'CONSOLIDADO', _('Consolidado')


class FormatoReporte(models.TextChoices):
    PDF = 'PDF', _('PDF')
    XLSX = 'XLSX', _('Excel')


class EstadoReporte(models.TextChoices):
    LISTO = 'LISTO', _('Listo')
    ERROR = 'ERROR', _('Error')


class EstadoLote(models.TextChoices):
    PENDIENTE = 'PENDIENTE', _('Pendiente')
    PARCIAL = 'PARCIAL', _('Parcial')
    COMPLETO = 'COMPLETO', _('Completo')


class MedioNotificacion(models.TextChoices):
    EMAIL = 'EMAIL', _('Email')


class OrigenNotificacion(models.TextChoices):
    SISTEMA = 'SISTEMA', _('Sistema')
    USUARIO = 'USUARIO', _('Usuario')


class EstadoEnvio(models.TextChoices):
    PENDIENTE = 'PENDIENTE', _('Pendiente')
    ENVIADO = 'ENVIADO', _('Enviado')
    ERROR = 'ERROR', _('Error')


# ====== MODELOS DE LA APP REPORTES ======

class Reporte(models.Model):
    """
    Modelo para representar los reportes del sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TipoReporte.choices)
    filtros = models.JSONField()
    formato = models.CharField(max_length=10, choices=FormatoReporte.choices)
    generado_por = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='reportes_generados')
    generado_en = models.DateTimeField(auto_now_add=True)
    ruta_archivo = models.FileField(upload_to='reportes/', blank=True, null=True)
    estado = models.CharField(max_length=10, choices=EstadoReporte.choices, default=EstadoReporte.LISTO)
    error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'reportes'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'

    def __str__(self):
        return f"{self.tipo} - {self.generado_en}"

    def previsualizar(self, filtros):
        """Genera una previsualización del reporte"""
        pass

    def exportar(self, filtros, formato):
        """Exporta el reporte en el formato especificado"""
        pass

    def validar_filtros(self, filtros):
        """Valida los filtros del reporte"""
        pass


class PlantillaCorreo(models.Model):
    """
    Modelo para representar las plantillas de correo
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, unique=True)
    asunto_tpl = models.CharField(max_length=500)
    cuerpo_tpl = models.TextField()
    variables = models.JSONField()
    version = models.IntegerField(default=1)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'plantillas_correo'
        verbose_name = 'Plantilla de Correo'
        verbose_name_plural = 'Plantillas de Correo'

    def __str__(self):
        return f"{self.nombre} v{self.version}"

    def render(self, variables):
        """Renderiza la plantilla con las variables proporcionadas"""
        pass


class Notificacion(models.Model):
    """
    Modelo para representar las notificaciones del sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    remitente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='notificaciones_enviadas')
    destinatario = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='notificaciones_recibidas')
    asunto = models.CharField(max_length=500)
    cuerpo = models.TextField()
    medio = models.CharField(max_length=10, choices=MedioNotificacion.choices, default=MedioNotificacion.EMAIL)
    origen = models.CharField(max_length=10, choices=OrigenNotificacion.choices)
    estado_envio = models.CharField(max_length=10, choices=EstadoEnvio.choices, default=EstadoEnvio.PENDIENTE)
    intentos = models.IntegerField(default=0)
    ultimo_intento_en = models.DateTimeField(blank=True, null=True)
    error_mensaje = models.TextField(blank=True, null=True)
    plantilla = models.ForeignKey(PlantillaCorreo, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notificaciones'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.remitente.nombre_completo()} -> {self.destinatario.nombre_completo()}: {self.asunto}"

    def redactar(self, remitente, destinatario, asunto, cuerpo, origen):
        """Redacta una nueva notificación"""
        pass

    def enviar(self):
        """Envía la notificación"""
        pass

    def reintentar(self):
        """Reintenta el envío de la notificación"""
        pass

    def marcar_error(self, mensaje):
        """Marca la notificación con error"""
        pass


class EnvioLoteNotificaciones(models.Model):
    """
    Modelo para representar los envíos masivos de notificaciones
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cronograma = models.ForeignKey(CronogramaGuardias, on_delete=models.CASCADE, related_name='envios_notificaciones')
    creado_en = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)
    enviados = models.IntegerField(default=0)
    fallidos = models.IntegerField(default=0)
    estado = models.CharField(max_length=10, choices=EstadoLote.choices, default=EstadoLote.PENDIENTE)
    
    class Meta:
        db_table = 'envios_lote_notificaciones'
        verbose_name = 'Envío Lote Notificaciones'
        verbose_name_plural = 'Envíos Lote Notificaciones'

    def __str__(self):
        return f"Lote {self.cronograma.nombre} - {self.estado}"

    def iniciar_para_publicacion(self, cronograma):
        """Inicia el envío masivo para publicación de cronograma"""
        pass

    def registrar_resultado(self, notificacion, ok):
        """Registra el resultado de una notificación"""
        pass

    def resumen(self):
        """Retorna un resumen del envío"""
        pass


# ====== CLASES AUXILIARES ======

class RenderCorreo(models.Model):
    """
    Modelo auxiliar para representar correos renderizados
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asunto = models.CharField(max_length=500)
    cuerpo = models.TextField()
    variables = models.JSONField()
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'render_correos'
        verbose_name = 'Correo Renderizado'
        verbose_name_plural = 'Correos Renderizados'

    def validar(self):
        """Valida el correo renderizado"""
        pass


class Vista(models.Model):
    """
    Modelo auxiliar para representar vistas de datos
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datos = models.JSONField()
    formato = models.CharField(max_length=50)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vistas'
        verbose_name = 'Vista'
        verbose_name_plural = 'Vistas'

    def renderizar(self):
        """Renderiza la vista"""
        pass
