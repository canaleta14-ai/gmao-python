let perPage = 10;
let currentPage = 1;
let paginacionUsuarios;

function cargarUsuarios(page = 1) {
    currentPage = page;
    const username = document.getElementById('filtro-username').value.trim();
    const email = document.getElementById('filtro-email').value.trim();
    const rol = document.getElementById('filtro-rol').value;
    const activo = document.getElementById('filtro-activo').value;

    let url = `/usuarios/api?page=${page}&per_page=${perPage}`;
    if (username) url += `&username=${encodeURIComponent(username)}`;
    if (email) url += `&email=${encodeURIComponent(email)}`;
    if (rol) url += `&rol=${encodeURIComponent(rol)}`;
    if (activo) url += `&activo=${encodeURIComponent(activo)}`;

    console.log('🔍 Cargando usuarios con URL:', url);
    console.log('üìä Filtros aplicados:', { username, email, rol, activo });

    fetch(url)
        .then(r => {
            console.log('üì° Response status:', r.status);
            return r.json();
        })
        .then(data => {
            console.log('üì¶ Datos recibidos:', data);
            const tbody = document.getElementById('tabla-usuarios');
            tbody.innerHTML = '';

            if (data.usuarios && data.usuarios.length > 0) {
                console.log(`üë• Mostrando ${data.usuarios.length} usuarios de ${data.total} total`);
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
                                    <button type="button" class="btn btn-sm btn-outline-primary action-btn edit" onclick="editarUsuario(${u.id})" title="Editar">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button type="button" class="btn btn-sm ${btnClass} action-btn special" onclick="toggleActivo(${u.id}, ${!u.activo})" title="${btnText}">
                                        <i class="bi ${btnIcon}"></i>
                                    </button>
                                    <button type="button" class="btn btn-sm btn-outline-danger action-btn delete" onclick="mostrarModalEliminarUsuario(${u.id}, '${u.username}')" title="Eliminar">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                });
            } else {
                console.log('üì≠ No se encontraron usuarios');
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted py-4">
                            <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                            No se encontraron usuarios con los filtros aplicados
                        </td>
                    </tr>
                `;
            }

            // Renderizar paginación
            if (typeof paginacionUsuarios !== 'undefined' && paginacionUsuarios.render) {
                paginacionUsuarios.render(data.page, data.per_page, data.total);
            }
            console.log(`✅ Usuarios cargados exitosamente`);
        })
        .catch(error => {
            console.error('❌ Error al cargar usuarios:', error);
            mostrarAlerta('Error al cargar usuarios', 'danger');
        });
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
                cargarEstadisticas(); // Actualizar estadísticas
            } else {
                mostrarAlerta(data.error || 'Error al cambiar estado del usuario', 'danger');
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
    const activo = document.getElementById('nuevo-activo').checked;

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
            rol: rol,
            activo: activo
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoUsuario'));
                modal.hide();
                mostrarAlerta('Usuario creado exitosamente', 'success');
                cargarUsuarios(1);
                cargarEstadisticas(); // Actualizar estadísticas
            } else {
                mostrarAlerta(data.error || 'Error al crear usuario', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al crear usuario', 'danger');
        });
}

function editarUsuario(id) {
    // Obtener datos del usuario
    fetch(`/usuarios/api/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const usuario = data.usuario;

                // Llenar el formulario modal
                document.getElementById('editar-id').value = usuario.id;
                document.getElementById('editar-username').value = usuario.username;
                document.getElementById('editar-email').value = usuario.email;
                document.getElementById('editar-nombre').value = usuario.nombre || '';
                document.getElementById('editar-password').value = '';
                document.getElementById('editar-rol').value = usuario.rol;
                document.getElementById('editar-activo').checked = usuario.activo;

                // Mostrar modal
                const modal = new bootstrap.Modal(document.getElementById('modalEditarUsuario'));
                modal.show();
            } else {
                mostrarAlerta('Error al obtener datos del usuario', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al obtener datos del usuario', 'danger');
        });
}

function actualizarUsuario() {
    const id = document.getElementById('editar-id').value;
    const username = document.getElementById('editar-username').value;
    const email = document.getElementById('editar-email').value;
    const nombre = document.getElementById('editar-nombre').value;
    const password = document.getElementById('editar-password').value;
    const rol = document.getElementById('editar-rol').value;
    const activo = document.getElementById('editar-activo').checked;

    if (!username || !email || !rol) {
        mostrarAlerta('Por favor complete todos los campos requeridos', 'warning');
        return;
    }

    const datosActualizacion = {
        username: username,
        email: email,
        nombre: nombre,
        rol: rol,
        activo: activo
    };

    // Solo incluir password si se proporcionó uno nuevo
    if (password && password.trim() !== '') {
        datosActualizacion.password = password;
    }

    fetch(`/usuarios/api/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datosActualizacion)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarUsuario'));
                modal.hide();
                mostrarAlerta('Usuario actualizado exitosamente', 'success');
                cargarUsuarios(currentPage);
                cargarEstadisticas(); // Actualizar estadísticas
            } else {
                mostrarAlerta(data.error || 'Error al actualizar usuario', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al actualizar usuario', 'danger');
        });
}

function mostrarModalEliminarUsuario(id, username) {
    document.getElementById('id-usuario-eliminar').value = id;
    document.getElementById('usuario-a-eliminar').textContent = username;

    const modal = new bootstrap.Modal(document.getElementById('modalEliminarUsuario'));
    modal.show();
}

function confirmarEliminarUsuario() {
    const id = document.getElementById('id-usuario-eliminar').value;

    fetch(`/usuarios/api/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalEliminarUsuario'));
                modal.hide();
                mostrarAlerta('Usuario eliminado exitosamente', 'success');
                cargarUsuarios(currentPage);
                cargarEstadisticas(); // Actualizar estadísticas
            } else {
                mostrarAlerta(data.error || 'Error al eliminar usuario', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar usuario', 'danger');
        });
}

function cargarEstadisticas() {
    fetch('/usuarios/api/estadisticas')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const stats = data.estadisticas;
                document.getElementById('stat-total-usuarios').textContent = stats.total_usuarios || 0;
                document.getElementById('stat-usuarios-activos').textContent = stats.usuarios_activos || 0;
                document.getElementById('stat-administradores').textContent = stats.por_rol?.Administrador || 0;
                document.getElementById('stat-tecnicos').textContent = stats.por_rol?.Técnico || 0;
            }
        })
        .catch(error => {
            console.error('Error al cargar estadísticas:', error);
        });
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
        'success': '✅ √âxito',
        'error': '❌ Error',
        'warning': '‚ö† Advertencia',
        'info': '‚Ñπ Información'
    };
    return titulos[tipo] || 'Información';
}

// Event listeners
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DOM cargado, inicializando usuarios...');

    // Inicializar paginación
    paginacionUsuarios = createPagination('paginacion-usuarios', cargarUsuarios, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true
    });

    // Verificar que los elementos existen
    const elementos = ['filtro-username', 'filtro-email', 'filtro-rol', 'filtro-activo'];
    elementos.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            console.log(`✅ Elemento ${id} encontrado:`, elemento);
        } else {
            console.error(`❌ Elemento ${id} NO encontrado`);
        }
    });

    cargarUsuarios(1);
    cargarEstadisticas();

    // Configurar búsqueda en tiempo real
    configurarBusquedaUsuarios();

    // Inicializar autocompletado después de cargar página
    setTimeout(() => {
        inicializarAutocompletado();
    }, 500);
});

// Configurar búsqueda en tiempo real para usuarios
function configurarBusquedaUsuarios() {
    console.log('🔍 Configurando búsqueda de usuarios...');

    // Campo de filtro por username - usar solo para autocompletado, no eventos directos
    const filtroUsername = document.getElementById('filtro-username');
    if (filtroUsername) {
        console.log('✅ Filtro de username encontrado - será manejado por autocompletado');
    } else {
        console.error('❌ No se encontró el elemento filtro-username');
    }

    // Campo de filtro por email - usar solo para autocompletado, no eventos directos
    const filtroEmail = document.getElementById('filtro-email');
    if (filtroEmail) {
        console.log('✅ Filtro de email encontrado - será manejado por autocompletado');
    } else {
        console.error('❌ No se encontró el elemento filtro-email');
    }

    // Filtros de selección (rol y estado) - estos sí necesitan eventos directos
    const filtroRol = document.getElementById('filtro-rol');
    if (filtroRol) {
        filtroRol.addEventListener('change', function (e) {
            console.log(`🔍 Filtro rol cambiado: "${e.target.value}"`);
            cargarUsuarios(1);
        });
        console.log('✅ Filtro de rol configurado');
    }

    const filtroActivo = document.getElementById('filtro-activo');
    if (filtroActivo) {
        filtroActivo.addEventListener('change', function (e) {
            console.log(`🔍 Filtro activo cambiado: "${e.target.value}"`);
            cargarUsuarios(1);
        });
        console.log('✅ Filtro de activo configurado');
    }

    console.log('✅ Filtros configurados - Autocompletado manejará username y email');
}

// Inicializar autocompletado en formularios de usuarios
function inicializarAutocompletado() {
    console.log('Inicializando autocompletado en usuarios...');

    // Verificar si AutoComplete está disponible
    if (!window.AutoComplete) {
        console.error('❌ AutoComplete no disponible - Verifica que autocomplete.js esté cargado');
        return;
    }
    console.log('✅ AutoComplete disponible');

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
            minChars: 1, // Búsqueda desde el primer carácter
            debounceTime: 250, // Respuesta rápida
            onSelect: (item) => {
                console.log('Usuario seleccionado para filtro:', item);
                cargarUsuarios(1);
            },
            onInput: (value) => {
                console.log('🔍 Input en autocompletado username:', value);
                // Búsqueda en tiempo real mientras escribe
                setTimeout(() => {
                    cargarUsuarios(1);
                }, 100);
            }
        });
        console.log('✅ Autocompletado de username configurado');
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
            minChars: 1, // Búsqueda desde el primer carácter
            debounceTime: 250, // Respuesta rápida
            onSelect: (item) => {
                console.log('Email seleccionado para filtro:', item);
                cargarUsuarios(1);
            },
            onInput: (value) => {
                console.log('🔍 Input en autocompletado email:', value);
                // Búsqueda en tiempo real mientras escribe
                setTimeout(() => {
                    cargarUsuarios(1);
                }, 100);
            }
        });
        console.log('✅ Autocompletado de email configurado');
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

    console.log('✅ Autocompletado inicializado completamente en usuarios');

    // Verificar que los elementos estén siendo "wrapeados" por autocompletado
    setTimeout(() => {
        const wrappers = document.querySelectorAll('.autocomplete-wrapper');
        console.log(`🔍 Elementos de autocompletado encontrados: ${wrappers.length}`);
        wrappers.forEach((wrapper, index) => {
            const input = wrapper.querySelector('input');
            if (input) {
                console.log(`✅ Autocompletado ${index + 1}: ${input.placeholder}`);
            }
        });
    }, 100);
}

// Función para limpiar filtros de usuarios
function limpiarFiltrosUsuarios() {
    console.log('üßπ Limpiando filtros de usuarios...');

    // Limpiar campos de filtro
    const filtros = [
        'filtro-username',
        'filtro-email',
        'filtro-rol',
        'filtro-activo'
    ];

    filtros.forEach(filtroId => {
        const elemento = document.getElementById(filtroId);
        if (elemento) {
            // Usar value para inputs y selectedIndex para selects
            if (elemento.tagName.toLowerCase() === 'select') {
                elemento.selectedIndex = 0;
            } else {
                elemento.value = '';
            }
            console.log(`✅ Filtro ${filtroId} limpiado`);
        }
    });

    // Limpiar también cualquier estado de autocompletado
    const autoCompleteInputs = document.querySelectorAll('.autocomplete-container input');
    autoCompleteInputs.forEach(input => {
        if (input.value) {
            input.value = '';
        }
    });

    // Recargar usuarios sin filtros
    currentPage = 1; // Resetear a la primera página
    cargarUsuarios(1);
    console.log('✅ Filtros limpiados y usuarios recargados');
}

// Prevenir envío de formularios por defecto
document.addEventListener('submit', function (e) {
    e.preventDefault();
});
