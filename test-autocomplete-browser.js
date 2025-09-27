// Script de test para autocompletado e historial en consola del navegador

// Función para probar el historial de un artículo específico
window.testHistorial = function (articuloId = 1) {
    console.clear();
    console.log('🧪 === TEST DE HISTORIAL DE MOVIMIENTOS ===');
    console.log('📦 Probando historial para artículo ID:', articuloId);

    // Test directo de la API
    const url = `/inventario/api/articulos/${articuloId}/movimientos?page=1&per_page=20`;
    console.log('🌐 URL a probar:', url);

    fetch(url)
        .then(response => {
            console.log('📡 Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos recibidos:', data);
            console.log('📈 Estructura de datos:', {
                hasMovimientos: !!data.movimientos,
                movimientosLength: data.movimientos ? data.movimientos.length : 0,
                total: data.total,
                pages: data.pages
            });

            if (data.movimientos && data.movimientos.length > 0) {
                console.log('✅ Movimientos encontrados:');
                data.movimientos.forEach((mov, i) => {
                    console.log(`   ${i + 1}. ${mov.fecha} - ${mov.tipo} - ${mov.cantidad} unidades`);
                });

                console.log('\n🎭 Probando función verHistorial del frontend...');
                if (typeof verHistorial === 'function') {
                    verHistorial(articuloId);
                } else {
                    console.error('❌ Función verHistorial no disponible');
                }
            } else {
                console.log('📭 No hay movimientos para este artículo');
            }
        })
        .catch(error => {
            console.error('❌ Error en test de historial:', error);
        });
};

// Función para listar todos los artículos disponibles
window.listarArticulos = function () {
    console.log('📋 === ARTÍCULOS DISPONIBLES ===');
    fetch('/inventario/api/articulos?page=1&per_page=10')
        .then(response => response.json())
        .then(data => {
            if (data.articulos && data.articulos.length > 0) {
                console.log('📦 Artículos encontrados:');
                data.articulos.forEach(art => {
                    console.log(`   ID: ${art.id} - ${art.codigo} - ${art.descripcion}`);
                });
                console.log('\n💡 Usa: testHistorial(ID) para probar el historial de un artículo');
            } else {
                console.log('❌ No hay artículos disponibles');
            }
        })
        .catch(error => {
            console.error('❌ Error listando artículos:', error);
        });
};

console.log('🛠️  Funciones de test cargadas:');
console.log('- testHistorial(id) - Prueba historial de artículo específico');
console.log('- listarArticulos() - Lista artículos disponibles');