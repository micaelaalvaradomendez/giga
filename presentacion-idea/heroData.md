Basado en el análisis de tus apuntes, especialmente los archivos de presentación y el documento final, he estructurado la sección de la **Problemática** como la pediste.

Está redactada con un perfil profesional (Analista Universitario/Ingeniero de Software), utilizando la terminología técnica adecuada pero manteniendo la claridad para una audiencia general.

---

### 1. Importancia de la Aplicación del Software (Impacto y Valor Agregado)

La importancia de la implementación del sistema **GIGA** (Gestión Integral de Guardias y Asistencia) trasciende la simple modernización tecnológica; radica en la **transformación digital** de un proceso crítico para la Secretaría de Protección Civil. El valor agregado del proyecto se sustenta en tres ejes fundamentales:

* **Integridad Financiera y Cumplimiento Normativo:** El sistema garantiza el cumplimiento estricto de la normativa vigente (Resolución N.° 425/22). Automatiza reglas de negocio complejas, como la distinción de incentivos salariales ("Plus" del 40% vs. 20%) según la categoría del agente (Operativo vs. Administrativo), asegurando que los fondos públicos se liquiden con precisión y eliminando la discrecionalidad humana,.
* **Transparencia y Trazabilidad (Auditoría):** Se introduce un estándar de **auditoría inmutable**. A diferencia del proceso anterior, cada modificación en una guardia o asistencia deja una huella digital indeleble (quién, cuándo y qué cambió), lo cual es vital para organismos públicos susceptibles a inspecciones.
* **Democratización de la Información:** El sistema rompe con la asimetría de información. Permite que cada actor, desde el Agente hasta el Director, gestione y audite su propio trabajo en tiempo real desde cualquier dispositivo, reduciendo la carga administrativa de consultas presenciales y empoderando al usuario final.

### 2. Descripción del Sistema Actual (La Problemática a Reemplazar)

La gestión actual depende de lo que técnicamente clasificamos como **"Sistemas Legados de Escritorio"**, caracterizados por procesos manuales, fragmentados y tecnológicamente obsoletos.

* **La "Caja Negra" del Excel y VBA:** El núcleo administrativo depende de planillas de cálculo con macros VBA complejas. Esto genera una alta dependencia tecnológica, ya que requiere instalación manual en cada equipo y presenta problemas de compatibilidad según la arquitectura del procesador (x86 vs x64),.
* **Silos de Información y Falta de Sincronización:** Al trabajar con archivos locales, la información no fluye. Si una Jefatura carga una novedad, esta queda aislada en su computadora sin reflejarse en tiempo real para la Dirección. Esto provoca inconsistencias graves entre lo planificado y lo liquidado.
* **Vulnerabilidad y Opacidad:** El sistema actual carece de controles de seguridad robustos. No existe un registro de auditoría fiable que permita rastrear quién modificó un dato crítico, y la integridad de la información depende de que los archivos no se corrompan o eliminen accidentalmente.
* **Errores Operativos:** La carga manual induce a errores frecuentes, como pagar de más o de menos debido a malas interpretaciones de las licencias o fallos de tipeo, generando incertidumbre financiera en el personal.

### 3. La Solución que Aporta el Software (GIGA)

GIGA propone una reingeniería del proceso mediante una **plataforma web centralizada, contenerizada y auditable**, diseñada bajo una arquitectura de microservicios.

* **Automatización de Reglas de Negocio:** El sistema reemplaza el cálculo manual por algoritmos validados en el backend (Python/Django) y base de datos (PostgreSQL), que calculan automáticamente las horas efectivas y el "Plus" correspondiente, eliminando el error humano.
* **Arquitectura Robusta y Segura (RBAC):** Se implementa un control de acceso basado en roles (Role-Based Access Control) donde el 94% de las operaciones requieren autenticación. Además, se incluyen mecanismos de **seguridad ofensiva/defensiva** como la detección de fraude por IP y verificación de identidad cruzada (DNI de sesión vs. DNI ingresado).
* **Gestión de la "Realidad Operativa" (Compensaciones e Incidencias):** El software digitaliza el manejo de imprevistos. Permite gestionar "Compensaciones" por excesos horarios (ej. siniestros) y un flujo de "Incidencias" para reclamos, asegurando que cada hora extra esté justificada y aprobada jerárquicamente.
* **Innovación con Inteligencia Artificial (RAG):** Se integra un módulo de IA que utiliza una arquitectura RAG (Retrieval-Augmented Generation) para responder consultas sobre el Convenio Colectivo basándose exclusivamente en la documentación oficial, reduciendo la incertidumbre normativa de los agentes,.