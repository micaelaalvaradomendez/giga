from django.db import models
from django.contrib.auth.models import User

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

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='GENERICO')
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"
