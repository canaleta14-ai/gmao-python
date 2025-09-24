// proveedores.js - JavaScript específico para el módulo de proveedores

document.addEventListener('DOMContentLoaded', function () {
    console.log('Módulo Proveedores cargado');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Encontrar elementos del colapso para mejorar UX
    const filtroHeader = document.querySelector('[data-bs-toggle="collapse"]');
    const filtroCollapse = document.getElementById('filtrosProveedores');

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

    // Inicializar funcionalidades adicionales
    setupFormProveedor();
    setupFiltrosProveedores();
    actualizarEstadisticas();
});

// Función para limpiar filtros
function limpiarFiltrosProveedores() {
    console.log('Limpiando filtros de proveedores');
    const form = document.getElementById('filtros-proveedores-form');
    if (form) {
        form.reset();
        filtrarTablaProveedores(); // Recargar tabla completa
    }
}

// Función para manejar el formulario de proveedores
function setupFormProveedor() {
    const form = document.getElementById('form-proveedor');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Obtener datos del formulario
            const data = {
                nombre_empresa: document.getElementById('nombre_empresa').value,
                nif: document.getElementById('nif').value,
                persona_contacto: document.getElementById('persona_contacto').value,
                email: document.getElementById('email').value,
                telefono: document.getElementById('telefono').value,
                categoria: document.getElementById('categoria_modal').value,
                direccion: document.getElementById('direccion').value,
                ciudad: document.getElementById('ciudad').value,
                codigo_postal: document.getElementById('codigo_postal').value,
                pais: document.getElementById('pais_modal').value
            };

            console.log('Datos del nuevo proveedor:', data);

            // Aquí iría la lógica para enviar al servidor
            // Por ahora solo mostramos un mensaje
            alert('Proveedor guardado correctamente (demo)');

            // Cerrar modal y limpiar formulario
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalProveedor'));
            if (modal) {
                modal.hide();
            }
            form.reset();
        });
    }
}

// Función para manejar filtros en tiempo real
function setupFiltrosProveedores() {
    const filtroBuscar = document.getElementById('buscar');
    const filtroCategoria = document.getElementById('categoria');
    const filtroEstado = document.getElementById('estado');
    const filtroPais = document.getElementById('pais');

    [filtroBuscar, filtroCategoria, filtroEstado, filtroPais].forEach(filtro => {
        if (filtro) {
            filtro.addEventListener('input', function () {
                filtrarTablaProveedores();
            });
            filtro.addEventListener('change', function () {
                filtrarTablaProveedores();
            });
        }
    });
}

// Función para filtrar la tabla de proveedores
function filtrarTablaProveedores() {
    const buscarFiltro = document.getElementById('buscar').value.toLowerCase();
    const categoriaFiltro = document.getElementById('categoria').value.toLowerCase();
    const estadoFiltro = document.getElementById('estado').value.toLowerCase();
    const paisFiltro = document.getElementById('pais').value.toLowerCase();

    const filas = document.querySelectorAll('#tbody-proveedores tr');

    filas.forEach(fila => {
        const proveedor = fila.cells[0].textContent.toLowerCase();
        const contacto = fila.cells[1].textContent.toLowerCase();
        const categoria = fila.cells[2].textContent.toLowerCase();
        const pais = fila.cells[3].textContent.toLowerCase();
        const estado = fila.cells[4].textContent.toLowerCase();

        const coincideBuscar = !buscarFiltro ||
            proveedor.includes(buscarFiltro) ||
            contacto.includes(buscarFiltro);
        const coincideCategoria = !categoriaFiltro || categoria.includes(categoriaFiltro);
        const coincideEstado = !estadoFiltro || estado.includes(estadoFiltro);
        const coincidePais = !paisFiltro || pais.includes(paisFiltro);

        if (coincideBuscar && coincideCategoria && coincideEstado && coincidePais) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });

    // Actualizar contador de resultados
    const filasVisibles = document.querySelectorAll('#tbody-proveedores tr:not([style*="display: none"])');
    console.log(`Mostrando ${filasVisibles.length} proveedores de ${filas.length} total`);

    // Actualizar estadísticas
    actualizarEstadisticas();
}

// Función para actualizar estadísticas
function actualizarEstadisticas() {
    const filas = document.querySelectorAll('#tbody-proveedores tr:not([style*="display: none"])');
    let activos = 0;
    let evaluacion = 0;

    filas.forEach(fila => {
        const estadoTexto = fila.cells[4].textContent.toLowerCase();
        if (estadoTexto.includes('activo')) {
            activos++;
        } else if (estadoTexto.includes('evaluación') || estadoTexto.includes('evaluacion')) {
            evaluacion++;
        }
    });

    // Actualizar contadores en las cards
    const totalElement = document.getElementById('total-proveedores');
    const activosElement = document.getElementById('proveedores-activos');
    const evaluacionElement = document.getElementById('proveedores-evaluacion');

    if (totalElement) totalElement.textContent = filas.length;
    if (activosElement) activosElement.textContent = activos;
    if (evaluacionElement) evaluacionElement.textContent = evaluacion;
}