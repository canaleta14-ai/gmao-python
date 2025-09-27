// asientos.js - Funcionalidad para gestión de asientos contables

// Variables globales
let asientosData = [];
let paginaActual = 1;
let asientosPorPagina = 10;
let asientoEditando = null;
let vistaDetallada = false;

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    console.log('Inicializando módulo de asientos contables...');

    // Establecer fecha actual por defecto
    establecerFechasPorDefecto();

    // Cargar datos iniciales
    cargarAsientos();

    // Configurar eventos
    configurarEventos();
});

// Establecer fechas por defecto
function establecerFechasPorDefecto() {
    const hoy = new Date();
    const primerDiaMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);

    const fechaHoy = hoy.toISOString().split('T')[0];
    const fechaPrimerDia = primerDiaMes.toISOString().split('T')[0];

    document.getElementById('fecha-desde').value = fechaPrimerDia;
    document.getElementById('fecha-hasta').value = fechaHoy;
    document.getElementById('asiento-fecha').value = fechaHoy;
}

// Configurar eventos
function configurarEventos() {
    // Eventos de filtros
    document.getElementById('filtro-numero').addEventListener('input', debounce(aplicarFiltros, 300));
    document.getElementById('filtro-cuenta').addEventListener('input', debounce(aplicarFiltros, 300));

    // Eventos del modal
    document.getElementById('modal-asiento').addEventListener('shown.bs.modal', function () {
        if (!asientoEditando) {
            // Agregar primera línea automáticamente
            agregarLinea();
        }
    });

    document.getElementById('modal-asiento').addEventListener('hidden.bs.modal', function () {
        limpiarFormularioAsiento();
    });
}

// Cargar asientos desde el servidor
async function cargarAsientos() {
    const loading = document.getElementById('loading-asientos');
    const tabla = document.getElementById('tabla-asientos');

    loading.style.display = 'block';
    tabla.style.display = 'none';

    try {
        // Simular llamada a API (reemplazar con endpoint real)
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Datos mock para demostración
        asientosData = generarDatosMockAsientos();

        mostrarAsientos();
        actualizarEstadisticas();
        generarPaginacion();

    } catch (error) {
        console.error('Error al cargar asientos:', error);
        mostrarMensaje('Error al cargar los asientos contables', 'danger');
    } finally {
        loading.style.display = 'none';
        tabla.style.display = 'block';
    }
}

// Generar datos mock para asientos
function generarDatosMockAsientos() {
    const asientos = [];
    const fechaHoy = new Date();

    for (let i = 1; i <= 25; i++) {
        const fecha = new Date(fechaHoy);
        fecha.setDate(fecha.getDate() - Math.floor(Math.random() * 30));

        const totalDebe = Math.random() * 5000 + 100;

        asientos.push({
            id: i,
            numero: `AST-${String(i).padStart(4, '0')}`,
            fecha: fecha.toISOString().split('T')[0],
            concepto: `Asiento contable ${i} - ${['Compra repuestos', 'Pago servicios', 'Regularización'][Math.floor(Math.random() * 3)]}`,
            total_debe: totalDebe,
            total_haber: totalDebe, // Asientos cuadrados
            estado: ['borrador', 'confirmado', 'cerrado'][Math.floor(Math.random() * 3)],
            lineas: generarLineasMock(totalDebe)
        });
    }

    return asientos.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
}

// Generar líneas mock para un asiento
function generarLineasMock(total) {
    const lineas = [];
    const numLineas = Math.floor(Math.random() * 3) + 2; // 2-4 líneas
    const montoPorLinea = total / numLineas;

    const cuentas = ['600000000', '622000000', '400000000', '570000000'];
    const conceptos = ['Compra material', 'Servicios técnicos', 'Pago a proveedor', 'Efectivo'];

    for (let i = 0; i < numLineas; i++) {
        const esDebe = Math.random() > 0.5;
        lineas.push({
            id: i + 1,
            cuenta_contable: cuentas[Math.floor(Math.random() * cuentas.length)],
            concepto: conceptos[Math.floor(Math.random() * conceptos.length)],
            debe: esDebe ? montoPorLinea : 0,
            haber: !esDebe ? montoPorLinea : 0
        });
    }

    return lineas;
}

// Mostrar asientos en la tabla
function mostrarAsientos() {
    const tbody = document.getElementById('lista-asientos');
    const filtros = obtenerFiltros();

    // Aplicar filtros
    let asientosFiltrados = asientosData.filter(asiento => {
        return (!filtros.numero || asiento.numero.toLowerCase().includes(filtros.numero.toLowerCase())) &&
            (!filtros.cuenta || asiento.lineas.some(linea => linea.cuenta_contable.includes(filtros.cuenta))) &&
            (!filtros.estado || asiento.estado === filtros.estado) &&
            (!filtros.fechaDesde || asiento.fecha >= filtros.fechaDesde) &&
            (!filtros.fechaHasta || asiento.fecha <= filtros.fechaHasta);
    });

    // Paginación
    const inicio = (paginaActual - 1) * asientosPorPagina;
    const fin = inicio + asientosPorPagina;
    const asientosPagina = asientosFiltrados.slice(inicio, fin);

    tbody.innerHTML = '';

    asientosPagina.forEach(asiento => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>
                <span class="num-asiento">${asiento.numero}</span>
            </td>
            <td>${formatearFecha(asiento.fecha)}</td>
            <td>
                <div class="concepto-truncado" title="${asiento.concepto}">
                    ${truncarTexto(asiento.concepto, 50)}
                </div>
            </td>
            <td class="debe-cell">
                <strong>${formatearMoneda(asiento.total_debe)}</strong>
            </td>
            <td class="haber-cell">
                <strong>${formatearMoneda(asiento.total_haber)}</strong>
            </td>
            <td>
                <span class="badge bg-${obtenerColorEstado(asiento.estado)}">${asiento.estado}</span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-sm btn-outline-primary action-btn view" onclick="verAsiento(${asiento.id})" title="Ver detalle">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarAsiento(${asiento.id})" 
                            title="Editar" ${asiento.estado === 'cerrado' ? 'disabled' : ''}>
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn delete" onclick="eliminarAsiento(${asiento.id})" 
                            title="Eliminar" ${asiento.estado === 'cerrado' ? 'disabled' : ''}>
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(fila);
    });

    // Actualizar información de paginación
    document.getElementById('info-paginacion').textContent =
        `Mostrando ${inicio + 1}-${Math.min(fin, asientosFiltrados.length)} de ${asientosFiltrados.length} asientos`;
}

// Actualizar estadísticas
function actualizarEstadisticas() {
    const filtros = obtenerFiltros();
    let asientosFiltrados = asientosData.filter(asiento => {
        return (!filtros.fechaDesde || asiento.fecha >= filtros.fechaDesde) &&
            (!filtros.fechaHasta || asiento.fecha <= filtros.fechaHasta);
    });

    const totalAsientos = asientosFiltrados.length;
    const totalDebe = asientosFiltrados.reduce((sum, asiento) => sum + asiento.total_debe, 0);
    const totalHaber = asientosFiltrados.reduce((sum, asiento) => sum + asiento.total_haber, 0);
    const balance = totalDebe - totalHaber;

    document.getElementById('total-asientos').textContent = totalAsientos;
    document.getElementById('total-debe').textContent = formatearMoneda(totalDebe);
    document.getElementById('total-haber').textContent = formatearMoneda(totalHaber);

    const balanceElement = document.getElementById('balance-general');
    balanceElement.textContent = formatearMoneda(Math.abs(balance));
    balanceElement.className = balance === 0 ? 'text-success' : 'text-danger';
}

// Obtener filtros actuales
function obtenerFiltros() {
    return {
        numero: document.getElementById('filtro-numero').value,
        cuenta: document.getElementById('filtro-cuenta').value,
        estado: document.getElementById('filtro-estado').value,
        fechaDesde: document.getElementById('fecha-desde').value,
        fechaHasta: document.getElementById('fecha-hasta').value
    };
}

// Aplicar filtros
function aplicarFiltros() {
    paginaActual = 1;
    mostrarAsientos();
    actualizarEstadisticas();
    generarPaginacion();
}

// Limpiar filtros
function limpiarFiltros() {
    document.getElementById('filtro-numero').value = '';
    document.getElementById('filtro-cuenta').value = '';
    document.getElementById('filtro-estado').value = '';
    establecerFechasPorDefecto();
    aplicarFiltros();
}

// Nuevo asiento
function nuevoAsiento() {
    asientoEditando = null;
    limpiarFormularioAsiento();

    // Generar número automático
    const proximoNumero = `AST-${String(asientosData.length + 1).padStart(4, '0')}`;
    document.getElementById('asiento-numero').value = proximoNumero;

    document.getElementById('titulo-modal-asiento').textContent = 'Nuevo Asiento Contable';

    const modal = new bootstrap.Modal(document.getElementById('modal-asiento'));
    modal.show();
}

// Editar asiento
function editarAsiento(id) {
    const asiento = asientosData.find(a => a.id === id);
    if (!asiento) return;

    if (asiento.estado === 'cerrado') {
        mostrarMensaje('No se puede editar un asiento cerrado', 'warning');
        return;
    }

    asientoEditando = asiento;

    // Cargar datos en el formulario
    document.getElementById('asiento-numero').value = asiento.numero;
    document.getElementById('asiento-fecha').value = asiento.fecha;
    document.getElementById('asiento-concepto').value = asiento.concepto;

    // Cargar líneas
    const tbody = document.getElementById('lineas-asiento');
    tbody.innerHTML = '';

    asiento.lineas.forEach(linea => {
        agregarLinea();
        const filas = tbody.querySelectorAll('tr');
        const ultimaFila = filas[filas.length - 1];

        ultimaFila.querySelector('.cuenta-select').value = linea.cuenta_contable;
        ultimaFila.querySelector('input[type="text"]').value = linea.concepto;
        ultimaFila.querySelector('.debe-input').value = linea.debe || '';
        ultimaFila.querySelector('.haber-input').value = linea.haber || '';
    });

    calcularTotales();

    document.getElementById('titulo-modal-asiento').textContent = 'Editar Asiento Contable';

    const modal = new bootstrap.Modal(document.getElementById('modal-asiento'));
    modal.show();
}

// Ver asiento
function verAsiento(id) {
    const asiento = asientosData.find(a => a.id === id);
    if (!asiento) return;

    const contenido = document.getElementById('contenido-ver-asiento');
    contenido.innerHTML = `
        <div class="row mb-3">
            <div class="col-md-6">
                <strong>Número:</strong> ${asiento.numero}<br>
                <strong>Fecha:</strong> ${formatearFecha(asiento.fecha)}<br>
                <strong>Estado:</strong> <span class="badge bg-${obtenerColorEstado(asiento.estado)}">${asiento.estado}</span>
            </div>
            <div class="col-md-6">
                <strong>Total Debe:</strong> ${formatearMoneda(asiento.total_debe)}<br>
                <strong>Total Haber:</strong> ${formatearMoneda(asiento.total_haber)}<br>
                <strong>Balance:</strong> <span class="balance-${asiento.total_debe === asiento.total_haber ? 'ok' : 'error'}">
                    ${formatearMoneda(Math.abs(asiento.total_debe - asiento.total_haber))}
                </span>
            </div>
        </div>
        <div class="mb-3">
            <strong>Concepto:</strong><br>
            ${asiento.concepto}
        </div>
        <div class="table-responsive">
            <table class="table table-bordered">
                <thead class="table-secondary">
                    <tr>
                        <th>Cuenta</th>
                        <th>Concepto</th>
                        <th>Debe</th>
                        <th>Haber</th>
                    </tr>
                </thead>
                <tbody>
                    ${asiento.lineas.map(linea => `
                        <tr>
                            <td><code>${linea.cuenta_contable}</code></td>
                            <td>${linea.concepto}</td>
                            <td class="debe-cell">${linea.debe ? formatearMoneda(linea.debe) : '-'}</td>
                            <td class="haber-cell">${linea.haber ? formatearMoneda(linea.haber) : '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
                <tfoot class="table-info">
                    <tr>
                        <td colspan="2"><strong>TOTALES</strong></td>
                        <td class="debe-cell"><strong>${formatearMoneda(asiento.total_debe)}</strong></td>
                        <td class="haber-cell"><strong>${formatearMoneda(asiento.total_haber)}</strong></td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('modal-ver-asiento'));
    modal.show();
}

// Eliminar asiento
function eliminarAsiento(id) {
    const asiento = asientosData.find(a => a.id === id);
    if (!asiento) return;

    if (asiento.estado === 'cerrado') {
        mostrarMensaje('No se puede eliminar un asiento cerrado', 'warning');
        return;
    }

    if (confirm(`¿Está seguro de que desea eliminar el asiento ${asiento.numero}?`)) {
        // Aquí iría la llamada a la API para eliminar
        const index = asientosData.findIndex(a => a.id === id);
        if (index > -1) {
            asientosData.splice(index, 1);
            mostrarAsientos();
            actualizarEstadisticas();
            generarPaginacion();
            mostrarMensaje('Asiento eliminado correctamente', 'success');
        }
    }
}

// Agregar línea al asiento
function agregarLinea() {
    const template = document.getElementById('template-linea-asiento');
    const clone = template.content.cloneNode(true);
    document.getElementById('lineas-asiento').appendChild(clone);
    calcularTotales();
}

// Eliminar línea del asiento
function eliminarLinea(boton) {
    const fila = boton.closest('tr');
    fila.remove();
    calcularTotales();
}

// Validar línea
function validarLinea(select) {
    const fila = select.closest('tr');
    const debeInput = fila.querySelector('.debe-input');
    const haberInput = fila.querySelector('.haber-input');

    // Asegurar que solo uno de los campos tenga valor
    debeInput.addEventListener('input', function () {
        if (this.value) haberInput.value = '';
    });

    haberInput.addEventListener('input', function () {
        if (this.value) debeInput.value = '';
    });
}

// Calcular totales
function calcularTotales() {
    const filas = document.querySelectorAll('#lineas-asiento tr');
    let totalDebe = 0;
    let totalHaber = 0;

    filas.forEach(fila => {
        const debe = parseFloat(fila.querySelector('.debe-input').value) || 0;
        const haber = parseFloat(fila.querySelector('.haber-input').value) || 0;
        totalDebe += debe;
        totalHaber += haber;
    });

    document.getElementById('total-debe-modal').textContent = formatearMoneda(totalDebe);
    document.getElementById('total-haber-modal').textContent = formatearMoneda(totalHaber);

    const balance = totalDebe - totalHaber;
    const balanceElement = document.getElementById('balance-modal');
    balanceElement.textContent = formatearMoneda(Math.abs(balance));

    if (balance === 0 && totalDebe > 0) {
        balanceElement.className = 'badge bg-success';
        balanceElement.textContent = 'Cuadrado';
        document.getElementById('btn-guardar-asiento').disabled = false;
    } else {
        balanceElement.className = 'badge bg-danger';
        balanceElement.textContent = formatearMoneda(Math.abs(balance));
        document.getElementById('btn-guardar-asiento').disabled = true;
    }
}

// Guardar asiento
async function guardarAsiento() {
    const form = document.getElementById('form-asiento');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Recopilar datos
    const asientoData = {
        numero: document.getElementById('asiento-numero').value,
        fecha: document.getElementById('asiento-fecha').value,
        concepto: document.getElementById('asiento-concepto').value,
        lineas: []
    };

    // Recopilar líneas
    const filas = document.querySelectorAll('#lineas-asiento tr');
    filas.forEach(fila => {
        const cuenta = fila.querySelector('.cuenta-select').value;
        const concepto = fila.querySelector('input[type="text"]').value;
        const debe = parseFloat(fila.querySelector('.debe-input').value) || 0;
        const haber = parseFloat(fila.querySelector('.haber-input').value) || 0;

        if (cuenta && (debe > 0 || haber > 0)) {
            asientoData.lineas.push({
                cuenta_contable: cuenta,
                concepto: concepto,
                debe: debe,
                haber: haber
            });
        }
    });

    if (asientoData.lineas.length < 2) {
        mostrarMensaje('El asiento debe tener al menos 2 líneas', 'warning');
        return;
    }

    try {
        // Simular guardado (reemplazar con llamada a API)
        await new Promise(resolve => setTimeout(resolve, 500));

        // Calcular totales
        asientoData.total_debe = asientoData.lineas.reduce((sum, linea) => sum + linea.debe, 0);
        asientoData.total_haber = asientoData.lineas.reduce((sum, linea) => sum + linea.haber, 0);
        asientoData.estado = 'borrador';

        if (asientoEditando) {
            // Actualizar existente
            const index = asientosData.findIndex(a => a.id === asientoEditando.id);
            asientosData[index] = { ...asientoEditando, ...asientoData };
            mostrarMensaje('Asiento actualizado correctamente', 'success');
        } else {
            // Crear nuevo
            asientoData.id = asientosData.length + 1;
            asientosData.unshift(asientoData);
            mostrarMensaje('Asiento creado correctamente', 'success');
        }

        // Cerrar modal y actualizar vista
        bootstrap.Modal.getInstance(document.getElementById('modal-asiento')).hide();
        mostrarAsientos();
        actualizarEstadisticas();
        generarPaginacion();

    } catch (error) {
        console.error('Error al guardar asiento:', error);
        mostrarMensaje('Error al guardar el asiento', 'danger');
    }
}

// Limpiar formulario de asiento
function limpiarFormularioAsiento() {
    document.getElementById('form-asiento').reset();
    document.getElementById('lineas-asiento').innerHTML = '';
    document.getElementById('total-debe-modal').textContent = '0.00';
    document.getElementById('total-haber-modal').textContent = '0.00';
    document.getElementById('balance-modal').textContent = '0.00';
    document.getElementById('balance-modal').className = 'badge bg-secondary';
    document.getElementById('btn-guardar-asiento').disabled = true;
    asientoEditando = null;
}

// Alternar vista
function alternarVista() {
    vistaDetallada = !vistaDetallada;

    const tabla = document.getElementById('tabla-asientos');
    const vistaDetalle = document.getElementById('vista-detallada');
    const icono = document.getElementById('icono-vista');
    const texto = document.getElementById('texto-vista');

    if (vistaDetallada) {
        tabla.style.display = 'none';
        vistaDetalle.style.display = 'block';
        icono.className = 'fas fa-list';
        texto.textContent = 'Vista Lista';
        mostrarVistaDetallada();
    } else {
        tabla.style.display = 'block';
        vistaDetalle.style.display = 'none';
        icono.className = 'fas fa-eye';
        texto.textContent = 'Vista Detallada';
    }
}

// Mostrar vista detallada
function mostrarVistaDetallada() {
    const container = document.getElementById('vista-detallada');
    const filtros = obtenerFiltros();

    let asientosFiltrados = asientosData.filter(asiento => {
        return (!filtros.numero || asiento.numero.toLowerCase().includes(filtros.numero.toLowerCase())) &&
            (!filtros.cuenta || asiento.lineas.some(linea => linea.cuenta_contable.includes(filtros.cuenta))) &&
            (!filtros.estado || asiento.estado === filtros.estado) &&
            (!filtros.fechaDesde || asiento.fecha >= filtros.fechaDesde) &&
            (!filtros.fechaHasta || asiento.fecha <= filtros.fechaHasta);
    });

    container.innerHTML = asientosFiltrados.map(asiento => `
        <div class="card mb-3">
            <div class="card-header asiento-header d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">
                        <span class="num-asiento">${asiento.numero}</span> - 
                        ${formatearFecha(asiento.fecha)}
                        <span class="badge bg-${obtenerColorEstado(asiento.estado)} ms-2">${asiento.estado}</span>
                    </h6>
                    <small class="text-muted">${asiento.concepto}</small>
                </div>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarAsiento(${asiento.id})" 
                            ${asiento.estado === 'cerrado' ? 'disabled' : ''}>
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn delete" onclick="eliminarAsiento(${asiento.id})" 
                            ${asiento.estado === 'cerrado' ? 'disabled' : ''}>
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-sm mb-0">
                        <thead>
                            <tr>
                                <th>Cuenta</th>
                                <th>Concepto</th>
                                <th>Debe</th>
                                <th>Haber</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${asiento.lineas.map(linea => `
                                <tr>
                                    <td><code>${linea.cuenta_contable}</code></td>
                                    <td>${linea.concepto}</td>
                                    <td class="debe-cell">${linea.debe ? formatearMoneda(linea.debe) : '-'}</td>
                                    <td class="haber-cell">${linea.haber ? formatearMoneda(linea.haber) : '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                        <tfoot class="table-info">
                            <tr>
                                <td colspan="2"><strong>TOTALES</strong></td>
                                <td class="debe-cell"><strong>${formatearMoneda(asiento.total_debe)}</strong></td>
                                <td class="haber-cell"><strong>${formatearMoneda(asiento.total_haber)}</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        </div>
    `).join('');
}

// Generar paginación
function generarPaginacion() {
    const filtros = obtenerFiltros();
    const asientosFiltrados = asientosData.filter(asiento => {
        return (!filtros.numero || asiento.numero.toLowerCase().includes(filtros.numero.toLowerCase())) &&
            (!filtros.cuenta || asiento.lineas.some(linea => linea.cuenta_contable.includes(filtros.cuenta))) &&
            (!filtros.estado || asiento.estado === filtros.estado) &&
            (!filtros.fechaDesde || asiento.fecha >= filtros.fechaDesde) &&
            (!filtros.fechaHasta || asiento.fecha <= filtros.fechaHasta);
    });

    const totalPaginas = Math.ceil(asientosFiltrados.length / asientosPorPagina);
    const paginacion = document.getElementById('paginacion-asientos');

    let html = '';

    // Botón anterior
    html += `
        <li class="page-item ${paginaActual === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual - 1})">Anterior</a>
        </li>
    `;

    // Números de página
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === 1 || i === totalPaginas || (i >= paginaActual - 2 && i <= paginaActual + 2)) {
            html += `
                <li class="page-item ${i === paginaActual ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="cambiarPagina(${i})">${i}</a>
                </li>
            `;
        } else if (i === paginaActual - 3 || i === paginaActual + 3) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }

    // Botón siguiente
    html += `
        <li class="page-item ${paginaActual === totalPaginas ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual + 1})">Siguiente</a>
        </li>
    `;

    paginacion.innerHTML = html;
}

// Cambiar página
function cambiarPagina(nuevaPagina) {
    const filtros = obtenerFiltros();
    const asientosFiltrados = asientosData.filter(asiento => {
        return (!filtros.numero || asiento.numero.toLowerCase().includes(filtros.numero.toLowerCase())) &&
            (!filtros.cuenta || asiento.lineas.some(linea => linea.cuenta_contable.includes(filtros.cuenta))) &&
            (!filtros.estado || asiento.estado === filtros.estado) &&
            (!filtros.fechaDesde || asiento.fecha >= filtros.fechaDesde) &&
            (!filtros.fechaHasta || asiento.fecha <= filtros.fechaHasta);
    });

    const totalPaginas = Math.ceil(asientosFiltrados.length / asientosPorPagina);

    if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
        paginaActual = nuevaPagina;
        mostrarAsientos();
        generarPaginacion();
    }
}

// Exportar asientos
function exportarAsientos() {
    mostrarMensaje('Función de exportación en desarrollo', 'info');
}

// Imprimir asiento
function imprimirAsiento() {
    window.print();
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

function truncarTexto(texto, maxLength) {
    return texto.length > maxLength ? texto.substring(0, maxLength) + '...' : texto;
}

function obtenerColorEstado(estado) {
    const colores = {
        'borrador': 'warning',
        'confirmado': 'info',
        'cerrado': 'success'
    };
    return colores[estado] || 'secondary';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function mostrarMensaje(mensaje, tipo) {
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
window.nuevoAsiento = nuevoAsiento;
window.editarAsiento = editarAsiento;
window.verAsiento = verAsiento;
window.eliminarAsiento = eliminarAsiento;
window.aplicarFiltros = aplicarFiltros;
window.limpiarFiltros = limpiarFiltros;
window.agregarLinea = agregarLinea;
window.eliminarLinea = eliminarLinea;
window.validarLinea = validarLinea;
window.calcularTotales = calcularTotales;
window.guardarAsiento = guardarAsiento;
window.alternarVista = alternarVista;
window.cambiarPagina = cambiarPagina;
window.exportarAsientos = exportarAsientos;
window.imprimirAsiento = imprimirAsiento;