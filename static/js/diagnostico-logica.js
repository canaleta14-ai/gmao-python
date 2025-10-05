// Diagnóstico específico de la lógica de generación
console.log('🔍 DIAGNÓSTICO DETALLADO - LÓGICA DE GENERACIÓN');
console.log('='.repeat(60));

async function diagnosticoLogicaGeneracion() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        console.log('📋 Simulando la lógica EXACTA del backend...');
        console.log('');
        
        // Obtener planes
        const planesResponse = await fetch('/planes/api', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        const planesData = await planesResponse.json();
        const planes = planesData.planes || planesData.items || [];
        
        // Simular la fecha/hora actual como lo hace el backend
        const ahora = new Date(); // datetime.now() en Python
        const ahoraStr = ahora.toISOString();
        
        console.log(`🕐 Fecha/hora actual (como backend): ${ahoraStr}`);
        console.log(`📅 Solo fecha: ${ahora.toISOString().split('T')[0]}`);
        console.log(`⏰ Solo hora: ${ahora.toISOString().split('T')[1]}`);
        console.log('');
        
        for (const plan of planes) {
            console.log(`📋 Analizando: ${plan.codigo} - ${plan.nombre}`);
            console.log(`   Estado: ${plan.estado}`);
            console.log(`   Próxima ejecución: ${plan.proxima_ejecucion}`);
            
            // Obtener detalles completos
            try {
                const detalleResponse = await fetch(`/planes/api/${plan.id}`, {
                    headers: { 'X-CSRFToken': csrfToken }
                });
                
                if (detalleResponse.ok) {
                    const detalle = await detalleResponse.json();
                    console.log(`   Generación automática: ${detalle.generacion_automatica}`);
                    
                    // Simular las condiciones EXACTAS del backend
                    const cumpleEstado = plan.estado === "Activo";
                    const cumpleGeneracion = detalle.generacion_automatica === true;
                    
                    // CLAVE: Analizar la comparación de fechas
                    const fechaEjecucion = plan.proxima_ejecucion;
                    console.log(`   📊 Comparación de fechas:`);
                    console.log(`      Backend compara: "${fechaEjecucion}" <= "${ahoraStr}"`);
                    
                    // Intentar diferentes interpretaciones de la fecha
                    const fechaEjecucionComoFecha = new Date(fechaEjecucion + 'T00:00:00');
                    const fechaEjecucionComoFechaISO = new Date(fechaEjecucion);
                    
                    console.log(`      Como fecha 00:00: ${fechaEjecucionComoFecha.toISOString()}`);
                    console.log(`      Como fecha ISO: ${fechaEjecucionComoFechaISO.toISOString()}`);
                    
                    const cumpleFecha1 = fechaEjecucionComoFecha <= ahora;
                    const cumpleFecha2 = fechaEjecucionComoFechaISO <= ahora;
                    
                    console.log(`      ¿Vencido opción 1?: ${cumpleFecha1}`);
                    console.log(`      ¿Vencido opción 2?: ${cumpleFecha2}`);
                    
                    const cumpleTodasCondiciones = cumpleEstado && cumpleGeneracion && (cumpleFecha1 || cumpleFecha2);
                    
                    console.log(`   🎯 Resumen de condiciones:`);
                    console.log(`      ✅ Estado Activo: ${cumpleEstado}`);
                    console.log(`      ✅ Generación automática: ${cumpleGeneracion}`);
                    console.log(`      ❓ Fecha vencida: ${cumpleFecha1 || cumpleFecha2}`);
                    console.log(`      🎯 ¿Debe generar?: ${cumpleTodasCondiciones}`);
                    
                    if (!cumpleTodasCondiciones) {
                        console.log(`   🚨 RAZONES por las que NO genera:`);
                        if (!cumpleEstado) console.log(`      - Estado no es "Activo"`);
                        if (!cumpleGeneracion) console.log(`      - Generación automática no es true`);
                        if (!cumpleFecha1 && !cumpleFecha2) console.log(`      - Fecha no está vencida`);
                    }
                }
            } catch (error) {
                console.log(`   ❌ Error obteniendo detalles: ${error.message}`);
            }
            
            console.log('');
        }
        
        // Verificar órdenes existentes
        console.log('📋 VERIFICANDO ÓRDENES EXISTENTES...');
        try {
            const ordenesResponse = await fetch('/ordenes/api', {
                headers: { 'X-CSRFToken': csrfToken }
            });
            
            if (ordenesResponse.ok) {
                const ordenesData = await ordenesResponse.json();
                const ordenes = ordenesData.ordenes || ordenesData.items || [];
                
                const ordenesHoy = ordenes.filter(o => {
                    const fechaCreacion = o.fecha_creacion || o.fecha_programada;
                    return fechaCreacion && fechaCreacion.includes('2025-10-03');
                });
                
                console.log(`📊 Total órdenes en el sistema: ${ordenes.length}`);
                console.log(`📅 Órdenes creadas hoy: ${ordenesHoy.length}`);
                
                if (ordenesHoy.length > 0) {
                    console.log('🔍 Órdenes de hoy:');
                    ordenesHoy.forEach((orden, i) => {
                        console.log(`   ${i + 1}. ${orden.numero_orden || orden.id} - ${orden.descripcion}`);
                    });
                }
            }
        } catch (error) {
            console.log('❌ Error verificando órdenes:', error.message);
        }
        
        console.log('');
        console.log('💡 CONCLUSIÓN:');
        console.log('Si todas las condiciones se cumplen pero no se generan órdenes,');
        console.log('el problema podría estar en:');
        console.log('1. Formato de fecha en la base de datos');
        console.log('2. Órdenes existentes bloqueando la generación');
        console.log('3. Error en la función de asignación de técnicos');
        
    } catch (error) {
        console.error('❌ Error en diagnóstico:', error);
    }
}

diagnosticoLogicaGeneracion();