// Gestión de Órdenes de Trabajo - JavaScript

// Variables globales
let ordenes = [];
let activos = [];
let tecnicos = [];
let ordenEditando = null;

// Variables de paginación
let currentPage = 1;
let perPage = 10;
let paginacionOrdenes;

// Inicialización cuando se carga la página
document.addEventListener("DOMContentLoaded", function () {
  console.log("Módulo de órdenes cargado");

  // Crear instancia de paginación
  paginacionOrdenes = createPagination("paginacion-ordenes", cargarOrdenes, {
    perPage: 10,
    showInfo: true,
    showSizeSelector: true,
  });

  if (document.getElementById("modalOrden")) {
    console.log("Modal de orden encontrado, cargando datos...");
    cargarDatosIniciales();
  }

  // Agregar listener al modal de recambios para inicializar autocompletado
  const modalRecambio = document.getElementById("modalAgregarRecambio");
  if (modalRecambio) {
    modalRecambio.addEventListener("shown.bs.modal", function () {
      inicializarAutocompletadoRecambio();
    });
  }

  cargarOrdenes();
});

// Cargar lista de órdenes con paginación
async function cargarOrdenes(page = 1) {
  try {
    currentPage = page;
    const params = new URLSearchParams({
      page: page,
      per_page: perPage,
    });

    const response = await fetch(`/ordenes/api?${params}`);
    if (response.ok) {
      const data = await response.json();
      ordenes = data.items || [];
      mostrarOrdenes();
      actualizarEstadisticas();

      // Renderizar paginación
      paginacionOrdenes.render(data.page, data.per_page, data.total);
    } else {
      throw new Error("Error al cargar órdenes");
    }
  } catch (error) {
    console.error("Error cargando órdenes:", error);
    mostrarMensaje("Error al cargar las órdenes", "danger");
  }
}

// Mostrar órdenes en la tabla
function mostrarOrdenes() {
  const tbody = document.getElementById("tabla-ordenes");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (ordenes.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="8" class="text-center">No hay órdenes de trabajo registradas</td></tr>';
    return;
  }

  ordenes.forEach((orden) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>#${orden.id}</td>
            <td>${orden.fecha_creacion || "N/A"}</td>
            <td>${orden.activo_nombre || "Sin asignar"}</td>
            <td class="col-tipo">${orden.tipo}</td>
            <td><span class="badge bg-${getBadgeColor(orden.prioridad)}">${
      orden.prioridad
    }</span></td>
            <td><span class="badge bg-${getEstadoBadgeColor(orden.estado)}">${
      orden.estado
    }</span></td>
            <td class="col-tecnico">${
              orden.tecnico_nombre || "Sin asignar"
            }</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary action-btn view" onclick="verOrden(${
                      orden.id
                    })" title="Ver detalles">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarOrden(${
                      orden.id
                    })" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info action-btn info" onclick="mostrarModalEstado(${
                      orden.id
                    })" title="Cambiar estado">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
            </td>
        `;
    tbody.appendChild(row);
  });
}

// Función para mostrar mensajes
function mostrarMensaje(mensaje, tipo = "info") {
  // Crear alerta Bootstrap
  const alertDiv = document.createElement("div");
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

// Ver detalles de una orden
function verOrden(id) {
  const orden = ordenes.find((o) => o.id === id);
  if (orden) {
    // Guardar ID de orden actual para gestión de recambios
    ordenActualId = id;

    document.getElementById("ver-orden-numero").textContent = `#${orden.id}`;
    document.getElementById("ver-orden-fecha").textContent =
      orden.fecha_creacion || "N/A";
    document.getElementById("ver-orden-tipo").textContent = orden.tipo || "N/A";
    document.getElementById(
      "ver-orden-prioridad"
    ).innerHTML = `<span class="badge bg-${getBadgeColor(orden.prioridad)}">${
      orden.prioridad
    }</span>`;
    document.getElementById(
      "ver-orden-estado"
    ).innerHTML = `<span class="badge bg-${getEstadoBadgeColor(
      orden.estado
    )}">${orden.estado}</span>`;
    document.getElementById("ver-orden-activo").textContent =
      orden.activo_nombre || "Sin asignar";
    document.getElementById("ver-orden-tecnico").textContent =
      orden.tecnico_nombre || "Sin asignar";
    document.getElementById("ver-orden-tiempo-estimado").textContent =
      orden.tiempo_estimado ? `${orden.tiempo_estimado} horas` : "N/A";
    document.getElementById("ver-orden-descripcion").textContent =
      orden.descripcion || "N/A";
    document.getElementById("ver-orden-observaciones").textContent =
      orden.observaciones || "Sin observaciones";
    document.getElementById("ver-orden-numero").dataset.ordenId = orden.id;

    // Cargar recambios de la orden
    cargarRecambiosOrden(id);

    const modal = new bootstrap.Modal(document.getElementById("modalVerOrden"));
    modal.show();
  }
}

// Editar una orden
async function editarOrden(id) {
  const orden = ordenes.find((o) => o.id === id);
  if (orden) {
    await cargarActivos();
    await cargarTecnicos();

    document.getElementById("orden-id").value = orden.id;
    document.getElementById("orden-tipo").value = orden.tipo || "";
    document.getElementById("orden-prioridad").value = orden.prioridad || "";
    document.getElementById("orden-activo").value = orden.activo_id || "";
    document.getElementById("orden-tecnico").value = orden.tecnico_id || "";
    document.getElementById("orden-fecha-programada").value =
      orden.fecha_programada || "";
    document.getElementById("orden-tiempo-estimado").value =
      orden.tiempo_estimado || "";
    document.getElementById("orden-descripcion").value =
      orden.descripcion || "";
    document.getElementById("orden-observaciones").value =
      orden.observaciones || "";

    document.getElementById("modalOrdenTitulo").innerHTML =
      '<i class="bi bi-pencil me-2"></i>Editar Orden de Trabajo';
    document.getElementById("boton-guardar-texto").textContent =
      "Actualizar Orden";

    // Inicializar manejo de archivos para edición
    inicializarArchivos(orden.id);

    const modal = new bootstrap.Modal(document.getElementById("modalOrden"));
    modal.show();
  }
}

// GESTIÓN DE ESTADOS - Nueva funcionalidad principal

// Mostrar modal para cambiar estado
function mostrarModalEstado(id) {
  const orden = ordenes.find((o) => o.id === id);
  if (orden) {
    document.getElementById("estado-orden-id").value = orden.id;
    document.getElementById("nuevo-estado").value = orden.estado;

    configurarEstadosValidos(orden.estado);

    const modalTitle = document.querySelector("#modalEstado .modal-title");
    modalTitle.innerHTML = `<i class="bi bi-arrow-repeat me-2"></i>Actualizar Estado - Orden #${orden.id}`;

    const modalBody = document.querySelector("#modalEstado .modal-body");
    const infoExistente = modalBody.querySelector(".orden-info");
    if (infoExistente) {
      infoExistente.remove();
    }

    const infoDiv = document.createElement("div");
    infoDiv.className = "orden-info alert alert-info mb-3";
    infoDiv.innerHTML = `
            <strong>Orden:</strong> ${orden.descripcion}<br>
            <strong>Estado actual:</strong> <span class="badge bg-${getEstadoBadgeColor(
              orden.estado
            )}">${orden.estado}</span><br>
            <strong>Técnico:</strong> ${orden.tecnico_nombre || "Sin asignar"}
        `;
    modalBody.insertBefore(infoDiv, modalBody.firstChild);

    const modal = new bootstrap.Modal(document.getElementById("modalEstado"));
    modal.show();
  }
}

// Configurar estados válidos según el estado actual
function configurarEstadosValidos(estadoActual) {
  const selectEstado = document.getElementById("nuevo-estado");
  const tiempoRealContainer = document.getElementById("tiempo-real-container");

  selectEstado.innerHTML = "";

  const transicionesValidas = {
    Pendiente: ["En Proceso", "Cancelada", "En Espera"],
    "En Proceso": ["Completada", "En Espera", "Cancelada"],
    "En Espera": ["En Proceso", "Pendiente", "Cancelada"],
    Completada: [],
    Cancelada: ["Pendiente"],
    Vencida: ["En Proceso", "Cancelada"],
  };

  const optionActual = document.createElement("option");
  optionActual.value = estadoActual;
  optionActual.textContent = `${estadoActual} (actual)`;
  optionActual.selected = true;
  selectEstado.appendChild(optionActual);

  const estadosValidos = transicionesValidas[estadoActual] || [];
  estadosValidos.forEach((estado) => {
    const option = document.createElement("option");
    option.value = estado;
    option.textContent = estado;
    selectEstado.appendChild(option);
  });

  if (tiempoRealContainer) {
    tiempoRealContainer.style.display = estadosValidos.includes("Completada")
      ? "block"
      : "none";
  }
}

// Actualizar estado de una orden
async function actualizarEstado() {
  const ordenId = document.getElementById("estado-orden-id").value;
  const nuevoEstado = document.getElementById("nuevo-estado").value;
  const observaciones = document.getElementById("observaciones-estado").value;
  const tiempoReal = document.getElementById("tiempo-real")
    ? document.getElementById("tiempo-real").value
    : null;

  if (!nuevoEstado) {
    mostrarMensaje("Debe seleccionar un nuevo estado", "warning");
    return;
  }

  try {
    const updateData = {
      estado: nuevoEstado,
      observaciones: observaciones || null,
    };

    if (nuevoEstado === "Completada" && tiempoReal) {
      updateData.tiempo_real = parseFloat(tiempoReal);
    }

    const response = await fetch(`/ordenes/api/${ordenId}/estado`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData),
    });

    if (response.ok) {
      mostrarMensaje(`Estado actualizado a: ${nuevoEstado}`, "success");

      // Si la orden se completó, descontar recambios automáticamente
      if (nuevoEstado === "Completada") {
        await descontarRecambiosAutomaticamente(ordenId);
      }

      const modal = bootstrap.Modal.getInstance(
        document.getElementById("modalEstado")
      );
      modal.hide();
      await cargarOrdenes(currentPage);
      document.getElementById("formEstado").reset();
    } else {
      const error = await response.json();
      throw new Error(error.mensaje || "Error al actualizar el estado");
    }
  } catch (error) {
    console.error("Error actualizando estado:", error);
    const mensajeError =
      error?.message || error?.toString() || "Error al actualizar el estado";
    mostrarMensaje(mensajeError, "danger");
  }
}

// Cambiar estado desde el modal de detalles
function cambiarEstadoDesdeDetalle() {
  const ordenId = parseInt(
    document.getElementById("ver-orden-numero").dataset.ordenId
  );
  const modalDetalle = bootstrap.Modal.getInstance(
    document.getElementById("modalVerOrden")
  );
  modalDetalle.hide();

  setTimeout(() => {
    mostrarModalEstado(ordenId);
  }, 300);
}

// Editar desde el modal de detalles
async function editarDesdeDetalle() {
  const ordenId = parseInt(
    document.getElementById("ver-orden-numero").dataset.ordenId
  );
  const modalDetalle = bootstrap.Modal.getInstance(
    document.getElementById("modalVerOrden")
  );
  modalDetalle.hide();

  setTimeout(async () => {
    await editarOrden(ordenId);
  }, 300);
}

// Actualizar estadísticas
function actualizarEstadisticas() {
  const stats = {
    pendientes: ordenes.filter((o) => o.estado === "Pendiente").length,
    enProceso: ordenes.filter((o) => o.estado === "En Proceso").length,
    completadas: ordenes.filter((o) => o.estado === "Completada").length,
    vencidas: ordenes.filter((o) => o.estado === "Vencida").length,
  };

  document.getElementById("stat-pendientes").textContent = stats.pendientes;
  document.getElementById("stat-en-proceso").textContent = stats.enProceso;
  document.getElementById("stat-completadas").textContent = stats.completadas;
  document.getElementById("stat-vencidas").textContent = stats.vencidas;
}

// Obtener color del badge según prioridad
function getBadgeColor(prioridad) {
  switch (prioridad) {
    case "Crítica":
      return "danger";
    case "Alta":
      return "warning";
    case "Media":
      return "info";
    case "Baja":
      return "secondary";
    default:
      return "secondary";
  }
}

// Obtener color del badge según estado
function getEstadoBadgeColor(estado) {
  switch (estado) {
    case "Pendiente":
      return "warning";
    case "En Proceso":
      return "info";
    case "Completada":
      return "success";
    case "Cancelada":
      return "secondary";
    case "En Espera":
      return "warning";
    case "Vencida":
      return "danger";
    default:
      return "secondary";
  }
}

// Cargar datos iniciales (activos y técnicos)
async function cargarDatosIniciales() {
  try {
    console.log("Iniciando carga de datos...");
    await Promise.all([cargarActivos(), cargarTecnicos()]);
    console.log("Datos iniciales cargados exitosamente");

    // Inicializar autocompletado después de cargar datos
    inicializarAutocompletado();
  } catch (error) {
    console.error("Error cargando datos iniciales:", error);
    mostrarMensaje("Error al cargar datos iniciales", "danger");
  }
}

// Cargar activos
async function cargarActivos() {
  try {
    const response = await fetch("/activos/api");
    if (response.ok) {
      const data = await response.json();
      activos = data;
      // Ya no necesitamos llenar select, usaremos autocompletado
      console.log(`Cargados ${activos.length} activos para autocompletado`);
    } else {
      console.error("Error al cargar activos");
    }
  } catch (error) {
    console.error("Error cargando activos:", error);
  }
}

// Cargar técnicos
async function cargarTecnicos() {
  try {
    console.log("Iniciando carga de técnicos...");
    const response = await fetch("/usuarios/api?per_page=100");
    console.log("Respuesta usuarios API:", await response.clone().json());

    if (response.ok) {
      const data = await response.json();
      console.log("Usuarios extraídos:", data.usuarios);

      // Filtrar solo usuarios activos con roles apropiados
      tecnicos = data.usuarios.filter((usuario) => {
        const esActivo = usuario.estado === "Activo";
        const rolValido = ["Técnico", "Administrador"].includes(usuario.rol);
        return esActivo && rolValido;
      });

      console.log("Técnicos filtrados:", tecnicos);

      // Ya no necesitamos llenar select, usaremos autocompletado
      console.log(`Cargados ${tecnicos.length} técnicos para autocompletado`);

      if (tecnicos.length === 0) {
        mostrarMensaje(
          "No hay técnicos disponibles para asignar órdenes",
          "warning"
        );
      }
    } else {
      console.error("Error al cargar técnicos");
    }
  } catch (error) {
    console.error("Error cargando técnicos:", error);
  }
}

// Llenar select de activos
function llenarSelectActivos() {
  const selectActivo = document.getElementById("orden-activo");
  if (!selectActivo) return;

  // Limpiar opciones existentes (excepto la primera)
  selectActivo.innerHTML = '<option value="">Seleccionar activo...</option>';

  activos.forEach((activo) => {
    const option = document.createElement("option");
    option.value = activo.id;
    option.textContent = `${activo.nombre} - ${
      activo.ubicacion || "Sin ubicación"
    }`;
    selectActivo.appendChild(option);
  });

  console.log(`Cargados ${activos.length} activos en el select`);
}

// Llenar select de técnicos
function llenarSelectTecnicos() {
  const selectTecnico = document.getElementById("orden-tecnico");
  if (!selectTecnico) {
    console.log("Select de técnico no encontrado");
    return;
  }

  console.log("Llenando select con técnicos:", tecnicos);

  // Limpiar opciones existentes (excepto la primera)
  selectTecnico.innerHTML = '<option value="">Asignar técnico...</option>';

  tecnicos.forEach((tecnico, index) => {
    console.log(`Agregando técnico ${index}:`, tecnico);
    const option = document.createElement("option");
    option.value = tecnico.id;

    // Usar solo nombre y rol (sin apellido)
    const nombre = tecnico.nombre || "Sin nombre";
    const rol = tecnico.rol || "Sin rol";
    option.textContent = `${nombre} - ${rol}`;
    selectTecnico.appendChild(option);
  });

  console.log(`Cargados ${tecnicos.length} técnicos en el select`);
  console.log("Select final HTML:", selectTecnico.innerHTML);
}

// Inicializar autocompletado en formularios
function inicializarAutocompletado() {
  console.log("Inicializando autocompletado en órdenes...");

  // Autocompletado para activos
  const activoInput = document.getElementById("orden-activo");
  if (activoInput && window.AutoComplete) {
    new AutoComplete({
      element: activoInput,
      localData: activos,
      displayKey: (item) =>
        `${item.nombre} - ${item.ubicacion || "Sin ubicación"} (${
          item.codigo
        })`,
      valueKey: "id",
      placeholder: "Buscar activo...",
      allowFreeText: false,
      customFilter: (item, query) => {
        if (!query || typeof query !== "string") return false;
        const q = query.toLowerCase();
        return (
          (item.nombre && item.nombre.toLowerCase().includes(q)) ||
          (item.codigo && item.codigo.toLowerCase().includes(q)) ||
          (item.ubicacion && item.ubicacion.toLowerCase().includes(q))
        );
      },
      onSelect: (item) => {
        console.log("Activo seleccionado:", item);
      },
    });
  }

  // Autocompletado para técnicos
  const tecnicoInput = document.getElementById("orden-tecnico");
  if (tecnicoInput && window.AutoComplete) {
    new AutoComplete({
      element: tecnicoInput,
      localData: tecnicos,
      displayKey: (item) => `${item.nombre} - ${item.rol}`,
      valueKey: "id",
      placeholder: "Buscar técnico...",
      allowFreeText: false,
      customFilter: (item, query) => {
        if (!query || typeof query !== "string") return false;
        const q = query.toLowerCase();
        return (
          (item.nombre && item.nombre.toLowerCase().includes(q)) ||
          (item.username && item.username.toLowerCase().includes(q)) ||
          (item.rol && item.rol.toLowerCase().includes(q))
        );
      },
      onSelect: (item) => {
        console.log("Técnico seleccionado:", item);
      },
    });
  }

  // Autocompletado para filtros de búsqueda
  const filtroBuscar = document.getElementById("filtro-buscar");
  if (filtroBuscar && window.AutoComplete) {
    new AutoComplete({
      element: filtroBuscar,
      localData: ordenes,
      displayKey: (item) => `#${item.id} - ${item.descripcion}`,
      valueKey: "descripcion",
      placeholder: "Buscar orden por descripción...",
      allowFreeText: true,
      customFilter: (item, query) => {
        if (!query || typeof query !== "string") return false;
        const q = query.toLowerCase();
        return (
          (item.descripcion && item.descripcion.toLowerCase().includes(q)) ||
          (item.id && item.id.toString().toLowerCase().includes(q)) ||
          (item.activo_nombre && item.activo_nombre.toLowerCase().includes(q))
        );
      },
      onSelect: (item) => {
        console.log("Orden filtrada:", item);
        aplicarFiltros(); // Aplicar filtros después de selección
      },
    });
  }

  console.log("Autocompletado inicializado en órdenes");

  // Configurar filtros en tiempo real
  configurarFiltrosOrdenes();
}

// Configurar event listeners para filtros
function configurarFiltrosOrdenes() {
  console.log("🔍 Configurando filtros de órdenes...");

  // Campo de búsqueda
  const filtroBuscar = document.getElementById("filtro-buscar");
  if (filtroBuscar) {
    filtroBuscar.addEventListener("input", aplicarFiltros);
    console.log("✅ Filtro de búsqueda configurado");
  }

  // Selectores de filtro
  const filtros = ["filtro-estado", "filtro-tipo", "filtro-prioridad"];
  filtros.forEach((filtroId) => {
    const elemento = document.getElementById(filtroId);
    if (elemento) {
      elemento.addEventListener("change", aplicarFiltros);
      console.log(`✅ Filtro ${filtroId} configurado`);
    }
  });
}

// Aplicar filtros a la lista de órdenes
function aplicarFiltros() {
  console.log("🔍 Aplicando filtros...");

  const textoBusqueda =
    document.getElementById("filtro-buscar")?.value.toLowerCase() || "";
  const filtroEstado = document.getElementById("filtro-estado")?.value || "";
  const filtroTipo = document.getElementById("filtro-tipo")?.value || "";
  const filtroPrioridad =
    document.getElementById("filtro-prioridad")?.value || "";

  let ordenesFiltradas = [...ordenes];

  // Filtro por texto de búsqueda
  if (textoBusqueda) {
    ordenesFiltradas = ordenesFiltradas.filter((orden) => {
      return (
        orden.descripcion.toLowerCase().includes(textoBusqueda) ||
        orden.id.toString().toLowerCase().includes(textoBusqueda) ||
        (orden.activo_nombre &&
          orden.activo_nombre.toLowerCase().includes(textoBusqueda)) ||
        (orden.tecnico_nombre &&
          orden.tecnico_nombre.toLowerCase().includes(textoBusqueda))
      );
    });
  }

  // Filtro por estado
  if (filtroEstado) {
    ordenesFiltradas = ordenesFiltradas.filter(
      (orden) => orden.estado === filtroEstado
    );
  }

  // Filtro por tipo
  if (filtroTipo) {
    ordenesFiltradas = ordenesFiltradas.filter(
      (orden) => orden.tipo === filtroTipo
    );
  }

  // Filtro por prioridad
  if (filtroPrioridad) {
    ordenesFiltradas = ordenesFiltradas.filter(
      (orden) => orden.prioridad === filtroPrioridad
    );
  }

  // Mostrar órdenes filtradas
  mostrarOrdenesFiltradas(ordenesFiltradas);

  console.log(
    `🔍 Filtros aplicados: ${ordenesFiltradas.length} de ${ordenes.length} órdenes`
  );
}

// Mostrar órdenes filtradas (versión específica para filtros)
function mostrarOrdenesFiltradas(ordenesFiltradas) {
  const tbody = document.getElementById("tabla-ordenes");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (ordenesFiltradas.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="9" class="text-center">No se encontraron órdenes con los filtros aplicados</td></tr>';
    return;
  }

  ordenesFiltradas.forEach((orden) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>#${orden.id}</td>
            <td>${orden.fecha_creacion || "N/A"}</td>
            <td>${orden.activo_nombre || "Sin asignar"}</td>
            <td>${orden.tipo}</td>
            <td>${orden.descripcion}</td>
            <td><span class="badge bg-${getBadgeColor(orden.prioridad)}">${
      orden.prioridad
    }</span></td>
            <td><span class="badge bg-${getEstadoBadgeColor(orden.estado)}">${
      orden.estado
    }</span></td>
            <td>${orden.tecnico_nombre || "Sin asignar"}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary action-btn view" onclick="verOrden(${
                      orden.id
                    })" title="Ver detalles">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarOrden(${
                      orden.id
                    })" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-info action-btn info" onclick="mostrarModalEstado(${
                      orden.id
                    })" title="Cambiar estado">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
            </td>
        `;
    tbody.appendChild(row);
  });
}

// Mostrar modal para nueva orden
function mostrarModalNuevaOrden() {
  // Resetear formulario
  document.getElementById("formOrden").reset();
  document.getElementById("orden-id").value = "";

  // Cambiar título del modal
  document.getElementById("modalOrdenTitulo").innerHTML =
    '<i class="bi bi-plus-circle me-2"></i>Nueva Orden de Trabajo';
  document.getElementById("boton-guardar-texto").textContent = "Crear Orden";

  // Cargar datos actuales
  cargarActivos();
  cargarTecnicos();

  // Inicializar manejo de archivos
  inicializarArchivos(null);

  // Mostrar modal
  const modal = new bootstrap.Modal(document.getElementById("modalOrden"));
  modal.show();
}

// Exportar CSV
async function exportarCSV() {
  try {
    if (typeof descargarCSVMejorado === "function") {
      await descargarCSVMejorado(
        "/ordenes/exportar-csv",
        "ordenes_trabajo_{fecha}",
        "CSV"
      );
    } else {
      // Fallback simple
      window.open("/ordenes/exportar-csv", "_blank");
    }
  } catch (error) {
    console.error("Error exportando CSV:", error);
    mostrarMensaje("Error al exportar CSV", "danger");
  }
}

// Guardar orden de trabajo
async function guardarOrden() {
  const form = document.getElementById("formOrden");
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  try {
    // Recopilar datos del formulario
    const ordenData = {
      tipo: document.getElementById("orden-tipo").value,
      prioridad: document.getElementById("orden-prioridad").value,
      activo_id: document.getElementById("orden-activo").value || null,
      tecnico_id: document.getElementById("orden-tecnico").value || null,
      fecha_programada:
        document.getElementById("orden-fecha-programada").value || null,
      tiempo_estimado:
        parseFloat(document.getElementById("orden-tiempo-estimado").value) ||
        null,
      descripcion: document.getElementById("orden-descripcion").value,
      observaciones:
        document.getElementById("orden-observaciones").value || null,
    };

    // Validar y limpiar datos antes de enviar
    if (ordenData.activo_id === "" || ordenData.activo_id === "null") {
      ordenData.activo_id = null;
    } else if (ordenData.activo_id) {
      ordenData.activo_id = parseInt(ordenData.activo_id);
    }

    if (ordenData.tecnico_id === "" || ordenData.tecnico_id === "null") {
      ordenData.tecnico_id = null;
    } else if (ordenData.tecnico_id) {
      ordenData.tecnico_id = parseInt(ordenData.tecnico_id);
    }

    // Log para debug
    console.log("Datos de orden a enviar:", ordenData);

    const ordenId = document.getElementById("orden-id").value;
    const esEdicion = ordenId && ordenId !== "";

    const url = esEdicion ? `/ordenes/api/${ordenId}` : "/ordenes";
    const method = esEdicion ? "PUT" : "POST";

    console.log(`Enviando ${method} a ${url}`);

    const response = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(ordenData),
    });

    if (response.ok) {
      const resultado = await response.json();
      const ordenIdFinal = esEdicion ? ordenId : resultado.id;

      // Subir archivos pendientes si es una orden nueva o si hay archivos pendientes
      if (archivosTemporales.length > 0) {
        try {
          await subirArchivosPendientes(ordenIdFinal);
        } catch (error) {
          console.error("Error al subir archivos:", error);
          mostrarMensaje(
            "Orden guardada, pero algunos archivos no se pudieron subir",
            "warning"
          );
        }
      }

      const mensaje = esEdicion
        ? "Orden actualizada exitosamente"
        : "Orden de trabajo creada exitosamente";
      mostrarMensaje(mensaje, "success");

      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("modalOrden")
      );
      modal.hide();

      // Recargar datos
      cargarOrdenes(currentPage);

      // Limpiar formulario
      form.reset();
      form.classList.remove("was-validated");

      // Limpiar archivos temporales
      archivosTemporales = [];
      limpiarListaArchivos();
    } else {
      let errorMessage = "Error al guardar la orden";
      try {
        const error = await response.json();
        errorMessage =
          error.mensaje ||
          error.message ||
          error.error ||
          "Error al guardar la orden";

        // Log detallado para debug
        console.error("Detalles del error del servidor:", {
          status: response.status,
          statusText: response.statusText,
          errorData: error,
          ordenData: ordenData,
        });
      } catch (parseError) {
        console.error("Error al parsear respuesta de error:", parseError);
        errorMessage = `Error del servidor (${response.status}): ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }
  } catch (error) {
    console.error("Error guardando orden:", error);
    const mensajeError =
      error?.message ||
      error?.toString() ||
      "Error al guardar la orden de trabajo";
    mostrarMensaje(mensajeError, "danger");
  }
}

// Función de debug para probar la carga de técnicos
window.debugTecnicos = async function () {
  console.log("=== DEBUG: Probando carga de técnicos ===");
  try {
    const response = await fetch("/usuarios/api?per_page=100");
    console.log("Response status:", response.status);
    const data = await response.json();
    console.log("Data completa:", data);
    console.log("Usuarios:", data.usuarios);

    if (data.usuarios) {
      const tecnicosActivos = data.usuarios.filter((u) => u.activo === true);
      console.log("Técnicos activos:", tecnicosActivos);

      const tecnicosValidos = tecnicosActivos.filter((u) =>
        ["Técnico", "Administrador"].includes(u.rol)
      );
      console.log("Técnicos válidos:", tecnicosValidos);
    }
  } catch (error) {
    console.error("Error en debug:", error);
  }
};

// Función de debug para revisar el DOM
window.debugDOM = function () {
  console.log("=== DEBUG: Revisando DOM ===");
  const selectTecnico = document.getElementById("orden-tecnico");
  console.log("Select técnico encontrado:", !!selectTecnico);
  if (selectTecnico) {
    console.log("HTML del select:", selectTecnico.innerHTML);
    console.log("Opciones:", selectTecnico.options.length);
  }
};

// ================================
// GESTIÓN DE ARCHIVOS ADJUNTOS
// ================================

// Variables globales para archivos
let archivosTemporales = [];
let ordenIdActual = null;

// Inicializar funcionalidad de archivos cuando se abre el modal
function inicializarArchivos(ordenId = null) {
  console.log("Inicializando archivos para orden:", ordenId);
  ordenIdActual = ordenId;
  archivosTemporales = [];

  // Configurar eventos de drag & drop
  const uploadArea = document.getElementById("upload-area");
  const fileInput = document.getElementById("file-input");
  const browseFiles = document.getElementById("browse-files");

  if (uploadArea && fileInput && browseFiles) {
    // Limpiar eventos previos para evitar duplicados
    uploadArea.replaceWith(uploadArea.cloneNode(true));
    const newUploadArea = document.getElementById("upload-area");

    // Eventos de drag & drop
    newUploadArea.addEventListener("dragover", handleDragOver);
    newUploadArea.addEventListener("dragleave", handleDragLeave);
    newUploadArea.addEventListener("drop", handleDrop);
    newUploadArea.addEventListener("click", () => fileInput.click());

    // Limpiar eventos del botón browse
    const newBrowseFiles = document.getElementById("browse-files");
    newBrowseFiles.addEventListener("click", (e) => {
      e.preventDefault();
      fileInput.click();
    });

    // Evento cuando se seleccionan archivos
    fileInput.addEventListener("change", handleFileSelect);
  }

  // Limpiar campos de enlace
  const urlInput = document.getElementById("enlace-url");
  const descripcionInput = document.getElementById("enlace-descripcion");
  if (urlInput) {
    urlInput.value = "";
    urlInput.classList.remove("enlace-valido", "enlace-invalido");
  }
  if (descripcionInput) {
    descripcionInput.value = "";
  }

  // Cargar archivos existentes si estamos editando
  if (ordenId) {
    cargarArchivosExistentes(ordenId);
  } else {
    limpiarListaArchivos();
  }
} // Eventos de drag & drop
function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.classList.add("dragover");
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.classList.remove("dragover");
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  e.currentTarget.classList.remove("dragover");

  const files = Array.from(e.dataTransfer.files);
  procesarArchivos(files);
}

// Manejar selección de archivos
function handleFileSelect(e) {
  const files = Array.from(e.target.files);
  procesarArchivos(files);
  e.target.value = ""; // Limpiar input para permitir seleccionar el mismo archivo
}

// Procesar archivos seleccionados
function procesarArchivos(files) {
  files.forEach((file) => {
    if (validarArchivo(file)) {
      const archivoTemporal = {
        id: Date.now() + Math.random(),
        archivo: file,
        nombre: file.name,
        tamaño: file.size,
        tipo: determinarTipoArchivo(file),
        progreso: 0,
        estado: "preparado", // preparado, subiendo, completado, error
      };

      archivosTemporales.push(archivoTemporal);
      añadirArchivoALista(archivoTemporal, true);
    }
  });
}

// Validar archivo
function validarArchivo(file) {
  const tiposPermitidos = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
  ];

  const tamañoMaximo = 10 * 1024 * 1024; // 10MB

  if (!tiposPermitidos.includes(file.type)) {
    mostrarMensaje(`Tipo de archivo no permitido: ${file.name}`, "danger");
    return false;
  }

  if (file.size > tamañoMaximo) {
    mostrarMensaje(`Archivo muy grande: ${file.name} (màx. 10MB)`, "danger");
    return false;
  }

  return true;
}

// Determinar tipo de archivo
function determinarTipoArchivo(file) {
  if (file.type.startsWith("image/")) {
    return "imagen";
  } else if (
    file.type.includes("pdf") ||
    file.type.includes("document") ||
    file.type.includes("sheet") ||
    file.type.includes("text")
  ) {
    return "documento";
  } else {
    return "archivo";
  }
}

// Añadir archivo a la lista visual
function añadirArchivoALista(archivo, esNuevo = false) {
  const listaArchivos = document.getElementById("lista-archivos");
  if (!listaArchivos) return;

  const archivoDiv = document.createElement("div");
  archivoDiv.className = `archivo-item archivo-${archivo.tipo}`;
  archivoDiv.setAttribute("data-archivo-id", archivo.id);

  let icono = "bi-file-earmark";
  if (archivo.tipo === "imagen") {
    icono = "bi-image";
  } else if (archivo.tipo === "documento") {
    icono = "bi-file-text";
  } else if (archivo.tipo === "enlace") {
    icono = "bi-link-45deg";
  }

  archivoDiv.innerHTML = `
        <div class="archivo-info">
            <i class="bi ${icono} archivo-icono"></i>
            <div class="archivo-detalles">
                <h6>${archivo.nombre || archivo.nombre_original}</h6>
                <small>${formatearTamaño(archivo.tamaño || archivo.tamaño)} ${
    archivo.descripcion ? "- " + archivo.descripcion : ""
  }</small >
    ${
      esNuevo && archivo.estado === "preparado"
        ? '<div class="upload-progress"><div class="upload-progress-bar" style="width: 0%"></div></div>'
        : ""
    }
            </div >
        </div >
    <div class="archivo-acciones">
        ${
          !esNuevo && archivo.tipo !== "enlace"
            ? `<button class="btn btn-sm btn-outline-primary" onclick="descargarArchivo(${archivo.id})"><i class="bi bi-download"></i></button>`
            : ""
        }
        ${
          archivo.tipo === "enlace"
            ? `<button class="btn btn-sm btn-outline-info" onclick="abrirEnlace('${archivo.url_enlace}')"><i class="bi bi-box-arrow-up-right"></i></button>`
            : ""
        }
        <button class="btn btn-sm btn-outline-danger" onclick="eliminarArchivo(${
          archivo.id
        }, ${esNuevo})"><i class="bi bi-trash"></i></button>
    </div>
`;

  listaArchivos.appendChild(archivoDiv);
}

// Formatear tamaño de archivo
function formatearTamaño(bytes) {
  if (!bytes) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

// Agregar enlace externo
async function agregarEnlace() {
  const urlInput = document.getElementById("enlace-url");
  const descripcionInput = document.getElementById("enlace-descripcion");

  if (!urlInput || !descripcionInput) {
    console.warn("Elementos de enlace no encontrados");
    return;
  }

  const url = urlInput.value.trim();
  const descripcion = descripcionInput.value.trim();

  // Validación mejorada
  if (!url) {
    mostrarMensaje("Por favor ingresa una URL", "danger");
    urlInput.focus();
    return;
  }

  if (!validarURL(url)) {
    mostrarMensaje("URL no válida. Debe incluir http:// o https://", "danger");
    urlInput.classList.add("enlace-invalido");
    urlInput.focus();
    return;
  }

  // Remover clases de validación previas
  urlInput.classList.remove("enlace-invalido");
  urlInput.classList.add("enlace-valido");

  try {
    if (ordenIdActual) {
      // Si estamos editando una orden existente, guardar inmediatamente
      const response = await fetch(`/ordenes/api/${ordenIdActual}/enlaces`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url,
          descripcion: descripcion,
        }),
      });

      if (response.ok) {
        const resultado = await response.json();
        añadirArchivoALista(resultado.enlace, false);
        mostrarMensaje("Enlace agregado exitosamente", "success");
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || "Error al agregar enlace");
      }
    } else {
      // Si es una orden nueva, agregar a lista temporal
      const enlaceTemp = {
        id: Date.now() + Math.random(),
        nombre: `Enlace: ${url}`,
        url_enlace: url,
        descripcion: descripcion,
        tipo: "enlace",
        tamaño: 0,
      };

      archivosTemporales.push(enlaceTemp);
      añadirArchivoALista(enlaceTemp, true);
      mostrarMensaje("Enlace agregado a la lista", "success");
    }

    // Limpiar campos solo si todo fue exitoso
    urlInput.value = "";
    descripcionInput.value = "";
    urlInput.classList.remove("enlace-valido");
  } catch (error) {
    console.error("Error al agregar enlace:", error);
    mostrarMensaje("Error al agregar enlace: " + error.message, "danger");
    urlInput.classList.add("enlace-invalido");
  }
}

// Validar URL
function validarURL(url) {
  try {
    // Verificar que la URL no esté vacía
    if (!url || url.trim() === "") {
      return false;
    }

    // Si no tiene protocolo, añadir https por defecto
    let urlToValidate = url.trim();
    if (
      !urlToValidate.startsWith("http://") &&
      !urlToValidate.startsWith("https://")
    ) {
      urlToValidate = "https://" + urlToValidate;
    }

    const urlObj = new URL(urlToValidate);

    // Verificar que tenga un dominio válido
    return urlObj.protocol === "http:" || urlObj.protocol === "https:";
  } catch (e) {
    console.warn("URL inválida:", url, e);
    return false;
  }
}

// Eliminar archivo
async function eliminarArchivo(archivoId, esNuevo = false) {
  try {
    if (esNuevo) {
      // Eliminar de lista temporal
      archivosTemporales = archivosTemporales.filter((a) => a.id !== archivoId);
    } else {
      // Eliminar del servidor
      const response = await fetch(`/ordenes/api/archivos/${archivoId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Error al eliminar archivo");
      }

      mostrarMensaje("Archivo eliminado exitosamente", "success");
    }

    // Eliminar del DOM
    const archivoElement = document.querySelector(
      `[data-archivo-id="${archivoId}"]`
    );
    if (archivoElement) {
      archivoElement.remove();
    }
  } catch (error) {
    console.error("Error al eliminar archivo:", error);
    mostrarMensaje("Error al eliminar archivo", "danger");
  }
}

// Descargar archivo
function descargarArchivo(archivoId) {
  window.open(`/ordenes/api/archivos/${archivoId}/download`, "_blank");
}

// Abrir enlace externo
function abrirEnlace(url) {
  window.open(url, "_blank");
}

// Cargar archivos existentes
async function cargarArchivosExistentes(ordenId) {
  try {
    const response = await fetch(`/ordenes/api/${ordenId}/archivos`);
    if (response.ok) {
      const archivos = await response.json();

      limpiarListaArchivos();

      archivos.forEach((archivo) => {
        añadirArchivoALista(archivo, false);
      });
    }
  } catch (error) {
    console.error("Error al cargar archivos:", error);
  }
}

// Limpiar lista de archivos
function limpiarListaArchivos() {
  const listaArchivos = document.getElementById("lista-archivos");
  if (listaArchivos) {
    listaArchivos.innerHTML = "";
  }
}

// Subir archivos pendientes (cuando se guarda la orden)
async function subirArchivosPendientes(ordenId) {
  console.log("Procesando archivos temporales:", archivosTemporales);

  // Procesar archivos
  const archivosPendientes = archivosTemporales.filter(
    (a) => a.archivo && a.estado === "preparado"
  );
  console.log("Archivos a subir:", archivosPendientes.length);

  for (const archivo of archivosPendientes) {
    try {
      archivo.estado = "subiendo";
      await subirArchivo(archivo, ordenId);
      archivo.estado = "completado";
      console.log("Archivo subido exitosamente:", archivo.nombre);
    } catch (error) {
      archivo.estado = "danger";
      console.error("Error al subir archivo:", archivo.nombre, error);
    }
  }

  // Procesar enlaces válidos
  const enlacesPendientes = archivosTemporales.filter(
    (a) =>
      a.tipo === "enlace" &&
      a.url_enlace &&
      a.url_enlace.trim() !== "" &&
      validarURL(a.url_enlace)
  );
  console.log("Enlaces a procesar:", enlacesPendientes.length);

  for (const enlace of enlacesPendientes) {
    try {
      console.log("Procesando enlace:", enlace.url_enlace);
      const response = await fetch(`/ordenes/api/${ordenId}/enlaces`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: enlace.url_enlace,
          descripcion: enlace.descripcion || "",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Error al guardar enlace");
      }

      console.log("Enlace guardado exitosamente:", enlace.url_enlace);
    } catch (error) {
      console.error("Error al guardar enlace:", enlace.url_enlace, error);
    }
  }
}

// Subir archivo individual
async function subirArchivo(archivoTemp, ordenId) {
  const formData = new FormData();
  formData.append("archivo", archivoTemp.archivo);
  formData.append("descripcion", archivoTemp.descripcion || "");

  const response = await fetch(`/ordenes/api/${ordenId}/archivos`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Error al subir archivo");
  }

  return await response.json();
}

// Función para limpiar filtros
function limpiarFiltros() {
  console.log("üßπ Limpiando filtros...");

  // Limpiar campos de filtro
  const filtros = [
    "filtro-buscar",
    "filtro-estado",
    "filtro-tipo",
    "filtro-prioridad",
  ];

  filtros.forEach((filtroId) => {
    const elemento = document.getElementById(filtroId);
    if (elemento) {
      elemento.value = "";
      console.log(`✅ Filtro ${filtroId} limpiado`);
    }
  });

  // Aplicar filtros (mostrarà todas las órdenes sin filtros)
  aplicarFiltros();
  console.log("✅ Filtros limpiados y vista actualizada");
}

// ================================
// GESTIÓN DE RECAMBIOS
// ================================

// Variables globales para recambios
let ordenActualId = null;
let autoCompleteRecambio = null;

// Mostrar modal para agregar recambio
function mostrarModalAgregarRecambio() {
  // Limpiar formulario
  document.getElementById("form-agregar-recambio").reset();
  document.getElementById("recambio-inventario-id").value = "";
  document.getElementById("recambio-stock").value = "";
  document.getElementById("recambio-info").textContent =
    "Selecciona un artículo para ver información de stock";

  // Mostrar modal
  const modalRecambio = new bootstrap.Modal(
    document.getElementById("modalAgregarRecambio")
  );
  modalRecambio.show();
} // Inicializar autocompletado para recambios
function inicializarAutocompletadoRecambio() {
  const input = document.getElementById("recambio-articulo");
  if (!input) {
    console.error("Input recambio-articulo no encontrado");
    return;
  }

  // Verificar que AutoComplete esté disponible
  if (typeof AutoComplete === "undefined") {
    setTimeout(inicializarAutocompletadoRecambio, 500);
    return;
  }

  // Limpiar instancia anterior si existe
  if (autoCompleteRecambio) {
    autoCompleteRecambio.destroy();
  }

  try {
    autoCompleteRecambio = new AutoComplete({
      element: input,
      apiUrl: "/inventario/api/articulos",
      searchKey: "q",
      displayKey: (item) => `${item.codigo} - ${item.descripcion}`,
      valueKey: "id",
      minChars: 2,
      maxResults: 10,
      placeholder: "Buscar artículo por código o descripción...",
      noResultsText: "No se encontraron artículos",
      loadingText: "Buscando...",
      onSelect: (item) => {
        // Completar campos
        document.getElementById(
          "recambio-articulo"
        ).value = `${item.codigo} - ${item.descripcion}`;
        document.getElementById("recambio-inventario-id").value = item.id;
        document.getElementById("recambio-stock").value =
          item.stock_actual || 0;

        // Actualizar info
        const stock = item.stock_actual || 0;
        const stockText =
          stock <= 0
            ? `⚠️ Sin stock disponible`
            : `📦 Stock disponible: ${stock} unidades`;

        document.getElementById("recambio-info").innerHTML = `
                    <strong>${item.codigo}</strong> - ${item.descripcion}<br>
                    <span class="${
                      stock <= 0
                        ? "text-danger"
                        : stock < 5
                        ? "text-warning"
                        : "text-success"
                    }">${stockText}</span>
                `;
      },
      onInput: (value) => {
        // Limpiar selección si el usuario está escribiendo
        if (value.length < 2) {
          document.getElementById("recambio-inventario-id").value = "";
          document.getElementById("recambio-stock").value = "";
          document.getElementById("recambio-info").textContent =
            "Selecciona un artículo para ver información de stock";
        }
      },
    });

    console.log("Autocompletado de recambios inicializado");
  } catch (error) {
    console.error("Error inicializando autocompletado recambios:", error);
  }
} // Guardar recambio
async function guardarRecambio() {
  try {
    const inventarioId = document.getElementById(
      "recambio-inventario-id"
    ).value;
    const cantidad = document.getElementById("recambio-cantidad").value;
    const observaciones = document.getElementById(
      "recambio-observaciones"
    ).value;

    if (!inventarioId) {
      mostrarAlertaRecambio("Debe seleccionar un artículo", "danger");
      return;
    }

    if (!cantidad || cantidad <= 0) {
      mostrarAlertaRecambio("Debe especificar una cantidad válida", "danger");
      return;
    }

    const response = await fetch(`/api/ordenes/${ordenActualId}/recambios`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inventario_id: parseInt(inventarioId),
        cantidad_solicitada: parseInt(cantidad),
        observaciones: observaciones,
      }),
    });

    const result = await response.json();

    if (response.ok) {
      mostrarAlertaRecambio(
        result.message || "Recambio agregado exitosamente",
        "success"
      );

      // Cerrar modal después de 1 segundo
      setTimeout(() => {
        bootstrap.Modal.getInstance(
          document.getElementById("modalAgregarRecambio")
        ).hide();
        cargarRecambiosOrden(ordenActualId); // Recargar lista de recambios
      }, 1000);
    } else {
      mostrarAlertaRecambio("Error: " + result.error, "danger");
    }
  } catch (error) {
    console.error("Error guardando recambio:", error);
    mostrarAlertaRecambio("Error de conexión", "danger");
  }
}

// Cargar recambios de una orden
async function cargarRecambiosOrden(ordenId) {
  try {
    const response = await fetch(`/api/ordenes/${ordenId}/recambios`);
    const result = await response.json();

    if (response.ok) {
      mostrarRecambios(result.recambios || []);
    } else {
      console.error("Error cargando recambios:", result.error);
    }
  } catch (error) {
    console.error("Error de conexión:", error);
  }
}

// Mostrar lista de recambios
function mostrarRecambios(recambios) {
  const sinRecambios = document.getElementById("sin-recambios");
  const tablaRecambios = document.getElementById("recambios-table");
  const tbody = document.getElementById("tbody-recambios");

  if (!recambios || recambios.length === 0) {
    sinRecambios.style.display = "block";
    tablaRecambios.style.display = "none";
    return;
  }

  sinRecambios.style.display = "none";
  tablaRecambios.style.display = "block";

  tbody.innerHTML = "";

  recambios.forEach((recambio) => {
    const row = tbody.insertRow();
    const estado = recambio.descontado
      ? '<span class="badge bg-success">Descontado</span>'
      : '<span class="badge bg-warning">Pendiente</span>';

    const stockClass =
      recambio.articulo?.stock_actual <= 0
        ? "text-danger"
        : recambio.articulo?.stock_actual < 5
        ? "text-warning"
        : "text-success";

    row.innerHTML = `
            <td><code>${recambio.articulo?.codigo || "N/A"}</code></td>
            <td>${recambio.articulo?.descripcion || "N/A"}</td>
            <td>${recambio.cantidad_solicitada}</td>
            <td>
                ${
                  recambio.descontado
                    ? recambio.cantidad_utilizada
                    : `<input type="number" class="form-control form-control-sm" value="${
                        recambio.cantidad_utilizada ||
                        recambio.cantidad_solicitada
                      }" 
                            min="0" max="${
                              recambio.cantidad_solicitada
                            }" onchange="actualizarCantidadRecambio(${
                        recambio.id
                      }, this.value)">`
                }
            </td>
            <td class="${stockClass}">${
      recambio.articulo?.stock_actual || 0
    }</td>
            <td>${estado}</td>
            <td>
                ${
                  !recambio.descontado
                    ? `<button class="btn btn-sm btn-outline-danger" onclick="eliminarRecambio(${recambio.id})">
                        <i class="bi bi-trash"></i>
                    </button>`
                    : '<span class="text-muted">N/A</span>'
                }
            </td>
        `;
  });
}

// Actualizar cantidad utilizada de un recambio
async function actualizarCantidadRecambio(recambioId, cantidadUtilizada) {
  try {
    const response = await fetch(`/api/recambios/${recambioId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        cantidad_utilizada: parseInt(cantidadUtilizada),
      }),
    });

    if (!response.ok) {
      const result = await response.json();
      console.error("Error actualizando cantidad:", result.error);
    }
  } catch (error) {
    console.error("Error de conexión:", error);
  }
}

// Eliminar recambio
async function eliminarRecambio(recambioId) {
  if (!confirm("¿Está seguro de eliminar este recambio?")) {
    return;
  }

  try {
    const response = await fetch(`/api/recambios/${recambioId}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (response.ok) {
      cargarRecambiosOrden(ordenActualId); // Recargar lista
    } else {
      mostrarMensaje("Error: " + result.error, "danger");
    }
  } catch (error) {
    console.error("Error eliminando recambio:", error);
    mostrarMensaje("Error de conexión", "danger");
  }
}

// Descontar recambios del stock
// Descontar recambios del stock (MANUAL)
async function descontarRecambios() {
  if (
    !confirm(
      "¿Confirma descontar todos los recambios pendientes del stock? Esta acción no se puede deshacer."
    )
  ) {
    return;
  }

  try {
    const response = await fetch(
      `/api/ordenes/${ordenActualId}/recambios/descontar`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          usuario_id: "sistema", // Aquí podrías usar el usuario actual
          manual: true,
        }),
      }
    );

    const result = await response.json();

    if (response.ok) {
      let mensaje = result.message;

      if (result.recambios_descontados?.length > 0) {
        mensaje += "\n\nRecambios descontados:";
        result.recambios_descontados.forEach((r) => {
          mensaje += `\n• ${r.articulo}: ${r.cantidad} unidades (Stock: ${r.stock_anterior} → ${r.stock_actual})`;
        });
      }

      if (result.errores?.length > 0) {
        mensaje += "\n\nErrores:";
        result.errores.forEach((e) => {
          mensaje += `\n• ${e.articulo}: ${e.error}`;
        });
      }

      mostrarMensaje(mensaje, "success");
      cargarRecambiosOrden(ordenActualId); // Recargar lista
    } else {
      mostrarMensaje("Error: " + result.error, "danger");
    }
  } catch (error) {
    console.error("Error descontando recambios:", error);
    mostrarMensaje("Error de conexión", "danger");
  }
}

// Mostrar alertas en el modal de recambios
function mostrarAlertaRecambio(mensaje, tipo) {
  const alertContainer = document.getElementById("alert-container-recambio");
  alertContainer.innerHTML = "";

  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${tipo} alert-dismissible fade show mt-3`;
  alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  alertContainer.appendChild(alertDiv);

  // Auto-eliminar después de 3 segundos para alertas de éxito
  if (tipo === "success") {
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.remove();
      }
    }, 3000);
  }
}

// Descontar recambios automáticamente al completar orden
async function descontarRecambiosAutomaticamente(ordenId) {
  try {
    const response = await fetch(
      `/api/ordenes/${ordenId}/recambios/descontar`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          usuario_id: "sistema",
          automatico: true,
        }),
      }
    );

    const result = await response.json();

    if (response.ok && result.recambios_descontados?.length > 0) {
      // Recambios descontados exitosamente
      const cantidad = result.recambios_descontados.length;
      console.log(
        `${cantidad} recambio(s) descontado(s) del stock automáticamente`
      );
    } else if (!response.ok && result.error) {
      // Solo mostrar error si hay problema real
      console.warn("Advertencia al descontar recambios:", result.error);
    }
  } catch (error) {
    console.error("Error descontando recambios automáticamente:", error);
    // No mostrar error al usuario para no interrumpir flujo de completar orden
  }
}
