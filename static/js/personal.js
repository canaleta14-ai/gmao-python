// personal.js - JavaScript específico para el módulo de personal

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Asegurar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Inicializar collapse para filtros
    const filtrosPersonal = document.getElementById('filtrosPersonal');
    if (filtrosPersonal) {
        const collapse = new bootstrap.Collapse(filtrosPersonal, {
            toggle: false // No abrir automáticamente
        });
        console.log('Collapse inicializado para filtrosPersonal');
    } else {
        console.error('Elemento filtrosPersonal no encontrado');
    }

    // Verificar que el header tiene el data-bs-toggle
    const filtrosHeader = document.querySelector('.filtros-header[data-bs-target="#filtrosPersonal"]');
    if (filtrosHeader) {
        console.log('Header de filtros encontrado');

        // Agregar event listener adicional por si acaso
        filtrosHeader.addEventListener('click', function (e) {
            console.log('Click en header de filtros');
            const target = document.querySelector(this.getAttribute('data-bs-target'));
            if (target) {
                const bsCollapse = bootstrap.Collapse.getOrCreateInstance(target);
                bsCollapse.toggle();
            }
        });
    } else {
        console.error('Header de filtros no encontrado');
    }
});

// Función para limpiar filtros
function limpiarFiltrosPersonal() {
    console.log('Limpiando filtros de personal');
    document.getElementById('filtros-personal-form').reset();
}