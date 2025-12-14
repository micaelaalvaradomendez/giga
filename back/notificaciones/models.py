from django.db import models
from personas.models import Agente

class Notificacion(models.Model):
    TIPO_CHOICES = (
        ('GUARDIA', 'Guardia'),
        ('HORA_EXTRA', 'Hora Extra'),
        ('INCIDENCIA', 'Incidencia'),
        ('ASISTENCIA', 'Asistencia'),
        ('USUARIO', 'Usuario'),
        ('LICENCIA', 'Licencia'),
        ('FERIADO', 'Feriado'),
        ('ORGANIGRAMA', 'Organigrama'),
        ('ROL', 'Rol'),
        ('LOGIN', 'Login'),
        ('CRONOGRAMA', 'Cronograma'),
        ('GENERICO', 'Generico'),
    )

    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='notificaciones', db_column='id_agente')
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='GENERICO')
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notificacion'
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.agente.nombre} {self.agente.apellido} - {self.titulo}"
