"""
Modelos Database First para Personas - Sistema GIGA.

ESTRATEGIA: Todos los modelos tienen managed=False
- Django puede hacer CRUD sobre los datos
- Django NO puede modificar estructura de tablas
- Estructura definida en scripts SQL (bd/init-scripts/)
"""

from django.db import models


class Area(models.Model):
    """Áreas de trabajo en Protección Civil."""
    id_area = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=100)
    activo = models.BooleanField(blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'area'
        
    def __str__(self):
        return self.nombre


class Rol(models.Model):
    """Roles/cargos de los agentes."""
    id_rol = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'
        
    def __str__(self):
        return self.nombre


class Agente(models.Model):
    """
    Agentes de Protección Civil - MODELO SIMPLE.
    No hereda de User para evitar conflictos con managed=False.
    """
    id_agente = models.BigAutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=100)
    dni = models.CharField(unique=True, max_length=20)
    legajo = models.CharField(unique=True, max_length=50)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    calle = models.CharField(max_length=150, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)
    horario_entrada = models.TimeField(blank=True, null=True)
    horario_salida = models.TimeField(blank=True, null=True)
    agrupacion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)
    id_area = models.ForeignKey('Area', models.DO_NOTHING, db_column='id_area', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'agente'
        
    @property
    def id(self):
        """Alias para compatibilidad con serializadores"""
        return self.id_agente
    
    @property
    def username(self):
        """Username basado en email"""
        return self.email.split('@')[0] if self.email else f"agente_{self.id_agente}"
    
    @property
    def area(self):
        """Referencia al área"""
        return self.id_area
    
    @property
    def is_active(self):
        """Mapeo para compatibilidad con Django User"""
        return self.activo if self.activo is not None else True
    
    @property
    def direccion(self):
        """Dirección completa concatenada"""
        parts = [self.calle, self.numero, self.ciudad, self.provincia]
        return ', '.join([part for part in parts if part])
    
    @property
    def cuil(self):
        """CUIL generado a partir del DNI (placeholder)"""
        if self.dni:
            return f"27{self.dni}4"  # Formato simplificado
        return None
    
    @property
    def fecha_ingreso(self):
        """Fecha de ingreso desde creado_en"""
        return self.creado_en.date() if self.creado_en else None
    
    @property
    def categoria_revista(self):
        """Categoría por defecto"""
        return "24"  # Valor por defecto
        
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def check_password(self, raw_password):
        """Verificar contraseña (implementar hash según la BD)"""
        # Por ahora comparación simple, mejorar con hash apropiado
        return self.password_hash == raw_password
    
    def set_password(self, raw_password):
        """Establecer contraseña (implementar hash según la BD)"""
        # Por ahora almacenamiento simple, mejorar con hash apropiado
        self.password_hash = raw_password


class AgenteRol(models.Model):
    """Relación entre agentes y roles."""
    id_agente_rol = models.BigAutoField(primary_key=True)
    id_agente = models.ForeignKey(Agente, models.DO_NOTHING, db_column='id_agente')
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')
    asignado_en = models.DateTimeField(blank=True, null=True)
    creado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'agente_rol'
        unique_together = (('id_agente', 'id_rol'),)
    
    @property
    def id(self):
        """Alias para compatibilidad"""
        return self.id_agente_rol
    
    @property
    def agente(self):
        """Referencia al agente"""
        return self.id_agente
    
    @property
    def rol(self):
        """Referencia al rol"""
        return self.id_rol
    
    @property
    def activo(self):
        """Por defecto activo"""
        return True
        
    def __str__(self):
        return f"{self.id_agente} - {self.id_rol}"
