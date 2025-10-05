// Script específico para activar solo la generación automática
console.log('🤖 ACTIVANDO GENERACIÓN AUTOMÁTICA EN PLANES');
console.log('='.repeat(50));

async function activarGeneracionAutomatica() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        console.log('📋 Obteniendo planes de mantenimiento...');
        
        // Obtener planes
        const planesResponse = await fetch('/planes/api', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        if (!planesResponse.ok) {
            throw new Error(`Error obteniendo planes: ${planesResponse.status}`);
        }
        
        const planesData = await planesResponse.json();
        const planes = planesData.planes || planesData.items || [];
        
        console.log(`📈 Total planes encontrados: ${planes.length}`);
        console.log('');
        
        for (const plan of planes) {
            console.log(`⚙️ Configurando plan: ${plan.codigo} - ${plan.nombre}`);
            
            try {
                // Obtener detalles completos del plan
                const detalleResponse = await fetch(`/planes/api/${plan.id}`, {
                    headers: { 'X-CSRFToken': csrfToken }
                });
                
                if (!detalleResponse.ok) {
                    console.log(`   ❌ Error obteniendo detalles: ${detalleResponse.status}`);
                    continue;
                }
                
                const detalle = await detalleResponse.json();
                console.log(`   📊 Estado actual: Activo=${detalle.estado}, GenAuto=${detalle.generacion_automatica}`);
                
                // Preparar datos actualizados
                const datosActualizados = {
                    ...detalle,
                    generacion_automatica: true,  // ← ¡CLAVE! Activar generación automática
                    estado: 'Activo'  // Asegurar que esté activo
                };
                
                // Actualizar el plan
                const actualizarResponse = await fetch(`/planes/api/${plan.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(datosActualizados)
                });
                
                if (actualizarResponse.ok) {
                    const resultado = await actualizarResponse.json();
                    console.log(`   ✅ ${plan.codigo}: Generación automática ACTIVADA`);
                } else {
                    const errorData = await actualizarResponse.json();
                    console.log(`   ❌ Error actualizando ${plan.codigo}:`, errorData);
                }
                
            } catch (error) {
                console.log(`   ❌ Error procesando ${plan.codigo}:`, error.message);
            }
            
            console.log('');
        }
        
        console.log('✅ CONFIGURACIÓN COMPLETADA');
        console.log('🎯 Ahora los planes tienen generación automática activada');
        console.log('');
        console.log('💡 PRÓXIMO PASO: Ejecuta generarOrdenesManualMejorado()');
        
    } catch (error) {
        console.error('❌ Error general:', error);
    }
}

activarGeneracionAutomatica();