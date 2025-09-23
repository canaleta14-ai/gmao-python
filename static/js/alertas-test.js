// PRUEBA DE ALERTAS ULTRA-RÁPIDA
console.log('🚨 Archivo de prueba de alertas cargado');

function loadMaintenanceAlertsTest() {
    console.log('🚨 TEST: Iniciando carga de alertas con timeout de 5 segundos');
    const start = performance.now();

    const container = document.getElementById('maintenanceAlerts');
    if (!container) {
        console.error('❌ Contenedor maintenanceAlerts no encontrado');
        return;
    }

    // Mostrar indicador de carga
    container.innerHTML = `
        <div class="alert alert-primary">
            <i class="bi bi-clock"></i> Cargando alertas de prueba...
            <div class="spinner-border spinner-border-sm ms-2" role="status"></div>
        </div>
    `;

    // Crear controlador de aborto con timeout de 5 segundos
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
        controller.abort();
        const timeoutMs = performance.now() - start;
        console.error(`🚨 TIMEOUT: Alertas canceladas después de ${timeoutMs.toFixed(2)}ms`);
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> <strong>Timeout de Prueba</strong>
                <br>Las alertas tardaron más de 5 segundos
                <br><small>Tiempo: ${timeoutMs.toFixed(0)}ms</small>
                <br><button class="btn btn-sm btn-primary mt-2" onclick="loadMaintenanceAlertsTest()">🔄 Reintentar</button>
            </div>
        `;
    }, 5000); // 5 segundos máximo

    fetch('/api/alertas-mantenimiento', {
        signal: controller.signal,
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            clearTimeout(timeoutId);
            const fetchTime = performance.now() - start;
            console.log(`🚨 Fetch completado en ${fetchTime.toFixed(2)}ms - Status: ${response.status}`);

            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const totalTime = performance.now() - start;
            console.log(`🚨 Alertas procesadas en ${totalTime.toFixed(2)}ms`, data);

            if (data && data.success && data.alertas && Array.isArray(data.alertas)) {
                if (data.alertas.length > 0) {
                    console.log(`🚨 Mostrando ${data.alertas.length} alertas`);

                    // Mostrar alertas de forma simple
                    let alertasHtml = '<div class="row">';
                    data.alertas.forEach((alerta, index) => {
                        alertasHtml += `
                        <div class="col-md-6 mb-3">
                            <div class="alert alert-warning">
                                <h6><i class="bi bi-exclamation-triangle"></i> ${alerta.titulo || 'Alerta ' + (index + 1)}</h6>
                                <p class="mb-1">${alerta.descripcion || 'Sin descripción'}</p>
                                <small class="text-muted">
                                    ${alerta.fecha_creacion ? 'Creada: ' + alerta.fecha_creacion : ''}
                                    ${alerta.prioridad ? ' | Prioridad: ' + alerta.prioridad : ''}
                                </small>
                            </div>
                        </div>
                    `;
                    });
                    alertasHtml += '</div>';

                    container.innerHTML = alertasHtml;
                } else {
                    container.innerHTML = `
                    <div class="alert alert-success">
                        <i class="bi bi-check-circle"></i> No hay alertas de mantenimiento pendientes
                        <br><small>Tiempo de respuesta: ${totalTime.toFixed(0)}ms</small>
                    </div>
                `;
                }
            } else {
                console.warn('🚨 Respuesta sin alertas válidas:', data);
                container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> No se encontraron alertas válidas
                    <br><small>Tiempo de respuesta: ${totalTime.toFixed(0)}ms</small>
                </div>
            `;
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            const errorTime = performance.now() - start;

            if (error.name === 'AbortError') {
                console.error(`🚨 Request abortado después de ${errorTime.toFixed(2)}ms`);
                return; // El timeout ya manejó la UI
            }

            console.error(`🚨 Error en alertas después de ${errorTime.toFixed(2)}ms:`, error);
            container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> <strong>Error al cargar alertas</strong>
                <br>Motivo: ${error.message}
                <br><small>Tiempo: ${errorTime.toFixed(0)}ms</small>
                <br><button class="btn btn-sm btn-primary mt-2" onclick="loadMaintenanceAlertsTest()">🔄 Reintentar</button>
            </div>
        `;
        });
}

// Función para probar directamente el endpoint
function testEndpointDirect() {
    console.log('🧪 TEST DIRECTO: Probando endpoint sin UI');
    const start = performance.now();

    fetch('/api/alertas-mantenimiento')
        .then(response => {
            const fetchTime = performance.now() - start;
            console.log(`🧪 Respuesta recibida en ${fetchTime.toFixed(2)}ms - Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const totalTime = performance.now() - start;
            console.log(`🧪 Total: ${totalTime.toFixed(2)}ms`, data);
        })
        .catch(error => {
            const errorTime = performance.now() - start;
            console.error(`🧪 Error después de ${errorTime.toFixed(2)}ms:`, error);
        });
}