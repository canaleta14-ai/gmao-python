// proveedores.js - JavaScript específico para el módulo de proveedores
// Última actualización: 2025-09-24 12:25:00 - Añadidas columnas Email y Dirección

// Variables globales
let proveedores = [];
let proveedoresFiltrados = [];
let proveedorEditando = null;
let filtrosActivos = {};

// Configuración de paginación
let currentPage = 1;
let perPage = 10;

// Instancia de paginación
let paginacionProveedores;

document.addEventListener('DOMContentLoaded', function () {
    console.log('=== PROVEEDORES MODULE DEBUG ===');
    console.log('Módulo Proveedores cargado');

    // Verificar elementos críticos
    console.log('tbody existe:', !!document.getElementById('tabla-proveedores'));
    console.log('Bootstrap disponible:', typeof bootstrap !== 'undefined');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

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
    setupFormProveedor();
    setupFiltrosProveedores();
    actualizarEstadisticas();

    // Inicializar paginación
    paginacionProveedores = createPagination('paginacion-proveedores', cargarProveedores, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true
    });

    // Cargar proveedores al inicializar
    console.log('Iniciando carga de proveedores...');
    cargarProveedores();
});// Función para limpiar filtros
function limpiarFiltrosProveedores() {
    console.log('Limpiando filtros de proveedores');
    const form = document.getElementById('filtros-proveedores-form');
    if (form) {
        form.reset();
        filtrarTablaProveedores(); // Recargar tabla completa
    }
}

// Cargar proveedores desde el servidor con paginación
async function cargarProveedores(page = 1) {
    console.log('cargarProveedores llamada con page:', page);
    try {
        currentPage = page;
        mostrarCargando(true);

        const params = new URLSearchParams({
            page: page,
            per_page: perPage
        });

        console.log('Haciendo fetch a:', `/proveedores/api?${params}`);
        const response = await fetch(`/proveedores/api?${params}`);
        console.log('Respuesta recibida:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Datos recibidos:', data);
            proveedores = data.items || [];
            mostrarProveedores(proveedores);
            actualizarContadorProveedores(data.total || proveedores.length);

            // Renderizar paginación si existe
            if (typeof paginacionProveedores !== 'undefined' && paginacionProveedores.render) {
                paginacionProveedores.render(data.page, data.per_page, data.total);
            }
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
    console.log('mostrarProveedores llamada con:', proveedoresAMostrar.length, 'proveedores');
    const tbody = document.getElementById('tabla-proveedores');
    console.log('tbody encontrado:', tbody);
    if (!tbody) return;

    tbody.innerHTML = '';

    if (proveedoresAMostrar.length === 0) {
        console.log('No hay proveedores para mostrar');
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

    console.log('Renderizando', proveedoresAMostrar.length, 'proveedores');
    proveedoresAMostrar.forEach(proveedor => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>
                <div class="fw-bold">${proveedor.nombre}</div>
            </td>
            <td><code>${proveedor.nif}</code></td>
            <td>${proveedor.direccion || '<span class="text-muted">—</span>'}</td>
            <td>${proveedor.contacto || '<span class="text-muted">—</span>'}</td>
            <td>${proveedor.email || '<span class="text-muted">—</span>'}</td>
            <td><code>${proveedor.cuenta_contable}</code></td>
            <td>
                <span class="badge ${proveedor.activo ? 'bg-success' : 'bg-secondary'}">
                    ${proveedor.activo ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td class="text-center">
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-sm btn-outline-primary action-btn view" onclick="verProveedor(${proveedor.id})" title="Ver">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm ${proveedor.activo ? 'btn-outline-warning' : 'btn-outline-success'} action-btn toggle" onclick="toggleProveedor(${proveedor.id})" title="${proveedor.activo ? 'Desactivar' : 'Activar'}">
                        <i class="bi ${proveedor.activo ? 'bi-toggle-off' : 'bi-toggle-on'}"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarProveedor(${proveedor.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn delete" onclick="eliminarProveedor(${proveedor.id}, '${proveedor.nombre}')" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(fila);
    });
    console.log('Proveedores renderizados correctamente');
}

// Actualizar contador de proveedores
function actualizarContadorProveedores(cantidad) {
    const contador = document.getElementById('contador-proveedores');
    if (contador) {
        contador.textContent = `${cantidad} proveedor${cantidad !== 1 ? 'es' : ''}`;
    }
}

// Función para manejar el formulario de proveedores
function setupFormProveedor() {
    const form = document.getElementById('form-proveedor');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Obtener datos del formulario
            const data = {
                nombre_empresa: document.getElementById('nombre_empresa').value,
                nif: document.getElementById('nif').value,
                persona_contacto: document.getElementById('persona_contacto').value,
                email: document.getElementById('email').value,
                telefono: document.getElementById('telefono').value,
                categoria: document.getElementById('categoria_modal').value,
                direccion: document.getElementById('direccion').value,
                ciudad: document.getElementById('ciudad').value,
                codigo_postal: document.getElementById('codigo_postal').value,
                pais: document.getElementById('pais_modal').value
            };

            console.log('Datos del nuevo proveedor:', data);

            // Aquí iría la lógica para enviar al servidor
            // Por ahora solo mostramos un mensaje
            alert('Proveedor guardado correctamente (demo)');

            // Cerrar modal y limpiar formulario
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalProveedor'));
            if (modal) {
                modal.hide();
            }
            form.reset();
        });
    }
}

// Función para manejar filtros en tiempo real
function setupFiltrosProveedores() {
    const filtroBuscar = document.getElementById('filtro-buscar');
    const filtroEstado = document.getElementById('filtro-estado');

    [filtroBuscar, filtroEstado].forEach(filtro => {
        if (filtro) {
            filtro.addEventListener('input', function () {
                filtrarProveedores();
            });
            filtro.addEventListener('change', function () {
                filtrarProveedores();
            });
        }
    });
}

// Función para filtrar la tabla de proveedores
function filtrarTablaProveedores() {
    const buscarFiltro = document.getElementById('buscar').value.toLowerCase();
    const categoriaFiltro = document.getElementById('categoria').value.toLowerCase();
    const estadoFiltro = document.getElementById('estado').value.toLowerCase();
    const paisFiltro = document.getElementById('pais').value.toLowerCase();

    const filas = document.querySelectorAll('#tbody-proveedores tr');

    filas.forEach(fila => {
        const proveedor = fila.cells[0].textContent.toLowerCase();
        const contacto = fila.cells[1].textContent.toLowerCase();
        const categoria = fila.cells[2].textContent.toLowerCase();
        const pais = fila.cells[3].textContent.toLowerCase();
        const estado = fila.cells[4].textContent.toLowerCase();

        const coincideBuscar = !buscarFiltro ||
            proveedor.includes(buscarFiltro) ||
            contacto.includes(buscarFiltro);
        const coincideCategoria = !categoriaFiltro || categoria.includes(categoriaFiltro);
        const coincideEstado = !estadoFiltro || estado.includes(estadoFiltro);
        const coincidePais = !paisFiltro || pais.includes(paisFiltro);

        if (coincideBuscar && coincideCategoria && coincideEstado && coincidePais) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });

    // Actualizar contador de resultados
    const filasVisibles = document.querySelectorAll('#tbody-proveedores tr:not([style*="display: none"])');
    console.log(`Mostrando ${filasVisibles.length} proveedores de ${filas.length} total`);

    // Actualizar estadísticas
    actualizarEstadisticas();
}

// Función para actualizar estadísticas
function actualizarEstadisticas() {
    // Cargar estadísticas desde la API en lugar de calcular desde filas visibles
    cargarEstadisticasProveedores();
}

// Cargar estadísticas de proveedores desde la API
async function cargarEstadisticasProveedores() {
    try {
        const response = await fetch('/proveedores/api/estadisticas');
        if (response.ok) {
            const estadisticas = await response.json();
            actualizarTarjetasEstadisticas(estadisticas);
        } else {
            console.error('Error al cargar estadísticas de proveedores');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Actualizar las tarjetas de estadísticas con datos de la API
function actualizarTarjetasEstadisticas(estadisticas) {
    document.getElementById('total-proveedores').textContent = estadisticas.total_proveedores || 0;
    document.getElementById('proveedores-activos').textContent = estadisticas.proveedores_activos || 0;
    document.getElementById('proveedores-pendientes').textContent = estadisticas.proveedores_pendientes || 0;
    document.getElementById('proveedores-inactivos').textContent = estadisticas.proveedores_inactivos || 0;
}

// Mostrar modal de nuevo proveedor
function mostrarModalNuevoProveedor() {
    limpiarFormularioProveedor();
    proveedorEditando = null;

    // Restablecer título del modal y botón
    const titulo = document.querySelector('#modalProveedor .modal-title');
    const botonGuardar = document.getElementById('btnGuardarProveedor');

    if (titulo) {
        titulo.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Nuevo Proveedor';
    }
    if (botonGuardar) {
        botonGuardar.innerHTML = '<i class="bi bi-save me-1"></i>Guardar';
    }

    const modal = new bootstrap.Modal(document.getElementById('modalProveedor'));
    modal.show();
}

// Limpiar formulario de proveedor
function limpiarFormularioProveedor() {
    const form = document.getElementById('formProveedor');
    if (form) {
        form.reset();
    }

    // Limpiar validaciones
    const campos = document.querySelectorAll('.is-invalid, .is-valid');
    campos.forEach(campo => {
        campo.classList.remove('is-invalid', 'is-valid');
    });

    const feedback = document.querySelectorAll('.invalid-feedback, .valid-feedback');
    feedback.forEach(elemento => {
        elemento.remove();
    });
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

// Función de prueba para verificar clicks
function testEditarProveedor(id) {
    console.log('=== TEST EDITAR PROVEEDOR ===');
    console.log('Función llamada correctamente con ID:', id);
    alert(`Test: Editar proveedor ${id}`);

    // Llamar a la función real
    editarProveedor(id);
}

// Editar proveedor
async function editarProveedor(id) {
    console.log('=== EDITAR PROVEEDOR DEBUG ===');
    console.log('ID recibido:', id);

    try {
        console.log('Iniciando edición de proveedor...');
        mostrarCargando(true);

        console.log('Realizando fetch a:', `/proveedores/api/${id}`);
        const response = await fetch(`/proveedores/api/${id}`);
        console.log('Response status:', response.status, response.ok);

        if (response.ok) {
            const proveedor = await response.json();
            console.log('Datos del proveedor recibidos:', proveedor);
            proveedorEditando = proveedor;

            // Verificar que los elementos del formulario existan
            const elementos = [
                'proveedor-id',
                'proveedor-nombre',
                'proveedor-nif',
                'proveedor-cuenta-contable',
                'proveedor-direccion',
                'proveedor-contacto',
                'proveedor-telefono',
                'proveedor-email'
            ];

            elementos.forEach(id => {
                const elemento = document.getElementById(id);
                console.log(`Elemento ${id}:`, elemento ? 'existe' : 'NO EXISTE');
            });

            // Llenar el formulario
            document.getElementById('proveedor-id').value = proveedor.id;
            document.getElementById('proveedor-nombre').value = proveedor.nombre;
            document.getElementById('proveedor-nif').value = proveedor.nif;
            document.getElementById('proveedor-cuenta-contable').value = proveedor.cuenta_contable;
            document.getElementById('proveedor-direccion').value = proveedor.direccion || '';
            document.getElementById('proveedor-contacto').value = proveedor.contacto || '';
            document.getElementById('proveedor-telefono').value = proveedor.telefono || '';
            document.getElementById('proveedor-email').value = proveedor.email || '';

            // Cambiar título del modal
            const titulo = document.querySelector('#modalProveedor .modal-title');
            const botonGuardar = document.getElementById('btnGuardarProveedor');

            if (titulo) {
                titulo.innerHTML = '<i class="bi bi-pencil me-2"></i>Editar Proveedor';
            }
            if (botonGuardar) {
                botonGuardar.innerHTML = '<i class="bi bi-check-lg me-1"></i>Actualizar';
            }

            // Mostrar modal
            const modalElement = document.getElementById('modalProveedor');
            console.log('Modal element:', modalElement ? 'existe' : 'NO EXISTE');

            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                console.log('Mostrando modal...');
                modal.show();
            } else {
                console.error('Modal modalProveedor no encontrado');
            }
        } else {
            console.error('Error en response:', response.status);
            mostrarMensaje('Error al cargar datos del proveedor', 'danger');
        }
    } catch (error) {
        console.error('Error completo:', error);
        mostrarMensaje('Error de conexión al cargar proveedor', 'danger');
    } finally {
        console.log('Finalizando mostrarCargando...');
        mostrarCargando(false);
    }
}

// Eliminar proveedor (muestra modal de confirmación)
function eliminarProveedor(id, nombre) {
    console.log('Solicitud de eliminar proveedor:', id, nombre);
    mostrarConfirmacionEliminar(id, nombre);
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

            // Recargar lista y actualizar estadísticas
            cargarProveedores(currentPage);
            actualizarEstadisticas();
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

// Funciones auxiliares
function mostrarMensaje(mensaje, tipo = 'info') {
    // Crear alerta Bootstrap
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Agregar al inicio del contenedor principal
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function mostrarCargando(mostrar) {
    console.log('mostrarCargando llamado con:', mostrar);

    // Buscar el botón en diferentes formas
    let boton = document.querySelector('#modalProveedor .btn-primary');

    if (!boton) {
        // Buscar por ID específico si existe
        boton = document.querySelector('#boton-guardar-proveedor');
    }

    if (!boton) {
        // Buscar cualquier botón con el texto de guardar
        boton = document.querySelector('button[onclick="guardarProveedor()"]');
    }

    console.log('Botón encontrado:', boton ? 'sí' : 'no');

    if (boton) {
        if (mostrar) {
            boton.disabled = true;
            boton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cargando...';
        } else {
            boton.disabled = false;
            const textoBoton = document.getElementById('boton-guardar-texto');
            if (textoBoton) {
                boton.innerHTML = `<i class="bi bi-check-lg me-1"></i><span id="boton-guardar-texto">${textoBoton.textContent}</span>`;
            } else {
                boton.innerHTML = '<i class="bi bi-check-lg me-1"></i>Guardar Proveedor';
            }
        }
    } else {
        console.warn('No se encontró el botón para mostrar estado de carga');
    }
}

// Exportar proveedores a CSV
async function exportarCSV() {
    try {
        if (typeof descargarCSVMejorado === 'function') {
            await descargarCSVMejorado('/proveedores/exportar-csv', 'proveedores_{fecha}', 'CSV');
        } else {
            // Fallback simple
            window.open('/proveedores/exportar-csv', '_blank');
        }
    } catch (error) {
        console.error('Error exportando CSV:', error);
        mostrarMensaje('Error al exportar CSV', 'danger');
    }
}

// Filtrar proveedores usando los filtros del formulario
function filtrarProveedores() {
    console.log('Filtrando proveedores...');

    const buscar = document.getElementById('filtro-buscar')?.value?.trim() || '';
    const estado = document.getElementById('filtro-estado')?.value || '';

    console.log('Filtros:', { buscar, estado });

    // Construir parámetros de filtro
    const params = new URLSearchParams({
        page: 1,
        per_page: perPage
    });

    // Nota: El backend ahora muestra todos los proveedores (activos e inactivos)
    // y soporta búsqueda general con el parámetro 'q'
    if (buscar) {
        params.append('q', buscar);
    }

    // El filtro de estado se aplica en el frontend en cargarProveedoresConFiltros

    // Realizar búsqueda con filtros
    cargarProveedoresConFiltros(params);
}

// Cargar proveedores con filtros específicos
async function cargarProveedoresConFiltros(params) {
    try {
        mostrarCargando(true);

        const response = await fetch(`/proveedores/api?${params}`);
        if (response.ok) {
            const data = await response.json();
            let proveedoresFiltrados = data.items || [];

            // Aplicar filtro de estado en el frontend
            const estadoFiltro = document.getElementById('filtro-estado')?.value || '';
            if (estadoFiltro === 'activo') {
                proveedoresFiltrados = proveedoresFiltrados.filter(p => p.activo);
            } else if (estadoFiltro === 'inactivo') {
                proveedoresFiltrados = proveedoresFiltrados.filter(p => !p.activo);
            }

            proveedores = proveedoresFiltrados;
            mostrarProveedores(proveedores);
            actualizarContadorProveedores(data.total || proveedores.length);

            // Actualizar paginación si existe
            if (typeof paginacionProveedores !== 'undefined' && paginacionProveedores.render) {
                paginacionProveedores.render(data.page, data.per_page, data.total);
            }
        } else {
            console.error('Error al filtrar proveedores');
            mostrarMensaje('Error al filtrar proveedores', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al filtrar proveedores', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Limpiar filtros (alias para limpiarFiltrosProveedores)
function limpiarFiltros() {
    console.log('Limpiando filtros...');

    // Limpiar campos de filtro
    const filtroBuscar = document.getElementById('filtro-buscar');
    const filtroEstado = document.getElementById('filtro-estado');

    if (filtroBuscar) filtroBuscar.value = '';
    if (filtroEstado) filtroEstado.value = ''; // Mostrar todos por defecto

    // Recargar lista completa
    cargarProveedores(1);
}

// Variable para el proveedor a eliminar
let proveedorAEliminar = null;

// Confirmar eliminación de proveedor
function confirmarEliminarProveedor() {
    if (proveedorAEliminar) {
        eliminarProveedorConfirmado(proveedorAEliminar.id);

        // Cerrar modal de confirmación
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalEliminarProveedor'));
        if (modal) {
            modal.hide();
        }

        proveedorAEliminar = null;
    }
}

// Mostrar modal de confirmación antes de eliminar
function mostrarConfirmacionEliminar(id, nombre) {
    proveedorAEliminar = { id, nombre };

    // Actualizar nombre en el modal
    const nombreElement = document.getElementById('nombre-proveedor-eliminar');
    if (nombreElement) {
        nombreElement.textContent = nombre;
    }

    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalEliminarProveedor'));
    modal.show();
}

// Eliminar proveedor confirmado
async function eliminarProveedorConfirmado(id) {
    try {
        mostrarCargando(true);

        const response = await fetch(`/proveedores/api/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            mostrarMensaje('Proveedor eliminado exitosamente', 'success');
            cargarProveedores(currentPage); // Recargar la página actual
            actualizarEstadisticas(); // Actualizar estadísticas
        } else {
            const errorData = await response.json();
            mostrarMensaje(errorData.error || 'Error al eliminar proveedor', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión al eliminar proveedor', 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Ver detalles del proveedor (modo solo lectura)
async function verProveedor(id) {
    try {
        mostrarCargando(true);

        const response = await fetch(`/proveedores/api/${id}`);
        if (response.ok) {
            const proveedor = await response.json();
            mostrarModalVerProveedor(proveedor);
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

// Mostrar modal de ver proveedor (solo lectura)
function mostrarModalVerProveedor(proveedor) {
    // Crear modal dinámico si no existe
    let modalVer = document.getElementById('modalVerProveedor');
    if (!modalVer) {
        modalVer = crearModalVerProveedor();
        document.body.appendChild(modalVer);
    }

    // Llenar datos del proveedor
    document.getElementById('ver-proveedor-nombre').textContent = proveedor.nombre;
    document.getElementById('ver-proveedor-nif').textContent = proveedor.nif;
    document.getElementById('ver-proveedor-cuenta-contable').textContent = proveedor.cuenta_contable;
    document.getElementById('ver-proveedor-direccion').textContent = proveedor.direccion || 'No especificada';
    document.getElementById('ver-proveedor-contacto').textContent = proveedor.contacto || 'No especificado';
    document.getElementById('ver-proveedor-telefono').textContent = proveedor.telefono || 'No especificado';
    document.getElementById('ver-proveedor-email').textContent = proveedor.email || 'No especificado';

    // Estado con badge
    const estadoBadge = document.getElementById('ver-proveedor-estado');
    estadoBadge.className = `badge ${proveedor.activo ? 'bg-success' : 'bg-secondary'}`;
    estadoBadge.textContent = proveedor.activo ? 'Activo' : 'Inactivo';

    // Mostrar modal
    const modal = new bootstrap.Modal(modalVer);
    modal.show();
}

// Crear el modal de ver proveedor dinámicamente
function crearModalVerProveedor() {
    const modalHTML = `
        <div class="modal fade" id="modalVerProveedor" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-eye me-2"></i>Detalles del Proveedor
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="text-muted">Información Básica</h6>
                                <p><strong>Nombre:</strong> <span id="ver-proveedor-nombre">-</span></p>
                                <p><strong>NIF:</strong> <span id="ver-proveedor-nif">-</span></p>
                                <p><strong>Cuenta Contable:</strong> <span id="ver-proveedor-cuenta-contable">-</span></p>
                                <p><strong>Estado:</strong> <span class="badge bg-success" id="ver-proveedor-estado">Activo</span></p>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-muted">Información de Contacto</h6>
                                <p><strong>Persona de Contacto:</strong> <span id="ver-proveedor-contacto">-</span></p>
                                <p><strong>Teléfono:</strong> <span id="ver-proveedor-telefono">-</span></p>
                                <p><strong>Email:</strong> <span id="ver-proveedor-email">-</span></p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h6 class="text-muted">Dirección</h6>
                            <p id="ver-proveedor-direccion">-</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="editarProveedorDesdeVer()">
                            <i class="bi bi-pencil me-1"></i>Editar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    const modalElement = document.createElement('div');
    modalElement.innerHTML = modalHTML;
    return modalElement.firstElementChild;
}

// Función auxiliar para editar desde el modal de ver
function editarProveedorDesdeVer() {
    // Cerrar modal de ver
    const modalVer = bootstrap.Modal.getInstance(document.getElementById('modalVerProveedor'));
    if (modalVer) {
        modalVer.hide();
    }

    // Obtener ID del proveedor desde los datos mostrados
    const nif = document.getElementById('ver-proveedor-nif').textContent;
    const proveedorActual = proveedores.find(p => p.nif === nif);

    if (proveedorActual) {
        editarProveedor(proveedorActual.id);
    }
}

// Función para activar/desactivar proveedor
async function toggleProveedor(id) {
    try {
        const response = await fetch(`/proveedores/api/${id}/toggle`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            mostrarMensaje(data.message, 'success');
            // Recargar la lista de proveedores
            await cargarProveedores();
        } else {
            mostrarMensaje(data.message || 'Error al cambiar estado del proveedor', 'danger');
        }
    } catch (error) {
        console.error('Error al cambiar estado del proveedor:', error);
        mostrarMensaje('Error de conexión al cambiar estado del proveedor', 'danger');
    }
}