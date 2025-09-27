// conteos.js - Funcionalidad para gestión de conteos de inventario

// Variables globales
let conteosActuales = [];
let paginaActualConteos = 1;
let conteosPorPagina = 15;
let filtrosConteos = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Inicializando módulo de conteos...');

    // Verificar que los elementos existen
    const periodoAño = document.getElementById('periodo-año');
    const periodoMes = document.getElementById('periodo-mes');

    if (periodoAño && periodoMes) {
        // Establecer fecha actual por defecto
        const hoy = new Date();
        periodoAño.value = hoy.getFullYear();
        periodoMes.value = hoy.getMonth() + 1;
    }

    // Cargar datos iniciales
    cargarResumenConteos();
    cargarConteos();

    // Configurar eventos
    configurarEventosConteos();
    configurarCalculoDiferencia();
    inicializarFiltrosConteos();

    // Inicializar autocompletado de usuarios
    inicializarAutocompletadoUsuarios();

    console.log('✅ Módulo de conteos inicializado');
});

// Cargar resumen de conteos
async function cargarResumenConteos() {
    try {
        const response = await fetch('/inventario/api/conteos/resumen');
        const data = await response.json();

        if (data.success) {
            const resumen = data.resumen;
            document.getElementById('periodo-actual').textContent = resumen.periodo_actual;
            document.getElementById('total-conteos').textContent = resumen.total_conteos;
            document.getElementById('conteos-completados').textContent = resumen.conteos_completados;
            document.getElementById('conteos-diferencias').textContent = resumen.conteos_diferencias;
            document.getElementById('conteos-pendientes').textContent = resumen.conteos_pendientes || 0;
        } else {
            console.error('Error en respuesta:', data.error);
            mostrarAlerta('Error al cargar resumen: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Error al cargar resumen:', error);
        mostrarAlerta('Error al cargar resumen de conteos', 'danger');
    }
}

// Cargar conteos
async function cargarConteos(page = 1, filtros = {}) {
    try {
        // Construir parámetros de la URL
        const params = new URLSearchParams({
            page: page,
            per_page: conteosPorPagina
        });

        // Agregar filtros si existen
        if (filtros.tipo_conteo) params.append('tipo_conteo', filtros.tipo_conteo);
        if (filtros.estado) params.append('estado', filtros.estado);
        if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
        if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
        if (filtros.con_diferencias) params.append('con_diferencias', filtros.con_diferencias);
        if (filtros.sin_usuario) params.append('sin_usuario', filtros.sin_usuario);

        const response = await fetch(`/inventario/api/conteos?${params}`);
        const data = await response.json();

        if (data.success) {
            conteosActuales = data.conteos;
            actualizarTablaConteos(data.conteos);
            document.getElementById('contador-conteos').textContent = `${data.pagination.total} conteos`;
            document.getElementById('total-resultados').textContent = data.pagination.total;

            // Actualizar paginación si es necesario
            if (data.pagination.pages > 1) {
                // Aquí se puede agregar lógica de paginación
                console.log(`Página ${data.pagination.page} de ${data.pagination.pages}`);
            }
        } else {
            console.error('Error en respuesta:', data.error);
            mostrarAlerta('Error al cargar conteos: ' + data.error, 'danger');
        }

    } catch (error) {
        console.error('Error al cargar conteos:', error);
        mostrarAlerta('Error al cargar conteos', 'danger');
    }
}

// Actualizar tabla de conteos
function actualizarTablaConteos(conteos) {
    const tbody = document.getElementById('tabla-conteos-body');
    tbody.innerHTML = '';

    conteos.forEach(conteo => {
        const tr = document.createElement('tr');

        // Determinar estilos según diferencia
        let diferenciaClass = '';
        let estadoBadge = 'bg-secondary';

        if (conteo.diferencia !== null) {
            if (Math.abs(conteo.diferencia) > 0) {
                diferenciaClass = conteo.diferencia > 0 ? 'text-success' : 'text-danger';
            }
        }

        switch (conteo.estado) {
            case 'pendiente':
                estadoBadge = 'bg-warning';
                break;
            case 'validado':
                estadoBadge = 'bg-success';
                break;
            case 'regularizado':
                estadoBadge = 'bg-primary';
                break;
        }

        tr.innerHTML = `
            <td>${formatearFecha(conteo.fecha_conteo)}</td>
            <td>
                <code>${conteo.articulo.codigo}</code><br>
                <small class="text-muted">${conteo.articulo.descripcion}</small>
            </td>
            <td>
                <span class="badge bg-info">${conteo.tipo_conteo}</span>
            </td>
            <td class="text-center">
                <strong>${conteo.stock_teorico}</strong>
            </td>
            <td class="text-center">
                ${conteo.stock_fisico !== null ? `<strong>${conteo.stock_fisico}</strong>` : '<span class="text-muted">-</span>'}
            </td>
            <td class="text-center ${diferenciaClass}">
                ${conteo.diferencia !== null ? `<strong>${conteo.diferencia > 0 ? '+' : ''}${conteo.diferencia}</strong>` : '<span class="text-muted">-</span>'}
            </td>
            <td class="text-center ${diferenciaClass}">
                ${conteo.porcentaje_diferencia !== null ? `<strong>${conteo.porcentaje_diferencia > 0 ? '+' : ''}${conteo.porcentaje_diferencia.toFixed(1)}%</strong>` : '<span class="text-muted">-</span>'}
            </td>
            <td>
                <span class="badge ${estadoBadge}">${conteo.estado}</span>
            </td>
            <td>
                ${conteo.usuario_conteo || '<span class="text-muted">-</span>'}
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    ${conteo.estado === 'pendiente' ?
                `<button type="button" class="btn btn-sm btn-outline-success action-btn special" onclick="mostrarModalProcesarConteo(${conteo.id}, '${conteo.articulo.codigo}', '${conteo.articulo.descripcion}', ${conteo.stock_teorico})" title="Procesar conteo">
                            <i class="bi bi-check"></i>
                        </button>` :
                `<button type="button" class="btn btn-sm btn-outline-primary action-btn view" onclick="verDetalleConteo(${conteo.id})" title="Ver detalle">
                            <i class="bi bi-eye"></i>
                        </button>`
            }
                    <button type="button" class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarConteo(${conteo.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

// Configurar eventos
function configurarEventosConteos() {
    // Filtros con auto-aplicación
    const filtros = ['filtro-tipo-conteo', 'filtro-estado-conteo', 'filtro-fecha-desde', 'filtro-fecha-hasta'];
    filtros.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.addEventListener('change', aplicarFiltrosConteos);
        }
    });
}

// Variables de filtros

// Aplicar filtros
function aplicarFiltrosConteos() {
    const filtros = {};

    const tipoConteo = document.getElementById('filtro-tipo-conteo').value;
    if (tipoConteo) filtros.tipo_conteo = tipoConteo;

    const estadoConteo = document.getElementById('filtro-estado-conteo').value;
    if (estadoConteo) filtros.estado = estadoConteo;

    const fechaDesde = document.getElementById('filtro-fecha-desde').value;
    if (fechaDesde) filtros.fecha_desde = fechaDesde;

    const fechaHasta = document.getElementById('filtro-fecha-hasta').value;
    if (fechaHasta) filtros.fecha_hasta = fechaHasta;

    // Nuevos filtros de checkbox
    if (document.getElementById('filtro-con-diferencias').checked) {
        filtros.con_diferencias = 'true';
    }

    if (document.getElementById('filtro-sin-usuario').checked) {
        filtros.sin_usuario = 'true';
    }

    filtrosConteos = filtros;
    paginaActualConteos = 1;
    cargarConteos(paginaActualConteos, filtros);
}

// Limpiar filtros
function limpiarFiltrosConteos() {
    document.getElementById('filtro-tipo-conteo').value = '';
    document.getElementById('filtro-estado-conteo').value = '';
    document.getElementById('filtro-fecha-desde').value = '';
    document.getElementById('filtro-fecha-hasta').value = '';
    document.getElementById('filtro-con-diferencias').checked = false;
    document.getElementById('filtro-sin-usuario').checked = false;

    filtrosConteos = {};
    paginaActualConteos = 1;
    cargarConteos();
}

// Inicializar listeners de filtros
function inicializarFiltrosConteos() {
    // Selects - cambio inmediato
    const selects = document.querySelectorAll('#filtros-conteos-form select');
    selects.forEach(select => {
        select.addEventListener('change', aplicarFiltrosConteos);
    });

    // Inputs de fecha - cambio inmediato
    const dateInputs = document.querySelectorAll('#filtros-conteos-form input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', aplicarFiltrosConteos);
    });

    // Checkboxes - cambio inmediato
    const checkboxes = document.querySelectorAll('#filtros-conteos-form input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', aplicarFiltrosConteos);
    });
}

// Iniciar período de conteo
function iniciarPeriodoConteo() {
    console.log('🎯 Función iniciarPeriodoConteo ejecutada');

    try {
        const modalElement = document.getElementById('modalNuevoPeriodo');
        console.log('🎭 Modal element:', modalElement);

        if (!modalElement) {
            console.error('❌ No se encontró el modal modalNuevoPeriodo');
            mostrarAlerta('Error: Modal no encontrado', 'danger');
            return;
        }

        // Probar sin Bootstrap Modal primero
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            const form = document.getElementById('formNuevoPeriodo');

            console.log('📋 Form element:', form);

            if (form) {
                form.reset();
            }

            // Establecer fecha actual
            const hoy = new Date();
            const periodoAño = document.getElementById('periodo-año');
            const periodoMes = document.getElementById('periodo-mes');

            if (periodoAño && periodoMes) {
                periodoAño.value = hoy.getFullYear();
                periodoMes.value = hoy.getMonth() + 1;
                console.log(`📅 Fecha establecida en modal: ${periodoMes.value}/${periodoAño.value}`);
            }

            console.log('👁️ Mostrando modal...');
            modal.show();
        } else {
            console.error('❌ Bootstrap no está disponible');
            mostrarAlerta('Error: Bootstrap no disponible', 'danger');
        }

    } catch (error) {
        console.error('❌ Error en iniciarPeriodoConteo:', error);
        mostrarAlerta('Error al abrir modal: ' + error.message, 'danger');
    }
}// Guardar nuevo período
async function guardarNuevoPeriodo() {
    const form = document.getElementById('formNuevoPeriodo');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const año = parseInt(document.getElementById('periodo-año').value);
    const mes = parseInt(document.getElementById('periodo-mes').value);

    console.log(`Creando período para ${mes}/${año}...`);

    try {
        // Por ahora simular que se crea el período correctamente
        mostrarAlerta(`Período ${mes}/${año} iniciado correctamente`, 'success');
        bootstrap.Modal.getInstance(document.getElementById('modalNuevoPeriodo')).hide();

        // Recargar datos
        cargarResumenConteos();
        cargarConteos();

    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error al crear el período', 'danger');
    }
}

// Generar conteos aleatorios
function generarConteosAleatorios() {
    console.log('🎯 Función generarConteosAleatorios ejecutada');

    try {
        const modalElement = document.getElementById('modalConteosAleatorios');
        console.log('🎭 Modal element:', modalElement);

        if (!modalElement) {
            console.error('❌ No se encontró el modal modalConteosAleatorios');
            mostrarAlerta('Error: Modal no encontrado', 'danger');
            return;
        }

        // Probar sin Bootstrap Modal primero
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            const form = document.getElementById('formConteosAleatorios');
            const cantidadInput = document.getElementById('cantidad-conteos');

            console.log('📋 Form element:', form);
            console.log('🔢 Cantidad input:', cantidadInput);

            if (form) {
                form.reset();
            }

            if (cantidadInput) {
                cantidadInput.value = 10;
            }

            console.log('👁️ Mostrando modal...');
            modal.show();
        } else {
            console.error('❌ Bootstrap no está disponible');
            mostrarAlerta('Error: Bootstrap no disponible', 'danger');
        }

    } catch (error) {
        console.error('❌ Error en generarConteosAleatorios:', error);
        mostrarAlerta('Error al abrir modal: ' + error.message, 'danger');
    }
}// Guardar conteos aleatorios
async function guardarConteosAleatorios() {
    console.log('🎯 Función guardarConteosAleatorios ejecutada');

    const form = document.getElementById('formConteosAleatorios');
    const cantidadInput = document.getElementById('cantidad-conteos');

    console.log('📋 Form:', form);
    console.log('🔢 Cantidad input:', cantidadInput);

    if (!form || !form.checkValidity()) {
        console.warn('⚠️ Formulario inválido');
        if (form) form.reportValidity();
        return;
    }

    const cantidad = parseInt(cantidadInput.value);
    console.log('🎲 Generando', cantidad, 'conteos aleatorios...');

    try {
        const response = await fetch('/inventario/api/conteos/aleatorios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cantidad })
        });

        console.log('📡 Response status:', response.status);
        const result = await response.json();
        console.log('📊 Result:', result);

        if (result.success) {
            mostrarAlerta(result.message, 'success');

            const modalInstance = bootstrap.Modal.getInstance(document.getElementById('modalConteosAleatorios'));
            if (modalInstance) {
                modalInstance.hide();
            }

            // Recargar datos
            cargarResumenConteos();
            cargarConteos();
        } else {
            mostrarAlerta('Error: ' + (result.error || 'Error desconocido'), 'danger');
        }
    } catch (error) {
        console.error('❌ Error al generar conteos:', error);
        mostrarAlerta('Error de conexión', 'danger');
    }
}

// Mostrar modal procesar conteo
function mostrarModalProcesarConteo(conteoId, articuloCodigo, articuloDescripcion, stockTeorico) {
    document.getElementById('conteo-id').value = conteoId;
    document.getElementById('conteo-articulo-info').value = `${articuloCodigo} - ${articuloDescripcion}`;
    document.getElementById('conteo-stock-teorico').value = stockTeorico;
    document.getElementById('formProcesarConteo').reset();
    document.getElementById('conteo-id').value = conteoId;
    document.getElementById('conteo-articulo-info').value = `${articuloCodigo} - ${articuloDescripcion}`;
    document.getElementById('conteo-stock-teorico').value = stockTeorico;

    // Ocultar información de diferencia
    document.getElementById('conteo-diferencia-info').style.display = 'none';

    // Limpiar campo de usuario
    document.getElementById('conteo-usuario').value = '';
    delete document.getElementById('conteo-usuario').dataset.userId;

    const modal = new bootstrap.Modal(document.getElementById('modalProcesarConteo'));
    modal.show();

    // Reinicializar autocompletado de usuarios cuando se muestre el modal
    modal._element.addEventListener('shown.bs.modal', function () {
        inicializarAutocompletadoUsuarios();
    }, { once: true });
}

// Configurar cálculo automático de diferencia
function configurarCalculoDiferencia() {
    const stockFisicoInput = document.getElementById('conteo-stock-fisico');
    if (stockFisicoInput) {
        stockFisicoInput.addEventListener('input', function () {
            calcularDiferencia();
        });
    }
}

// Calcular diferencia
function calcularDiferencia() {
    const stockTeorico = parseInt(document.getElementById('conteo-stock-teorico').value) || 0;
    const stockFisico = parseInt(document.getElementById('conteo-stock-fisico').value);

    if (stockFisico !== undefined && !isNaN(stockFisico)) {
        const diferencia = stockFisico - stockTeorico;
        const porcentajeDiferencia = stockTeorico > 0 ? (diferencia / stockTeorico) * 100 : 0;

        const infoDiv = document.getElementById('conteo-diferencia-info');

        let alertClass = 'alert-info';
        let mensaje = 'Sin diferencias';

        if (diferencia > 0) {
            alertClass = 'alert-success';
            mensaje = `Exceso de ${diferencia} unidades (+${porcentajeDiferencia.toFixed(1)}%)`;
        } else if (diferencia < 0) {
            alertClass = 'alert-danger';
            mensaje = `Faltante de ${Math.abs(diferencia)} unidades (${porcentajeDiferencia.toFixed(1)}%)`;
        }

        infoDiv.className = `alert ${alertClass}`;
        infoDiv.innerHTML = `
            <i class="fas fa-calculator"></i>
            <strong>Diferencia calculada:</strong> ${mensaje}
        `;
        infoDiv.style.display = 'block';
    } else {
        document.getElementById('conteo-diferencia-info').style.display = 'none';
    }
}

// Inicializar autocompletado de usuarios
function inicializarAutocompletadoUsuarios() {
    // Buscar el input de usuario en cualquier modal que esté presente
    const usuarioInput = document.getElementById('editar-usuario') ||
        document.getElementById('conteo-usuario') ||
        document.querySelector('input[id*="usuario"]');

    console.log('🔄 Inicializando autocompletado de usuarios...');
    console.log('📝 Input element:', usuarioInput);
    console.log('📚 AutoComplete available:', typeof AutoComplete !== 'undefined');

    if (!usuarioInput) {
        console.error('❌ No se encontró el elemento conteo-usuario');
        return;
    }

    // Verificar que el elemento esté completamente en el DOM
    if (!usuarioInput.parentNode) {
        console.warn('⚠️ Input no tiene parentNode - esperando un momento...');
        setTimeout(() => inicializarAutocompletadoUsuarios(), 100);
        return;
    }

    if (typeof AutoComplete === 'undefined') {
        console.error('❌ AutoComplete no está disponible - usando fallback');
        // Usar un fallback simple con datalist
        crearDatalistUsuarios(usuarioInput);
        return;
    }

    try {
        // Verificar si ya existe una instancia
        if (usuarioInput._autocomplete) {
            console.log('🗑️ Destruyendo instancia anterior');
            usuarioInput._autocomplete.destroy();
        }

        const autocomplete = new AutoComplete(usuarioInput, {
            apiUrl: '/usuarios/api/autocomplete',
            searchKey: 'q',
            minChars: 2,
            delay: 300,
            renderItem: function (item) {
                return `
                    <div class="autocomplete-item">
                        <strong>${item.username}</strong>
                        <br>
                        <small class="text-muted">
                            ${item.nombre || ''} - ${item.rol || ''}
                        </small>
                    </div>
                `;
            },
            onSelect: function (item) {
                usuarioInput.value = item.username;
                usuarioInput.dataset.userId = item.id;
            },
            // Agregar fallback para datos estáticos si la API falla
            fallbackData: [
                { id: 1, username: 'admin', nombre: 'Administrador', rol: 'admin' },
                { id: 2, username: 'supervisor', nombre: 'Supervisor', rol: 'supervisor' },
                { id: 3, username: 'tecnico1', nombre: 'Técnico Principal', rol: 'tecnico' },
                { id: 4, username: 'tecnico2', nombre: 'Técnico Auxiliar', rol: 'tecnico' },
                { id: 5, username: 'operador', nombre: 'Operador', rol: 'operador' }
            ]
        });

        // Guardar referencia para poder destruirla después
        usuarioInput._autocomplete = autocomplete;

        console.log('✅ Autocompletado de usuarios inicializado correctamente');
    } catch (error) {
        console.error('❌ Error al inicializar autocompletado de usuarios:', error);
        // Fallback: usar datalist simple
        crearDatalistUsuarios(usuarioInput);
    }
}

// Función fallback para crear un datalist simple
function crearDatalistUsuarios(input) {
    console.log('🔄 Creando datalist fallback para usuarios');

    // Crear datalist si no existe
    let datalist = document.getElementById('usuarios-datalist');
    if (!datalist) {
        datalist = document.createElement('datalist');
        datalist.id = 'usuarios-datalist';

        // Datos de ejemplo
        const usuarios = [
            'admin',
            'supervisor',
            'tecnico1',
            'tecnico2',
            'operador',
            'mantenimiento',
            'jefe_taller'
        ];

        usuarios.forEach(usuario => {
            const option = document.createElement('option');
            option.value = usuario;
            datalist.appendChild(option);
        });

        document.body.appendChild(datalist);
    }

    // Asociar datalist al input
    input.setAttribute('list', 'usuarios-datalist');
    input.placeholder = 'Escribe el nombre del usuario (ej: admin, tecnico1...)';

    console.log('✅ Datalist fallback creado');
}

// Función para llenar datalist de usuarios
function llenarDatalistUsuarios(datalistId) {
    const usuarios = [
        { username: 'admin', nombre: 'Administrador', rol: 'admin' },
        { username: 'supervisor', nombre: 'Supervisor', rol: 'supervisor' },
        { username: 'tecnico1', nombre: 'Técnico Principal', rol: 'tecnico' },
        { username: 'tecnico2', nombre: 'Técnico Auxiliar', rol: 'tecnico' },
        { username: 'operador', nombre: 'Operador', rol: 'operador' }
    ];

    const datalist = document.getElementById(datalistId);
    if (datalist) {
        datalist.innerHTML = '';
        usuarios.forEach(usuario => {
            const option = document.createElement('option');
            option.value = usuario.username;
            option.textContent = `${usuario.username} - ${usuario.nombre}`;
            datalist.appendChild(option);
        });
    }
}

// Guardar conteo físico
async function guardarConteoFisico() {
    const form = document.getElementById('formProcesarConteo');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const conteoId = parseInt(document.getElementById('conteo-id').value);
    const stockFisico = parseInt(document.getElementById('conteo-stock-fisico').value);
    const usuario = document.getElementById('conteo-usuario').value;
    const observaciones = document.getElementById('conteo-observaciones').value;

    try {
        const response = await fetch(`/inventario/api/conteos/${conteoId}/procesar`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_fisico: stockFisico,
                usuario: usuario,
                observaciones: observaciones
            })
        });

        const result = await response.json();

        if (result.success) {
            mostrarAlerta(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalProcesarConteo')).hide();
            cargarResumenConteos();
            cargarConteos();
        } else {
            mostrarAlerta('Error: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'danger');
    }
}

// Funciones auxiliares
function formatearFecha(fechaString) {
    const fecha = new Date(fechaString);
    return fecha.toLocaleDateString('es-ES');
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

// Guardar conteo editado
async function guardarEditarConteo() {
    const form = document.getElementById('formEditarConteo');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const conteoId = parseInt(document.getElementById('editar-conteo-id').value);
    const stockFisico = parseInt(document.getElementById('editar-stock-fisico').value);
    const usuario = document.getElementById('editar-usuario').value;
    const observaciones = document.getElementById('editar-observaciones').value;

    try {
        const response = await fetch(`/inventario/api/conteos/${conteoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_fisico: stockFisico,
                usuario_conteo: usuario,
                observaciones: observaciones
            })
        });

        const result = await response.json();

        if (result.success) {
            mostrarAlerta(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalEditarConteo')).hide();
            cargarResumenConteos();
            cargarConteos();
        } else {
            mostrarAlerta('Error: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'danger');
    }
}

// Funciones placeholder
function verDetalleConteo(id) {
    mostrarAlerta('Vista de detalle en desarrollo', 'info');
}

function editarConteo(id) {
    console.log('🔧 Editando conteo ID:', id);

    // Obtener datos del conteo
    fetch(`/inventario/api/conteos/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const conteo = data.conteo;

                // Verificar que se pueda editar
                if (conteo.estado === 'regularizado') {
                    mostrarAlerta('No se puede editar un conteo ya regularizado', 'warning');
                    return;
                }

                // Llenar el modal con los datos
                document.getElementById('editar-conteo-id').value = conteo.id;
                document.getElementById('editar-articulo-info').value =
                    `${conteo.articulo.codigo} - ${conteo.articulo.descripcion}`;
                document.getElementById('editar-stock-teorico').value = conteo.stock_teorico;
                document.getElementById('editar-stock-fisico').value = conteo.stock_fisico || '';
                document.getElementById('editar-usuario').value = conteo.usuario_conteo || '';
                document.getElementById('editar-observaciones').value = conteo.observaciones || '';

                // Llenar datalist de usuarios para el modal de editar
                llenarDatalistUsuarios('usuarios-datalist-editar');

                // Mostrar el modal
                const modal = new bootstrap.Modal(document.getElementById('modalEditarConteo'));
                modal.show();
            } else {
                mostrarAlerta('Error al cargar datos del conteo: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error de conexión al cargar el conteo', 'danger');
        });
}

// Exportar funciones globales
window.iniciarPeriodoConteo = iniciarPeriodoConteo;
window.guardarNuevoPeriodo = guardarNuevoPeriodo;
window.generarConteosAleatorios = generarConteosAleatorios;
window.guardarConteosAleatorios = guardarConteosAleatorios;
window.mostrarModalProcesarConteo = mostrarModalProcesarConteo;
window.guardarConteoFisico = guardarConteoFisico;
window.guardarEditarConteo = guardarEditarConteo;
window.aplicarFiltrosConteos = aplicarFiltrosConteos;
window.limpiarFiltrosConteos = limpiarFiltrosConteos;
window.verDetalleConteo = verDetalleConteo;
window.editarConteo = editarConteo;