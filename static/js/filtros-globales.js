/**
 * Sistema global de filtros colapsables
 * Proporciona funcionalidad consistente para todos los módulos del sistema GMAO
 */

document.addEventListener('DOMContentLoaded', function () {
    // Inicializar filtros colapsables en todas las páginas
    initFiltrosGlobales();
});

function initFiltrosGlobales() {
    const filtrosHeader = document.querySelector('.filtros-header');
    const filtrosCollapse = document.querySelector('#filtros-collapse');

    if (!filtrosHeader || !filtrosCollapse) return;

    // Recordar estado de filtros por página
    const currentPage = window.location.pathname;

    // NO aplicar lógica global para la página de personal (usuarios) - dejar que Bootstrap maneje todo
    if (currentPage === '/usuarios/') {
        return;
    }

    // Agregar indicador visual de colapso
    const icon = document.createElement('i');
    icon.className = 'fas fa-chevron-down ms-auto filtros-toggle-icon';
    filtrosHeader.appendChild(icon);

    const storageKey = `filtros_${currentPage}`;

    // Restaurar estado guardado
    const savedState = localStorage.getItem(storageKey);
    if (savedState === 'shown') {
        filtrosCollapse.classList.add('show');
        icon.style.transform = 'rotate(180deg)';
    }

    // Manejar eventos de colapso
    filtrosCollapse.addEventListener('show.bs.collapse', function () {
        icon.style.transform = 'rotate(180deg)';
        localStorage.setItem(storageKey, 'shown');
    });

    filtrosCollapse.addEventListener('hide.bs.collapse', function () {
        icon.style.transform = 'rotate(0deg)';
        localStorage.setItem(storageKey, 'hidden');
    });

    // Agregar contador de filtros activos
    addFiltrosCounter();

    // Monitorear cambios en filtros
    monitorFiltrosChanges();
}

function addFiltrosCounter() {
    const filtrosHeader = document.querySelector('.filtros-header h6');
    if (!filtrosHeader) return;

    const counter = document.createElement('span');
    counter.className = 'badge bg-primary ms-2 filtros-counter';
    counter.textContent = '0';
    counter.style.display = 'none';
    filtrosHeader.appendChild(counter);
}

function monitorFiltrosChanges() {
    const filtrosBody = document.querySelector('.filtros-body');
    if (!filtrosBody) return;

    // Monitorear inputs y selects
    const inputs = filtrosBody.querySelectorAll('input[type="text"], select');
    const checkboxes = filtrosBody.querySelectorAll('input[type="checkbox"]');

    function updateCounter() {
        let activeFilters = 0;

        // Contar inputs de texto con valor
        inputs.forEach(input => {
            if (input.value && input.value.trim() !== '' && input.value !== input.querySelector('option')?.value) {
                activeFilters++;
            }
        });

        // Contar checkboxes marcados
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                activeFilters++;
            }
        });

        // Actualizar contador visual
        const counter = document.querySelector('.filtros-counter');
        if (counter) {
            counter.textContent = activeFilters;
            counter.style.display = activeFilters > 0 ? 'inline-block' : 'none';
        }

        // Auto-expandir si hay filtros activos
        const filtrosCollapse = document.querySelector('#filtros-collapse');
        if (activeFilters > 0 && !filtrosCollapse.classList.contains('show')) {
            const bsCollapse = new bootstrap.Collapse(filtrosCollapse, { show: false });
            bsCollapse.show();
        }
    }

    // Agregar listeners
    [...inputs, ...checkboxes].forEach(element => {
        element.addEventListener('input', updateCounter);
        element.addEventListener('change', updateCounter);
    });

    // Actualizar contador inicial
    updateCounter();
}

/**
 * Función global para limpiar todos los filtros
 * Puede ser llamada desde cualquier módulo
 */
function limpiarFiltrosGlobal() {
    const filtrosBody = document.querySelector('.filtros-body');
    if (!filtrosBody) return;

    // Limpiar inputs de texto
    filtrosBody.querySelectorAll('input[type="text"]').forEach(input => {
        input.value = '';
    });

    // Resetear selects
    filtrosBody.querySelectorAll('select').forEach(select => {
        select.selectedIndex = 0;
    });

    // Desmarcar checkboxes
    filtrosBody.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });

    // Actualizar contador
    const counter = document.querySelector('.filtros-counter');
    if (counter) {
        counter.textContent = '0';
        counter.style.display = 'none';
    }

    // Colapsar filtros si no hay filtros activos
    const filtrosCollapse = document.querySelector('#filtros-collapse');
    if (filtrosCollapse && filtrosCollapse.classList.contains('show')) {
        const bsCollapse = new bootstrap.Collapse(filtrosCollapse, { show: false });
        bsCollapse.hide();
    }
}

/**
 * Función para exportar configuración de filtros
 * Útil para reportes y debugging
 */
function exportarConfiguracionFiltros() {
    const filtrosBody = document.querySelector('.filtros-body');
    if (!filtrosBody) return null;

    const config = {
        modulo: window.location.pathname,
        timestamp: new Date().toISOString(),
        filtros: {}
    };

    // Capturar valores de filtros
    filtrosBody.querySelectorAll('input, select').forEach(element => {
        if (element.id) {
            config.filtros[element.id] = {
                tipo: element.type || element.tagName.toLowerCase(),
                valor: element.value,
                marcado: element.checked || false
            };
        }
    });

    return config;
}