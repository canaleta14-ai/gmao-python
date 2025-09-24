// personal.js - JavaScript específico para el módulo de personal

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    console.log('Bootstrap está disponible');

    // Verificar elementos del colapso
    const filtroHeader = document.querySelector('[data-bs-toggle="collapse"]');
    const filtroCollapse = document.getElementById('filtrosPersonal');

    console.log('Filtro header:', filtroHeader);
    console.log('Filtro collapse:', filtroCollapse);

    if (filtroHeader && filtroCollapse) {
        console.log('Elementos del colapso encontrados correctamente');

        // Agregar event listeners para debug
        filtroHeader.addEventListener('click', function (e) {
            console.log('Click en header del filtro detectado');
        });

        filtroCollapse.addEventListener('show.bs.collapse', function () {
            console.log('Collapse showing...');
        });

        filtroCollapse.addEventListener('shown.bs.collapse', function () {
            console.log('Collapse shown');
        });

        filtroCollapse.addEventListener('hide.bs.collapse', function () {
            console.log('Collapse hiding...');
        });

        filtroCollapse.addEventListener('hidden.bs.collapse', function () {
            console.log('Collapse hidden');
        });
    } else {
        console.error('No se encontraron los elementos del colapso');
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