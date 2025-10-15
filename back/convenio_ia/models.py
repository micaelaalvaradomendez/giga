from django.db import models
from django.utils.translation import gettext_lazy as _
from personas.models import Agente
import uuid


# ====== ENUMS DE LA APP CONVENIO_IA ======

class EstadoConvenio(models.TextChoices):
    VIGENTE = 'VIGENTE', _('Vigente')
    OBSOLETO = 'OBSOLETO', _('Obsoleto')


class MetodoIndice(models.TextChoices):
    BM25 = 'BM25', _('BM25')
    EMBEDDINGS = 'EMBEDDINGS', _('Embeddings')


# ====== MODELOS DE LA APP CONVENIO_IA ======

class Convenio(models.Model):
    """
    Modelo para representar los convenios colectivos de trabajo
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=50)
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField(blank=True, null=True)
    archivo_ruta = models.FileField(upload_to='convenios/')
    hash = models.CharField(max_length=64)  # SHA-256 hash
    estado = models.CharField(max_length=20, choices=EstadoConvenio.choices, default=EstadoConvenio.VIGENTE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'convenios'
        verbose_name = 'Convenio'
        verbose_name_plural = 'Convenios'

    def __str__(self):
        return f"Convenio v{self.version} ({self.vigencia_desde})"

    def actualizar_version(self, archivo):
        """Actualiza la versión del convenio"""
        pass

    def vigente_en(self, fecha):
        """Verifica si el convenio está vigente en una fecha"""
        pass


class IndiceConvenio(models.Model):
    """
    Modelo para representar los índices de búsqueda de convenios
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    convenio = models.OneToOneField(Convenio, on_delete=models.CASCADE, related_name='indice')
    metodo = models.CharField(max_length=20, choices=MetodoIndice.choices)
    hash_indice = models.CharField(max_length=64)
    construido_en = models.DateTimeField(auto_now_add=True)
    version_motor = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'indices_convenio'
        verbose_name = 'Índice de Convenio'
        verbose_name_plural = 'Índices de Convenio'

    def __str__(self):
        return f"Índice {self.convenio.version} - {self.metodo}"

    def construir(self, convenio, metodo):
        """Construye el índice para un convenio"""
        pass

    def buscar(self, pregunta):
        """Busca en el índice usando una pregunta"""
        pass


class ConsultaConvenio(models.Model):
    """
    Modelo para representar las consultas realizadas sobre convenios
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='consultas_convenio')
    pregunta = models.TextField()
    respuesta = models.TextField(blank=True, null=True)
    citas = models.JSONField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultas_convenio'
        verbose_name = 'Consulta de Convenio'
        verbose_name_plural = 'Consultas de Convenio'

    def __str__(self):
        return f"Consulta de {self.usuario.nombre_completo()} - {self.creado_en}"

    def responder(self, indice, pregunta):
        """Responde una pregunta usando el índice"""
        pass

    def registrar_auditoria(self):
        """Registra la consulta en auditoría"""
        pass


# ====== CLASES AUXILIARES ======

class ResultadoBusqueda(models.Model):
    """
    Modelo auxiliar para representar resultados de búsqueda
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resultados = models.JSONField()
    relevancia = models.DecimalField(max_digits=5, decimal_places=4)
    tiempo = models.DurationField()
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resultados_busqueda'
        verbose_name = 'Resultado de Búsqueda'
        verbose_name_plural = 'Resultados de Búsqueda'

    def obtener_primeros(self, n):
        """Obtiene los primeros n resultados"""
        pass


class RespuestaConCitas(models.Model):
    """
    Modelo auxiliar para representar respuestas con citas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respuesta = models.TextField()
    citas = models.JSONField()
    confianza = models.DecimalField(max_digits=5, decimal_places=4)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuestas_con_citas'
        verbose_name = 'Respuesta con Citas'
        verbose_name_plural = 'Respuestas con Citas'

    def formatear(self):
        """Formatea la respuesta con citas"""
        pass


class Archivo(models.Model):
    """
    Modelo auxiliar para manejar archivos del sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    contenido = models.BinaryField()
    tipo = models.CharField(max_length=100)
    tamaño = models.BigIntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'archivos'
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'

    def __str__(self):
        return self.nombre

    def guardar(self, ruta):
        """Guarda el archivo en una ruta específica"""
        pass

    def leer(self):
        """Lee el contenido del archivo"""
        pass
