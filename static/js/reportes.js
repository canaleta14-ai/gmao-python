// reportes.js - Funcionalidad para reportes de inventario

// Variables globales
let tipoReporteActual = 'valoracion';
let datosReporteActual = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    console.log('Inicializando módulo de reportes...');

    // Establecer fechas por defecto
    establecerFechasPorDefecto();

    // Cargar parámetros del primer reporte
    seleccionarTipoReporte('valoracion');

    // Generar reporte inicial
    setTimeout(() => {
        generarReporte();
    }, 500);
});

// Establecer fechas por defecto
function establecerFechasPorDefecto() {
    const hoy = new Date();
    const primerDiaMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);

    // Formatear fechas para inputs
    const fechaHoy = hoy.toISOString().split('T')[0];
    const fechaPrimerDia = primerDiaMes.toISOString().split('T')[0];

    // Establecer en templates
    setTimeout(() => {
        const fechaCorte = document.getElementById('param-fecha-corte');
        if (fechaCorte) fechaCorte.value = fechaHoy;

        const fechaDesde = document.getElementById('param-fecha-desde');
        if (fechaDesde) fechaDesde.value = fechaPrimerDia;

        const fechaHasta = document.getElementById('param-fecha-hasta');
        if (fechaHasta) fechaHasta.value = fechaHoy;
    }, 100);
}

// Seleccionar tipo de reporte
function seleccionarTipoReporte(tipo) {
    tipoReporteActual = tipo;

    // Actualizar lista activa
    document.querySelectorAll('#lista-tipos-reporte .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');

    // Cargar parámetros correspondientes
    cargarParametrosReporte(tipo);

    // Actualizar título
    actualizarTituloReporte(tipo);
}

// Cargar parámetros del reporte
function cargarParametrosReporte(tipo) {
    const parametrosContainer = document.getElementById('parametros-reporte');
    let templateId = 'template-generico';

    switch (tipo) {
        case 'valoracion':
            templateId = 'template-valoracion';
            break;
        case 'movimientos':
            templateId = 'template-movimientos';
            break;
        case 'stock-bajo':
            templateId = 'template-stock-bajo';
            break;
        default:
            templateId = 'template-generico';
    }

    const template = document.getElementById(templateId);
    if (template) {
        parametrosContainer.innerHTML = template.innerHTML;
        establecerFechasPorDefecto();
    }
}

// Actualizar título del reporte
function actualizarTituloReporte(tipo) {
    const titulos = {
        'valoracion': 'Valoración de Stock',
        'movimientos': 'Movimientos de Inventario',
        'stock-bajo': 'Artículos con Stock Bajo',
        'criticos': 'Artículos Críticos',
        'conteos': 'Resumen de Conteos',
        'abc': 'Análisis ABC',
        'rotacion': 'Rotación de Inventario'
    };

    document.getElementById('titulo-reporte').textContent = titulos[tipo] || 'Reporte de Inventario';
}

// Generar reporte
async function generarReporte() {
    const loadingDiv = document.getElementById('loading-reporte');
    const contenidoDiv = document.getElementById('contenido-reporte');

    // Mostrar loading
    loadingDiv.style.display = 'block';
    contenidoDiv.style.display = 'none';

    try {
        // Simular llamada a API
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Generar datos mock según el tipo
        let datos;
        switch (tipoReporteActual) {
            case 'valoracion':
                datos = generarDatosValoracion();
                break;
            case 'movimientos':
                datos = generarDatosMovimientos();
                break;
            case 'stock-bajo':
                datos = generarDatosStockBajo();
                break;
            case 'criticos':
                datos = generarDatosCriticos();
                break;
            case 'conteos':
                datos = generarDatosConteos();
                break;
            default:
                datos = { mensaje: 'Reporte en desarrollo' };
        }

        datosReporteActual = datos;
        mostrarResultadosReporte(datos);

        // Actualizar timestamp
        document.getElementById('ultima-actualizacion').textContent = new Date().toLocaleString('es-ES');

    } catch (error) {
        console.error('Error al generar reporte:', error);
        contenidoDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error al generar el reporte. Por favor, inténtelo de nuevo.
            </div>
        `;
    } finally {
        // Ocultar loading
        loadingDiv.style.display = 'none';
        contenidoDiv.style.display = 'block';
    }
}

// Mostrar resultados del reporte
function mostrarResultadosReporte(datos) {
    const contenidoDiv = document.getElementById('contenido-reporte');

    switch (tipoReporteActual) {
        case 'valoracion':
            contenidoDiv.innerHTML = generarHTMLValoracion(datos);
            break;
        case 'movimientos':
            contenidoDiv.innerHTML = generarHTMLMovimientos(datos);
            break;
        case 'stock-bajo':
            contenidoDiv.innerHTML = generarHTMLStockBajo(datos);
            break;
        case 'criticos':
            contenidoDiv.innerHTML = generarHTMLCriticos(datos);
            break;
        case 'conteos':
            contenidoDiv.innerHTML = generarHTMLConteos(datos);
            break;
        default:
            contenidoDiv.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    ${datos.mensaje || 'Reporte en desarrollo'}
                </div>
            `;
    }
}

// Generar datos mock para valoración
function generarDatosValoracion() {
    return {
        resumen: {
            total_articulos: 234,
            valor_total: 45678.90,
            articulos_con_stock: 198,
            valor_con_stock: 42341.25
        },
        por_categoria: [
            { categoria: 'Mecánicos', cantidad: 89, valor: 18456.30 },
            { categoria: 'Eléctricos', cantidad: 67, valor: 12789.45 },
            { categoria: 'Hidráulicos', cantidad: 45, valor: 8934.20 },
            { categoria: 'Neumáticos', cantidad: 23, valor: 5432.10 },
            { categoria: 'Lubricantes', cantidad: 8, valor: 2341.80 }
        ],
        top_articulos: [
            { codigo: 'REP001', descripcion: 'Motor eléctrico 5HP', stock: 5, valor_unitario: 850.00, valor_total: 4250.00 },
            { codigo: 'REP002', descripcion: 'Bomba hidráulica', stock: 3, valor_unitario: 1200.00, valor_total: 3600.00 },
            { codigo: 'REP003', descripcion: 'Variador de frecuencia', stock: 2, valor_unitario: 1500.00, valor_total: 3000.00 }
        ]
    };
}

// Generar HTML para valoración
function generarHTMLValoracion(datos) {
    return `
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card border-primary">
                    <div class="card-body text-center">
                        <h5 class="text-primary">${datos.resumen.total_articulos}</h5>
                        <small class="text-muted">Total Artículos</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-success">
                    <div class="card-body text-center">
                        <h5 class="text-success">${formatearMoneda(datos.resumen.valor_total)}</h5>
                        <small class="text-muted">Valor Total</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-info">
                    <div class="card-body text-center">
                        <h5 class="text-info">${datos.resumen.articulos_con_stock}</h5>
                        <small class="text-muted">Con Stock</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-warning">
                    <div class="card-body text-center">
                        <h5 class="text-warning">${formatearMoneda(datos.resumen.valor_con_stock)}</h5>
                        <small class="text-muted">Valor Stock</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <h6>Valoración por Categoría</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Categoría</th>
                                <th>Cantidad</th>
                                <th>Valor</th>
                                <th>%</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${datos.por_categoria.map(cat => `
                                <tr>
                                    <td>${cat.categoria}</td>
                                    <td>${cat.cantidad}</td>
                                    <td>${formatearMoneda(cat.valor)}</td>
                                    <td>${((cat.valor / datos.resumen.valor_total) * 100).toFixed(1)}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="col-md-6">
                <h6>Artículos de Mayor Valor</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Descripción</th>
                                <th>Stock</th>
                                <th>Valor Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${datos.top_articulos.map(art => `
                                <tr>
                                    <td><code>${art.codigo}</code></td>
                                    <td>${art.descripcion}</td>
                                    <td>${art.stock}</td>
                                    <td><strong>${formatearMoneda(art.valor_total)}</strong></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Generar datos mock para movimientos
function generarDatosMovimientos() {
    return {
        total_movimientos: 156,
        movimientos: [
            { fecha: '2024-09-20', tipo: 'entrada', articulo: 'REP001', cantidad: 10, motivo: 'Compra a proveedor' },
            { fecha: '2024-09-21', tipo: 'salida', articulo: 'REP002', cantidad: 2, motivo: 'Orden de trabajo #123' },
            { fecha: '2024-09-22', tipo: 'ajuste', articulo: 'REP003', cantidad: -1, motivo: 'Diferencia inventario' }
        ]
    };
}

// Generar HTML para movimientos
function generarHTMLMovimientos(datos) {
    return `
        <div class="mb-3">
            <h6>Total de movimientos: ${datos.total_movimientos}</h6>
        </div>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Tipo</th>
                        <th>Artículo</th>
                        <th>Cantidad</th>
                        <th>Motivo</th>
                    </tr>
                </thead>
                <tbody>
                    ${datos.movimientos.map(mov => `
                        <tr>
                            <td>${formatearFecha(mov.fecha)}</td>
                            <td><span class="badge bg-${obtenerColorTipo(mov.tipo)}">${mov.tipo}</span></td>
                            <td><code>${mov.articulo}</code></td>
                            <td>${mov.cantidad > 0 ? '+' : ''}${mov.cantidad}</td>
                            <td>${mov.motivo}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Generar datos mock para stock bajo
function generarDatosStockBajo() {
    return {
        articulos: [
            { codigo: 'REP001', descripcion: 'Filtro aceite', stock_actual: 2, stock_minimo: 5, urgencia: 'alta' },
            { codigo: 'REP002', descripcion: 'Correa distribución', stock_actual: 1, stock_minimo: 3, urgencia: 'media' },
            { codigo: 'REP003', descripcion: 'Pastillas freno', stock_actual: 0, stock_minimo: 2, urgencia: 'critica' }
        ]
    };
}

// Generar HTML para stock bajo
function generarHTMLStockBajo(datos) {
    return `
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Descripción</th>
                        <th>Stock Actual</th>
                        <th>Stock Mínimo</th>
                        <th>Urgencia</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    ${datos.articulos.map(art => `
                        <tr>
                            <td><code>${art.codigo}</code></td>
                            <td>${art.descripcion}</td>
                            <td><span class="badge bg-${art.stock_actual === 0 ? 'danger' : 'warning'}">${art.stock_actual}</span></td>
                            <td>${art.stock_minimo}</td>
                            <td><span class="badge bg-${obtenerColorUrgencia(art.urgencia)}">${art.urgencia}</span></td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="generarOrdenCompra('${art.codigo}')">
                                    <i class="fas fa-shopping-cart"></i> Comprar
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Generar datos mock para críticos
function generarDatosCriticos() {
    return {
        articulos: [
            { codigo: 'CRIT001', descripcion: 'Motor principal', stock: 1, estado: 'disponible' },
            { codigo: 'CRIT002', descripcion: 'Controlador PLC', stock: 0, estado: 'agotado' }
        ]
    };
}

// Generar HTML para críticos
function generarHTMLCriticos(datos) {
    return `
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Atención:</strong> Los siguientes artículos están marcados como críticos para la operación.
        </div>
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Descripción</th>
                        <th>Stock</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    ${datos.articulos.map(art => `
                        <tr class="${art.stock === 0 ? 'table-danger' : ''}">
                            <td><code>${art.codigo}</code></td>
                            <td>${art.descripcion}</td>
                            <td><span class="badge bg-${art.stock === 0 ? 'danger' : 'success'}">${art.stock}</span></td>
                            <td><span class="badge bg-${art.estado === 'agotado' ? 'danger' : 'success'}">${art.estado}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Generar datos mock para conteos
function generarDatosConteos() {
    return {
        resumen: {
            total_conteos: 45,
            completados: 32,
            pendientes: 13,
            diferencias: 8
        }
    };
}

// Generar HTML para conteos
function generarHTMLConteos(datos) {
    return `
        <div class="row">
            <div class="col-md-3">
                <div class="card border-primary">
                    <div class="card-body text-center">
                        <h4 class="text-primary">${datos.resumen.total_conteos}</h4>
                        <small class="text-muted">Total Conteos</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-success">
                    <div class="card-body text-center">
                        <h4 class="text-success">${datos.resumen.completados}</h4>
                        <small class="text-muted">Completados</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-warning">
                    <div class="card-body text-center">
                        <h4 class="text-warning">${datos.resumen.pendientes}</h4>
                        <small class="text-muted">Pendientes</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-danger">
                    <div class="card-body text-center">
                        <h4 class="text-danger">${datos.resumen.diferencias}</h4>
                        <small class="text-muted">Con Diferencias</small>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-4">
            <p class="text-muted">Progreso de conteos: ${((datos.resumen.completados / datos.resumen.total_conteos) * 100).toFixed(1)}%</p>
            <div class="progress">
                <div class="progress-bar" style="width: ${(datos.resumen.completados / datos.resumen.total_conteos) * 100}%"></div>
            </div>
        </div>
    `;
}

// Funciones auxiliares
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(valor);
}

function formatearFecha(fechaString) {
    const fecha = new Date(fechaString);
    return fecha.toLocaleDateString('es-ES');
}

function obtenerColorTipo(tipo) {
    const colores = {
        'entrada': 'success',
        'salida': 'danger',
        'ajuste': 'warning',
        'regularizacion': 'info'
    };
    return colores[tipo] || 'secondary';
}

function obtenerColorUrgencia(urgencia) {
    const colores = {
        'critica': 'danger',
        'alta': 'warning',
        'media': 'info',
        'baja': 'secondary'
    };
    return colores[urgencia] || 'secondary';
}

// Funciones de exportación
function exportarReporte() {
    if (!datosReporteActual) {
        alert('No hay datos para exportar. Genere un reporte primero.');
        return;
    }

    // Simulación de exportación
    mostrarAlerta('Exportación a Excel en desarrollo', 'info');
}

function generarReportePDF() {
    if (!datosReporteActual) {
        alert('No hay datos para exportar. Genere un reporte primero.');
        return;
    }

    // Simulación de generación PDF
    mostrarAlerta('Generación de PDF en desarrollo', 'info');
}

function generarOrdenCompra(codigo) {
    mostrarAlerta(`Función de orden de compra para ${codigo} en desarrollo`, 'info');
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

// Exportar funciones globales
window.seleccionarTipoReporte = seleccionarTipoReporte;
window.generarReporte = generarReporte;
window.exportarReporte = exportarReporte;
window.generarReportePDF = generarReportePDF;
window.generarOrdenCompra = generarOrdenCompra;