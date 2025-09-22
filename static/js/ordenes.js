// Gestión de Órdenes de Trabajo - JavaScript

// Variables globales
let ordenes = [];
let activos = [];
let tecnicos = [];
let ordenEditando = null;

// Variables de paginación
let currentPage = 1;
let perPage = 10;
let paginacionOrdenes;

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('Módulo de órdenes cargado');

    // Crear instancia de paginación
    paginacionOrdenes = createPagination('paginacion-ordenes', cargarOrdenes, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true
    });

    if (document.getElementById('modalOrden')) {
        console.log('Modal de orden encontrado, cargando datos...');
        cargarDatosIniciales();
    }
    cargarOrdenes();
});

// Cargar lista de órdenes con paginación
async function cargarOrdenes(page = 1) {
    try {
        currentPage = page;
        const params = new URLSearchParams({
            page: page,
            per_page: perPage
        });

        const response = await fetch(`/ordenes/api?${params}`);
        if (response.ok) {
            const data = await response.json();
            ordenes = data.items || [];
            mostrarOrdenes();
            actualizarEstadisticas();

            // Renderizar paginación
            paginacionOrdenes.render(data.page, data.per_page, data.total);
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

        // Inicializar manejo de archivos para edición
        inicializarArchivos(orden.id);

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
            await cargarOrdenes(currentPage);
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

        // Inicializar autocompletado después de cargar datos
        inicializarAutocompletado();
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
            // Ya no necesitamos llenar select, usaremos autocompletado
            console.log(`Cargados ${activos.length} activos para autocompletado`);
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

            // Ya no necesitamos llenar select, usaremos autocompletado
            console.log(`Cargados ${tecnicos.length} técnicos para autocompletado`);

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

// Inicializar autocompletado en formularios
function inicializarAutocompletado() {
    console.log('Inicializando autocompletado en órdenes...');

    // Autocompletado para activos
    const activoInput = document.getElementById('orden-activo');
    if (activoInput && window.AutoComplete) {
        new AutoComplete({
            element: activoInput,
            localData: activos,
            displayKey: item => `${item.nombre} - ${item.ubicacion || 'Sin ubicación'} (${item.codigo})`,
            valueKey: 'id',
            placeholder: 'Buscar activo...',
            allowFreeText: false,
            customFilter: (item, query) => {
                const q = query.toLowerCase();
                return item.nombre.toLowerCase().includes(q) ||
                    item.codigo.toLowerCase().includes(q) ||
                    (item.ubicacion && item.ubicacion.toLowerCase().includes(q));
            },
            onSelect: (item) => {
                console.log('Activo seleccionado:', item);
            }
        });
    }

    // Autocompletado para técnicos
    const tecnicoInput = document.getElementById('orden-tecnico');
    if (tecnicoInput && window.AutoComplete) {
        new AutoComplete({
            element: tecnicoInput,
            localData: tecnicos,
            displayKey: item => `${item.nombre} - ${item.rol}`,
            valueKey: 'id',
            placeholder: 'Buscar técnico...',
            allowFreeText: false,
            customFilter: (item, query) => {
                const q = query.toLowerCase();
                return item.nombre.toLowerCase().includes(q) ||
                    item.username.toLowerCase().includes(q) ||
                    item.rol.toLowerCase().includes(q);
            },
            onSelect: (item) => {
                console.log('Técnico seleccionado:', item);
            }
        });
    }

    // Autocompletado para filtros de búsqueda
    const filtroBuscar = document.getElementById('filtro-buscar');
    if (filtroBuscar && window.AutoComplete) {
        new AutoComplete({
            element: filtroBuscar,
            localData: ordenes,
            displayKey: item => `#${item.id} - ${item.descripcion}`,
            valueKey: 'descripcion',
            placeholder: 'Buscar orden por descripción...',
            allowFreeText: true,
            customFilter: (item, query) => {
                const q = query.toLowerCase();
                return item.descripcion.toLowerCase().includes(q) ||
                    item.id.toString().includes(q) ||
                    (item.activo_nombre && item.activo_nombre.toLowerCase().includes(q));
            },
            onSelect: (item) => {
                console.log('Orden filtrada:', item);
                aplicarFiltros(); // Aplicar filtros después de selección
            }
        });
    }

    console.log('Autocompletado inicializado en órdenes');
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

    // Inicializar manejo de archivos
    inicializarArchivos(null);

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

        const url = esEdicion ? `/ordenes/api/${ordenId}` : '/ordenes';
        const method = esEdicion ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ordenData)
        });

        if (response.ok) {
            const resultado = await response.json();
            const ordenIdFinal = esEdicion ? ordenId : resultado.id;

            // Subir archivos pendientes si es una orden nueva o si hay archivos pendientes
            if (archivosTemporales.length > 0) {
                try {
                    await subirArchivosPendientes(ordenIdFinal);
                    mostrarToast('Archivos adjuntos procesados', 'info');
                } catch (error) {
                    console.error('Error al subir archivos:', error);
                    mostrarToast('Orden guardada, pero algunos archivos no se pudieron subir', 'warning');
                }
            }

            const mensaje = esEdicion ? 'Orden actualizada exitosamente' : 'Orden de trabajo creada exitosamente';
            mostrarToast(mensaje, 'success');

            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalOrden'));
            modal.hide();

            // Recargar datos
            cargarOrdenes(currentPage);

            // Limpiar formulario
            form.reset();
            form.classList.remove('was-validated');

            // Limpiar archivos temporales
            archivosTemporales = [];
            limpiarListaArchivos();

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

// ================================
// GESTIÓN DE ARCHIVOS ADJUNTOS
// ================================

// Variables globales para archivos
let archivosTemporales = [];
let ordenIdActual = null;

// Inicializar funcionalidad de archivos cuando se abre el modal
function inicializarArchivos(ordenId = null) {
    console.log('Inicializando archivos para orden:', ordenId);
    ordenIdActual = ordenId;
    archivosTemporales = [];

    // Configurar eventos de drag & drop
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const browseFiles = document.getElementById('browse-files');

    if (uploadArea && fileInput && browseFiles) {
        // Limpiar eventos previos para evitar duplicados
        uploadArea.replaceWith(uploadArea.cloneNode(true));
        const newUploadArea = document.getElementById('upload-area');

        // Eventos de drag & drop
        newUploadArea.addEventListener('dragover', handleDragOver);
        newUploadArea.addEventListener('dragleave', handleDragLeave);
        newUploadArea.addEventListener('drop', handleDrop);
        newUploadArea.addEventListener('click', () => fileInput.click());

        // Limpiar eventos del botón browse
        const newBrowseFiles = document.getElementById('browse-files');
        newBrowseFiles.addEventListener('click', (e) => {
            e.preventDefault();
            fileInput.click();
        });

        // Evento cuando se seleccionan archivos
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Limpiar campos de enlace
    const urlInput = document.getElementById('enlace-url');
    const descripcionInput = document.getElementById('enlace-descripcion');
    if (urlInput) {
        urlInput.value = '';
        urlInput.classList.remove('enlace-valido', 'enlace-invalido');
    }
    if (descripcionInput) {
        descripcionInput.value = '';
    }

    // Cargar archivos existentes si estamos editando
    if (ordenId) {
        cargarArchivosExistentes(ordenId);
    } else {
        limpiarListaArchivos();
    }
}// Eventos de drag & drop
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');

    const files = Array.from(e.dataTransfer.files);
    procesarArchivos(files);
}

// Manejar selección de archivos
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    procesarArchivos(files);
    e.target.value = ''; // Limpiar input para permitir seleccionar el mismo archivo
}

// Procesar archivos seleccionados
function procesarArchivos(files) {
    files.forEach(file => {
        if (validarArchivo(file)) {
            const archivoTemporal = {
                id: Date.now() + Math.random(),
                archivo: file,
                nombre: file.name,
                tamaño: file.size,
                tipo: determinarTipoArchivo(file),
                progreso: 0,
                estado: 'preparado' // preparado, subiendo, completado, error
            };

            archivosTemporales.push(archivoTemporal);
            añadirArchivoALista(archivoTemporal, true);
        }
    });
}

// Validar archivo
function validarArchivo(file) {
    const tiposPermitidos = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
        'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain', 'text/csv'
    ];

    const tamañoMaximo = 10 * 1024 * 1024; // 10MB

    if (!tiposPermitidos.includes(file.type)) {
        mostrarToast(`Tipo de archivo no permitido: ${file.name}`, 'error');
        return false;
    }

    if (file.size > tamañoMaximo) {
        mostrarToast(`Archivo muy grande: ${file.name} (máx. 10MB)`, 'error');
        return false;
    }

    return true;
}

// Determinar tipo de archivo
function determinarTipoArchivo(file) {
    if (file.type.startsWith('image/')) {
        return 'imagen';
    } else if (file.type.includes('pdf') || file.type.includes('document') || file.type.includes('sheet') || file.type.includes('text')) {
        return 'documento';
    } else {
        return 'archivo';
    }
}

// Añadir archivo a la lista visual
function añadirArchivoALista(archivo, esNuevo = false) {
    const listaArchivos = document.getElementById('lista-archivos');
    if (!listaArchivos) return;

    const archivoDiv = document.createElement('div');
    archivoDiv.className = `archivo-item archivo-${archivo.tipo}`;
    archivoDiv.setAttribute('data-archivo-id', archivo.id);

    let icono = 'bi-file-earmark';
    if (archivo.tipo === 'imagen') {
        icono = 'bi-image';
    } else if (archivo.tipo === 'documento') {
        icono = 'bi-file-text';
    } else if (archivo.tipo === 'enlace') {
        icono = 'bi-link-45deg';
    }

    archivoDiv.innerHTML = `
        <div class="archivo-info">
            <i class="bi ${icono} archivo-icono"></i>
            <div class="archivo-detalles">
                <h6>${archivo.nombre || archivo.nombre_original}</h6>
                <small>${formatearTamaño(archivo.tamaño || archivo.tamaño)} ${archivo.descripcion ? '- ' + archivo.descripcion : ''}</small>
                ${esNuevo && archivo.estado === 'preparado' ? '<div class="upload-progress"><div class="upload-progress-bar" style="width: 0%"></div></div>' : ''}
            </div>
        </div>
        <div class="archivo-acciones">
            ${!esNuevo && archivo.tipo !== 'enlace' ? `<button class="btn btn-sm btn-outline-primary" onclick="descargarArchivo(${archivo.id})"><i class="bi bi-download"></i></button>` : ''}
            ${archivo.tipo === 'enlace' ? `<button class="btn btn-sm btn-outline-info" onclick="abrirEnlace('${archivo.url_enlace}')"><i class="bi bi-box-arrow-up-right"></i></button>` : ''}
            <button class="btn btn-sm btn-outline-danger" onclick="eliminarArchivo(${archivo.id}, ${esNuevo})"><i class="bi bi-trash"></i></button>
        </div>
    `;

    listaArchivos.appendChild(archivoDiv);
}

// Formatear tamaño de archivo
function formatearTamaño(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Agregar enlace externo
async function agregarEnlace() {
    const urlInput = document.getElementById('enlace-url');
    const descripcionInput = document.getElementById('enlace-descripcion');

    if (!urlInput || !descripcionInput) {
        console.warn('Elementos de enlace no encontrados');
        return;
    }

    const url = urlInput.value.trim();
    const descripcion = descripcionInput.value.trim();

    // Validación mejorada
    if (!url) {
        mostrarToast('Por favor ingresa una URL', 'error');
        urlInput.focus();
        return;
    }

    if (!validarURL(url)) {
        mostrarToast('URL no válida. Debe incluir http:// o https://', 'error');
        urlInput.classList.add('enlace-invalido');
        urlInput.focus();
        return;
    }

    // Remover clases de validación previas
    urlInput.classList.remove('enlace-invalido');
    urlInput.classList.add('enlace-valido');

    try {
        if (ordenIdActual) {
            // Si estamos editando una orden existente, guardar inmediatamente
            const response = await fetch(`/ordenes/api/${ordenIdActual}/enlaces`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    descripcion: descripcion
                })
            });

            if (response.ok) {
                const resultado = await response.json();
                añadirArchivoALista(resultado.enlace, false);
                mostrarToast('Enlace agregado exitosamente', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al agregar enlace');
            }
        } else {
            // Si es una orden nueva, agregar a lista temporal
            const enlaceTemp = {
                id: Date.now() + Math.random(),
                nombre: `Enlace: ${url}`,
                url_enlace: url,
                descripcion: descripcion,
                tipo: 'enlace',
                tamaño: 0
            };

            archivosTemporales.push(enlaceTemp);
            añadirArchivoALista(enlaceTemp, true);
            mostrarToast('Enlace agregado a la lista', 'success');
        }

        // Limpiar campos solo si todo fue exitoso
        urlInput.value = '';
        descripcionInput.value = '';
        urlInput.classList.remove('enlace-valido');

    } catch (error) {
        console.error('Error al agregar enlace:', error);
        mostrarToast('Error al agregar enlace: ' + error.message, 'error');
        urlInput.classList.add('enlace-invalido');
    }
}

// Validar URL
function validarURL(url) {
    try {
        // Verificar que la URL no esté vacía
        if (!url || url.trim() === '') {
            return false;
        }

        // Si no tiene protocolo, añadir https por defecto
        let urlToValidate = url.trim();
        if (!urlToValidate.startsWith('http://') && !urlToValidate.startsWith('https://')) {
            urlToValidate = 'https://' + urlToValidate;
        }

        const urlObj = new URL(urlToValidate);

        // Verificar que tenga un dominio válido
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch (e) {
        console.warn('URL inválida:', url, e);
        return false;
    }
}

// Eliminar archivo
async function eliminarArchivo(archivoId, esNuevo = false) {
    try {
        if (esNuevo) {
            // Eliminar de lista temporal
            archivosTemporales = archivosTemporales.filter(a => a.id !== archivoId);
        } else {
            // Eliminar del servidor
            const response = await fetch(`/ordenes/api/archivos/${archivoId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Error al eliminar archivo');
            }

            mostrarToast('Archivo eliminado exitosamente', 'success');
        }

        // Eliminar del DOM
        const archivoElement = document.querySelector(`[data-archivo-id="${archivoId}"]`);
        if (archivoElement) {
            archivoElement.remove();
        }

    } catch (error) {
        console.error('Error al eliminar archivo:', error);
        mostrarToast('Error al eliminar archivo', 'error');
    }
}

// Descargar archivo
function descargarArchivo(archivoId) {
    window.open(`/ordenes/api/archivos/${archivoId}/download`, '_blank');
}

// Abrir enlace externo
function abrirEnlace(url) {
    window.open(url, '_blank');
}

// Cargar archivos existentes
async function cargarArchivosExistentes(ordenId) {
    try {
        const response = await fetch(`/ordenes/api/${ordenId}/archivos`);
        if (response.ok) {
            const archivos = await response.json();

            limpiarListaArchivos();

            archivos.forEach(archivo => {
                añadirArchivoALista(archivo, false);
            });
        }
    } catch (error) {
        console.error('Error al cargar archivos:', error);
    }
}

// Limpiar lista de archivos
function limpiarListaArchivos() {
    const listaArchivos = document.getElementById('lista-archivos');
    if (listaArchivos) {
        listaArchivos.innerHTML = '';
    }
}

// Subir archivos pendientes (cuando se guarda la orden)
async function subirArchivosPendientes(ordenId) {
    console.log('Procesando archivos temporales:', archivosTemporales);

    // Procesar archivos
    const archivosPendientes = archivosTemporales.filter(a => a.archivo && a.estado === 'preparado');
    console.log('Archivos a subir:', archivosPendientes.length);

    for (const archivo of archivosPendientes) {
        try {
            archivo.estado = 'subiendo';
            await subirArchivo(archivo, ordenId);
            archivo.estado = 'completado';
            console.log('Archivo subido exitosamente:', archivo.nombre);
        } catch (error) {
            archivo.estado = 'error';
            console.error('Error al subir archivo:', archivo.nombre, error);
        }
    }

    // Procesar enlaces válidos
    const enlacesPendientes = archivosTemporales.filter(a =>
        a.tipo === 'enlace' &&
        a.url_enlace &&
        a.url_enlace.trim() !== '' &&
        validarURL(a.url_enlace)
    );
    console.log('Enlaces a procesar:', enlacesPendientes.length);

    for (const enlace of enlacesPendientes) {
        try {
            console.log('Procesando enlace:', enlace.url_enlace);
            const response = await fetch(`/ordenes/api/${ordenId}/enlaces`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: enlace.url_enlace,
                    descripcion: enlace.descripcion || ''
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al guardar enlace');
            }

            console.log('Enlace guardado exitosamente:', enlace.url_enlace);
        } catch (error) {
            console.error('Error al guardar enlace:', enlace.url_enlace, error);
        }
    }
}

// Subir archivo individual
async function subirArchivo(archivoTemp, ordenId) {
    const formData = new FormData();
    formData.append('archivo', archivoTemp.archivo);
    formData.append('descripcion', archivoTemp.descripcion || '');

    const response = await fetch(`/ordenes/api/${ordenId}/archivos`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error('Error al subir archivo');
    }

    return await response.json();
}