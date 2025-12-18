Basado en la documentación detallada del informe final y tus requerimientos específicos, he redactado la sección de **Metodología y Organización** estructurada en los tres bloques que solicitaste.

Esta redacción está diseñada para resaltar la madurez del equipo (colaboración y nivelación de habilidades) y el uso inteligente de herramientas modernas (IA para documentación).

---

### 1. Estrategia de Trabajo: Enfoque "Full Stack" y Nivelación Técnica

Para abordar la complejidad del sistema GIGA, el equipo adoptó una estrategia de desarrollo basada en el **"Corte Vertical" (Vertical Slicing)** bajo una modalidad Full-Stack. En lugar de dividirnos rígidamente en desarrolladores de "Frontend" y "Backend", cada integrante asumió la responsabilidad de implementar funcionalidades completas de extremo a extremo (desde la tabla en la base de datos hasta la interfaz de usuario).

Esta decisión fue estratégica para fortalecer las capacidades del grupo:

* **Colaboración y Mentoría:** Esta dinámica permitió nivelar las habilidades técnicas del equipo. Aquellos integrantes con mayor experiencia en ciertas capas (ej. Base de Datos o Docker) brindaron soporte y "code reviews" activos a sus compañeros durante la implementación de sus módulos, transformando el desarrollo en un proceso de aprendizaje continuo y asegurando que todo el equipo comprendiera la arquitectura integral del sistema.


* **Autonomía:** Evitamos los cuellos de botella tradicionales donde el Frontend debe esperar a que el Backend termine una API. Al dominar el flujo completo, cada desarrollador pudo avanzar con autonomía en sus tareas asignadas.



### 2. Evolución del Ciclo de Vida del Software

El proyecto siguió una **Metodología Híbrida**, comenzando con una fase de planificación estructurada (Cascada) para garantizar bases sólidas, y transicionando hacia una ejecución dinámica (Ágil) para la construcción del producto.

La evolución del software se dio en las siguientes etapas cronológicas:

1. 
**Ingeniería de Requerimientos y Casos de Uso (Fase Secuencial):** Durante agosto y septiembre, nos enfocamos exclusivamente en el relevamiento de necesidades con el cliente y la definición formal de los Requerimientos Funcionales y los Diagramas de Casos de Uso, sin escribir código aún.


2. **Diseño de Arquitectura y Datos:** Definimos la infraestructura en Docker y diseñamos el Modelo Entidad-Relación. Aquí tomamos la decisión crítica de migrar a una estrategia **"Database First"**, diseñando las tablas en SQL directo para garantizar la integridad antes de conectar el backend.


3. **Desarrollo Iterativo (Sprints):**
* 
**Sprint 1:** Construcción de los cimientos (Docker, Autenticación y Login).


* 
**Sprint 2:** Desarrollo del núcleo administrativo (ABM de Agentes y Áreas) e integración inicial con IA.


* 
**Sprint 3:** Implementación de la lógica de negocio compleja (Guardias, Asistencia y el módulo no planificado de Compensaciones).


* 
**Sprint 4:** Estabilización, desarrollo del módulo de Incidencias y hardening de seguridad (RBAC).




4. 
**Testeo y Puesta en Producción:** Finalmente, realizamos pruebas de integración y desplegamos la solución en **Railway**, asegurando la persistencia de datos y la correcta configuración de dominios cruzados para la entrega final.



### 3. Dinámica de Equipo y Herramientas de Gestión

La gestión del proyecto se sustentó en la validación constante y el uso de herramientas de IA para mantener la trazabilidad.

* **Validación con el Cliente:** Todas las decisiones funcionales, desde la lógica del "Plus Salarial" hasta la incorporación del módulo de "Compensaciones", fueron corroboradas y validadas con el nexo de la Secretaría de Protección Civil antes de su implementación. Esto evitó el retrabajo y aseguró que el software resolviera problemas reales.


* **Documentación Asistida por IA (Copilot):** Implementamos una metodología innovadora para la documentación técnica. Utilizamos **GitHub Copilot** en modo agente para analizar los "diffs" (diferencias) entre los distintos commits del repositorio. La IA procesaba los cambios técnicos realizados en el código y generaba los borradores de los **Resúmenes de Sprint**, garantizando que la documentación reflejara con exactitud técnica la evolución del desarrollo.


* 
**Gestión de Tareas (Trello):** Utilizamos un tablero Kanban en Trello para visualizar el flujo de trabajo, asignando responsables a cada tarjeta y monitoreando estrictamente qué estaba "Pendiente", "En Progreso" y "Terminado".


* **Toma de Decisiones Ágil (WhatsApp):** Para resolver dudas operativas durante la codificación ("¿Cómo manejamos este error?", "¿Cambiamos este tipo de dato?"), utilizamos un grupo de WhatsApp como canal de decisión rápida. Esto permitió que cualquier integrante consultara una duda y recibiera el aval inmediato del resto del equipo para avanzar sin bloqueos.