// Función de test súper simple
function testDashboardSimple() {
    console.log('🧪 TEST: Dashboard súper simple');

    // Solo cambiar contenido del contenedor de alertas
    const container = document.getElementById('maintenanceAlerts');
    if (container) {
        container.innerHTML = '<div class="alert alert-success">✅ Test exitoso - Dashboard funciona</div>';
        console.log('✅ Contenedor actualizado exitosamente');
    } else {
        console.log('❌ Contenedor maintenanceAlerts no encontrado');
    }
}

// Función para probar solo el login
function testLoginProcess() {
    console.log('🔐 TEST: Proceso de login');
    const loginStart = performance.now();

    fetch('/api/user/info')
        .then(response => {
            const loginTime = performance.now() - loginStart;
            console.log(`🔐 Login check completado en ${loginTime.toFixed(2)}ms`);
            return response.json();
        })
        .then(data => {
            console.log('🔐 Usuario autenticado:', data.success);
        })
        .catch(error => {
            const loginTime = performance.now() - loginStart;
            console.error(`❌ Error login después de ${loginTime.toFixed(2)}ms:`, error);
        });
}

console.log('🧪 Test functions loaded. Try: testDashboardSimple() or testLoginProcess()');