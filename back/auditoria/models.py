from django.db import models
from django.utils.translation import gettext_lazy as _
from personas.models import Agente
from guardias.models import ReglaPlus
import uuid


# ====== ENUMS DE LA APP AUDITORIA ======

class PoliticaVentanas(models.TextChoices):
    ESTRICTO = 'ESTRICTO', _('Estricto')
    FLEXIBLE = 'FLEXIBLE', _('Flexible')


class AccionAuditoria(models.TextChoices):
    CREATE = 'CREATE', _('Crear')
    UPDATE = 'UPDATE', _('Actualizar')
    DELETE = 'DELETE', _('Eliminar')
    LOGIN = 'LOGIN', _('Iniciar Sesión')
    RECOVERY = 'RECOVERY', _('Recuperación')
    PUBLICACION = 'PUBLICACION', _('Publicación')


# ====== MODELOS DE LA APP AUDITORIA ======

class ParametrosControlHorario(models.Model):
    """
    Modelo para representar los parámetros de control horario
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ventana_marcacion_ingreso_min = models.IntegerField()
    ventana_marcacion_egreso_min = models.IntegerField()
    tolerancia_ingreso_min = models.IntegerField()
    tolerancia_egreso_min = models.IntegerField()
    politica_ventanas = models.CharField(max_length=20, choices=PoliticaVentanas.choices)
    version = models.IntegerField(default=1)
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parametros_control_horario'
        verbose_name = 'Parámetros Control Horario'
        verbose_name_plural = 'Parámetros Control Horario'

    def __str__(self):
        return f"Versión {self.version} - Vigente desde {self.vigente_desde}"

    def validar_coherencia(self):
        """Valida la coherencia de los parámetros"""
        pass

    def aplicar_desde(self, fecha):
        """Aplica los parámetros desde una fecha específica"""
        pass

    def versionar(self, nueva_cfg):
        """Crea una nueva versión de la configuración"""
        pass

    def restaurar(self, version):
        """Restaura una versión específica"""
        pass

    def reglas_plus(self):
        """Retorna las reglas plus asociadas"""
        pass


class RegistroAuditoria(models.Model):
    """
    Modelo para representar los registros de auditoría del sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entidad = models.CharField(max_length=100)
    entidad_id = models.UUIDField()
    accion = models.CharField(max_length=20, choices=AccionAuditoria.choices)
    usuario = models.ForeignKey(Agente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    datos_previos = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'registros_auditoria'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        indexes = [
            models.Index(fields=['entidad', 'entidad_id']),
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['usuario']),
        ]

    def __str__(self):
        return f"{self.entidad} - {self.accion} - {self.fecha_hora}"

    @classmethod
    def registrar(cls, entidad, entidad_id, accion, usuario_id, datos_previos, datos_nuevos, ip):
        """Registra una acción en la auditoría"""
        pass

    @classmethod
    def buscar(cls, filtros):
        """Busca registros de auditoría según filtros"""
        pass

    def exportar(self, formato):
        """Exporta el registro en el formato especificado"""
        pass
