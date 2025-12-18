// ================= CONFIGURACIÓN DE CONTENIDO =================
// Este archivo contiene SOLO los datos de la presentación
// Para agregar/eliminar slides, solo modifica este archivo

const slides = [
    {
        id: 4,
        title: "Metodología",
        icon: "📋",
        tabs: [
            {
                id: "estrategia",
                title: "Estrategia Híbrida",
                icon: "📊",
                content: `
                    <p><strong>Enfoque de trabajo:</strong> "Vertical Slicing" con modalidad Full-Stack.</p>
                    <ul>
                        <li><strong>Corte Vertical:</strong> Cada integrante implementa funcionalidades completas (DB → backend → frontend), evitando dependencias rígidas entre capas.</li>
                        <li><strong>Colaboración y mentoría:</strong> Revisiones de código y soporte interno para nivelar habilidades del equipo y compartir conocimientos técnicos (DB, Docker, seguridad, etc.).</li>
                        <li><strong>Autonomía:</strong> Se reducen cuellos de botella: los desarrolladores avanzan de forma independiente dominando el flujo completo de la funcionalidad.</li>
                    </ul>
                `
            },
            {
                id: "evolucion",
                title: "Evolución (Sprints)",
                icon: "🔄",
                content: `
                    <p><strong>Fases y cronología:</strong></p>
                    <ul>
                        <li><strong>Ingeniería de Requerimientos (Agosto-Septiembre):</strong> Relevamiento con el cliente y definición de casos de uso.</li>
                        <li><strong>Diseño de Arquitectura y Datos:</strong> Infraestructura en Docker y estrategia <em>Database First</em> para asegurar integridad del modelo.</li>
                        <li><strong>Desarrollo por Sprints:</strong>
                            <ul>
                                <li><strong>Sprint 1:</strong> Cimientos (Docker, autenticación/login).</li>
                                <li><strong>Sprint 2:</strong> Núcleo administrativo (ABM de agentes y áreas) e integración inicial con IA.</li>
                                <li><strong>Sprint 3:</strong> Lógica de negocio (Guardias, Asistencia) y módulo de Compensaciones.</li>
                                <li><strong>Sprint 4:</strong> Estabilización, módulo de Incidencias y hardening (RBAC).</li>
                            </ul>
                        </li>
                        <li><strong>Testeo y despliegue:</strong> Pruebas de integración y despliegue en Railway.</li>
                    </ul>
                `
            },
            {
                id: "dinamica",
                title: "Dinámica y Herramientas",
                icon: "🛠️",
                content: `
                    <p>Gestión del proyecto y herramientas utilizadas:</p>
                    <ul>
                        <li><strong>Validación con el cliente:</strong> Decisiones funcionales validadas para evitar retrabajo.</li>
                        <li><strong>Documentación asistida por IA:</strong> Uso de GitHub Copilot para generar resúmenes de sprint y documentación técnica.</li>
                        <li><strong>Gestión Kanban:</strong> Tablero Trello para seguimiento de tareas (Pendiente / En Progreso / Terminado).</li>
                        <li><strong>Comunicación rápida:</strong> Canal operativo en WhatsApp para decisiones inmediatas durante la codificación.</li>
                    </ul>
                    <div style="margin-top:20px; text-align:center;">
                        <img src="trello.png" alt="trello kanban" style="width:180px; height:auto; max-width:80%; border:3px solid var(--secondary-color); border-radius:10px; box-shadow:0 0 20px rgba(77, 238, 234, 0.3);">
                    </div>
                `
            }
        ]
},
    {
        id: 6,
        title: "Tecnología",
        icon: "💻",
        tabs: [
            {
                id: "stack",
                title: "Stack Tecnológico",
                icon: "🔧",
                content: `
                    <p><strong>Arquitectura de microservicios para escalabilidad y mantenibilidad:</strong></p>
                    <ul>
                        <li><strong>Infraestructura:</strong> Docker + Docker Compose (contenerización multiplataforma), Nginx como Gateway y Reverse Proxy (SSL, enrutamiento, CORS).</li>
                        <li><strong>Backend:</strong> Python + Django REST Framework (API RESTful, autenticación, reglas de negocio), PostgreSQL 16 Alpine (Database First para integridad referencial).</li>
                        <li><strong>Frontend:</strong> SvelteKit + Vite (sin Virtual DOM, menor bundle size, optimizado para móviles de gama media).</li>
                        <li><strong>Servicios auxiliares:</strong> MinIO (S3-compatible para PDFs), N8N (orquestación low-code de flujos e IA), Google Gemini API (procesamiento de consultas del Convenio Colectivo).</li>
                        <li><strong>Producción:</strong> Railway (PaaS con soporte Docker Compose y volúmenes persistentes).</li>
                    </ul>
                `
            },
            {
                id: "desafio",
                title: "Desafío de Aprendizaje",
                icon: "🎯",
                content: `
                    <p><strong>Decisión de arquitectura como aprendizaje intencional:</strong></p>
                    <ul>
                        <li>Aunque el proyecto permitía un <strong>monolito tradicional</strong>, elegimos <strong>microservicios contenerizados</strong> como desafío personal y educativo.</li>
                        <li>Objetivo: dominar estándares de la industria moderna (Docker, orquestación, redes internas, variables de entorno).</li>
                        <li>Beneficios: desarrollo de habilidades Full Stack, entorno portable y agnóstico (funciona idénticamente en cualquier OS: Windows/Linux/MacOS).</li>
                        <li>Resultado: comprensión profunda de cómo interactúan componentes distribuidos, preparación para entornos productivos complejos.</li>
                    </ul>
                `
            },
            {
                id: "despliegue",
                title: "Despliegue en Nube",
                icon: "☁️",
                content: `
                    <p><strong>Flujo de conexión Docker (desarrollo):</strong></p>
                    <ul>
                        <li><strong>Red privada:</strong> <code>giga-network</code> aisla servicios del exterior.</li>
                        <li><strong>Gateway único:</strong> Todo el tráfico entra por puerto 80 (Nginx), que enruta a Frontend (puerto 3000), Backend (8000) y N8N según la ruta.</li>
                        <li><strong>Comunicación interna:</strong> Contenedores usan DNS de Docker (ej. <code>postgres:5432</code>, <code>minio:9000</code>) sin exposición pública.</li>
                    </ul>
                    <p><strong>Selección de plataforma productiva:</strong></p>
                    <ul>
                        <li><strong>Oracle Cloud:</strong> Descartado (alta complejidad de configuración VM).</li>
                        <li><strong>Render:</strong> Descartado (sin volúmenes persistentes → pérdida de configuraciones N8N/MinIO).</li>
                        <li><strong>Railway (elegido):</strong> Soporte nativo Docker Compose, volúmenes persistentes, migración transparente (un solo comando), gestión de variables de entorno y logs en tiempo real.</li>
                    </ul>
                `
            }
        ]
    },
    {
        id: 7,
        title: "Inteligencia Artificial",
        icon: "🧠",
        tabs: [
            {
                id: "arquitectura",
                title: "Arquitectura RAG",
                icon: "🔄",
                content: `
                    <p><strong>Flujo de integración con IA (módulo Convenio):</strong></p>
                    <ul>
                        <li><strong>1. Solicitud:</strong> Usuario consulta en lenguaje natural desde SvelteKit → Nginx Gateway.</li>
                        <li><strong>2. Orquestación (n8n):</strong> Nginx deriva tráfico a n8n vía Webhook, iniciando un workflow automatizado.</li>
                        <li><strong>3. Recuperación de Contexto (RAG):</strong> n8n conecta a MinIO (S3-compatible), descarga PDF del Convenio Colectivo y extrae texto plano.</li>
                        <li><strong>4. Generación (Gemini):</strong> n8n construye prompt enriquecido (pregunta + texto PDF) y lo envía a Google Gemini con instrucciones de Grounding (responder solo según el documento).</li>
                        <li><strong>5. Entrega:</strong> Respuesta formateada en JSON vuelve al Frontend en tiempo real.</li>
                    </ul>
                    <p><strong>Beneficios:</strong> Desacople entre lógica de negocio e IA, cambio de documento sin tocar código.</p>
                `
            },
            {
                id: "optimizacion",
                title: "Optimización con IA",
                icon: "⚡",
                content: `
                    <p><strong>GitHub Copilot como auditor de calidad (Sprint 4):</strong></p>
                    <ul>
                        <li><strong>Análisis estático:</strong> Detección de antipatrones que degradaban rendimiento.</li>
                        <li><strong>Caso 1 (Layout Thrashing):</strong> Evento <code>mousemove</code> en panel admin forzaba recálculo de posición de todas las tarjetas en cada píxel → Solución: <code>requestAnimationFrame</code> limitando cálculos al elemento activo.</li>
                        <li><strong>Caso 2 (Peticiones redundantes):</strong> Menú principal ejecutaba <code>checkSession</code> en cada navegación → Solución: lógica de bandera + memoización CSS, reduciendo carga CPU en móviles.</li>
                    </ul>
                    <p><strong>Resultado:</strong> Mejora significativa de rendimiento en dispositivos de gama media.</p>
                `
            },
            {
                id: "seguridad",
                title: "Aprendizaje vs Seguridad",
                icon: "🔒",
                content: `
                    <p><strong>Decisión estratégica a futuro:</strong></p>
                    <ul>
                        <li><strong>Valor pedagógico:</strong> n8n permitió aprender orquestación de workflows y servicios, habilidad demandada en la industria.</li>
                        <li><strong>Riesgo identificado:</strong> Inyección de prompts indirecta / Stored XSS (OWASP Top 10 for LLMs) — atacante podría "envenenar" contexto para manipular al LLM y generar código JavaScript malicioso.</li>
                        <li><strong>Complejidad:</strong> Sanitización perfecta de respuestas generativas es extremadamente difícil de garantizar.</li>
                        <li><strong>Conclusión:</strong> Se priorizó seguridad e integridad de datos financieros sobre innovación del chatbot en producción crítica → refactorización o eliminación a futuro.</li>
                    </ul>
                `
            }
        ]
    },
    {
        id: 8,
        title: "Desafíos",
        icon: "🔥",
        tabs: [
            {
                id: "conway",
                title: "Ley de Conway",
                icon: "🧩",
                content: `
                    <p><strong>Marco teórico sociotécnico:</strong></p>
                    <ul>
                        <li><strong>Definición:</strong> "Las organizaciones que diseñan sistemas producen diseños que replican sus propias estructuras de comunicación" (Melvin Conway, 1967).</li>
                        <li><strong>Implicación:</strong> El software no es solo código, es un artefacto sociotécnico. Si el equipo/cliente tiene procesos fragmentados, el sistema heredará esas fallas arquitectónicas.</li>
                        <li><strong>Desafío GIGA:</strong> Evitar modelar el "caos" preexistente del sistema manual en Excel en la nueva arquitectura.</li>
                    </ul>
                `
            },
            {
                id: "proceso",
                title: "Trampa del Proceso Heredado",
                icon: "⚠️",
                content: `
                    <p><strong>Desafío del doble rol (cliente/desarrollador):</strong></p>
                    <ul>
                        <li><strong>Estrategia inicial:</strong> Aislar a integrante con rol dual como "solo cliente" en relevamiento para evitar contaminar solución técnica con vicios del sistema actual.</li>
                        <li><strong>Problema:</strong> Caímos en modelar el problema con sus errores (digitalizamos burocracia en lugar de optimizarla).</li>
                        <li><strong>Solución:</strong> Limpieza profunda de casos de uso para abstraernos del proceso manual y diseñar sistema lógico puro.</li>
                    </ul>
                    <p><strong>Refactorización Code First → Database First:</strong></p>
                    <ul>
                        <li><strong>Problema:</strong> Enfoque inicial Code First (Django) generó lógica compleja innecesaria y parches para excepciones heredadas del proceso manual.</li>
                        <li><strong>Solución estructural:</strong> Reestructurar a Database First (diseñar BD en PostgreSQL con reglas de integridad estrictas primero), eliminando "grasa" del proceso anterior y reduciendo deuda técnica.</li>
                    </ul>
                `
            },
            {
                id: "tecnicos",
                title: "Desafíos Técnicos",
                icon: "🛠️",
                content: `
                    <p><strong>Evolución del equipo y modularidad:</strong></p>
                    <ul>
                        <li>Integración plena de compañera cliente/dev permitió iteración más rápida.</li>
                        <li>Nuevos módulos (Compensaciones, Incidencias) modelados de manera óptima y modular, no como parches.</li>
                        <li>Resultado: aplicación flexible, desacoplada y adaptable a otros ámbitos.</li>
                    </ul>
                    <p><strong>Barrera Docker (comunicación entre contenedores):</strong></p>
                    <ul>
                        <li><strong>Desafío:</strong> Configuración correcta para que servicios (Frontend, Backend, BD, N8N) se comuniquen en red interna sin exposición innecesaria.</li>
                        <li><strong>Superación:</strong> Reestructurar <code>docker-compose</code> para pasar de monolito a servicios aislados con volúmenes persistentes, aprendiendo sobre redes virtuales y gateway (Nginx).</li>
                    </ul>
                    <p><strong>Otros desafíos resueltos:</strong></p>
                    <ul>
                        <li><strong>Infraestructura:</strong> Render sin persistencia (n8n se borraba) → migración a Railway.</li>
                        <li><strong>Seguridad:</strong> Fraude en marcación → validación cruzada de sesión e IP.</li>
                        <li><strong>CORS:</strong> Problemas de cookies entre dominios → configuración de Nginx.</li>
                    </ul>
                `
            }
        ]
    },
    {
        id: 9,
        title: "Aprendizajes",
        icon: "🎓",
        tabs: [
            {
                id: "analista",
                title: "Del Código al Modelo",
                icon: "🧠",
                content: `
                    <p><strong>La visión del analista:</strong></p>
                    <ul>
                        <li><strong>Lección principal:</strong> Un buen software nace de entender profundamente el negocio, no de teclear rápido.</li>
                        <li><strong>Aplicación de Conway:</strong> Aprendimos a no "programar la burocracia" — nuestra responsabilidad es cuestionar procesos, no solo automatizarlos.</li>
                        <li><strong>Abstracción:</strong> La robustez se logra con diseño de datos sólido (Database First), no con parches en el código. Modelar reglas de negocio de forma agnóstica permite escalabilidad más allá del dominio original.</li>
                        <li><strong>Transformación:</strong> De estudiantes que tiran código a analistas que resuelven problemas.</li>
                    </ul>
                `
            },
            {
                id: "tecnica",
                title: "Madurez Técnica",
                icon: "⚙️",
                content: `
                    <p><strong>Salir de la zona de confort académica:</strong></p>
                    <ul>
                        <li><strong>Orquestación vs. programación:</strong> Diferencia entre hacer "una página web" y construir una arquitectura de software (Docker, Nginx, microservicios = ecosistema vivo de partes interconectadas).</li>
                        <li><strong>Infraestructura y despliegue:</strong> Aprendizaje sobre redes, volúmenes persistentes, CI/CD y debugging en producción real.</li>
                        <li><strong>Responsabilidad tecnológica:</strong> No deslumbrarse por "moda" (hype de IA) si compromete seguridad. Priorizar integridad del sistema sobre innovación superficial.</li>
                        <li><strong>Gestión de deuda técnica:</strong> Refactorización planificada, importancia de Database First, seguridad RBAC.</li>
                    </ul>
                `
            },
            {
                id: "humano",
                title: "Crecimiento Humano",
                icon: "🤝",
                content: `
                    <p><strong>Soft skills y gestión de equipos:</strong></p>
                    <ul>
                        <li><strong>Profesionalismo y amistad:</strong> Integración de nuevos compañeros obligó a profesionalizar interacciones — separar lo personal de lo académico para tomar decisiones objetivas.</li>
                        <li><strong>Empatía activa:</strong> Equipo de alto rendimiento no es el que nunca falla, sino el que se cubre las espaldas. Cuando un compañero no podía cumplir, el resto asumía carga sin reproches.</li>
                        <li><strong>Superación de expectativas:</strong> No solo aprobar, sino entregar producto de nivel profesional. Autoexigencia para superar límites y aprender tecnologías desde cero en tiempos récord.</li>
                        <li><strong>Contexto difícil:</strong> Proyecto desarrollado en contexto personal/académico complejo — resiliencia y colaboración humana probadas.</li>
                    </ul>
                    <p><strong>Conclusión:</strong> GIGA es la prueba tangible de nuestra capacidad para transformar problemas humanos en soluciones tecnológicas eficientes, seguras y escalables.</p>
                `
            }
        ]
    },
    {
        id: 10,
        title: "Sistema Final",
        icon: "🚀",
        tabs: [
            {
                id: "acceso-web",
                title: "Acceso Web",
                icon: "🌐",
                content: `
                    <p style="text-align:center; font-size:1.3rem; margin-bottom:30px;">El sistema está operativo y en producción.</p>
                    
                    <div style="display:flex; justify-content:center; align-items:center; gap:50px; margin-top:30px;">
                        <!-- QR Code -->
                        <div style="text-align:center;">
                            <h3 style="color:var(--secondary-color); margin-bottom:15px;">Acceso Web</h3>
                            <img src="qr-pag.png" alt="QR Code GIGA" style="width:200px; height:200px; border:3px solid var(--accent-color); border-radius:10px; box-shadow:0 0 20px rgba(255,42,109,0.3);">
                            <p style="margin-top:10px; font-size:1.1rem; color:#05d9e8;">giga-untdf.up.railway.app</p>
                        </div>
                        
                        <!-- Credenciales de Acceso -->
                        <div style="background:rgba(255,255,255,0.05); padding:30px; border-radius:15px; border:1px solid rgba(5,217,232,0.3); min-width:350px;">
                            <h3 style="color:var(--accent-color); margin-bottom:20px; text-align:center;">Credenciales de Prueba</h3>
                            
                            <div style="margin-bottom:20px; padding:15px; background:rgba(0,0,0,0.3); border-radius:8px;">
                                <p style="font-size:0.9rem; color:#888; margin-bottom:5px;">Usuarios:</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>CUIL:</strong> 10-91327519-8</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>CUIL:</strong> 10-94803013-8</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>CUIL:</strong> 10-91537996-8</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>CUIL:</strong> 10-99530780-8</p>
                            </div>
                            
                            <div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:8px;">
                                <p style="font-size:0.9rem; color:#888; margin-bottom:5px;">Contraseña:</p>
                                
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>Testing123!</strong></p>
                            </div>
                        </div>
                    </div>
                `
            },
            {
                id: "presentacion",
                title: "Presentación",
                icon: "📊",
                content: `
                    <div style="display:flex; flex-direction:column; align-items:center; gap:20px;">
                        <h3 style="color:var(--secondary-color);">Equipo de Desarrollo</h3>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; text-align:left; font-size:1.1rem;">
                            <div>• Aguila Cárcamo Tayra Belén</div>
                            <div>• Alvarado Mendez Micaela</div>
                            <div>• Criniti Teresa</div>
                            <div>• Frers Pamela</div>
                            <div>• García Cristian</div>
                            <div>• Gomez Antonaz Leandro</div>
                        </div>
                        
                        <div style="margin-top:30px; text-align:center;">
                            <h3 style="color:var(--accent-color); margin-bottom:15px;">Acceder a la Presentación</h3>
                            <img src="qr-prest.png" alt="QR Presentación" style="width:180px; height:180px; border:3px solid var(--secondary-color); border-radius:10px; box-shadow:0 0 20px rgba(77, 238, 234, 0.3);">
                        </div>
                    </div>
                `
            }
        ]
    },
    {
        id: 12,
        title: "Futuro",
        icon: "🔮",
        tabs: [
            {
                id: "escalabilidad",
                title: "Escalabilidad Modular",
                icon: "🔧",
                content: `
                    <p><strong>GIGA como framework adaptable:</strong></p>
                    <ul>
                        <li><strong>Diseño abstracto:</strong> Lógica de "Guardias" y "Asistencias" separada de reglas de negocio (cálculo de Plus encapsulado en funciones DB y backend Python).</li>
                        <li><strong>Aplicabilidad:</strong> Exportable a hospitales (guardias médicas), empresas de seguridad (rotación de puestos), industria (turnos 24/7) con modificaciones leves en parámetros.</li>
                        <li><strong>Modularidad "Hot-Swap":</strong> Arquitectura Docker permite agregar/eliminar servicios sin downtime (probado en producción: módulo Incidencias y refactorización de Licencias en Railway).</li>
                    </ul>
                `
            },
            {
                id: "movil",
                title: "App Nativa y Anti-Fraude",
                icon: "📱",
                content: `
                    <p><strong>Siguiente salto: aplicación móvil iOS/Android.</strong></p>
                    <ul>
                        <li><strong>Sistema QR Dinámico (Tokenizado):</strong>
                            <ul>
                                <li>Pantalla en entrada de institución muestra QR único temporal (tipo TOTP) que cambia cada 30 seg.</li>
                                <li>Agente escanea con App GIGA en su celular registrado.</li>
                                <li>Anti-Fraude: garantiza presencia física (ver QR) + uso de dispositivo personal (nadie puede marcar por otro enviando foto, QR expira).</li>
                            </ul>
                        </li>
                    </ul>
                `
            },
            {
                id: "integraciones",
                title: "Integraciones y Biometría",
                icon: "🔐",
                content: `
                    <p><strong>Investigación I+D para escalabilidad gubernamental:</strong></p>
                    <ul>
                        <li><strong>Integración AFIP/GDE:</strong>
                            <ul>
                                <li>Certificado Digital X.509 y protocolo WSAA (Ticket de Acceso).</li>
                                <li>Validación de estructura BD contra esquemas XML oficiales (estándar SOAP) para garantizar validez legal.</li>
                            </ul>
                        </li>
                        <li><strong>Biometría nativa (Huella/Rostro):</strong>
                            <ul>
                                <li>APIs <code>BiometricPrompt</code> (Android) / <code>LocalAuthentication</code> (iOS).</li>
                                <li>App no guarda huella, consulta al OS del celular: "¿Es el dueño del teléfono?"</li>
                                <li>Implementación: Keystore/Keychain genera llave criptográfica única → firma digital de marcación → backend verifica firma del dispositivo confiable.</li>
                                <li>Reutiliza seguridad de grado militar de smartphones sin costo extra.</li>
                            </ul>
                        </li>
                    </ul>
                `
            }
        ]
    }
];

const heroData = {
    title: "GIGA SYSTEM",
    subtitle: "Gestión Integral de Guardias y Asistencia",
    tabs: [
        {
            id: "importancia",
            title: "Importancia",
            icon: "🚨",
            content: `
                <p>La Secretaría de Protección Civil opera en un entorno crítico donde la precisión administrativa es vital.</p>
                <ul>
                    <li><strong>El Problema:</strong> Gestión manual, planillas de papel y Excel con macros (VBA) obsoletas.</li>
                    <li><strong>El Riesgo:</strong> Errores en cálculos de sueldos (Plus), falta de transparencia y dependencia física.</li>
                    <li><strong>La Misión:</strong> Modernizar, centralizar y asegurar la información.</li>
                </ul>
            `
        },
        {
            id: "sistemas-viejos",
            title: "Sistemas Viejos",
            icon: "💾",
            content: `
                <p>Analizamos la situación actual encontrando:</p>
                <ul>
                    <li>Dependencia de una herramienta interna en Excel con VBA.</li>
                    <li>Instalación manual equipo por equipo (Sin sincronización).</li>
                    <li>Incompatibilidad de arquitecturas (x86 vs x64).</li>
                    <li>Errores humanos recurrentes en la carga de horas.</li>
                </ul>
                <div style="display:flex; justify-content:center; gap:20px; margin-top:20px; flex-wrap:wrap;">
                    <figure style="margin:0; text-align:center;">
                        <img src="actuial1.jpeg" alt="Captura sistema actual 1" style="width:220px; height:auto; border-radius:8px; border:2px solid rgba(255,255,255,0.06);">
                    </figure>
                    <figure style="margin:0; text-align:center;">
                        <img src="actuial2.jpeg" alt="Captura sistema actual 2" style="width:220px; height:auto; border-radius:8px; border:2px solid rgba(255,255,255,0.06);">
                    </figure>
                    <figure style="margin:0; text-align:center;">
                        <img src="actuial3.jpeg" alt="Captura sistema actual 3" style="width:220px; height:auto; border-radius:8px; border:2px solid rgba(255,255,255,0.06);">
                    </figure>
                </div>
            `
        },
        {
            id: "solucion",
            title: "La Solución",
            icon: "🌐",
            content: `
                <p>Transformación de procesos manuales a un flujo de datos auditable:</p>
                <ul>
                    <li><strong>1. Integridad Financiera:</strong> Automatización del cálculo de Plus (40%/20%) según reglas de negocio.</li>
                    <li><strong>2. Anti-Fraude:</strong> Verificación cruzada de identidad (DNI + IP + Sesión) en tiempo real.</li>
                    <li><strong>3. Cadena de Mando:</strong> Workflow de aprobación estricto (Planificación vs. Validación).</li>
                    <li><strong>4. Realidad Operativa:</strong> Gestión digital de Compensaciones (Horas Extra) e Incidencias.</li>
                    <li><strong>5. Democratización:</strong> Dashboard 24/7 para el agente (Autogestión).</li>
                </ul>
            `
        }
    ]
};

