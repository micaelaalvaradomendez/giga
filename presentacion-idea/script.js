// ================= LÓGICA 3D Y ORBITAL =================
// Este archivo requiere que data.js esté cargado previamente
// Contiene SOLO la funcionalidad de la presentación
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
    // Nota: Se removió el cierre por detección geométrica del núcleo circular
    // porque podía interferir con interacciones internas (tabs/botones).

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

    // Agregar funcionalidad de lightbox para imágenes dentro del modal/clon
    const modalImages = clone.querySelectorAll('img');
    if (modalImages.length > 0) {
        modalImages.forEach(img => {
            img.style.cursor = 'zoom-in';
            img.addEventListener('click', (e) => {
                e.stopPropagation();

                // Crear backdrop del lightbox
                const lb = document.createElement('div');
                lb.className = 'image-lightbox';

                // Imagen grande
                const large = document.createElement('img');
                large.src = img.src;
                large.alt = img.alt || '';

                // Botón cerrar
                const closeImg = document.createElement('div');
                closeImg.className = 'close-img';
                closeImg.innerHTML = '&times;';

                lb.appendChild(large);
                lb.appendChild(closeImg);
                document.body.appendChild(lb);

                // Función de cierre
                const removeLightbox = () => {
                    if (lb && lb.parentNode) lb.parentNode.removeChild(lb);
                    document.removeEventListener('keydown', escHandler);
                };

                // Cerrar al hacer click en backdrop o en el botón
                lb.addEventListener('click', (ev) => {
                    if (ev.target === lb || ev.target === closeImg) removeLightbox();
                });

                // Cerrar con ESC
                function escHandler(ev) {
                    if (ev.key === 'Escape') removeLightbox();
                }
                document.addEventListener('keydown', escHandler);
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