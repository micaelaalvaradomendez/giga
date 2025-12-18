Basado en los documentos técnicos adjuntos y la investigación sobre vulnerabilidades en LLMs, aquí tienes la redacción detallada para tu informe, estructurada en las tres secciones solicitadas.

---

### 1. Arquitectura y Flujo de Integración con IA (Módulo Convenio)

Para la funcionalidad de "Consulta del Convenio", no implementamos una conexión directa entre el Frontend y la IA. En su lugar, diseñamos una arquitectura de orquestación de microservicios utilizando **n8n** como middleware inteligente. Esto nos permitió desacoplar la lógica de negocio de la lógica de inteligencia artificial.

**El flujo de comunicación es el siguiente:**

1. **Solicitud del Usuario:** El Agente realiza una pregunta en lenguaje natural desde la interfaz (SvelteKit). Esta petición sale hacia nuestro Gateway (Nginx).
2. **Orquestación (n8n):** Nginx deriva el tráfico al contenedor de **n8n** mediante un Webhook (POST). Aquí inicia un flujo de trabajo automatizado ("Workflow") que actúa como cerebro de la operación.
3. **Recuperación de Contexto (RAG):**
* Antes de preguntar a la IA, n8n se conecta al servicio de almacenamiento **MinIO** (compatible con S3) dentro de nuestra red interna Docker.
* Descarga el archivo PDF del Convenio Colectivo actualizado. Esto es crítico porque permite cambiar el documento legal sin tocar una sola línea de código.
* Utiliza un nodo de procesamiento para extraer el texto plano del PDF.


4. **Generación de Respuesta (Gemini):**
* n8n construye un *prompt* enriquecido que combina la pregunta del usuario con el texto extraído del PDF.
* Se envía este paquete a la API de **Google Gemini**, con instrucciones estrictas de "Grounding" (responder basándose *únicamente* en el texto proporcionado) para eliminar alucinaciones.


5. **Entrega:** La respuesta generada vuelve a n8n, se formatea en JSON y se envía de regreso al Frontend para ser mostrada al usuario en tiempo real.

### 2. Optimización de Frontend con GitHub Copilot (Modo Agente)

Durante la fase de estabilización (Sprint 4), integramos **GitHub Copilot en modo Agente** no solo para autocompletar código, sino como un auditor de calidad en tiempo real. Utilizamos esta herramienta para realizar un análisis estático profundo del repositorio, detectando "antipatrones" que degradaban el rendimiento de la aplicación.

**Casos de éxito en la optimización:**

* **Detección de Saturación del DOM (Layout Thrashing):** El agente identificó un problema crítico en el panel de administración (`paneladmin`), donde un evento de movimiento del mouse (`mousemove`) forzaba al navegador a recalcular la posición de *todas* las tarjetas en cada píxel de movimiento. Copilot sugirió y refactorizó el código para usar `requestAnimationFrame`, limitando los cálculos solo al elemento activo y liberando el hilo principal del navegador.
* **Refactorización de Componentes Reactivos (`menu.svelte`):** Detectamos que el menú principal realizaba peticiones de red redundantes (`checkSession`) cada vez que el usuario navegaba entre páginas. El agente propuso una lógica de "bandera de control" para ejecutar la verificación una sola vez y memoizar los estilos CSS, reduciendo drásticamente la carga de CPU en dispositivos móviles de gama media.

### 3. Aprendizaje vs. Seguridad: El Futuro del Módulo de IA

La implementación de este módulo con **n8n** fue una herramienta pedagógica invaluable. Nos permitió aprender sobre **automatización de flujos de trabajo (Workflows)** y orquestación de servicios, habilidades altamente demandadas en la industria actual. Logramos construir un sistema funcional capaz de leer documentos y razonar sobre ellos en tiempo récord.

**Sin embargo, la decisión estratégica a futuro es refactorizar o eliminar este módulo en entornos productivos críticos.**

Durante las pruebas de seguridad en la etapa de producción, y tras investigar informes recientes de ciberseguridad (OWASP Top 10 for LLMs), identificamos un riesgo significativo conocido como **Inyección de Scripts a través de LLM (Indirect Prompt Injection / Stored XSS)**.

**¿Por qué es un riesgo?**
Las investigaciones demuestran que un atacante podría intentar "envenenar" el contexto (por ejemplo, enviando una "novedad" con instrucciones ocultas) para manipular al modelo de lenguaje. Si el LLM no filtra correctamente su salida y la aplicación renderiza esa respuesta sin una sanitización estricta, el modelo podría ser engañado para generar código JavaScript malicioso (`<script>...`) que se ejecutaría en el navegador del administrador al leer el reporte. Dado que garantizar una sanitización perfecta de las respuestas de una IA generativa es extremadamente complejo, priorizamos la seguridad e integridad de los datos financieros sobre la innovación del chatbot en esta versión final.