# App: Convenio IA - Modelos de Base de Datos

## Descripción
Esta app implementa un sistema de inteligencia artificial para consultas sobre convenios colectivos de trabajo, utilizando técnicas de búsqueda semántica y procesamiento de lenguaje natural.

## Enums Definidos

### EstadoConvenio
```python
class EstadoConvenio(models.TextChoices):
    VIGENTE = 'VIGENTE', _('Vigente')
    OBSOLETO = 'OBSOLETO', _('Obsoleto')
```

### MetodoIndice
```python
class MetodoIndice(models.TextChoices):
    BM25 = 'BM25', _('BM25')
    EMBEDDINGS = 'EMBEDDINGS', _('Embeddings')
```

## Modelos Definidos

### 1. Convenio
**Tabla:** `convenio_ia_convenio`

```python
class Convenio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=50)
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField(blank=True, null=True)
    archivo_ruta = models.FileField(upload_to='convenios/')
    hash = models.CharField(max_length=64)  # SHA-256 hash
    estado = models.CharField(max_length=20, choices=EstadoConvenio.choices, default=EstadoConvenio.VIGENTE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
```

**Características:**
- Almacena documentos de convenios colectivos de trabajo
- Control de versiones y vigencia temporal
- Hash SHA-256 para integridad del documento
- Estados: VIGENTE/OBSOLETO

**Métodos definidos:**
- `actualizar_version(archivo)`: Actualiza versión del convenio
- `vigente_en(fecha)`: Verifica vigencia en fecha específica

**Ejemplo de uso:**
```python
# Verificar si convenio está vigente
convenio = Convenio.objects.get(version="2024.1")
es_vigente = convenio.vigente_en(date.today())

# Actualizar versión
nuevo_archivo = request.FILES['convenio_pdf']
convenio.actualizar_version(nuevo_archivo)
```

### 2. IndiceConvenio
**Tabla:** `convenio_ia_indiceconvenio`

```python
class IndiceConvenio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    convenio = models.OneToOneField(Convenio, on_delete=models.CASCADE, related_name='indice')
    metodo = models.CharField(max_length=20, choices=MetodoIndice.choices)
    hash_indice = models.CharField(max_length=64)
    construido_en = models.DateTimeField(auto_now_add=True)
    version_motor = models.CharField(max_length=50)
```

**Características:**
- Índices de búsqueda para cada convenio
- Soporte para múltiples métodos: BM25 y Embeddings
- Hash de integridad del índice
- Tracking de versión del motor de IA usado

**Métodos definidos:**
- `construir(convenio, metodo)`: Construye índice para un convenio
- `buscar(pregunta)`: Realiza búsqueda en el índice

**Técnicas de Indexación:**

#### BM25 (Best Matching 25)
- Algoritmo de ranking basado en frecuencia de términos
- Optimizado para búsquedas exactas y por palabras clave
- Rápido y eficiente para consultas específicas

#### Embeddings
- Vectorización semántica del contenido
- Comprende contexto y significado
- Mejor para preguntas complejas y relacionales

### 3. ConsultaConvenio
**Tabla:** `convenio_ia_consultaconvenio`

```python
class ConsultaConvenio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='consultas_convenio')
    pregunta = models.TextField()
    respuesta = models.TextField(blank=True, null=True)
    citas = models.JSONField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Registro de todas las consultas realizadas
- Almacena preguntas, respuestas y citas del convenio
- Citas en formato JSON con referencias específicas
- Auditoría completa de uso del sistema

**Métodos definidos:**
- `responder(indice, pregunta)`: Genera respuesta usando IA
- `registrar_auditoria()`: Registra consulta en auditoría

**Estructura de citas JSON:**
```json
{
  "citas": [
    {
      "texto": "El horario de trabajo será de 8 horas diarias...",
      "pagina": 15,
      "seccion": "CAPÍTULO III - JORNADA DE TRABAJO",
      "articulo": "Artículo 23",
      "relevancia": 0.95
    },
    {
      "texto": "Los trabajadores tendrán derecho a...",
      "pagina": 16,
      "seccion": "CAPÍTULO III - JORNADA DE TRABAJO", 
      "articulo": "Artículo 24",
      "relevancia": 0.87
    }
  ]
}
```

## Modelos Auxiliares

### 4. ResultadoBusqueda
**Tabla:** `convenio_ia_resultadobusqueda`

```python
class ResultadoBusqueda(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resultados = models.JSONField()
    relevancia = models.DecimalField(max_digits=5, decimal_places=4)
    tiempo = models.DurationField()
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Cache de resultados de búsqueda
- Métricas de relevancia y performance
- Optimización de consultas repetidas

### 5. RespuestaConCitas
**Tabla:** `convenio_ia_respuestaconcitas`

```python
class RespuestaConCitas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respuesta = models.TextField()
    citas = models.JSONField()
    confianza = models.DecimalField(max_digits=5, decimal_places=4)
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Respuestas estructuradas con citas
- Score de confianza de la respuesta
- Formato reutilizable

### 6. Archivo
**Tabla:** `convenio_ia_archivo`

```python
class Archivo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    contenido = models.BinaryField()
    tipo = models.CharField(max_length=100)
    tamaño = models.BigIntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)
```

**Características:**
- Gestión de archivos del sistema
- Almacenamiento binario seguro
- Metadatos de archivo

## Flujo de Trabajo del Sistema

### 1. Carga de Convenio
```python
# 1. Subir nuevo convenio
convenio = Convenio.objects.create(
    version="2024.2",
    vigencia_desde=date(2024, 1, 1),
    archivo_ruta=archivo_pdf,
    estado=EstadoConvenio.VIGENTE
)

# 2. Construir índice automáticamente
IndiceConvenio.construir(convenio, MetodoIndice.EMBEDDINGS)
```

### 2. Procesamiento de Consulta
```python
# 1. Recibir pregunta del usuario
pregunta = "¿Cuáles son los días de vacaciones que corresponden?"

# 2. Buscar en índice
indice = IndiceConvenio.objects.get(convenio__estado=EstadoConvenio.VIGENTE)
resultados = indice.buscar(pregunta)

# 3. Generar respuesta con IA
respuesta = generar_respuesta_ia(pregunta, resultados)

# 4. Registrar consulta
consulta = ConsultaConvenio.objects.create(
    usuario=request.user.agente,
    pregunta=pregunta,
    respuesta=respuesta.texto,
    citas=respuesta.citas
)
```

### 3. Actualización de Convenio
```python
# 1. Marcar convenio anterior como obsoleto
convenio_anterior = Convenio.objects.get(version="2024.1")
convenio_anterior.estado = EstadoConvenio.OBSOLETO
convenio_anterior.save()

# 2. Activar nuevo convenio
convenio_nuevo = Convenio.objects.create(
    version="2024.2",
    vigencia_desde=date(2024, 6, 1)
)

# 3. Reconstruir índices
IndiceConvenio.construir(convenio_nuevo, MetodoIndice.BM25)
IndiceConvenio.construir(convenio_nuevo, MetodoIndice.EMBEDDINGS)
```

## Integraciones con IA

### Motores de IA Soportados

#### OpenAI GPT
```python
import openai

def generar_respuesta_openai(pregunta, contexto):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un experto en convenios colectivos de trabajo."},
            {"role": "user", "content": f"Pregunta: {pregunta}\nContexto: {contexto}"}
        ]
    )
    return response.choices[0].message.content
```

#### Ollama (Local)
```python
import requests

def generar_respuesta_ollama(pregunta, contexto):
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama2',
        'prompt': f"Pregunta: {pregunta}\nContexto: {contexto}",
        'stream': False
    })
    return response.json()['response']
```

#### Hugging Face Transformers
```python
from transformers import pipeline

def generar_respuesta_huggingface(pregunta, contexto):
    qa_pipeline = pipeline("question-answering")
    result = qa_pipeline(question=pregunta, context=contexto)
    return result['answer']
```

### Técnicas de Procesamiento

#### Extracción de Texto (PDF)
```python
import PyPDF2
import pdfplumber

def extraer_texto_pdf(archivo_path):
    texto = ""
    with pdfplumber.open(archivo_path) as pdf:
        for page in pdf.pages:
            texto += page.extract_text()
    return texto
```

#### Chunking Inteligente
```python
def dividir_en_chunks(texto, max_tokens=500, overlap=50):
    chunks = []
    palabras = texto.split()
    
    for i in range(0, len(palabras), max_tokens - overlap):
        chunk = ' '.join(palabras[i:i + max_tokens])
        chunks.append(chunk)
    
    return chunks
```

#### Generación de Embeddings
```python
from sentence_transformers import SentenceTransformer

def generar_embeddings(textos):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(textos)
    return embeddings
```

## API Endpoints

### Consultas
```python
# POST /api/convenio-ia/consultar/
{
    "pregunta": "¿Cuántos días de licencia por paternidad corresponden?"
}

# Response
{
    "respuesta": "Según el Artículo 45, corresponden 5 días hábiles por nacimiento de hijo.",
    "citas": [
        {
            "texto": "Por nacimiento de hijo corresponderán 5 días hábiles...",
            "articulo": "Artículo 45",
            "pagina": 23,
            "relevancia": 0.98
        }
    ],
    "confianza": 0.95
}
```

### Historial
```python
# GET /api/convenio-ia/consultas/
[
    {
        "id": "uuid",
        "pregunta": "¿Cuántos días de licencia...?",
        "respuesta": "Según el Artículo 45...",
        "creado_en": "2024-01-15T10:30:00Z"
    }
]
```

### Convenios
```python
# GET /api/convenio-ia/convenios/
[
    {
        "id": "uuid",
        "version": "2024.2",
        "vigencia_desde": "2024-01-01",
        "estado": "VIGENTE",
        "indice_disponible": true
    }
]
```

## Casos de Uso Típicos

### Consultas Frecuentes
- Licencias y permisos
- Horarios de trabajo
- Escalas salariales
- Beneficios y compensaciones
- Procedimientos disciplinarios

### Consultas Complejas
- Cálculos de antigüedad
- Combinación de beneficios
- Casos especiales y excepciones
- Interpretación de cláusulas ambiguas

## Métricas y Analytics

### Performance
- Tiempo de respuesta promedio
- Accuracy de respuestas
- Satisfacción del usuario
- Consultas por día/mes

### Contenido
- Artículos más consultados
- Temas más frecuentes
- Gaps de información
- Sugerencias de mejora

## Relaciones Principales

1. **Convenio ↔ IndiceConvenio**: 1:1 (Cada convenio tiene un índice)
2. **Agente ↔ ConsultaConvenio**: 1:N (Un agente hace múltiples consultas)

## Consideraciones Técnicas

### Seguridad
- Validación de consultas maliciosas
- Rate limiting por usuario
- Auditoría completa de accesos
- Sanitización de respuestas

### Escalabilidad
- Cache de respuestas frecuentes
- Procesamiento asíncrono de índices
- Distribución de carga de IA
- Optimización de embeddings

### Compliance
- Trazabilidad de consultas
- Versionado de convenios
- Backup de datos críticos
- Conformidad legal