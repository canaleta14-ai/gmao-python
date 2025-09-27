// Script de prueba para verificar funcionalidad
console.log('🧪 test-inventario.js cargado correctamente');
console.log('🧪 Iniciando pruebas de JavaScript...');

// Verificar que las funciones existen
const funcionesRequeridas = [
    'mostrarModalNuevoArticulo',
    'categoriaSeleccionada',
    'generarCodigoAutomatico',
    'crearCategoriaRapida'
];

function verificarFunciones() {
    console.log('🔍 Verificando funciones...');

    funcionesRequeridas.forEach(nombreFuncion => {
        if (typeof window[nombreFuncion] === 'function') {
            console.log(`✅ ${nombreFuncion} - OK`);
        } else {
            console.log(`❌ ${nombreFuncion} - NO ENCONTRADA`);
        }
    });
}

// Verificar APIs de categorías
async function probarAPICategorias() {
    console.log('🌐 Probando API de categorías...');

    try {
        const response = await fetch('/api/categorias/');
        const data = await response.json();

        if (data.success) {
            console.log(`✅ API Categorías - ${data.categorias.length} categorías encontradas`);
            data.categorias.forEach(cat => {
                console.log(`   📋 ${cat.nombre} (${cat.prefijo}) - ${cat.total_articulos} artículos`);
            });
        } else {
            console.log('❌ API Categorías - Error:', data.message);
        }
    } catch (error) {
        console.log('❌ API Categorías - Error de conexión:', error);
    }
}

// Ejecutar pruebas cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        console.log('🧪 ========== INICIO DE PRUEBAS ==========');
        verificarFunciones();
        probarAPICategorias();
        console.log('🧪 ========== FIN DE PRUEBAS ==========');
    }, 1000); // Esperar 1 segundo para que todo se cargue
});

// Función de prueba manual
window.testInventario = function () {
    console.log('🧪 Ejecutando prueba manual...');
    verificarFunciones();
    probarAPICategorias();
};