// Gestión de Proveedores - JavaScript

// Variables globales
let proveedores = [];
let proveedorEditando = null;

// Variables de paginación
let currentPage = 1;
let perPage = 10;
let paginacionProveedores;

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    // Crear instancia de paginación
    paginacionProveedores = createPagination('paginacion-proveedores', cargarProveedores, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true
    });

    cargarProveedores();
    inicializarEventos();
});

// Cargar proveedores desde el servidor con paginación
async function cargarProveedores(page = 1) {
    try {
        currentPage = page;
        mostrarCargando(true);

        const params = new URLSearchParams({
            page: page,
            per_page: perPage
        });

        const response = await fetch(`/proveedores/api?${params}`);
        if (response.ok) {
            const data = await response.json();
            proveedores = data.items || [];
            mostrarProveedores(proveedores);
            actualizarContadorProveedores(data.total || proveedores.length);

            // Renderizar paginación
            paginacionProveedores.render(data.page, data.per_page, data.total);
        } else {
            console.error('Error al cargar proveedores');
            mostrarMensaje('Error al cargar proveedores', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al cargar proveedores', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Mostrar proveedores en la tabla
function mostrarProveedores(proveedoresAMostrar) {
    const tbody = document.getElementById('tabla-proveedores');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (proveedoresAMostrar.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    No se encontraron proveedores
                </td>
            </tr>
        `;
        return;
    }

    proveedoresAMostrar.forEach(proveedor => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>
                <div class="fw-bold">${proveedor.nombre}</div>
                ${proveedor.direccion ? `<small class="text-muted">${proveedor.direccion}</small>` : ''}
            </td>
            <td><code>${proveedor.nif}</code></td>
            <td><code>${proveedor.cuenta_contable}</code></td>
            <td>${proveedor.contacto || '<span class="text-muted">—</span>'}</td>
            <td>${proveedor.telefono || '<span class="text-muted">—</span>'}</td>
            <td>${proveedor.email || '<span class="text-muted">—</span>'}</td>
            <td>
                <span class="badge ${proveedor.activo ? 'bg-success' : 'bg-secondary'}">
                    ${proveedor.activo ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-info" onclick="editarProveedor(${proveedor.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="eliminarProveedor(${proveedor.id}, '${proveedor.nombre}')" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

// Actualizar contador de proveedores
function actualizarContadorProveedores(cantidad) {
    const contador = document.getElementById('contador-proveedores');
    if (contador) {
        contador.textContent = `${cantidad} proveedor${cantidad !== 1 ? 'es' : ''}`;
    }
}

// Mostrar modal de nuevo proveedor
function mostrarModalNuevoProveedor() {
    proveedorEditando = null;
    limpiarFormularioProveedor();

    document.getElementById('modalProveedorTitulo').innerHTML =
        '<i class="bi bi-plus-circle me-2"></i>Nuevo Proveedor';
    document.getElementById('boton-guardar-texto').textContent = 'Crear Proveedor';

    const modal = new bootstrap.Modal(document.getElementById('modalProveedor'));
    modal.show();
}

// Limpiar formulario de proveedor
function limpiarFormularioProveedor() {
    document.getElementById('formProveedor').reset();
    document.getElementById('proveedor-id').value = '';

    // Limpiar validaciones
    const campos = document.querySelectorAll('.is-invalid, .is-valid');
    campos.forEach(campo => {
        campo.classList.remove('is-invalid', 'is-valid');
    });

    const feedback = document.querySelectorAll('.invalid-feedback, .valid-feedback');
    feedback.forEach(f => f.remove());
}

// Validar NIF
async function validarNIF() {
    const nifInput = document.getElementById('proveedor-nif');
    const nif = nifInput.value.trim();

    if (!nif) {
        return;
    }

    // Si estamos editando y el NIF no ha cambiado, no validar
    if (proveedorEditando && proveedorEditando.nif === nif.toUpperCase()) {
        return;
    }

    try {
        const response = await fetch('/proveedores/validar-nif', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nif: nif })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.valido) {
                mostrarValidacion(nifInput, true, 'NIF válido');
            } else {
                mostrarValidacion(nifInput, false, data.mensaje || 'NIF ya existe');
            }
        } else {
            mostrarValidacion(nifInput, false, 'Error al validar NIF');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarValidacion(nifInput, false, 'Error de conexión');
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

    // Agregar nueva validación
    const feedbackDiv = document.createElement('div');
    if (valido) {
        campo.classList.add('is-valid');
        feedbackDiv.className = 'valid-feedback';
    } else {
        campo.classList.add('is-invalid');
        feedbackDiv.className = 'invalid-feedback';
    }
    feedbackDiv.textContent = mensaje;
    campo.parentNode.appendChild(feedbackDiv);
}

// Guardar proveedor (crear o actualizar)
async function guardarProveedor() {
    const form = document.getElementById('formProveedor');

    // Validar formulario
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const proveedor = {
        nombre: document.getElementById('proveedor-nombre').value.trim(),
        nif: document.getElementById('proveedor-nif').value.trim(),
        cuenta_contable: document.getElementById('proveedor-cuenta-contable').value.trim(),
        direccion: document.getElementById('proveedor-direccion').value.trim(),
        contacto: document.getElementById('proveedor-contacto').value.trim(),
        telefono: document.getElementById('proveedor-telefono').value.trim(),
        email: document.getElementById('proveedor-email').value.trim(),
    };

    try {
        mostrarCargando(true);

        const url = proveedorEditando ?
            `/proveedores/api/${proveedorEditando.id}` :
            '/proveedores/';

        const method = proveedorEditando ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(proveedor)
        });

        if (response.ok) {
            const data = await response.json();
            mostrarMensaje(
                proveedorEditando ? 'Proveedor actualizado exitosamente' : 'Proveedor creado exitosamente',
                'success'
            );

            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalProveedor'));
            modal.hide();

            // Recargar lista
            cargarProveedores(currentPage);
        } else {
            const error = await response.json();
            mostrarMensaje(error.message || 'Error al guardar proveedor', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al guardar proveedor', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Editar proveedor
async function editarProveedor(id) {
    try {
        mostrarCargando(true);

        const response = await fetch(`/proveedores/api/${id}`);
        if (response.ok) {
            proveedorEditando = await response.json();

            // Llenar formulario
            document.getElementById('proveedor-id').value = proveedorEditando.id;
            document.getElementById('proveedor-nombre').value = proveedorEditando.nombre;
            document.getElementById('proveedor-nif').value = proveedorEditando.nif;
            document.getElementById('proveedor-cuenta-contable').value = proveedorEditando.cuenta_contable;
            document.getElementById('proveedor-direccion').value = proveedorEditando.direccion || '';
            document.getElementById('proveedor-contacto').value = proveedorEditando.contacto || '';
            document.getElementById('proveedor-telefono').value = proveedorEditando.telefono || '';
            document.getElementById('proveedor-email').value = proveedorEditando.email || '';

            // Cambiar título del modal
            document.getElementById('modalProveedorTitulo').innerHTML =
                '<i class="bi bi-pencil me-2"></i>Editar Proveedor';
            document.getElementById('boton-guardar-texto').textContent = 'Actualizar Proveedor';

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalProveedor'));
            modal.show();
        } else {
            mostrarMensaje('Error al cargar datos del proveedor', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al cargar proveedor', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Eliminar proveedor
function eliminarProveedor(id, nombre) {
    document.getElementById('nombre-proveedor-eliminar').textContent = nombre;

    // Guardar ID para confirmar eliminación
    document.getElementById('modalEliminarProveedor').setAttribute('data-proveedor-id', id);

    const modal = new bootstrap.Modal(document.getElementById('modalEliminarProveedor'));
    modal.show();
}

// Confirmar eliminación de proveedor
async function confirmarEliminarProveedor() {
    const modal = document.getElementById('modalEliminarProveedor');
    const proveedorId = modal.getAttribute('data-proveedor-id');

    try {
        mostrarCargando(true);

        const response = await fetch(`/proveedores/api/${proveedorId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            mostrarMensaje('Proveedor eliminado exitosamente', 'success');

            // Cerrar modal
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();

            // Recargar lista
            cargarProveedores(currentPage);
        } else {
            const error = await response.json();
            mostrarMensaje(error.message || 'Error al eliminar proveedor', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al eliminar proveedor', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Filtrar proveedores
function filtrarProveedores() {
    const buscar = document.getElementById('filtro-buscar').value.toLowerCase();
    const estado = document.getElementById('filtro-estado').value;

    const proveedoresFiltrados = proveedores.filter(proveedor => {
        const coincideBusqueda = !buscar ||
            (proveedor.nombre && proveedor.nombre.toLowerCase().includes(buscar)) ||
            (proveedor.nif && proveedor.nif.toLowerCase().includes(buscar)) ||
            (proveedor.contacto && proveedor.contacto.toLowerCase().includes(buscar));

        const coincidenEstado = !estado ||
            (estado === 'activo' && proveedor.activo) ||
            (estado === 'inactivo' && !proveedor.activo);

        return coincideBusqueda && coincidenEstado;
    });

    mostrarProveedores(proveedoresFiltrados);
    actualizarContadorProveedores(proveedoresFiltrados.length);
}

// Limpiar filtros
function limpiarFiltros() {
    document.getElementById('filtro-buscar').value = '';
    document.getElementById('filtro-estado').value = 'activo';
    filtrarProveedores();
}

// Exportar CSV
async function exportarCSV() {
    await descargarCSVMejorado('/proveedores/exportar-csv', 'proveedores_{fecha}', 'CSV');
}

// Inicializar eventos
function inicializarEventos() {
    // Filtros en tiempo real
    document.getElementById('filtro-buscar').addEventListener('input', filtrarProveedores);
    document.getElementById('filtro-estado').addEventListener('change', filtrarProveedores);

    // Validación del NIF al escribir
    document.getElementById('proveedor-nif').addEventListener('input', function () {
        this.value = this.value.toUpperCase();
    });

    // Inicializar autocompletado después de cargar datos
    setTimeout(() => {
        inicializarAutocompletado();
    }, 500);
}

// Inicializar autocompletado en formularios de proveedores
function inicializarAutocompletado() {
    console.log('Inicializando autocompletado en proveedores...');

    if (!window.AutoComplete) {
        console.log('AutoComplete no disponible');
        return;
    }

    // Autocompletado para filtro de búsqueda general
    const filtroBuscar = document.getElementById('filtro-buscar');
    if (filtroBuscar) {
        new AutoComplete({
            element: filtroBuscar,
            apiUrl: '/proveedores/api',
            searchKey: 'q',
            displayKey: item => `${item.nombre} (${item.nif}) - ${item.contacto || 'Sin contacto'}`,
            valueKey: 'nombre',
            placeholder: 'Buscar proveedor por nombre, NIF o contacto...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Proveedor seleccionado para filtro:', item);
                filtrarProveedores();
            }
        });
    }

    // Autocompletado para campo nombre en formulario de nuevo proveedor
    const proveedorNombre = document.getElementById('proveedor-nombre');
    if (proveedorNombre) {
        new AutoComplete({
            element: proveedorNombre,
            localData: proveedores,
            displayKey: 'nombre',
            valueKey: 'nombre',
            placeholder: 'Nombre del proveedor...',
            allowFreeText: true,
            customFilter: (item, query) => {
                const q = query.toLowerCase();
                return item.nombre.toLowerCase().includes(q);
            },
            onSelect: (item) => {
                console.log('Nombre de proveedor seleccionado:', item);
                // Rellenar otros campos si están disponibles
                if (item.nif) document.getElementById('proveedor-nif').value = item.nif;
                if (item.contacto) document.getElementById('proveedor-contacto').value = item.contacto;
                if (item.direccion) document.getElementById('proveedor-direccion').value = item.direccion;
            }
        });
    }

    // Autocompletado para campo contacto
    const proveedorContacto = document.getElementById('proveedor-contacto');
    if (proveedorContacto) {
        // Obtener contactos únicos de proveedores existentes
        const contactosUnicos = [...new Set(proveedores
            .filter(proveedor => proveedor.contacto && proveedor.contacto.trim())
            .map(proveedor => proveedor.contacto))];

        new AutoComplete({
            element: proveedorContacto,
            localData: contactosUnicos.map(contacto => ({ contacto })),
            displayKey: 'contacto',
            valueKey: 'contacto',
            placeholder: 'Persona de contacto...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Contacto seleccionado:', item);
            }
        });
    }

    console.log('Autocompletado inicializado en proveedores');
}

// Mostrar mensaje al usuario
function mostrarMensaje(mensaje, tipo = 'info') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alerta.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
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
    if (mostrar) {
        document.body.classList.add('loading');
    } else {
        document.body.classList.remove('loading');
    }
}