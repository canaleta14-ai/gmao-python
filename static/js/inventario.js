// inventario.js - Funcionalidad para el módulo de inventario

console.log('🔧 inventario.js cargado correctamente');

// Variables globales
let articulosActuales = [];
let paginaActual = 1;
let articulosPorPagina = 10;
let filtrosAplicados = {};
let paginacionInventario;
let categoriasDisponibles = []; // Nuevo: array para categorías dinámicas

// Clase principal de la aplicación de inventario
class InventarioApp {
    constructor() {
        this.categorias = [];
        this.articuloSeleccionado = null;
    }

    async init() {
        await this.cargarCategorias();
        this.setupEventListeners();
    }

    async cargarCategorias() {
        try {
            const response = await fetch('/api/categorias/');
            const data = await response.json();

            if (data.success) {
                this.categorias = data.categorias;
                categoriasDisponibles = data.categorias; // Mantener compatibilidad
                this.actualizarSelectoresCategorias();
                console.log('✅ Categorías cargadas:', this.categorias.length);
            } else {
                console.error('Error cargando categorías:', data.message);
            }
        } catch (error) {
            console.error('Error en petición de categorías:', error);
        }
    }

    actualizarSelectoresCategorias() {
        const selectores = ['filtro-categoria', 'nuevo-categoria'];

        selectores.forEach(selectorId => {
            const select = document.getElementById(selectorId);
            if (select) {
                // Mantener la primera opción
                const primeraOpcion = select.querySelector('option[value=""]');
                select.innerHTML = '';

                if (primeraOpcion) {
                    select.appendChild(primeraOpcion);
                }

                // Añadir categorías dinámicas
                this.categorias.forEach(categoria => {
                    if (categoria.activo) {
                        const option = document.createElement('option');
                        option.value = categoria.id;
                        option.textContent = `${categoria.nombre} (${categoria.prefijo})`;
                        option.dataset.prefijo = categoria.prefijo;
                        option.dataset.color = categoria.color;
                        select.appendChild(option);
                    }
                });
            }
        });
    }

    categoriaSeleccionada() {
        const select = document.getElementById('nuevo-categoria');
        const previewSpan = document.getElementById('categoria-preview');
        const codigoInput = document.getElementById('nuevo-codigo');

        if (select && select.value) {
            const categoria = this.categorias.find(c => c.id == select.value);
            if (categoria) {
                // Mostrar preview
                if (previewSpan) {
                    previewSpan.innerHTML = `
                        <span class="badge" style="background-color: ${categoria.color}">
                            ${categoria.prefijo}
                        </span>
                        Próximo código: ${categoria.prefijo}-${new Date().getFullYear()}-${String(categoria.ultimo_numero + 1).padStart(3, '0')}
                    `;
                }

                // Limpiar código actual para generar uno nuevo
                if (codigoInput) {
                    codigoInput.value = '';
                    codigoInput.placeholder = 'Se generará automáticamente';
                }
            }
        } else {
            if (previewSpan) previewSpan.innerHTML = '';
            if (codigoInput) codigoInput.placeholder = 'Ingrese código manualmente';
        }
    }

    async generarCodigoAutomatico() {
        const categoriaSelect = document.getElementById('nuevo-categoria');
        const codigoInput = document.getElementById('nuevo-codigo');

        if (!categoriaSelect || !categoriaSelect.value) {
            alert('Por favor seleccione una categoría primero');
            return;
        }

        try {
            const response = await fetch(`/api/categorias/${categoriaSelect.value}/codigo`);
            const data = await response.json();

            if (data.success) {
                codigoInput.value = data.codigo;

                // Actualizar el último número en la categoría local
                const categoria = this.categorias.find(c => c.id == categoriaSelect.value);
                if (categoria) {
                    categoria.ultimo_numero = data.siguiente_numero;
                }

                console.log('✅ Código generado:', data.codigo);
            } else {
                alert('Error al generar código: ' + data.message);
            }
        } catch (error) {
            console.error('Error generando código:', error);
            alert('Error de conexión');
        }
    }

    async crearCategoriaRapida() {
        const nombre = document.getElementById('rapida-nombre').value.trim();
        const prefijo = document.getElementById('rapida-prefijo').value.trim().toUpperCase();
        const color = document.getElementById('rapida-color').value;

        if (!nombre || !prefijo) {
            alert('El nombre y prefijo son requeridos');
            return;
        }

        try {
            const response = await fetch('/api/categorias/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, prefijo, color })
            });

            const data = await response.json();

            if (data.success) {
                // Recargar categorías
                await this.cargarCategorias();

                // Seleccionar la nueva categoría
                const select = document.getElementById('nuevo-categoria');
                if (select && data.categoria) {
                    select.value = data.categoria.id;
                    this.categoriaSeleccionada();
                }

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalCategoria'));
                if (modal) modal.hide();

                // Limpiar formulario
                document.getElementById('formCategoriaRapida').reset();

                alert('Categoría creada exitosamente');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error creando categoría:', error);
            alert('Error de conexión');
        }
    }

    setupEventListeners() {
        // Eventos específicos de categorías ya están en el HTML
        console.log('✅ Event listeners de categorías configurados');
    }
}

// Instancia global de la aplicación
let inventarioApp;

console.log('🔧 inventario.js cargado correctamente');

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Inicializando módulo de inventario...');
    console.log('üìç DOM elements check:');
    console.log('- tabla-inventario-body:', document.getElementById('tabla-inventario-body') ? '✅' : '❌');
    console.log('- paginacion-inventario:', document.getElementById('paginacion-inventario') ? '✅' : '❌');

    // Inicializar paginación
    console.log('üìÑ Inicializando paginación...');
    paginacionInventario = createPagination('paginacion-inventario', cargarArticulos, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true
    });
    console.log('üìÑ Paginación inicializada:', paginacionInventario ? '✅' : '❌');

    // Cargar datos iniciales
    console.log('üìä Cargando estadísticas...');
    cargarEstadisticas();

    console.log('üì¶ Cargando artículos...');
    cargarArticulos();

    // Configurar eventos de filtros
    configurarEventosFiltros();

    // Configurar grupo contable automático
    configurarGrupoContable();

    // Configurar autocompletado
    configurarAutocompletado();

    console.log('✅ Inicialización de inventario completada');
});

// Función para mostrar/ocultar estado de carga en la tabla
function mostrarCargando(mostrar = true) {
    const tbody = document.getElementById('tabla-inventario-body');
    if (!tbody) return;

    if (mostrar) {
        // Solo mostrar loading si no hay ya un loading-row
        if (!tbody.querySelector('#loading-row')) {
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
    } else {
        // Ocultar loading: eliminar solo la fila de loading si existe
        const loadingRow = tbody.querySelector('#loading-row');
        if (loadingRow) {
            loadingRow.remove();
        }
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
    console.log('🔄 cargarArticulos iniciado - página:', page, 'filtros:', filtros);

    const tbody = document.getElementById('tabla-inventario-body');
    console.log('üìã tbody encontrado:', tbody ? '✅' : '❌');

    // Mostrar estado de carga solo si no es la primera carga
    if (!tbody.querySelector('#loading-row')) {
        console.log('üìç Mostrando spinner de carga...');
        mostrarCargando(true);
    }

    try {
        // Construir URL con parámetros
        const params = new URLSearchParams({
            page: page,
            per_page: articulosPorPagina,
            ...filtros
        });

        const url = `/inventario/api/articulos?${params}`;
        console.log('üåê Haciendo fetch a:', url);

        const response = await fetch(url);
        console.log('üì° Respuesta recibida - Status:', response.status, 'Content-Type:', response.headers.get('content-type'));

        if (response.status === 401 || response.status === 302) {
            console.log('üîê Redirección de autenticación detectada - redirigiendo al login');
            window.location.href = '/login';
            return;
        }

        const data = await response.json();
        console.log('üì¶ Datos recibidos:', data);
        console.log('üìä Total artículos:', data.total);
        console.log('üìã Cantidad de artículos:', data.articulos ? data.articulos.length : 0);

        if (response.ok) {
            console.log('✅ Respuesta exitosa, procesando datos...');
            articulosActuales = data.articulos;

            console.log('üìù Llamando a actualizarTablaArticulos...');
            actualizarTablaArticulos(data.articulos);
            console.log('üìÑ actualizarTablaArticulos completado');

            // Renderizar paginación
            if (typeof paginacionInventario !== 'undefined' && paginacionInventario.render) {
                paginacionInventario.render(data.page, data.per_page, data.total);
            }

            // Actualizar contadores
            const totalElement = document.getElementById('total-resultados');
            if (totalElement) totalElement.textContent = data.total;

            const articulosMostrados = document.getElementById('articulos-mostrados');
            if (articulosMostrados) articulosMostrados.textContent = data.articulos.length;

            const totalFiltrados = document.getElementById('total-articulos-filtrados');
            if (totalFiltrados) totalFiltrados.textContent = data.total;

        } else {
            // En caso de error, limpiar tabla y mostrar mensaje
            console.error('❌ Error en respuesta:', data);
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
        console.log('🔧 Detalles del error:', {
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
                <strong>${articulo.descripcion}</strong>
                ${articulo.critico ? '<i class="bi bi-exclamation-triangle-fill text-danger ms-1" title="Artículo Crítico"></i>' : ''}
            </td>
            <td>
                ${articulo.categoria ? `<span class="badge bg-secondary">${articulo.categoria}</span>` : '<span class="text-muted">-</span>'}
            </td>
            <td>
                <span class="badge ${estadoBadge} me-1">${articulo.stock_actual}</span>
                <small class="text-muted">${articulo.unidad_medida || 'UND'}</small>
            </td>
            <td>
                <small class="text-muted">
                    <div><strong>${articulo.stock_minimo}</strong></div>
                    <div><strong>${articulo.stock_maximo}</strong></div>
                </small>
            </td>
            <td>${articulo.ubicacion || '<span class="text-muted">-</span>'}</td>
            <td class="text-end">${articulo.precio_promedio ? formatearMoneda(articulo.precio_promedio) : '<span class="text-muted">-</span>'}</td>
            <td class="text-end"><strong class="text-success">${formatearMoneda(articulo.valor_stock || 0)}</strong></td>
            <td><span class="badge ${estadoBadge}">${estadoText}</span></td>
            <td class="text-center">
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="editarArticulo(${articulo.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-success" onclick="mostrarModalMovimiento(${articulo.id}, '${articulo.codigo}', '${articulo.descripcion}')" title="Movimiento">
                        <i class="bi bi-arrow-left-right"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info" onclick="verHistorial(${articulo.id})" title="Historial">
                        <i class="bi bi-clock-history"></i>
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
    document.getElementById('nuevo-activo').checked = true;

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
        activo: document.getElementById('nuevo-activo').checked
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
function mostrarModalMovimiento(articuloId = null, codigo = '', descripcion = '') {
    console.log('📂 Abriendo modal de movimiento:', { articuloId, codigo, descripcion });

    // Limpiar formulario
    document.getElementById('formMovimiento').reset();

    // Limpiar y forzar reinicialización del autocompletado
    const articuloInput = document.getElementById('movimiento-articulo-info');
    if (articuloInput) {
        articuloInput.dataset.autocompleteInitialized = '';
        articuloInput.value = '';
        console.log('🧹 Campo de artículo limpiado para nueva inicialización');
    }

    // Si se llama con parámetros específicos, pre-rellenar
    if (articuloId) {
        document.getElementById('movimiento-articulo-id').value = articuloId;
        const displayValue = `${codigo} - ${descripcion}`;
        if (articuloInput) {
            articuloInput.value = displayValue;
        }
        console.log('📝 Artículo pre-seleccionado:', displayValue);
    } else {
        // Si no hay artículo pre-seleccionado, limpiar
        document.getElementById('movimiento-articulo-id').value = '';
        console.log('🆕 Modal sin artículo pre-seleccionado');
    }

    const modal = new bootstrap.Modal(document.getElementById('modalMovimiento'));
    modal.show();

    // Siempre inicializar autocompletado después de mostrar el modal
    setTimeout(() => {
        console.log('⏰ Inicializando autocompletado después de mostrar modal...');
        initializeArticuloAutoComplete();
    }, 150);
}

// Función global para reinicializar autocompletado manualmente
window.reiniciarAutocompletado = function () {
    console.log('🔄 Reinicializando autocompletado manualmente...');
    const input = document.getElementById('movimiento-articulo-info');
    if (input) {
        // Forzar reinicialización
        input.dataset.autocompleteInitialized = '';
        initializeArticuloAutoComplete();
    } else {
        console.error('❌ Input no encontrado para reinicialización');
    }
};

// Función global para probar API manualmente
window.probarAPI = function (query = 'a') {
    console.log(`🧪 Probando API con query: "${query}"`);
    fetch(`/inventario/api/articulos?q=${query}&per_page=5`)
        .then(response => {
            console.log('📡 Status API:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos API:', data);
            if (data.articulos && data.articulos.length > 0) {
                console.log('✅ API funciona correctamente');
            } else {
                console.log('⚠️ API responde pero sin artículos');
            }
        })
        .catch(error => {
            console.error('❌ Error API:', error);
        });
};

// Inicializar autocompletado para artículos en modal de movimiento
function initializeArticuloAutoComplete() {
    console.log('🔧 Intentando inicializar autocompletado de artículos...');

    const input = document.getElementById('movimiento-articulo-info');
    if (!input) {
        console.error('❌ Input movimiento-articulo-info no encontrado');
        return;
    }

    if (input.dataset.autocompleteInitialized) {
        console.log('⚠️ Autocompletado ya inicializado, forzando reinicialización...');
        // Limpiar inicialización previa
        input.dataset.autocompleteInitialized = '';
        const wrapper = input.closest('.autocomplete-wrapper');
        if (wrapper) {
            console.log('🧹 Removiendo wrapper anterior');
            const originalInput = wrapper.querySelector('input[type="hidden"]');
            if (originalInput) {
                wrapper.parentNode.insertBefore(input, wrapper);
                wrapper.remove();
            }
        }
    }

    // Verificar que AutoComplete esté disponible
    if (typeof AutoComplete === 'undefined') {
        console.error('❌ AutoComplete no disponible. Reintentando en 1 segundo...');
        setTimeout(initializeArticuloAutoComplete, 1000);
        return;
    }

    console.log('✅ AutoComplete disponible, configurando...');

    try {
        // Crear configuración para AutoComplete
        console.log('🚀 Creando instancia de AutoComplete...');
        const autocompleteInstance = new AutoComplete({
            element: input,
            apiUrl: '/inventario/api/articulos',
            searchKey: 'q',
            displayKey: item => `${item.codigo} - ${item.descripcion}`,
            valueKey: 'id',
            minChars: 1,
            maxResults: 15,
            placeholder: 'Buscar artículo por código o descripción...',
            noResultsText: 'No se encontraron artículos',
            loadingText: 'Buscando artículos...',
            onSelect: (item) => {
                console.log('✅ Artículo seleccionado:', item);
                document.getElementById('movimiento-articulo-id').value = item.id;

                // Mostrar información adicional del stock
                const stockInfo = document.getElementById('stock-info-display');
                if (stockInfo) {
                    stockInfo.innerHTML = `
                        <small class="text-muted">
                            <strong>Stock:</strong> ${item.stock_actual || 0} | 
                            <strong>Mínimo:</strong> ${item.stock_minimo || 0} | 
                            <strong>Categoría:</strong> ${item.categoria || 'N/A'}
                        </small>
                    `;
                    stockInfo.style.display = 'block';
                }
            },
            onInput: (value) => {
                console.log('� Escribiendo:', value);
                // Limpiar selección si el usuario está escribiendo
                if (value.length < 2) {
                    document.getElementById('movimiento-articulo-id').value = '';
                    const stockInfo = document.getElementById('stock-info-display');
                    if (stockInfo) {
                        stockInfo.style.display = 'none';
                    }
                }
            }
        });

        input.dataset.autocompleteInitialized = 'true';

        // Remover readonly del input original
        input.removeAttribute('readonly');
        input.value = ''; // Limpiar cualquier valor existente

        console.log('✅ Autocompletado de artículos inicializado correctamente');

        return autocompleteInstance;

        // Test inmediato de la API
        setTimeout(() => {
            console.log('🧪 Probando API directamente...');
            fetch('/inventario/api/articulos?q=a&per_page=5')
                .then(response => {
                    console.log('📡 Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Respuesta de API:', data);
                    if (data.articulos && data.articulos.length > 0) {
                        console.log('✅ API funciona, artículos encontrados:', data.articulos.length);
                        console.log('📝 Primer artículo:', data.articulos[0]);
                    } else {
                        console.log('⚠️ API responde pero sin artículos');
                    }
                })
                .catch(error => {
                    console.error('❌ Error en API:', error);
                });
        }, 500);

        return autocompleteInstance;
    } catch (error) {
        console.error('❌ Error al inicializar autocompletado:', error);
        console.error('Error details:', error.stack);
    }
}

// Validar stock para movimientos de salida
function validarStockParaSalida(articulo) {
    const cantidadInput = document.getElementById('movimiento-cantidad');
    const stockAlert = document.getElementById('stock-alert');

    if (cantidadInput && stockAlert) {
        cantidadInput.addEventListener('input', function () {
            const cantidad = parseInt(this.value) || 0;

            if (cantidad > articulo.stock_actual) {
                stockAlert.innerHTML = `
                    <div class="alert alert-warning alert-sm mt-2">
                        <i class="fas fa-exclamation-triangle me-1"></i>
                        ⚠️ Cantidad solicitada (${cantidad}) supera el stock disponible (${articulo.stock_actual})
                    </div>
                `;
                stockAlert.style.display = 'block';
            } else if (cantidad > (articulo.stock_actual - articulo.stock_minimo)) {
                stockAlert.innerHTML = `
                    <div class="alert alert-info alert-sm mt-2">
                        <i class="fas fa-info-circle me-1"></i>
                        ℹ️ Esta salida dejará el stock por debajo del mínimo recomendado (${articulo.stock_minimo})
                    </div>
                `;
                stockAlert.style.display = 'block';
            } else {
                stockAlert.style.display = 'none';
            }
        });
    }
}

// Inicializar listeners para el modal de movimiento
function initializeMovimientoModalListeners() {
    const tipoSelect = document.getElementById('movimiento-tipo');
    const cantidadInput = document.getElementById('movimiento-cantidad');
    const stockAlert = document.getElementById('stock-alert');

    if (tipoSelect) {
        tipoSelect.addEventListener('change', function () {
            const articuloId = document.getElementById('movimiento-articulo-id').value;

            if (this.value === 'salida' && articuloId && articulosActuales.length > 0) {
                // Buscar el artículo actual para validar stock
                const articulo = articulosActuales.find(a => a.id == articuloId);
                if (articulo) {
                    validarStockParaSalida(articulo);
                }
            } else if (stockAlert) {
                stockAlert.style.display = 'none';
            }
        });
    }
}

// Función mejorada para mostrar un modal de movimiento general (sin artículo específico)
function mostrarModalMovimientoGeneral() {
    mostrarModalMovimiento(); // Llama sin parámetros para habilitar autocompletado
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
            // Usar el mensaje detallado de la API si está disponible
            let mensaje = result.message || 'Movimiento registrado exitosamente';

            // Si tenemos información del artículo, crear mensaje más descriptivo
            if (result.articulo && result.movimiento) {
                const articulo = result.articulo;
                const movimiento = result.movimiento;
                const tipo = movimiento.tipo;
                const cantidad = Math.abs(movimiento.cantidad);

                // Emojis y texto según el tipo de movimiento
                const tipoInfo = {
                    'entrada': { emoji: '📦➕', texto: 'entrada', color: 'success' },
                    'salida': { emoji: '📦➖', texto: 'salida', color: 'danger' },
                    'ajuste': { emoji: '⚖️', texto: 'ajuste', color: 'warning' },
                    'regularizacion': { emoji: '🔄', texto: 'regularización', color: 'info' }
                };

                const info = tipoInfo[tipo] || { emoji: '📦', texto: tipo, color: 'info' };

                // Crear mensaje enriquecido
                mensaje = `${info.emoji} Movimiento de ${info.texto} registrado: ${cantidad} unidades de ${articulo.codigo}`;

                // Agregar información de stock si está disponible
                if (articulo.stock_actual !== null) {
                    const stockAnterior = articulo.stock_anterior;
                    if (stockAnterior !== null && stockAnterior !== articulo.stock_actual) {
                        mensaje += `\n📊 Stock: ${stockAnterior} → ${articulo.stock_actual}`;
                    } else {
                        mensaje += `\n📊 Stock actual: ${articulo.stock_actual}`;
                    }
                }

                // Alertas especiales
                if (tipo === 'salida' && articulo.stock_actual <= 0) {
                    mensaje += '\n⚠️ ¡Artículo sin stock!';
                } else if (articulo.stock_actual < 5) { // Umbral bajo configurable
                    mensaje += '\n🟡 Stock bajo';
                }
            }

            mostrarAlerta(mensaje, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalMovimiento')).hide();
            cargarArticulos(paginaActual, filtrosAplicados);
            cargarEstadisticas();
        } else {
            // Mejorar mensajes de error también
            let mensajeError = result.error || 'Error desconocido';

            // Personalizar mensajes de error comunes
            if (mensajeError.includes('Stock insuficiente')) {
                mensajeError = '⚠️ ' + mensajeError + '\n💡 Verifica el stock disponible antes de realizar la salida';
            } else if (mensajeError.includes('Artículo no encontrado')) {
                mensajeError = '❌ ' + mensajeError + '\n💡 Selecciona un artículo válido del autocompletado';
            } else if (mensajeError.includes('Campo requerido')) {
                mensajeError = '📝 ' + mensajeError + '\n💡 Completa todos los campos obligatorios';
            } else {
                mensajeError = '❌ ' + mensajeError;
            }

            mostrarAlerta(mensajeError, 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'danger');
    }
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

    // Convertir saltos de línea a <br> para HTML
    const mensajeHtml = mensaje.replace(/\n/g, '<br>');

    // Crear alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.style.maxWidth = '400px'; // Limitar ancho para mejor legibilidad
    alertDiv.innerHTML = `
        <div style="word-wrap: break-word;">${mensajeHtml}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.appendChild(alertDiv);

    // Auto-eliminar después de tiempo variable según el tipo y longitud
    let timeout = 5000; // Por defecto
    if (tipo === 'success' && mensaje.length > 100) {
        timeout = 7000; // Más tiempo para mensajes largos de éxito
    } else if (tipo === 'danger') {
        timeout = 8000; // Más tiempo para errores
    }

    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, timeout);
}

// Funciones implementadas
function editarArticulo(id) {
    // Obtener datos del artículo y mostrar modal de edición
    fetch(`/inventario/api/articulos/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success === false) {
                mostrarAlerta('Error al cargar artículo: ' + data.error, 'danger');
                return;
            }

            // Llenar el modal con los datos del artículo
            document.getElementById('edit-codigo').value = data.codigo || '';
            document.getElementById('edit-descripcion').value = data.descripcion || '';
            document.getElementById('edit-categoria').value = data.categoria || '';
            document.getElementById('edit-subcategoria').value = data.subcategoria || '';
            document.getElementById('edit-ubicacion').value = data.ubicacion || '';
            document.getElementById('edit-stock-minimo').value = data.stock_minimo || 0;
            document.getElementById('edit-stock-maximo').value = data.stock_maximo || '';
            document.getElementById('edit-unidad-medida').value = data.unidad_medida || 'UNI';
            document.getElementById('edit-precio-unitario').value = data.precio_unitario || '';
            document.getElementById('edit-proveedor').value = data.proveedor_principal || '';
            document.getElementById('edit-cuenta-contable').value = data.cuenta_contable_compra || '622000000';
            document.getElementById('edit-grupo-contable').value = data.grupo_contable || '';
            document.getElementById('edit-observaciones').value = data.observaciones || '';

            // Checkboxes
            document.getElementById('edit-critico').checked = data.critico || false;
            document.getElementById('edit-activo').checked = data.activo !== false; // Por defecto true

            // Guardar ID del artículo que se está editando
            document.getElementById('modalEditarArticulo').dataset.articuloId = id;

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalEditarArticulo'));
            modal.show();
        })
        .catch(error => {
            console.error('Error al cargar artículo:', error);
            mostrarAlerta('Error al cargar artículo para edición', 'danger');
        });
}

function guardarEdicionArticulo() {
    const articuloId = document.getElementById('modalEditarArticulo').dataset.articuloId;
    if (!articuloId) {
        mostrarAlerta('Error: ID de artículo no encontrado', 'danger');
        return;
    }

    const data = {
        codigo: document.getElementById('edit-codigo').value.trim(),
        descripcion: document.getElementById('edit-descripcion').value.trim(),
        categoria: document.getElementById('edit-categoria').value.trim(),
        subcategoria: document.getElementById('edit-subcategoria').value.trim(),
        ubicacion: document.getElementById('edit-ubicacion').value.trim(),
        stock_minimo: parseInt(document.getElementById('edit-stock-minimo').value) || 0,
        stock_maximo: parseInt(document.getElementById('edit-stock-maximo').value) || null,
        unidad_medida: document.getElementById('edit-unidad-medida').value,
        precio_unitario: parseFloat(document.getElementById('edit-precio-unitario').value) || null,
        proveedor_principal: document.getElementById('edit-proveedor').value.trim(),
        cuenta_contable_compra: document.getElementById('edit-cuenta-contable').value.trim(),
        grupo_contable: document.getElementById('edit-grupo-contable').value.trim(),
        critico: document.getElementById('edit-critico').checked,
        activo: document.getElementById('edit-activo').checked,
        observaciones: document.getElementById('edit-observaciones').value.trim()
    };

    // Validar campos requeridos
    if (!data.codigo || !data.descripcion) {
        mostrarAlerta('Los campos Código y Descripción son obligatorios', 'warning');
        return;
    }

    fetch(`/inventario/api/articulos/${articuloId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                mostrarAlerta(result.message, 'success');
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarArticulo'));
                modal.hide();
                // Recargar artículos
                cargarArticulos();
            } else {
                mostrarAlerta('Error: ' + result.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error al guardar edición:', error);
            mostrarAlerta('Error de conexión al guardar cambios', 'danger');
        });
}

function verHistorial(id) {
    console.log('📋 Abriendo historial para artículo ID:', id);

    // Cargar historial de movimientos del artículo
    const url = `/inventario/api/articulos/${id}/movimientos?page=1&per_page=20`;
    console.log('🌐 URL de historial:', url);

    fetch(url)
        .then(response => {
            console.log('📡 Response status historial:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos de historial:', data);

            if (data.error) {
                console.error('❌ Error en datos de historial:', data.error);
                mostrarAlerta('Error al cargar historial: ' + data.error, 'danger');
                return;
            }

            // Llenar la tabla de historial
            const tbody = document.getElementById('historial-tbody');
            if (!tbody) {
                console.error('❌ No se encontró elemento historial-tbody');
                return;
            }

            tbody.innerHTML = '';
            console.log('🧹 Tabla de historial limpiada');

            if (!data.movimientos || data.movimientos.length === 0) {
                console.log('📭 Sin movimientos para mostrar');
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-4">
                            <div class="text-muted">
                                <i class="fas fa-history fa-3x mb-3 opacity-25"></i>
                                <p>No hay movimientos registrados para este artículo</p>
                            </div>
                        </td>
                    </tr>
                `;
            } else {
                console.log('📊 Mostrando', data.movimientos.length, 'movimientos');
                data.movimientos.forEach((movimiento, index) => {
                    console.log(`   ${index + 1}. ${movimiento.fecha} - ${movimiento.tipo} - ${movimiento.cantidad}`);

                    const tipoClass = movimiento.tipo === 'entrada' ? 'success' :
                        movimiento.tipo === 'salida' ? 'danger' : 'warning';
                    const tipoIcon = movimiento.tipo === 'entrada' ? 'plus' :
                        movimiento.tipo === 'salida' ? 'minus' : 'exchange-alt';

                    tbody.innerHTML += `
                        <tr>
                            <td>${movimiento.fecha}</td>
                            <td>
                                <span class="badge bg-${tipoClass}">
                                    <i class="fas fa-${tipoIcon} me-1"></i>
                                    ${movimiento.tipo}
                                    ${movimiento.subtipo ? ` (${movimiento.subtipo})` : ''}
                                </span>
                            </td>
                            <td class="text-end">${movimiento.cantidad}</td>
                            <td class="text-end">
                                ${movimiento.precio_unitario ?
                            movimiento.precio_unitario.toFixed(2) : '-'}
                            </td>
                            <td class="text-end">
                                ${movimiento.valor_total ?
                            movimiento.valor_total.toFixed(2) : '-'}
                            </td>
                            <td>
                                ${movimiento.documento_referencia || '-'}
                                ${movimiento.usuario_id ? `<br><small class="text-muted">por ${movimiento.usuario_id}</small>` : ''}
                            </td>
                        </tr>
                    `;
                });
            }

            // Actualizar paginación si hay más páginas
            if (data.pages > 1) {
                // Aquí se podría implementar paginación para el historial
                console.log(`Historial tiene ${data.pages} páginas`);
            }

            console.log('✅ Tabla de historial completada');

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalHistorial'));
            modal.show();
            console.log('📱 Modal de historial mostrado');
        })
        .catch(error => {
            console.error('❌ Error al cargar historial:', error);
            mostrarAlerta('Error al cargar historial de movimientos', 'danger');
        });
}

function mostrarMovimientos() {
    // Cargar vista general de movimientos
    fetch('/inventario/api/movimientos?page=1&per_page=25')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                mostrarAlerta('Error al cargar movimientos: ' + data.error, 'danger');
                return;
            }

            // Llenar la tabla de movimientos generales
            const tbody = document.getElementById('movimientos-tbody');
            tbody.innerHTML = '';

            if (!data.movimientos || data.movimientos.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-4">
                            <div class="text-muted">
                                <i class="fas fa-exchange-alt fa-3x mb-3 opacity-25"></i>
                                <p>No hay movimientos registrados</p>
                            </div>
                        </td>
                    </tr>
                `;
            } else {
                data.movimientos.forEach(movimiento => {
                    const tipoClass = movimiento.tipo === 'entrada' ? 'success' :
                        movimiento.tipo === 'salida' ? 'danger' : 'warning';
                    const tipoIcon = movimiento.tipo === 'entrada' ? 'plus' :
                        movimiento.tipo === 'salida' ? 'minus' : 'exchange-alt';

                    tbody.innerHTML += `
                        <tr>
                            <td>${movimiento.fecha}</td>
                            <td>
                                <span class="badge bg-${tipoClass}">
                                    <i class="fas fa-${tipoIcon} me-1"></i>
                                    ${movimiento.tipo}
                                </span>
                            </td>
                            <td>
                                <strong>${movimiento.codigo_articulo}</strong><br>
                                <small class="text-muted">${movimiento.descripcion_articulo}</small>
                            </td>
                            <td class="text-end">${movimiento.cantidad} ${movimiento.unidad_medida}</td>
                            <td class="text-end">
                                ${movimiento.precio_unitario ?
                            movimiento.precio_unitario.toFixed(2) : '-'}
                            </td>
                            <td class="text-end">
                                ${movimiento.valor_total ?
                            movimiento.valor_total.toFixed(2) : '-'}
                            </td>
                            <td>
                                ${movimiento.documento_referencia || '-'}
                                ${movimiento.usuario_id ?
                            `<br><small class="text-muted">por ${movimiento.usuario_id}</small>` : ''}
                            </td>
                        </tr>
                    `;
                });
            }

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalMovimientos'));
            modal.show();
        })
        .catch(error => {
            console.error('Error al cargar movimientos:', error);
            mostrarAlerta('Error al cargar vista general de movimientos', 'danger');
        });
}

// Exportar funciones globales
window.mostrarModalNuevoArticulo = mostrarModalNuevoArticulo;
window.guardarNuevoArticulo = guardarNuevoArticulo;
window.mostrarModalMovimiento = mostrarModalMovimiento;
window.guardarMovimiento = guardarMovimiento;
window.aplicarFiltros = aplicarFiltros;
window.limpiarFiltros = limpiarFiltros;
window.editarArticulo = editarArticulo;
window.guardarEdicionArticulo = guardarEdicionArticulo;
window.verHistorial = verHistorial;
window.mostrarMovimientos = mostrarMovimientos;
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
                console.log('üì¶ Item de inventario seleccionado:', item);
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

// Función para exportar CSV
async function exportarCSV() {
    await descargarCSVMejorado('/inventario/exportar-csv', 'inventario_{fecha}', 'CSV');
}

// Exponer funciones globales
window.mostrarModalNuevoArticulo = mostrarModalNuevoArticulo;
window.guardarNuevoArticulo = guardarNuevoArticulo;
window.mostrarModalMovimiento = mostrarModalMovimiento;
window.mostrarModalMovimientoGeneral = mostrarModalMovimientoGeneral;
window.guardarMovimiento = guardarMovimiento;
window.aplicarFiltros = aplicarFiltros;
window.limpiarFiltros = limpiarFiltros;
window.editarArticulo = editarArticulo;
window.verHistorial = verHistorial;
window.mostrarMovimientos = mostrarMovimientos;
window.exportarCSV = exportarCSV;
window.mostrarCargando = mostrarCargando;

// Inicializar listeners del modal cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    initializeMovimientoModalListeners();

    // Listener para cuando se muestre el modal de movimiento
    const modalMovimiento = document.getElementById('modalMovimiento');
    if (modalMovimiento) {
        modalMovimiento.addEventListener('shown.bs.modal', function () {
            console.log('🎭 Modal de movimiento mostrado, verificando autocompletado...');
            const input = document.getElementById('movimiento-articulo-info');
            const articuloId = document.getElementById('movimiento-articulo-id').value;

            // Solo inicializar autocompletado si no hay artículo pre-seleccionado
            if (input && !articuloId) {
                console.log('🔧 Inicializando autocompletado automáticamente...');
                setTimeout(() => {
                    initializeArticuloAutoComplete();
                }, 100); // Pequeño delay para asegurar que el DOM esté listo
            } else {
                console.log('ℹ️ Artículo pre-seleccionado, no se inicializa autocompletado');
            }
        });
    }
});
