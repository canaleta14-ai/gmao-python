// Diagnóstico para función mostrarCargando en inventario
// Este archivo puede ser incluido temporalmente para debugging

console.log('🔧 Diagnóstico de mostrarCargando cargado');

// Función de debugging para mostrarCargando
function debugMostrarCargando() {
    console.group('🔍 Debug mostrarCargando');

    // Verificar si existe la función
    if (typeof mostrarCargando === 'function') {
        console.log('✅ mostrarCargando existe como función');

        // Verificar si está en window
        if (typeof window.mostrarCargando === 'function') {
            console.log('✅ window.mostrarCargando existe');
        } else {
            console.warn('⚠️ window.mostrarCargando NO existe');
        }

        // Test de la función
        try {
            console.log('🧪 Probando mostrarCargando(true)...');
            mostrarCargando(true);

            setTimeout(() => {
                console.log('🧪 Probando mostrarCargando(false)...');
                mostrarCargando(false);
                console.log('✅ Ambas llamadas funcionaron correctamente');
            }, 2000);

        } catch (error) {
            console.error('❌ Error al probar mostrarCargando:', error);
        }

    } else {
        console.error('❌ mostrarCargando NO existe como función');
    }

    // Verificar tbody
    const tbody = document.getElementById('tabla-inventario-body');
    console.log('📋 tbody encontrado:', tbody ? '✅' : '❌');

    if (tbody) {
        console.log('📊 Contenido actual del tbody:', tbody.innerHTML.length > 100 ? 'Tiene contenido' : 'Vacío o poco contenido');
    }

    console.groupEnd();
}

// Exportar para uso manual en consola
window.debugMostrarCargando = debugMostrarCargando;

// Función para simular cancelación de CSV
function simularCancelacionCSV() {
    console.log('🎭 Simulando cancelación de descarga CSV...');

    // Simular el comportamiento de descargarCSVMejorado cuando se cancela
    console.log('1. Activando mostrarCargando(true)...');
    if (typeof window.mostrarCargando === 'function') {
        window.mostrarCargando(true);

        setTimeout(() => {
            console.log('2. Simulando cancelación - llamando mostrarCargando(false)...');
            window.mostrarCargando(false);
            console.log('✅ Simulación completada');
        }, 2000);
    } else {
        console.error('❌ window.mostrarCargando no está disponible');
    }
}

window.simularCancelacionCSV = simularCancelacionCSV;

console.log('🎯 Funciones de debug disponibles:');
console.log('  - debugMostrarCargando() : Diagnóstico completo');
console.log('  - simularCancelacionCSV() : Simular cancelación de CSV');