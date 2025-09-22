// Variables y funciones específicas de Inventario
let inventarioData = [];
let paginacionInventario;

// Inicializar paginación
document.addEventListener('DOMContentLoaded', function () {
    // Configurar paginación
    paginacionInventario = new Pagination('paginacion-inventario', cargarInventario, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true,
        pageSizes: [10, 25, 50, 100]
    });

    // Cargar datos iniciales
    cargarInventario(1);
});

function cargarInventario(page = 1, per_page = null) {
    if (per_page) {
        paginacionInventario.setPerPage(per_page);
    }

    const params = new URLSearchParams({
        page: page,
        per_page: paginacionInventario.perPage
    });

    // Agregar filtros de búsqueda si existen
    const searchInput = document.getElementById('search-inventario');
    if (searchInput && searchInput.value.trim()) {
        params.append('q', searchInput.value.trim());
    }

    fetch(`/api/inventario?${params}`)
        .then(response => response.json())
        .then(data => {
            inventarioData = data.items || data;
            renderInventario(data.items || data);
            updateInventarioStats(data.items || data);

            // Renderizar paginación si hay datos paginados
            if (data.page && data.per_page && data.total) {
                paginacionInventario.render(data.page, data.per_page, data.total);
            }
        })
        .catch(error => {
            console.error('Error cargando inventario:', error);
            showNotificationToast('Error al cargar inventario', 'error');
        });
}

// Función legacy para compatibilidad
function loadInventario() {
    cargarInventario(1);
}
function renderInventario(items) {
    const tbody = document.getElementById('inventarioTableBody');
    if (!tbody) {
        console.error('Table body not found');
        return;
    }

    tbody.innerHTML = '';

    if (!items || items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    No se encontraron elementos en el inventario
                </td>
            </tr>
        `;
        return;
    }

    items.forEach(item => {
        tbody.innerHTML += `
            <tr>
                <td>${item.codigo}</td>
                <td>${item.descripcion}</td>
                <td>${item.categoria}</td>
                <td>${item.stock_actual}</td>
                <td>${item.stock_minimo}</td>
                <td>${item.ubicacion}</td>
                <td>${item.precio_unitario}</td>
                <td>${getEstadoInventarioBadge(item.estado)}</td>
                <td>
                    <button class="btn btn-sm btn-info" title="Ver detalles" onclick="viewItem(${item.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" title="Editar" onclick="editItem(${item.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}
function updateInventarioStats(items) {
    if (!items) return;

    // Actualizar estadísticas básicas
    const totalItems = document.getElementById('total-items');
    if (totalItems) {
        totalItems.textContent = items.length;
    }

    // Calcular estadísticas adicionales
    const disponibles = items.filter(item => item.estado === 'Disponible').length;
    const bajoStock = items.filter(item => item.estado === 'Bajo Stock').length;
    const sinStock = items.filter(item => item.estado === 'Sin Stock').length;

    // Actualizar elementos si existen
    const elemDisponibles = document.getElementById('items-disponibles');
    const elemBajoStock = document.getElementById('items-bajo-stock');
    const elemSinStock = document.getElementById('items-sin-stock');

    if (elemDisponibles) elemDisponibles.textContent = disponibles;
    if (elemBajoStock) elemBajoStock.textContent = bajoStock;
    if (elemSinStock) elemSinStock.textContent = sinStock;
}

// Función de búsqueda con debounce
function setupInventarioSearch() {
    const searchInput = document.getElementById('search-inventario');
    if (!searchInput) return;

    let debounceTimer;
    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            cargarInventario(1);
        }, 300);
    });
}

// Configurar búsqueda cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    setupInventarioSearch();
});

// Función toast para notificaciones
function mostrarToast(mensaje, tipo = 'info') {
    showNotificationToast(mensaje, tipo);
}
function openEntradaModal() { /* ... */ }
function openSalidaModal() { /* ... */ }
function openItemModal() { /* ... */ }
// Utilidad para mostrar badge de estado
function getEstadoInventarioBadge(estado) {
    if (estado === 'Disponible') return '<span class="badge bg-success">Disponible</span>';
    if (estado === 'Bajo Stock') return '<span class="badge bg-warning">Bajo Stock</span>';
    if (estado === 'Sin Stock') return '<span class="badge bg-danger">Sin Stock</span>';
    return '<span class="badge bg-secondary">Desconocido</span>';
}
// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    // Configurar paginación
    paginacionInventario = new Pagination('paginacion-inventario', cargarInventario, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true,
        pageSizes: [10, 25, 50, 100]
    });

    // Cargar datos iniciales
    cargarInventario(1);

    // Configurar búsqueda
    setupInventarioSearch();
});
