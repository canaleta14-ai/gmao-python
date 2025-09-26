// personal.js - JavaScript específico para el módulo de personal

// Variables globales para paginación
let paginacionPersonal = null;
let paginaActualPersonal = 1;
let totalPaginasPersonal = 1;
let totalEmpleados = 0;

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Inicializar paginación
    inicializarPaginacionPersonal();

    // Encontrar elementos del colapso para mejorar UX
    const filtroHeader = document.querySelector('[data-bs-toggle="collapse"]');
    const filtroCollapse = document.getElementById('filtros-collapse');

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
    setupFormPersonal();
    setupFiltrosPersonal();
});

// Función para limpiar filtros
function limpiarFiltrosPersonal() {
    console.log('🧹 Limpiando filtros de personal');

    // Limpiar campos individuales
    document.getElementById('nombre').value = '';
    document.getElementById('departamento').value = '';
    document.getElementById('cargo').value = '';

    // Limpiar clases de filtrado
    const filas = document.querySelectorAll('#tbody-personal tr');
    filas.forEach(fila => {
        fila.classList.remove('filtrado-oculto');
    });

    // Re-renderizar paginación con todos los datos
    if (paginacionPersonal) {
        const elementosPorPagina = 10;
        const totalFilas = filas.length;

        paginaActualPersonal = 1;
        paginacionPersonal.render(paginaActualPersonal, elementosPorPagina, totalFilas);
    }

    // Actualizar vista
    actualizarVistaPersonal();
}// Función para manejar el formulario de personal
function setupFormPersonal() {
    const form = document.getElementById('form-personal');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Obtener datos del formulario
            const formData = new FormData(form);
            const data = {
                nombres: document.getElementById('nombres').value,
                apellidos: document.getElementById('apellidos').value,
                cedula: document.getElementById('cedula').value,
                email: document.getElementById('email').value,
                telefono: document.getElementById('telefono').value,
                fecha_ingreso: document.getElementById('fecha_ingreso').value,
                departamento: document.getElementById('departamento_modal').value,
                cargo: document.getElementById('cargo_modal').value,
                estado: document.getElementById('estado').value,
                salario: document.getElementById('salario').value
            };

            console.log('Datos del nuevo empleado:', data);

            // Aquí iría la lógica para enviar al servidor
            // Por ahora solo mostramos un mensaje
            alert('Empleado guardado correctamente (demo)');

            // Cerrar modal y limpiar formulario
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalPersonal'));
            if (modal) {
                modal.hide();
            }
            form.reset();
        });
    }
}

// Función para manejar filtros en tiempo real
function setupFiltrosPersonal() {
    const filtroNombre = document.getElementById('nombre');
    const filtroDepartamento = document.getElementById('departamento');
    const filtroCargo = document.getElementById('cargo');

    [filtroNombre, filtroDepartamento, filtroCargo].forEach(filtro => {
        if (filtro) {
            filtro.addEventListener('input', function () {
                filtrarTablaPersonal();
            });
        }
    });
}

// Función para inicializar la paginación de personal
function inicializarPaginacionPersonal() {
    console.log('🔧 Inicializando paginación de personal...');

    // Verificar que el módulo de paginación esté disponible
    if (typeof Pagination === 'undefined') {
        console.error('❌ Módulo de paginación no está disponible');
        return;
    }

    const container = document.getElementById('paginacion-personal');
    if (!container) {
        console.error('❌ Contenedor de paginación no encontrado');
        return;
    }

    try {
        // Configurar paginación con los datos actuales de la tabla
        const filas = document.querySelectorAll('#tbody-personal tr');
        totalEmpleados = filas.length;
        const elementosPorPagina = 10;
        totalPaginasPersonal = Math.ceil(totalEmpleados / elementosPorPagina);

        // Crear instancia de paginación usando el constructor correcto
        paginacionPersonal = new Pagination('paginacion-personal', function (page, perPage) {
            console.log(`📄 Cambiando a página ${page}`);
            paginaActualPersonal = page;
            actualizarVistaPersonal();
        }, {
            perPage: elementosPorPagina,
            maxVisiblePages: 5
        });

        // Renderizar la paginación inicial
        paginacionPersonal.render(paginaActualPersonal, elementosPorPagina, totalEmpleados);

        console.log(`✅ Paginación inicializada: ${totalPaginasPersonal} páginas, ${totalEmpleados} empleados`);

        // Actualizar vista inicial
        actualizarVistaPersonal();

    } catch (error) {
        console.error('❌ Error inicializando paginación:', error);
    }
}

// Función para actualizar la vista de empleados según la página
function actualizarVistaPersonal() {
    const elementosPorPagina = 10;
    const inicio = (paginaActualPersonal - 1) * elementosPorPagina;
    const fin = inicio + elementosPorPagina;

    const filas = document.querySelectorAll('#tbody-personal tr');

    // Ocultar todas las filas
    filas.forEach(fila => {
        fila.style.display = 'none';
    });

    // Mostrar solo las filas de la página actual
    for (let i = inicio; i < fin && i < filas.length; i++) {
        filas[i].style.display = '';
    }

    // Actualizar contador
    const filasVisibles = Math.min(elementosPorPagina, filas.length - inicio);
    document.getElementById('contador-empleados').textContent =
        `Mostrando ${filasVisibles} de ${filas.length} empleados (página ${paginaActualPersonal} de ${totalPaginasPersonal})`;

    console.log(`📊 Vista actualizada: página ${paginaActualPersonal}, mostrando filas ${inicio + 1} a ${Math.min(fin, filas.length)}`);
}

// Función para filtrar la tabla de personal
function filtrarTablaPersonal() {
    const nombreFiltro = document.getElementById('nombre').value.toLowerCase();
    const departamentoFiltro = document.getElementById('departamento').value.toLowerCase();
    const cargoFiltro = document.getElementById('cargo').value.toLowerCase();

    const filas = document.querySelectorAll('#tbody-personal tr');
    let filasVisibles = 0;

    filas.forEach(fila => {
        const nombre = fila.cells[1].textContent.toLowerCase();
        const departamento = fila.cells[2].textContent.toLowerCase();
        const cargo = fila.cells[3].textContent.toLowerCase();

        const coincideNombre = !nombreFiltro || nombre.includes(nombreFiltro);
        const coincideDepartamento = !departamentoFiltro || departamento.includes(departamentoFiltro);
        const coincideCargo = !cargoFiltro || cargo.includes(cargoFiltro);

        if (coincideNombre && coincideDepartamento && coincideCargo) {
            fila.style.display = '';
            fila.classList.remove('filtrado-oculto');
            filasVisibles++;
        } else {
            fila.style.display = 'none';
            fila.classList.add('filtrado-oculto');
        }
    });

    // Re-renderizar paginación con los resultados filtrados
    if (paginacionPersonal) {
        const elementosPorPagina = 10;
        paginaActualPersonal = 1; // Volver a la primera página

        // Re-renderizar paginación con nuevo total
        paginacionPersonal.render(paginaActualPersonal, elementosPorPagina, filasVisibles);

        // Actualizar vista
        actualizarVistaPersonalFiltrado();
    }

    console.log(`🔍 Filtros aplicados: ${filasVisibles} empleados de ${filas.length} total`);
}

// Función para actualizar la vista con filtros aplicados
function actualizarVistaPersonalFiltrado() {
    const elementosPorPagina = 10;
    const inicio = (paginaActualPersonal - 1) * elementosPorPagina;

    // Obtener solo las filas que no están ocultas por filtros
    const filasVisibles = Array.from(document.querySelectorAll('#tbody-personal tr:not(.filtrado-oculto)'));

    // Ocultar todas las filas primero
    document.querySelectorAll('#tbody-personal tr').forEach(fila => {
        if (!fila.classList.contains('filtrado-oculto')) {
            fila.style.display = 'none';
        }
    });

    // Mostrar solo las filas de la página actual
    const fin = inicio + elementosPorPagina;
    for (let i = inicio; i < fin && i < filasVisibles.length; i++) {
        filasVisibles[i].style.display = '';
    }

    // Actualizar contador
    const totalPaginasActual = Math.ceil(filasVisibles.length / elementosPorPagina);
    const filasEnPagina = Math.min(elementosPorPagina, filasVisibles.length - inicio);

    document.getElementById('contador-empleados').textContent =
        `Mostrando ${filasEnPagina} de ${filasVisibles.length} empleados${totalPaginasActual > 1 ? ` (página ${paginaActualPersonal} de ${totalPaginasActual})` : ''}`;
}// Función para exportar CSV
function exportarCSVPersonal() {
    console.log('Exportando datos de personal a CSV...');

    // Obtener datos de la tabla
    const tabla = document.getElementById('tabla-personal');
    const filas = tabla.querySelectorAll('tbody tr:not([style*="display: none"])');

    if (filas.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    // Preparar datos CSV
    let csvContent = 'ID,Nombre,Departamento,Cargo,Email,Telefono,Estado\n';

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        const id = celdas[0].textContent.trim();
        const nombre = celdas[1].querySelector('.fw-bold').textContent.trim();
        const departamento = celdas[2].querySelector('.badge').textContent.trim();
        const cargo = celdas[3].textContent.trim();

        // Extraer email y teléfono del contenido HTML
        const contactoDiv = celdas[4];
        const email = contactoDiv.querySelector('div:first-child').textContent.replace('📧', '').trim();
        const telefono = contactoDiv.querySelector('div:last-child').textContent.replace('📞', '').trim();

        const estado = celdas[5].querySelector('.badge').textContent.trim();

        csvContent += `"${id}","${nombre}","${departamento}","${cargo}","${email}","${telefono}","${estado}"\n`;
    });

    // Descargar archivo
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `personal_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}