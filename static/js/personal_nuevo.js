// Personal Module - Gestión de empleados
let empleadosData = [];
let filteredData = [];
let paginaActual = 1;

// Reutilizar la función estándar de paginación
let pagination;

document.addEventListener('DOMContentLoaded', async function () {
    try {
        await cargarEmpleados();
        configurarEventHandlers();
    } catch (error) {
        console.error('Error en inicialización de personal:', error);
        mostrarError('Error al cargar el módulo de personal');
    }
});

// Funciones de API
async function cargarEmpleados() {
    try {
        const response = await fetch('/usuarios/api?per_page=999');
        if (!response.ok) throw new Error(`Error al cargar empleados: ${response.status}`);

        empleadosData = await response.json();
        filteredData = [...empleadosData];

        // Inicializar paginación usando la función estándar
        if (typeof createPagination === 'function') {
            pagination = createPagination(filteredData.length, 10);
            actualizarVistaEmpleados();
        } else {
            console.error('createPagination no está disponible');
            mostrarError('Error: Sistema de paginación no disponible');
        }
    } catch (error) {
        console.error('Error cargando empleados:', error);
        mostrarError('Error al cargar los empleados');
    }
}

function actualizarVistaEmpleados() {
    const container = document.getElementById('empleados-tbody');
    if (!container) {
        console.error('Container empleados-tbody no encontrado');
        return;
    }

    const inicio = (pagination.currentPage - 1) * pagination.itemsPerPage;
    const fin = inicio + pagination.itemsPerPage;
    const empleadosPagina = filteredData.slice(inicio, fin);

    container.innerHTML = '';

    if (empleadosPagina.length === 0) {
        container.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="fas fa-users"></i> No se encontraron empleados
                </td>
            </tr>
        `;
        return;
    }

    empleadosPagina.forEach(empleado => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>${empleado.nombre}</td>
            <td>${empleado.email}</td>
            <td>${empleado.rol || 'Sin rol'}</td>
            <td>
                <span class="badge ${empleado.activo ? 'bg-success' : 'bg-secondary'}">
                    ${empleado.activo ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editarEmpleado(${empleado.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarEmpleado(${empleado.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        container.appendChild(fila);
    });

    actualizarControlPaginacion();
}

function actualizarControlPaginacion() {
    const paginationContainer = document.getElementById('personal-pagination');
    if (!paginationContainer || !pagination) return;

    // Usar el sistema de paginación estándar
    pagination.totalItems = filteredData.length;
    pagination.totalPages = Math.ceil(pagination.totalItems / pagination.itemsPerPage);

    let paginationHTML = '';

    // Botón anterior
    if (pagination.currentPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <button class="page-link" onclick="cambiarPagina(${pagination.currentPage - 1})">
                    <i class="fas fa-chevron-left"></i>
                </button>
            </li>
        `;
    }

    // Números de página
    const maxPaginas = 5;
    let inicio = Math.max(1, pagination.currentPage - Math.floor(maxPaginas / 2));
    let fin = Math.min(pagination.totalPages, inicio + maxPaginas - 1);

    if (fin - inicio + 1 < maxPaginas) {
        inicio = Math.max(1, fin - maxPaginas + 1);
    }

    for (let i = inicio; i <= fin; i++) {
        paginationHTML += `
            <li class="page-item ${i === pagination.currentPage ? 'active' : ''}">
                <button class="page-link" onclick="cambiarPagina(${i})">${i}</button>
            </li>
        `;
    }

    // Botón siguiente
    if (pagination.currentPage < pagination.totalPages) {
        paginationHTML += `
            <li class="page-item">
                <button class="page-link" onclick="cambiarPagina(${pagination.currentPage + 1})">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </li>
        `;
    }

    paginationContainer.innerHTML = paginationHTML;

    // Actualizar información de paginación
    const info = document.getElementById('personal-pagination-info');
    if (info) {
        const desde = (pagination.currentPage - 1) * pagination.itemsPerPage + 1;
        const hasta = Math.min(pagination.currentPage * pagination.itemsPerPage, pagination.totalItems);
        info.textContent = `Mostrando ${desde}-${hasta} de ${pagination.totalItems} empleados`;
    }
}

// Función de cambio de página compatible con el sistema estándar
function cambiarPagina(nuevaPagina) {
    if (nuevaPagina >= 1 && nuevaPagina <= pagination.totalPages) {
        pagination.currentPage = nuevaPagina;
        actualizarVistaEmpleados();
    }
}

// Event Handlers
function configurarEventHandlers() {
    // Búsqueda en tiempo real
    const searchInput = document.getElementById('search-empleados');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filtrarEmpleados, 300));
    }

    // Filtros
    const filtroRol = document.getElementById('filtro-rol');
    if (filtroRol) {
        filtroRol.addEventListener('change', filtrarEmpleados);
    }

    const filtroEstado = document.getElementById('filtro-estado');
    if (filtroEstado) {
        filtroEstado.addEventListener('change', filtrarEmpleados);
    }

    // Botón nuevo empleado
    const btnNuevo = document.getElementById('btn-nuevo-empleado');
    if (btnNuevo) {
        btnNuevo.addEventListener('click', () => {
            // Abrir modal o redirigir a formulario
            window.location.href = '/personal/nuevo';
        });
    }

    // Exportar CSV
    const btnExportarCSV = document.getElementById('btn-exportar-csv-empleados');
    if (btnExportarCSV) {
        btnExportarCSV.addEventListener('click', exportarCSVPersonal);
    }
}

// Funciones de filtrado
function filtrarEmpleados() {
    const searchTerm = document.getElementById('search-empleados')?.value?.toLowerCase() || '';
    const filtroRol = document.getElementById('filtro-rol')?.value || '';
    const filtroEstado = document.getElementById('filtro-estado')?.value || '';

    filteredData = empleadosData.filter(empleado => {
        const coincideSearch = !searchTerm ||
            empleado.nombre.toLowerCase().includes(searchTerm) ||
            empleado.email.toLowerCase().includes(searchTerm);

        const coincideRol = !filtroRol || empleado.rol === filtroRol;
        const coincideEstado = !filtroEstado ||
            (filtroEstado === 'activo' ? empleado.activo : !empleado.activo);

        return coincideSearch && coincideRol && coincideEstado;
    });

    // Resetear paginación
    pagination.currentPage = 1;
    pagination.totalItems = filteredData.length;
    pagination.totalPages = Math.ceil(pagination.totalItems / pagination.itemsPerPage);

    actualizarVistaEmpleados();
}

// Funciones de empleados
async function editarEmpleado(id) {
    window.location.href = `/personal/editar/${id}`;
}

async function eliminarEmpleado(id) {
    if (!confirm('¿Está seguro de que desea eliminar este empleado?')) {
        return;
    }

    try {
        const response = await fetch(`/usuarios/api/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            mostrarMensaje('Empleado eliminado correctamente', 'success');
            await cargarEmpleados();
        } else {
            mostrarMensaje('Error al eliminar el empleado', 'error');
        }
    } catch (error) {
        console.error('Error eliminando empleado:', error);
        mostrarMensaje('Error al eliminar el empleado', 'error');
    }
}

// Exportar CSV usando el sistema unificado
async function exportarCSVPersonal() {
    try {
        // Mostrar mensaje de descarga
        if (typeof mostrarMensaje === 'function') {
            mostrarMensaje('Preparando archivo CSV para descarga...', 'info');
        }

        // Usar la función unificada de descarga CSV
        if (typeof descargarCSVMejorado === 'function') {
            const headers = ['Nombre', 'Email', 'Rol', 'Estado', 'Fecha Registro'];
            const csvData = filteredData.map(empleado => [
                empleado.nombre,
                empleado.email,
                empleado.rol || 'Sin rol',
                empleado.activo ? 'Activo' : 'Inactivo',
                empleado.fecha_registro ? new Date(empleado.fecha_registro).toLocaleDateString() : 'N/A'
            ]);

            descargarCSVMejorado(csvData, headers, 'empleados');
        } else {
            // Fallback a descarga tradicional
            const url = '/personal/exportar-csv';
            const a = document.createElement('a');
            a.href = url;
            a.download = 'empleados.csv';
            a.click();
        }
    } catch (error) {
        console.error('Error exportando CSV:', error);
        if (typeof mostrarMensaje === 'function') {
            mostrarMensaje('Error al exportar CSV', 'error');
        }
    }
}

// Utilidades
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function mostrarError(mensaje) {
    console.error(mensaje);
    if (typeof mostrarMensaje === 'function') {
        mostrarMensaje(mensaje, 'error');
    } else {
        alert(mensaje);
    }
}