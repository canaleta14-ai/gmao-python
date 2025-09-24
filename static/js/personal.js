// personal.js - JavaScript específico para el módulo de personal

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Encontrar elementos del colapso para mejorar UX
    const filtroHeader = document.querySelector('[data-bs-toggle="collapse"]');
    const filtroCollapse = document.getElementById('filtrosPersonal');

    if (filtroHeader && filtroCollapse) {
        // Asegurar que inicie colapsado
        if (!filtroCollapse.classList.contains('show')) {
            filtroHeader.classList.add('collapsed');
            filtroHeader.setAttribute('aria-expanded', 'false');
        }

        // Mejorar la indicación visual del estado
        filtroCollapse.addEventListener('show.bs.collapse', function () {
            filtroHeader.classList.remove('collapsed');
        });

        filtroCollapse.addEventListener('hide.bs.collapse', function () {
            filtroHeader.classList.add('collapsed');
        });
    }
});

// Función para limpiar filtros
function limpiarFiltrosPersonal() {
    console.log('Limpiando filtros de personal');
    const form = document.getElementById('filtros-personal-form');
    if (form) {
        form.reset();
    }
}