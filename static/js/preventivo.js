// Variables y funciones específicas de Planes
let planesData = [];
let paginacionPlanes;
let filtrosPlanes = {}; // Almacenar filtros globalmente
// Sistema de selección masiva

// Función debounce para optimizar búsquedas
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

// Inicializar cuando se carga la página
document.addEventListener("DOMContentLoaded", function () {
  console.log("ï£¿ðŸ”§ Módulo de mantenimiento preventivo cargado");

  // Configurar paginación
  paginacionPlanes = createPagination("paginacion-planes", cargarPlanes, {
    perPage: 10,
    showInfo: true,
    showSizeSelector: true,
    pageSizes: [10, 25, 50, 100],
  });

  // Configurar búsqueda y filtros
  configurarFiltrosPreventivo();

  // Configurar búsqueda en tiempo real
  configurarBusquedaPreventivo();

  // Configurar autocompletado (deshabilitado)
  // setTimeout(() => {
  //   inicializarAutocompletadoPreventivo();
  // }, 500);

  // Cargar datos iniciales
  cargarPlanes(1);

  // Cargar estadísticas
  cargarEstadisticasPlanes();

  // Agregar funciones adicionales del segundo DOMContentLoaded
  if (typeof cargarActivos === "function") {
    cargarActivos(); // Cargar activos para el select
  }

  // Configurar búsqueda adicional
  if (typeof setupPlanesSearch === "function") {
    setupPlanesSearch();
  }

  // Agregar event listeners para las funciones de frecuencia
  const tipoFrecuenciaSelect = document.getElementById("tipo_frecuencia");
  if (tipoFrecuenciaSelect && typeof cambiarTipoFrecuencia === "function") {
    tipoFrecuenciaSelect.addEventListener("change", cambiarTipoFrecuencia);
  }

  const tipoMensualSelect = document.getElementById("tipo_mensual");
  if (tipoMensualSelect && typeof cambiarTipoMensual === "function") {
    tipoMensualSelect.addEventListener("change", cambiarTipoMensual);
  }

  // Event listeners para actualizar vista previa cuando cambien los valores
  const inputsParaPreview = [
    "fecha_inicio",
    "intervalo_dias",
    "intervalo_semanas",
    "intervalo_meses",
    "dia_mes",
    "semana_mes",
    "dia_semana_mes",
    "fechas_especificas",
  ];

  inputsParaPreview.forEach((id) => {
    const element = document.getElementById(id);
    if (element && typeof previsualizarFechas === "function") {
      element.addEventListener("change", previsualizarFechas);
      element.addEventListener("input", previsualizarFechas);
    }
  });

  // Event listener para checkboxes de días de la semana
  document.addEventListener("change", function (e) {
    if (
      e.target.name === "dias_semana" &&
      typeof previsualizarFechas === "function"
    ) {
      previsualizarFechas();
    }
  });
});

// Configurar filtros de mantenimiento preventivo
function configurarFiltrosPreventivo() {
  console.log("ï£¿ðŸ” Configurando filtros de mantenimiento preventivo...");

  // Selectores de filtro
  const filtros = ["filtro-estado", "filtro-frecuencia", "filtro-vencimiento"];
  filtros.forEach((filtroId) => {
    const elemento = document.getElementById(filtroId);
    if (elemento) {
      elemento.addEventListener("change", aplicarFiltrosPreventivo);
      console.log(`✅ Filtro ${filtroId} configurado`);
    }
  });
}

// Configurar búsqueda en tiempo real con debounce
function configurarBusquedaPreventivo() {
  console.log("ðŸ” Configurando búsqueda en tiempo real para preventivo...");

  const campoBusqueda = document.getElementById("filtro-buscar");

  if (campoBusqueda) {
    // Crear función debounced para la búsqueda
    const busquedaDebounced = debounce(() => {
      console.log("ðŸ”Ž Ejecutando búsqueda...");
      filtrarPlanes();
    }, 500);

    // Agregar event listener con debounce
    campoBusqueda.addEventListener("input", busquedaDebounced);
    console.log("✅ Búsqueda en tiempo real configurada");
  } else {
    console.warn("—š  Campo filtro-buscar no encontrado");
  }
}

// Filtrar planes con búsqueda del lado del servidor
function filtrarPlanes() {
  console.log("ðŸ” filtrarPlanes() ejecutado");
  const filtros = {};

  // Filtro de búsqueda
  const buscar = document.getElementById("filtro-buscar");
  if (buscar && buscar.value.trim()) {
    filtros.q = buscar.value.trim();
    console.log("ðŸ“ Filtro de búsqueda:", filtros.q);
  }

  // Filtros de selección
  const estado = document.getElementById("filtro-estado");
  if (estado && estado.value) {
    filtros.estado = estado.value;
    console.log("📊 Filtro de estado:", filtros.estado);
  }

  const frecuencia = document.getElementById("filtro-frecuencia");
  if (frecuencia && frecuencia.value) {
    filtros.frecuencia = frecuencia.value;
    console.log("ðŸ”§ Filtro de frecuencia:", filtros.frecuencia);
  }

  const vencimiento = document.getElementById("filtro-vencimiento");
  if (vencimiento && vencimiento.value) {
    filtros.vencimiento = vencimiento.value;
    console.log("—š¡ Filtro de vencimiento:", filtros.vencimiento);
  }

  // Guardar filtros globalmente
  filtrosPlanes = filtros;
  console.log("ðŸ’¾ Filtros guardados:", filtros);

  // Reiniciar a la primera página y cargar con filtros
  console.log("ð📄 Cargando planes con filtros...");
  cargarPlanes(1, null, filtros);
}

// Limpiar filtros
function limpiarFiltros() {
  document.getElementById("filtro-buscar").value = "";
  document.getElementById("filtro-estado").value = "";
  document.getElementById("filtro-frecuencia").value = "";
  document.getElementById("filtro-vencimiento").value = "";

  // Recargar datos sin filtros
  filtrosPlanes = {};
  cargarPlanes(1);
}

// Alias para compatibilidad con el botón HTML
function aplicarFiltros() {
  filtrarPlanes();
}

// Función para mostrar/ocultar estado de carga en la tabla de planes
function mostrarCargandoPlanes(mostrar = true) {
  const tbody = document.getElementById("planesTableBody");
  if (!tbody) return;

  if (mostrar) {
    // Solo mostrar loading si no hay ya un loading-row
    if (!tbody.querySelector("#loading-row-planes")) {
      tbody.innerHTML = `
                <tr id="loading-row-planes">
                    <td colspan="9" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="mt-2 text-muted">Cargando planes de mantenimiento...</p>
                    </td>
                </tr>
            `;
    }
  } else {
    // Ocultar loading: eliminar solo la fila de loading si existe
    const loadingRow = tbody.querySelector("#loading-row-planes");
    if (loadingRow) {
      loadingRow.remove();
    }
  }
}

// Aplicar filtros a la lista de planes
function aplicarFiltrosPreventivo() {
  console.log("ï£¿ðŸ” Aplicando filtros de preventivo...");
  // Construir objeto de filtros
  const filtros = {};

  // Filtros adicionales
  const filtroEstado = document.getElementById("filtro-estado");
  if (filtroEstado && filtroEstado.value) {
    filtros.estado = filtroEstado.value;
  }

  const filtroFrecuencia = document.getElementById("filtro-frecuencia");
  if (filtroFrecuencia && filtroFrecuencia.value) {
    filtros.frecuencia = filtroFrecuencia.value;
  }

  const filtroVencimiento = document.getElementById("filtro-vencimiento");
  if (filtroVencimiento && filtroVencimiento.value) {
    filtros.vencimiento = filtroVencimiento.value;
  }

  console.log("ï£¿ðŸ” Filtros aplicados:", filtros);
  cargarPlanes(1); // Recargar con filtros aplicados
}

// Inicializar autocompletado
function inicializarAutocompletadoPreventivo() {
  console.log("ï£¿ðŸ” Inicializando autocompletado en preventivo...");

  if (!window.AutoComplete) {
    console.log("—Œ AutoComplete no disponible");
    return;
  }

  const campoBuscar = document.getElementById("search-planes");
  if (campoBuscar) {
    new AutoComplete({
      element: campoBuscar,
      apiUrl: "/planes/api",
      searchKey: "q",
      displayKey: (item) => `${item.codigo} - ${item.nombre} (${item.equipo})`,
      valueKey: "codigo",
      placeholder: "Buscar por código, nombre o equipo...",
      allowFreeText: true,
      customFilter: (item, query) => {
        if (!query || typeof query !== "string") return false;
        const q = query.toLowerCase();
        return (
          (item.codigo && item.codigo.toLowerCase().includes(q)) ||
          (item.nombre && item.nombre.toLowerCase().includes(q)) ||
          (item.equipo && item.equipo.toLowerCase().includes(q))
        );
      },
      onSelect: (item) => {
        console.log("ï£¿ðŸ”§ Plan seleccionado:", item);
        aplicarFiltrosPreventivo();
      },
    });
    console.log("✅ Autocompletado de preventivo configurado");
  }
}

// Función para limpiar filtros de preventivo
function limpiarFiltrosPreventivo() {
  console.log("🔧 Limpiando filtros de preventivo...");

  // Limpiar campos de filtro
  const filtros = [
    "search-planes",
    "filtro-estado",
    "filtro-frecuencia",
    "filtro-vencimiento",
  ];

  filtros.forEach((filtroId) => {
    const elemento = document.getElementById(filtroId);
    if (elemento) {
      elemento.value = "";
      console.log(`✅ Filtro ${filtroId} limpiado`);
    }
  });

  // Aplicar filtros (mostraráá todos los planes sin filtros)
  aplicarFiltrosPreventivo();
  console.log("✅ Filtros limpiados y vista actualizada");
}

function cargarPlanes(page = 1, per_page = null, filtros = null) {
  if (per_page) {
    paginacionPlanes.setPerPage(per_page);
  }

  // Mostrar indicador de carga
  mostrarCargandoPlanes(true);

  const params = new URLSearchParams({
    page: page,
    per_page: paginacionPlanes.perPage,
  });

  // Usar filtros pasados como parámetro o filtros globales
  const filtrosActuales = filtros || filtrosPlanes || {};

  // Agregar filtros de búsqueda desde el objeto de filtros
  if (filtrosActuales.q) {
    params.append("q", filtrosActuales.q);
  }

  if (filtrosActuales.estado) {
    params.append("estado", filtrosActuales.estado);
  }

  if (filtrosActuales.frecuencia) {
    params.append("frecuencia", filtrosActuales.frecuencia);
  }

  if (filtrosActuales.vencimiento) {
    params.append("vencimiento", filtrosActuales.vencimiento);
  }

  console.log("📡 Petición a /planes/api con params:", params.toString());

  fetch(`/planes/api?${params}`)
    .then((response) => response.json())
    .then((data) => {
      planesData = data.items || data;
      renderPlanes(data.items || data);

      // Renderizar paginación si hay datos paginados
      if (data.page && data.per_page && data.total) {
        paginacionPlanes.render(data.page, data.per_page, data.total);
      }

      // Ocultar indicador de carga
      mostrarCargandoPlanes(false);
    })
    .catch((error) => {
      console.error("Error cargando planes:", error);
      showNotificationToast("Error al cargar planes de mantenimiento", "error");
      // Ocultar indicador de carga en caso de error
      mostrarCargandoPlanes(false);
    });
}

// Función legacy para compatibilidad
function loadPlanes() {
  cargarPlanes(1);
}
function renderPlanes(planes) {
  const tbody = document.getElementById("planesTableBody");
  if (!tbody) {
    console.error("Table body not found");
    return;
  }

  tbody.innerHTML = "";

  if (!planes || planes.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="bi bi-calendar-check fs-1 d-block mb-2"></i>
                    No se encontraron planes de mantenimiento
                </td>
            </tr>
        `;
    return;
  }

  planes.forEach((plan) => {
    tbody.innerHTML += `
            <tr>
                <td>${plan.codigo}</td>
                <td>${plan.nombre}</td>
                <td>${plan.equipo}</td>
                <td>${plan.frecuencia}</td>
                <td>${plan.ultima_ejecucion || "N/A"}</td>
                <td>${plan.proxima_ejecucion || "N/A"}</td>
                <td>${getEstadoPlanBadge(plan.estado)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-sm btn-outline-primary action-btn view" title="Ver detalles" onclick="viewPlan(${
                          plan.id
                        })">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger action-btn delete" title="Eliminar" onclick="deletePlan(${
                          plan.id
                        }, '${plan.codigo}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
  });
}
function guardarPlan() {
  const form = document.getElementById("formPlan");
  const editingId = form.dataset.editingId;
  const isEditing = !!editingId;

  // Recopilar datos básicos del formulario
  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  // Agregar datos específicos de frecuencia
  const tipoFrecuencia = document.getElementById("tipo_frecuencia").value;
  data.tipo_frecuencia = tipoFrecuencia;

  // Agregar campo de generación automática
  const generacionAutomatica = document.getElementById("generacion_automatica");
  data.generacion_automatica = generacionAutomatica
    ? generacionAutomatica.checked
    : true;

  // Mapear tipo_frecuencia a frecuencia para el backend
  const mapeoFrecuencia = {
    diario: "Diario",
    semanal: "Semanal",
    mensual: "Mensual",
    personalizado: "Personalizado",
  };
  data.frecuencia = mapeoFrecuencia[tipoFrecuencia] || "Personalizado";

  // Datos específicos según el tipo de frecuencia
  if (tipoFrecuencia === "diaria") {
    const intervaloDias = document.getElementById("intervalo_dias").value;
    data.intervalo_dias = intervaloDias ? parseInt(intervaloDias) : 1; // Valor por defecto: 1
  } else if (tipoFrecuencia === "semanal") {
    const intervaloSemanas = document.getElementById("intervalo_semanas").value;
    data.intervalo_semanas = intervaloSemanas ? parseInt(intervaloSemanas) : 1; // Valor por defecto: 1

    // Recopilar días de la semana seleccionados
    const diasSeleccionados = [];
    document
      .querySelectorAll('input[name="dias_semana"]:checked')
      .forEach((cb) => {
        diasSeleccionados.push(cb.value);
      });
    data.dias_semana = diasSeleccionados;
  } else if (tipoFrecuencia === "mensual") {
    const intervaloMeses = document.getElementById("intervalo_meses").value;
    data.intervalo_meses = intervaloMeses ? parseInt(intervaloMeses) : 1; // Valor por defecto: 1
    data.tipo_mensual = document.getElementById("tipo_mensual").value;

    if (data.tipo_mensual === "dia_mes") {
      const diaMes = document.getElementById("dia_mes").value;
      data.dia_mes = diaMes ? parseInt(diaMes) : 1; // Valor por defecto: 1
      // Limpiar campos no utilizados
      data.semana_mes = null;
      data.dia_semana_mes = null;
    } else if (data.tipo_mensual === "dia_semana_mes") {
      const semanaMes = document.getElementById("semana_mes").value;
      data.semana_mes = semanaMes ? parseInt(semanaMes) : 1; // Valor por defecto: 1
      data.dia_semana_mes = document.getElementById("dia_semana_mes").value;
      // Limpiar campo no utilizado
      data.dia_mes = null;
    }
  } else if (tipoFrecuencia === "personalizada") {
    data.patron_personalizado = document.getElementById(
      "patron_personalizado"
    ).value;
    data.fechas_especificas =
      document.getElementById("fechas_especificas").value;
  }

  // Calcular próximas fechas para enviar al backend
  try {
    const proximasFechas = calcularProximasFechas();
    data.proximas_fechas = proximasFechas
      .slice(0, 10)
      .map((fecha) => fecha.toISOString().split("T")[0]);
  } catch (error) {
    console.error("Error al calcular fechas:", error);
    data.proximas_fechas = [];
  }

  // Validar datos antes de enviar
  if (!data.nombre || !data.activo_id) {
    showNotificationToast(
      "Por favor complete todos los campos obligatorios (nombre y activo)",
      "warning"
    );
    return;
  }

  // Convertir activo_id a entero
  if (data.activo_id) {
    data.activo_id = parseInt(data.activo_id);
  }

  // Convertir tiempo_estimado a float si existe
  if (data.tiempo_estimado) {
    data.tiempo_estimado = parseFloat(data.tiempo_estimado);
  }

  // El código se genera automáticamente si no se proporciona
  if (!data.codigo || data.codigo.trim() === "") {
    // El backend generará el código automáticamente
    delete data.codigo;
  }

  if (!tipoFrecuencia) {
    showNotificationToast(
      "Por favor seleccione un tipo de frecuencia",
      "warning"
    );
    return;
  }

  // Validaciones específicas por tipo de frecuencia
  if (tipoFrecuencia === "semanal" && data.dias_semana.length === 0) {
    showNotificationToast(
      "Por favor seleccione al menos un día de la semana",
      "warning"
    );
    return;
  }

  console.log("Datos a enviar:", data); // Debug
  console.log(
    "Modo:",
    isEditing ? "Edición" : "Creación",
    isEditing ? `(ID: ${editingId})` : ""
  ); // Debug

  // Configurar URL y método según el modo
  const url = isEditing ? `/planes/api/${editingId}` : "/planes/api";
  const method = isEditing ? "PUT" : "POST";

  fetch(url, {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      console.log("Response status:", response.status);
      if (!response.ok) {
        // Si es error del servidor, intentar leer el mensaje de error
        return response
          .json()
          .catch(() => {
            throw new Error(`HTTP error! status: ${response.status}`);
          })
          .then((errorData) => {
            throw new Error(
              errorData.error || `HTTP error! status: ${response.status}`
            );
          });
      }
      return response.json();
    })
    .then((result) => {
      console.log("Resultado:", result);
      if (result.success) {
        const mensaje = isEditing
          ? "Plan de mantenimiento editado exitosamente"
          : "Plan de mantenimiento creado exitosamente";
        showNotificationToast(mensaje, "success");
        bootstrap.Modal.getInstance(
          document.getElementById("planModal")
        ).hide();
        cargarPlanes(1); // Recargar datos con paginación
      } else {
        showNotificationToast(
          result.message || result.error || "Error al guardar el plan",
          "error"
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotificationToast("Error al comunicarse con el servidor", "error");
    });
}

// Función de búsqueda con debounce (LEGACY - reemplazada por configurarFiltrosPreventivo)
// function setupPlanesSearch() {
//     const searchInput = document.getElementById('search-planes');
//     if (!searchInput) return;

//     let debounceTimer;
//     searchInput.addEventListener('input', function () {
//         clearTimeout(debounceTimer);
//         debounceTimer = setTimeout(() => {
//             cargarPlanes(1);
//         }, 300);
//     });
// }

// Función para cargar activos en el select
function cargarActivos() {
  const selectActivo = document.getElementById("activo_id");
  if (!selectActivo) {
    console.log("Select activo_id no encontrado");
    return;
  }

  console.log("Cargando activos...");
  fetch("/ordenes/activos")
    .then((response) => {
      console.log("Response status:", response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((activos) => {
      console.log("Activos recibidos:", activos);

      // Limpiar opciones existentes excepto la primera
      selectActivo.innerHTML =
        '<option value="">Seleccionar activo...</option>';

      // Agregar opciones de activos
      if (Array.isArray(activos) && activos.length > 0) {
        activos.forEach((activo) => {
          const option = document.createElement("option");
          option.value = activo.id;
          option.textContent =
            activo.display || `${activo.codigo} - ${activo.nombre}`;
          selectActivo.appendChild(option);
        });
        console.log(`Se cargaron ${activos.length} activos`);
      } else {
        console.log("No se encontraron activos o el formato es incorrecto");
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No hay activos disponibles";
        option.disabled = true;
        selectActivo.appendChild(option);
      }
    })
    .catch((error) => {
      console.error("Error cargando activos:", error);
      showNotificationToast("Error al cargar la lista de activos", "error");

      // Agregar opción de error
      selectActivo.innerHTML =
        '<option value="">Error al cargar activos</option>';
    });
}

// Utilidad para mostrar badge de estado
function getEstadoPlanBadge(estado) {
  if (estado === "Activo")
    return '<span class="badge bg-success">Activo</span>';
  if (estado === "Vencido")
    return '<span class="badge bg-danger">Vencido</span>';
  if (estado === "Próximo")
    return '<span class="badge bg-warning">Próximo</span>';
  return '<span class="badge bg-secondary">Desconocido</span>';
}

function getPrioridadBadge(prioridad) {
  if (prioridad === "Alta") return '<span class="badge bg-danger">Alta</span>';
  if (prioridad === "Media")
    return '<span class="badge bg-warning">Media</span>';
  if (prioridad === "Baja") return '<span class="badge bg-success">Baja</span>';
  return '<span class="badge bg-secondary">Desconocida</span>';
}

function formatearFecha(fechaStr) {
  if (!fechaStr) return "N/A";
  try {
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (error) {
    return fechaStr;
  }
}
// Funciones para manejo de frecuencias de mantenimiento preventivo
function cambiarTipoFrecuencia() {
  const tipoElement = document.getElementById("tipo_frecuencia");
  if (!tipoElement) return;

  const tipo = tipoElement.value;

  // Ocultar todías las secciones de configuración
  const secciones = [
    "config-diaria",
    "config-semanal",
    "config-mensual",
    "config-personalizada",
  ];
  secciones.forEach((id) => {
    const elemento = document.getElementById(id);
    if (elemento) elemento.style.display = "none";
  });

  // Mostrar la sección correspondiente
  const seccionActiva = document.getElementById(
    `config-${
      tipo === "personalizada"
        ? "personalizada"
        : tipo === "diaria"
        ? "diaria"
        : tipo === "semanal"
        ? "semanal"
        : tipo === "mensual"
        ? "mensual"
        : ""
    }`
  );
  if (seccionActiva) {
    seccionActiva.style.display = "block";
  }

  // Actualizar vista previa
  previsualizarFechas();
}

function cambiarTipoMensual() {
  const tipo = document.getElementById("tipo_mensual");
  if (!tipo) return; // Salir si el elemento no existe

  const tipoValue = tipo.value;

  // Ocultar todías las opciones mensuales
  const diaEspecificoMes = document.getElementById("dia-especifico-mes");
  const diaSemanaMs = document.getElementById("dia-semana-mes");

  if (diaEspecificoMes) diaEspecificoMes.style.display = "none";
  if (diaSemanaMs) diaSemanaMs.style.display = "none";

  // Mostrar la opción correspondiente
  if (tipoValue === "dia_mes" && diaEspecificoMes) {
    diaEspecificoMes.style.display = "block";
  } else if (tipoValue === "dia_semana_mes" && diaSemanaMs) {
    diaSemanaMs.style.display = "block";
  }

  // Actualizar vista previa
  previsualizarFechas();
}

function previsualizarFechas() {
  const previewContainer = document.getElementById("preview-fechas");
  const tipoElement = document.getElementById("tipo_frecuencia");

  if (!previewContainer) return;

  if (!tipoElement || !tipoElement.value) {
    previewContainer.innerHTML =
      '<p class="text-muted">Seleccione un tipo de frecuencia para ver la vista previa.</p>';
    return;
  }

  try {
    const fechas = calcularProximasFechas();

    if (fechas.length === 0) {
      previewContainer.innerHTML =
        '<p class="text-warning">No se pueden calcular fechas con la configuración actual.</p>';
      return;
    }

    let html = '<ul class="list-unstyled">';
    fechas.slice(0, 5).forEach((fecha, index) => {
      const fechaFormateada = fecha.toLocaleDateString("es-ES", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      html += `<li><i class="fas fa-calendar me-2"></i>${fechaFormateada}</li>`;
    });
    html += "</ul>";

    if (fechas.length > 5) {
      html += `<small class="text-muted">Y ${
        fechas.length - 5
      } fechas más...</small>`;
    }

    previewContainer.innerHTML = html;
  } catch (error) {
    console.error("Error al calcular fechas:", error);
    previewContainer.innerHTML =
      '<p class="text-danger">Error al calcular las fechas. Verifique la configuración.</p>';
  }
}

function calcularProximasFechas() {
  const tipoElement = document.getElementById("tipo_frecuencia");
  if (!tipoElement) return [];

  const tipo = tipoElement.value;

  // Usar fecha actual si no hay campo fecha_inicio
  const fechaInicioElement = document.getElementById("fecha_inicio");
  const fechaInicio = fechaInicioElement
    ? new Date(fechaInicioElement.value || new Date())
    : new Date();

  const fechas = [];

  switch (tipo) {
    case "diario":
      return calcularFechasDiarias(fechaInicio);
    case "semanal":
      return calcularFechasSemanales(fechaInicio);
    case "mensual":
      return calcularFechasMensuales(fechaInicio);
    case "personalizado":
      return calcularFechasPersonalizadas(fechaInicio);
    default:
      return [];
  }
}

function calcularFechasDiarias(fechaInicio) {
  const intervaloElement = document.getElementById("intervalo_dias");
  const intervalo = intervaloElement
    ? parseInt(intervaloElement.value) || 1
    : 1;
  const fechas = [];
  let fecha = new Date(fechaInicio);

  for (let i = 0; i < 10; i++) {
    fechas.push(new Date(fecha));
    fecha.setDate(fecha.getDate() + intervalo);
  }

  return fechas;
}

function calcularFechasSemanales(fechaInicio) {
  const intervaloElement = document.getElementById("intervalo_semanas");
  const intervalo = intervaloElement
    ? parseInt(intervaloElement.value) || 1
    : 1;
  const diasSeleccionados = [];

  // Recopilar días seleccionados (0 = domingo, 1 = lunes, etc.)
  const checkboxes = document.querySelectorAll(
    'input[name="dias_semana"]:checked'
  );
  checkboxes.forEach((cb) => {
    diasSeleccionados.push(parseInt(cb.value));
  });

  if (diasSeleccionados.length === 0) return [];

  const fechas = [];
  let fechaActual = new Date(fechaInicio);
  let semanasContadas = 0;

  // Encontrar el primer día seleccionado a partir de fechaInicio
  while (fechas.length < 10 && semanasContadas < 52) {
    // Máximo 52 semanas
    const diaSemana = fechaActual.getDay();

    if (diasSeleccionados.includes(diaSemana)) {
      // Verificar si esta semana debe incluirse según el intervalo
      const semanaDesdeInicio = Math.floor(
        (fechaActual - fechaInicio) / (7 * 24 * 60 * 60 * 1000)
      );
      if (semanaDesdeInicio % intervalo === 0) {
        fechas.push(new Date(fechaActual));
      }
    }

    // Avanzar al siguiente día
    fechaActual.setDate(fechaActual.getDate() + 1);
    semanasContadas++;
  }

  return fechas;
}

function calcularFechasMensuales(fechaInicio) {
  const tipoMensualElement = document.getElementById("tipo_mensual");
  const intervalMesesElement = document.getElementById("intervalo_meses");

  if (!tipoMensualElement) return [];

  const tipoMensual = tipoMensualElement.value;
  const intervalMeses = intervalMesesElement
    ? parseInt(intervalMesesElement.value) || 1
    : 1;
  const fechas = [];

  if (tipoMensual === "dia_mes") {
    const diaMesElement = document.getElementById("dia_mes");
    const diaMes = diaMesElement ? parseInt(diaMesElement.value) || 1 : 1;

    // Calcular la primera fecha válida a partir de fechaInicio
    let fecha = new Date(fechaInicio);
    fecha.setDate(diaMes);

    // Si la fecha calculada es anterior a fechaInicio, avanzar al próximo mes
    if (fecha < fechaInicio) {
      fecha.setMonth(fecha.getMonth() + 1);
      fecha.setDate(diaMes);
    }

    for (let i = 0; i < 12; i++) {
      // Ajustar si el día no existe en este mes (ej: 31 de febrero -> 28/29 de febrero)
      const ultimoDiaMes = new Date(
        fecha.getFullYear(),
        fecha.getMonth() + 1,
        0
      ).getDate();
      if (diaMes > ultimoDiaMes) {
        fecha.setDate(ultimoDiaMes);
      }

      fechas.push(new Date(fecha));
      fecha.setMonth(fecha.getMonth() + intervalMeses);
      fecha.setDate(diaMes);
    }
  } else if (tipoMensual === "dia_semana_mes") {
    const semanaMesElement = document.getElementById("semana_mes");
    const diaSemanaElement = document.getElementById("dia_semana_mes");

    const semanaDelMes = semanaMesElement
      ? parseInt(semanaMesElement.value) || 1
      : 1;
    const diaSemana = diaSemanaElement
      ? parseInt(diaSemanaElement.value) || 1
      : 1;

    let fecha = new Date(fechaInicio);
    fecha.setDate(1); // Primer día del mes

    for (let i = 0; i < 12; i++) {
      const fechaCalculada = calcularDiaSemanaDelMes(
        fecha.getFullYear(),
        fecha.getMonth(),
        semanaDelMes,
        diaSemana
      );
      if (fechaCalculada && fechaCalculada >= fechaInicio) {
        fechas.push(fechaCalculada);
      }
      fecha.setMonth(fecha.getMonth() + intervalMeses);
    }
  }

  return fechas;
}

function calcularDiaSemanaDelMes(año, mes, semana, diaSemana) {
  // semana: 1-4 (primera, segunda, tercera, cuarta semana)
  // diaSemana: 0-6 (domingo=0, lunes=1, etc.)

  const primerDia = new Date(año, mes, 1);
  const primerDiaSemana = primerDia.getDay();

  // Calcular el primer día de la semana especificada en el mes
  let diasHastaPrimerOcurrencia = (diaSemana - primerDiaSemana + 7) % 7;
  if (diasHastaPrimerOcurrencia === 0 && primerDiaSemana !== diaSemana) {
    diasHastaPrimerOcurrencia = 7;
  }

  const diaObjetivo = 1 + diasHastaPrimerOcurrencia + (semana - 1) * 7;

  // Verificar que el día existe en el mes
  const ultimoDiaDelMes = new Date(año, mes + 1, 0).getDate();
  if (diaObjetivo > ultimoDiaDelMes) {
    return null; // El día no existe en este mes
  }

  return new Date(año, mes, diaObjetivo);
}

function calcularFechasPersonalizadas(fechaInicio) {
  const fechasEspecificasElement =
    document.getElementById("fechas_especificas");
  const fechas = [];

  if (fechasEspecificasElement && fechasEspecificasElement.value) {
    const lineas = fechasEspecificasElement.value.split("\n");
    lineas.forEach((linea) => {
      linea = linea.trim();
      if (linea) {
        try {
          const fecha = new Date(linea);
          if (!isNaN(fecha.getTime()) && fecha >= fechaInicio) {
            fechas.push(fecha);
          }
        } catch (error) {
          console.warn("Fecha inválida:", linea);
        }
      }
    });
  }

  // Ordenar fechas
  fechas.sort((a, b) => a - b);

  return fechas;
}

// Función para resetear el formulario de mantenimiento preventivo
function resetearFormularioPreventivo() {
  document.getElementById("formPlan").reset();

  // Ocultar todías las secciones de configuración
  document.getElementById("config-diaria").style.display = "none";
  document.getElementById("config-semanal").style.display = "none";
  document.getElementById("config-mensual").style.display = "none";
  document.getElementById("config-personalizada").style.display = "none";

  // Limpiar vista previa
  document.getElementById("preview-fechas").innerHTML =
    '<p class="text-muted">Seleccione un tipo de frecuencia para ver la vista previa.</p>';
}

// Función para abrir el modal con reseteo
function openPlanModal() {
  // Limpiar formulario y remover datos de edición
  resetearFormularioPreventivo();
  delete document.getElementById("formPlan").dataset.editingId;

  // Configurar modal para creación
  document.getElementById("modalTitle").textContent =
    "Nuevo Plan de Mantenimiento";

  new bootstrap.Modal(document.getElementById("planModal")).show();
}

// Funciones para manejar acciones de planes
function viewPlan(planId) {
  console.log("Ver detalles del plan:", planId);

  // Obtener datos completos del plan desde el servidor
  fetch(`/planes/api/${planId}`)
    .then((response) => response.json())
    .then((result) => {
      if (result.success && result.plan) {
        const plan = result.plan;

        // Crear modal de detalles dinámico
        const modalHtml = `
                    <div class="modal fade" id="viewPlanModal" tabindex="-1" aria-labelledby="viewPlanModalLabel" aria-hidden="true">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header bg-info text-white">
                                    <h5 class="modal-title" id="viewPlanModalLabel">
                                        <i class="bi bi-eye me-2"></i>Detalles del Plan de Mantenimiento
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="card h-100">
                                                <div class="card-header bg-light">
                                                    <h6 class="mb-0"><i class="bi bi-info-circle me-1"></i>Información General</h6>
                                                </div>
                                                <div class="card-body">
                                                    <table class="table table-sm table-borderless">
                                                        <tr>
                                                            <td><strong>Código:</strong></td>
                                                            <td>${
                                                              plan.codigo_plan
                                                            }</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Nombre:</strong></td>
                                                            <td>${
                                                              plan.nombre
                                                            }</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Descripción:</strong></td>
                                                            <td>${
                                                              plan.descripcion ||
                                                              "N/A"
                                                            }</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Estado:</strong></td>
                                                            <td>${getEstadoPlanBadge(
                                                              plan.estado
                                                            )}</td>
                                                        </tr>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="card h-100">
                                                <div class="card-header bg-light">
                                                    <h6 class="mb-0"><i class="bi bi-gear me-1"></i>Detalles Técnicos</h6>
                                                </div>
                                                <div class="card-body">
                                                    <table class="table table-sm table-borderless">
                                                        <tr>
                                                            <td><strong>Activo/Equipo:</strong></td>
                                                            <td>${
                                                              plan.activo_nombre ||
                                                              "N/A"
                                                            }</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Tiempo Estimado:</strong></td>
                                                            <td>${
                                                              plan.tiempo_estimado
                                                                ? plan.tiempo_estimado +
                                                                  " horas"
                                                                : "N/A"
                                                            }</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Frecuencia:</strong></td>
                                                            <td><span class="badge bg-primary">${
                                                              plan.frecuencia
                                                            }</span></td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Días de Frecuencia:</strong></td>
                                                            <td>${
                                                              plan.frecuencia_dias
                                                                ? plan.frecuencia_dias +
                                                                  " días"
                                                                : "N/A"
                                                            }</td>
                                                        </tr>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row mt-3">
                                        <div class="col-12">
                                            <div class="card">
                                                <div class="card-header bg-light">
                                                    <h6 class="mb-0"><i class="bi bi-calendar me-1"></i>Programación</h6>
                                                </div>
                                                <div class="card-body">
                                                    <div class="row">
                                                        <div class="col-md-6">
                                                            <strong>Última Ejecución:</strong><br>
                                                            <span class="text-muted">${
                                                              plan.ultima_ejecucion
                                                                ? formatearFecha(
                                                                    plan.ultima_ejecucion
                                                                  )
                                                                : "Nunca ejecutado"
                                                            }</span>
                                                        </div>
                                                        <div class="col-md-6">
                                                            <strong>Próxima Ejecución:</strong><br>
                                                            <span class="text-muted">${
                                                              plan.proxima_ejecucion
                                                                ? formatearFecha(
                                                                    plan.proxima_ejecucion
                                                                  )
                                                                : "No programado"
                                                            }</span>
                                                        </div>
                                                    </div>
                                                    ${
                                                      plan.instrucciones
                                                        ? `
                                                    <div class="mt-3">
                                                        <strong>Instrucciones:</strong><br>
                                                        <div class="border rounded p-2 bg-light">
                                                            ${plan.instrucciones}
                                                        </div>
                                                    </div>
                                                    `
                                                        : ""
                                                    }
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-warning" onclick="editPlan(${
                                      plan.id
                                    }); bootstrap.Modal.getInstance(document.getElementById('viewPlanModal')).hide();">
                                        <i class="bi bi-pencil me-1"></i>Editar Plan
                                    </button>
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

        // Agregar modal al DOM
        document.body.insertAdjacentHTML("beforeend", modalHtml);

        const modal = new bootstrap.Modal(
          document.getElementById("viewPlanModal")
        );

        // Limpiar modal del DOM cuando se cierre
        document
          .getElementById("viewPlanModal")
          .addEventListener("hidden.bs.modal", function () {
            this.remove();
          });

        // Mostrar modal
        modal.show();
      } else {
        showNotificationToast(
          "Error al cargar los detalles del plan: " +
            (result.error || "Error desconocido"),
          "error"
        );
      }
    })
    .catch((error) => {
      console.error("Error al obtener detalles del plan:", error);
      showNotificationToast("Error al cargar los detalles del plan", "error");
    });
}

function editPlan(planId) {
  console.log("Editar plan:", planId);

  // Obtener detalles completos del plan desde el servidor
  fetch(`/planes/api/${planId}`)
    .then((response) => response.json())
    .then((result) => {
      if (result.success) {
        const plan = result.plan;
        console.log("Datos del plan a editar:", plan);

        // Llenar el formulario con los datos del plan
        try {
          document.getElementById("codigo_plan").value = plan.codigo_plan || "";
          document.getElementById("nombre").value = plan.nombre || "";
          document.getElementById("descripcion").value = plan.descripcion || "";
          document.getElementById("instrucciones").value =
            plan.instrucciones || "";
          document.getElementById("tiempo_estimado").value =
            plan.tiempo_estimado || "";
        } catch (error) {
          console.error("Error al llenar campos básicos:", error);
        }

        // Seleccionar el activo correcto
        if (plan.activo_id) {
          try {
            const selectActivo = document.getElementById("activo_id");
            if (selectActivo) {
              selectActivo.value = plan.activo_id;
            }
          } catch (error) {
            console.error("Error al seleccionar activo:", error);
          }
        }

        // Configurar generación automática
        try {
          const generacionAutomatica = document.getElementById(
            "generacion_automatica"
          );
          if (generacionAutomatica) {
            generacionAutomatica.checked = plan.generacion_automatica !== false; // Default true
          }
        } catch (error) {
          console.error("Error al configurar generación automática:", error);
        }

        // Configurar frecuencia básica
        if (plan.frecuencia) {
          try {
            const mapeoFrecuencia = {
              Diario: "diario",
              Semanal: "semanal",
              Mensual: "mensual",
              Personalizado: "personalizado",
            };
            const tipoFrecuencia =
              mapeoFrecuencia[plan.frecuencia] || "personalizado";
            const tipoFrecuenciaElement =
              document.getElementById("tipo_frecuencia");
            if (tipoFrecuenciaElement) {
              tipoFrecuenciaElement.value = tipoFrecuencia;
              cambiarTipoFrecuencia(); // Mostrar la configuración correspondiente
            }
          } catch (error) {
            console.error("Error al configurar frecuencia:", error);
          }
        }

        // Configurar modal en modo edición
        document.getElementById("modalTitle").innerHTML =
          '<i class="bi bi-pencil me-2"></i>Editar Plan de Mantenimiento';
        document.getElementById("formPlan").dataset.editingId = planId;

        // Abrir el modal
        new bootstrap.Modal(document.getElementById("planModal")).show();
      } else {
        showNotificationToast(
          "Error al cargar los datos del plan: " +
            (result.error || "Error desconocido"),
          "error"
        );
      }
    })
    .catch((error) => {
      console.error("Error al obtener datos del plan:", error);
      showNotificationToast("Error al cargar los datos del plan", "error");
    });
}

function deletePlan(planId, planCodigo) {
  console.log("Eliminar plan:", planId);

  // Crear modal de confirmación dinámico
  const modalHtml = `
        <div class="modal fade" id="confirmDeleteModal" tabindex="-1" aria-labelledby="confirmDeleteModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="confirmDeleteModalLabel">
                            <i class="bi bi-exclamation-triangle me-2"></i>Confirmar Eliminación
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>¿Está seguro de que desea eliminar el plan de mantenimiento?</p>
                        <div class="alert alert-warning">
                            <strong>Código del Plan:</strong> ${planCodigo}<br>
                            <strong>Advertencia:</strong> Esta acción no se puede deshacer.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                            <i class="bi bi-trash me-1"></i>Eliminar Plan
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

  // Agregar modal al DOM
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  const modal = new bootstrap.Modal(
    document.getElementById("confirmDeleteModal")
  );

  // Manejar confirmación
  document
    .getElementById("confirmDeleteBtn")
    .addEventListener("click", async function () {
      try {
        console.log("Enviando solicitud DELETE para plan ID:", planId);

        const response = await fetch(`/planes/api/${planId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        });

        const result = await response.json();
        console.log("Respuesta de eliminación:", result);

        if (response.ok && result.success) {
          showNotificationToast(
            "Plan de mantenimiento eliminado exitosamente",
            "success"
          );
          modal.hide();
          cargarPlanes(); // Recargar la tabla
        } else {
          showNotificationToast(
            "Error al eliminar el plan: " +
              (result.error || "Error desconocido"),
            "error"
          );
        }
      } catch (error) {
        console.error("Error al eliminar plan:", error);
        showNotificationToast("Error al eliminar el plan", "error");
      }
    });

  // Limpiar modal del DOM cuando se cierre
  document
    .getElementById("confirmDeleteModal")
    .addEventListener("hidden.bs.modal", function () {
      this.remove();
    });

  // Mostrar modal
  modal.show();
}

// Función para cargar estadísticas de planes
function cargarEstadisticasPlanes() {
  console.log("📊 Cargando estadísticas de planes...");

  fetch("/planes/api/estadisticas")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("📊 Estadísticas recibidas:", data);
      actualizarTarjetasEstadisticas(data);
    })
    .catch((error) => {
      console.error("—Œ Error cargando estadísticas:", error);
      // En caso de error, mostrar 0 en las tarjetas
      actualizarTarjetasEstadisticas({
        planes_activos: 0,
        planes_proximos: 0,
        planes_vencidos: 0,
        planes_completados: 0,
      });
    });
}

// Función para actualizar las tarjetas de estadísticas
function actualizarTarjetasEstadisticas(data) {
  console.log("ðŸŽ¯ Actualizando tarjetas con datos:", data);

  // Función helper para animar contadores
  function animarContador(elementId, valorFinal) {
    const elemento = document.getElementById(elementId);
    if (!elemento) {
      console.warn(`—š  Elemento ${elementId} no encontrado`);
      return;
    }

    const valorInicial = parseInt(elemento.textContent) || 0;
    const duracion = 1000; // 1 segundo
    const pasos = 60; // 60fps
    const incremento = (valorFinal - valorInicial) / pasos;
    let contador = valorInicial;

    const intervalo = setInterval(() => {
      contador += incremento;
      if (
        (incremento > 0 && contador >= valorFinal) ||
        (incremento < 0 && contador <= valorFinal)
      ) {
        elemento.textContent = valorFinal;
        clearInterval(intervalo);
        console.log(`✅ ${elementId} actualizado a: ${valorFinal}`);
      } else {
        elemento.textContent = Math.round(contador);
      }
    }, 1000 / pasos);
  }

  // Actualizar cada tarjeta con animación
  animarContador("stat-activos", data.planes_activos || 0);
  animarContador("stat-proximos", data.planes_proximos || 0);
  animarContador("stat-vencidos", data.planes_vencidos || 0);
  animarContador("stat-completados", data.planes_completados || 0);

  console.log("ðŸŽ‰ Tarjetas de estadísticas actualizadas exitosamente");
}

// Función para exportar planes a CSV
function exportarCSV() {
  console.log("ðŸ“ Iniciando exportación de planes a CSV...");

  if (!planesData || planesData.length === 0) {
    if (typeof mostrarMensaje === "function") {
      mostrarMensaje(
        "No hay datos para exportar. Primero carga los planes.",
        "warning"
      );
    } else {
      showNotificationToast(
        "No hay datos para exportar. Primero carga los planes.",
        "warning"
      );
    }
    return;
  }

  try {
    // Definir las columnas del CSV
    const columnas = [
      "Código",
      "Nombre",
      "Estado",
      "Frecuencia",
      "Última Ejecución",
      "Próxima Ejecución",
      "Tiempo Estimado (hrs)",
      "Activo Asignado",
      "Descripción",
    ];

    // Crear el contenido CSV
    let csvContent = columnas.join(",") + "\n";

    planesData.forEach((plan) => {
      const fila = [
        `"${plan.codigo_plan || ""}"`,
        `"${plan.nombre || ""}"`,
        `"${plan.estado || ""}"`,
        `"${plan.frecuencia || ""}"`,
        plan.ultima_ejecucion
          ? `"${formatearFecha(plan.ultima_ejecucion)}"`
          : '""',
        plan.proxima_ejecucion
          ? `"${formatearFecha(plan.proxima_ejecucion)}"`
          : '""',
        plan.tiempo_estimado || "0",
        `"${plan.activo_nombre || ""}"`,
        `"${(plan.descripcion || "").replace(/"/g, '""')}"`, // Escapar comillas dobles
      ];
      csvContent += fila.join(",") + "\n";
    });

    console.log(`📊 Generando CSV con ${planesData.length} planes...`);

    // Crear y descargar el archivo
    // Añadir BOM UTF-8 para evitar caracteres mal codificados en Excel
    const blob = new Blob(["\uFEFF" + csvContent], {
      type: "text/csv;charset=utf-8;",
    });

    if (!blob || blob.size === 0) {
      throw new Error("No se pudo crear el archivo CSV");
    }

    const link = document.createElement("a");

    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute("href", url);

      // Generar nombre del archivo con fecha actual
      const ahora = new Date();
      const fechaFormateada =
        ahora.getFullYear() +
        (ahora.getMonth() + 1).toString().padStart(2, "0") +
        ahora.getDate().toString().padStart(2, "0");
      const nombreArchivo = `planes_mantenimiento_${fechaFormateada}.csv`;
      link.setAttribute("download", nombreArchivo);

      link.style.visibility = "hidden";
      document.body.appendChild(link);

      // Intentar la descarga
      try {
        link.click();
        console.log("✅ Comando de descarga ejecutado");

        // Mostrar mensaje informativo apropiado con delay para dar tiempo a que se inicie la descarga
        // La descarga se inicia automáticamente sin notificación

        // Limpiar después de un tiempo
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }, 1000);
      } catch (clickError) {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        throw new Error("Error al iniciar la descarga: " + clickError.message);
      }
    } else {
      throw new Error("Su navegador no soporta la descarga de archivos");
    }
  } catch (error) {
    console.error("—Œ Error al exportar CSV:", error);
    if (typeof mostrarMensaje === "function") {
      mostrarMensaje("Error al exportar el archivo CSV", "danger");
    } else {
      showNotificationToast("Error al exportar el archivo CSV", "error");
    }
  }
}

// Función helper para formatear fechas en el CSV
function formatearFecha(fechaString) {
  if (!fechaString) return "";

  try {
    const fecha = new Date(fechaString);
    const dia = fecha.getDate().toString().padStart(2, "0");
    const mes = (fecha.getMonth() + 1).toString().padStart(2, "0");
    const año = fecha.getFullYear();
    return `${dia}/${mes}/${año}`;
  } catch (error) {
    return fechaString;
  }
}

// Función para generar órdenes manualmente
function generarOrdenesManual() {
  console.log("ð📄 Iniciando generación manual de órdenes...");

  // Mostrar modal de confirmación en lugar de confirm()
  showConfirmModal({
    title: "Generar Í“rdenes Manualmente",
    message:
      "Esto generará órdenes de trabajo para todos los planes que NO tengan generación automática activada.<br><br>¿Desea continuar?",
    confirmText: "Generar Í“rdenes",
    cancelText: "Cancelar",
    type: "warning",
    onConfirm: function () {
      ejecutarGeneracionManual();
    },
    onCancel: function () {
      console.log("—Œ Generación manual cancelada por el usuario");
    },
  });
}

// Función separada para ejecutar la generación después de la confirmación
function ejecutarGeneracionManual() {
  console.log("—³ Ejecutando generación manual...");

  // Hacer la petición sin manipular el botón (el modal ya maneja el loading)
  fetch("/planes/api/generar-ordenes-manual", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((result) => {
      console.log("✅ Resultado generación manual:", result);

      if (result.success) {
        const cantidad = result.ordenes_generadas || 0;
        const mensaje =
          cantidad > 0
            ? `✅ Generación manual completada: ${cantidad} órdenes creadas`
            : "—„¹ No había planes pendientes para generación manual";

        showNotificationToast(mensaje, cantidad > 0 ? "success" : "info");

        // Recargar datos después de un momento
        setTimeout(() => {
          cargarPlanes(paginacionPlanes?.currentPage || 1);
          cargarEstadisticasPlanes();
        }, 1000);
      } else {
        showNotificationToast(
          `—Œ Error en generación manual: ${
            result.error || "Error desconocido"
          }`,
          "error"
        );
      }
    })
    .catch((error) => {
      console.error("—Œ Error en generación manual:", error);
      showNotificationToast(
        `—Œ Error al generar órdenes: ${error.message}`,
        "error"
      );
    });
}
