// conteos.js - Funcionalidad para gestión de conteos de inventario

// Variables globales
let conteosActuales = [];
let paginaActualConteos = 1;
let conteosPorPagina = 15;
let filtrosConteos = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    console.log('Inicializando módulo de conteos...');

    // Establecer fecha actual por defecto
    const hoy = new Date();
    document.getElementById('periodo-año').value = hoy.getFullYear();
    document.getElementById('periodo-mes').value = hoy.getMonth() + 1;

    // Cargar datos iniciales
    cargarResumenConteos();
    cargarConteos();

    // Configurar eventos
    configurarEventosConteos();
    configurarCalculoDiferencia();
});

// Cargar resumen de conteos
async function cargarResumenConteos() {
    try {
        // Por ahora usamos datos mock, después se conectará a la API
        const resumen = {
            periodo_actual: `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`,
            total_conteos: 45,
            conteos_completados: 32,
            conteos_diferencias: 8
        };

        document.getElementById('periodo-actual').textContent = resumen.periodo_actual;
        document.getElementById('total-conteos').textContent = resumen.total_conteos;
        document.getElementById('conteos-completados').textContent = resumen.conteos_completados;
        document.getElementById('conteos-diferencias').textContent = resumen.conteos_diferencias;
    } catch (error) {
        console.error('Error al cargar resumen:', error);
    }
}

// Cargar conteos
async function cargarConteos(page = 1, filtros = {}) {
    try {
        // Mock data - en producción se conectará a la API
        const mockConteos = [
            {
                id: 1,
                fecha_conteo: '2024-09-20',
                articulo_codigo: 'REP001',
                articulo_descripcion: 'Filtro de aceite',
                tipo_conteo: 'mensual',
                stock_teorico: 25,
                stock_fisico: 23,
                diferencia: -2,
                porcentaje_diferencia: -8.0,
                estado: 'validado',
                usuario_conteo: 'jperez'
            },
            {
                id: 2,
                fecha_conteo: '2024-09-21',
                articulo_codigo: 'REP002',
                articulo_descripcion: 'Correa de distribución',
                tipo_conteo: 'aleatorio',
                stock_teorico: 15,
                stock_fisico: null,
                diferencia: null,
                porcentaje_diferencia: null,
                estado: 'pendiente',
                usuario_conteo: null
            },
            {
                id: 3,
                fecha_conteo: '2024-09-22',
                articulo_codigo: 'REP003',
                articulo_descripcion: 'Pastillas de freno',
                tipo_conteo: 'mensual',
                stock_teorico: 40,
                stock_fisico: 42,
                diferencia: 2,
                porcentaje_diferencia: 5.0,
                estado: 'regularizado',
                usuario_conteo: 'mgarcia'
            }
        ];

        actualizarTablaConteos(mockConteos);
        document.getElementById('total-conteos-lista').textContent = mockConteos.length;

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
                <code>${conteo.articulo_codigo}</code><br>
                <small class="text-muted">${conteo.articulo_descripcion}</small>
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
                `<button type="button" class="btn btn-outline-success" onclick="mostrarModalProcesarConteo(${conteo.id}, '${conteo.articulo_codigo}', '${conteo.articulo_descripcion}', ${conteo.stock_teorico})" title="Procesar conteo">
                            <i class="fas fa-check"></i>
                        </button>` :
                `<button type="button" class="btn btn-outline-info" onclick="verDetalleConteo(${conteo.id})" title="Ver detalle">
                            <i class="fas fa-eye"></i>
                        </button>`
            }
                    <button type="button" class="btn btn-outline-primary" onclick="editarConteo(${conteo.id})" title="Editar">
                        <i class="fas fa-edit"></i>
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

    filtrosConteos = {};
    paginaActualConteos = 1;
    cargarConteos();
}

// Iniciar período de conteo
function iniciarPeriodoConteo() {
    const modal = new bootstrap.Modal(document.getElementById('modalNuevoPeriodo'));
    document.getElementById('formNuevoPeriodo').reset();

    // Establecer fecha actual
    const hoy = new Date();
    document.getElementById('periodo-año').value = hoy.getFullYear();
    document.getElementById('periodo-mes').value = hoy.getMonth() + 1;

    modal.show();
}

// Guardar nuevo período
async function guardarNuevoPeriodo() {
    const form = document.getElementById('formNuevoPeriodo');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const data = {
        año: parseInt(document.getElementById('periodo-año').value),
        mes: parseInt(document.getElementById('periodo-mes').value),
        usuario_responsable: document.getElementById('periodo-responsable').value,
        observaciones: document.getElementById('periodo-observaciones').value
    };

    try {
        const response = await fetch('/inventario/api/periodos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            mostrarAlerta('Período de inventario iniciado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalNuevoPeriodo')).hide();
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

// Generar conteos aleatorios
function generarConteosAleatorios() {
    const modal = new bootstrap.Modal(document.getElementById('modalConteosAleatorios'));
    document.getElementById('formConteosAleatorios').reset();
    document.getElementById('cantidad-conteos').value = 10;
    modal.show();
}

// Guardar conteos aleatorios
async function guardarConteosAleatorios() {
    const form = document.getElementById('formConteosAleatorios');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const cantidad = parseInt(document.getElementById('cantidad-conteos').value);

    try {
        const response = await fetch('/inventario/api/conteos/aleatorios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cantidad })
        });

        const result = await response.json();

        if (response.ok) {
            mostrarAlerta(`${result.conteos.length} conteos aleatorios generados exitosamente`, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalConteosAleatorios')).hide();
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

    const modal = new bootstrap.Modal(document.getElementById('modalProcesarConteo'));
    modal.show();
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
        const response = await fetch(`/inventario/api/conteos/${conteoId}`, {
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

        if (response.ok) {
            mostrarAlerta('Conteo procesado exitosamente', 'success');
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

// Funciones placeholder
function verDetalleConteo(id) {
    mostrarAlerta('Vista de detalle en desarrollo', 'info');
}

function editarConteo(id) {
    mostrarAlerta('Función de edición en desarrollo', 'info');
}

// Exportar funciones globales
window.iniciarPeriodoConteo = iniciarPeriodoConteo;
window.guardarNuevoPeriodo = guardarNuevoPeriodo;
window.generarConteosAleatorios = generarConteosAleatorios;
window.guardarConteosAleatorios = guardarConteosAleatorios;
window.mostrarModalProcesarConteo = mostrarModalProcesarConteo;
window.guardarConteoFisico = guardarConteoFisico;
window.aplicarFiltrosConteos = aplicarFiltrosConteos;
window.limpiarFiltrosConteos = limpiarFiltrosConteos;
window.verDetalleConteo = verDetalleConteo;
window.editarConteo = editarConteo;