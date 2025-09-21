// Variables y funciones específicas de Inventario
let inventarioData = [];
function loadInventario() {
    fetch('/api/inventario')
        .then(response => response.json())
        .then(data => {
            inventarioData = data;
            renderInventario(data);
            updateInventarioStats(data);
        })
        .catch(error => console.error('Error:', error));
}
function renderInventario(items) {
    const tbody = document.getElementById('inventarioTableBody');
    tbody.innerHTML = '';
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
    document.getElementById('total-items').textContent = items.length;
    // Aquí puedes calcular y actualizar el valor total, stock bajo, sin stock, etc.
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
document.addEventListener('DOMContentLoaded', loadInventario);
