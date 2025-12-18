Basado en la documentación técnica del informe final y la presentación de módulos, he redactado la sección de **Tecnología e Infraestructura** siguiendo tus indicaciones.

Esta redacción destaca tanto el rigor técnico (stack y flujo) como el valor pedagógico de las decisiones arquitectónicas (el desafío de aprender Docker/Microservicios frente a un monolito tradicional).

---

### 1. Stack Tecnológico Integral (Desarrollo y Producción)

Para la construcción del sistema GIGA se seleccionó un conjunto de tecnologías modernas orientadas a una arquitectura de microservicios, garantizando escalabilidad, rendimiento y mantenibilidad tanto en entornos locales como productivos.

* **Infraestructura y Orquestación:**
* **Docker & Docker Compose:** Motor de contenerización para estandarizar el entorno de desarrollo y producción, eliminando conflictos de dependencias entre sistemas operativos (Windows/Linux/MacOS).
* **Nginx:** Servidor web utilizado como **Gateway y Reverse Proxy**. Gestiona el enrutamiento de tráfico, seguridad SSL y evita conflictos de CORS al centralizar las peticiones.


* **Backend y Persistencia:**
* **Python + Django REST Framework (DRF):** Núcleo lógico del sistema, encargado de la API RESTful, autenticación y reglas de negocio complejas (liquidación de haberes),.
* **PostgreSQL 16 (Alpine):** Base de datos relacional robusta. Se priorizó una imagen ligera (Alpine) y una estrategia *Database First* para garantizar la integridad referencial.


* **Frontend (Cliente):**
* **SvelteKit + Vite:** Framework progresivo seleccionado por su eficiencia (sin Virtual DOM) y menor *bundle size*, optimizando la experiencia en dispositivos móviles de gama media utilizados por los agentes,.


* **Servicios Auxiliares e IA:**
* **MinIO:** Almacenamiento de objetos (S3 compatible) para desacoplar los archivos binarios (PDFs del convenio) de la base de datos, mejorando el rendimiento.
* **N8N:** Motor de automatización *low-code* para orquestar los flujos de inteligencia artificial y notificaciones por correo.
* **Google Gemini API:** Modelo de lenguaje utilizado para el procesamiento de consultas sobre el Convenio Colectivo.


* **Plataforma de Producción:**
* **Railway:** Servicio de nube (PaaS) para el despliegue continuo y gestión de volúmenes persistentes.



### 2. Justificación de la Orquestación: Un Desafío de Aprendizaje

Si bien el alcance del proyecto permitía optar por una arquitectura monolítica tradicional (más sencilla de configurar), el equipo tomó la decisión deliberada de implementar una **arquitectura de microservicios contenerizada**. Esta elección no fue solo técnica, sino un **desafío personal y educativo** para superar los límites de nuestro conocimiento previo.

Decidimos "salir de la zona de confort" para dominar estándares de la industria moderna. Aprender a orquestar contenedores con **Docker** y configurar **Nginx** como manejador de conexiones nos permitió entender profundamente cómo interactúan los componentes de software en una red distribuida. Esta complejidad intencional fortaleció nuestras habilidades *Full Stack*, enseñándonos a resolver problemas de redes internas, volúmenes de datos y variables de entorno que una arquitectura monolítica hubiera ocultado. Gracias a esta estrategia, logramos un entorno de desarrollo agnóstico y portable, donde el sistema funciona idénticamente en la máquina de cualquier integrante, independientemente de su sistema operativo,.

### 3. Flujo de Conexión y Redes en Desarrollo (Docker)

La arquitectura se diseñó sobre una red virtual privada (`giga-network`) gestionada por Docker, aislando los servicios del exterior y centralizando el acceso. El flujo de conexión funciona de la siguiente manera:

1. **Punto Único de Entrada (Gateway):** Todo el tráfico externo (del navegador del desarrollador) ingresa exclusivamente por el puerto **80**, gestionado por el contenedor de **Nginx**.
2. **Enrutamiento Inteligente (Reverse Proxy):** Nginx analiza la petición y la deriva al contenedor correspondiente dentro de la red interna:
* Las peticiones de interfaz web se redirigen al contenedor de **Frontend (SvelteKit)** en el puerto 3000.
* Las llamadas a la API (`/api/...`) se redirigen al contenedor de **Backend (Django)** en el puerto 8000.
* Las peticiones de automatización (`/webhook/...`) se envían a **N8N**.


3. **Comunicación Inter-Servicios:** Dentro de la red `giga-network`, los contenedores se comunican por nombre de servicio (DNS interno de Docker) sin exponerse públicamente. Por ejemplo, el Backend accede a la base de datos llamando al host `postgres` (puerto 5432) y N8N recupera documentos llamando a `minio` (puerto 9000).

### 4. Estrategia de Despliegue en la Nube: Selección de Railway

La inversión de tiempo realizada en la contenerización (Docker) durante el desarrollo resultó ser el factor clave para una puesta en producción ágil y exitosa. Para el entorno productivo, realizamos un análisis comparativo entre tres proveedores:

* **Oracle Cloud:** Descartado por la alta complejidad de configuración de sus instancias VM para los tiempos del proyecto.
* **Render:** Descartado tras detectar una limitación crítica: la falta de soporte para volúmenes persistentes en sus planes accesibles, lo que causaba la pérdida de configuraciones de N8N y archivos de MinIO tras cada reinicio,.
* **Railway (Seleccionado):** Elegido por su soporte nativo para `Docker Compose` y gestión automática de **Volúmenes Persistentes**.

Gracias a la estrategia de Dockerización previa, la migración a Railway fue transparente. Pudimos replicar la arquitectura local en la nube con un solo comando, y la capacidad de gestionar variables de entorno y logs en tiempo real nos permitió resolver problemas en producción (como errores de CORS y conexión de base de datos) de manera mucho más ágil que con métodos de despliegue tradicionales.