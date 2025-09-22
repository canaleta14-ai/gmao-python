// Variables y funciones específicas de Planes
let planesData = [];
let paginacionPlanes;

// Inicializar paginación
document.addEventListener('DOMContentLoaded', function () {
    // Configurar paginación
    paginacionPlanes = new Pagination('paginacion-planes', cargarPlanes, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true,
        pageSizes: [10, 25, 50, 100]
    });

    // Cargar datos iniciales
    cargarPlanes(1);

    // Configurar búsqueda
    setupPlanesSearch();
});

function cargarPlanes(page = 1, per_page = null) {
    if (per_page) {
        paginacionPlanes.setPerPage(per_page);
    }

    const params = new URLSearchParams({
        page: page,
        per_page: paginacionPlanes.perPage
    });

    // Agregar filtros de búsqueda si existen
    const searchInput = document.getElementById('search-planes');
    if (searchInput && searchInput.value.trim()) {
        params.append('q', searchInput.value.trim());
    }

    fetch(`/planes/api?${params}`)
        .then(response => response.json())
        .then(data => {
            planesData = data.items || data;
            renderPlanes(data.items || data);

            // Renderizar paginación si hay datos paginados
            if (data.page && data.per_page && data.total) {
                paginacionPlanes.render(data.page, data.per_page, data.total);
            }
        })
        .catch(error => {
            console.error('Error cargando planes:', error);
            showNotificationToast('Error al cargar planes de mantenimiento', 'error');
        });
}

// Función legacy para compatibilidad
function loadPlanes() {
    cargarPlanes(1);
}
function renderPlanes(planes) {
    const tbody = document.getElementById('planesTableBody');
    if (!tbody) {
        console.error('Table body not found');
        return;
    }

    tbody.innerHTML = '';

    if (!planes || planes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-calendar-check fs-1 d-block mb-2"></i>
                    No se encontraron planes de mantenimiento
                </td>
            </tr>
        `;
        return;
    }

    planes.forEach(plan => {
        tbody.innerHTML += `
            <tr>
                <td>${plan.codigo}</td>
                <td>${plan.nombre}</td>
                <td>${plan.equipo}</td>
                <td>${plan.frecuencia}</td>
                <td>${plan.ultima_ejecucion || 'N/A'}</td>
                <td>${plan.proxima_ejecucion || 'N/A'}</td>
                <td>${getEstadoPlanBadge(plan.estado)}</td>
                <td>
                    <button class="btn btn-sm btn-info" title="Ver detalles" onclick="viewPlan(${plan.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" title="Editar" onclick="editPlan(${plan.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}
function openPlanModal() {
    document.getElementById('formPlan').reset();
    new bootstrap.Modal(document.getElementById('planModal')).show();
}
function guardarPlan() {
    const form = document.getElementById('formPlan');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    fetch('/api/planes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showNotificationToast('Plan guardado exitosamente', 'success');
                bootstrap.Modal.getInstance(document.getElementById('planModal')).hide();
                cargarPlanes(1); // Recargar datos con paginación
            } else {
                showNotificationToast('Error al guardar el plan', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotificationToast('Error al guardar el plan', 'error');
        });
}

// Función de búsqueda con debounce
function setupPlanesSearch() {
    const searchInput = document.getElementById('search-planes');
    if (!searchInput) return;

    let debounceTimer;
    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            cargarPlanes(1);
        }, 300);
    });
}

// Función toast para notificaciones
function mostrarToast(mensaje, tipo = 'info') {
    showNotificationToast(mensaje, tipo);
}
// Utilidad para mostrar badge de estado
function getEstadoPlanBadge(estado) {
    if (estado === 'Activo') return '<span class="badge bg-success">Activo</span>';
    if (estado === 'Vencido') return '<span class="badge bg-danger">Vencido</span>';
    if (estado === 'Próximo') return '<span class="badge bg-warning">Próximo</span>';
    return '<span class="badge bg-secondary">Desconocido</span>';
}
// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    // Configurar paginación
    paginacionPlanes = new Pagination('paginacion-planes', cargarPlanes, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true,
        pageSizes: [10, 25, 50, 100]
    });

    // Cargar datos iniciales
    cargarPlanes(1);

    // Configurar búsqueda
    setupPlanesSearch();
});
