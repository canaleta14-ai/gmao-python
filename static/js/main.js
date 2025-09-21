// ========== CONFIGURACIÓN GLOBAL ==========
const API_BASE_URL = '';
let currentUser = null;
let notifications = [];
let chartInstances = {};
let currentSection = 'dashboard'; // Sección actual

// ========== INICIALIZACIÓN ==========
document.addEventListener('DOMContentLoaded', function () {
    // Cargar elementos críticos primero
    initializeApp();
    setupEventListeners();
    setupNavigationHandlers();

    // Cargar datos de usuario de forma diferida
    setTimeout(() => {
        loadUserInfo();
    }, 100);

    // Verificar notificaciones de forma diferida
    setTimeout(() => {
        checkNotifications();
    }, 500);

    // Configurar auto-refresh después
    setTimeout(() => {
        setupAutoRefresh();
    }, 1000);
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
        const toggler = document.querySelector('.navbar-toggler');
        if (sidebar && sidebar.classList.contains('show') &&
            !sidebar.contains(e.target) && !toggler.contains(e.target)) {
            sidebar.classList.remove('show');
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
                        overlay.remove();
                    });
                }
                overlay.classList.add('show');
            } else {
                if (overlay) {
                    overlay.remove();
                }
            }
        } else {
            // En pantallas grandes, usar clase 'collapsed'
            sidebar.classList.toggle('collapsed');

            // Ajustar el margen del contenido principal
            if (sidebar.classList.contains('collapsed')) {
                mainContent.style.marginLeft = '0';
            } else {
                mainContent.style.marginLeft = '250px';
            }
        }
    }
}

function loadSectionContent(sectionName) {
    // Cargar contenido específico según la sección
    switch (sectionName) {
        case 'dashboard':
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
    // Actualizar dashboard cada 30 segundos
    setInterval(() => {
        if (currentSection === 'dashboard') {
            loadDashboard();
        }
    }, 30000);

    // Verificar notificaciones cada minuto
    setInterval(checkNotifications, 60000);
}

// ========== GESTIÓN DE SESIÓN ==========
function loadUserInfo() {
    fetch('/api/user/info')
        .then(response => response.json())
        .then(data => {
            currentUser = data;
            updateUserInterface(data);
        })
        .catch(error => console.error('Error cargando info de usuario:', error));
}

function updateUserInterface(user) {
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => {
        el.textContent = user.nombre || user.username;
    });
}

// ========== SISTEMA DE NOTIFICACIONES ==========
function checkNotifications() {
    fetch('/api/notificaciones')
        .then(response => response.json())
        .then(data => {
            notifications = data;
            updateNotificationBadge(data.length);
            if (data.length > 0) {
                showNotificationToast(data[0]);
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

function showNotificationToast(notification) {
    const toastHTML = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi bi-bell-fill text-primary me-2"></i>
                <strong class="me-auto">${notification.titulo}</strong>
                <small>${notification.tiempo}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${notification.mensaje}
            </div>
        </div>
    `;

    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// ========== DASHBOARD MEJORADO ==========
function loadDashboard() {
    // Cargar estadísticas
    fetch('/api/estadisticas')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
            createDashboardCharts(data);
        })
        .catch(error => console.error('Error:', error));

    // Cargar órdenes recientes
    loadRecentOrders();

    // Cargar alertas de mantenimiento
    loadMaintenanceAlerts();
}

function updateDashboardStats(data) {
    // Actualizar contadores con animación
    animateCounter('stat-ordenes-activas', data.ordenes_por_estado['En Proceso'] || 0);
    animateCounter('stat-completadas', data.ordenes_por_estado['Completada'] || 0);
    animateCounter('stat-pendientes', data.ordenes_por_estado['Pendiente'] || 0);
    animateCounter('stat-activos', data.total_activos || 0);
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
    // Verificar si Chart.js está disponible
    if (typeof Chart === 'undefined') {
        loadChartJS().then(() => createDashboardCharts(data));
        return;
    }

    // Gráfico de órdenes por día
    createOrdersChart(data);

    // Gráfico de estado de equipos
    createEquipmentChart(data);

    // Gráfico de tendencias
    createTrendsChart(data);
}

function loadChartJS() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = resolve;
        script.onerror = reject;
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
    fetch('/api/alertas-mantenimiento')
        .then(response => response.json())
        .then(alerts => {
            displayMaintenanceAlerts(alerts);
        })
        .catch(error => console.error('Error:', error));
}

function displayMaintenanceAlerts(alerts) {
    const container = document.getElementById('maintenanceAlerts');
    if (!container) return;

    if (alerts.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay alertas de mantenimiento</p>';
        return;
    }

    container.innerHTML = alerts.map(alert => `
        <div class="alert alert-${alert.tipo} alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong>${alert.equipo}:</strong> ${alert.mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `).join('');
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