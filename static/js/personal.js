// personal.js - JavaScript específico para el módulo de personal

// Variables globales
let paginacionPersonal = null;
let empleadosData = [];

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Inicializar módulo
    inicializarModuloPersonal();

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

// Función principal de inicialización
function inicializarModuloPersonal() {
    console.log('🚀 Inicializando módulo de personal...');

    // Cargar datos de empleados desde la tabla HTML existente
    cargarEmpleadosDesdeTabla();

    // Inicializar paginación usando el sistema estándar
    inicializarPaginacion();
}

// Cargar empleados desde la tabla HTML
function cargarEmpleadosDesdeTabla() {
    const filas = document.querySelectorAll('#tbody-personal tr');
    empleadosData = [];

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        if (celdas.length >= 6) {
            empleadosData.push({
                id: celdas[0].textContent.trim(),
                nombre: celdas[1].querySelector('.fw-bold')?.textContent.trim() || celdas[1].textContent.trim(),
                departamento: celdas[2].querySelector('.badge')?.textContent.trim() || celdas[2].textContent.trim(),
                cargo: celdas[3].textContent.trim(),
                email: celdas[4].querySelector('div:first-child')?.textContent.replace('📧', '').trim() || '',
                telefono: celdas[4].querySelector('div:last-child')?.textContent.replace('📞', '').trim() || '',
                estado: celdas[5].querySelector('.badge')?.textContent.trim() || celdas[5].textContent.trim(),
                elemento: fila
            });
        }
    });

    console.log(`📊 Cargados ${empleadosData.length} empleados`);
}

// Inicializar paginación estándar
function inicializarPaginacion() {
    console.log('🔧 Inicializando paginación estándar...');

    if (typeof createPagination === 'undefined') {
        console.error('❌ Función createPagination no disponible');
        return;
    }

    try {
        paginacionPersonal = createPagination('paginacion-personal', renderizarEmpleados, {
            perPage: 10,
            showInfo: true,
            showSizeSelector: false
        });

        console.log('✅ Paginación inicializada correctamente');

        // Cargar primera página
        renderizarEmpleados(1, 10);

    } catch (error) {
        console.error('❌ Error inicializando paginación:', error);
    }
}

// Renderizar empleados para una página específica
function renderizarEmpleados(page, perPage) {
    console.log(`📄 Renderizando página ${page} (${perPage} por página)`);

    const tbody = document.getElementById('tbody-personal');
    if (!tbody) {
        console.error('❌ No se encontró tbody-personal');
        return;
    }

    // Aplicar filtros si existen
    let empleadosFiltrados = aplicarFiltros();

    // Calcular paginación
    const totalEmpleados = empleadosFiltrados.length;
    const inicio = (page - 1) * perPage;
    const empleadosPagina = empleadosFiltrados.slice(inicio, inicio + perPage);

    // Limpiar tbody
    tbody.innerHTML = '';

    // Renderizar empleados de la página actual
    empleadosPagina.forEach(empleado => {
        tbody.appendChild(empleado.elemento.cloneNode(true));
    });

    // Actualizar paginación
    if (paginacionPersonal) {
        paginacionPersonal.updateData(totalEmpleados);
    }

    // Actualizar contador
    actualizarContador(empleadosPagina.length, totalEmpleados, page, Math.ceil(totalEmpleados / perPage));

    console.log(`✅ Renderizados ${empleadosPagina.length} empleados de ${totalEmpleados} total`);
}

// Aplicar filtros activos
function aplicarFiltros() {
    // Si no hay filtros activos, devolver todos los empleados
    const nombreFiltro = document.getElementById('nombre')?.value.toLowerCase() || '';
    const departamentoFiltro = document.getElementById('departamento')?.value.toLowerCase() || '';
    const cargoFiltro = document.getElementById('cargo')?.value.toLowerCase() || '';

    if (!nombreFiltro && !departamentoFiltro && !cargoFiltro) {
        return empleadosData;
    }

    return empleadosData.filter(empleado => {
        const cumpleNombre = !nombreFiltro || empleado.nombre.toLowerCase().includes(nombreFiltro);
        const cumpleDepartamento = !departamentoFiltro || empleado.departamento.toLowerCase().includes(departamentoFiltro);
        const cumpleCargo = !cargoFiltro || empleado.cargo.toLowerCase().includes(cargoFiltro);

        return cumpleNombre && cumpleDepartamento && cumpleCargo;
    });
}

// personal.js - JavaScript específico para el módulo de personal

// Variables globales
let paginacionPersonal = null;
let empleadosData = [];

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Inicializar módulo
    inicializarModuloPersonal();

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

// Función principal de inicialización
function inicializarModuloPersonal() {
    console.log('🚀 Inicializando módulo de personal...');

    // Cargar datos de empleados desde la tabla HTML existente
    cargarEmpleadosDesdeTabla();

    // Inicializar paginación usando el sistema estándar
    inicializarPaginacion();
}

// Cargar empleados desde la tabla HTML
function cargarEmpleadosDesdeTabla() {
    const filas = document.querySelectorAll('#tbody-personal tr');
    empleadosData = [];

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        if (celdas.length >= 6) {
            empleadosData.push({
                id: celdas[0].textContent.trim(),
                nombre: celdas[1].querySelector('.fw-bold')?.textContent.trim() || celdas[1].textContent.trim(),
                departamento: celdas[2].querySelector('.badge')?.textContent.trim() || celdas[2].textContent.trim(),
                cargo: celdas[3].textContent.trim(),
                email: celdas[4].querySelector('div:first-child')?.textContent.replace('📧', '').trim() || '',
                telefono: celdas[4].querySelector('div:last-child')?.textContent.replace('📞', '').trim() || '',
                estado: celdas[5].querySelector('.badge')?.textContent.trim() || celdas[5].textContent.trim(),
                elemento: fila.cloneNode(true) // Clonar para mantener estructura
            });
        }
    });

    console.log(`📊 Cargados ${empleadosData.length} empleados`);
}

// Inicializar paginación estándar
function inicializarPaginacion() {
    console.log('🔧 Inicializando paginación estándar...');

    if (typeof createPagination === 'undefined') {
        console.error('❌ Función createPagination no disponible');
        return;
    }

    try {
        paginacionPersonal = createPagination('paginacion-personal', renderizarEmpleados, {
            perPage: 10,
            showInfo: true,
            showSizeSelector: false
        });

        console.log('✅ Paginación inicializada correctamente');

        // Cargar primera página
        renderizarEmpleados(1, 10);

    } catch (error) {
        console.error('❌ Error inicializando paginación:', error);
    }
}

// Renderizar empleados para una página específica
function renderizarEmpleados(page, perPage) {
    console.log(`📄 Renderizando página ${page} (${perPage} por página)`);

    const tbody = document.getElementById('tbody-personal');
    if (!tbody) {
        console.error('❌ No se encontró tbody-personal');
        return;
    }

    // Aplicar filtros si existen
    let empleadosFiltrados = aplicarFiltros();

    // Calcular paginación
    const totalEmpleados = empleadosFiltrados.length;
    const inicio = (page - 1) * perPage;
    const empleadosPagina = empleadosFiltrados.slice(inicio, inicio + perPage);

    // Limpiar tbody
    tbody.innerHTML = '';

    // Renderizar empleados de la página actual
    empleadosPagina.forEach(empleado => {
        tbody.appendChild(empleado.elemento.cloneNode(true));
    });

    // Actualizar paginación
    if (paginacionPersonal) {
        paginacionPersonal.updateData(totalEmpleados);
    }

    // Actualizar contador
    actualizarContador(empleadosPagina.length, totalEmpleados, page, Math.ceil(totalEmpleados / perPage));

    console.log(`✅ Renderizados ${empleadosPagina.length} empleados de ${totalEmpleados} total`);
}

// Aplicar filtros activos
function aplicarFiltros() {
    // Si no hay filtros activos, devolver todos los empleados
    const nombreFiltro = document.getElementById('nombre')?.value.toLowerCase() || '';
    const departamentoFiltro = document.getElementById('departamento')?.value.toLowerCase() || '';
    const cargoFiltro = document.getElementById('cargo')?.value.toLowerCase() || '';

    if (!nombreFiltro && !departamentoFiltro && !cargoFiltro) {
        return empleadosData;
    }

    return empleadosData.filter(empleado => {
        const cumpleNombre = !nombreFiltro || empleado.nombre.toLowerCase().includes(nombreFiltro);
        const cumpleDepartamento = !departamentoFiltro || empleado.departamento.toLowerCase().includes(departamentoFiltro);
        const cumpleCargo = !cargoFiltro || empleado.cargo.toLowerCase().includes(cargoFiltro);

        return cumpleNombre && cumpleDepartamento && cumpleCargo;
    });
}

// Actualizar contador de empleados
function actualizarContador(empleadosPagina, totalEmpleados, paginaActual, totalPaginas) {
    const contador = document.getElementById('contador-empleados');
    if (contador) {
        contador.textContent =
            `Mostrando ${empleadosPagina} de ${totalEmpleados} empleados${totalPaginas > 1 ? ` (página ${paginaActual} de ${totalPaginas})` : ''}`;
    }
}

// Función para limpiar filtros
function limpiarFiltrosPersonal() {
    console.log('🧹 Limpiando filtros de personal');

    // Limpiar campos
    document.getElementById('nombre').value = '';
    document.getElementById('departamento').value = '';
    document.getElementById('cargo').value = '';

    // Re-renderizar primera página sin filtros
    renderizarEmpleados(1, 10);
}

// Función para manejar el formulario de personal
function setupFormPersonal() {
    const form = document.getElementById('form-personal');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Obtener datos del formulario
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
                // Re-renderizar desde la primera página cuando se aplican filtros
                renderizarEmpleados(1, 10);
            });
        }
    });
}

// Función para exportar CSV
function exportarCSVPersonal() {
    console.log('Exportando datos de personal a CSV...');

    try {
        // Obtener datos filtrados actuales
        const empleadosFiltrados = aplicarFiltros();

        if (empleadosFiltrados.length === 0) {
            alert('No hay datos para exportar');
            return;
        }

        // Preparar datos CSV
        let csvContent = 'ID,Nombre,Departamento,Cargo,Email,Telefono,Estado\n';

        empleadosFiltrados.forEach(empleado => {
            csvContent += `"${empleado.id}","${empleado.nombre}","${empleado.departamento}","${empleado.cargo}","${empleado.email}","${empleado.telefono}","${empleado.estado}"\n`;
        });

        // Descargar archivo
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        const nombreArchivo = `personal_${new Date().toISOString().split('T')[0]}.csv`;
        link.setAttribute('download', nombreArchivo);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();

        // Limpiar después de un delay
        setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 100);

        // Mostrar mensaje informativo apropiado
        if (typeof mostrarMensaje === 'function') {
            mostrarMensaje(`Descarga iniciada. Revise su carpeta de descargas para el archivo ${nombreArchivo}.`, 'info');
        }

    } catch (error) {
        console.error('Error al exportar CSV de personal:', error);
        if (typeof mostrarMensaje === 'function') {
            mostrarMensaje('Error al exportar archivo CSV', 'danger');
        } else {
            alert('Error al exportar archivo CSV');
        }
    }
}
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

    try {
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
        const nombreArchivo = `personal_${new Date().toISOString().split('T')[0]}.csv`;
        link.setAttribute('download', nombreArchivo);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();

        // Limpiar después de un delay
        setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 100);

        // Mostrar mensaje informativo apropiado
        if (typeof mostrarMensaje === 'function') {
            mostrarMensaje(`Descarga iniciada. Revise su carpeta de descargas para el archivo ${nombreArchivo}.`, 'info');
        }

    } catch (error) {
        console.error('Error al exportar CSV de personal:', error);
        if (typeof mostrarMensaje === 'function') {
            mostrarMensaje('Error al exportar archivo CSV', 'danger');
        } else {
            alert('Error al exportar archivo CSV');
        }
    }
}