"""
Modelos para el sistema de incidencias relacionadas con guardias.
Sistema de reclamos para diferencias en registro de guardias.
"""

from django.db import models
from django.utils import timezone
import json


class Incidencia(models.Model):
    """
    Modelo para incidencias/reclamos relacionados con guardias.
    Permite a los agentes reportar diferencias entre guardias realizadas
    y guardias registradas en el sistema.
    """
    
    # Choices para estados
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('en_proceso', 'En Proceso'), 
        ('pendiente_informacion', 'Información Pendiente'),
        ('resuelta', 'Resuelta'),
        ('cerrada', 'Cerrada'),
    ]
    
    # Choices para prioridad
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    # Identificación
    numero = models.CharField(max_length=20, unique=True, editable=False)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Estado y prioridad
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='abierta')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    
    # Relaciones con personas
    creado_por = models.ForeignKey(
        'personas.Agente', 
        on_delete=models.CASCADE, 
        related_name='incidencias_creadas',
        db_column='creado_por'  # Nombre exacto en BD
    )
    asignado_a = models.ForeignKey(
        'personas.Agente', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='incidencias_asignadas',
        db_column='asignado_a'  # Nombre exacto en BD
    )
    
    # Área involucrada (para filtros de jefatura)
    area_involucrada = models.ForeignKey(
        'personas.Area',
        on_delete=models.CASCADE,
        related_name='incidencias',
        db_column='area_involucrada'  # Nombre exacto en BD
    )
    
    # Fechas importantes
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    # Resolución
    resolucion = models.TextField(blank=True, null=True)
    
    # Seguimiento (JSON para comentarios con timestamp y autor)
    comentarios_seguimiento = models.JSONField(default=list, blank=True)
    
    class Meta:
        managed = False  # Database First - tabla gestionada por SQL scripts
        db_table = 'incidencia'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['creado_por']),
            models.Index(fields=['asignado_a']),
            models.Index(fields=['area_involucrada']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Generar número único: INC-YYYY-###
            year = timezone.now().year
            count = Incidencia.objects.filter(
                numero__startswith=f'INC-{year}-'
            ).count() + 1
            self.numero = f'INC-{year}-{count:03d}'
        
        # Actualizar fecha de asignación si se asigna por primera vez
        if self.asignado_a and not self.fecha_asignacion:
            self.fecha_asignacion = timezone.now()
        
        # Actualizar fecha de resolución si se marca como resuelta o cerrada
        if self.estado in ['resuelta', 'cerrada'] and not self.fecha_resolucion:
            self.fecha_resolucion = timezone.now()
        
        super().save(*args, **kwargs)
    
    def agregar_comentario(self, autor, comentario):
        """Agregar un comentario de seguimiento"""
        nuevo_comentario = {
            'autor': f"{autor.nombre} {autor.apellido}",
            'autor_id': autor.id_agente,
            'comentario': comentario,
            'fecha': timezone.now().isoformat()
        }
        self.comentarios_seguimiento.append(nuevo_comentario)
        self.save()
    
    def resolver_incidencia(self, resolucion, autor=None):
        """Resolver la incidencia"""
        self.fecha_resolucion = timezone.now()
        self.resolucion = resolucion
        
        if autor:
            comentario = f"Incidencia resuelta: {resolucion}"
            self.agregar_comentario(autor, comentario)
        
        self.save()
    
    def puede_ser_editada(self):
        """Determina si la incidencia puede ser editada"""
        return self.estado not in ['resuelta', 'cerrada']
    
    def puede_cambiar_estado(self, usuario):
        """Determina si un usuario puede cambiar el estado de la incidencia"""
        # Solo el asignado o un administrador pueden cambiar estado
        if self.asignado_a_id == usuario.id_agente:
            return True
            
        # Verificar si es administrador, director o jefatura
        roles = [ar.id_rol.nombre for ar in usuario.agenterol_set.all()]
        return any(rol in ['Administrador', 'Director', 'Jefatura', 'Jefe de Área'] for rol in roles)
    
    def cambiar_estado(self, nuevo_estado, usuario, comentario=None):
        """Cambiar el estado de la incidencia con registro de seguimiento"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        
        # Agregar comentario de cambio de estado
        mensaje_comentario = f"Estado cambiado de '{dict(self.ESTADO_CHOICES)[estado_anterior]}' a '{dict(self.ESTADO_CHOICES)[nuevo_estado]}'"
        if comentario:
            mensaje_comentario += f". Comentario: {comentario}"
        
        self.agregar_comentario(usuario, mensaje_comentario)
        self.save()
        
        return estado_anterior
    
    def puede_ser_vista_por(self, agente):
        """Determina si un agente puede ver esta incidencia"""
        # El creador siempre puede ver
        if self.creado_por_id == agente.id_agente:
            return True
        
        # El asignado puede ver
        if self.asignado_a_id == agente.id_agente:
            return True
        
        # Verificar roles del agente
        roles = [ar.id_rol.nombre for ar in agente.agenterol_set.all()]
        
        # Administrador ve todas
        if 'Administrador' in roles:
            return True
        
        # Jefatura ve las de su área
        if any(rol in ['Jefatura', 'Jefe de Área'] for rol in roles):
            return self.area_involucrada_id == agente.id_area
        
        return False
    
    @property
    def tiempo_resolucion(self):
        """Calcula el tiempo de resolución en días"""
        if self.fecha_resolucion:
            return (self.fecha_resolucion - self.fecha_creacion).days
        return None
    
    @property
    def esta_vencida(self):
        """Determina si la incidencia está vencida (más de 7 días sin resolver)"""
        if self.fecha_resolucion:
            return False
        
        dias_transcurridos = (timezone.now() - self.fecha_creacion).days
        return dias_transcurridos > 7
    
    def __str__(self):
        return f"{self.numero} - {self.titulo}"