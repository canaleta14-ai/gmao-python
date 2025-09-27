// FunciÃ³n de test sÃºper simple
function testDashboardSimple() {
    console.log('ğŸ§ª TEST: Dashboard sÃºper simple');

    // Solo cambiar contenido del contenedor de alertas
    const container = document.getElementById('maintenanceAlerts');
    if (container) {
        container.innerHTML = '<div class="alert alert-success">âœ… Test exitoso - Dashboard funciona</div>';
        console.log('âœ… Contenedor actualizado exitosamente');
    } else {
        console.log('â�Œ Contenedor maintenanceAlerts no encontrado');
    }
}

// FunciÃ³n para probar solo el login
function testLoginProcess() {
    console.log('ğŸ”� TEST: Proceso de login');
    const loginStart = performance.now();

    fetch('/api/user/info')
        .then(response => {
            const loginTime = performance.now() - loginStart;
            console.log(`ğŸ”� Login check completado en ${loginTime.toFixed(2)}ms`);
            return response.json();
        })
        .then(data => {
            console.log('ğŸ”� Usuario autenticado:', data.success);
        })
        .catch(error => {
            const loginTime = performance.now() - loginStart;
            console.error(`â�Œ Error login despuÃ©s de ${loginTime.toFixed(2)}ms:`, error);
        });
}

console.log('ğŸ§ª Test functions loaded. Try: testDashboardSimple() or testLoginProcess()');