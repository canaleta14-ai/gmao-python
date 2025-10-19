// conteos.js - Funcionalidad para gestión de conteos de inventario

// Variables globales
let conteosActuales = [];
let paginaActualConteos = 1;
let conteosPorPagina = 15;
let filtrosConteos = {};

// Inicialización
document.addEventListener("DOMContentLoaded", function () {
  console.log("Inicializando módulo de conteos...");

  // Establecer fecha actual por defecto
  const hoy = new Date();
  document.getElementById("periodo-año").value = hoy.getFullYear();
  document.getElementById("periodo-mes").value = hoy.getMonth() + 1;

  // Cargar datos iniciales
  cargarResumenConteos();
  cargarConteos();

  // Configurar eventos
  configurarEventosConteos();
  configurarCalculoDiferencia();

  // Inicializar autocompletado de usuarios
  inicializarAutocompletadoUsuarios();
});

// Cargar resumen de conteos
async function cargarResumenConteos() {
  try {
    const response = await fetch("/inventario/api/conteos/resumen");
    const data = await response.json();

    if (data.success) {
      const resumen = data.resumen;
      document.getElementById("periodo-actual").textContent =
        resumen.periodo_actual;
      document.getElementById("total-conteos").textContent =
        resumen.total_conteos;
      document.getElementById("conteos-completados").textContent =
        resumen.conteos_completados;
      document.getElementById("conteos-diferencias").textContent =
        resumen.conteos_diferencias;
    } else {
      console.error("Error en respuesta:", data.error);
      mostrarAlerta("Error al cargar resumen: " + data.error, "danger");
    }
  } catch (error) {
    console.error("Error al cargar resumen:", error);
    mostrarAlerta("Error al cargar resumen de conteos", "danger");
  }
}

// Cargar conteos
async function cargarConteos(page = 1, filtros = {}) {
  try {
    // Construir parámetros de la URL
    const params = new URLSearchParams({
      page: page,
      per_page: conteosPorPagina,
    });

    // Agregar filtros si existen
    if (filtros.tipo_conteo) params.append("tipo_conteo", filtros.tipo_conteo);
    if (filtros.estado) params.append("estado", filtros.estado);
    if (filtros.fecha_desde) params.append("fecha_desde", filtros.fecha_desde);
    if (filtros.fecha_hasta) params.append("fecha_hasta", filtros.fecha_hasta);

    const response = await fetch(`/inventario/api/conteos?${params}`);
    const data = await response.json();

    if (data.success) {
      conteosActuales = data.conteos;
      actualizarTablaConteos(data.conteos);
      document.getElementById("total-conteos-lista").textContent =
        data.pagination.total;

      // Actualizar paginación si es necesario
      if (data.pagination.pages > 1) {
        // Aquí se puede agregar lógica de paginación
        console.log(
          `Página ${data.pagination.page} de ${data.pagination.pages}`
        );
      }
    } else {
      console.error("Error en respuesta:", data.error);
      mostrarAlerta("Error al cargar conteos: " + data.error, "danger");
    }
  } catch (error) {
    console.error("Error al cargar conteos:", error);
    mostrarAlerta("Error al cargar conteos", "danger");
  }
}

// Actualizar tabla de conteos
function actualizarTablaConteos(conteos) {
  const tbody = document.getElementById("tabla-conteos-body");

  if (!tbody) {
    console.error("❌ No se encontró el elemento tabla-conteos-body");
    return;
  }

  tbody.innerHTML = "";

  if (conteos.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="10" class="text-center text-muted">No hay conteos para mostrar</td></tr>';
    return;
  }

  conteos.forEach((conteo) => {
    try {
      const tr = document.createElement("tr");

      // Determinar estilos según diferencia
      let diferenciaClass = "";
      let estadoBadge = "bg-secondary";

      if (conteo.diferencia !== null) {
        if (Math.abs(conteo.diferencia) > 0) {
          diferenciaClass =
            conteo.diferencia > 0 ? "text-success" : "text-danger";
        }
      }

      switch (conteo.estado) {
        case "pendiente":
          estadoBadge = "bg-warning";
          break;
        case "validado":
          estadoBadge = "bg-success";
          break;
        case "regularizado":
          estadoBadge = "bg-primary";
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
                ${
                  conteo.stock_fisico !== null
                    ? `<strong>${conteo.stock_fisico}</strong>`
                    : '<span class="text-muted">-</span>'
                }
            </td>
            <td class="text-center ${diferenciaClass}">
                ${
                  conteo.diferencia !== null
                    ? `<strong>${conteo.diferencia > 0 ? "+" : ""}${
                        conteo.diferencia
                      }</strong>`
                    : '<span class="text-muted">-</span>'
                }
            </td>
            <td class="text-center ${diferenciaClass}">
                ${
                  conteo.porcentaje_diferencia !== null
                    ? `<strong>${
                        conteo.porcentaje_diferencia > 0 ? "+" : ""
                      }${conteo.porcentaje_diferencia.toFixed(1)}%</strong>`
                    : '<span class="text-muted">-</span>'
                }
            </td>
            <td>
                <span class="badge ${estadoBadge}">${conteo.estado}</span>
            </td>
            <td>
                ${conteo.usuario_conteo || '<span class="text-muted">-</span>'}
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    ${
                      conteo.estado === "pendiente"
                        ? `<button type="button" class="btn btn-sm btn-outline-success action-btn special" onclick="mostrarModalProcesarConteo(${conteo.id}, '${conteo.articulo.codigo}', '${conteo.articulo.descripcion}', ${conteo.stock_teorico})" title="Procesar conteo">
                            <i class="bi bi-check"></i>
                        </button>`
                        : `<button type="button" class="btn btn-sm btn-outline-primary action-btn view" onclick="verDetalleConteo(${conteo.id})" title="Ver detalle">
                            <i class="bi bi-eye"></i>
                        </button>`
                    }
                    <button type="button" class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarConteo(${
                      conteo.id
                    })" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    ${
                      conteo.estado === "pendiente"
                        ? `<button type="button" class="btn btn-sm btn-outline-danger action-btn delete" onclick="confirmarEliminarConteo(${conteo.id}, '${conteo.articulo.codigo}')" title="Eliminar conteo">
                            <i class="bi bi-trash"></i>
                        </button>`
                        : ""
                    }
                </div>
            </td>
        `;

      tbody.appendChild(tr);
    } catch (error) {
      console.error(`❌ Error al renderizar conteo:`, error);
      console.error(`📦 Datos del conteo problemático:`, conteo);
    }
  });
}

// Configurar eventos
function configurarEventosConteos() {
  // Filtros con auto-aplicación
  const filtros = [
    "filtro-tipo-conteo",
    "filtro-estado-conteo",
    "filtro-fecha-desde",
    "filtro-fecha-hasta",
  ];
  filtros.forEach((id) => {
    const elemento = document.getElementById(id);
    if (elemento) {
      elemento.addEventListener("change", aplicarFiltrosConteos);
    }
  });
}

// Aplicar filtros
function aplicarFiltrosConteos() {
  const filtros = {};

  const tipoConteo = document.getElementById("filtro-tipo-conteo").value;
  if (tipoConteo) filtros.tipo_conteo = tipoConteo;

  const estadoConteo = document.getElementById("filtro-estado-conteo").value;
  if (estadoConteo) filtros.estado = estadoConteo;

  const fechaDesde = document.getElementById("filtro-fecha-desde").value;
  if (fechaDesde) filtros.fecha_desde = fechaDesde;

  const fechaHasta = document.getElementById("filtro-fecha-hasta").value;
  if (fechaHasta) filtros.fecha_hasta = fechaHasta;

  filtrosConteos = filtros;
  paginaActualConteos = 1;
  cargarConteos(paginaActualConteos, filtros);
}

// Limpiar filtros
function limpiarFiltrosConteos() {
  document.getElementById("filtro-tipo-conteo").value = "";
  document.getElementById("filtro-estado-conteo").value = "";
  document.getElementById("filtro-fecha-desde").value = "";
  document.getElementById("filtro-fecha-hasta").value = "";

  filtrosConteos = {};
  paginaActualConteos = 1;
  cargarConteos();
}

// Iniciar período de conteo
function iniciarPeriodoConteo() {
  const modal = new bootstrap.Modal(
    document.getElementById("modalNuevoPeriodo")
  );
  document.getElementById("formNuevoPeriodo").reset();

  // Establecer fecha actual
  const hoy = new Date();
  document.getElementById("periodo-año").value = hoy.getFullYear();
  document.getElementById("periodo-mes").value = hoy.getMonth() + 1;

  // Llenar datalist de usuarios para el periodo
  llenarDatalistUsuarios("usuarios-datalist-periodo");

  // Intentar inicializar autocompletado avanzado si está disponible
  inicializarAutocompletadoUsuarioPeriodo();

  modal.show();
}

// Guardar nuevo período
async function guardarNuevoPeriodo() {
  const form = document.getElementById("formNuevoPeriodo");

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const usuarioInput = document.getElementById("periodo-responsable");
  const data = {
    año: parseInt(document.getElementById("periodo-año").value),
    mes: parseInt(document.getElementById("periodo-mes").value),
    usuario_responsable: usuarioInput.value, // Enviar el nombre del usuario
    observaciones: document.getElementById("periodo-observaciones").value,
  };

  console.log("📤 Enviando datos del período:", data);

  try {
    const response = await fetch("/inventario/api/periodos-inventario", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    console.log("📥 Respuesta del servidor:", result);

    if (result.success) {
      mostrarAlerta(result.message, "success");
      bootstrap.Modal.getInstance(
        document.getElementById("modalNuevoPeriodo")
      ).hide();
      cargarResumenConteos();
      cargarConteos();
    } else {
      mostrarAlerta("Error: " + result.error, "danger");
    }
  } catch (error) {
    console.error("Error:", error);
    mostrarAlerta("Error de conexión", "danger");
  }
}

// Generar conteos aleatorios
function generarConteosAleatorios() {
  const modal = new bootstrap.Modal(
    document.getElementById("modalConteosAleatorios")
  );
  document.getElementById("formConteosAleatorios").reset();
  document.getElementById("cantidad-conteos").value = 10;
  modal.show();
}

// Guardar conteos aleatorios
async function guardarConteosAleatorios() {
  const form = document.getElementById("formConteosAleatorios");

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const cantidad = parseInt(document.getElementById("cantidad-conteos").value);

  try {
    const response = await fetch("/inventario/api/conteos/aleatorios", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ cantidad }),
    });

    const result = await response.json();

    if (result.success) {
      mostrarAlerta(result.message, "success");
      bootstrap.Modal.getInstance(
        document.getElementById("modalConteosAleatorios")
      ).hide();
      cargarResumenConteos();
      cargarConteos();
    } else {
      mostrarAlerta(
        "Error: " + (result.error || "Error desconocido"),
        "danger"
      );
    }
  } catch (error) {
    console.error("Error:", error);
    mostrarAlerta("Error de conexión", "danger");
  }
}

// Mostrar modal procesar conteo
function mostrarModalProcesarConteo(
  conteoId,
  articuloCodigo,
  articuloDescripcion,
  stockTeorico
) {
  document.getElementById("conteo-id").value = conteoId;
  document.getElementById(
    "conteo-articulo-info"
  ).value = `${articuloCodigo} - ${articuloDescripcion}`;
  document.getElementById("conteo-stock-teorico").value = stockTeorico;
  document.getElementById("formProcesarConteo").reset();
  document.getElementById("conteo-id").value = conteoId;
  document.getElementById(
    "conteo-articulo-info"
  ).value = `${articuloCodigo} - ${articuloDescripcion}`;
  document.getElementById("conteo-stock-teorico").value = stockTeorico;

  // Ocultar información de diferencia
  document.getElementById("conteo-diferencia-info").style.display = "none";

  // Limpiar campo de usuario
  document.getElementById("conteo-usuario").value = "";
  delete document.getElementById("conteo-usuario").dataset.userId;

  const modal = new bootstrap.Modal(
    document.getElementById("modalProcesarConteo")
  );
  modal.show();

  // Reinicializar autocompletado de usuarios cuando se muestre el modal
  modal._element.addEventListener(
    "shown.bs.modal",
    function () {
      inicializarAutocompletadoUsuarios();
    },
    { once: true }
  );
}

// Configurar cálculo automático de diferencia
function configurarCalculoDiferencia() {
  const stockFisicoInput = document.getElementById("conteo-stock-fisico");
  if (stockFisicoInput) {
    stockFisicoInput.addEventListener("input", function () {
      calcularDiferencia();
    });
  }
}

// Calcular diferencia
function calcularDiferencia() {
  const stockTeorico =
    parseInt(document.getElementById("conteo-stock-teorico").value) || 0;
  const stockFisico = parseInt(
    document.getElementById("conteo-stock-fisico").value
  );

  if (stockFisico !== undefined && !isNaN(stockFisico)) {
    const diferencia = stockFisico - stockTeorico;
    const porcentajeDiferencia =
      stockTeorico > 0 ? (diferencia / stockTeorico) * 100 : 0;

    const infoDiv = document.getElementById("conteo-diferencia-info");

    let alertClass = "alert-info";
    let mensaje = "Sin diferencias";

    if (diferencia > 0) {
      alertClass = "alert-success";
      mensaje = `Exceso de ${diferencia} unidades (+${porcentajeDiferencia.toFixed(
        1
      )}%)`;
    } else if (diferencia < 0) {
      alertClass = "alert-danger";
      mensaje = `Faltante de ${Math.abs(
        diferencia
      )} unidades (${porcentajeDiferencia.toFixed(1)}%)`;
    }

    infoDiv.className = `alert ${alertClass}`;
    infoDiv.innerHTML = `
            <i class="fas fa-calculator"></i>
            <strong>Diferencia calculada:</strong> ${mensaje}
        `;
    infoDiv.style.display = "block";
  } else {
    document.getElementById("conteo-diferencia-info").style.display = "none";
  }
}

// Inicializar autocompletado de usuarios
function inicializarAutocompletadoUsuarios() {
  const usuarioInput = document.getElementById("conteo-usuario");

  console.log("🔄 Inicializando autocompletado de usuarios...");
  console.log("📝 Input element:", usuarioInput);
  console.log(
    "📚 AutoComplete available:",
    typeof AutoComplete !== "undefined"
  );

  if (!usuarioInput) {
    console.error("❌ No se encontró el elemento conteo-usuario");
    return;
  }

  // Verificar que el elemento esté completamente en el DOM
  if (!usuarioInput.parentNode) {
    console.warn("⚠️ Input no tiene parentNode - esperando un momento...");
    setTimeout(() => inicializarAutocompletadoUsuarios(), 100);
    return;
  }

  if (typeof AutoComplete === "undefined") {
    console.error("❌ AutoComplete no está disponible - usando fallback");
    // Usar un fallback simple con datalist
    crearDatalistUsuarios(usuarioInput);
    return;
  }

  try {
    // Verificar si ya existe una instancia
    if (usuarioInput._autocomplete) {
      console.log("🗑️ Destruyendo instancia anterior");
      usuarioInput._autocomplete.destroy();
    }

    const autocomplete = new AutoComplete({
      element: usuarioInput,
      apiUrl: "/usuarios/api/autocomplete",
      searchKey: "q",
      minChars: 2,
      debounceTime: 300,
      renderItem: function (item) {
        return `
                    <div class="autocomplete-item">
                        <strong>${item.username}</strong>
                        <br>
                        <small class="text-muted">
                            ${item.nombre || ""} - ${item.rol || ""}
                        </small>
                    </div>
                `;
      },
      onSelect: function (item) {
        usuarioInput.value = item.username;
        usuarioInput.dataset.userId = item.id;
      },
      // Agregar fallback para datos estáticos si la API falla
      localData: [
        { id: 1, username: "admin", nombre: "Administrador", rol: "admin" },
        {
          id: 2,
          username: "supervisor",
          nombre: "Supervisor",
          rol: "supervisor",
        },
        {
          id: 3,
          username: "tecnico1",
          nombre: "Técnico Principal",
          rol: "tecnico",
        },
        {
          id: 4,
          username: "tecnico2",
          nombre: "Técnico Auxiliar",
          rol: "tecnico",
        },
        { id: 5, username: "operador", nombre: "Operador", rol: "operador" },
      ],
    });

    // Guardar referencia para poder destruirla después
    usuarioInput._autocomplete = autocomplete;

    console.log("✅ Autocompletado de usuarios inicializado correctamente");
  } catch (error) {
    console.error("❌ Error al inicializar autocompletado de usuarios:", error);
    // Fallback: usar datalist simple
    crearDatalistUsuarios(usuarioInput);
  }
}

// Función fallback para crear un datalist simple
function crearDatalistUsuarios(input) {
  console.log("🔄 Creando datalist fallback para usuarios");

  // Crear datalist si no existe
  let datalist = document.getElementById("usuarios-datalist");
  if (!datalist) {
    datalist = document.createElement("datalist");
    datalist.id = "usuarios-datalist";

    // Datos de ejemplo
    const usuarios = [
      "admin",
      "supervisor",
      "tecnico1",
      "tecnico2",
      "operador",
      "mantenimiento",
      "jefe_taller",
    ];

    usuarios.forEach((usuario) => {
      const option = document.createElement("option");
      option.value = usuario;
      datalist.appendChild(option);
    });

    document.body.appendChild(datalist);
  }

  // Asociar datalist al input
  input.setAttribute("list", "usuarios-datalist");
  input.placeholder = "Escribe el nombre del usuario (ej: admin, tecnico1...)";

  console.log("✅ Datalist fallback creado");
}

// Función para llenar datalist de usuarios
async function llenarDatalistUsuarios(datalistId) {
  try {
    // Cargar usuarios reales desde la API
    const response = await fetch("/usuarios/api?per_page=100");
    if (!response.ok) {
      throw new Error("Error al cargar usuarios");
    }

    const data = await response.json();
    const usuarios = data.usuarios || [];

    const datalist = document.getElementById(datalistId);
    if (datalist) {
      datalist.innerHTML = "";

      // Filtrar solo usuarios activos
      const usuariosActivos = usuarios.filter((u) => u.estado === "Activo");

      usuariosActivos.forEach((usuario) => {
        const option = document.createElement("option");
        // Usar el nombre como value y mostrar nombre completo
        option.value = usuario.nombre;
        option.textContent = `${usuario.nombre} (${usuario.rol})`;
        // Guardar el username en un atributo data
        option.setAttribute(
          "data-username",
          usuario.email
            ? usuario.email.split("@")[0]
            : usuario.nombre.toLowerCase().replace(/\s+/g, "")
        );
        datalist.appendChild(option);
      });

      console.log(`✅ Cargados ${usuariosActivos.length} usuarios en datalist`);
    }
  } catch (error) {
    console.error("Error cargando usuarios:", error);
    // Fallback: usar datos por defecto
    const datalist = document.getElementById(datalistId);
    if (datalist) {
      datalist.innerHTML = `
        <option value="Administrador">Administrador (admin)</option>
        <option value="Supervisor">Supervisor (supervisor)</option>
      `;
    }
  }
}

// Inicializar autocompletado de usuarios para período
function inicializarAutocompletadoUsuarioPeriodo() {
  const usuarioInput = document.getElementById("periodo-responsable");

  console.log("🔄 Inicializando autocompletado de usuarios para período...");

  if (!usuarioInput) {
    console.error("❌ No se encontró el elemento periodo-responsable");
    return;
  }

  // Verificar que el elemento esté completamente en el DOM
  if (!usuarioInput.parentNode) {
    console.warn("⚠️ Input no tiene parentNode - esperando un momento...");
    setTimeout(() => inicializarAutocompletadoUsuarioPeriodo(), 100);
    return;
  }

  // DESHABILITADO: No usar AutoComplete complejo que causa problemas
  // Solo usar el datalist simple que ya fue llenado con usuarios reales
  console.log("� Usando solo datalist simple - AutoComplete deshabilitado");

  // Limpiar cualquier instancia anterior de AutoComplete si existe
  if (usuarioInput._autocomplete) {
    try {
      usuarioInput._autocomplete.destroy();
      delete usuarioInput._autocomplete;
      console.log("🗑️ Instancia anterior de AutoComplete eliminada");
    } catch (e) {
      console.warn("⚠️ Error al destruir autocomplete anterior:", e);
    }
  }

  console.log(
    "✅ Autocompletado de usuarios para período inicializado correctamente"
  );
}

// Guardar conteo físico
async function guardarConteoFisico() {
  const form = document.getElementById("formProcesarConteo");

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const conteoId = parseInt(document.getElementById("conteo-id").value);
  const stockFisico = parseInt(
    document.getElementById("conteo-stock-fisico").value
  );
  const usuario = document.getElementById("conteo-usuario").value;
  const observaciones = document.getElementById("conteo-observaciones").value;

  try {
    const response = await fetch(
      `/inventario/api/conteos/${conteoId}/procesar`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          stock_fisico: stockFisico,
          usuario: usuario,
          observaciones: observaciones,
        }),
      }
    );

    const result = await response.json();

    if (result.success) {
      mostrarAlerta(result.message, "success");
      bootstrap.Modal.getInstance(
        document.getElementById("modalProcesarConteo")
      ).hide();
      cargarResumenConteos();
      cargarConteos();
    } else {
      mostrarAlerta("Error: " + result.error, "danger");
    }
  } catch (error) {
    console.error("Error:", error);
    mostrarAlerta("Error de conexión", "danger");
  }
}

// Funciones auxiliares
function formatearFecha(fechaString) {
  const fecha = new Date(fechaString);
  return fecha.toLocaleDateString("es-ES");
}

function mostrarAlerta(mensaje, tipo) {
  // Crear contenedor si no existe
  let alertContainer = document.getElementById("alert-container");
  if (!alertContainer) {
    alertContainer = document.createElement("div");
    alertContainer.id = "alert-container";
    alertContainer.className = "position-fixed top-0 end-0 p-3";
    alertContainer.style.zIndex = "1055";
    document.body.appendChild(alertContainer);
  }

  // Crear alerta
  const alertDiv = document.createElement("div");
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
  const form = document.getElementById("formEditarConteo");

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const conteoId = parseInt(document.getElementById("editar-conteo-id").value);
  const stockFisico = parseInt(
    document.getElementById("editar-stock-fisico").value
  );
  const usuario = document.getElementById("editar-usuario").value;
  const observaciones = document.getElementById("editar-observaciones").value;

  try {
    const response = await fetch(`/inventario/api/conteos/${conteoId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        stock_fisico: stockFisico,
        usuario_conteo: usuario,
        observaciones: observaciones,
      }),
    });

    const result = await response.json();

    if (result.success) {
      mostrarAlerta(result.message, "success");
      bootstrap.Modal.getInstance(
        document.getElementById("modalEditarConteo")
      ).hide();
      cargarResumenConteos();
      cargarConteos();
    } else {
      mostrarAlerta("Error: " + result.error, "danger");
    }
  } catch (error) {
    console.error("Error:", error);
    mostrarAlerta("Error de conexión", "danger");
  }
}

// Funciones placeholder
async function verDetalleConteo(id) {
  try {
    const response = await fetch(`/inventario/api/conteos/${id}`);
    const data = await response.json();

    if (data.success) {
      const conteo = data.conteo;

      // Mostrar información del artículo y permitir editar
      editarConteo(id);
    } else {
      mostrarAlerta("Error al cargar detalle del conteo", "danger");
    }
  } catch (error) {
    console.error("Error al ver detalle:", error);
    mostrarAlerta("Error al cargar detalle del conteo", "danger");
  }
}

function editarConteo(id) {
  console.log("🔧 Editando conteo ID:", id);

  // Obtener datos del conteo
  fetch(`/inventario/api/conteos/${id}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const conteo = data.conteo;

        // Verificar que se pueda editar
        if (conteo.estado === "regularizado") {
          mostrarAlerta(
            "No se puede editar un conteo ya regularizado",
            "warning"
          );
          return;
        }

        // Llenar el modal con los datos
        document.getElementById("editar-conteo-id").value = conteo.id;
        document.getElementById(
          "editar-articulo-info"
        ).value = `${conteo.articulo.codigo} - ${conteo.articulo.descripcion}`;
        document.getElementById("editar-stock-teorico").value =
          conteo.stock_teorico;
        document.getElementById("editar-stock-fisico").value =
          conteo.stock_fisico || "";
        document.getElementById("editar-usuario").value =
          conteo.usuario_conteo || "";
        document.getElementById("editar-observaciones").value =
          conteo.observaciones || "";

        // Llenar datalist de usuarios para el modal de editar
        llenarDatalistUsuarios("usuarios-datalist-editar");

        // Mostrar el modal
        const modal = new bootstrap.Modal(
          document.getElementById("modalEditarConteo")
        );
        modal.show();
      } else {
        mostrarAlerta(
          "Error al cargar datos del conteo: " + data.error,
          "danger"
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      mostrarAlerta("Error de conexión al cargar el conteo", "danger");
    });
}

// Exportar funciones globales
window.iniciarPeriodoConteo = iniciarPeriodoConteo;
window.guardarNuevoPeriodo = guardarNuevoPeriodo;
window.generarConteosAleatorios = generarConteosAleatorios;
window.guardarConteosAleatorios = guardarConteosAleatorios;
window.mostrarModalProcesarConteo = mostrarModalProcesarConteo;
window.confirmarEliminarConteo = confirmarEliminarConteo;
window.eliminarConteo = eliminarConteo;

// Variables para eliminar conteo
let conteoIdParaEliminar = null;

// Confirmar eliminación de conteo
function confirmarEliminarConteo(id, codigoArticulo) {
  conteoIdParaEliminar = id;
  document.getElementById("codigo-articulo-eliminar-conteo").textContent =
    codigoArticulo;

  const modal = new bootstrap.Modal(
    document.getElementById("modalEliminarConteo")
  );
  modal.show();
}

// Eliminar conteo
async function eliminarConteo() {
  if (!conteoIdParaEliminar) return;

  try {
    const response = await fetch(
      `/inventario/api/conteos/${conteoIdParaEliminar}`,
      {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
      }
    );

    const data = await response.json();

    if (data.success) {
      mostrarAlerta("Conteo eliminado correctamente", "success");

      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("modalEliminarConteo")
      );
      modal.hide();

      // Recargar lista
      cargarConteos(paginaActualConteos, filtrosConteos);
      cargarResumenConteos();
    } else {
      mostrarAlerta("Error al eliminar conteo: " + data.error, "danger");
    }
  } catch (error) {
    console.error("Error:", error);
    mostrarAlerta("Error al eliminar el conteo", "danger");
  }

  conteoIdParaEliminar = null;
}

window.guardarConteoFisico = guardarConteoFisico;
window.guardarEditarConteo = guardarEditarConteo;
window.aplicarFiltrosConteos = aplicarFiltrosConteos;
window.limpiarFiltrosConteos = limpiarFiltrosConteos;
window.verDetalleConteo = verDetalleConteo;
window.editarConteo = editarConteo;
