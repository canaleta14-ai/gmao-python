let perPage = 10;
let currentPage = 1;

function cargarUsuarios(page = 1) {
    currentPage = page;
    const username = document.getElementById('filtro-username').value;
    const email = document.getElementById('filtro-email').value;
    const rol = document.getElementById('filtro-rol').value;
    const activo = document.getElementById('filtro-activo').value;

    let url = `/usuarios/api?page=${page}&per_page=${perPage}`;
    if (username) url += `&username=${encodeURIComponent(username)}`;
    if (email) url += `&email=${encodeURIComponent(email)}`;
    if (rol) url += `&rol=${encodeURIComponent(rol)}`;
    if (activo) url += `&activo=${encodeURIComponent(activo)}`;

    fetch(url)
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('tabla-usuarios');
            tbody.innerHTML = '';

            data.usuarios.forEach(u => {
                const badgeClass = u.activo ? 'bg-success' : 'bg-secondary';
                const badgeText = u.activo ? 'Activo' : 'Inactivo';
                const btnClass = u.activo ? 'btn-outline-warning' : 'btn-outline-success';
                const btnIcon = u.activo ? 'bi-toggle-off' : 'bi-toggle-on';
                const btnText = u.activo ? 'Desactivar' : 'Activar';

                tbody.innerHTML += `
                    <tr>
                        <td><span class="badge bg-light text-dark">${u.id}</span></td>
                        <td><strong>${u.username}</strong></td>
                        <td>${u.email}</td>
                        <td>${u.nombre || '<em class="text-muted">Sin especificar</em>'}</td>
                        <td><span class="badge bg-primary">${u.rol}</span></td>
                        <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                        <td>
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary" onclick="editarUsuario(${u.id})" title="Editar">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button type="button" class="btn ${btnClass}" onclick="toggleActivo(${u.id}, ${!u.activo})" title="${btnText}">
                                    <i class="bi ${btnIcon}"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            renderPaginacion(data.page, data.per_page, data.total);
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al cargar usuarios', 'danger');
        });
}

function renderPaginacion(page, perPage, total) {
    const paginacion = document.getElementById('paginacion');
    paginacion.innerHTML = '';

    const totalPages = Math.ceil(total / perPage);

    if (totalPages <= 1) return;

    // Botón anterior
    const prevClass = page === 1 ? 'disabled' : '';
    paginacion.innerHTML += `
        <li class="page-item ${prevClass}">
            <a class="page-link" href="#" onclick="cargarUsuarios(${page - 1})">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;

    // Números de página
    for (let i = 1; i <= totalPages; i++) {
        const activeClass = i === page ? 'active' : '';
        paginacion.innerHTML += `
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" onclick="cargarUsuarios(${i})">${i}</a>
            </li>
        `;
    }

    // Botón siguiente
    const nextClass = page === totalPages ? 'disabled' : '';
    paginacion.innerHTML += `
        <li class="page-item ${nextClass}">
            <a class="page-link" href="#" onclick="cargarUsuarios(${page + 1})">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;
}

function toggleActivo(id, estado) {
    fetch(`/usuarios/api/${id}/estado`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activo: estado })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarAlerta(`Usuario ${estado ? 'activado' : 'desactivado'} exitosamente`, 'success');
                cargarUsuarios(currentPage);
            } else {
                mostrarAlerta('Error al cambiar estado del usuario', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al cambiar estado del usuario', 'danger');
        });
}

function mostrarModalNuevoUsuario() {
    const modal = new bootstrap.Modal(document.getElementById('modalNuevoUsuario'));
    document.getElementById('formNuevoUsuario').reset();
    modal.show();
}

function crearUsuario() {
    const username = document.getElementById('nuevo-username').value;
    const email = document.getElementById('nuevo-email').value;
    const nombre = document.getElementById('nuevo-nombre').value;
    const password = document.getElementById('nuevo-password').value;
    const rol = document.getElementById('nuevo-rol').value;

    if (!username || !email || !password || !rol) {
        mostrarAlerta('Por favor complete todos los campos requeridos', 'warning');
        return;
    }

    fetch('/usuarios/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: username,
            email: email,
            nombre: nombre,
            password: password,
            rol: rol
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoUsuario'));
                modal.hide();
                mostrarAlerta('Usuario creado exitosamente', 'success');
                cargarUsuarios(1);
            } else {
                mostrarAlerta('Error al crear usuario', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al crear usuario', 'danger');
        });
}

function editarUsuario(id) {
    // Función para editar usuario (por implementar)
    mostrarAlerta('Función de edición en desarrollo', 'info');
}

function mostrarAlerta(mensaje, tipo) {
    if (!mensaje || mensaje === 'undefined' || mensaje === null) {
        mensaje = 'Operación realizada';
    }

    // Mapear tipos de Bootstrap a tipos de toast
    const tipoMap = {
        'danger': 'error',
        'success': 'success',
        'warning': 'warning',
        'info': 'info'
    };

    const tipoToast = tipoMap[tipo] || 'info';

    // Solo mostrar en consola si es error o si estamos en desarrollo
    if (tipoToast === 'error' || window.location.hostname === 'localhost') {
        console.log(`${tipoToast.toUpperCase()}: ${mensaje}`);
    }

    // Usar el sistema de toasts global si está disponible
    if (typeof showNotificationToast === 'function') {
        showNotificationToast({
            titulo: getTituloSegunTipo(tipoToast),
            mensaje: mensaje,
            tipo: tipoToast,
            tiempo: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        });
    } else {
        // Fallback al sistema de alertas
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
        alertContainer.style.top = '20px';
        alertContainer.style.right = '20px';
        alertContainer.style.zIndex = '9999';
        alertContainer.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertContainer);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
}

function getTituloSegunTipo(tipo) {
    const titulos = {
        'success': '✅ Éxito',
        'error': '❌ Error',
        'warning': '⚠️ Advertencia',
        'info': 'ℹ️ Información'
    };
    return titulos[tipo] || 'Información';
}

// Event listeners
document.addEventListener('DOMContentLoaded', function () {
    cargarUsuarios(1);

    // Permitir buscar con Enter en los campos de filtro
    ['filtro-username', 'filtro-email'].forEach(id => {
        document.getElementById(id).addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                cargarUsuarios(1);
            }
        });
    });

    // Inicializar autocompletado después de cargar página
    setTimeout(() => {
        inicializarAutocompletado();
    }, 500);
});

// Inicializar autocompletado en formularios de usuarios
function inicializarAutocompletado() {
    console.log('Inicializando autocompletado en usuarios...');

    if (!window.AutoComplete) {
        console.log('AutoComplete no disponible');
        return;
    }

    // Autocompletado para filtro de username
    const filtroUsername = document.getElementById('filtro-username');
    if (filtroUsername) {
        new AutoComplete({
            element: filtroUsername,
            apiUrl: '/usuarios/api',
            searchKey: 'q',
            displayKey: item => `${item.username} (${item.nombre || 'Sin nombre'})`,
            valueKey: 'username',
            placeholder: 'Buscar por usuario...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Usuario seleccionado para filtro:', item);
                cargarUsuarios(1);
            }
        });
    }

    // Autocompletado para filtro de email
    const filtroEmail = document.getElementById('filtro-email');
    if (filtroEmail) {
        new AutoComplete({
            element: filtroEmail,
            apiUrl: '/usuarios/api',
            searchKey: 'q',
            displayKey: item => `${item.email} - ${item.nombre || item.username}`,
            valueKey: 'email',
            placeholder: 'Buscar por email...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Email seleccionado para filtro:', item);
                cargarUsuarios(1);
            }
        });
    }

    // Autocompletado para campo nombre en formulario de nuevo usuario
    const nuevoNombre = document.getElementById('nuevo-nombre');
    if (nuevoNombre) {
        new AutoComplete({
            element: nuevoNombre,
            apiUrl: '/usuarios/api',
            searchKey: 'nombre',
            displayKey: 'nombre',
            valueKey: 'nombre',
            placeholder: 'Nombre completo...',
            allowFreeText: true,
            onSelect: (item) => {
                console.log('Nombre seleccionado:', item);
            }
        });
    }

    console.log('Autocompletado inicializado en usuarios');
}

// Prevenir envío de formularios por defecto
document.addEventListener('submit', function (e) {
    e.preventDefault();
});
