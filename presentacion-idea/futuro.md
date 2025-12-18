Basado en el análisis de tu documentación y una investigación sobre los estándares de integración nacional (AFIP/GDE) y biometría móvil, he redactado la sección de **Proyección y Futuro del Proyecto**.

Está dividida en los tres bloques estratégicos que solicitaste, con un lenguaje técnico que demuestra investigación y visión a largo plazo.

---

### 1. Escalabilidad del Modelo y Arquitectura Modular

Nuestro sistema GIGA fue diseñado no como una solución rígida, sino como un **framework de gestión de recursos humanos adaptable**. La lógica interna modeló el problema de las "Guardias" y "Asistencias" de forma abstracta, separando la estructura de datos (quién estuvo dónde y cuándo) de las reglas de negocio (cómo se paga eso).

* **Aplicabilidad en Otras Áreas (Salud y Seguridad):**
Gracias a que la lógica de liquidación (Cálculo del Plus 40%/20%) está encapsulada en funciones de base de datos y métodos específicos del backend (Python), el sistema es fácilmente exportable. Con modificaciones leves en los parámetros de configuración (sin reescribir el núcleo), este software puede implementarse en:
* **Hospitales y Clínicas:** Para gestionar guardias médicas, donde las reglas de horas son similares pero los convenios cambian.
* **Empresas de Seguridad Privada:** Para el control de rotación de puestos y horas nocturnas.


* **Modularidad "Hot-Swap" (Probada en Producción):**
La arquitectura de microservicios contenerizada (Docker) demostró su valor real cuando implementamos el módulo de **Incidencias** y refactorizamos **Licencias** en plena etapa final. Esta estructura nos permite:
* **Agregar funcionalidades:** Desplegar un nuevo contenedor (servicio) sin detener el sistema principal.
* **Eliminar/Reemplazar:** Dar de baja módulos obsoletos o actualizar lógica crítica en tiempo real sin "downtime" (tiempo de inactividad) perceptible para el usuario, una capacidad que validamos al corregir *bugs* de producción directamente en Railway.



### 2. Evolución Tecnológica: Ecosistema Móvil y Anti-Fraude (QR)

El siguiente salto evolutivo del proyecto es el desarrollo de una **Aplicación Nativa (iOS y Android)**, lo que habilitará el uso del hardware del dispositivo para solucionar la problemática del fraude en la asistencia ("Buddy Punching").

* **Sistema de Marcación por QR Dinámico (Tokenizado):**
Implementaremos un sistema de validación presencial estricta mediante un doble factor:
* **El Desafío:** En la entrada de la institución, una pantalla (tablet/monitor) mostrará un **QR Único Temporal** (tipo TOTP) que cambia cada 30 segundos.
* **La Validación:** El agente deberá escanear ese QR con su **App GIGA** instalada en su celular personal.
* **Anti-Fraude:** Esto garantiza que el agente está *físicamente* en el lugar (para ver el QR) y que está usando *su* dispositivo registrado (nadie puede marcar por él enviando una foto, ya que el QR expira en segundos).



### 3. Investigación I+D: Integraciones Nacionales y Biometría

Para esta sección, realizamos una investigación sobre los requisitos técnicos para escalar el sistema a nivel gubernamental y mejorar la seguridad.

#### A. Integración con Organismos Nacionales (AFIP / GEN / GDE)

Investigamos por qué la comunicación con sistemas como AFIP o GEN requiere una validación estricta de la App y la Base de Datos. No se trata solo de enviar datos, sino de **Interoperabilidad y Seguridad Jurídica**:

* **Autenticación WSN (Web Service de Negocio):** AFIP no permite conexiones directas. Requiere que nuestra aplicación obtenga un **Certificado Digital X.509** y solicite un "Ticket de Acceso" (TA) mediante el protocolo WSAA (Web Service de Autenticación y Autorización).
* **Validación de Estructura (Schemas):** La base de datos de GIGA debe validarse a nivel nacional para asegurar que nuestros modelos de datos (CUITs, Tipos de Factura/Recibo) cumplan estrictamente con los esquemas XML oficiales del gobierno (estándar SOAP). Si nuestra BD no valida contra estos esquemas, la integración es rechazada automáticamente.
* **Por qué es necesario:** Esta validación garantiza que un registro en GIGA tenga la misma validez legal que un registro en los servidores del gobierno.

#### B. Autenticación Biométrica (Huella/Rostro) - "Trae tu propia identidad"

En lugar de crear una base de datos de huellas propia (costoso y riesgoso por privacidad), la estrategia a futuro es utilizar la **Biometría Nativa del Dispositivo**.

* **Implementación Técnica:** Utilizaremos las APIs nativas (`BiometricPrompt` en Android / `LocalAuthentication` en iOS).
* **Cómo funciona:** La App GIGA no guardará la huella. Le pedirá al sistema operativo del celular: *"¿Es el dueño del teléfono quien está intentando marcar?"*.
* **Requisitos para lograrlo:**
1. **Keystore/Keychain:** Generar una llave criptográfica única cuando el usuario instala la App, guardada en el chip de seguridad del celular.
2. **Firma Digital:** Cuando el usuario pone el dedo/cara, el celular desbloquea esa llave y "firma" la marcación de asistencia.
3. **Backend Verification:** El servidor recibe la marcación firmada y valida que provenga del dispositivo confiable del agente. Esto reutiliza la seguridad de grado militar de los smartphones actuales sin costo extra para la organización.