// Variables y funciones específicas de Planes
let planesData = [];
function loadPlanes() {
    fetch('/api/planes')
        .then(response => response.json())
        .then(data => {
            planesData = data;
            renderPlanes(data);
        })
        .catch(error => console.error('Error:', error));
}
function renderPlanes(planes) {
    const tbody = document.getElementById('planesTableBody');
    tbody.innerHTML = '';
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
                alert('Plan guardado exitosamente');
                bootstrap.Modal.getInstance(document.getElementById('planModal')).hide();
                loadPlanes();
            }
        })
        .catch(error => console.error('Error:', error));
}
// Utilidad para mostrar badge de estado
function getEstadoPlanBadge(estado) {
    if (estado === 'Activo') return '<span class="badge bg-success">Activo</span>';
    if (estado === 'Vencido') return '<span class="badge bg-danger">Vencido</span>';
    if (estado === 'Próximo') return '<span class="badge bg-warning">Próximo</span>';
    return '<span class="badge bg-secondary">Desconocido</span>';
}
// Inicialización
document.addEventListener('DOMContentLoaded', loadPlanes);
