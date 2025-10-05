/**
 * Script de depuración para el calendario
 * Ejecutar en consola del navegador (F12 -> Console) en la página del calendario
 */

(async () => {
    console.log('🔍 Depurando calendario de órdenes...\n');
    
    try {
        // 1. Verificar que estamos en la página del calendario
        const calendarEl = document.getElementById('calendario');
        if (!calendarEl) {
            console.error('❌ No estás en la página del calendario');
            console.log('👉 Navega a /calendario primero');
            return;
        }
        
        // 2. Obtener datos del mes actual
        const ahora = new Date();
        const year = ahora.getFullYear();
        const month = ahora.getMonth() + 1; // JavaScript usa 0-11
        
        console.log(`📅 Consultando eventos para: ${month}/${year}\n`);
        
        const url = `/calendario/api/ordenes?year=${year}&month=${month}`;
        console.log(`🌐 URL: ${url}\n`);
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ Respuesta exitosa\n');
            console.log(`📊 Estadísticas:`);
            console.log(`   - Total eventos: ${data.eventos ? data.eventos.length : 0}`);
            console.log(`   - Total órdenes en BD: ${data.total_ordenes}`);
            console.log(`   - Total planes: ${data.total_planes}\n`);
            
            if (data.eventos && data.eventos.length > 0) {
                console.log(`📋 Primeros 5 eventos:`);
                console.table(data.eventos.slice(0, 5).map(e => ({
                    ID: e.id,
                    Título: e.title,
                    Fecha: e.start,
                    Tipo: e.tipo,
                    Estado: e.estado || 'N/A'
                })));
                
                // Contar por tipo
                const ordenes = data.eventos.filter(e => e.tipo === 'orden');
                const planes = data.eventos.filter(e => e.tipo === 'plan_futuro');
                
                console.log(`\n📈 Desglose:`);
                console.log(`   - Eventos de órdenes: ${ordenes.length}`);
                console.log(`   - Eventos de planes futuros: ${planes.length}`);
                
                if (ordenes.length === 0 && data.total_ordenes > 0) {
                    console.warn(`\n⚠️ PROBLEMA DETECTADO:`);
                    console.warn(`   Hay ${data.total_ordenes} órdenes en la BD pero 0 eventos creados`);
                    console.warn(`   Esto puede ser por:`);
                    console.warn(`   1. Las órdenes no tienen fecha_programada ni fecha_creacion`);
                    console.warn(`   2. Error en la conversión de fechas`);
                    console.warn(`   3. Las fechas están fuera del rango del mes actual`);
                }
                
            } else {
                console.warn('⚠️ No se encontraron eventos para mostrar');
                
                if (data.total_ordenes > 0) {
                    console.warn(`\n❓ Hay ${data.total_ordenes} órdenes en BD pero no se crearon eventos`);
                    console.warn('   Revisa los logs del servidor para más detalles');
                }
            }
            
        } else {
            console.error('❌ Error en la respuesta:', data.error);
        }
        
        // 3. Verificar logs del servidor
        console.log('\n\n📝 Para ver los logs del servidor, ejecuta en terminal PowerShell:');
        console.log('gcloud app logs read --limit=50 --project=gmao-sistema-2025 | Select-String -Pattern "DEBUG Calendario"');
        
    } catch (error) {
        console.error('❌ Error ejecutando debug:', error);
    }
})();
