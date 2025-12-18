Basado en tu solicitud y en los documentos adjuntos (especialmente "PRESENTACION - agregar" y "Documento final - GIGA"), he redactado la sección de **Desafíos y Ley de Conway**.

Esta sección conecta la teoría sociotécnica con la realidad vivida por el equipo, justificando los cambios arquitectónicos (como el paso a Database First) no solo como decisiones técnicas, sino como correcciones estructurales necesarias para evitar replicar los errores del proceso manual anterior.

---

### 1. Marco Teórico: La Ley de Conway como Herramienta de Diagnóstico

Para comprender la evolución y los desafíos de este proyecto, utilizamos la **Ley de Conway** como marco de análisis. Melvin Conway postuló en 1967 que *"las organizaciones que diseñan sistemas están limitadas a producir diseños que son copias de las estructuras de comunicación de estas organizaciones"*. En términos simples: el software termina pareciéndose a las personas y procesos que lo construyen.

Esto implica que el software no es solo código, sino un **artefacto sociotécnico**. Si el equipo de desarrollo o el cliente tienen una estructura de comunicación fragmentada o procesos viciados, el sistema resultante heredará esas mismas fallas arquitectónicas ("ineficiencias en interfaces"). Nuestro desafío principal fue evitar modelar el "caos" preexistente en el nuevo sistema.

### 2. Desafíos Enfrentados: Superando la "Trampa del Proceso Heredado"

#### A. El Dilema del Doble Rol (Cliente/Desarrollador) y la "Contaminación" de Requerimientos

Uno de los desafíos más singulares fue que una integrante del equipo ocupaba también el rol de "cliente real" (nexo con Protección Civil).

* **Estrategia Inicial:** Por consenso, decidimos aislarla inicialmente en un rol puramente de "Cliente" durante la etapa de relevamiento. El objetivo era evitar que su conocimiento interno del sistema actual (viciado por el uso de Excel y parches manuales) contaminara la solución técnica.
* **El Problema (Validación de Conway):** A pesar de esta precaución, en la primera etapa de requerimientos caímos en la trampa de **"modelar el problema con sus errores"** en lugar de modelar la solución. Inconscientemente, replicamos las ineficiencias del área administrativa en los diagramas iniciales, creando un flujo que digitalizaba la burocracia en lugar de optimizarla. Fue necesario realizar una "limpieza" profunda de los casos de uso para abstraernos del proceso manual y diseñar un sistema lógico puro.

#### B. Refactorización Arquitectónica: De "Code First" a "Database First"

Este vicio de origen se manifestó técnicamente en el Backend. Al inicio, utilizamos Django con un enfoque "Code First", dejando que el framework definiera la base de datos según nuestros modelos mentales iniciales.

* **El Resultado:** Esto generó una "lógica compleja innecesaria" en el backend. El código se llenó de parches para manejar las excepciones y reglas extrañas que arrastrábamos del proceso manual.
* **La Solución Estructural:** Tuvimos que reestructurar todo el proyecto adoptando una estrategia **"Database First"**. Diseñamos primero la base de datos en SQL (PostgreSQL) con reglas de integridad estrictas. Esto nos obligó a pensar en los datos de forma limpia y relacional, eliminando la "grasa" del proceso anterior. Esta decisión simplificó drásticamente la lógica del backend y redujo la deuda técnica.

#### C. Evolución del Equipo y Modularidad

A medida que el proyecto maduró, la dinámica del equipo cambió. La compañera que actuaba como cliente se integró plenamente al desarrollo, lo que nos permitió iterar más rápido.

* **Gestión de Nuevos Requerimientos:** Cuando surgieron necesidades no previstas, como el módulo de **Compensaciones** o **Incidencias**, ya habíamos aprendido la lección. En lugar de parcharlas sobre lo existente, evaluamos cómo modelarlas de manera óptima y modular.
* **Resultado:** Esta madurez nos permitió construir una aplicación flexible y desacoplada, aplicable no solo a Protección Civil, sino adaptable a otros ámbitos con problemáticas de guardias similares.

#### D. La Barrera Técnica: Docker y la Comunicación entre Contenedores

Finalmente, enfrentamos un desafío puramente técnico que también reflejaba problemas de comunicación (entre servicios). La implementación de **Docker** y la orquestación de microservicios fue compleja. Nos costó encontrar la configuración correcta para que los contenedores (Frontend, Backend, BD, N8N) se "hablaran" entre sí dentro de la red interna sin exponerse innecesariamente.

* **Superación:** Tuvimos que reestructurar la configuración de `docker-compose` para pasar de un entorno monolítico a uno de servicios aislados con volúmenes persistentes, aprendiendo en el proceso sobre redes virtuales y gateways (Nginx).