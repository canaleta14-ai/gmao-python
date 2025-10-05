/**
 * Script completo de diagnóstico y solución para el calendario
 * Ejecutar en consola del navegador (F12 -> Console) en /calendario
 */

(async () => {
    console.log('🔍 DIAGNÓSTICO COMPLETO DEL CALENDARIO\n');
    console.log('='.repeat(60));
    
    // 1. Verificar elementos básicos
    console.log('\n1️⃣ VERIFICACIÓN DE ELEMENTOS');
    const calEl = document.getElementById('calendario');
    const fullCalendarLoaded = typeof FullCalendar !== 'undefined';
    
    console.log(`   ✅ Elemento #calendario: ${calEl ? 'Encontrado' : '❌ NO ENCONTRADO'}`);
    console.log(`   ✅ FullCalendar lib: ${fullCalendarLoaded ? 'Cargada' : '❌ NO CARGADA'}`);
    console.log(`   ✅ Instancia calendar: ${window.calendar ? 'Creada' : '❌ NO CREADA'}`);
    
    if (!calEl) {
        console.error('\n❌ No estás en la página /calendario');
        return;
    }
    
    // 2. Verificar datos de la API
    console.log('\n2️⃣ DATOS DE LA API');
    const ahora = new Date();
    const year = ahora.getFullYear();
    const month = ahora.getMonth() + 1;
    
    try {
        const response = await fetch(`/calendario/api/ordenes?year=${year}&month=${month}`);
        const data = await response.json();
        
        if (data.success) {
            console.log(`   ✅ API responde correctamente`);
            console.log(`   📊 Total eventos: ${data.eventos.length}`);
            console.log(`   📋 Órdenes en BD: ${data.total_ordenes}`);
            console.log(`   📅 Planes futuros: ${data.total_planes}`);
            
            if (data.eventos.length > 0) {
                console.log('\n   📋 Primeros 3 eventos:');
                console.table(data.eventos.slice(0, 3).map(e => ({
                    Título: e.title,
                    Fecha: e.start,
                    Tipo: e.tipo,
                    Color: e.backgroundColor
                })));
            } else {
                console.warn('   ⚠️ La API no devuelve eventos');
            }
        } else {
            console.error('   ❌ Error en API:', data.error);
            return;
        }
    } catch (error) {
        console.error('   ❌ Error llamando a la API:', error);
        return;
    }
    
    // 3. Verificar estado del calendario FullCalendar
    console.log('\n3️⃣ ESTADO DE FULLCALENDAR');
    if (window.calendar) {
        const eventos = window.calendar.getEvents();
        console.log(`   📊 Eventos cargados en calendario: ${eventos.length}`);
        
        if (eventos.length > 0) {
            console.log('\n   ✅ CALENDARIO TIENE EVENTOS - Primeros 3:');
            console.table(eventos.slice(0, 3).map(e => ({
                ID: e.id,
                Título: e.title,
                Fecha: e.startStr,
                Color: e.backgroundColor
            })));
            
            console.log('\n   🎨 PROBLEMA VISUAL DETECTADO');
            console.log('   El calendario tiene datos pero puede no estar renderizando correctamente');
            console.log('   Intentando soluciones...\n');
            
            // Solución 1: Forzar re-render
            console.log('   🔧 Solución 1: Re-render del calendario...');
            window.calendar.render();
            
            // Solución 2: Refetch events
            console.log('   🔧 Solución 2: Refetch de eventos...');
            window.calendar.refetchEvents();
            
            // Solución 3: Ajustar altura
            console.log('   🔧 Solución 3: Ajustar altura...');
            window.calendar.updateSize();
            
            console.log('\n   ✅ Soluciones aplicadas - Verifica el calendario visual');
            
        } else if (eventos.length === 0) {
            console.warn('   ⚠️ Calendario creado pero SIN EVENTOS cargados');
            console.log('\n   🔄 Intentando recargar eventos...');
            
            window.calendar.refetchEvents();
            
            setTimeout(() => {
                const eventosNuevos = window.calendar.getEvents();
                console.log(`   📊 Después de refetch: ${eventosNuevos.length} eventos`);
                
                if (eventosNuevos.length === 0) {
                    console.error('\n   ❌ PROBLEMA: No se cargan eventos');
                    console.log('   Posibles causas:');
                    console.log('   1. Error en la función events de FullCalendar');
                    console.log('   2. Fechas fuera del rango visible');
                    console.log('   3. Error de CORS o red');
                    console.log('\n   🔧 Recargando página...');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    console.log('   ✅ Eventos cargados correctamente!');
                }
            }, 1000);
        }
    } else {
        console.error('   ❌ Instancia de calendar no encontrada');
        console.log('   🔄 Recargando página para reinicializar...');
        setTimeout(() => location.reload(), 2000);
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ Diagnóstico completo\n');
    
})();
