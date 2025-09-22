// ========== CONFIGURACIÓN GLOBAL ==========
const API_BASE_URL = '';
let currentUser = null;
let notifications = [];
let chartInstances = {};
let currentSection = 'dashboard'; // Sección actual

// ========== INICIALIZACIÓN ==========
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DOMContentLoaded - Iniciando aplicación...');
    const appStart = performance.now();

    // Cargar elementos críticos primero
    console.log('⚙️ Iniciando initializeApp...');
    const initStart = performance.now();
    initializeApp();
    console.log(`⚙️ initializeApp completado en ${(performance.now() - initStart).toFixed(2)}ms`);

    console.log('👂 Iniciando setupEventListeners...');
    const listenersStart = performance.now();
    setupEventListeners();
    console.log(`👂 setupEventListeners completado en ${(performance.now() - listenersStart).toFixed(2)}ms`);

    console.log('🧭 Iniciando setupNavigationHandlers...');
    const navStart = performance.now();
    setupNavigationHandlers();
    console.log(`🧭 setupNavigationHandlers completado en ${(performance.now() - navStart).toFixed(2)}ms`);

    // Cargar datos de usuario de forma diferida
    setTimeout(() => {
        console.log('👤 Iniciando loadUserInfo (diferido)...');
        const userStart = performance.now();
        loadUserInfo();
        setTimeout(() => {
            console.log(`👤 loadUserInfo completado en ${(performance.now() - userStart).toFixed(2)}ms`);
        }, 50);
    }, 100);

    // Verificar notificaciones de forma diferida  
    setTimeout(() => {
        console.log('🔔 Iniciando checkNotifications (diferido)...');
        const notifStart = performance.now();
        checkNotifications();
        setTimeout(() => {
            console.log(`🔔 checkNotifications completado en ${(performance.now() - notifStart).toFixed(2)}ms`);
        }, 50);
    }, 500);

    // Configurar auto-refresh después
    setTimeout(() => {
        console.log('🔄 Iniciando setupAutoRefresh (diferido)...');
        const refreshStart = performance.now();
        setupAutoRefresh();
        setTimeout(() => {
            console.log(`🔄 setupAutoRefresh completado en ${(performance.now() - refreshStart).toFixed(2)}ms`);
        }, 50);
    }, 1000);

    const appTime = performance.now() - appStart;
    console.log(`🚀 DOMContentLoaded completado en ${appTime.toFixed(2)}ms`);
});

// Manejar navegación con botones atrás/adelante del navegador
function setupNavigationHandlers() {
    window.addEventListener('hashchange', function () {
        const hash = window.location.hash.substring(1) || 'dashboard';
        // En un sistema multi-página, redirigir en lugar de cambiar secciones
        if (hash && hash !== window.location.pathname.substring(1)) {
            const routeMap = {
                'dashboard': '/',
                'activos': '/activos',
                'proveedores': '/proveedores',
                'ordenes': '/ordenes',
                'preventivo': '/planes',
                'inventario': '/inventario',
                'personal': '/usuarios',
                'reportes': '/reportes'
            };

            const route = routeMap[hash];
            if (route && route !== window.location.pathname) {
                window.location.href = route;
            }
        }
    });
}

function initializeApp() {
    // No llamar showSection en un sistema multi-página
    // const hash = window.location.hash.substring(1) || 'dashboard';
    // showSection(hash);

    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupEventListeners() {
    // Búsqueda en tiempo real para activos
    const searchActivo = document.getElementById('searchActivo');
    if (searchActivo) {
        searchActivo.addEventListener('input', debounce(function () {
            if (typeof filtrarActivos === 'function') {
                filtrarActivos();
            }
        }, 300));
    }

    // Manejar redimensionamiento de ventana para sidebar responsive
    window.addEventListener('resize', function () {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');

        if (window.innerWidth >= 992) {
            // En pantallas grandes, remover clases de móvil
            if (sidebar) {
                sidebar.classList.remove('show');
            }
            if (overlay) {
                overlay.remove();
            }
        }
    });

    // Event listeners para navegación
    document.addEventListener('click', function (e) {
        // Manejar clicks en enlaces de navegación hash
        if (e.target.matches('a[href^="#"]') || e.target.closest('a[href^="#"]')) {
            const link = e.target.matches('a[href^="#"]') ? e.target : e.target.closest('a[href^="#"]');
            const sectionName = link.getAttribute('href').substring(1);
            if (sectionName) {
                // En lugar de showSection, redirigir usando las rutas apropiadas
                const routeMap = {
                    'dashboard': '/',
                    'activos': '/activos',
                    'proveedores': '/proveedores',
                    'ordenes': '/ordenes',
                    'preventivo': '/planes',
                    'inventario': '/inventario',
                    'personal': '/usuarios',
                    'reportes': '/reportes'
                };

                const route = routeMap[sectionName];
                if (route) {
                    e.preventDefault();
                    window.location.href = route;
                }
            }
        }
    });

    // Manejar navegación con botones que tienen data-section
    document.addEventListener('click', function (e) {
        if (e.target.matches('[data-section]') || e.target.closest('[data-section]')) {
            const button = e.target.matches('[data-section]') ? e.target : e.target.closest('[data-section]');
            const sectionName = button.getAttribute('data-section');
            if (sectionName) {
                // Redirigir usando las rutas apropiadas
                const routeMap = {
                    'dashboard': '/',
                    'activos': '/activos',
                    'proveedores': '/proveedores',
                    'ordenes': '/ordenes',
                    'preventivo': '/planes',
                    'inventario': '/inventario',
                    'personal': '/usuarios',
                    'reportes': '/reportes'
                };

                const route = routeMap[sectionName];
                if (route) {
                    e.preventDefault();
                    window.location.href = route;
                }
            }
        }
    });

    // Cerrar sidebar en móvil al hacer click fuera
    document.addEventListener('click', function (e) {
        const sidebar = document.querySelector('.sidebar');
        const toggleButton = document.querySelector('.btn[onclick="toggleSidebar()"]');

        // Solo proceder si el sidebar existe y está visible en móvil
        if (sidebar && toggleButton) {
            // Verificar si estamos en modo móvil (sidebar con clase 'show' o visible)
            const isMobile = window.innerWidth < 992; // Bootstrap lg breakpoint
            const sidebarVisible = sidebar.classList.contains('show') ||
                (isMobile && !sidebar.classList.contains('collapsed'));

            if (sidebarVisible && !sidebar.contains(e.target) && !toggleButton.contains(e.target)) {
                // Ocultar sidebar en móvil
                if (typeof toggleSidebar === 'function') {
                    toggleSidebar();
                } else {
                    sidebar.classList.remove('show');
                }
            }
        }
    });
}

// ========== NAVEGACIÓN ENTRE SECCIONES ==========
function showSection(sectionName) {
    // Esta función ahora solo funciona si realmente existe el elemento en el DOM
    // Se usa para casos específicos donde hay secciones dinámicas en una misma página

    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        // Ocultar todas las secciones de la misma página
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(section => {
            section.style.display = 'none';
        });

        // Mostrar la sección seleccionada
        targetSection.style.display = 'block';

        // Actualizar navegación activa
        updateActiveNavigation(sectionName);

        // Cargar contenido específico de la sección si existe la función
        if (typeof loadSectionContent === 'function') {
            loadSectionContent(sectionName);
        }

        // Actualizar URL sin recargar
        window.location.hash = sectionName;

        // Guardar sección actual
        currentSection = sectionName;
    } else {
        // Si no existe la sección en esta página, redirigir a la ruta apropiada
        console.warn(`Sección '${sectionName}' no encontrada en esta página`);

        const routeMap = {
            'dashboard': '/',
            'activos': '/activos',
            'proveedores': '/proveedores',
            'ordenes': '/ordenes',
            'preventivo': '/planes',
            'inventario': '/inventario',
            'personal': '/usuarios',
            'reportes': '/reportes'
        };

        const route = routeMap[sectionName];
        if (route && route !== window.location.pathname) {
            window.location.href = route;
        }
    }
} function updateActiveNavigation(sectionName) {
    // Remover clase activa de todos los enlaces de navegación
    const navLinks = document.querySelectorAll('.sidebar .nav-link, .navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Agregar clase activa al enlace correspondiente
    const activeLink = document.querySelector(`[href="#${sectionName}"], [data-section="${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// ========== FUNCIONES DE UI ==========

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebar && mainContent) {
        // En dispositivos móviles (menos de 992px)
        const isMobile = window.innerWidth < 992;

        if (isMobile) {
            // En móvil, usar clase 'show' para mostrar/ocultar
            sidebar.classList.toggle('show');

            // Crear o remover overlay
            let overlay = document.querySelector('.sidebar-overlay');
            if (sidebar.classList.contains('show')) {
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.className = 'sidebar-overlay';
                    document.body.appendChild(overlay);

                    // Cerrar sidebar al hacer click en overlay
                    overlay.addEventListener('click', () => {
                        sidebar.classList.remove('show');
                        overlay.classList.remove('show');
                        setTimeout(() => {
                            if (overlay.parentNode) {
                                overlay.remove();
                            }
                        }, 300);
                    });
                }
                // Pequeño delay para activar la animación
                setTimeout(() => {
                    overlay.classList.add('show');
                }, 10);
            } else {
                if (overlay) {
                    overlay.classList.remove('show');
                    setTimeout(() => {
                        if (overlay.parentNode) {
                            overlay.remove();
                        }
                    }, 300);
                }
            }
        } else {
            // En pantallas grandes, usar clase 'collapsed'
            sidebar.classList.toggle('collapsed');
            // El CSS se encarga de los ajustes del main-content
        }
    }
}

function loadSectionContent(sectionName) {
    // Cargar contenido específico según la sección
    switch (sectionName) {
        case 'dashboard':
            console.log('� Cargando dashboard optimizado...');
            if (typeof loadDashboard === 'function') {
                loadDashboard();
            }
            break;
        case 'activos':
            if (typeof cargarActivos === 'function') {
                cargarActivos();
            }
            break;
        case 'ordenes':
            if (typeof cargarOrdenes === 'function') {
                cargarOrdenes();
            }
            break;
        case 'mantenimiento':
            if (typeof cargarMantenimiento === 'function') {
                cargarMantenimiento();
            }
            break;
        case 'reportes':
            if (typeof cargarReportes === 'function') {
                cargarReportes();
            }
            break;
        default:
            console.log(`No hay función de carga específica para la sección: ${sectionName}`);
    }
}

function setupAutoRefresh() {
    console.log('🔄 setupAutoRefresh COMPLETAMENTE DESHABILITADO');

    // AUTO-REFRESH COMPLETAMENTE DESHABILITADO PARA ELIMINAR CUALQUIER INTERFERENCIA
    // NO se ejecutarán recargas automáticas

    /*
    // CÓDIGO DESHABILITADO:
    setInterval(() => {
        if (currentSection === 'dashboard') {
            console.log('🔄 Auto-refresh del dashboard (5 minutos)');
            loadDashboard();
        }
    }, 300000);

    setInterval(() => {
        console.log('🔔 Auto-refresh de notificaciones (10 minutos)');
        checkNotifications();
    }, 600000);
    */
}// ========== GESTIÓN DE SESIÓN Y USUARIO ==========
function loadUserInfo() {
    console.log('👤 INICIO loadUserInfo - Haciendo fetch a /api/user/info...');
    const fetchStart = performance.now();

    // Intentar cargar información real del usuario
    fetch('/api/user/info')
        .then(response => {
            const fetchTime = performance.now() - fetchStart;
            console.log(`👤 Fetch completado en ${fetchTime.toFixed(2)}ms - Status: ${response.status}`);

            if (response.ok) {
                return response.json();
            } else if (response.status === 401) {
                console.log('👤 Usuario no autenticado - Redirigiendo a login...');
                // Usuario no autenticado, redirigir a login
                window.location.href = '/login';
                return null;
            } else {
                throw new Error('Error al obtener información del usuario');
            }
        })
        .then(data => {
            const processStart = performance.now();
            console.log('👤 Procesando datos de usuario...');

            if (data && data.success) {
                currentUser = {
                    id: data.user.id,
                    nombre: data.user.nombre,
                    username: data.user.username,
                    rol: data.user.rol,
                    email: data.user.email,
                    activo: data.user.activo
                };
                updateUserInterface(currentUser);

                const processTime = performance.now() - processStart;
                console.log(`👤 Datos procesados en ${processTime.toFixed(2)}ms`);
            }
        })
        .catch(error => {
            const errorTime = performance.now() - fetchStart;
            console.warn(`👤 Error después de ${errorTime.toFixed(2)}ms:`, error);
            // Usar datos por defecto como fallback
            currentUser = {
                nombre: 'Usuario',
                username: 'usuario',
                rol: 'Usuario',
                email: 'usuario@gmao.com'
            };
            updateUserInterface(currentUser);
        });
}

function updateUserInterface(user) {
    const userNameElements = document.querySelectorAll('.user-name, #current-user');
    userNameElements.forEach(el => {
        el.textContent = user.nombre || user.username;
    });

    // Actualizar información adicional si existen los elementos
    const emailElements = document.querySelectorAll('.user-email');
    emailElements.forEach(el => {
        el.textContent = user.email || '';
    });

    const roleElements = document.querySelectorAll('.user-role');
    roleElements.forEach(el => {
        el.textContent = user.rol || '';
    });
}

// Función para cerrar sesión
function logout() {
    // Mostrar confirmación
    if (!confirm('¿Está seguro que desea cerrar sesión?')) {
        return;
    }

    // Mostrar loading
    showNotificationToast('Cerrando sesión...', 'info');

    // Limpiar datos locales
    currentUser = null;
    notifications = [];

    // Redirigir directamente a logout (más simple y confiable)
    setTimeout(() => {
        window.location.href = '/logout';
    }, 500);
}

// Función para abrir modal de perfil/configuración
function openProfileModal() {
    // Verificar si el modal ya existe
    let modal = document.getElementById('profileModal');

    if (!modal) {
        // Crear el modal dinámicamente
        const modalHTML = `
            <div class="modal fade" id="profileModal" tabindex="-1" aria-labelledby="profileModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="profileModalLabel">
                                <i class="bi bi-person-gear me-2"></i>Configuración de Usuario
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                        </div>
                        <div class="modal-body">
                            <form id="profileForm">
                                <div class="text-center mb-4">
                                    <i class="bi bi-person-circle fs-1 text-primary"></i>
                                    <h6 class="mt-2">${currentUser?.nombre || 'Usuario'}</h6>
                                    <small class="text-muted">${currentUser?.rol || 'Usuario'}</small>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="userName" class="form-label">Nombre</label>
                                    <input type="text" class="form-control" id="userName" 
                                           value="${currentUser?.nombre || ''}" readonly>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="userEmail" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="userEmail" 
                                           value="${currentUser?.email || ''}" readonly>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="userRole" class="form-label">Rol</label>
                                    <input type="text" class="form-control" id="userRole" 
                                           value="${currentUser?.rol || ''}" readonly>
                                </div>
                                
                                <div class="alert alert-info">
                                    <i class="bi bi-info-circle me-2"></i>
                                    Para modificar estos datos, contacte al administrador del sistema.
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                            <button type="button" class="btn btn-primary" onclick="openChangePasswordModal()">
                                <i class="bi bi-key"></i> Cambiar Contraseña
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('profileModal');
    }

    // Mostrar el modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Función para cambiar contraseña
function openChangePasswordModal() {
    // Cerrar modal de perfil primero
    const profileModal = bootstrap.Modal.getInstance(document.getElementById('profileModal'));
    if (profileModal) {
        profileModal.hide();
    }

    // Crear modal de cambio de contraseña
    const modalHTML = `
        <div class="modal fade" id="changePasswordModal" tabindex="-1" aria-labelledby="changePasswordModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="changePasswordModalLabel">
                            <i class="bi bi-key me-2"></i>Cambiar Contraseña
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                    </div>
                    <div class="modal-body">
                        <form id="changePasswordForm">
                            <div class="mb-3">
                                <label for="currentPassword" class="form-label">Contraseña Actual</label>
                                <input type="password" class="form-control" id="currentPassword" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="newPassword" class="form-label">Nueva Contraseña</label>
                                <input type="password" class="form-control" id="newPassword" required minlength="6">
                                <div class="form-text">Mínimo 6 caracteres</div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="confirmPassword" class="form-label">Confirmar Nueva Contraseña</label>
                                <input type="password" class="form-control" id="confirmPassword" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="changePassword()">
                            <i class="bi bi-check-lg"></i> Cambiar Contraseña
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remover modal anterior si existe
    const existingModal = document.getElementById('changePasswordModal');
    if (existingModal) {
        existingModal.remove();
    }

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('changePasswordModal'));
    modal.show();
}

function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validaciones
    if (!currentPassword || !newPassword || !confirmPassword) {
        showNotificationToast('Todos los campos son obligatorios', 'warning');
        return;
    }

    if (newPassword !== confirmPassword) {
        showNotificationToast('Las contraseñas no coinciden', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showNotificationToast('La nueva contraseña debe tener al menos 6 caracteres', 'warning');
        return;
    }

    // Enviar solicitud
    fetch('/api/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotificationToast('Contraseña cambiada exitosamente', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                modal.hide();
            } else {
                showNotificationToast(data.message || 'Error al cambiar contraseña', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotificationToast('Error al cambiar contraseña', 'error');
        });
}

// ========== SISTEMA DE NOTIFICACIONES ==========
function checkNotifications() {
    // TODO: Implementar endpoint /api/notificaciones cuando esté disponible
    // Por ahora inicializamos con array vacío para evitar errores 404
    notifications = [];
    updateNotificationBadge(0);
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

function showNotificationToast(message, type = 'info') {
    // Soporte para ambos formatos: objeto o string
    let notification;
    if (typeof message === 'string') {
        notification = {
            titulo: getTypeTitle(type),
            mensaje: message,
            tipo: type
        };
    } else {
        notification = message;
    }

    // Mapear tipos de notificación a clases de Bootstrap
    const tipoIconMap = {
        'success': { icon: 'bi-check-circle-fill', class: 'text-success', bgClass: 'bg-success' },
        'error': { icon: 'bi-exclamation-triangle-fill', class: 'text-danger', bgClass: 'bg-danger' },
        'warning': { icon: 'bi-exclamation-triangle-fill', class: 'text-warning', bgClass: 'bg-warning' },
        'info': { icon: 'bi-info-circle-fill', class: 'text-info', bgClass: 'bg-info' }
    };

    const tipoConfig = tipoIconMap[notification.tipo] || tipoIconMap['info'];

    // Determinar duración basada en el tipo
    const duracion = notification.tipo === 'error' ? 8000 : 4000;

    const toastHTML = `
        <div class="toast align-items-center border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="${duracion}" data-tipo="${notification.tipo}">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center">
                    <i class="bi ${tipoConfig.icon} ${tipoConfig.class} me-2"></i>
                    <div>
                        <strong>${notification.titulo}</strong><br>
                        <span class="text-muted small">${notification.mensaje}</span>
                    </div>
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duracion
    });

    toast.show();

    // Limpiar toasts antiguos después de que se oculten
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function getTypeTitle(type) {
    const titles = {
        'success': 'Éxito',
        'error': 'Error',
        'warning': 'Advertencia',
        'info': 'Información'
    };
    return titles[type] || 'Notificación';
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// ========== DASHBOARD MEJORADO ==========
function loadDashboard() {
    console.log('� DASHBOARD ULTRA-SIMPLIFICADO - Solo lo esencial');

    // Cargar alertas de mantenimiento inmediatamente (ya confirmado rápido: 10-16ms)
    if (alertsContainer) {
        console.log('🚨 Iniciando carga de alertas (backend confirmado rápido)...');
        loadMaintenanceAlertsSimple();
    }

    // Cargar estadísticas (no bloquea otras cargas)
    console.log('📈 Iniciando carga de estadísticas...');
    const statsStart = performance.now();
    fetch('/api/estadisticas')
        .then(response => {
            const statsTime = performance.now() - statsStart;
            console.log(`📈 Estadísticas cargadas en ${statsTime.toFixed(2)}ms`);
            return response.json();
        })
        .then(data => {
            updateDashboardStats(data);

            // Cargar gráficos de forma no-bloqueante
            setTimeout(() => {
                console.log('📊 Iniciando carga de gráficos...');
                createDashboardChartsWithTimeout(data);
            }, 100);
        })
        .catch(error => {
            const statsTime = performance.now() - statsStart;
            console.error(`❌ Error estadísticas después de ${statsTime.toFixed(2)}ms:`, error);
        });

    // Cargar órdenes recientes (paralelo)
    console.log('📋 Iniciando carga de órdenes recientes...');
    loadRecentOrders();

    // COMENTAR TODO LO DEMÁS TEMPORALMENTE
    console.log('✅ Dashboard simplificado cargado instantáneamente');

    /* CÓDIGO ORIGINAL COMENTADO PARA DEBUGGING:
    
    // Cargar estadísticas (no bloquea otras cargas)
    console.log('📈 Iniciando carga de estadísticas...');
    const statsStart = performance.now();
    fetch('/api/estadisticas')
        .then(response => {
            const statsTime = performance.now() - statsStart;
            console.log(`📈 Estadísticas cargadas en ${statsTime.toFixed(2)}ms`);
            return response.json();
        })
        .then(data => {
            updateDashboardStats(data);
            
            // Cargar gráficos de forma no-bloqueante con timeout
            setTimeout(() => {
                console.log('📊 Iniciando carga de gráficos (no-bloqueante)...');
                createDashboardChartsWithTimeout(data);
            }, 500); // Retraso para no bloquear la UI
        })
        .catch(error => {
            const statsTime = performance.now() - statsStart;
            console.error(`❌ Error estadísticas después de ${statsTime.toFixed(2)}ms:`, error);
        });

    // Cargar órdenes recientes (no bloquea otras cargas)
    console.log('📋 Iniciando carga de órdenes recientes...');
    loadRecentOrders();

    // Cargar alertas de mantenimiento de forma asíncrona (con retraso mínimo)
    setTimeout(() => {
        if (document.getElementById('maintenanceAlerts')) {
            console.log('🚨 Iniciando carga de alertas...');
            loadMaintenanceAlertsSimple();
        }
    }, 100); // Pequeño retraso para no bloquear la UI
    
    const dashboardTime = performance.now() - dashboardStart;
    console.log(`📊 Dashboard setup completado en ${dashboardTime.toFixed(2)}ms`);
    
    */
}// Función simplificada y más robusta
function loadMaintenanceAlertsSimple() {
    console.log('� INICIO: Carga directa de alertas');

    const container = document.getElementById('maintenanceAlerts');
    if (!container) return;

    // Indicador mínimo
    container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div> Cargando...</div>';

    // Petición súper simple - sin timeout, sin AbortController
    fetch('/api/alertas-mantenimiento')
        .then(response => response.json())
        .then(data => {
            console.log('✅ Respuesta recibida:', data);
            if (data.success && data.alertas) {
                displayMaintenanceAlerts(data.alertas);
            } else {
                container.innerHTML = '<div class="alert alert-info">No hay alertas disponibles</div>';
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            container.innerHTML = `
                <div class="alert alert-warning">
                    Error cargando alertas
                    <br><button class="btn btn-sm btn-primary" onclick="loadMaintenanceAlertsSimple()">Reintentar</button>
                </div>
            `;
        });
}

// Función de test para llamar desde la consola del navegador
function testAlertas() {
    console.log('🧪 TEST: Iniciando prueba directa de alertas');
    const start = performance.now();

    fetch('/api/alertas-mantenimiento', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            const fetchTime = performance.now() - start;
            console.log(`🧪 Fetch completado en ${fetchTime.toFixed(2)}ms - Status: ${response.status}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const totalTime = performance.now() - start;
            console.log(`🧪 TOTAL DESDE DASHBOARD: ${totalTime.toFixed(2)}ms`);
            console.log(`🧪 Datos:`, data);
            console.log(`🧪 Alertas: ${data.alertas ? data.alertas.length : 0}`);

            // Resultado visual
            alert(`✅ Test completado en ${totalTime.toFixed(2)}ms\nAlertas: ${data.alertas ? data.alertas.length : 0}`);
        })
        .catch(error => {
            const errorTime = performance.now() - start;
            console.error(`🧪 Error: ${error} después de ${errorTime.toFixed(2)}ms`);
            alert(`❌ Error: ${error.message} (${errorTime.toFixed(2)}ms)`);
        });
}

// DIAGNÓSTICO EXHAUSTIVO - REVISAR TODO
function diagnosticoExhaustivo() {
    console.log('🔍 DIAGNÓSTICO EXHAUSTIVO - Revisando TODO');

    // 1. TODOS los elementos con classes de carga
    console.log('1️⃣ BUSCANDO ELEMENTOS DE CARGA:');
    const loadingSelectors = [
        '.spinner-border', '.spinner-grow', '.loading', '.is-loading',
        '[class*="load"]', '[class*="spin"]', '[class*="wait"]',
        '.fa-spinner', '.fa-circle-o-notch', '.fa-refresh',
        '[data-loading]', '[aria-busy="true"]'
    ];

    loadingSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            console.log(`   ❗ ${selector}: ${elements.length} elementos encontrados`);
            elements.forEach((el, i) => {
                console.log(`      ${i + 1}. ${el.tagName} - Classes: ${el.className}`);
                console.log(`         Visible: ${el.offsetWidth > 0 && el.offsetHeight > 0}`);
                console.log(`         Display: ${getComputedStyle(el).display}`);
                console.log(`         Opacity: ${getComputedStyle(el).opacity}`);
            });
        }
    });

    // 2. Verificar texto que indica carga
    console.log('2️⃣ BUSCANDO TEXTO DE CARGA:');
    const textosLoading = ['cargando', 'loading', 'espera', 'wait', 'procesando'];
    textosLoading.forEach(texto => {
        const xpath = `//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '${texto}')]`;
        const result = document.evaluate(xpath, document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
        if (result.snapshotLength > 0) {
            console.log(`   ❗ Texto "${texto}": ${result.snapshotLength} elementos`);
            for (let i = 0; i < result.snapshotLength; i++) {
                const el = result.snapshotItem(i);
                console.log(`      ${el.tagName}: "${el.textContent.trim()}"`);
            }
        }
    });

    // 3. Verificar atributos aria y data
    console.log('3️⃣ VERIFICANDO ATRIBUTOS:');
    const busyElements = document.querySelectorAll('[aria-busy="true"]');
    const loadingData = document.querySelectorAll('[data-loading="true"]');
    console.log(`   aria-busy="true": ${busyElements.length}`);
    console.log(`   data-loading="true": ${loadingData.length}`);

    // 4. CSS animations activas
    console.log('4️⃣ VERIFICANDO ANIMACIONES CSS:');
    const allElements = document.querySelectorAll('*');
    let animatingElements = 0;
    allElements.forEach(el => {
        const style = getComputedStyle(el);
        if (style.animationName !== 'none' || style.transitionProperty !== 'all') {
            animatingElements++;
        }
    });
    console.log(`   Elementos con animaciones: ${animatingElements}`);

    // 5. Timers y intervals activos
    console.log('5️⃣ VERIFICANDO TIMERS:');
    console.log('   (Nota: No se pueden listar directamente, pero revisaremos el código)');

    // 6. Network requests activos
    console.log('6️⃣ VERIFICANDO NETWORK:');
    if (window.performance && window.performance.getEntriesByType) {
        const resources = window.performance.getEntriesByType('resource');
        const recentRequests = resources.filter(r => Date.now() - r.startTime < 5000);
        console.log(`   Requests recientes (últimos 5s): ${recentRequests.length}`);
    }

    // 7. Estado del DOM
    console.log('7️⃣ ESTADO DEL DOM:');
    console.log(`   readyState: ${document.readyState}`);
    console.log(`   Total elementos: ${document.querySelectorAll('*').length}`);

    // 8. Específico del dashboard
    console.log('8️⃣ DASHBOARD ESPECÍFICO:');
    const dashboardMain = document.querySelector('#dashboard, .dashboard, main');
    if (dashboardMain) {
        console.log(`   Dashboard encontrado: ${dashboardMain.tagName}.${dashboardMain.className}`);
        const loadingInDashboard = dashboardMain.querySelectorAll('.loading, .spinner-border, [class*="load"]');
        console.log(`   Loading en dashboard: ${loadingInDashboard.length}`);
    }

    console.log('🔍 DIAGNÓSTICO EXHAUSTIVO COMPLETADO');
}

// FUNCIÓN DE ELIMINACIÓN RADICAL
function eliminacionRadical() {
    console.log('💥 ELIMINACIÓN RADICAL - Eliminando TODO lo que pueda causar loading');

    // 1. Eliminar TODOS los spinners y loading
    const allLoadingSelectors = [
        '.spinner-border', '.spinner-grow', '.loading', '.is-loading',
        '[class*="load"]', '[class*="spin"]', '[class*="wait"]',
        '.fa-spinner', '.fa-circle-o-notch', '.fa-refresh'
    ];

    let removedCount = 0;
    allLoadingSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            console.log(`🗑️ Eliminando: ${el.tagName}.${el.className}`);
            el.remove();
            removedCount++;
        });
    });

    // 2. Limpiar atributos
    document.querySelectorAll('[aria-busy="true"]').forEach(el => {
        el.setAttribute('aria-busy', 'false');
        console.log('🔧 aria-busy limpiado');
    });

    document.querySelectorAll('[data-loading="true"]').forEach(el => {
        el.setAttribute('data-loading', 'false');
        console.log('🔧 data-loading limpiado');
    });

    // 3. Detener animaciones CSS
    const style = document.createElement('style');
    style.textContent = `
        * {
            animation: none !important;
            transition: none !important;
        }
        .spinner-border, .spinner-grow, .loading {
            display: none !important;
        }
    `;
    document.head.appendChild(style);
    console.log('🎨 Animaciones CSS deshabilitadas');

    // 4. Forzar contenido del dashboard
    const alertsContainer = document.getElementById('maintenanceAlerts');
    if (alertsContainer) {
        console.log('🚨 Forzando contenido de alertas...');
        loadMaintenanceAlertsSimple();
    }

    // 5. Limpiar Chart.js
    if (typeof Chart === 'undefined') {
        window.createDashboardCharts = () => console.log('📊 Charts omitidos');
        window.createDashboardChartsWithTimeout = () => console.log('📊 Charts omitidos');
    }

    console.log(`💥 ELIMINACIÓN RADICAL COMPLETADA - ${removedCount} elementos eliminados`);
}

// DIAGNÓSTICO PROFUNDO - ¿Qué está cargando?
function diagnosticarCargaContinua() {
    console.log('🔍 DIAGNÓSTICO PROFUNDO: ¿Qué sigue cargando?');

    // 1. Verificar indicadores de carga en el DOM
    const spinners = document.querySelectorAll('.spinner-border, .loading, [class*="load"]');
    console.log(`🔄 Spinners/Indicadores encontrados: ${spinners.length}`);
    spinners.forEach((spinner, i) => {
        console.log(`   ${i + 1}. ${spinner.className} - Visible: ${spinner.style.display !== 'none'}`);
    });

    // 2. Verificar requests pendientes
    const xhrActive = window.XMLHttpRequest.toString().includes('open');
    console.log(`📡 Requests XHR activos: ${xhrActive}`);

    // 3. Verificar timers activos
    console.log('⏰ Verificando timers/intervals...');

    // 4. Verificar estado de elementos clave
    const alertsContainer = document.getElementById('maintenanceAlerts');
    if (alertsContainer) {
        console.log(`🚨 Contenedor alertas HTML: ${alertsContainer.innerHTML.substring(0, 100)}...`);
    }

    const dashboardContent = document.querySelector('#dashboard-content, .dashboard, main');
    if (dashboardContent) {
        console.log(`📊 Dashboard content encontrado: ${dashboardContent.tagName}`);
        console.log(`📊 Dashboard classes: ${dashboardContent.className}`);
    }

    // 5. Verificar si hay overlays o modales
    const overlays = document.querySelectorAll('.modal, .overlay, .backdrop');
    console.log(`🎭 Overlays/Modales: ${overlays.length}`);

    // 6. Estado de la página
    console.log(`📄 Document ready state: ${document.readyState}`);
    console.log(`🖼️ Imágenes pendientes: ${document.images.length}`);

    // 7. Verificar Chart.js si está cargado
    if (typeof Chart !== 'undefined') {
        console.log('📊 Chart.js está cargado');
    } else {
        console.log('❌ Chart.js NO está cargado (¿esperando carga?)');
    }

    // 8. Performance del navegador
    const timing = performance.timing;
    const loadTime = timing.loadEventEnd - timing.navigationStart;
    console.log(`⚡ Tiempo de carga página: ${loadTime}ms`);

    console.log('🔍 Diagnóstico completo terminado');
}

// Función para forzar limpieza de indicadores de carga
function limpiarIndicadoresCarga() {
    console.log('🧹 LIMPIANDO indicadores de carga...');

    // Remover todos los spinners
    const spinners = document.querySelectorAll('.spinner-border, .loading, [class*="load"]');
    console.log(`🗑️ Removiendo ${spinners.length} spinners...`);
    spinners.forEach((spinner, i) => {
        console.log(`   Removiendo: ${spinner.className}`);
        spinner.remove();
    });

    // Limpiar clases de carga
    const elementsWithLoading = document.querySelectorAll('[class*="loading"]');
    elementsWithLoading.forEach(el => {
        el.classList.remove('loading', 'is-loading');
    });

    // Verificar y limpiar alertas container
    const alertsContainer = document.getElementById('maintenanceAlerts');
    if (alertsContainer) {
        console.log('🚨 Forzando carga de alertas...');
        alertsContainer.innerHTML = '<div class="alert alert-info">Cargando alertas...</div>';
        loadMaintenanceAlertsSimple();
    }

    // Limpiar cualquier loading en el dashboard
    const dashboardElements = document.querySelectorAll('[class*="dashboard"] .spinner-border, [class*="dashboard"] .loading');
    dashboardElements.forEach(el => {
        console.log('📊 Removiendo loading del dashboard');
        el.remove();
    });

    console.log('✅ Limpieza completada');
}

// Función para arreglar Chart.js
function arreglarChartJS() {
    console.log('📊 ARREGLANDO Chart.js...');

    if (typeof Chart === 'undefined') {
        console.log('📊 Chart.js no está disponible - eliminando dependencias...');

        // Deshabilitar cualquier función que espere Chart.js
        window.createDashboardChartsWithTimeout = function () {
            console.log('📊 Charts deshabilitados - Chart.js no disponible');
        };

        window.createDashboardCharts = function () {
            console.log('📊 Charts deshabilitados - Chart.js no disponible');
        };

        console.log('📊 Chart.js dependencies deshabilitadas');
    } else {
        console.log('✅ Chart.js está disponible');
    }
}

// Función de limpieza total
function limpiezaTotal() {
    console.log('🧽 LIMPIEZA TOTAL del dashboard...');

    limpiarIndicadoresCarga();
    arreglarChartJS();

    // Forzar restauración del dashboard
    setTimeout(() => {
        console.log('🔄 Forzando restauración del dashboard...');
        restaurarDashboard();
    }, 500);

    console.log('✅ Limpieza total completada');
}// Función para restaurar dashboard completo
function restaurarDashboard() {
    console.log('🔄 RESTAURANDO DASHBOARD - Backend confirmado rápido');

    // Cargar alertas inmediatamente
    const alertsContainer = document.getElementById('maintenanceAlerts');
    if (alertsContainer) {
        console.log('🚨 Cargando alertas (backend: 10-16ms)...');
        loadMaintenanceAlertsSimple();
    }

    // Cargar estadísticas
    console.log('📈 Cargando estadísticas...');
    fetch('/api/estadisticas')
        .then(response => response.json())
        .then(data => {
            console.log('📈 Estadísticas cargadas:', data);
            updateDashboardStats(data);
        })
        .catch(error => console.error('❌ Error estadísticas:', error));

    // Cargar órdenes
    console.log('📋 Cargando órdenes...');
    loadRecentOrders();

    console.log('✅ Dashboard restaurado completamente');
}

// Función para cargar alertas en el dashboard actual
function cargarAlertasAhora() {
    console.log('🚀 EJECUTANDO: loadMaintenanceAlertsSimple() directamente');
    if (typeof loadMaintenanceAlertsSimple === 'function') {
        loadMaintenanceAlertsSimple();
    } else {
        console.error('❌ loadMaintenanceAlertsSimple no encontrada');
    }
}

// Función adicional de test simple
function testAlertasSimple() {
    console.log('🧪 TEST SIMPLE: Probando endpoint de alertas');
    const start = performance.now();

    fetch('/api/alertas-mantenimiento')
        .then(response => {
            const time = performance.now() - start;
            console.log(`⏱️ Tiempo de respuesta: ${time.toFixed(2)}ms`);
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos recibidos:', data);
            console.log('✅ TEST COMPLETADO - La API funciona correctamente');
        })
        .catch(error => {
            console.error('❌ TEST FALLÓ:', error);
        });
}

// Función de diagnóstico completo del dashboard
function diagnosticoDashboard() {
    console.log('🚨 DIAGNÓSTICO COMPLETO: Midiendo todos los endpoints del dashboard');

    const endpoints = [
        '/api/estadisticas',
        '/api/alertas-mantenimiento',
        '/ordenes/api?limit=5'
    ];

    endpoints.forEach((endpoint, index) => {
        const start = performance.now();
        console.log(`🔍 ${index + 1}. Probando: ${endpoint}`);

        fetch(endpoint)
            .then(response => {
                const time = performance.now() - start;
                console.log(`⏱️ ${endpoint}: ${time.toFixed(2)}ms - Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log(`📊 ${endpoint}: Datos recibidos exitosamente`);
                if (endpoint.includes('estadisticas')) {
                    console.log('   - Estadísticas:', Object.keys(data || {}).length, 'propiedades');
                } else if (endpoint.includes('alertas')) {
                    console.log('   - Alertas:', data?.total || 0, 'alertas');
                } else if (endpoint.includes('ordenes')) {
                    console.log('   - Órdenes:', data?.length || 0, 'órdenes');
                }
            })
            .catch(error => {
                const time = performance.now() - start;
                console.error(`❌ ${endpoint}: ERROR después de ${time.toFixed(2)}ms -`, error);
            });
    });
}// Función mejorada con sistema de fallback
function loadMaintenanceAlertsWithFallback() {
    console.log('🔄 Iniciando carga de alertas con sistema de fallback');

    // Intentar carga normal primero
    loadMaintenanceAlerts();

    // Si después de 4 segundos no se ha cargado, mostrar mensaje especial
    setTimeout(() => {
        const container = document.getElementById('maintenanceAlerts');
        if (container && container.innerHTML.includes('Cargando alertas de mantenimiento')) {
            console.warn('⚠️ Fallback activado: Las alertas están tardando más de lo esperado');
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong>Las alertas están tardando en cargar...</strong>
                    <br><small class="text-muted">Si el problema persiste, puede haber un problema con la base de datos.</small>
                    <br><button class="btn btn-sm btn-primary mt-2" onclick="loadMaintenanceAlertsSimple()">
                        <i class="bi bi-arrow-clockwise"></i> Forzar nueva carga
                    </button>
                    <button class="btn btn-sm btn-outline-secondary mt-2 ms-2" onclick="skipAlerts()">
                        <i class="bi bi-skip-forward"></i> Continuar sin alertas
                    </button>
                </div>
            `;
        }
    }, 4000);
}

function loadRecentOrders() {
    console.log('📋 Cargando órdenes recientes...');
    const ordersStart = performance.now();

    fetch('/ordenes/api?limit=5')
        .then(response => {
            const ordersTime = performance.now() - ordersStart;
            console.log(`📋 Respuesta órdenes recibida en ${ordersTime.toFixed(2)}ms`);
            return response.json();
        })
        .then(ordenes => {
            const ordersTime = performance.now() - ordersStart;
            console.log(`📋 Órdenes procesadas en ${ordersTime.toFixed(2)}ms - ${ordenes?.length || 0} órdenes`);

            const tbody = document.getElementById('ordenes-recientes-tbody');
            if (!tbody) return;

            tbody.innerHTML = '';

            if (!ordenes || ordenes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No hay órdenes recientes</td></tr>';
                return;
            }

            // Tomar solo las 5 más recientes
            const ordenesRecientes = ordenes.slice(0, 5);

            ordenesRecientes.forEach(orden => {
                const row = document.createElement('tr');

                // Determinar clase de prioridad
                let prioridadClass = 'bg-secondary';
                switch (orden.prioridad) {
                    case 'Crítica': prioridadClass = 'bg-danger'; break;
                    case 'Alta': prioridadClass = 'bg-warning text-dark'; break;
                    case 'Media': prioridadClass = 'bg-info'; break;
                    case 'Baja': prioridadClass = 'bg-secondary'; break;
                }

                // Determinar clase de estado
                let estadoClass = 'bg-secondary';
                switch (orden.estado) {
                    case 'Pendiente': estadoClass = 'bg-warning text-dark'; break;
                    case 'En Proceso': estadoClass = 'bg-info'; break;
                    case 'Completada': estadoClass = 'bg-success'; break;
                    case 'Cancelada': estadoClass = 'bg-danger'; break;
                }

                row.innerHTML = `
                    <td><strong>#${orden.id}</strong></td>
                    <td>${orden.activo_nombre || 'No asignado'}</td>
                    <td>${orden.tipo || 'N/A'}</td>
                    <td><span class="badge ${prioridadClass}">${orden.prioridad || 'N/A'}</span></td>
                    <td><span class="badge ${estadoClass}">${orden.estado || 'N/A'}</span></td>
                    <td>${orden.tecnico_nombre || 'Sin asignar'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="verDetalleOrden(${orden.id})" title="Ver detalles">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                `;

                tbody.appendChild(row);
            });
        })
        .catch(error => {
            const ordersTime = performance.now() - ordersStart;
            console.error(`❌ Error órdenes después de ${ordersTime.toFixed(2)}ms:`, error);
            const tbody = document.getElementById('ordenes-recientes-tbody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Error al cargar órdenes</td></tr>';
            }
        });
}

function verDetalleOrden(ordenId) {
    // Redirigir a la página de órdenes con foco en esa orden específica
    window.location.href = `/ordenes/?orden=${ordenId}`;
}

function updateDashboardStats(data) {
    console.log('📈 Iniciando updateDashboardStats...');
    const statsStart = performance.now();

    // Actualizar contadores con animación
    animateCounter('stat-ordenes-activas', data.ordenes_por_estado['En Proceso'] || 0);
    animateCounter('stat-completadas', data.ordenes_por_estado['Completada'] || 0);
    animateCounter('stat-pendientes', data.ordenes_por_estado['Pendiente'] || 0);
    animateCounter('stat-activos', data.total_activos || 0);

    const statsTime = performance.now() - statsStart;
    console.log(`📈 updateDashboardStats completado en ${statsTime.toFixed(2)}ms`);
}

function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const startValue = parseInt(element.textContent) || 0;
    const duration = 1000;
    const step = (targetValue - startValue) / (duration / 16);
    let current = startValue;

    const timer = setInterval(() => {
        current += step;
        if ((step > 0 && current >= targetValue) || (step < 0 && current <= targetValue)) {
            element.textContent = targetValue;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

function createDashboardCharts(data) {
    console.log('📊 Iniciando createDashboardCharts...');
    const chartsStart = performance.now();

    // Verificar si Chart.js está disponible
    if (typeof Chart === 'undefined') {
        console.log('⚠️ Chart.js no está disponible, cargando desde CDN...');
        loadChartJS().then(() => {
            const chartsTime = performance.now() - chartsStart;
            console.log(`📊 Chart.js cargado en ${chartsTime.toFixed(2)}ms, creando gráficos...`);
            createDashboardCharts(data);
        }).catch(error => {
            const chartsTime = performance.now() - chartsStart;
            console.error(`❌ Error cargando Chart.js después de ${chartsTime.toFixed(2)}ms:`, error);
        });
        return;
    }

    // Gráfico de órdenes por día
    createOrdersChart(data);

    // Gráfico de estado de equipos
    createEquipmentChart(data);

    // Gráfico de tendencias
    createTrendsChart(data);

    const chartsTime = performance.now() - chartsStart;
    console.log(`📊 createDashboardCharts completado en ${chartsTime.toFixed(2)}ms`);
}

// Función de gráficos con timeout para evitar bloqueos
function createDashboardChartsWithTimeout(data) {
    console.log('📊 Iniciando carga de gráficos con timeout...');

    // Timeout de 5 segundos para la carga de Chart.js
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Timeout cargando gráficos')), 5000);
    });

    // Si Chart.js ya está disponible, usarlo directamente
    if (typeof Chart !== 'undefined') {
        console.log('📊 Chart.js ya disponible, creando gráficos...');
        createDashboardCharts(data);
        return;
    }

    // Cargar Chart.js con timeout
    Promise.race([
        loadChartJS(),
        timeoutPromise
    ])
        .then(() => {
            console.log('📊 Chart.js cargado, creando gráficos...');
            createDashboardCharts(data);
        })
        .catch(error => {
            console.warn('⚠️ No se pudieron cargar los gráficos:', error.message);
            // Mostrar mensaje en lugar de gráficos
            showChartsPlaceholder();
        });
}

// Mostrar placeholder si los gráficos no se pueden cargar
function showChartsPlaceholder() {
    const chartsContainers = ['ordersChart', 'equipmentChart', 'trendsChart'];

    chartsContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container && container.parentElement) {
            container.parentElement.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-graph-up" style="font-size: 2rem;"></i>
                    <p class="mt-2">Gráficos no disponibles</p>
                    <small>Los gráficos no se pudieron cargar desde el CDN</small>
                </div>
            `;
        }
    });
}

function loadChartJS() {
    console.log('🌐 Cargando Chart.js desde CDN...');
    const cdnStart = performance.now();

    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = () => {
            const cdnTime = performance.now() - cdnStart;
            console.log(`✅ Chart.js cargado exitosamente en ${cdnTime.toFixed(2)}ms`);
            resolve();
        };
        script.onerror = (error) => {
            const cdnTime = performance.now() - cdnStart;
            console.error(`❌ Error cargando Chart.js después de ${cdnTime.toFixed(2)}ms:`, error);
            reject(error);
        };
        document.head.appendChild(script);
    });
}

function createOrdersChart(data) {
    const ctx = document.getElementById('ordersChart');
    if (!ctx) return;

    // Destruir gráfico anterior si existe
    if (chartInstances.orders) {
        chartInstances.orders.destroy();
    }

    chartInstances.orders = new Chart(ctx, {
        type: 'line',
        data: {
            labels: getLast7Days(),
            datasets: [{
                label: 'Órdenes Completadas',
                data: [12, 19, 3, 5, 2, 3, 7],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }, {
                label: 'Órdenes Creadas',
                data: [5, 10, 15, 8, 12, 7, 9],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createEquipmentChart(data) {
    const ctx = document.getElementById('equipmentChart');
    if (!ctx) return;

    if (chartInstances.equipment) {
        chartInstances.equipment.destroy();
    }

    chartInstances.equipment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.activos_por_estado || {}),
            datasets: [{
                data: Object.values(data.activos_por_estado || {}),
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

function createTrendsChart(data) {
    const ctx = document.getElementById('trendsChart');
    if (!ctx) return;

    if (chartInstances.trends) {
        chartInstances.trends.destroy();
    }

    chartInstances.trends = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
            datasets: [{
                label: 'MTBF (horas)',
                data: [720, 680, 740, 780, 820, 850],
                backgroundColor: 'rgba(54, 162, 235, 0.8)'
            }, {
                label: 'MTTR (horas)',
                data: [4.5, 4.2, 3.8, 3.5, 3.2, 3.0],
                backgroundColor: 'rgba(255, 99, 132, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

function getLast7Days() {
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric' }));
    }
    return days;
}

function loadMaintenanceAlerts() {
    // Solo cargar alertas si estamos en la página del dashboard
    const container = document.getElementById('maintenanceAlerts');
    if (!container) {
        // Salir silenciosamente si no estamos en el dashboard
        return;
    }

    console.log('🔍 Cargando alertas de mantenimiento...');

    // Crear un AbortController para timeout más agresivo
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        console.warn('⏰ Timeout de 3 segundos alcanzado, abortando petición de alertas');
        controller.abort();
    }, 3000); // Timeout reducido a 3 segundos

    fetch('/api/alertas-mantenimiento', {
        signal: controller.signal,
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
        .then(response => {
            clearTimeout(timeoutId);
            console.log('📡 Respuesta recibida:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos de alertas:', data);
            if (data.success) {
                console.log(`✅ Cargando ${data.alertas?.length || 0} alertas`);
                displayMaintenanceAlerts(data.alertas);
            } else {
                console.warn('⚠️ Error en respuesta de alertas:', data.error);
                displayMaintenanceAlerts([]); // Mostrar contenedor vacío
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            const container = document.getElementById('maintenanceAlerts');

            if (error.name === 'AbortError') {
                console.error('⏱️ Timeout cargando alertas de mantenimiento (3 segundos)');
                if (container) {
                    container.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="bi bi-hourglass-split me-2"></i>
                            <strong>Tiempo agotado:</strong> Las alertas tardaron más de 3 segundos en cargar.
                            <br><small class="text-muted">Esto puede indicar un problema con la base de datos o la red.</small>
                            <br><button class="btn btn-sm btn-outline-danger mt-2" onclick="loadMaintenanceAlerts()">
                                <i class="bi bi-arrow-clockwise"></i> Reintentar carga de alertas
                            </button>
                        </div>
                    `;
                }
            } else {
                console.error('❌ Error cargando alertas de mantenimiento:', error);
                if (container) {
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-triangle me-2"></i>
                            Error al cargar alertas: ${error.message}
                            <br><button class="btn btn-sm btn-outline-primary mt-2" onclick="loadMaintenanceAlerts()">
                                <i class="bi bi-arrow-clockwise"></i> Reintentar
                            </button>
                        </div>
                    `;
                }
            }
        });
}

// Función para saltar alertas en caso de problemas persistentes
function skipAlerts() {
    console.log('⏭️ Saltando carga de alertas por solicitud del usuario');
    const container = document.getElementById('maintenanceAlerts');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-light">
                <i class="bi bi-info-circle me-2"></i>
                Alertas omitidas por el usuario.
                <br><button class="btn btn-sm btn-outline-primary mt-1" onclick="loadMaintenanceAlertsSimple()">
                    <i class="bi bi-arrow-clockwise"></i> Cargar alertas
                </button>
            </div>
        `;
    }
} function displayMaintenanceAlerts(alerts) {
    const container = document.getElementById('maintenanceAlerts');
    if (!container) {
        console.warn('⚠️ Contenedor maintenanceAlerts no encontrado');
        return;
    }

    console.log('🎨 Renderizando alertas:', alerts?.length || 0);

    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                No hay alertas de mantenimiento pendientes
            </div>
        `;
        console.log('ℹ️ No hay alertas para mostrar');
        return;
    }

    const alertHTML = alerts.map(alert => {
        const iconClass = alert.tipo === 'vencido' ? 'bi-exclamation-triangle' : 'bi-clock';
        const alertClass = alert.prioridad === 'alta' ? 'danger' :
            alert.prioridad === 'media' ? 'warning' : 'info';

        const fechaInfo = alert.tipo === 'vencido' ?
            `Vencido hace ${alert.dias_vencido} día${alert.dias_vencido !== 1 ? 's' : ''}` :
            `Vence en ${alert.dias_restantes} día${alert.dias_restantes !== 1 ? 's' : ''}`;

        return `
            <div class="alert alert-${alertClass} alert-dismissible fade show mb-2" role="alert">
                <i class="${iconClass} me-2"></i>
                <div>
                    <strong>${alert.titulo}</strong><br>
                    <small class="text-muted">
                        ${alert.activo} - ${fechaInfo}
                    </small>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }).join('');

    container.innerHTML = alertHTML;
    console.log('✅ Alertas renderizadas exitosamente');
}

// ========== GESTIÓN DE ACTIVOS MEJORADA ==========
class ActivosManager {
    constructor() {
        this.activos = [];
        this.filteredActivos = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
    }

    async load() {
        try {
            const response = await fetch('/api/activos');
            this.activos = await response.json();
            this.filteredActivos = [...this.activos];
            this.render();
        } catch (error) {
            console.error('Error cargando activos:', error);
            showAlert('Error al cargar activos', 'danger');
        }
    }

    filter(searchTerm = '', tipo = '', ubicacion = '', estado = '') {
        this.filteredActivos = this.activos.filter(activo => {
            const matchSearch = !searchTerm ||
                activo.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                activo.codigo.toLowerCase().includes(searchTerm.toLowerCase());
            const matchTipo = !tipo || activo.tipo === tipo;
            const matchUbicacion = !ubicacion || activo.ubicacion === ubicacion;
            const matchEstado = !estado || activo.estado === estado;

            return matchSearch && matchTipo && matchUbicacion && matchEstado;
        });

        this.currentPage = 1;
        this.render();
    }

    render() {
        const tbody = document.getElementById('activosTableBody');
        if (!tbody) return;

        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const pageActivos = this.filteredActivos.slice(start, end);

        tbody.innerHTML = pageActivos.map(activo => `
            <tr>
                <td>${activo.codigo}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <i class="bi bi-cpu text-primary me-2"></i>
                        ${activo.nombre}
                    </div>
                </td>
                <td><span class="badge bg-secondary">${activo.tipo}</span></td>
                <td><i class="bi bi-geo-alt me-1"></i>${activo.ubicacion}</td>
                <td>${this.getEstadoBadge(activo.estado)}</td>
                <td>${activo.ultimo_mantenimiento || 'N/A'}</td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-info" onclick="viewActivo(${activo.id})"
                                data-bs-toggle="tooltip" title="Ver detalles">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="editActivo(${activo.id})"
                                data-bs-toggle="tooltip" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-primary" onclick="showActivoHistory(${activo.id})"
                                data-bs-toggle="tooltip" title="Historial">
                            <i class="bi bi-clock-history"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="createMaintenanceOrder(${activo.id})"
                                data-bs-toggle="tooltip" title="Crear orden">
                            <i class="bi bi-wrench"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        this.renderPagination();
        this.updateStats();
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredActivos.length / this.itemsPerPage);
        const paginationContainer = document.getElementById('activosPagination');
        if (!paginationContainer) return;

        let html = `
            <nav>
                <ul class="pagination justify-content-center">
                    <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                        <a class="page-link" href="#" onclick="activosManager.goToPage(${this.currentPage - 1})">
                            Anterior
                        </a>
                    </li>
        `;

        for (let i = 1; i <= totalPages; i++) {
            html += `
                <li class="page-item ${this.currentPage === i ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="activosManager.goToPage(${i})">${i}</a>
                </li>
            `;
        }

        html += `
                    <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                        <a class="page-link" href="#" onclick="activosManager.goToPage(${this.currentPage + 1})">
                            Siguiente
                        </a>
                    </li>
                </ul>
            </nav>
        `;

        return html;
    }
}

// ========== UTILIDADES ==========
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

// Función mejorada para descargar archivos CSV con opciones
async function descargarCSVMejorado(url, nombrePorDefecto, tipo = 'CSV') {
    try {
        // Mostrar modal de configuración de descarga
        const configuracion = await mostrarModalDescargaCSV(nombrePorDefecto, tipo);
        if (!configuracion) return; // Usuario canceló

        mostrarCargando(true);

        // Realizar fetch
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const blob = await response.blob();

        // Intentar usar File System Access API si está disponible (Chrome/Edge modernos)
        if ('showSaveFilePicker' in window) {
            try {
                const fileHandle = await window.showSaveFilePicker({
                    suggestedName: configuracion.nombre,
                    types: [{
                        description: `Archivos ${tipo}`,
                        accept: {
                            'text/csv': ['.csv'],
                            'application/vnd.ms-excel': ['.csv']
                        }
                    }]
                });

                const writable = await fileHandle.createWritable();
                await writable.write(blob);
                await writable.close();

                mostrarMensaje(`Archivo ${tipo} guardado exitosamente en la ubicación seleccionada`, 'success');
                return;
            } catch (err) {
                if (err.name !== 'AbortError') {
                    console.warn('Error con File System Access API, usando descarga tradicional:', err);
                }
                // Si el usuario cancela o hay error, continuar con descarga tradicional
            }
        }

        // Descarga tradicional como fallback
        const url_blob = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url_blob;
        a.download = configuracion.nombre;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();

        // Limpiar
        window.URL.revokeObjectURL(url_blob);
        document.body.removeChild(a);

        mostrarMensaje(`Archivo ${tipo} descargado exitosamente`, 'success');

    } catch (error) {
        console.error('Error al descargar archivo:', error);
        mostrarMensaje(`Error al descargar archivo ${tipo}: ${error.message}`, 'danger');
    } finally {
        mostrarCargando(false);
    }
}

// Modal para configurar descarga de CSV
function mostrarModalDescargaCSV(nombrePorDefecto, tipo = 'CSV') {
    return new Promise((resolve) => {
        const modalId = 'modalDescargaCSV';

        // Remover modal anterior si existe
        const modalExistente = document.getElementById(modalId);
        if (modalExistente) {
            modalExistente.remove();
        }

        const fechaHoy = new Date().toISOString().split('T')[0];
        const nombreSugerido = nombrePorDefecto.replace(/\{fecha\}/g, fechaHoy);

        const modalHTML = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">
                                <i class="bi bi-download me-2"></i>Configurar Descarga ${tipo}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                        </div>
                        <div class="modal-body">
                            <form id="formDescargaCSV">
                                <div class="mb-3">
                                    <label for="nombreArchivo" class="form-label">Nombre del archivo:</label>
                                    <div class="input-group">
                                        <input type="text" class="form-control" id="nombreArchivo" 
                                               value="${nombreSugerido}" required>
                                        <span class="input-group-text">.csv</span>
                                    </div>
                                    <div class="form-text">
                                        Puede usar <code>{fecha}</code> para incluir la fecha actual
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="incluirFecha" 
                                               ${nombreSugerido.includes(fechaHoy) ? 'checked' : ''}>
                                        <label class="form-check-label" for="incluirFecha">
                                            Incluir fecha en el nombre
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="alert alert-info">
                                    <i class="bi bi-info-circle me-2"></i>
                                    ${window.showSaveFilePicker ?
                'Su navegador permite elegir la ubicación de descarga.' :
                'El archivo se descargará en su carpeta de descargas predeterminada.'}
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" id="btnConfirmarDescarga">
                                <i class="bi bi-download me-1"></i>Descargar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        const modal = new bootstrap.Modal(document.getElementById(modalId));
        const inputNombre = document.getElementById('nombreArchivo');
        const checkboxFecha = document.getElementById('incluirFecha');
        const btnConfirmar = document.getElementById('btnConfirmarDescarga');

        // Event listeners
        checkboxFecha.addEventListener('change', function () {
            const nombreBase = inputNombre.value.replace(`_${fechaHoy}`, '').replace(fechaHoy, '');
            if (this.checked) {
                if (!inputNombre.value.includes(fechaHoy)) {
                    inputNombre.value = `${nombreBase}_${fechaHoy}`;
                }
            } else {
                inputNombre.value = nombreBase.replace(/^_|_$/, '');
            }
        });

        btnConfirmar.addEventListener('click', function () {
            const nombre = inputNombre.value.trim();
            if (nombre) {
                modal.hide();
                resolve({ nombre: nombre + '.csv' });
            } else {
                inputNombre.classList.add('is-invalid');
            }
        });

        // Resolver con null si se cancela
        document.getElementById(modalId).addEventListener('hidden.bs.modal', function () {
            this.remove();
            resolve(null);
        });

        modal.show();
        inputNombre.focus();
        inputNombre.select();
    });
}