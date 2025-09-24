// activos.js - JavaScript específico para el módulo de activos

document.addEventListener('DOMContentLoaded', function () {
    console.log('Módulo Activos cargado');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Encontrar elementos del colapso para mejorar UX
    const filtroHeader = document.querySelector('[data-bs-toggle="collapse"]');
    const filtroCollapse = document.getElementById('filtrosActivos');

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
    setupFormActivo();
    setupFiltrosActivos();
    actualizarEstadisticas();
});

// Función para limpiar filtros
function limpiarFiltrosActivos() {
    console.log('Limpiando filtros de activos');
    const form = document.getElementById('filtros-activos-form');
    if (form) {
        form.reset();
        filtrarTablaActivos(); // Recargar tabla completa
    }
}

// Función para manejar el formulario de activos
function setupFormActivo() {
    const form = document.getElementById('form-activo');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Obtener datos del formulario
            const data = {
                codigo: document.getElementById('codigo').value,
                nombre: document.getElementById('nombre').value,
                descripcion: document.getElementById('descripcion').value,
                departamento: document.getElementById('departamento_modal').value,
                tipo: document.getElementById('tipo_modal').value,
                marca: document.getElementById('marca').value,
                modelo: document.getElementById('modelo').value,
                numero_serie: document.getElementById('numero_serie').value,
                fecha_adquisicion: document.getElementById('fecha_adquisicion').value,
                estado: document.getElementById('estado_modal').value,
                valor_adquisicion: document.getElementById('valor_adquisicion').value
            };

            console.log('Datos del nuevo activo:', data);

            // Aquí iría la lógica para enviar al servidor
            // Por ahora solo mostramos un mensaje
            alert('Activo guardado correctamente (demo)');

            // Cerrar modal y limpiar formulario
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalActivo'));
            if (modal) {
                modal.hide();
            }
            form.reset();

            // Recargar tabla (en implementación real)
            // cargarTablaActivos();
        });
    }
}

// Función para manejar filtros en tiempo real
function setupFiltrosActivos() {
    const filtroBuscar = document.getElementById('buscar');
    const filtroDepartamento = document.getElementById('departamento');
    const filtroEstado = document.getElementById('estado');
    const filtroTipo = document.getElementById('tipo');

    [filtroBuscar, filtroDepartamento, filtroEstado, filtroTipo].forEach(filtro => {
        if (filtro) {
            filtro.addEventListener('input', function () {
                filtrarTablaActivos();
            });
            filtro.addEventListener('change', function () {
                filtrarTablaActivos();
            });
        }
    });
}

// Función para filtrar la tabla de activos
function filtrarTablaActivos() {
    const buscarFiltro = document.getElementById('buscar').value.toLowerCase();
    const departamentoFiltro = document.getElementById('departamento').value.toLowerCase();
    const estadoFiltro = document.getElementById('estado').value.toLowerCase();
    const tipoFiltro = document.getElementById('tipo').value.toLowerCase();

    const filas = document.querySelectorAll('#tbody-activos tr');

    filas.forEach(fila => {
        const codigo = fila.cells[0].textContent.toLowerCase();
        const nombre = fila.cells[1].textContent.toLowerCase();
        const departamento = fila.cells[2].textContent.toLowerCase();
        const tipo = fila.cells[3].textContent.toLowerCase();
        const estado = fila.cells[4].textContent.toLowerCase();

        const coincideBuscar = !buscarFiltro ||
            codigo.includes(buscarFiltro) ||
            nombre.includes(buscarFiltro);
        const coincideDepartamento = !departamentoFiltro || departamento.includes(departamentoFiltro);
        const coincideEstado = !estadoFiltro || estado.includes(estadoFiltro);
        const coincideTipo = !tipoFiltro || tipo.includes(tipoFiltro);

        if (coincideBuscar && coincideDepartamento && coincideEstado && coincideTipo) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });

    // Actualizar contador de resultados
    const filasVisibles = document.querySelectorAll('#tbody-activos tr:not([style*="display: none"])');
    console.log(`Mostrando ${filasVisibles.length} activos de ${filas.length} total`);

    // Actualizar estadísticas
    actualizarEstadisticas();
}

// Función para actualizar estadísticas
function actualizarEstadisticas() {
    const filas = document.querySelectorAll('#tbody-activos tr:not([style*="display: none"])');
    let operativos = 0;
    let mantenimiento = 0;

    filas.forEach(fila => {
        const estadoTexto = fila.cells[4].textContent.toLowerCase();
        if (estadoTexto.includes('operativo')) {
            operativos++;
        } else if (estadoTexto.includes('mantención') || estadoTexto.includes('mantenimiento')) {
            mantenimiento++;
        }
    });

    // Actualizar contadores en las cards
    const totalElement = document.getElementById('total-activos');
    const operativosElement = document.getElementById('activos-operativos');
    const mantenimientoElement = document.getElementById('activos-mantenimiento');

    if (totalElement) totalElement.textContent = filas.length;
    if (operativosElement) operativosElement.textContent = operativos;
    if (mantenimientoElement) mantenimientoElement.textContent = mantenimiento;
}