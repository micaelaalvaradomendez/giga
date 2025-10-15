from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# ====== MODELOS DE LA APP PERSONAS ======

class Area(models.Model):
    """
    Modelo para representar las áreas de la organización
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'areas'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def agentes_activos(self):
        """Retorna los agentes activos de esta área"""
        pass


class Agente(models.Model):
    """
    Modelo para representar a los agentes de la organización
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    legajo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField()
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='agentes')
    
    class Meta:
        db_table = 'agentes'
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'

    def __str__(self):
        return f"{self.legajo} - {self.nombre_completo()}"

    def nombre_completo(self):
        """Retorna el nombre completo del agente"""
        pass

    def puede_marcar(self, fecha):
        """Verifica si el agente puede marcar en una fecha determinada"""
        pass

    def es_activo(self):
        """Verifica si el agente está activo"""
        pass


class Rol(models.Model):
    """
    Modelo para representar los roles del sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)
    permisos = models.JSONField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre

    def tiene_permiso(self, accion):
        """Verifica si el rol tiene un permiso específico"""
        pass


class CuentaAcceso(models.Model):
    """
    Modelo para representar las cuentas de acceso al sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agente = models.OneToOneField(Agente, on_delete=models.CASCADE, related_name='cuenta_acceso')
    usuario = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    activa = models.BooleanField(default=True)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    roles = models.ManyToManyField(Rol, blank=True)
    
    class Meta:
        db_table = 'cuentas_acceso'
        verbose_name = 'Cuenta de Acceso'
        verbose_name_plural = 'Cuentas de Acceso'

    def __str__(self):
        return f"{self.usuario} - {self.agente.nombre_completo()}"

    def autenticar(self, password):
        """Autentica la cuenta con la contraseña proporcionada"""
        pass

    def cambiar_password(self, nueva):
        """Cambia la contraseña de la cuenta"""
        pass
