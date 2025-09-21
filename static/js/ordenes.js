// Gestión de Órdenes de Trabajo - JavaScript

// Variables globales
let ordenes = [];
let activos = [];
let tecnicos = [];
let ordenEditando = null;

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('Módulo de órdenes cargado');
    if (document.getElementById('modalOrden')) {
        console.log('Modal de orden encontrado, cargando datos...');
        cargarDatosIniciales();
    }
    cargarOrdenes();
});

// Cargar lista de órdenes
async function cargarOrdenes() {
    try {
        const response = await fetch('/ordenes/api');
        if (response.ok) {
            ordenes = await response.json();
            mostrarOrdenes();
            actualizarEstadisticas();
        } else {
            throw new Error('Error al cargar órdenes');
        }
    } catch (error) {
        console.error('Error cargando órdenes:', error);
        mostrarToast('Error al cargar las órdenes', 'error');
    }
}

// Mostrar órdenes en la tabla
function mostrarOrdenes() {
    const tbody = document.getElementById('tabla-ordenes');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (ordenes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No hay órdenes de trabajo registradas</td></tr>';
        return;
    }

    ordenes.forEach(orden => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>#${orden.id}</td>
            <td>${orden.fecha_creacion || 'N/A'}</td>
            <td>${orden.activo_nombre || 'Sin asignar'}</td>
            <td>${orden.tipo}</td>
            <td>${orden.descripcion}</td>
            <td><span class="badge bg-${getBadgeColor(orden.prioridad)}">${orden.prioridad}</span></td>
            <td><span class="badge bg-${getEstadoBadgeColor(orden.estado)}">${orden.estado}</span></td>
            <td>${orden.tecnico_nombre || 'Sin asignar'}</td>
            <td>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="verOrden(${orden.id})" title="Ver detalles">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" onclick="editarOrden(${orden.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info" onclick="mostrarModalEstado(${orden.id})" title="Cambiar estado">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Función para mostrar toast
function mostrarToast(mensaje, tipo = 'info') {
    if (!mensaje || mensaje === 'undefined' || mensaje === null) {
        mensaje = 'Operación realizada';
    }
    console.log(`${tipo.toUpperCase()}: ${mensaje}`);
    if (typeof showNotificationToast === 'function') {
        showNotificationToast({
            titulo: tipo === 'error' ? 'Error' : 'Información',
            mensaje: mensaje,
            tipo: tipo,
            tiempo: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        });
    }
}

// Ver detalles de una orden
function verOrden(id) {
    const orden = ordenes.find(o => o.id === id);
    if (orden) {
        document.getElementById('ver-orden-numero').textContent = `#${orden.id}`;
        document.getElementById('ver-orden-fecha').textContent = orden.fecha_creacion || 'N/A';
        document.getElementById('ver-orden-tipo').textContent = orden.tipo || 'N/A';
        document.getElementById('ver-orden-prioridad').innerHTML = `<span class="badge bg-${getBadgeColor(orden.prioridad)}">${orden.prioridad}</span>`;
        document.getElementById('ver-orden-estado').innerHTML = `<span class="badge bg-${getEstadoBadgeColor(orden.estado)}">${orden.estado}</span>`;
        document.getElementById('ver-orden-activo').textContent = orden.activo_nombre || 'Sin asignar';
        document.getElementById('ver-orden-tecnico').textContent = orden.tecnico_nombre || 'Sin asignar';
        document.getElementById('ver-orden-tiempo-estimado').textContent = orden.tiempo_estimado ? `${orden.tiempo_estimado} horas` : 'N/A';
        document.getElementById('ver-orden-descripcion').textContent = orden.descripcion || 'N/A';
        document.getElementById('ver-orden-observaciones').textContent = orden.observaciones || 'Sin observaciones';
        document.getElementById('ver-orden-numero').dataset.ordenId = orden.id;

        const modal = new bootstrap.Modal(document.getElementById('modalVerOrden'));
        modal.show();
        mostrarToast(`Ver detalles de orden #${id}`, 'info');
    }
}

// Editar una orden
async function editarOrden(id) {
    const orden = ordenes.find(o => o.id === id);
    if (orden) {
        await cargarActivos();
        await cargarTecnicos();

        document.getElementById('orden-id').value = orden.id;
        document.getElementById('orden-tipo').value = orden.tipo || '';
        document.getElementById('orden-prioridad').value = orden.prioridad || '';
        document.getElementById('orden-activo').value = orden.activo_id || '';
        document.getElementById('orden-tecnico').value = orden.tecnico_id || '';
        document.getElementById('orden-fecha-programada').value = orden.fecha_programada || '';
        document.getElementById('orden-tiempo-estimado').value = orden.tiempo_estimado || '';
        document.getElementById('orden-descripcion').value = orden.descripcion || '';
        document.getElementById('orden-observaciones').value = orden.observaciones || '';

        document.getElementById('modalOrdenTitulo').innerHTML = '<i class="bi bi-pencil me-2"></i>Editar Orden de Trabajo';
        document.getElementById('boton-guardar-texto').textContent = 'Actualizar Orden';

        const modal = new bootstrap.Modal(document.getElementById('modalOrden'));
        modal.show();
        mostrarToast(`Editar orden #${id}`, 'info');
    }
}

// GESTIÓN DE ESTADOS - Nueva funcionalidad principal

// Mostrar modal para cambiar estado
function mostrarModalEstado(id) {
    const orden = ordenes.find(o => o.id === id);
    if (orden) {
        document.getElementById('estado-orden-id').value = orden.id;
        document.getElementById('nuevo-estado').value = orden.estado;

        configurarEstadosValidos(orden.estado);

        const modalTitle = document.querySelector('#modalEstado .modal-title');
        modalTitle.innerHTML = `<i class="bi bi-arrow-repeat me-2"></i>Actualizar Estado - Orden #${orden.id}`;

        const modalBody = document.querySelector('#modalEstado .modal-body');
        const infoExistente = modalBody.querySelector('.orden-info');
        if (infoExistente) {
            infoExistente.remove();
        }

        const infoDiv = document.createElement('div');
        infoDiv.className = 'orden-info alert alert-info mb-3';
        infoDiv.innerHTML = `
            <strong>Orden:</strong> ${orden.descripcion}<br>
            <strong>Estado actual:</strong> <span class="badge bg-${getEstadoBadgeColor(orden.estado)}">${orden.estado}</span><br>
            <strong>Técnico:</strong> ${orden.tecnico_nombre || 'Sin asignar'}
        `;
        modalBody.insertBefore(infoDiv, modalBody.firstChild);

        const modal = new bootstrap.Modal(document.getElementById('modalEstado'));
        modal.show();
        mostrarToast(`Cambiar estado de orden #${id}`, 'info');
    }
}

// Configurar estados válidos según el estado actual
function configurarEstadosValidos(estadoActual) {
    const selectEstado = document.getElementById('nuevo-estado');
    const tiempoRealContainer = document.getElementById('tiempo-real-container');

    selectEstado.innerHTML = '';

    const transicionesValidas = {
        'Pendiente': ['En Proceso', 'Cancelada', 'En Espera'],
        'En Proceso': ['Completada', 'En Espera', 'Cancelada'],
        'En Espera': ['En Proceso', 'Pendiente', 'Cancelada'],
        'Completada': [],
        'Cancelada': ['Pendiente'],
        'Vencida': ['En Proceso', 'Cancelada']
    };

    const optionActual = document.createElement('option');
    optionActual.value = estadoActual;
    optionActual.textContent = `${estadoActual} (actual)`;
    optionActual.selected = true;
    selectEstado.appendChild(optionActual);

    const estadosValidos = transicionesValidas[estadoActual] || [];
    estadosValidos.forEach(estado => {
        const option = document.createElement('option');
        option.value = estado;
        option.textContent = estado;
        selectEstado.appendChild(option);
    });

    if (tiempoRealContainer) {
        tiempoRealContainer.style.display = estadosValidos.includes('Completada') ? 'block' : 'none';
    }
}

// Actualizar estado de una orden
async function actualizarEstado() {
    const ordenId = document.getElementById('estado-orden-id').value;
    const nuevoEstado = document.getElementById('nuevo-estado').value;
    const observaciones = document.getElementById('observaciones-estado').value;
    const tiempoReal = document.getElementById('tiempo-real') ? document.getElementById('tiempo-real').value : null;

    if (!nuevoEstado) {
        mostrarToast('Debe seleccionar un nuevo estado', 'warning');
        return;
    }

    try {
        const updateData = {
            estado: nuevoEstado,
            observaciones: observaciones || null
        };

        if (nuevoEstado === 'Completada' && tiempoReal) {
            updateData.tiempo_real = parseFloat(tiempoReal);
        }

        const response = await fetch(`/ordenes/${ordenId}/estado`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            mostrarToast(`Estado actualizado a: ${nuevoEstado}`, 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEstado'));
            modal.hide();
            await cargarOrdenes();
            document.getElementById('formEstado').reset();
        } else {
            const error = await response.json();
            throw new Error(error.mensaje || 'Error al actualizar el estado');
        }

    } catch (error) {
        console.error('Error actualizando estado:', error);
        const mensajeError = error?.message || error?.toString() || 'Error al actualizar el estado';
        mostrarToast(mensajeError, 'error');
    }
}

// Cambiar estado desde el modal de detalles
function cambiarEstadoDesdeDetalle() {
    const ordenId = parseInt(document.getElementById('ver-orden-numero').dataset.ordenId);
    const modalDetalle = bootstrap.Modal.getInstance(document.getElementById('modalVerOrden'));
    modalDetalle.hide();

    setTimeout(() => {
        mostrarModalEstado(ordenId);
    }, 300);
}

// Editar desde el modal de detalles
async function editarDesdeDetalle() {
    const ordenId = parseInt(document.getElementById('ver-orden-numero').dataset.ordenId);
    const modalDetalle = bootstrap.Modal.getInstance(document.getElementById('modalVerOrden'));
    modalDetalle.hide();

    setTimeout(async () => {
        await editarOrden(ordenId);
    }, 300);
}

// Actualizar estadísticas
function actualizarEstadisticas() {
    const stats = {
        pendientes: ordenes.filter(o => o.estado === 'Pendiente').length,
        enProceso: ordenes.filter(o => o.estado === 'En Proceso').length,
        completadas: ordenes.filter(o => o.estado === 'Completada').length,
        vencidas: ordenes.filter(o => o.estado === 'Vencida').length
    };

    document.getElementById('stat-pendientes').textContent = stats.pendientes;
    document.getElementById('stat-en-proceso').textContent = stats.enProceso;
    document.getElementById('stat-completadas').textContent = stats.completadas;
    document.getElementById('stat-vencidas').textContent = stats.vencidas;
}

// Obtener color del badge según prioridad
function getBadgeColor(prioridad) {
    switch (prioridad) {
        case 'Crítica': return 'danger';
        case 'Alta': return 'warning';
        case 'Media': return 'info';
        case 'Baja': return 'secondary';
        default: return 'secondary';
    }
}

// Obtener color del badge según estado
function getEstadoBadgeColor(estado) {
    switch (estado) {
        case 'Pendiente': return 'warning';
        case 'En Proceso': return 'info';
        case 'Completada': return 'success';
        case 'Cancelada': return 'secondary';
        case 'En Espera': return 'warning';
        case 'Vencida': return 'danger';
        default: return 'secondary';
    }
}

// Cargar datos iniciales (activos y técnicos)
async function cargarDatosIniciales() {
    try {
        console.log('Iniciando carga de datos...');
        await Promise.all([cargarActivos(), cargarTecnicos()]);
        console.log('Datos iniciales cargados exitosamente');
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        mostrarToast('Error al cargar datos iniciales', 'error');
    }
}

// Cargar activos
async function cargarActivos() {
    try {
        const response = await fetch('/activos/api');
        if (response.ok) {
            const data = await response.json();
            activos = data;
            llenarSelectActivos();
        } else {
            console.error('Error al cargar activos');
        }
    } catch (error) {
        console.error('Error cargando activos:', error);
    }
}

// Cargar técnicos
async function cargarTecnicos() {
    try {
        console.log('Iniciando carga de técnicos...');
        const response = await fetch('/usuarios/api?per_page=100');
        console.log('Respuesta usuarios API:', await response.clone().json());

        if (response.ok) {
            const data = await response.json();
            console.log('Usuarios extraídos:', data.usuarios);

            // Filtrar solo usuarios activos con roles apropiados
            tecnicos = data.usuarios.filter(usuario => {
                const esActivo = usuario.activo === true;
                const rolValido = ['Técnico', 'Administrador'].includes(usuario.rol);
                return esActivo && rolValido;
            });

            console.log('Técnicos filtrados:', tecnicos);

            llenarSelectTecnicos();

            if (tecnicos.length === 0) {
                mostrarToast('No hay técnicos disponibles para asignar órdenes', 'warning');
            }
        } else {
            console.error('Error al cargar técnicos');
        }
    } catch (error) {
        console.error('Error cargando técnicos:', error);
    }
}

// Llenar select de activos
function llenarSelectActivos() {
    const selectActivo = document.getElementById('orden-activo');
    if (!selectActivo) return;

    // Limpiar opciones existentes (excepto la primera)
    selectActivo.innerHTML = '<option value="">Seleccionar activo...</option>';

    activos.forEach(activo => {
        const option = document.createElement('option');
        option.value = activo.id;
        option.textContent = `${activo.nombre} - ${activo.ubicacion || 'Sin ubicación'}`;
        selectActivo.appendChild(option);
    });

    console.log(`Cargados ${activos.length} activos en el select`);
}

// Llenar select de técnicos
function llenarSelectTecnicos() {
    const selectTecnico = document.getElementById('orden-tecnico');
    if (!selectTecnico) {
        console.log('Select de técnico no encontrado');
        return;
    }

    console.log('Llenando select con técnicos:', tecnicos);

    // Limpiar opciones existentes (excepto la primera)
    selectTecnico.innerHTML = '<option value="">Asignar técnico...</option>';

    tecnicos.forEach((tecnico, index) => {
        console.log(`Agregando técnico ${index}:`, tecnico);
        const option = document.createElement('option');
        option.value = tecnico.id;

        // Usar solo nombre y rol (sin apellido)
        const nombre = tecnico.nombre || 'Sin nombre';
        const rol = tecnico.rol || 'Sin rol';
        option.textContent = `${nombre} - ${rol}`;
        selectTecnico.appendChild(option);
    });

    console.log(`Cargados ${tecnicos.length} técnicos en el select`);
    console.log('Select final HTML:', selectTecnico.innerHTML);
}

// Mostrar modal para nueva orden
function mostrarModalNuevaOrden() {
    // Resetear formulario
    document.getElementById('formOrden').reset();
    document.getElementById('orden-id').value = '';

    // Cambiar título del modal
    document.getElementById('modalOrdenTitulo').innerHTML = '<i class="bi bi-plus-circle me-2"></i>Nueva Orden de Trabajo';
    document.getElementById('boton-guardar-texto').textContent = 'Crear Orden';

    // Cargar datos actuales
    cargarActivos();
    cargarTecnicos();

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalOrden'));
    modal.show();
}

// Exportar CSV
async function exportarCSV() {
    try {
        if (typeof descargarCSVMejorado === 'function') {
            await descargarCSVMejorado('/ordenes/exportar-csv', 'ordenes_trabajo_{fecha}', 'CSV');
        } else {
            // Fallback simple
            window.open('/ordenes/exportar-csv', '_blank');
        }
    } catch (error) {
        console.error('Error exportando CSV:', error);
        mostrarToast('Error al exportar CSV', 'error');
    }
}

// Guardar orden de trabajo
async function guardarOrden() {
    const form = document.getElementById('formOrden');
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    try {
        // Recopilar datos del formulario
        const ordenData = {
            tipo: document.getElementById('orden-tipo').value,
            prioridad: document.getElementById('orden-prioridad').value,
            activo_id: document.getElementById('orden-activo').value || null,
            tecnico_id: document.getElementById('orden-tecnico').value || null,
            fecha_programada: document.getElementById('orden-fecha-programada').value || null,
            tiempo_estimado: parseFloat(document.getElementById('orden-tiempo-estimado').value) || null,
            descripcion: document.getElementById('orden-descripcion').value,
            observaciones: document.getElementById('orden-observaciones').value || null
        };

        const ordenId = document.getElementById('orden-id').value;
        const esEdicion = ordenId && ordenId !== '';

        const url = esEdicion ? `/ordenes/${ordenId}` : '/ordenes';
        const method = esEdicion ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ordenData)
        });

        if (response.ok) {
            const mensaje = esEdicion ? 'Orden actualizada exitosamente' : 'Orden de trabajo creada exitosamente';
            mostrarToast(mensaje, 'success');

            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalOrden'));
            modal.hide();

            // Recargar datos
            cargarOrdenes();

            // Limpiar formulario
            form.reset();
            form.classList.remove('was-validated');

        } else {
            const error = await response.json();
            throw new Error(error.mensaje || 'Error al guardar la orden');
        }

    } catch (error) {
        console.error('Error guardando orden:', error);
        const mensajeError = error?.message || error?.toString() || 'Error al guardar la orden de trabajo';
        mostrarToast(mensajeError, 'error');
    }
}

// Función de debug para probar la carga de técnicos
window.debugTecnicos = async function () {
    console.log('=== DEBUG: Probando carga de técnicos ===');
    try {
        const response = await fetch('/usuarios/api?per_page=100');
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Data completa:', data);
        console.log('Usuarios:', data.usuarios);

        if (data.usuarios) {
            const tecnicosActivos = data.usuarios.filter(u => u.activo === true);
            console.log('Técnicos activos:', tecnicosActivos);

            const tecnicosValidos = tecnicosActivos.filter(u => ['Técnico', 'Administrador'].includes(u.rol));
            console.log('Técnicos válidos:', tecnicosValidos);
        }
    } catch (error) {
        console.error('Error en debug:', error);
    }
};

// Función de debug para revisar el DOM
window.debugDOM = function () {
    console.log('=== DEBUG: Revisando DOM ===');
    const selectTecnico = document.getElementById('orden-tecnico');
    console.log('Select técnico encontrado:', !!selectTecnico);
    if (selectTecnico) {
        console.log('HTML del select:', selectTecnico.innerHTML);
        console.log('Opciones:', selectTecnico.options.length);
    }
};