// inventario.js - Funcionalidad para el módulo de inventario

console.log('🔧 inventario.js cargado correctamente');

// Variables globales
let articulosActuales = [];
let paginaActual = 1;
let articulosPorPagina = 10;
let filtrosAplicados = {};

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Inicializando módulo de inventario...');
    console.log('📍 DOM elementos encontrados:');
    console.log('- tabla-inventario-body:', document.getElementById('tabla-inventario-body') ? '✅' : '❌');

    // Cargar datos iniciales
    console.log('📊 Cargando estadísticas...');
    cargarEstadisticas();

    console.log('📦 Cargando artículos...');
    cargarArticulos();

    // Configurar eventos de filtros
    configurarEventosFiltros();

    // Configurar grupo contable automático
    configurarGrupoContable();

    // Configurar autocompletado
    configurarAutocompletado();
});

// Función para mostrar estado de carga en la tabla
function mostrarCargando() {
    const tbody = document.getElementById('tabla-inventario-body');
    if (tbody) {
        tbody.innerHTML = `
            <tr id="loading-row">
                <td colspan="10" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2 text-muted">Cargando artículos...</p>
                </td>
            </tr>
        `;
    }
}

// Función para cargar estadísticas del dashboard
async function cargarEstadisticas() {
    try {
        const response = await fetch('/inventario/api/estadisticas');
        const data = await response.json();

        if (response.ok) {
            actualizarTarjetasEstadisticas(data);
        } else {
            console.error('Error al cargar estadísticas:', data.error);
        }
    } catch (error) {
        console.error('Error en petición de estadísticas:', error);
    }
}

// Actualizar tarjetas de estadísticas
function actualizarTarjetasEstadisticas(stats) {
    document.getElementById('total-articulos').textContent = stats.total_articulos || 0;
    document.getElementById('valor-stock').textContent = formatearMoneda(stats.valor_total_stock || 0);
    document.getElementById('stock-bajo').textContent = stats.articulos_bajo_minimo || 0;
    document.getElementById('articulos-criticos').textContent = stats.articulos_criticos || 0;
}

// Función para cargar artículos con filtros y paginación
async function cargarArticulos(page = 1, filtros = {}) {
    console.log('🔄 cargarArticulos iniciado - página:', page, 'filtros:', filtros);

    const tbody = document.getElementById('tabla-inventario-body');
    console.log('📋 tbody encontrado:', tbody ? '✅' : '❌');

    // Mostrar estado de carga solo si no es la primera carga
    if (!tbody.querySelector('#loading-row')) {
        console.log('📍 Mostrando spinner de carga...');
        mostrarCargando();
    }

    try {
        // Construir URL con parámetros
        const params = new URLSearchParams({
            page: page,
            per_page: articulosPorPagina,
            ...filtros
        });

        const url = `/inventario/api/articulos?${params}`;
        console.log('🌐 Haciendo fetch a:', url);

        const response = await fetch(url);
        console.log('📡 Respuesta recibida - Status:', response.status);

        const data = await response.json();
        console.log('📦 Datos recibidos:', data);
        console.log('📊 Total artículos:', data.total);
        console.log('📋 Cantidad de artículos:', data.articulos ? data.articulos.length : 0);

        if (response.ok) {
            console.log('✅ Respuesta exitosa, procesando datos...');
            articulosActuales = data.articulos;

            console.log('📝 Llamando a actualizarTablaArticulos...');
            actualizarTablaArticulos(data.articulos);
            console.log('📄 actualizarTablaArticulos completado');

            console.log('📊 Llamando a actualizarPaginacion...');
            actualizarPaginacion(data.total, page, articulosPorPagina);

            // Actualizar contadores
            const totalElement = document.getElementById('total-resultados');
            if (totalElement) totalElement.textContent = data.total;

            const articulosMostrados = document.getElementById('articulos-mostrados');
            if (articulosMostrados) articulosMostrados.textContent = data.articulos.length;

            const totalFiltrados = document.getElementById('total-articulos-filtrados');
            if (totalFiltrados) totalFiltrados.textContent = data.total;

        } else {
            // En caso de error, limpiar tabla y mostrar mensaje
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center py-4">
                        <div class="alert alert-warning mb-0">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error al cargar artículos: ${data.error || 'Error desconocido'}
                        </div>
                    </td>
                </tr>
            `;
            mostrarAlerta('Error al cargar artículos: ' + (data.error || 'Error desconocido'), 'danger');
        }
    } catch (error) {
        console.error('❌ Error al cargar artículos:', error);
        console.log('🔧 Detalles del error:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });

        // En caso de error de conexión, limpiar tabla y mostrar mensaje
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-4">
                    <div class="alert alert-danger mb-0">
                        <i class="fas fa-wifi me-2"></i>
                        Error de conexión. Verifique su conexión a internet.
                    </div>
                    <button class="btn btn-primary mt-2" onclick="cargarArticulos()">
                        <i class="fas fa-redo me-1"></i>Reintentar
                    </button>
                </td>
            </tr>
        `;
        mostrarAlerta('Error de conexión al cargar artículos', 'danger');
    }
}

// Actualizar tabla de artículos
function actualizarTablaArticulos(articulos) {
    const tbody = document.getElementById('tabla-inventario-body');
    tbody.innerHTML = '';

    if (!articulos || articulos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-4">
                    <div class="text-muted">
                        <i class="fas fa-box-open fa-3x mb-3 opacity-25"></i>
                        <p class="mb-0">No se encontraron artículos</p>
                        <small>Intente ajustar los filtros de búsqueda</small>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    articulos.forEach(articulo => {
        const tr = document.createElement('tr');

        // Determinar estado y clase CSS
        let estadoClass = 'success';
        let estadoText = 'Normal';
        let estadoBadge = 'bg-success';

        if (articulo.stock_actual === 0) {
            estadoClass = 'danger';
            estadoText = 'Sin Stock';
            estadoBadge = 'bg-danger';
        } else if (articulo.necesita_reposicion) {
            estadoClass = 'warning';
            estadoText = 'Bajo Mínimo';
            estadoBadge = 'bg-warning';
        }

        if (articulo.critico) {
            estadoText += ' (Crítico)';
            estadoBadge = 'bg-danger';
        }

        tr.innerHTML = `
            <td><code>${articulo.codigo}</code></td>
            <td>
                ${articulo.descripcion}
                ${articulo.critico ? '<i class="fas fa-exclamation-triangle text-danger ms-1" title="Crítico"></i>' : ''}
            </td>
            <td>
                ${articulo.categoria ? `<span class="badge bg-secondary">${articulo.categoria}</span>` : '-'}
            </td>
            <td>
                <span class="badge ${estadoBadge}">${articulo.stock_actual}</span>
                <small class="text-muted d-block">${articulo.unidad_medida || 'UND'}</small>
            </td>
            <td>
                <small class="text-muted">
                    Mín: ${articulo.stock_minimo}<br>
                    Máx: ${articulo.stock_maximo}
                </small>
            </td>
            <td>
                ${articulo.ubicacion || '-'}
            </td>
            <td>
                ${articulo.precio_promedio ? formatearMoneda(articulo.precio_promedio) : '-'}
            </td>
            <td>
                <strong>${formatearMoneda(articulo.valor_stock || 0)}</strong>
            </td>
            <td>
                <span class="badge ${estadoBadge}">${estadoText}</span>
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-primary" onclick="editarArticulo(${articulo.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-outline-success" onclick="mostrarModalMovimiento(${articulo.id}, '${articulo.codigo}', '${articulo.descripcion}')" title="Movimiento">
                        <i class="fas fa-exchange-alt"></i>
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="verHistorial(${articulo.id})" title="Historial">
                        <i class="fas fa-history"></i>
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

// Configurar eventos de filtros
function configurarEventosFiltros() {
    // Filtros de texto con debounce
    const filtrosTexto = ['filtro-codigo', 'filtro-descripcion', 'filtro-ubicacion'];
    filtrosTexto.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', debounce(aplicarFiltros, 500));
        }
    });

    // Filtros de selección
    const filtrosSelect = ['filtro-categoria'];
    filtrosSelect.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            select.addEventListener('change', aplicarFiltros);
        }
    });

    // Checkboxes
    const checkboxes = ['filtro-bajo-minimo', 'filtro-critico'];
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', aplicarFiltros);
        }
    });
}

// Aplicar filtros
function aplicarFiltros() {
    const filtros = {};

    // Filtros de texto
    const codigo = document.getElementById('filtro-codigo').value.trim();
    if (codigo) filtros.codigo = codigo;

    const descripcion = document.getElementById('filtro-descripcion').value.trim();
    if (descripcion) filtros.descripcion = descripcion;

    const ubicacion = document.getElementById('filtro-ubicacion').value.trim();
    if (ubicacion) filtros.ubicacion = ubicacion;

    // Filtros de selección
    const categoria = document.getElementById('filtro-categoria').value;
    if (categoria) filtros.categoria = categoria;

    // Checkboxes
    if (document.getElementById('filtro-bajo-minimo').checked) {
        filtros.bajo_minimo = 'true';
    }

    if (document.getElementById('filtro-critico').checked) {
        filtros.critico = 'true';
    }

    filtrosAplicados = filtros;
    paginaActual = 1;
    cargarArticulos(paginaActual, filtros);
}

// Limpiar filtros
function limpiarFiltros() {
    document.getElementById('filtro-codigo').value = '';
    document.getElementById('filtro-descripcion').value = '';
    document.getElementById('filtro-ubicacion').value = '';
    document.getElementById('filtro-categoria').value = '';
    document.getElementById('filtro-bajo-minimo').checked = false;
    document.getElementById('filtro-critico').checked = false;

    filtrosAplicados = {};
    paginaActual = 1;
    cargarArticulos();
}

// Mostrar modal nuevo artículo
function mostrarModalNuevoArticulo() {
    const modal = new bootstrap.Modal(document.getElementById('modalNuevoArticulo'));
    document.getElementById('formNuevoArticulo').reset();

    // Establecer valores por defecto
    document.getElementById('nuevo-cuenta-contable').value = '622000000';
    document.getElementById('nuevo-requiere-conteo').checked = true;

    modal.show();
}

// Configurar grupo contable automático
function configurarGrupoContable() {
    const grupoSelect = document.getElementById('nuevo-grupo-contable');
    const cuentaInput = document.getElementById('nuevo-cuenta-contable');

    if (grupoSelect && cuentaInput) {
        grupoSelect.addEventListener('change', function () {
            if (this.value === '60') {
                cuentaInput.value = '600000000';
                mostrarAlerta('Cuenta contable actualizada para grupo 60', 'info');
            } else {
                cuentaInput.value = '622000000';
            }
        });
    }
}

// Guardar nuevo artículo
async function guardarNuevoArticulo() {
    const form = document.getElementById('formNuevoArticulo');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        codigo: document.getElementById('nuevo-codigo').value,
        descripcion: document.getElementById('nuevo-descripcion').value,
        categoria: document.getElementById('nuevo-categoria').value,
        stock_minimo: parseInt(document.getElementById('nuevo-stock-minimo').value) || 0,
        stock_maximo: parseInt(document.getElementById('nuevo-stock-maximo').value) || 100,
        ubicacion: document.getElementById('nuevo-ubicacion').value,
        precio_unitario: parseFloat(document.getElementById('nuevo-precio-unitario').value) || null,
        unidad_medida: document.getElementById('nuevo-unidad-medida').value,
        proveedor: document.getElementById('nuevo-proveedor').value,
        cuenta_contable_compra: document.getElementById('nuevo-cuenta-contable').value,
        grupo_contable: document.getElementById('nuevo-grupo-contable').value,
        critico: document.getElementById('nuevo-critico').checked,
        requiere_conteo: document.getElementById('nuevo-requiere-conteo').checked
    };

    try {
        const response = await fetch('/inventario/api/articulos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            mostrarAlerta('Artículo creado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalNuevoArticulo')).hide();
            cargarArticulos(paginaActual, filtrosAplicados);
            cargarEstadisticas();
        } else {
            mostrarAlerta('Error: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'danger');
    }
}

// Mostrar modal de movimiento
function mostrarModalMovimiento(articuloId, codigo, descripcion) {
    document.getElementById('movimiento-articulo-id').value = articuloId;
    document.getElementById('movimiento-articulo-info').value = `${codigo} - ${descripcion}`;
    document.getElementById('formMovimiento').reset();
    document.getElementById('movimiento-articulo-id').value = articuloId;

    const modal = new bootstrap.Modal(document.getElementById('modalMovimiento'));
    modal.show();
}

// Guardar movimiento
async function guardarMovimiento() {
    const form = document.getElementById('formMovimiento');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        tipo: document.getElementById('movimiento-tipo').value,
        cantidad: parseInt(document.getElementById('movimiento-cantidad').value),
        motivo: document.getElementById('movimiento-motivo').value
    };

    try {
        const response = await fetch('/inventario/api/movimientos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...data,
                inventario_id: parseInt(document.getElementById('movimiento-articulo-id').value)
            })
        });

        const result = await response.json();

        if (response.ok) {
            mostrarAlerta('Movimiento registrado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalMovimiento')).hide();
            cargarArticulos(paginaActual, filtrosAplicados);
            cargarEstadisticas();
        } else {
            mostrarAlerta('Error: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'danger');
    }
}

// Funciones de paginación
function actualizarPaginacion(total, paginaActual, porPagina) {
    const totalPaginas = Math.ceil(total / porPagina);
    const pagination = document.getElementById('paginacion-inventario');
    pagination.innerHTML = '';

    if (totalPaginas <= 1) return;

    // Botón anterior
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${paginaActual === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="cambiarPagina(${paginaActual - 1})">Anterior</a>`;
    pagination.appendChild(prevLi);

    // Números de página
    const inicio = Math.max(1, paginaActual - 2);
    const fin = Math.min(totalPaginas, paginaActual + 2);

    for (let i = inicio; i <= fin; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === paginaActual ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="cambiarPagina(${i})">${i}</a>`;
        pagination.appendChild(li);
    }

    // Botón siguiente
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${paginaActual === totalPaginas ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="cambiarPagina(${paginaActual + 1})">Siguiente</a>`;
    pagination.appendChild(nextLi);
}

function cambiarPagina(nuevaPagina) {
    if (nuevaPagina < 1) return;
    paginaActual = nuevaPagina;
    cargarArticulos(paginaActual, filtrosAplicados);
}

// Funciones auxiliares
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(valor);
}

function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function mostrarAlerta(mensaje, tipo) {
    // Crear contenedor si no existe
    let alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '1055';
        document.body.appendChild(alertContainer);
    }

    // Crear alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.appendChild(alertDiv);

    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Funciones placeholder para futuras implementaciones
function editarArticulo(id) {
    mostrarAlerta('Función de edición en desarrollo', 'info');
}

function verHistorial(id) {
    mostrarAlerta('Historial de movimientos en desarrollo', 'info');
}

function mostrarMovimientos() {
    mostrarAlerta('Vista de movimientos en desarrollo', 'info');
}

// Exportar funciones globales
window.mostrarModalNuevoArticulo = mostrarModalNuevoArticulo;
window.guardarNuevoArticulo = guardarNuevoArticulo;
window.mostrarModalMovimiento = mostrarModalMovimiento;
window.guardarMovimiento = guardarMovimiento;
window.aplicarFiltros = aplicarFiltros;
window.limpiarFiltros = limpiarFiltros;
window.cambiarPagina = cambiarPagina;
window.editarArticulo = editarArticulo;
window.verHistorial = verHistorial;
window.mostrarMovimientos = mostrarMovimientos;

function configurarAutocompletado() {
    if (!window.AutoComplete) {
        console.log('❌ AutoComplete no disponible');
        return;
    }

    const campoBuscar = document.getElementById('search-inventario');
    if (campoBuscar) {
        new AutoComplete({
            element: campoBuscar,
            apiUrl: '/inventario/api',
            searchKey: 'q',
            displayKey: item => `${item.codigo} - ${item.descripcion}`,
            valueKey: 'codigo',
            placeholder: 'Buscar por código, descripción o categoría...',
            allowFreeText: true,
            customFilter: (item, query) => {
                const q = query.toLowerCase();
                return item.codigo.toLowerCase().includes(q) ||
                    item.descripcion.toLowerCase().includes(q) ||
                    (item.categoria && item.categoria.toLowerCase().includes(q));
            },
            onSelect: (item) => {
                console.log('📦 Item de inventario seleccionado:', item);
                cargarInventario(1);
            }
        });
        console.log('✅ Autocompletado de inventario configurado');
    }
}

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

    fetch(`/inventario/api?${params}`)
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
