// Modulo Usuarios - JavaScript

let usuarios = [];
let usuariosFiltrados = [];
let paginaActual = 1;
let usuariosPorPagina = 10;

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

document.addEventListener("DOMContentLoaded", function () {
    console.log("Modulo Usuarios iniciado");
    cargarUsuarios();
    inicializarEventListeners();
});

function inicializarEventListeners() {
    // Busqueda en tiempo real con debounce
    const filtrarUsuariosDebounced = debounce(filtrarUsuarios, 500);

    const inputBuscar = document.getElementById("filtro-buscar");
    if (inputBuscar) {
        inputBuscar.addEventListener("input", filtrarUsuariosDebounced);
    }

    // Event listeners para filtros (sin debounce, cambio inmediato)
    const filtros = [
        "filtro-rol",
        "filtro-cargo",
        "filtro-estado",
        "filtro-fecha",
    ];
    filtros.forEach((filtroId) => {
        const filtro = document.getElementById(filtroId);
        if (filtro) {
            filtro.addEventListener("change", filtrarUsuarios);
        }
    });

    // Event listener para el checkbox "Seleccionar todo"
    const selectAllCheckbox = document.getElementById("select-all");
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            toggleSelectAll(this.checked);
        });
    }

    // Event delegation para botones de acción
    document.addEventListener("click", function (event) {
        const target = event.target.closest("[data-action]");
        if (target) {
            // Prevenir múltiples clics
            if (target.disabled) return;

            const action = target.dataset.action;
            const id = parseInt(target.dataset.id);

            console.log("Acción:", action, "ID:", id);

            // Deshabilitar temporalmente el botón
            target.disabled = true;
            setTimeout(() => (target.disabled = false), 1000);

            if (action === "editar") {
                editarUsuario(id);
            } else if (action === "eliminar") {
                const usuario = usuarios.find(u => u.id == id);
                if (usuario) {
                    eliminarUsuario(id, usuario.nombre);
                }
            }
        }
    });

    // Event listener para el botón guardar usuario
    const btnGuardarUsuario = document.getElementById("btn-guardar-usuario");
    if (btnGuardarUsuario) {
        btnGuardarUsuario.addEventListener("click", function () {
            const modal = document.getElementById("modalUsuario");
            const editingId = modal.getAttribute("data-editing-id");

            if (editingId) {
                actualizarUsuario(parseInt(editingId));
            } else {
                crearUsuario();
            }
        });
    }
}

function cargarUsuarios(filtros = {}) {
    console.log("Iniciando carga de usuarios con filtros:", filtros);

    // Construir parámetros de consulta
    const params = new URLSearchParams();
    if (filtros.q) params.append("q", filtros.q);
    if (filtros.rol) params.append("rol", filtros.rol);
    if (filtros.cargo) params.append("cargo", filtros.cargo);
    if (filtros.estado) params.append("estado", filtros.estado);

    const url = `/usuarios/api${params.toString() ? '?' + params.toString() : ''}`;

    fetch(url)
        .then((response) => {
            console.log("Status de respuesta:", response.status);
            console.log("Content-Type:", response.headers.get("Content-Type"));

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Verificar si es JSON o HTML (redireccion de login)
            const contentType = response.headers.get("Content-Type");
            if (contentType && contentType.includes("text/html")) {
                console.warn(
                    "Respuesta HTML recibida, probablemente redirección de login"
                );
                window.location.href = "/login";
                throw new Error("Sesión expirada o no autenticado");
            }

            return response.json();
        })
        .then((data) => {
            console.log("Respuesta de API:", data);

            // Ocultar indicador de carga inicial
            const loadingIndicator = document.getElementById("loading-initial");
            if (loadingIndicator) {
                loadingIndicator.style.display = "none";
            }

            if (data.success) {
                usuarios = data.usuarios || [];
                usuariosFiltrados = [...usuarios];
                mostrarUsuarios();
                actualizarContador();
                cargarEstadisticas();
                console.log("Usuarios cargados exitosamente:", usuarios.length);
            } else {
                console.error("Error al cargar usuarios:", data.error);
                mostrarError(
                    "Error al cargar usuarios: " + (data.error || "Error desconocido")
                );
            }
        })
        .catch((error) => {
            console.error("Error de conexión:", error);

            // Ocultar indicador de carga
            const loadingIndicator = document.getElementById("loading-initial");
            if (loadingIndicator) {
                loadingIndicator.style.display = "none";
            }

            if (error.message.includes("Sesión expirada")) {
                mostrarError(
                    "Sesión expirada. Por favor, recarga la página para iniciar sesión nuevamente."
                );
            } else {
                mostrarError(
                    "Error de conexión al cargar usuarios. Usando datos de prueba."
                );
                // Fallback a datos de prueba si falla la conexión
                cargarDatosPrueba();
            }
        });
}

function mostrarError(mensaje) {
    mostrarMensaje(mensaje, "danger");
}

function cargarDatosPrueba() {
    console.log("Cargando datos de prueba...");

    usuarios = [
        {
            id: 1,
            codigo: "USR001",
            nombre: "Juan Pérez",
            email: "juan.perez@empresa.com",
            telefono: "+34 666 123 456",
            departamento: "Mantenimiento",
            cargo: "Técnico Senior",
            rol: "Técnico",
            estado: "Activo",
            fecha_ingreso: "2023-01-15",
        },
        {
            id: 2,
            codigo: "USR002",
            nombre: "María García",
            email: "maria.garcia@empresa.com",
            telefono: "+34 666 234 567",
            departamento: "Administracion",
            cargo: "Coordinadora",
            rol: "Supervisor",
            estado: "Activo",
            fecha_ingreso: "2023-02-20",
        },
        {
            id: 3,
            codigo: "USR003",
            nombre: "Carlos López",
            email: "carlos.lopez@empresa.com",
            telefono: "+34 666 345 678",
            departamento: "Operaciones",
            cargo: "Supervisor",
            rol: "Supervisor",
            estado: "Activo",
            fecha_ingreso: "2023-03-10",
        },
        {
            id: 4,
            codigo: "USR004",
            nombre: "Ana Martínez",
            email: "ana.martinez@empresa.com",
            telefono: "+34 666 456 789",
            departamento: "RRHH",
            cargo: "Analista",
            rol: "Analista",
            estado: "Inactivo",
            fecha_ingreso: "2023-01-30",
        },
    ];
    usuariosFiltrados = [...usuarios];
    mostrarUsuarios();
    actualizarContador();
    cargarEstadisticas();
    console.log("Datos de prueba cargados:", usuarios.length);
}

function cargarEstadisticas() {
    // Actualizar estadísticas básicas
    const totalUsuarios = usuarios.length;
    const usuariosActivos = usuarios.filter((u) => u.estado === "Activo").length;
    const usuariosInactivos = usuarios.filter(
        (u) => u.estado === "Inactivo"
    ).length;
    const departamentos = new Set(usuarios.map((u) => u.departamento)).size;

    const totalElement = document.getElementById("total-usuarios");
    const activosElement = document.getElementById("usuarios-activos");
    const inactivosElement = document.getElementById("usuarios-inactivos");
    const departamentosElement = document.getElementById("departamentos");

    if (totalElement) totalElement.textContent = totalUsuarios;
    if (activosElement) activosElement.textContent = usuariosActivos;
    if (inactivosElement) inactivosElement.textContent = usuariosInactivos;
    if (departamentosElement) departamentosElement.textContent = departamentos;
}

function mostrarUsuarios() {
    const tbody = document.getElementById("tabla-usuarios");
    if (!tbody) {
        console.error("No se encontró el elemento tabla-usuarios");
        return;
    }

    console.log("Mostrando usuarios:", usuariosFiltrados.length);

    // Calcular paginación
    const inicio = (paginaActual - 1) * usuariosPorPagina;
    const fin = inicio + usuariosPorPagina;
    const usuariosPagina = usuariosFiltrados.slice(inicio, fin);

    // Limpiar tabla
    tbody.innerHTML = "";

    if (usuariosPagina.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-4">
                    <div class="text-muted">
                        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                        <p class="mb-0">No se encontraron usuarios</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    usuariosPagina.forEach((usuario) => {
        const fila = document.createElement("tr");
        fila.innerHTML = crearFilaUsuario(usuario);
        tbody.appendChild(fila);

        // Agregar event listener al checkbox individual
        const checkbox = fila.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener("change", function () {
                actualizarEstadoSeleccion();
                mostrarAccionesMasivas();
            });
        }
    });

    console.log("Usuarios mostrados en la tabla:", usuariosPagina.length);

    // Actualizar paginación
    actualizarPaginacion();
}

function crearFilaUsuario(usuario) {
    const estadoBadge =
        usuario.estado === "Activo" ? "bg-success" : "bg-secondary";
    const fechaIngreso = usuario.fecha_ingreso
        ? new Date(usuario.fecha_ingreso).toLocaleDateString("es-ES")
        : "-";

    // Función para obtener badge del rol
    const getRoleBadge = (rol) => {
        const roleColors = {
            Administrador: "bg-danger",
            Supervisor: "bg-warning text-dark",
            Técnico: "bg-primary",
            Analista: "bg-info text-dark",
            Operador: "bg-success",
        };
        const color = roleColors[rol] || "bg-secondary";
        return `<span class="badge ${color}">${rol}</span>`;
    };

    return `
        <td>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" data-id="${usuario.id
        }">
            </div>
        </td>
        <td><span class="text-muted">#${usuario.id}</span></td>
        <td><span class="badge bg-light text-dark">${usuario.codigo}</span></td>
        <td>
            <div class="fw-bold">${usuario.nombre}</div>
            <small class="text-muted">${usuario.email}</small>
        </td>
        <td><small class="text-muted">${usuario.telefono || "-"}</small></td>
        <td>${usuario.cargo}</td>
        <td>${getRoleBadge(usuario.rol)}</td>
        <td>
            <span class="badge ${estadoBadge}">${usuario.estado}</span>
        </td>
        <td>
            <small class="text-muted">${fechaIngreso}</small>
        </td>
        <td class="text-center">
            <div class="btn-group btn-group-sm" role="group">
                <button class="btn btn-sm btn-outline-secondary action-btn edit" data-action="editar" data-id="${usuario.id
        }" title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger action-btn delete" data-action="eliminar" data-id="${usuario.id
        }" title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </td>
    `;
}

function actualizarContador() {
    const contador = document.getElementById("contador-usuarios");
    if (contador) {
        const total = usuariosFiltrados.length;
        contador.textContent = `${total} usuario${total !== 1 ? "s" : ""}`;
    }
}

function actualizarPaginacion() {
    const totalPaginas = Math.ceil(usuariosFiltrados.length / usuariosPorPagina);
    const paginacion = document.getElementById("paginacion-usuarios");

    if (!paginacion || totalPaginas <= 1) {
        if (paginacion) paginacion.innerHTML = "";
        return;
    }

    let html =
        '<ul class="pagination pagination-sm justify-content-center mb-0">';

    // Botón anterior
    html += `
        <li class="page-item ${paginaActual === 1 ? "disabled" : ""}">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual - 1
        })">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;

    // Páginas numeradas
    for (let i = 1; i <= totalPaginas; i++) {
        if (
            i === 1 ||
            i === totalPaginas ||
            (i >= paginaActual - 2 && i <= paginaActual + 2)
        ) {
            html += `
                <li class="page-item ${i === paginaActual ? "active" : ""}">
                    <a class="page-link" href="#" onclick="cambiarPagina(${i})">${i}</a>
                </li>
            `;
        } else if (i === paginaActual - 3 || i === paginaActual + 3) {
            html +=
                '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }

    // Botón siguiente
    html += `
        <li class="page-item ${paginaActual === totalPaginas ? "disabled" : ""
        }">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual + 1
        })">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;

    html += "</ul>";
    paginacion.innerHTML = html;
}

function cambiarPagina(nuevaPagina) {
    const totalPaginas = Math.ceil(usuariosFiltrados.length / usuariosPorPagina);
    if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
        paginaActual = nuevaPagina;
        mostrarUsuarios();
    }
}

function filtrarUsuarios() {
    console.log("🔍 Filtrando usuarios...");

    const filtros = {
        q: document.getElementById("filtro-buscar")?.value.trim() || "",
        rol: document.getElementById("filtro-rol")?.value || "",
        cargo: document.getElementById("filtro-cargo")?.value || "",
        estado: document.getElementById("filtro-estado")?.value || "",
    };

    console.log("Filtros aplicados:", filtros);

    // Cargar usuarios con filtros desde el servidor
    cargarUsuarios(filtros);
}

function limpiarFiltros() {
    console.log("🧹 Limpiando filtros...");

    document.getElementById("filtro-buscar").value = "";
    document.getElementById("filtro-cargo").value = "";
    document.getElementById("filtro-rol").value = "";
    document.getElementById("filtro-estado").value = "";

    const filtroTelefono = document.getElementById("filtro-telefono");
    if (filtroTelefono) filtroTelefono.value = "";

    const filtroFecha = document.getElementById("filtro-fecha");
    if (filtroFecha) filtroFecha.value = "";

    paginaActual = 1;

    // Recargar usuarios sin filtros
    cargarUsuarios();
    mostrarUsuarios();
    actualizarContador();
}

function mostrarModalNuevoUsuario() {
    limpiarFormulario();
    generarCodigoAutomatico();

    const modalElement = document.getElementById("modalUsuario");
    modalElement.removeAttribute("data-editing-id"); // Limpiar modo edición

    const modal = new bootstrap.Modal(modalElement);
    document.getElementById("modalUsuarioLabel").innerHTML =
        '<i class="bi bi-person-plus me-2"></i>Nuevo Usuario';
    modal.show();
}

function limpiarFormulario() {
    const form = document.getElementById("form-usuario");
    if (form) {
        form.reset();
        form.classList.remove("was-validated");
    }
}

function generarCodigoAutomatico() {
    const codigo = document.getElementById("codigo");
    if (codigo) {
        codigo.value = generarCodigoUsuario();
    }
}

function crearUsuario() {
    const form = document.getElementById("form-usuario");
    if (!form.checkValidity()) {
        form.classList.add("was-validated");
        return;
    }

    const formData = new FormData(form);
    const userData = {
        username: formData.get("username"),
        email: formData.get("email"),
        password: formData.get("password"),
        nombre: formData.get("nombre"),
        rol: formData.get("rol") || "Técnico",
        estado: formData.get("estado") || "Activo",
        fecha_ingreso: new Date().toISOString().split("T")[0]
    };

    fetch("/usuarios/api", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                const username = document.getElementById("username").value;
                mostrarMensaje(
                    `Usuario '${username}' creado correctamente. Para usar esta cuenta, haga logout y login con las credenciales proporcionadas.`,
                    "success"
                );
                cerrarModalUsuario();
                cargarUsuarios();
            } else {
                mostrarMensaje(
                    "Error: " + (data.error || "Error al crear usuario"),
                    "danger"
                );
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            mostrarMensaje("Error de conexión al servidor", "danger");
        });
}

async function editarUsuario(id) {
    console.log("Editando usuario con ID:", id, typeof id);

    try {
        const response = await fetch(`/usuarios/api/${id}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const usuario = data.usuario;
                console.log("Usuario obtenido del servidor:", usuario);

                // Llenar el formulario con los datos del usuario
                document.getElementById("codigo").value = usuario.username || ""; // Usar username como código
                document.getElementById("username").value = usuario.username || "";
                document.getElementById("nombre").value = usuario.nombre || "";
                document.getElementById("email").value = usuario.email || "";
                // No llenar password en edición por seguridad
                document.getElementById("telefono").value = usuario.telefono || "";
                document.getElementById("departamento").value =
                    usuario.departamento || "Mantenimiento";
                document.getElementById("cargo").value = usuario.cargo || "Técnico";
                document.getElementById("rol").value = usuario.rol || "Técnico";
                document.getElementById("estado").value = usuario.estado || "Activo";

                // Cambiar el título del modal
                const modalLabel = document.getElementById("modalUsuarioLabel");
                if (modalLabel) {
                    modalLabel.innerHTML =
                        '<i class="bi bi-pencil me-2"></i>Editar Usuario';
                }

                // Guardar el ID del usuario en el modal para usar después
                const modalElement = document.getElementById("modalUsuario");
                modalElement.setAttribute("data-editing-id", id);

                // Mostrar modal
                const modal = new bootstrap.Modal(modalElement);
                modal.show();

                console.log("Modal de edición mostrado para usuario ID:", id);
            } else {
                console.error("Error del servidor:", data.error);
                mostrarMensaje(
                    "Error al cargar los datos del usuario: " + data.error,
                    "danger"
                );
            }
        } else {
            console.error("Error HTTP:", response.status);
            mostrarMensaje("Error al cargar los datos del usuario", "danger");
        }
    } catch (error) {
        console.error("Error de conexión:", error);
        mostrarMensaje("Error de conexión al cargar usuario", "danger");
    }
}

function actualizarUsuario(id) {
    console.log("Actualizando usuario con ID:", id);

    const form = document.getElementById("form-usuario");
    const isEditing = form.closest("[data-editing-id]") !== null;

    // En modo edición, hacer el campo password opcional
    const passwordField = document.getElementById("password");
    if (isEditing) {
        passwordField.removeAttribute("required");
    } else {
        passwordField.setAttribute("required", "required");
    }

    if (!form.checkValidity()) {
        form.classList.add("was-validated");
        mostrarMensaje(
            "Por favor, complete todos los campos requeridos",
            "warning"
        );
        return;
    }

    const formData = new FormData(form);
    const userData = Object.fromEntries(formData);
    userData.id = id;

    // Si estamos editando y el password está vacío, no enviarlo
    if (isEditing && (!userData.password || userData.password.trim() === "")) {
        delete userData.password;
    }

    console.log("Datos a enviar:", userData);

    fetch(`/usuarios/api/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
    })
        .then((response) => {
            console.log("Response status:", response.status);
            return response.json();
        })
        .then((data) => {
            console.log("Respuesta del servidor:", data);
            if (data.success) {
                mostrarMensaje("Usuario actualizado correctamente", "success");
                cerrarModalUsuario();
                cargarUsuarios();
            } else {
                mostrarMensaje(
                    "Error: " + (data.error || "Error al actualizar usuario"),
                    "danger"
                );
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            mostrarMensaje("Error de conexión al servidor", "danger");
        });
}

async function eliminarUsuario(id, nombre) {
    console.log('Solicitud de eliminar usuario:', id, nombre);

    try {
        const resp = await fetch(`/usuarios/api/${id}`);
        if (resp.ok) {
            const data = await resp.json();
            const username = data?.usuario?.username || "";
            if (username === "admin") {
                mostrarMensaje("No se puede eliminar el usuario administrador", "warning");
                const btn = document.querySelector(`button.action-btn.delete[data-id="${id}"]`);
                if (btn) {
                    btn.disabled = true;
                    btn.title = "Administrador protegido";
                }
                return;
            }
        }
    } catch (e) {
        console.error("Error verificando usuario antes de eliminar:", e);
    }

    mostrarConfirmacionEliminarUsuario(id, nombre);
}

function cerrarModalUsuario() {
    const modal = bootstrap.Modal.getInstance(
        document.getElementById("modalUsuario")
    );
    if (modal) {
        modal.hide();
    }

    // Limpiar modo edición
    document.getElementById("modalUsuario").removeAttribute("data-editing-id");

    // Resetear título del modal
    document.getElementById("modalUsuarioLabel").innerHTML =
        '<i class="bi bi-person-plus me-2"></i>Nuevo Usuario';

    // Limpiar formulario
    const form = document.getElementById("form-usuario");
    if (form) {
        form.reset();
        form.classList.remove("was-validated");
    }
}

function exportarCSVUsuarios() {
    if (usuariosFiltrados.length === 0) {
        mostrarMensaje("No hay usuarios para exportar", "warning");
        return;
    }

    // Usar la función estandarizada como en el resto de la app
    if (typeof descargarCSVMejorado === "function") {
        descargarCSVMejorado(
            "/usuarios/exportar-csv",
            "usuarios_{fecha}",
            "CSV"
        ).catch((error) => {
            console.error("Error exportando CSV:", error);
            mostrarMensaje("Error al exportar CSV", "danger");
        });
    } else {
        // Fallback simple si no está disponible descargarCSVMejorado
        window.open("/usuarios/exportar-csv", "_blank");
    }
}

function mostrarMensaje(mensaje, tipo = "info") {
    const alertas = document.querySelector(".alert");
    if (alertas) {
        alertas.remove();
    }

    const alerta = document.createElement("div");
    alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    const container = document.querySelector(".container-fluid");
    container.insertBefore(alerta, container.firstChild);

    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        if (alerta.parentNode) {
            alerta.remove();
        }
    }, 5000);
}

// ===== FUNCIONES DE SELECCIÓN MASIVA =====

function toggleSelectAll(seleccionado) {
    const checkboxes = document.querySelectorAll(
        '#tabla-usuarios input[type="checkbox"]'
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = seleccionado;
    });
    actualizarEstadoSeleccion();
    mostrarAccionesMasivas();
}

function actualizarEstadoSeleccion() {
    const checkboxes = document.querySelectorAll(
        '#tabla-usuarios input[type="checkbox"]'
    );
    const selectAllCheckbox = document.getElementById("select-all");
    const totalCheckboxes = checkboxes.length;
    const seleccionados = document.querySelectorAll(
        '#tabla-usuarios input[type="checkbox"]:checked'
    );
    const totalSeleccionados = seleccionados.length;

    if (selectAllCheckbox) {
        if (totalSeleccionados === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (totalSeleccionados === totalCheckboxes) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
            selectAllCheckbox.checked = false;
        }
    }

    // Actualizar contador de seleccionados
    const contadorSeleccion = document.getElementById("contador-seleccion");
    if (contadorSeleccion) {
        if (totalSeleccionados > 0) {
            contadorSeleccion.textContent = `${totalSeleccionados} seleccionado${totalSeleccionados > 1 ? "s" : ""
                }`;
            contadorSeleccion.style.display = "inline";
        } else {
            contadorSeleccion.style.display = "none";
        }
    }
}

function mostrarAccionesMasivas() {
    const seleccionados = document.querySelectorAll(
        '#tabla-usuarios input[type="checkbox"]:checked'
    );
    const accionesMasivas = document.getElementById("acciones-masivas");

    if (accionesMasivas) {
        if (seleccionados.length > 0) {
            accionesMasivas.style.display = "block";
        } else {
            accionesMasivas.style.display = "none";
        }
    }
}

function obtenerUsuariosSeleccionados() {
    const seleccionados = document.querySelectorAll(
        '#tabla-usuarios input[type="checkbox"]:checked'
    );
    const idsSeleccionados = Array.from(seleccionados).map((checkbox) =>
        parseInt(checkbox.getAttribute("data-id"))
    );
    return usuarios.filter((usuario) => idsSeleccionados.includes(usuario.id));
}

function eliminarSeleccionados() {
    const usuariosSeleccionados = obtenerUsuariosSeleccionados();
    if (usuariosSeleccionados.length === 0) {
        mostrarMensaje("No hay usuarios seleccionados", "warning");
        return;
    }

    const nombres = usuariosSeleccionados.map((u) => u.nombre).join(", ");
    const mensaje =
        usuariosSeleccionados.length === 1
            ? `¿Estás seguro de eliminar al usuario "${nombres}"?`
            : `¿Estás seguro de eliminar a los ${usuariosSeleccionados.length} usuarios seleccionados?<br><br>${nombres}`;

    // Mostrar modal de confirmación en lugar de confirm()
    showConfirmModal({
        title: "Eliminar Usuarios",
        message: mensaje,
        confirmText: "Eliminar",
        cancelText: "Cancelar",
        type: "danger",
        onConfirm: function () {
            const promesas = usuariosSeleccionados.map((usuario) =>
                fetch(`/usuarios/api/${usuario.id}`, { method: "DELETE" }).then(
                    (response) => response.json()
                )
            );

            Promise.all(promesas)
                .then((resultados) => {
                    const exitosos = resultados.filter((r) => r.success).length;
                    const fallidos = resultados.length - exitosos;

                    if (fallidos === 0) {
                        mostrarMensaje(
                            `${exitosos} usuario${exitosos > 1 ? "s" : ""} eliminado${exitosos > 1 ? "s" : ""
                            } correctamente`,
                            "success"
                        );
                    } else {
                        mostrarMensaje(
                            `${exitosos} usuarios eliminados, ${fallidos} fallaron`,
                            "warning"
                        );
                    }

                    cargarUsuarios();
                    limpiarSeleccion();
                })
                .catch((error) => {
                    console.error("Error:", error);
                    mostrarMensaje("Error al eliminar usuarios", "danger");
                });
        },
        onCancel: function () {
            console.log("❌ Eliminación cancelada por el usuario");
        }
    });
}

function cambiarEstadoSeleccionados(nuevoEstado) {
    const usuariosSeleccionados = obtenerUsuariosSeleccionados();
    if (usuariosSeleccionados.length === 0) {
        mostrarMensaje("No hay usuarios seleccionados", "warning");
        return;
    }

    const accion = nuevoEstado === "Activo" ? "activar" : "desactivar";
    const mensaje = `¿Estás seguro de ${accion} ${usuariosSeleccionados.length
        } usuario${usuariosSeleccionados.length > 1 ? "s" : ""}?`;

    // Mostrar modal de confirmación en lugar de confirm()
    showConfirmModal({
        title: nuevoEstado === "Activo" ? "Activar Usuarios" : "Desactivar Usuarios",
        message: mensaje,
        confirmText: nuevoEstado === "Activo" ? "Activar" : "Desactivar",
        cancelText: "Cancelar",
        type: "warning",
        onConfirm: function () {
            const promesas = usuariosSeleccionados.map((usuario) => {
                const userData = {
                    username: usuario.username || usuario.nombre?.toLowerCase().replace(/\s+/g, ''),
                    email: usuario.email,
                    nombre: usuario.nombre,
                    rol: usuario.rol,
                    estado: nuevoEstado
                };
                return fetch(`/usuarios/api/${usuario.id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(userData),
                }).then((response) => response.json());
            });

            Promise.all(promesas)
                .then((resultados) => {
                    const exitosos = resultados.filter((r) => r.success).length;
                    const fallidos = resultados.length - exitosos;

                    if (fallidos === 0) {
                        mostrarMensaje(
                            `${exitosos} usuario${exitosos > 1 ? "s" : ""} ${accion}${exitosos > 1 ? "s" : ""
                            } correctamente`,
                            "success"
                        );
                    } else {
                        mostrarMensaje(
                            `${exitosos} usuarios procesados, ${fallidos} fallaron`,
                            "warning"
                        );
                    }

                    cargarUsuarios();
                    limpiarSeleccion();
                })
                .catch((error) => {
                    console.error("Error:", error);
                    mostrarMensaje(`Error al ${accion} usuarios`, "danger");
                });
        },
        onCancel: function () {
            console.log("❌ Cambio de estado cancelado por el usuario");
        }
    });
}

function exportarSeleccionados() {
    const usuariosSeleccionados = obtenerUsuariosSeleccionados();
    if (usuariosSeleccionados.length === 0) {
        mostrarMensaje("No hay usuarios seleccionados para exportar", "warning");
        return;
    }

    const headers = [
        "Código",
        "Nombre",
        "Email",
        "Teléfono",
        "Departamento",
        "Cargo",
        "Rol",
        "Estado",
        "Fecha Ingreso",
    ];
    const csvContent = [
        headers.join(","),
        ...usuariosSeleccionados.map((usuario) =>
            [
                usuario.codigo,
                `"${usuario.nombre}"`,
                usuario.email,
                usuario.telefono || "",
                `"${usuario.departamento}"`,
                `"${usuario.cargo}"`,
                usuario.rol,
                usuario.estado,
                usuario.fecha_ingreso || "",
            ].join(",")
        ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute(
        "download",
        `usuarios_seleccionados_${new Date().toISOString().split("T")[0]}.csv`
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    mostrarMensaje(
        `${usuariosSeleccionados.length} usuario${usuariosSeleccionados.length > 1 ? "s" : ""
        } exportado${usuariosSeleccionados.length > 1 ? "s" : ""} correctamente`,
        "success"
    );
}

function limpiarSeleccion() {
    const selectAllCheckbox = document.getElementById("select-all");
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    }

    const checkboxes = document.querySelectorAll(
        '#tabla-usuarios input[type="checkbox"]'
    );
    checkboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });

    mostrarAccionesMasivas();
    actualizarEstadoSeleccion();
}

// Función para crear un nuevo usuario
function crearUsuario() {
    const form = document.getElementById("form-usuario");
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const usuarioData = {
        username: formData.get("username"), // Usar username como username
        email: formData.get("email"),
        password: formData.get("password"),
        nombre: formData.get("nombre"),
        rol: formData.get("rol") || "Técnico",
        estado: formData.get("estado") || "Activo",
    };

    // Validar campos requeridos
    if (
        !usuarioData.username ||
        !usuarioData.email ||
        !usuarioData.password ||
        !usuarioData.nombre
    ) {
        mostrarMensaje(
            "Por favor, complete todos los campos requeridos",
            "warning"
        );
        return;
    }

    const btnGuardar = document.getElementById("btn-guardar-usuario");
    const originalText = btnGuardar.innerHTML;
    btnGuardar.disabled = true;
    btnGuardar.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';

    fetch("/usuarios/api", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(usuarioData),
    })
        .then((response) => {
            console.log("Status de respuesta:", response.status);
            console.log("Content-Type:", response.headers.get("Content-Type"));
            return response.json();
        })
        .then((data) => {
            console.log("Respuesta de API:", data);

            if (data.success) {
                mostrarMensaje("Usuario creado correctamente", "success");

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById("modalUsuario")
                );
                modal.hide();

                // Limpiar formulario
                form.reset();

                // Recargar usuarios
                cargarUsuarios();
            } else {
                mostrarMensaje(
                    "Error al crear usuario: " + (data.error || "Error desconocido"),
                    "danger"
                );
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            mostrarMensaje("Error de conexión al crear usuario", "danger");
        })
        .finally(() => {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = originalText;
        });
} // Función para actualizar un usuario existente
function actualizarUsuario(id) {
    const form = document.getElementById("form-usuario");
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = new FormData(form);
    const usuarioData = {
        username: formData.get("username"),
        email: formData.get("email"),
        nombre: formData.get("nombre"),
        rol: formData.get("rol") || "Técnico",
        estado: formData.get("estado") || "Activo",
    };

    // Solo incluir password si se proporcionó uno nuevo
    const password = formData.get("password");
    if (password) {
        usuarioData.password = password;
    }

    const btnGuardar = document.getElementById("btn-guardar-usuario");
    const originalText = btnGuardar.innerHTML;
    btnGuardar.disabled = true;
    btnGuardar.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';

    fetch(`/usuarios/api/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(usuarioData),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                mostrarMensaje("Usuario actualizado correctamente", "success");

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById("modalUsuario")
                );
                modal.hide();

                // Recargar usuarios
                cargarUsuarios();
            } else {
                mostrarMensaje(
                    "Error al actualizar usuario: " + (data.error || "Error desconocido"),
                    "danger"
                );
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            mostrarMensaje("Error de conexión al actualizar usuario", "danger");
        })
        .finally(() => {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = originalText;
        });
}

// Función para eliminar un usuario
async function eliminarUsuario(id) {
    const usuario = usuarios.find((u) => u.id === id);
    if (!usuario) {
        mostrarMensaje("Usuario no encontrado", "danger");
        return;
    }

    // Verificar si es el usuario administrador antes de mostrar confirmación
    try {
        const resp = await fetch(`/usuarios/api/${id}`);
        if (resp.ok) {
            const data = await resp.json();
            const username = data?.usuario?.username || "";
            if (username === "admin") {
                mostrarMensaje("No se puede eliminar el usuario administrador", "warning");
                const btn = document.querySelector(`button.action-btn.delete[data-id="${id}"]`);
                if (btn) {
                    btn.disabled = true;
                    btn.title = "Administrador protegido";
                }
                return;
            }
        }
    } catch (e) {
        console.error("Error verificando usuario antes de confirmar eliminación:", e);
    }

    // Mostrar modal de confirmación en lugar de confirm()
    showConfirmModal({
        title: "Eliminar Usuario",
        message: `¿Está seguro de que desea eliminar al usuario "${usuario.nombre}"?<br><br>Esta acción no se puede deshacer.`,
        confirmText: "Eliminar",
        cancelText: "Cancelar",
        type: "danger",
        onConfirm: function () {
            fetch(`/usuarios/api/${id}`, {
                method: "DELETE",
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        mostrarMensaje("Usuario eliminado correctamente", "success");
                        // Recargar usuarios
                        cargarUsuarios();
                    } else {
                        mostrarMensaje(
                            "Error al eliminar usuario: " + (data.error || "Error desconocido"),
                            "danger"
                        );
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    mostrarMensaje("Error de conexión al eliminar usuario", "danger");
                });
        },
        onCancel: function () {
            console.log("❌ Eliminación de usuario cancelada");
        }
    });
}

// Función para generar un código de usuario único
function generarCodigoUsuario() {
    const timestamp = Date.now().toString().slice(-4); // Últimos 4 dígitos del timestamp
    const random = Math.floor(Math.random() * 1000)
        .toString()
        .padStart(3, "0"); // 3 dígitos aleatorios
    return `USR${timestamp}${random}`;
}

// Variable para el usuario a eliminar
let usuarioAEliminar = null;

function confirmarEliminarUsuario() {
    if (usuarioAEliminar) {
        eliminarUsuarioConfirmado(usuarioAEliminar.id);
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalEliminarUsuario'));
        if (modal) {
            modal.hide();
        }
        usuarioAEliminar = null;
    }
}

// Mostrar modal de confirmación antes de eliminar
async function mostrarConfirmacionEliminarUsuario(id, nombre) {
    try {
        const resp = await fetch(`/usuarios/api/${id}`);
        if (resp.ok) {
            const data = await resp.json();
            const username = data?.usuario?.username || "";
            if (username === "admin") {
                mostrarMensaje("No se puede eliminar el usuario administrador", "warning");
                const btn = document.querySelector(`button.action-btn.delete[data-id="${id}"]`);
                if (btn) {
                    btn.disabled = true;
                    btn.title = "Administrador protegido";
                }
                return;
            }
        }
    } catch (e) {
        console.error("Error verificando usuario:", e);
    }

    usuarioAEliminar = { id, nombre };

    const nombreElement = document.getElementById('nombre-usuario-eliminar');
    if (nombreElement) {
        nombreElement.textContent = nombre;
    }

    const modal = new bootstrap.Modal(document.getElementById('modalEliminarUsuario'));
    modal.show();
}

// Eliminar usuario confirmado
async function eliminarUsuarioConfirmado(id) {
    try {
        mostrarCargando(true);

        const response = await fetch(`/usuarios/api/${id}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
        });

        const data = await response.json();

        if (data.success) {
            mostrarMensaje("Usuario eliminado correctamente", "success");
            cargarUsuarios();
        } else {
            mostrarMensaje(
                "Error: " + (data.error || "Error al eliminar usuario"),
                "danger"
            );
        }
    } catch (error) {
        console.error("Error al eliminar usuario:", error);
        mostrarMensaje("Error de conexión al eliminar usuario", "danger");
    } finally {
        mostrarCargando(false);
    }
}
