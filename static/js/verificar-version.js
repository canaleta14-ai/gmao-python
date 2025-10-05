/**
 * Script para verificar versión de archivos JavaScript cargados
 * y forzar recarga sin caché
 * 
 * Ejecutar en consola del navegador (F12 -> Console)
 */

(async () => {
    console.log('🔍 Verificando versión de archivos JavaScript...\n');
    
    // 1. Verificar si hay botones de editar en la página actual
    const botonesEditar = document.querySelectorAll('button[onclick*="editar"], .btn.edit');
    const iconosEditar = document.querySelectorAll('.bi-pencil');
    
    console.log(`📊 Estado actual de la página:`);
    console.log(`   - Botones con onclick editar: ${botonesEditar.length}`);
    console.log(`   - Iconos bi-pencil: ${iconosEditar.length}`);
    
    if (botonesEditar.length > 0 || iconosEditar.length > 0) {
        console.warn('\n⚠️ DETECTADOS BOTONES DE EDITAR ANTIGUOS');
        console.log('\n🔄 Soluciones:\n');
        
        console.log('✅ Opción 1: RECARGA FORZADA (MÁS RÁPIDO)');
        console.log('   Windows: Ctrl + Shift + R o Ctrl + F5');
        console.log('   Mac: Cmd + Shift + R');
        
        console.log('\n✅ Opción 2: Limpiar caché del navegador');
        console.log('   1. F12 → Network → Check "Disable cache"');
        console.log('   2. Mantener F12 abierto y recargar');
        
        console.log('\n✅ Opción 3: Ejecutar limpieza automática');
        console.log('   Ejecuta: limpiarCache()');
        
        // Definir función global para limpiar caché
        window.limpiarCache = async () => {
            console.log('\n🧹 Limpiando caché de archivos JavaScript...');
            
            const archivos = [
                '/static/js/activos.js',
                '/static/js/proveedores.js',
                '/static/js/ordenes.js',
                '/static/js/preventivo.js',
                '/static/js/inventario.js'
            ];
            
            for (const archivo of archivos) {
                try {
                    const url = `${archivo}?v=${Date.now()}`;
                    const response = await fetch(url, { cache: 'reload' });
                    
                    if (response.ok) {
                        console.log(`   ✅ ${archivo} - Actualizado`);
                    } else {
                        console.warn(`   ⚠️ ${archivo} - Status ${response.status}`);
                    }
                } catch (e) {
                    console.error(`   ❌ ${archivo} - Error: ${e.message}`);
                }
            }
            
            console.log('\n🔄 Recarga la página ahora para aplicar cambios');
            console.log('   setTimeout(() => location.reload(true), 2000);');
            
            // Auto-reload después de 3 segundos
            setTimeout(() => {
                console.log('🔃 Recargando página...');
                location.reload(true);
            }, 3000);
        };
        
    } else {
        console.log('\n✅ ¡PERFECTO! No se detectaron botones de editar antiguos');
        console.log('   La versión actualizada está cargada correctamente');
    }
    
    // 2. Verificar scripts cargados
    console.log('\n📦 Scripts cargados en la página:');
    const scripts = Array.from(document.querySelectorAll('script[src*="/static/js/"]'));
    scripts.forEach(script => {
        console.log(`   - ${script.src.split('/').pop()}`);
    });
    
    // 3. Información de la caché
    console.log('\n💾 Información de caché del navegador:');
    if ('caches' in window) {
        const cacheNames = await caches.keys();
        console.log(`   - Cachés disponibles: ${cacheNames.length}`);
        cacheNames.forEach(name => console.log(`     • ${name}`));
    } else {
        console.log('   - Cache API no disponible');
    }
    
})();
