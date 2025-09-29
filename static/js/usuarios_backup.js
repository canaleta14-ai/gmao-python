// Modulo Usuarios - JavaScript

let usuarios = [];
let usuariosFiltrados = [];
let paginaActual = 1;
let usuariosPorPagina = 10;

document.addEventListener('DOMContentLoaded', function () {
    console.log('Modulo Usuarios iniciado');
    cargarUsuarios();
    inicializarEventListeners();
});

function inicializarEventListeners() {
    // Busqueda en tiempo real
    const inputBuscar = document.getElementById('filtro-buscar');
    if (inputBuscar) {
        let timeoutBusqueda;
        inputBuscar.addEventListener('input', function () {
            clearTimeout(timeoutBusqueda);
            timeoutBusqueda = setTimeout(filtrarUsuarios, 300);
        });
    }

    // Event listeners para filtros
    const filtros = ['filtro-departamento', 'filtro-cargo', 'filtro-estado', 'filtro-fecha'];
    filtros.forEach(filtroId => {
        const filtro = document.getElementById(filtroId);
        if (filtro) {
            filtro.addEventListener('change', filtrarUsuarios);
        }
    });
}

function cargarUsuarios() {
    console.log('Iniciando carga de usuarios...');

    fetch('/usuarios/api')
        .then(response => {
            console.log('Status de respuesta:', response.status);
            console.log('Content-Type:', response.headers.get('Content-Type'));

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Verificar si es JSON o HTML (redireccion de login)
            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('text/html')) {
                console.warn('Respuesta HTML recibida, probablemente redirección de login');
                throw new Error('Sesión expirada o no autenticado');
            }

            return response.json();
        })
        .then(data => {
            console.log('Respuesta de API:', data);

            // Ocultar indicador de carga inicial
            const loadingIndicator = document.getElementById('loading-initial');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }

            if (data.success) {
                usuarios = data.usuarios || [];
                usuariosFiltrados = [...usuarios];
                mostrarUsuarios();
                actualizarContador();
                cargarEstadisticas();
                console.log('Usuarios cargados exitosamente:', usuarios.length);
            } else {
                console.error('Error al cargar usuarios:', data.error);
                mostrarError('Error al cargar usuarios: ' + (data.error || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error de conexión:', error);

            // Ocultar indicador de carga
            const loadingIndicator = document.getElementById('loading-initial');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }

            if (error.message.includes('Sesión expirada')) {
                mostrarError('Sesión expirada. Por favor, recarga la página para iniciar sesión nuevamente.');
            } else {
                mostrarError('Error de conexión al cargar usuarios. Usando datos de prueba.');
                // Fallback a datos de prueba si falla la conexión
                cargarDatosPrueba();
            }
        });
}

function mostrarError(mensaje) {
    mostrarMensaje(mensaje, 'danger');
} function cargarDatosPrueba() {
    console.log('Cargando datos de prueba...');

    usuarios = [
        {
            id: 1,
            codigo: 'USR001',
            nombre: 'Juan Pérez',
            email: 'juan.perez@empresa.com',
            telefono: '+34 666 123 456',
            departamento: 'Mantenimiento',
            cargo: 'Técnico Senior',
            rol: 'Técnico',
            estado: 'Activo',
            fecha_ingreso: '2023-01-15'
        },
        {
            id: 2,
            codigo: 'USR002',
            nombre: 'María García',
            email: 'maria.garcia@empresa.com',
            telefono: '+34 666 234 567',
            departamento: 'Administracion',
            cargo: 'Coordinadora',
            rol: 'Supervisor',
            estado: 'Activo',
            fecha_ingreso: '2023-02-20'
        },
        {
            id: 3,
            codigo: 'USR003',
            nombre: 'Carlos López',
            email: 'carlos.lopez@empresa.com',
            telefono: '+34 666 345 678',
            departamento: 'Operaciones',
            cargo: 'Supervisor',
            rol: 'Supervisor',
            estado: 'Activo',
            fecha_ingreso: '2023-03-10'
        },
        {
            id: 4,
            codigo: 'USR004',
            nombre: 'Ana Martínez',
            email: 'ana.martinez@empresa.com',
            telefono: '+34 666 456 789',
            departamento: 'RRHH',
            cargo: 'Analista',
            rol: 'Analista',
            estado: 'Inactivo',
            fecha_ingreso: '2023-01-30'
        }
    ];
    usuariosFiltrados = [...usuarios];
    mostrarUsuarios();
    actualizarContador();
    cargarEstadisticas();
    console.log('Datos de prueba cargados:', usuarios.length);
}

function cargarEstadisticas() {
    // Actualizar estadísticas básicas
    const totalUsuarios = usuarios.length;
    const usuariosActivos = usuarios.filter(u => u.estado === 'Activo').length;
    const usuariosInactivos = usuarios.filter(u => u.estado === 'Inactivo').length;
    const departamentos = new Set(usuarios.map(u => u.departamento)).size;

    const totalElement = document.getElementById('total-usuarios');
    const activosElement = document.getElementById('usuarios-activos');
    const inactivosElement = document.getElementById('usuarios-inactivos');
    const departamentosElement = document.getElementById('departamentos');

    if (totalElement) totalElement.textContent = totalUsuarios;
    if (activosElement) activosElement.textContent = usuariosActivos;
    if (inactivosElement) inactivosElement.textContent = usuariosInactivos;
    if (departamentosElement) departamentosElement.textContent = departamentos;
}

function mostrarUsuarios() {
    const tbody = document.getElementById('tabla-usuarios');
    if (!tbody) {
        console.error('No se encontró el elemento tabla-usuarios');
        return;
    }

    console.log('Mostrando usuarios:', usuariosFiltrados.length);

    // Calcular paginación
    const inicio = (paginaActual - 1) * usuariosPorPagina;
    const fin = inicio + usuariosPorPagina;
    const usuariosPagina = usuariosFiltrados.slice(inicio, fin);

    // Limpiar tabla
    tbody.innerHTML = '';

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

    usuariosPagina.forEach(usuario => {
        const fila = document.createElement('tr');
        fila.innerHTML = crearFilaUsuario(usuario);
        tbody.appendChild(fila);
    });

    console.log('Usuarios mostrados en la tabla:', usuariosPagina.length);

    // Actualizar paginación
    actualizarPaginacion();
}

function crearFilaUsuario(usuario) {
    const estadoBadge = usuario.estado === 'Activo' ? 'bg-success' : 'bg-secondary';
    const fechaIngreso = usuario.fecha_ingreso ? new Date(usuario.fecha_ingreso).toLocaleDateString('es-ES') : '-';

    // Función para obtener badge del rol
    const getRoleBadge = (rol) => {
        const roleColors = {
            'Administrador': 'bg-danger',
            'Supervisor': 'bg-warning text-dark',
            'Técnico': 'bg-primary',
            'Analista': 'bg-info text-dark',
            'Operador': 'bg-success'
        };
        const color = roleColors[rol] || 'bg-secondary';
        return `<span class="badge ${color}">${rol}</span>`;
    };

    return `
        <td>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" data-id="${usuario.id}">
            </div>
        </td>
        <td>${usuario.id}</td>
        <td><span class="badge bg-light text-dark">${usuario.codigo}</span></td>
        <td>
            <div class="fw-bold">${usuario.nombre}</div>
            <small class="text-muted">${usuario.email}</small>
        </td>
        <td><small class="text-muted">${usuario.telefono || '-'}</small></td>
        <td>${usuario.cargo}</td>
        <td>${getRoleBadge(usuario.rol)}</td>
        <td>
            <span class="badge ${estadoBadge}">${usuario.estado}</span>
        </td>
        <td>
            <small class="text-muted">${fechaIngreso}</small>
        </td>
        <td class="text-center">
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary btn-sm" onclick="editarUsuario(${usuario.id})" 
                    title="Editar usuario" data-bs-toggle="tooltip">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="confirmarEliminacion(${usuario.id}, '${usuario.nombre}')" 
                    title="Eliminar usuario" data-bs-toggle="tooltip">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
}

function actualizarContador() {
    const contador = document.getElementById('contador-usuarios');
    if (contador) {
        const total = usuariosFiltrados.length;
        contador.textContent = `${total} usuario${total !== 1 ? 's' : ''}`;
    }
}

function actualizarPaginacion() {
    const totalPaginas = Math.ceil(usuariosFiltrados.length / usuariosPorPagina);
    const paginacion = document.getElementById('paginacion-usuarios');

    if (!paginacion || totalPaginas <= 1) {
        if (paginacion) paginacion.innerHTML = '';
        return;
    }

    let html = '<ul class="pagination pagination-sm justify-content-center mb-0">';

    // Botón anterior
    html += `
        <li class="page-item ${paginaActual === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual - 1})">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;

    // Páginas numeradas
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
            <a class="page-link" href="#" onclick="cambiarPagina(${paginaActual + 1})">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;

    html += '</ul>';
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
    const buscar = document.getElementById('filtro-buscar').value.toLowerCase();
    const cargo = document.getElementById('filtro-cargo').value;
    const rol = document.getElementById('filtro-rol').value;
    const estado = document.getElementById('filtro-estado').value;
    const telefono = document.getElementById('filtro-telefono').value;
    const fecha = document.getElementById('filtro-fecha').value;

    usuariosFiltrados = usuarios.filter(usuario => {
        const coincideBusqueda = !buscar ||
            (usuario.codigo && usuario.codigo.toLowerCase().includes(buscar)) ||
            (usuario.nombre && usuario.nombre.toLowerCase().includes(buscar)) ||
            (usuario.email && usuario.email.toLowerCase().includes(buscar));

        const coincideCargo = !cargo || (usuario.cargo && usuario.cargo.toLowerCase().includes(cargo.toLowerCase()));
        const coincideRol = !rol || usuario.rol === rol;
        const coincideEstado = !estado || usuario.estado === estado;
        const coincideTelefono = !telefono || (usuario.telefono && usuario.telefono.includes(telefono));

        let coincideFecha = true;
        if (fecha && usuario.fecha_ingreso) {
            const fechaUsuario = new Date(usuario.fecha_ingreso);
            const hoy = new Date();

            switch (fecha) {
                case 'hoy':
                    coincideFecha = fechaUsuario.toDateString() === hoy.toDateString();
                    break;
                case 'semana':
                    const semanaAtras = new Date(hoy.getTime() - 7 * 24 * 60 * 60 * 1000);
                    coincideFecha = fechaUsuario >= semanaAtras;
                    break;
                case 'mes':
                    const mesAtras = new Date(hoy.getFullYear(), hoy.getMonth() - 1, hoy.getDate());
                    coincideFecha = fechaUsuario >= mesAtras;
                    break;
                case 'trimestre':
                    const trimestreAtras = new Date(hoy.getFullYear(), hoy.getMonth() - 3, hoy.getDate());
                    coincideFecha = fechaUsuario >= trimestreAtras;
                    break;
            }
        }

        return coincideBusqueda && coincideCargo && coincideRol && coincideEstado && coincideTelefono && coincideFecha;
    });

    paginaActual = 1; // Resetear a la primera página
    mostrarUsuarios();
    actualizarContador();
}

function limpiarFiltros() {
    document.getElementById('filtro-buscar').value = '';
    document.getElementById('filtro-cargo').value = '';
    document.getElementById('filtro-rol').value = '';
    document.getElementById('filtro-estado').value = '';
    document.getElementById('filtro-telefono').value = '';
    document.getElementById('filtro-fecha').value = '';

    usuariosFiltrados = [...usuarios];
    paginaActual = 1;
    mostrarUsuarios();
    actualizarContador();
}

function mostrarModalNuevoUsuario() {
    limpiarFormulario();
    generarCodigoAutomatico();
    const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
    document.getElementById('modalUsuarioLabel').innerHTML = '<i class="bi bi-person-plus me-2"></i>Nuevo Usuario';
    modal.show();
}

function limpiarFormulario() {
    const form = document.getElementById('form-usuario');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
}

function generarCodigoAutomatico() {
    const codigo = document.getElementById('codigo');
    if (codigo) {
        const nuevoNumero = usuarios.length + 1;
        codigo.value = 'USR' + nuevoNumero.toString().padStart(3, '0');
    }
}

function crearUsuario() {
    const form = document.getElementById('form-usuario');
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const formData = new FormData(form);
    const userData = Object.fromEntries(formData);

    // Agregar fecha de ingreso actual
    userData.fecha_ingreso = new Date().toISOString().split('T')[0];

    fetch('/usuarios/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarMensaje('Usuario creado correctamente', 'success');
                cerrarModalUsuario();
                cargarUsuarios(); // Recargar la lista
                cargarEstadisticas(); // Actualizar estadísticas
            } else {
                mostrarMensaje('Error: ' + (data.error || 'Error al crear usuario'), 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error de conexión al servidor', 'danger');
        });
}

function verUsuario(id) {
    const usuario = usuarios.find(u => u.id === id);
    if (usuario) {
        const fechaIngreso = usuario.fecha_ingreso ? new Date(usuario.fecha_ingreso).toLocaleDateString('es-ES') : 'No disponible';
        const mensaje = `
            <strong>Información del Usuario</strong><br><br>
            <strong>Código:</strong> ${usuario.codigo}<br>
            <strong>Nombre:</strong> ${usuario.nombre}<br>
            <strong>Email:</strong> ${usuario.email}<br>
            <strong>Teléfono:</strong> ${usuario.telefono || 'No disponible'}<br>
            <strong>Departamento:</strong> ${usuario.departamento}<br>
            <strong>Cargo:</strong> ${usuario.cargo}<br>
            <strong>Estado:</strong> ${usuario.estado}<br>
            <strong>Fecha de ingreso:</strong> ${fechaIngreso}
        `;

        // Crear modal personalizado para mostrar detalles
        const modalHtml = `
            <div class="modal fade" id="modalDetallesUsuario" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-person-circle me-2"></i>Detalles del Usuario
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${mensaje}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remover modal anterior si existe
        const modalAnterior = document.getElementById('modalDetallesUsuario');
        if (modalAnterior) {
            modalAnterior.remove();
        }

        // Agregar nuevo modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('modalDetallesUsuario'));
        modal.show();
    }
}

function editarUsuario(id) {
    const usuario = usuarios.find(u => u.id === id);
    if (usuario) {
        const usuario = usuarios.find(u => u.id === id);
        if (usuario) {
            // Llenar el formulario con los datos del usuario
            document.getElementById('codigo').value = usuario.codigo;
            document.getElementById('nombre').value = usuario.nombre;
            document.getElementById('email').value = usuario.email;
            document.getElementById('telefono').value = usuario.telefono || '';
            document.getElementById('departamento').value = usuario.departamento;
            document.getElementById('cargo').value = usuario.cargo;
            document.getElementById('rol').value = usuario.rol;
            document.getElementById('estado').value = usuario.estado;

            // Cambiar el título del modal
            document.getElementById('modalUsuarioLabel').innerHTML = '<i class="fas fa-user-edit me-2"></i>Editar Usuario';

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
            modal.show();

            // Cambiar la función del botón guardar temporalmente
            const botonGuardar = document.querySelector('#modalUsuario .btn-primary');
            botonGuardar.onclick = function () { actualizarUsuario(id); };
        }
    }

    function actualizarUsuario(id) {
        const form = document.getElementById('form-usuario');
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const formData = new FormData(form);
        const userData = Object.fromEntries(formData);
        userData.id = id;

        fetch(`/usuarios/api/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    mostrarMensaje('Usuario actualizado correctamente', 'success');
                    cerrarModalUsuario();
                    cargarUsuarios();
                    cargarEstadisticas();
                } else {
                    mostrarMensaje('Error: ' + (data.error || 'Error al actualizar usuario'), 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('Error de conexión al servidor', 'danger');
            });
    }

    function confirmarEliminacion(id, nombre) {
        if (confirm(`¿Estás seguro de eliminar al usuario "${nombre}"?`)) {
            eliminarUsuario(id);
        }
    }

    function eliminarUsuario(id) {
        fetch(`/usuarios/api/${id}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    mostrarMensaje('Usuario eliminado correctamente', 'success');
                    cargarUsuarios();
                } else {
                    mostrarMensaje('Error: ' + (data.error || 'Error al eliminar usuario'), 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('Error de conexión al servidor', 'danger');
            });
    }

    function cerrarModalUsuario() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalUsuario'));
        if (modal) {
            modal.hide();
        }

        // Restaurar la función original del botón guardar
        const botonGuardar = document.querySelector('#modalUsuario .btn-primary');
        botonGuardar.onclick = crearUsuario;
    }

    function exportarCSVUsuarios() {
        if (usuariosFiltrados.length === 0) {
            mostrarMensaje('No hay usuarios para exportar', 'warning');
            return;
        }

        const headers = ['Código', 'Nombre', 'Email', 'Teléfono', 'Departamento', 'Cargo', 'Estado', 'Fecha Ingreso'];
        const csvContent = [
            headers.join(','),
            ...usuariosFiltrados.map(usuario => [
                usuario.codigo,
                `"${usuario.nombre}"`,
                usuario.email,
                usuario.telefono || '',
                `"${usuario.departamento}"`,
                `"${usuario.cargo}"`,
                usuario.estado,
                usuario.fecha_ingreso || ''
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `usuarios_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        mostrarMensaje('Archivo CSV descargado correctamente', 'success');
    }

    function mostrarMensaje(mensaje, tipo = 'info') {
        const alertas = document.querySelector('.alert');
        if (alertas) {
            alertas.remove();
        }

        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

        const container = document.querySelector('.container-fluid');
        container.insertBefore(alerta, container.firstChild);

        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            if (alerta.parentNode) {
                alerta.remove();
            }
        }, 5000);
    }
