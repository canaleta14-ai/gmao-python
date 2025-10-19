/**
 * Trazabilidad de Lotes FIFO
 * Visualización completa del historial y movimientos de un lote específico
 */

let datosLote = null;
let chartEvolucion = null;
let chartDistribucion = null;

/**
 * Cargar datos de trazabilidad desde la API
 */
async function cargarTrazabilidad(loteId) {
  try {
    document.getElementById("loading").style.display = "block";
    document.getElementById("contenido").style.display = "none";

    const response = await fetch(`/lotes/api/lotes/${loteId}/trazabilidad`);
    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Error al cargar los datos");
    }

    datosLote = data;

    // Renderizar todo
    renderizarInformacionLote(data.lote);
    renderizarEstadisticas(data.estadisticas);
    renderizarTimeline(data.movimientos);
    renderizarTablaMovimientos(data.movimientos);
    renderizarOrdenesTrabajo(data.ordenes_trabajo);
    crearGraficos(data);

    document.getElementById("loading").style.display = "none";
    document.getElementById("contenido").style.display = "block";
  } catch (error) {
    console.error("Error al cargar trazabilidad:", error);
    document.getElementById("loading").innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error al cargar la información: ${error.message}
            </div>
        `;
  }
}

/**
 * Renderizar información básica del lote
 */
function renderizarInformacionLote(lote) {
  const estadoVencimiento = lote.esta_vencido
    ? '<span class="badge bg-danger">Vencido</span>'
    : lote.dias_hasta_vencimiento !== null
    ? lote.dias_hasta_vencimiento < 30
      ? `<span class="badge bg-warning">Vence en ${lote.dias_hasta_vencimiento} días</span>`
      : `<span class="badge bg-success">Vence en ${lote.dias_hasta_vencimiento} días</span>`
    : '<span class="badge bg-secondary">Sin vencimiento</span>';

  const estadoLote = lote.activo
    ? '<span class="badge bg-success">Activo</span>'
    : '<span class="badge bg-secondary">Inactivo</span>';

  const proveedor = lote.proveedor
    ? `<span class="badge bg-info">${lote.proveedor.nombre}</span>`
    : '<span class="text-muted">Sin proveedor</span>';

  const html = `
        <div class="row">
            <div class="col-md-6">
                <table class="table table-sm">
                    <tr>
                        <th style="width: 40%;">Código Lote:</th>
                        <td><strong>${lote.codigo_lote || "N/A"}</strong></td>
                    </tr>
                    <tr>
                        <th>Artículo:</th>
                        <td>
                            <a href="/lotes/inventario/${
                              lote.inventario.id
                            }" class="text-decoration-none">
                                ${lote.inventario.codigo} - ${
    lote.inventario.nombre
  }
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <th>Unidad:</th>
                        <td>${lote.inventario.unidad_medida}</td>
                    </tr>
                    <tr>
                        <th>Fecha Entrada:</th>
                        <td>${formatearFecha(lote.fecha_entrada)}</td>
                    </tr>
                    <tr>
                        <th>Fecha Vencimiento:</th>
                        <td>${
                          lote.fecha_vencimiento
                            ? formatearFecha(lote.fecha_vencimiento)
                            : "Sin vencimiento"
                        } ${estadoVencimiento}</td>
                    </tr>
                    <tr>
                        <th>Estado:</th>
                        <td>${estadoLote}</td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6">
                <table class="table table-sm">
                    <tr>
                        <th style="width: 40%;">Documento Origen:</th>
                        <td>${lote.documento_origen || "N/A"}</td>
                    </tr>
                    <tr>
                        <th>Proveedor:</th>
                        <td>${proveedor}</td>
                    </tr>
                    <tr>
                        <th>Precio Unitario:</th>
                        <td><strong>$${formatearNumero(
                          lote.precio_unitario
                        )}</strong></td>
                    </tr>
                    <tr>
                        <th>Costo Total:</th>
                        <td><strong>$${formatearNumero(
                          lote.costo_total
                        )}</strong></td>
                    </tr>
                    <tr>
                        <th>Usuario Creación:</th>
                        <td>${lote.usuario_creacion || "N/A"}</td>
                    </tr>
                    <tr>
                        <th>Fecha Creación:</th>
                        <td>${formatearFecha(lote.fecha_creacion)}</td>
                    </tr>
                </table>
            </div>
        </div>
        ${
          lote.observaciones
            ? `
            <div class="alert alert-info mt-3">
                <strong>Observaciones:</strong> ${lote.observaciones}
            </div>
        `
            : ""
        }
    `;

  document.getElementById("info-lote").innerHTML = html;
}

/**
 * Renderizar estadísticas
 */
function renderizarEstadisticas(stats) {
  document.getElementById("stat-inicial").textContent = formatearNumero(
    datosLote.lote.cantidad_inicial
  );
  document.getElementById("stat-consumido").textContent = formatearNumero(
    stats.cantidad_consumida
  );
  document.getElementById("stat-disponible").textContent = formatearNumero(
    datosLote.lote.cantidad_actual
  );
  document.getElementById(
    "stat-porcentaje"
  ).textContent = `${stats.porcentaje_utilizado}%`;
}

/**
 * Renderizar timeline de movimientos
 */
function renderizarTimeline(movimientos) {
  if (movimientos.length === 0) {
    document.getElementById("timeline").innerHTML =
      '<p class="text-muted text-center">No hay movimientos registrados</p>';
    return;
  }

  let html = "";

  // Agregar entrada inicial
  html += crearItemTimeline("entrada", {
    fecha: datosLote.lote.fecha_entrada,
    cantidad: datosLote.lote.cantidad_inicial,
    tipo_movimiento: "entrada",
    observaciones: "Entrada inicial del lote",
    documento_referencia: datosLote.lote.documento_origen,
  });

  // Agregar movimientos
  movimientos.forEach((mov) => {
    html += crearItemTimeline(mov.tipo_movimiento, mov);
  });

  document.getElementById("timeline").innerHTML = html;
}

/**
 * Crear item individual del timeline
 */
function crearItemTimeline(tipo, movimiento) {
  const colores = {
    entrada: { bg: "success", icon: "box-arrow-in-down" },
    consumo: { bg: "danger", icon: "box-arrow-right" },
    reserva: { bg: "warning", icon: "bookmark" },
    liberacion: { bg: "info", icon: "arrow-counterclockwise" },
    ajuste: { bg: "secondary", icon: "wrench" },
  };

  const config = colores[tipo] || { bg: "secondary", icon: "circle" };

  const ordenInfo = movimiento.orden_trabajo
    ? `
        <div class="mt-2">
            <span class="badge bg-primary">
                <i class="bi bi-wrench me-1"></i>
                Orden: ${movimiento.orden_trabajo.numero}
            </span>
        </div>
    `
    : "";

  return `
        <div class="timeline-item">
            <div class="timeline-marker ${tipo}"></div>
            <div class="card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">
                                <span class="badge badge-tipo bg-${config.bg}">
                                    <i class="bi bi-${config.icon} me-1"></i>
                                    ${tipo.toUpperCase()}
                                </span>
                                <strong class="ms-2">${formatearNumero(
                                  movimiento.cantidad
                                )} ${
    datosLote.lote.inventario.unidad_medida
  }</strong>
                            </h6>
                            <p class="text-muted small mb-0">
                                <i class="bi bi-clock me-1"></i>
                                ${formatearFechaHora(movimiento.fecha)}
                            </p>
                        </div>
                        <div class="text-end">
                            ${
                              movimiento.usuario_id
                                ? `<small class="text-muted">Por: ${movimiento.usuario_id}</small>`
                                : ""
                            }
                        </div>
                    </div>
                    ${
                      movimiento.documento_referencia
                        ? `
                        <div class="mt-2">
                            <small><strong>Documento:</strong> ${movimiento.documento_referencia}</small>
                        </div>
                    `
                        : ""
                    }
                    ${
                      movimiento.observaciones
                        ? `
                        <div class="mt-2">
                            <small><strong>Observaciones:</strong> ${movimiento.observaciones}</small>
                        </div>
                    `
                        : ""
                    }
                    ${ordenInfo}
                </div>
            </div>
        </div>
    `;
}

/**
 * Renderizar tabla de movimientos
 */
function renderizarTablaMovimientos(movimientos) {
  const tbody = document.querySelector("#tabla-movimientos tbody");

  if (movimientos.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="6" class="text-center text-muted">No hay movimientos registrados</td></tr>';
    return;
  }

  let html = "";

  movimientos.forEach((mov) => {
    const badgeClass =
      {
        consumo: "danger",
        reserva: "warning",
        liberacion: "info",
        ajuste: "secondary",
      }[mov.tipo_movimiento] || "secondary";

    html += `
            <tr>
                <td>${formatearFechaHora(mov.fecha)}</td>
                <td><span class="badge bg-${badgeClass}">${
      mov.tipo_movimiento
    }</span></td>
                <td><strong>${formatearNumero(mov.cantidad)}</strong></td>
                <td>${mov.documento_referencia || "-"}</td>
                <td>${mov.usuario_id || "-"}</td>
                <td>${mov.observaciones || "-"}</td>
            </tr>
        `;
  });

  tbody.innerHTML = html;
}

/**
 * Renderizar órdenes de trabajo asociadas
 */
function renderizarOrdenesTrabajo(ordenes) {
  const tbody = document.querySelector("#tabla-ordenes tbody");

  if (ordenes.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="6" class="text-center text-muted">No hay órdenes asociadas</td></tr>';
    return;
  }

  let html = "";

  ordenes.forEach((orden) => {
    const estadoBadge =
      {
        pendiente: "warning",
        en_progreso: "info",
        completada: "success",
        cancelada: "danger",
      }[orden.estado] || "secondary";

    html += `
            <tr>
                <td><strong>${orden.numero}</strong></td>
                <td>${orden.descripcion}</td>
                <td>${
                  orden.activo
                    ? `${orden.activo.codigo} - ${orden.activo.nombre}`
                    : "-"
                }</td>
                <td><span class="badge bg-${estadoBadge}">${
      orden.estado
    }</span></td>
                <td>${formatearFecha(orden.fecha_creacion)}</td>
                <td>
                    <a href="/ordenes/${
                      orden.id
                    }" class="btn btn-sm btn-outline-info" target="_blank">
                        <i class="bi bi-eye"></i>
                    </a>
                </td>
            </tr>
        `;
  });

  tbody.innerHTML = html;
}

/**
 * Crear gráficos
 */
function crearGraficos(data) {
  crearGraficoEvolucion(data);
  crearGraficoDistribucion(data);
}

/**
 * Gráfico de evolución de cantidad
 */
function crearGraficoEvolucion(data) {
  const ctx = document.getElementById("chartEvolucion").getContext("2d");

  if (chartEvolucion) {
    chartEvolucion.destroy();
  }

  // Preparar datos para el gráfico
  const movimientos = [
    {
      fecha: data.lote.fecha_entrada,
      cantidad: data.lote.cantidad_inicial,
      tipo: "entrada",
    },
    ...data.movimientos,
  ];

  let cantidadActual = data.lote.cantidad_inicial;
  const labels = [];
  const valores = [];

  movimientos.forEach((mov) => {
    labels.push(formatearFecha(mov.fecha));

    if (mov.tipo_movimiento === "consumo") {
      cantidadActual -= mov.cantidad;
    } else if (mov.tipo_movimiento === "ajuste") {
      cantidadActual = mov.cantidad;
    }

    valores.push(cantidadActual);
  });

  chartEvolucion = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Cantidad Disponible",
          data: valores,
          borderColor: "#667eea",
          backgroundColor: "rgba(102, 126, 234, 0.1)",
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return formatearNumero(value);
            },
          },
        },
      },
    },
  });
}

/**
 * Gráfico de distribución por tipo de movimiento
 */
function crearGraficoDistribucion(data) {
  const ctx = document.getElementById("chartDistribucion").getContext("2d");

  if (chartDistribucion) {
    chartDistribucion.destroy();
  }

  const stats = data.estadisticas;

  chartDistribucion = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Consumido", "Reservado", "Liberado", "Disponible"],
      datasets: [
        {
          data: [
            stats.cantidad_consumida,
            stats.cantidad_reservada,
            stats.cantidad_liberada,
            data.lote.cantidad_actual,
          ],
          backgroundColor: ["#dc3545", "#ffc107", "#17a2b8", "#28a745"],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const label = context.label || "";
              const value = context.parsed || 0;
              return `${label}: ${formatearNumero(value)} ${
                data.lote.inventario.unidad_medida
              }`;
            },
          },
        },
      },
    },
  });
}

/**
 * Filtrar movimientos por tipo
 */
function filtrarMovimientos() {
  const filtro = document.getElementById("filtro-tipo").value;

  if (!datosLote) return;

  let movimientosFiltrados = datosLote.movimientos;

  if (filtro) {
    movimientosFiltrados = movimientosFiltrados.filter(
      (m) => m.tipo_movimiento === filtro
    );
  }

  renderizarTimeline(movimientosFiltrados);
  renderizarTablaMovimientos(movimientosFiltrados);
}

/**
 * Exportar a Excel
 */
function exportarExcel() {
  if (!datosLote) return;

  // Crear CSV
  let csv = "Fecha,Tipo,Cantidad,Documento,Usuario,Observaciones\n";

  datosLote.movimientos.forEach((mov) => {
    csv += `${formatearFechaHora(mov.fecha)},${mov.tipo_movimiento},${
      mov.cantidad
    },${mov.documento_referencia || ""},${mov.usuario_id || ""},${
      mov.observaciones || ""
    }\n`;
  });

  // Descargar
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute(
    "download",
    `trazabilidad_lote_${datosLote.lote.codigo_lote || datosLote.lote.id}.csv`
  );
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Funciones auxiliares de formateo
 */
function formatearFecha(fecha) {
  if (!fecha) return "-";
  const d = new Date(fecha);
  return d.toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatearFechaHora(fecha) {
  if (!fecha) return "-";
  const d = new Date(fecha);
  return d.toLocaleString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatearNumero(num) {
  if (num === null || num === undefined) return "0";
  return parseFloat(num).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
