// Función corregida de loadDashboard
function loadDashboard() {
    console.log('🚀 DASHBOARD - Cargando componentes...');

    // Cargar alertas de mantenimiento inmediatamente
    const alertsContainer = document.getElementById('maintenanceAlerts');
    if (alertsContainer) {
        console.log('📋 Iniciando carga de alertas...');
        if (typeof loadMaintenanceAlertsSimple === 'function') {
            loadMaintenanceAlertsSimple();
        } else {
            console.warn('⚠️ loadMaintenanceAlertsSimple no está definida');
        }
    } else {
        console.warn('⚠️ Contenedor de alertas no encontrado');
    }

    // Cargar estadísticas (no bloquea otras cargas)
    console.log('📊 Iniciando carga de estadísticas...');
    const statsStart = performance.now();
    fetch('/api/estadisticas')
        .then(response => {
            const statsTime = performance.now() - statsStart;
            console.log(`📊 Estadísticas cargadas en ${statsTime.toFixed(2)}ms`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos recibidos:', data);
            updateDashboardStats(data);

            // Cargar gráficos de forma no-bloqueante
            setTimeout(() => {
                console.log('📈 Iniciando carga de gráficos...');
                if (typeof createDashboardChartsWithTimeout === 'function') {
                    createDashboardChartsWithTimeout(data);
                } else {
                    console.warn('⚠️ createDashboardChartsWithTimeout no está definida');
                }
            }, 100);
        })
        .catch(error => {
            const statsTime = performance.now() - statsStart;
            console.error(`❌ Error estadísticas después de ${statsTime.toFixed(2)}ms:`, error);
        });

    // Cargar órdenes recientes (paralelo)
    console.log('📋 Iniciando carga de órdenes recientes...');
    if (typeof loadRecentOrders === 'function') {
        loadRecentOrders();
    } else {
        console.warn('⚠️ loadRecentOrders no está definida');
    }
}