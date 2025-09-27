// Test de funciones para ordenes.js
console.log('🧪 Verificando funciones de ordenes.js...');

// Verificar que las funciones principales existen
const functionsToTest = [
    'mostrarModalNuevaOrden',
    'exportarCSV',
    'cargarOrdenes',
    'mostrarOrdenes',
    'mostrarToast'
];

let allFunctionsOk = true;

functionsToTest.forEach(funcName => {
    if (typeof window[funcName] === 'function') {
        console.log(`✅ ${funcName} está definida correctamente`);
    } else {
        console.error(`❌ ${funcName} NO está definida`);
        allFunctionsOk = false;
    }
});

if (allFunctionsOk) {
    console.log('🎉 Todas las funciones de órdenes están disponibles');
} else {
    console.log('⚠️  Algunas funciones no están disponibles');
}

// Función de test específica para órdenes
window.testOrdenesModule = function () {
    console.log('🧪 Probando módulo de órdenes...');

    try {
        // Verificar variables globales
        console.log('Variables globales:', {
            ordenes: typeof ordenes,
            activos: typeof activos,
            tecnicos: typeof tecnicos
        });

        console.log('✅ Test del módulo de órdenes completado');
    } catch (error) {
        console.error('❌ Error en test de órdenes:', error);
    }
};

console.log('✅ Script de test de órdenes cargado. Usa testOrdenesModule() para probar');