// ================= CONFIGURACIÓN DE DATOS =================
// Datos embebidos para funcionamiento independiente (sin servidor)
const slides = [
    {
        id: 4,
        title: "Metodología",
        icon: "📋",
        content: `
            <p>Adoptamos un enfoque Híbrido:</p>
            <ul>
                <li><strong>Fase 1 (Cascada):</strong> Análisis y Diseño estricto (Agosto-Septiembre).</li>
                <li><strong>Fase 2 (Ágil/Scrum):</strong> Construcción iterativa e incremental.</li>
            </ul>
            <p>Organización mediante Tablero Kanban (Trello) y Git Flow.</p>
        `
    },
    {
        id: 5,
        title: "Sprints",
        icon: "🏃‍♂️",
        content: `
            <p>Evolución del desarrollo en 4 etapas:</p>
            <ul>
                <li><strong>Sprint 1:</strong> Cimientos, Docker y Autenticación.</li>
                <li><strong>Sprint 2:</strong> Núcleo (Agentes), refactorización a "Database First".</li>
                <li><strong>Sprint 3:</strong> Lógica de Negocio (Guardias, Licencias) y Compensaciones.</li>
                <li><strong>Sprint 4:</strong> Seguridad (RBAC), Anti-Fraude y Despliegue Final.</li>
            </ul>
        `
    },
    {
        id: 6,
        title: "Tecnología",
        icon: "💻",
        tabs: [
            {
                id: "backend",
                title: "Backend",
                icon: "🐍",
                content: `
                    <p>Django REST Framework con PostgreSQL</p>
                    <ul>
                        <li>API RESTful</li>
                        <li>Autenticación JWT</li>
                        <li>ORM Database First</li>
                    </ul>
                `
            },
            {
                id: "frontend",
                title: "Frontend",
                icon: "⚡",
                content: `
                    <p>SvelteKit con TypeScript</p>
                    <ul>
                        <li>SSR/SPA Híbrido</li>
                        <li>Reactivo</li>
                        <li>Optimizado</li>
                    </ul>
                `
            },
            {
                id: "infraestructura",
                title: "Infraestructura",
                icon: "🐳",
                content: `
                    <p>Docker + Railway</p>
                    <ul>
                        <li>Microservicios</li>
                        <li>CI/CD Automático</li>
                        <li>NGINX Gateway</li>
                    </ul>
                `
            }
        ]
    },
    {
        id: 7,
        title: "Inteligencia Artificial",
        icon: "🧠",
        content: `
            <p>Integración de Chatbot para consultas del Convenio Colectivo.</p>
            <ul>
                <li><strong>Motor:</strong> n8n (Orquestador de flujos).</li>
                <li><strong>Almacenamiento:</strong> MinIO (Object Storage) para los PDFs.</li>
                <li><strong>Modelo:</strong> Gemini Flash 2.5 con "Corpus Cerrado" para evitar alucinaciones.</li>
            </ul>
        `
    },
    {
        id: 8,
        title: "Desafíos",
        icon: "🔥",
        content: `
            <p>Problemas críticos resueltos durante el desarrollo:</p>
            <ul>
                <li><strong>Infraestructura:</strong> Render no permitía persistencia de archivos (n8n se borraba). Migramos a <strong>Railway</strong>.</li>
                <li><strong>Seguridad:</strong> Detección de fraude (Marcación por otros). Implementamos validación cruzada de sesión e IP.</li>
                <li><strong>CORS:</strong> Problemas de cookies entre Front y Back en dominios distintos.</li>
            </ul>
        `
    },
    {
        id: 9,
        title: "Aprendizajes",
        icon: "🎓",
        content: `
            <ul>
                <li>Gestión de deuda técnica y refactorización.</li>
                <li>Despliegue real en nube (CI/CD).</li>
                <li>Importancia de "Database First" en sistemas complejos.</li>
                <li>Seguridad ofensiva y defensiva (RBAC).</li>
            </ul>
        `
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
                            <img src="imagenes/qr-pag.png" alt="QR Code GIGA" style="width:200px; height:200px; border:3px solid var(--accent-color); border-radius:10px; box-shadow:0 0 20px rgba(255,42,109,0.3);">
                            <p style="margin-top:10px; font-size:1.1rem; color:#05d9e8;">giga-untdf.up.railway.app</p>
                        </div>
                        
                        <!-- Credenciales de Acceso -->
                        <div style="background:rgba(255,255,255,0.05); padding:30px; border-radius:15px; border:1px solid rgba(5,217,232,0.3); min-width:350px;">
                            <h3 style="color:var(--accent-color); margin-bottom:20px; text-align:center;">Credenciales de Prueba</h3>
                            
                            <div style="margin-bottom:20px; padding:15px; background:rgba(0,0,0,0.3); border-radius:8px;">
                                <p style="font-size:0.9rem; color:#888; margin-bottom:5px;">Usuario 1:</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>CUIL:</strong> 20-12345678-9</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>Contraseña:</strong> demo123</p>
                            </div>
                            
                            <div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:8px;">
                                <p style="font-size:0.9rem; color:#888; margin-bottom:5px;">Usuario 2:</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>CUIL:</strong> 27-98765432-1</p>
                                <p style="font-family:monospace; font-size:1.1rem;"><strong>Contraseña:</strong> demo456</p>
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
                            <img src="imagenes/qr-prest.png" alt="QR Presentación" style="width:180px; height:180px; border:3px solid var(--secondary-color); border-radius:10px; box-shadow:0 0 20px rgba(77, 238, 234, 0.3);">
                        </div>
                    </div>
                `
            }
        ]
    },
    {
        id: 11, // Nuevo ID
        title: "Escalabilidad",
        icon: "🌍",
        content: `
            <p>GIGA trasciende a Protección Civil. Su arquitectura abstracta permite gestion de turnos en:</p>
            <ul>
                <li><strong>Salud:</strong> Guardias médicas y cronogramas hospitalarios.</li>
                <li><strong>Industria:</strong> Turnos rotativos en fábricas 24/7.</li>
                <li><strong>Seguridad:</strong> Despliegue territorial (Policía/Bomberos).</li>
            </ul>
        `
    },
    {
        id: 12, // Nuevo ID
        title: "Futuro",
        icon: "🔮",
        content: `
            <p>Roadmap de evolución tecnológica (GIGA 2.0):</p>
            <ul>
                <li><strong>Biometría Real (WebAuthn):</strong> Uso de huella/rostro del celular para validar identidad física.</li>
                <li><strong>Geofencing:</strong> Validación de ubicación GPS para guardias de campo.</li>
                <li><strong>Modo Offline (PWA):</strong> Operatividad sin conexión para zonas de emergencia.</li>
            </ul>
        `
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
                <div style="background:#333; padding:20px; text-align:center; border-radius:10px; margin-top:20px;">
                    <em>[Espacio para Capturas de Excel Viejos]</em>
                </div>
            `
        },
        {
            id: "solucion",
            title: "La Solución",
            icon: "🌐",
            content: `
                <p>Desarrollamos una plataforma web integral:</p>
                <ul>
                    <li><strong>Centralizada:</strong> Una única fuente de verdad.</li>
                    <li><strong>Accesible:</strong> Desde PC, Tablets y Móviles.</li>
                    <li><strong>Transparente:</strong> El agente ve sus horas en tiempo real.</li>
                    <li><strong>Segura:</strong> Auditoría completa de cada movimiento.</li>
                </ul>
            `
        }
    ]
};

// ================= LÓGICA 3D Y ORBITAL =================
const universe = document.getElementById('universe');
const orbitRing = document.getElementById('orbitRing');
const centerObject = document.getElementById('centerObject');
const overlayContainer = document.getElementById('overlayContainer');

// Variable dinámica para el radio
let orbitRadius = 550;
let currentRotation = 0;
let targetRotation = 0;
let isPaused = false;

// Crear Tarjetas cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    updateOrbitRadius(); // Calcular radio inicial
    initializeApp();
    window.addEventListener('resize', updateOrbitRadius); // Recalcular al redimensionar
});

function updateOrbitRadius() {
    const width = window.innerWidth;
    if (width <= 480) {
        orbitRadius = 170;
    } else if (width <= 768) {
        orbitRadius = 300;
    } else if (width <= 1024) {
        orbitRadius = 400;
    } else {
        orbitRadius = 550;
    }
}

function initializeApp() {
    // Crear Tarjetas
    slides.forEach((slide, index) => {
        const card = document.createElement('div');
        card.className = 'orbit-card';

        // Ángulo: Distribuir uniformemente en 360 grados
        const angle = (360 / slides.length) * index;
        card.dataset.angle = angle;
        card.dataset.id = index;

        // HTML Interno
        card.innerHTML = `
            <div class="card-icon">${slide.icon}</div>
            <div class="card-label">${slide.title}</div>
        `;

        // Click en tarjeta
        card.addEventListener('click', (e) => {
            e.stopPropagation();
            openCard(card, slide);
        });

        // Touch end para evitar que el drag dispare el click
        card.addEventListener('touchend', (e) => {
            if (!isDragging) {
                e.stopPropagation();
                openCard(card, slide);
            }
        });

        orbitRing.appendChild(card);
    });

    // Iniciar animaciones
    animate();
    animateParticles();
}

// Función de Renderizado (Animation Loop)
function animate() {
    // Lerp para suavidad (Acercar current a target)
    currentRotation += (targetRotation - currentRotation) * 0.05;

    // Rotar el anillo
    orbitRing.style.transform = `rotateY(-${currentRotation}deg)`;

    // Actualizar tarjetas (Mantenerlas mirando al frente y escalar por profundidad)
    document.querySelectorAll('.orbit-card').forEach(card => {
        const baseAngle = parseFloat(card.dataset.angle);

        // Usamos Math.cos directamente con la diferencia de ángulos
        const angleDiff = (baseAngle - currentRotation);
        const radians = (angleDiff * Math.PI) / 180;

        // Depth: 1 (frente) a -1 (atrás)
        const depth = Math.cos(radians);

        const scale = 0.8 + (depth * 0.4); // Rango 0.4 a 1.2
        const opacity = 0.3 + ((depth + 1) / 2) * 0.7; // Rango 0.3 a 1.0
        const zIndex = Math.floor((depth + 1) * 100);

        card.style.transform = `
            rotateY(${baseAngle}deg) 
            translateZ(${orbitRadius}px) 
            scale(${scale})
        `;
        card.style.opacity = opacity;
        card.style.zIndex = zIndex;

        // Efecto visual extra: tarjetas de atrás más oscuras
        card.style.filter = `brightness(${0.5 + ((depth + 1) / 2) * 0.5})`;
    });

    requestAnimationFrame(animate);
}

// Control de Rotación con Mouse Wheel
window.addEventListener('wheel', (e) => {
    e.preventDefault(); // Evitar scroll de la página
    if (!isPaused) {
        // Reducimos la sensibilidad para evitar saltos muy grandes
        targetRotation += e.deltaY * 0.05;
    }
}, { passive: false }); // Permitir preventDefault

// Control de Rotación Arrastrando (Touch/Mouse)
let isDragging = false;
let startX = 0;
let startRotation = 0;

// Mouse Events
document.addEventListener('mousedown', (e) => {
    if (isPaused) return;
    isDragging = true;
    startX = e.clientX;
    startRotation = targetRotation;
});

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - startX;
    targetRotation = startRotation - deltaX * 0.5;
});

document.addEventListener('mouseup', () => isDragging = false);

// Touch Events (Móvil)
document.addEventListener('touchstart', (e) => {
    if (isPaused) return;
    isDragging = true;
    startX = e.touches[0].clientX;
    startRotation = targetRotation;
}, { passive: false });

document.addEventListener('touchmove', (e) => {
    if (!isDragging) return;
    e.preventDefault(); // Evitar scroll vertical nativo al arrastrar
    const deltaX = e.touches[0].clientX - startX;
    targetRotation = startRotation - deltaX * 0.8; // Sensibilidad aumentada para touch
}, { passive: false });

document.addEventListener('touchend', () => isDragging = false);


// ================= SISTEMA DE EXPANSIÓN (CLONES) =================

function openCard(cardElement, slideData) {
    if (isPaused) return; // Ya hay algo abierto
    isPaused = true;

    // 1. Rotar anillo para traer tarjeta al frente
    const angle = parseFloat(cardElement.dataset.angle);
    // Ajustar targetRotation para que coincida con este ángulo
    // Queremos que currentRotation = angle.
    // Pero targetRotation puede estar en 720, 1080... buscamos el múltiplo más cercano
    const cycle = Math.round(targetRotation / 360);
    targetRotation = (cycle * 360) + angle;

    // 2. Esperar un poco a que gire y luego expandir
    setTimeout(() => {
        createOverlay(cardElement, slideData, false);
    }, 300);
}

// Click en Núcleo
centerObject.addEventListener('click', (e) => {
    e.stopPropagation();
    if (isPaused) return;
    isPaused = true;

    createOverlay(centerObject, heroData, true);
});

function createOverlay(sourceElement, data, isHero) {
    // Efecto de alejamiento del fondo
    universe.classList.add('receded');

    // Obtener posición inicial para animación fluida
    const rect = sourceElement.getBoundingClientRect();

    // Crear el fondo oscuro clickeable
    const overlay = document.createElement('div');
    overlay.className = 'modal-backdrop';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 2000;
        display: flex;
        justify-content: center;
        align-items: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: auto; /* IMPORTANTE: Habilitar clicks */
    `;

    // Crear el clon (modal)
    // Crear el clon (modal)
    const clone = document.createElement('div');
    clone.className = `expanded-card ${isHero ? 'hero-mode' : ''}`;

    // Posición inicial (la del elemento original)
    clone.style.width = rect.width + 'px';
    clone.style.height = rect.height + 'px';
    clone.style.top = rect.top + 'px';
    clone.style.left = rect.left + 'px';
    clone.style.borderRadius = isHero ? '50%' : '15px'; // Núcleo es redondo
    clone.style.position = 'absolute';

    // Contenido diferente para Hero (con tabs) vs Slides normales
    if (isHero) {
        // Generar HTML de tabs
        const tabsHTML = data.tabs.map((tab, index) => `
            <button class="tab-btn ${index === 0 ? 'active' : ''}" data-tab="${tab.id}">
                <span class="tab-icon">${tab.icon}</span>
                <span class="tab-title">${tab.title}</span>
            </button>
        `).join('');

        const tabContentsHTML = data.tabs.map((tab, index) => `
            <div class="tab-content ${index === 0 ? 'active' : ''}" data-tab="${tab.id}">
                ${tab.content}
            </div>
        `).join('');

        clone.innerHTML = `
            <div class="expanded-content">
                <h2>${data.title}</h2>
                <p class="hero-subtitle">${data.subtitle}</p>
                <div class="tabs-container">
                    <div class="tabs-nav">
                        ${tabsHTML}
                    </div>
                    <div class="tabs-body">
                        ${tabContentsHTML}
                    </div>
                </div>
            </div>
            <div class="close-btn">&times;</div>
        `;
    } else {
        // Verificar si el slide tiene tabs
        if (data.tabs && data.tabs.length > 0) {
            // Generar HTML de tabs (igual que en hero)
            const tabsHTML = data.tabs.map((tab, index) => `
                <button class="tab-btn ${index === 0 ? 'active' : ''}" data-tab="${tab.id}">
                    <span class="tab-icon">${tab.icon}</span>
                    <span class="tab-title">${tab.title}</span>
                </button>
            `).join('');

            const tabContentsHTML = data.tabs.map((tab, index) => `
                <div class="tab-content ${index === 0 ? 'active' : ''}" data-tab="${tab.id}">
                    ${tab.content}
                </div>
            `).join('');

            clone.innerHTML = `
                <div class="expanded-content">
                    <h2>${data.title}</h2>
                    <div class="tabs-container">
                        <div class="tabs-nav">
                            ${tabsHTML}
                        </div>
                        <div class="tabs-body">
                            ${tabContentsHTML}
                        </div>
                    </div>
                </div>
                <div class="close-btn">&times;</div>
            `;
        } else {
            // Contenido normal para slides sin tabs
            clone.innerHTML = `
                <div class="expanded-content">
                    <h2>${data.title}</h2>
                    <div class="body-text">${data.content}</div>
                </div>
                <div class="close-btn">&times;</div>
            `;
        }
    }

    // Agregar modal al overlay
    overlay.appendChild(clone);
    overlayContainer.appendChild(overlay);

    // Forzar reflow para que la animación CSS funcione
    overlay.offsetHeight;

    // Activar expansión
    setTimeout(() => {
        overlay.style.opacity = '1';
        clone.classList.add('active');
    }, 10);

    // Botón Cerrar
    const closeBtn = clone.querySelector('.close-btn');
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeOverlay(overlay, clone, rect, isHero);
    });

    // Click en el fondo oscuro (backdrop) para cerrar
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeOverlay(overlay, clone, rect, isHero);
        }
    });

    // DETECCIÓN GEOMÉTRICA PARA EL NÚCLEO (CÍRCULO)
    // Si es Hero, el div es cuadrado pero se ve redondo.
    // Si clickean en las esquinas (fuera del radio), debe cerrarse.
    if (isHero) {
        clone.addEventListener('click', (e) => {
            // Coordenadas del click relativas al centro del modal
            const modalRect = clone.getBoundingClientRect();
            const centerX = modalRect.left + modalRect.width / 2;
            const centerY = modalRect.top + modalRect.height / 2;

            const clickX = e.clientX;
            const clickY = e.clientY;

            // Distancia del click al centro
            const distance = Math.sqrt(Math.pow(clickX - centerX, 2) + Math.pow(clickY - centerY, 2));

            // Radio del círculo (usamos el menor lado por seguridad, aunque debería ser cuadrado)
            const radius = modalRect.width / 2;

            // Si la distancia es mayor al radio, clickearon en la "esquina" invisible
            if (distance > radius) {
                closeOverlay(overlay, clone, rect, isHero);
            }
        });
    }

    // Si tiene tabs, agregar funcionalidad
    if (data.tabs && data.tabs.length > 0) {
        const tabButtons = clone.querySelectorAll('.tab-btn');
        const tabContents = clone.querySelectorAll('.tab-content');

        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tabId = btn.dataset.tab;

                tabButtons.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                btn.classList.add('active');
                const activeContent = clone.querySelector(`.tab-content[data-tab="${tabId}"]`);
                if (activeContent) {
                    activeContent.classList.add('active');
                }
            });
        });
    }
}

function closeOverlay(overlayElement, cloneElement, originalRect, isHero) {
    // Fade out overlay
    overlayElement.style.opacity = '0';

    // Desactivar clase active (vuelve a posición original)
    cloneElement.classList.remove('active');

    // Restaurar coords originales
    cloneElement.style.width = originalRect.width + 'px';
    cloneElement.style.height = originalRect.height + 'px';
    cloneElement.style.top = originalRect.top + 'px';
    cloneElement.style.left = originalRect.left + 'px';
    if (isHero) cloneElement.style.borderRadius = '50%';

    // Restaurar universo
    universe.classList.remove('receded');

    // Esperar animación y borrar
    setTimeout(() => {
        overlayElement.remove();
        isPaused = false;
    }, 600);
}

// ================= PARTÍCULAS (Copiado de mica.html) =================
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

const particles = [];
class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.size = Math.random() * 2;
        this.alpha = Math.random() * 0.5 + 0.1;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }
    draw() {
        ctx.fillStyle = `rgba(5, 217, 232, ${this.alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}
for (let i = 0; i < 100; i++) particles.push(new Particle());

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
        p.update();
        p.draw();
        // Conexiones simples
        particles.forEach(p2 => {
            const dx = p.x - p2.x;
            const dy = p.y - p2.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 100) {
                ctx.strokeStyle = `rgba(5, 217, 232, ${0.1 - dist / 1000})`;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        });
    });
    requestAnimationFrame(animateParticles);
}