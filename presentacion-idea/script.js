// ===========================================
// FUNCIONALIDAD JAVASCRIPT
// ===========================================

// 1. Manejo de Modales (Abrir/Cerrar)
function openModal(id) {
    // Muestra el overlay (fondo gris claro semi-transparente)
    document.getElementById(id + '-overlay').style.display = 'flex';
    // Bloquea el scroll del cuerpo principal mientras el modal esté abierto
    document.body.style.overflow = 'hidden'; 
}

function closeModal(id) {
    // Oculta el overlay
    document.getElementById(id + '-overlay').style.display = 'none';
    // Restaura el scroll
    document.body.style.overflow = 'auto';
}


// 2. Lógica del Scroll Snapping (Resaltar Navegación Lateral)

document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.querySelector('.timeline-container');
    const sections = document.querySelectorAll('.section-item');
    const navLinks = document.querySelectorAll('nav a');

    // Función para determinar qué sección está más visible
    const updateActiveLink = () => {
        let activeIndex = 0;
        
        // Calcular la posición central del viewport
        const viewportCenter = window.innerHeight / 2;

        sections.forEach((section, index) => {
            // Obtener la posición de la sección relativa al viewport
            const rect = section.getBoundingClientRect();
            
            // Si el centro de la sección está cerca del centro del viewport, activarla
            if (rect.top <= viewportCenter && rect.bottom >= viewportCenter) {
                activeIndex = index;
            }
        });

        // Eliminar 'active' de todos los enlaces
        navLinks.forEach(link => link.classList.remove('active'));

        // Añadir 'active' al enlace correspondiente
        if (navLinks[activeIndex]) {
            navLinks[activeIndex].classList.add('active');
        }
    };
    
    // Escuchar eventos de scroll en el contenedor principal
    mainContainer.addEventListener('scroll', updateActiveLink);
    
    // Inicializar el enlace activo al cargar
    updateActiveLink();
});

// 3. Manejo de Clicks en la Navegación (Scroll suave)
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        document.querySelector(targetId).scrollIntoView({
            behavior: 'smooth'
        });
    });
});