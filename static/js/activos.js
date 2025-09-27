// Gestión de Activos - JavaScript

// Variables globales
let activos = [];
let departamentos = {};
let codigoEditableActivo = false;
let modoEdicionActivo = false; // Nueva variable para trackear modo edición

// Variables de paginación
let currentPage = 1;
let perPage = 10;
let paginacionActivos;

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    // Crear instancia de paginación
    paginacionActivos = createPagination('paginacion-activos', cargarActivos, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true
    });

    // Solo cargar datos esenciales al inicio
    cargarDepartamentos();
    cargarEstadisticasActivos();

    // Cargar activos de forma diferida
    setTimeout(() => {
        cargarActivos();
    }, 100);

    inicializarEventos();

    // Inicializar autocompletado después de cargar datos
    setTimeout(() => {
        inicializarAutocompletado();
    }, 200);

    // Event listener para preview de archivos en el formulario principal
    const inputArchivos = document.getElementById('archivos-manuales');
    if (inputArchivos) {
        inputArchivos.addEventListener('change', function () {
            const archivos = this.files;
            const preview = document.getElementById('archivos-preview');
            const contenedor = document.getElementById('lista-archivos-preview');

            if (archivos.length > 0) {
                let html = '';
                for (let i = 0; i < archivos.length; i++) {
                    const archivo = archivos[i];
                    const tamano = formatearTamano(archivo.size);
                    html += `
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <i class="bi ${obtenerIconoArchivo(archivo.name.split('.').pop())}"></i>
                            <span class="small">${archivo.name} (${tamano})</span>
                        </div>
                    `;
                }
                preview.innerHTML = html;
                contenedor.style.display = 'block';
            } else {
                contenedor.style.display = 'none';
            }
        });
    }
});

// Cargar departamentos desde el servidor
async function cargarDepartamentos() {
    try {
        const response = await fetch('/activos/departamentos');
        if (response.ok) {
            departamentos = await response.json();
            llenarSelectDepartamentos();
        } else {
            console.error('Error al cargar departamentos');
            mostrarMensaje('Error al cargar departamentos', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al cargar departamentos', 'danger');
    }
}

// Llenar los select de departamentos
function llenarSelectDepartamentos() {
    const selects = ['filtro-departamento', 'nuevo-departamento'];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            // Limpiar opciones existentes (excepto la primera en algunos casos)
            if (selectId === 'filtro-departamento') {
                select.innerHTML = '<option value="">Todos</option>';
            } else {
                select.innerHTML = '<option value="">Seleccionar departamento</option>';
            }

            // Agregar departamentos (departamentos es un objeto con códigos como claves)
            Object.entries(departamentos).forEach(([codigo, nombre]) => {
                const option = document.createElement('option');
                option.value = codigo;
                option.textContent = `${codigo} - ${nombre}`;
                select.appendChild(option);
            });
        }
    });
}

// Cargar proveedores desde el servidor
async function cargarProveedores() {
    try {
        const response = await fetch('/proveedores/api');
        if (response.ok) {
            const proveedores = await response.json();
            llenarSelectProveedores(proveedores);
        } else {
            console.error('Error al cargar proveedores');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Llenar el select de proveedores
function llenarSelectProveedores(proveedores) {
    const select = document.getElementById('nuevo-proveedor');
    if (select) {
        // Limpiar opciones existentes
        select.innerHTML = '<option value="">Seleccionar proveedor...</option>';

        // Agregar proveedores activos únicamente
        proveedores
            .filter(proveedor => proveedor.activo)
            .forEach(proveedor => {
                const option = document.createElement('option');
                option.value = proveedor.id;
                option.textContent = `${proveedor.nombre} (${proveedor.nif})`;
                select.appendChild(option);
            });
    }
}

// Cargar estadísticas de activos
async function cargarEstadisticasActivos() {
    try {
        const response = await fetch('/activos/api/estadisticas');
        if (response.ok) {
            const estadisticas = await response.json();
            actualizarEstadisticasActivos(estadisticas);
        } else {
            console.error('Error al cargar estadísticas de activos');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Actualizar las tarjetas de estadísticas
function actualizarEstadisticasActivos(estadisticas) {
    document.getElementById('total-activos').textContent = estadisticas.total_activos || 0;
    document.getElementById('activos-operativos').textContent = estadisticas.activos_operativos || 0;
    document.getElementById('activos-mantenimiento').textContent = estadisticas.activos_mantenimiento || 0;
    document.getElementById('activos-fuera-servicio').textContent = estadisticas.activos_fuera_servicio || 0;
}

// Cargar activos desde el servidor con paginación
async function cargarActivos(page = 1) {
    try {
        currentPage = page;
        mostrarCargando(true);

        const params = new URLSearchParams({
            page: page,
            per_page: perPage
        });

        const response = await fetch(`/activos/api?${params}`);
        if (response.ok) {
            const data = await response.json();
            activos = data.items || [];
            mostrarActivos(activos);
            actualizarContadorActivos(data.total || activos.length);

            // Renderizar paginación
            paginacionActivos.render(data.page, data.per_page, data.total);
        } else {
            console.error('Error al cargar activos');
            mostrarMensaje('Error al cargar activos', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al cargar activos', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Mostrar activos en la tabla
function mostrarActivos(activosAMostrar) {
    const tbody = document.getElementById('tabla-activos');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (activosAMostrar.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    No se encontraron activos
                </td>
            </tr>
        `;
        return;
    }

    activosAMostrar.forEach(activo => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>
                <span class="codigo-activo">${activo.codigo || 'Sin código'}</span>
            </td>
            <td>
                <span class="fw-medium">${obtenerNombreDepartamento(activo.departamento)}</span>
                <br>
                <small class="text-muted">${activo.departamento}</small>
            </td>
            <td>
                <span class="fw-medium">${activo.nombre}</span>
                ${activo.modelo ? `<br><small class="text-muted">${activo.modelo}</small>` : ''}
            </td>
            <td>
                <span class="badge bg-secondary">${activo.tipo || 'Sin tipo'}</span>
            </td>
            <td>${activo.ubicacion || '-'}</td>
            <td>
                <span class="text-muted">${activo.proveedor || '-'}</span>
            </td>
            <td>
                <span class="badge ${obtenerClaseEstado(activo.estado)}">${activo.estado || 'Sin estado'}</span>
            </td>
            <td>
                <span class="badge ${obtenerClasePrioridad(activo.prioridad)}">${activo.prioridad || 'Media'}</span>
            </td>
            <td>
                ${activo.ultimo_mantenimiento ?
                new Date(activo.ultimo_mantenimiento).toLocaleDateString('es-ES') :
                '<span class="text-muted">Sin registro</span>'
            }
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-sm btn-outline-primary action-btn view" onclick="verActivo(${activo.id})" title="Ver detalles">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info action-btn info" onclick="gestionarManuales(${activo.id})" title="Manuales">
                        <i class="bi bi-file-earmark-pdf"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarActivo(${activo.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn delete" onclick="eliminarActivo(${activo.id})" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

// Obtener nombre del departamento por código
function obtenerNombreDepartamento(codigo) {
    return departamentos[codigo] || 'Desconocido';
}

// Obtener clase CSS para el estado
function obtenerClaseEstado(estado) {
    switch (estado) {
        case 'Operativo':
            return 'bg-success';
        case 'En Mantenimiento':
            return 'bg-warning';
        case 'Fuera de Servicio':
            return 'bg-danger';
        case 'En Reparación':
            return 'bg-info';
        case 'Inactivo':
            return 'bg-secondary';
        default:
            return 'bg-secondary';
    }
}

// Obtener clase CSS para la prioridad
function obtenerClasePrioridad(prioridad) {
    switch (prioridad) {
        case 'Baja':
            return 'bg-success';
        case 'Media':
            return 'bg-primary';
        case 'Alta':
            return 'bg-warning';
        case 'Crítica':
            return 'bg-danger';
        default:
            return 'bg-primary';
    }
}

// Actualizar contador de activos
function actualizarContadorActivos(cantidad) {
    const contador = document.getElementById('contador-activos');
    if (contador) {
        contador.textContent = `${cantidad} activo${cantidad !== 1 ? 's' : ''}`;
    }
}

// Mostrar modal de nuevo activo
function mostrarModalNuevoActivo() {
    modoEdicionActivo = false; // Desactivar modo edición
    limpiarFormularioActivo();

    // Cargar proveedores solo cuando se abre el modal
    const selectProveedores = document.getElementById('nuevo-proveedor');
    if (selectProveedores && selectProveedores.children.length <= 1) {
        cargarProveedores();
    }

    const modal = new bootstrap.Modal(document.getElementById('modalNuevoActivo'));
    modal.show();
}

// Limpiar formulario de activo
function limpiarFormularioActivo() {
    modoEdicionActivo = false; // Desactivar modo edición
    document.getElementById('formNuevoActivo').reset();
    document.getElementById('nuevo-codigo').value = '';
    document.getElementById('nuevo-codigo').readOnly = true;
    codigoEditableActivo = false;

    // Remover campo oculto de ID si existe
    const hiddenId = document.getElementById('activo-id');
    if (hiddenId) {
        hiddenId.remove();
    }

    // Restaurar título del modal
    const titulo = document.querySelector('#modalNuevoActivo .modal-title');
    if (titulo) {
        titulo.innerHTML = '<i class="bi bi-plus me-2"></i>Nuevo Activo';
    }

    // Restaurar texto del botón
    const botonGuardar = document.querySelector('#modalNuevoActivo .btn-primary');
    if (botonGuardar) {
        botonGuardar.innerHTML = '<i class="bi bi-check me-1"></i>Crear Activo';
    }

    // Limpiar validaciones
    const campos = document.querySelectorAll('.is-invalid, .is-valid');
    campos.forEach(campo => {
        campo.classList.remove('is-invalid', 'is-valid');
    });

    const feedback = document.querySelectorAll('.invalid-feedback, .valid-feedback');
    feedback.forEach(f => f.remove());
}

// Generar código automáticamente
async function generarCodigo() {
    // No generar código si estamos en modo edición
    if (modoEdicionActivo) {
        console.log('Generación de código omitida: modo edición activo');
        return;
    }

    const departamento = document.getElementById('nuevo-departamento').value;
    const campoInput = document.getElementById('nuevo-codigo');

    if (!departamento) {
        campoInput.value = '';
        return;
    }

    try {
        const response = await fetch(`/activos/generar-codigo/${departamento}`);
        if (response.ok) {
            const data = await response.json();
            campoInput.value = data.codigo;
            validarCodigo(data.codigo);
        } else {
            console.error('Error al generar código');
            mostrarMensaje('Error al generar código', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al generar código', 'danger');
    }
}

// Habilitar edición manual del código
function habilitarEdicionCodigo() {
    const campo = document.getElementById('nuevo-codigo');
    codigoEditableActivo = true;
    campo.readOnly = false;
    campo.focus();

    // Agregar evento para validar mientras escribe
    campo.addEventListener('input', function () {
        validarCodigo(this.value);
    });
}

// Validar formato del código
async function validarCodigo(codigo) {
    const campo = document.getElementById('nuevo-codigo');

    if (!codigo) {
        mostrarValidacion(campo, false, 'El código es requerido');
        return false;
    }

    // Validar formato básico
    const formatoValido = /^\d{3}A\d{5}$/.test(codigo);
    if (!formatoValido) {
        mostrarValidacion(campo, false, 'Formato inválido. Use: 123A45678');
        return false;
    }

    try {
        // Validar unicidad en el servidor
        const response = await fetch('/activos/validar-codigo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ codigo: codigo })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.valido) {
                mostrarValidacion(campo, true, 'Código válido');
                return true;
            } else {
                mostrarValidacion(campo, false, data.mensaje || 'Código ya existe');
                return false;
            }
        } else {
            mostrarValidacion(campo, false, 'Error al validar código');
            return false;
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarValidacion(campo, false, 'Error de conexión');
        return false;
    }
}

// Mostrar validación en campo
function mostrarValidacion(campo, valido, mensaje) {
    // Limpiar validaciones anteriores
    campo.classList.remove('is-valid', 'is-invalid');
    const feedbackAnterior = campo.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (feedbackAnterior) {
        feedbackAnterior.remove();
    }

    // Aplicar nueva validación
    const feedback = document.createElement('div');
    if (valido) {
        campo.classList.add('is-valid');
        feedback.className = 'valid-feedback';
    } else {
        campo.classList.add('is-invalid');
        feedback.className = 'invalid-feedback';
    }

    feedback.textContent = mensaje;
    campo.parentNode.appendChild(feedback);
}

// Crear nuevo activo
async function crearActivo() {
    const form = document.getElementById('formNuevoActivo');

    // Validar formulario
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const codigo = document.getElementById('nuevo-codigo').value;
    const activoId = document.getElementById('activo-id')?.value;
    const esEdicion = activoId && activoId !== '';

    // Validar código si es editable y es una creación
    if (!esEdicion && codigoEditableActivo) {
        const codigoValido = await validarCodigo(codigo);
        if (!codigoValido) {
            return;
        }
    }

    const activo = {
        codigo: codigo,
        departamento: document.getElementById('nuevo-departamento').value,
        nombre: document.getElementById('nuevo-nombre').value,
        tipo: document.getElementById('nuevo-tipo').value,
        ubicacion: document.getElementById('nuevo-ubicacion').value,
        estado: document.getElementById('nuevo-estado').value,
        prioridad: document.getElementById('nuevo-prioridad').value,
        modelo: document.getElementById('nuevo-modelo').value,
        numero_serie: document.getElementById('nuevo-numero-serie').value,
        fabricante: document.getElementById('nuevo-fabricante').value,
        proveedor: document.getElementById('nuevo-proveedor').value,
        descripcion: document.getElementById('nuevo-descripcion').value
    };

    try {
        mostrarCargando(true);

        const url = esEdicion ? `/activos/api/${activoId}` : '/activos/';
        const method = esEdicion ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(activo)
        });

        if (response.ok) {
            const resultado = await response.json();
            const mensaje = esEdicion ? 'Activo actualizado exitosamente' : 'Activo creado exitosamente';
            mostrarMensaje(mensaje, 'success');

            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoActivo'));
            modal.hide();

            // Desactivar modo edición
            modoEdicionActivo = false;

            // Limpiar formulario
            limpiarFormularioActivo();

            // Recargar lista
            cargarActivos(currentPage);

            // Actualizar estadísticas
            cargarEstadisticasActivos();
        } else {
            const error = await response.json();
            mostrarMensaje(error.mensaje || 'Error al procesar activo', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al procesar activo', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Filtrar activos
function filtrarActivos() {
    const buscar = document.getElementById('filtro-buscar').value.toLowerCase();
    const departamento = document.getElementById('filtro-departamento').value;
    const tipo = document.getElementById('filtro-tipo').value;
    const estado = document.getElementById('filtro-estado').value;
    const prioridad = document.getElementById('filtro-prioridad').value;

    const activosFiltrados = activos.filter(activo => {
        const coincideBusqueda = !buscar ||
            (activo.codigo && activo.codigo.toLowerCase().includes(buscar)) ||
            (activo.nombre && activo.nombre.toLowerCase().includes(buscar)) ||
            (activo.descripcion && activo.descripcion.toLowerCase().includes(buscar));

        const coincideDepartamento = !departamento || activo.departamento === departamento;
        const coincideTipo = !tipo || activo.tipo === tipo;
        const coincideEstado = !estado || activo.estado === estado;
        const coincidePrioridad = !prioridad || activo.prioridad === prioridad;

        return coincideBusqueda && coincideDepartamento && coincideTipo && coincideEstado && coincidePrioridad;
    });

    mostrarActivos(activosFiltrados);
    actualizarContadorActivos(activosFiltrados.length);
}// Limpiar filtros
function limpiarFiltros() {
    document.getElementById('filtro-buscar').value = '';
    document.getElementById('filtro-departamento').value = '';
    document.getElementById('filtro-tipo').value = '';
    document.getElementById('filtro-estado').value = '';
    document.getElementById('filtro-prioridad').value = '';

    mostrarActivos(activos);
    actualizarContadorActivos(activos.length);
}

// Exportar activos a CSV
async function exportarCSV() {
    await descargarCSVMejorado('/activos/exportar-csv', 'activos_{fecha}', 'CSV');
}

// Funciones de gestión de activos
async function verActivo(id) {
    try {
        const response = await fetch(`/activos/api/${id}`);
        if (response.ok) {
            const activo = await response.json();
            mostrarDetallesActivo(activo);
        } else {
            mostrarMensaje('Error al cargar los detalles del activo', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al cargar activo', 'danger');
    }
}

async function editarActivo(id) {
    try {
        modoEdicionActivo = true; // Activar modo edición
        const response = await fetch(`/activos/api/${id}`);
        if (response.ok) {
            const activo = await response.json();

            // Asegurar que los departamentos estén cargados antes de llenar el formulario
            if (Object.keys(departamentos).length === 0) {
                console.log('Recargando departamentos...');
                await cargarDepartamentos();
            }

            llenarFormularioEdicion(activo);
            mostrarModalEdicion();
        } else {
            mostrarMensaje('Error al cargar los datos del activo', 'danger');
            modoEdicionActivo = false; // Desactivar modo edición si hay error
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al cargar activo', 'danger');
        modoEdicionActivo = false; // Desactivar modo edición si hay error
    }
}

async function eliminarActivo(id) {
    if (confirm('¿Está seguro de que desea eliminar este activo? Esta acción no se puede deshacer.')) {
        try {
            const response = await fetch(`/activos/api/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                mostrarMensaje('Activo eliminado exitosamente', 'success');
                cargarActivos(currentPage); // Recargar la lista
                cargarEstadisticasActivos(); // Actualizar estadísticas
            } else {
                const error = await response.json();
                mostrarMensaje(error.error || 'Error al eliminar activo', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarMensaje('Error de conexión al eliminar activo', 'danger');
        }
    }
}

// Mostrar detalles del activo en un modal
function mostrarDetallesActivo(activo) {
    const detallesHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-muted">Información Básica</h6>
                <p><strong>Código:</strong> ${activo.codigo}</p>
                <p><strong>Nombre:</strong> ${activo.nombre}</p>
                <p><strong>Departamento:</strong> ${activo.departamento}</p>
                <p><strong>Tipo:</strong> ${activo.tipo || 'No especificado'}</p>
                <p><strong>Estado:</strong> <span class="badge bg-${obtenerColorEstado(activo.estado)}">${activo.estado}</span></p>
            </div>
            <div class="col-md-6">
                <h6 class="text-muted">Detalles Técnicos</h6>
                <p><strong>Ubicación:</strong> ${activo.ubicacion || 'No especificada'}</p>
                <p><strong>Fabricante:</strong> ${activo.fabricante || 'No especificado'}</p>
                <p><strong>Modelo:</strong> ${activo.modelo || 'No especificado'}</p>
                <p><strong>N° Serie:</strong> ${activo.numero_serie || 'No especificado'}</p>
                <p><strong>Proveedor:</strong> ${activo.proveedor || 'No especificado'}</p>
            </div>
        </div>
        ${activo.descripcion ? `
            <div class="mt-3">
                <h6 class="text-muted">Descripción</h6>
                <p>${activo.descripcion}</p>
            </div>
        ` : ''}
    `;

    // Crear modal dinámico para mostrar detalles
    const modalHTML = `
        <div class="modal fade" id="modalVerActivo" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-eye me-2"></i>Detalles del Activo
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${detallesHTML}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="editarActivo(${activo.id})">
                            <i class="bi bi-pencil me-1"></i>Editar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remover modal anterior si existe
    const modalExistente = document.getElementById('modalVerActivo');
    if (modalExistente) {
        modalExistente.remove();
    }

    // Agregar nuevo modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalVerActivo'));
    modal.show();
}

// Llenar formulario de edición con datos del activo
function llenarFormularioEdicion(activo) {
    // Agregar campo oculto para el ID del activo
    let hiddenId = document.getElementById('activo-id');
    if (!hiddenId) {
        hiddenId = document.createElement('input');
        hiddenId.type = 'hidden';
        hiddenId.id = 'activo-id';
        document.getElementById('formNuevoActivo').appendChild(hiddenId);
    }
    hiddenId.value = activo.id;

    // Llenar campos del formulario
    document.getElementById('nuevo-codigo').value = activo.codigo;
    document.getElementById('nuevo-nombre').value = activo.nombre;
    document.getElementById('nuevo-tipo').value = activo.tipo || '';
    document.getElementById('nuevo-ubicacion').value = activo.ubicacion || '';
    document.getElementById('nuevo-estado').value = activo.estado;
    document.getElementById('nuevo-prioridad').value = activo.prioridad;
    document.getElementById('nuevo-descripcion').value = activo.descripcion || '';
    document.getElementById('nuevo-modelo').value = activo.modelo || '';
    document.getElementById('nuevo-numero-serie').value = activo.numero_serie || '';
    document.getElementById('nuevo-fabricante').value = activo.fabricante || '';
    document.getElementById('nuevo-proveedor').value = activo.proveedor || '';

    // Establecer departamento - ya no necesitamos interceptar onchange
    const selectDepartamento = document.getElementById('nuevo-departamento');
    if (selectDepartamento && activo.departamento) {
        // Verificar si la opción existe en el select
        const opcionExistente = selectDepartamento.querySelector(`option[value="${activo.departamento}"]`);
        if (opcionExistente) {
            selectDepartamento.value = activo.departamento;
            console.log(`Departamento establecido: ${activo.departamento}`);
        } else {
            console.warn(`Departamento ${activo.departamento} no encontrado en el select, creando opción...`);
            // Crear la opción si no existe
            const option = document.createElement('option');
            option.value = activo.departamento;
            option.textContent = `${activo.departamento} - ${departamentos[activo.departamento] || 'Departamento desconocido'}`;
            selectDepartamento.appendChild(option);
            selectDepartamento.value = activo.departamento;
        }
    } else if (!activo.departamento) {
        console.warn('El activo no tiene departamento asignado');
    }
}

// Mostrar modal de edición
function mostrarModalEdicion() {
    // Cambiar título del modal
    const titulo = document.querySelector('#modalNuevoActivo .modal-title');
    if (titulo) {
        titulo.innerHTML = '<i class="bi bi-pencil me-2"></i>Editar Activo';
    }

    // Cambiar texto del botón
    const botonGuardar = document.querySelector('#modalNuevoActivo .btn-primary');
    if (botonGuardar) {
        botonGuardar.innerHTML = '<i class="bi bi-check me-1"></i>Actualizar';
    }

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalNuevoActivo'));
    modal.show();
}

// Obtener color para el badge de estado
function obtenerColorEstado(estado) {
    const colores = {
        'Operativo': 'success',
        'Mantenimiento': 'warning',
        'Fuera de Servicio': 'danger',
        'En Reparación': 'info'
    };
    return colores[estado] || 'secondary';
}

// Inicializar eventos
function inicializarEventos() {
    // Evento de búsqueda en tiempo real
    const campoBuscar = document.getElementById('filtro-buscar');
    if (campoBuscar) {
        let timeoutBusqueda;
        campoBuscar.addEventListener('input', function () {
            clearTimeout(timeoutBusqueda);
            timeoutBusqueda = setTimeout(filtrarActivos, 300);
        });
    }

    // Eventos de filtros
    const filtros = ['filtro-departamento', 'filtro-tipo', 'filtro-estado', 'filtro-prioridad'];
    filtros.forEach(filtroId => {
        const filtro = document.getElementById(filtroId);
        if (filtro) {
            filtro.addEventListener('change', filtrarActivos);
        }
    });
}

// Inicializar autocompletado en formularios de activos
function inicializarAutocompletado() {
    console.log('Inicializando autocompletado en activos...');

    if (!window.AutoComplete) {
        console.log('AutoComplete no disponible');
        return;
    }

    // Autocompletado para filtro de búsqueda general
    const filtroBuscar = document.getElementById('filtro-buscar');
    if (filtroBuscar) {
        new AutoComplete({
            element: filtroBuscar,
            apiUrl: '/activos/api',
            searchKey: 'q',
            displayKey: item => `${item.nombre} (${item.codigo}) - ${item.ubicacion || 'Sin ubicación'}`,
            valueKey: 'nombre',
            placeholder: 'Buscar activo por nombre, código o ubicación...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Activo seleccionado para filtro:', item);
                filtrarActivos();
            }
        });
    }

    // Autocompletado para ubicaciones en formulario de nuevo activo
    const ubicacionInput = document.getElementById('nuevo-ubicacion');
    if (ubicacionInput) {
        // Obtener ubicaciones únicas de activos existentes
        const ubicacionesUnicas = [...new Set(activos
            .filter(activo => activo.ubicacion && activo.ubicacion.trim())
            .map(activo => activo.ubicacion))];

        new AutoComplete({
            element: ubicacionInput,
            localData: ubicacionesUnicas.map(ubicacion => ({ ubicacion })),
            displayKey: 'ubicacion',
            valueKey: 'ubicacion',
            placeholder: 'Ubicación del activo...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Ubicación seleccionada:', item);
            }
        });
    }

    // Autocompletado para fabricantes
    const fabricanteInput = document.getElementById('nuevo-fabricante');
    if (fabricanteInput) {
        // Obtener fabricantes únicos de activos existentes
        const fabricantesUnicos = [...new Set(activos
            .filter(activo => activo.fabricante && activo.fabricante.trim())
            .map(activo => activo.fabricante))];

        new AutoComplete({
            element: fabricanteInput,
            localData: fabricantesUnicos.map(fabricante => ({ fabricante })),
            displayKey: 'fabricante',
            valueKey: 'fabricante',
            placeholder: 'Fabricante del activo...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Fabricante seleccionado:', item);
            }
        });
    }

    // Autocompletado para modelos
    const modeloInput = document.getElementById('nuevo-modelo');
    if (modeloInput) {
        // Obtener modelos únicos de activos existentes
        const modelosUnicos = [...new Set(activos
            .filter(activo => activo.modelo && activo.modelo.trim())
            .map(activo => activo.modelo))];

        new AutoComplete({
            element: modeloInput,
            localData: modelosUnicos.map(modelo => ({ modelo })),
            displayKey: 'modelo',
            valueKey: 'modelo',
            placeholder: 'Modelo del activo...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Modelo seleccionado:', item);
            }
        });
    }

    console.log('Autocompletado inicializado en activos');
}

// Mostrar mensaje de notificación
function mostrarMensaje(mensaje, tipo = 'info') {
    // Crear elemento de alerta
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alerta.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alerta);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alerta.parentNode) {
            alerta.parentNode.removeChild(alerta);
        }
    }, 5000);
}

// Mostrar/ocultar indicador de carga
function mostrarCargando(mostrar) {
    const indicadores = document.querySelectorAll('.loading-indicator');
    if (mostrar) {
        document.body.classList.add('loading');
    } else {
        document.body.classList.remove('loading');
    }
}

// ========== GESTIÓN DE MANUALES ==========

// Abrir modal de gestión de manuales
async function gestionarManuales(activoId) {
    try {
        // Obtener información del activo
        const response = await fetch(`/activos/api/${activoId}`);
        if (response.ok) {
            const activo = await response.json();

            // Actualizar título del modal
            document.getElementById('modalManualesLabel').innerHTML =
                `<i class="bi bi-files me-2"></i>Manuales: ${activo.nombre}`;

            // Guardar ID del activo
            document.getElementById('activo-id-manual').value = activoId;

            // Cargar lista de manuales
            await cargarManuales(activoId);

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalManuales'));
            modal.show();
        }
    } catch (error) {
        console.error('Error al cargar manuales:', error);
        mostrarMensaje('Error al cargar información del activo', 'danger');
    }
}

// Cargar lista de manuales
async function cargarManuales(activoId) {
    try {
        const response = await fetch(`/activos/api/${activoId}/manuales`);
        if (response.ok) {
            const manuales = await response.json();
            mostrarListaManuales(manuales);
        } else {
            mostrarListaManuales([]);
        }
    } catch (error) {
        console.error('Error al cargar manuales:', error);
        mostrarListaManuales([]);
    }
}

// Mostrar lista de manuales en el modal
function mostrarListaManuales(manuales) {
    const container = document.getElementById('lista-manuales');

    if (manuales.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-file-earmark display-4"></i>
                <p class="mt-2">No hay manuales disponibles</p>
                <small>Haga clic en "Agregar Manual" para subir documentos</small>
            </div>
        `;
        return;
    }

    const manualesHTML = manuales.map(manual => {
        const fechaSubida = new Date(manual.fecha_subida).toLocaleDateString('es-ES');
        const tamanoArchivo = formatearTamano(manual.tamano);
        const iconoArchivo = obtenerIconoArchivo(manual.extension);

        return `
            <div class="card mb-2">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            <i class="bi ${iconoArchivo} fs-4 text-primary"></i>
                        </div>
                        <div class="col">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${manual.nombre_archivo}</h6>
                                    <small class="text-muted">
                                        ${manual.tipo} • ${tamanoArchivo} • ${fechaSubida}
                                    </small>
                                    ${manual.descripcion ? `<br><small class="text-muted">${manual.descripcion}</small>` : ''}
                                </div>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary" onclick="descargarManual(${manual.id})" title="Descargar">
                                        <i class="bi bi-download"></i>
                                    </button>
                                    <button class="btn btn-outline-info" onclick="previsualizarManual(${manual.id})" title="Vista previa">
                                        <i class="bi bi-eye"></i>
                                    </button>
                                    <button class="btn btn-outline-danger" onclick="eliminarManual(${manual.id})" title="Eliminar">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = manualesHTML;
}

// Mostrar formulario para subir manual
function mostrarSubirManual() {
    document.getElementById('form-subir-manual').style.display = 'block';
    document.getElementById('formSubirManual').reset();
}

// Ocultar formulario para subir manual
function ocultarSubirManual() {
    document.getElementById('form-subir-manual').style.display = 'none';
    document.getElementById('formSubirManual').reset();
}

// Subir manual
async function subirManual() {
    const form = document.getElementById('formSubirManual');
    const formData = new FormData();

    const activoId = document.getElementById('activo-id-manual').value;
    const archivo = document.getElementById('archivo-manual').files[0];
    const tipo = document.getElementById('tipo-manual').value;
    const descripcion = document.getElementById('descripcion-manual').value;

    // Validaciones
    if (!archivo) {
        mostrarMensaje('Debe seleccionar un archivo', 'warning');
        return;
    }

    if (!tipo) {
        mostrarMensaje('Debe seleccionar un tipo de documento', 'warning');
        return;
    }

    // Validar tamaño del archivo (5MB máximo)
    if (archivo.size > 5 * 1024 * 1024) {
        mostrarMensaje('El archivo no puede superar los 5MB', 'warning');
        return;
    }

    // Preparar datos para envío
    formData.append('archivo', archivo);
    formData.append('tipo', tipo);
    formData.append('descripcion', descripcion);

    try {
        mostrarCargando(true);

        const response = await fetch(`/activos/api/${activoId}/manuales`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const resultado = await response.json();
            mostrarMensaje('Manual subido exitosamente', 'success');

            // Ocultar formulario y recargar lista
            ocultarSubirManual();
            await cargarManuales(activoId);
        } else {
            const error = await response.json();
            mostrarMensaje(error.mensaje || 'Error al subir el manual', 'danger');
        }
    } catch (error) {
        console.error('Error al subir manual:', error);
        mostrarMensaje('Error de conexión al subir manual', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Descargar manual
async function descargarManual(manualId) {
    try {
        const response = await fetch(`/activos/api/manuales/${manualId}/descargar`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Obtener nombre del archivo del header
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'manual.pdf';
            if (disposition) {
                const matches = /filename="([^"]*)"/.exec(disposition);
                if (matches && matches[1]) {
                    filename = matches[1];
                }
            }

            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            mostrarMensaje('Manual descargado exitosamente', 'success');
        } else {
            mostrarMensaje('Error al descargar manual', 'danger');
        }
    } catch (error) {
        console.error('Error al descargar manual:', error);
        mostrarMensaje('Error de conexión al descargar manual', 'danger');
    }
}

// Previsualizar manual (para PDFs y imágenes)
async function previsualizarManual(manualId) {
    try {
        const response = await fetch(`/activos/api/manuales/${manualId}/previsualizar`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            // Abrir en nueva pestaña
            window.open(url, '_blank');

            // Limpiar URL después de un tiempo
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
            }, 60000);
        } else {
            mostrarMensaje('No se puede previsualizar este tipo de archivo', 'warning');
        }
    } catch (error) {
        console.error('Error al previsualizar manual:', error);
        mostrarMensaje('Error al previsualizar manual', 'danger');
    }
}

// Eliminar manual
async function eliminarManual(manualId) {
    if (!confirm('¿Está seguro de que desea eliminar este manual? Esta acción no se puede deshacer.')) {
        return;
    }

    try {
        const response = await fetch(`/activos/api/manuales/${manualId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            mostrarMensaje('Manual eliminado exitosamente', 'success');

            // Recargar lista
            const activoId = document.getElementById('activo-id-manual').value;
            await cargarManuales(activoId);
        } else {
            const error = await response.json();
            mostrarMensaje(error.mensaje || 'Error al eliminar manual', 'danger');
        }
    } catch (error) {
        console.error('Error al eliminar manual:', error);
        mostrarMensaje('Error de conexión al eliminar manual', 'danger');
    }
}

// Funciones utilitarias para manuales
function obtenerIconoArchivo(extension) {
    const iconos = {
        'pdf': 'bi-file-earmark-pdf',
        'doc': 'bi-file-earmark-word',
        'docx': 'bi-file-earmark-word',
        'txt': 'bi-file-earmark-text',
        'png': 'bi-file-earmark-image',
        'jpg': 'bi-file-earmark-image',
        'jpeg': 'bi-file-earmark-image'
    };
    return iconos[extension.toLowerCase()] || 'bi-file-earmark';
}

function formatearTamano(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
