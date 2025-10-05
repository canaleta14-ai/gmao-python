// Script para forzar recarga de inventario.js sin caché
console.log('🔄 Forzando recarga de inventario.js...');

// 1. Crear un nuevo elemento script con cache buster
const timestamp = new Date().getTime();
const script = document.createElement('script');
script.src = `/static/js/inventario.js?v=${timestamp}`;
script.onload = function() {
    console.log('✅ inventario.js recargado con timestamp:', timestamp);
    console.log('📋 Motivos actuales:');
    if (typeof MOTIVOS_POR_TIPO !== 'undefined') {
        console.log('   SALIDA:', MOTIVOS_POR_TIPO.salida);
        console.log('   REGULARIZACION:', MOTIVOS_POR_TIPO.regularizacion);
    } else {
        console.log('   ⚠️ MOTIVOS_POR_TIPO no está definido');
    }
};
script.onerror = function() {
    console.error('❌ Error al cargar inventario.js');
};

// 2. Eliminar script antiguo si existe
const oldScripts = document.querySelectorAll('script[src*="inventario.js"]');
oldScripts.forEach(s => s.remove());

// 3. Agregar nuevo script
document.head.appendChild(script);

console.log('📝 Script agregado, esperando carga...');
console.log('   Después de cargar, recarga la página para ver los cambios');
