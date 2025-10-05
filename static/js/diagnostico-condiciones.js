// Script de diagnóstico específico para condiciones de generación
console.log('🔍 DIAGNÓSTICO ESPECÍFICO - CONDICIONES DE GENERACIÓN');
console.log('='.repeat(65));

async function diagnosticoCondicionesGeneracion() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        console.log('📋 1. VERIFICANDO DETALLES COMPLETOS DE PLANES...');
        
        // Obtener planes con más detalles
        const planesResponse = await fetch('/planes/api?per_page=100', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        const planesData = await planesResponse.json();
        const planes = planesData.planes || planesData.items || [];
        
        const hoy = new Date();
        const hoyStr = '03/10/2025'; // Fecha actual
        
        console.log(`📅 Fecha actual: ${hoyStr}`);
        console.log(`📈 Total planes: ${planes.length}`);
        console.log('');
        
        for (let i = 0; i < planes.length; i++) {
            const plan = planes[i];
            const vencido = plan.proxima_ejecucion <= hoyStr || plan.proxima_ejecucion === hoyStr;
            
            console.log(`📋 Plan ${i + 1}: ${plan.codigo} - ${plan.nombre}`);
            console.log(`   ✅ Estado: ${plan.estado}`);
            console.log(`   📅 Próxima ejecución: ${plan.proxima_ejecucion}`);
            console.log(`   ⏰ ¿Vencido?: ${vencido ? 'SÍ ✅' : 'NO ❌'}`);
            
            // Intentar obtener detalles específicos del plan
            try {
                const detalleResponse = await fetch(`/planes/api/${plan.id}`, {
                    headers: { 'X-CSRFToken': csrfToken }
                });
                
                if (detalleResponse.ok) {
                    const detalle = await detalleResponse.json();
                    const autoGen = detalle.generacion_automatica;
                    console.log(`   🤖 Generación automática: ${autoGen !== undefined ? (autoGen ? 'SÍ ✅' : 'NO ❌') : 'NO DEFINIDO ❓'}`);
                    
                    // Verificar condiciones completas
                    const cumpleCondiciones = (
                        plan.estado === 'Activo' && 
                        vencido && 
                        autoGen === true
                    );
                    
                    console.log(`   🎯 ¿Debe generar orden?: ${cumpleCondiciones ? 'SÍ ✅' : 'NO ❌'}`);
                    
                    if (!cumpleCondiciones) {
                        console.log('   🚨 RAZONES POR LAS QUE NO GENERA:');
                        if (plan.estado !== 'Activo') console.log('      - Estado no es Activo');
                        if (!vencido) console.log('      - No está vencido');
                        if (autoGen !== true) console.log('      - Generación automática desactivada');
                    }
                } else {
                    console.log(`   ❌ No se pudo obtener detalle (${detalleResponse.status})`);
                }
            } catch (error) {
                console.log(`   ❌ Error obteniendo detalle: ${error.message}`);
            }
            
            console.log('');
        }
        
        // 2. Verificar técnicos disponibles
        console.log('👥 2. VERIFICANDO TÉCNICOS DISPONIBLES...');
        const usuariosResponse = await fetch('/usuarios/api', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        if (usuariosResponse.ok) {
            const usuariosData = await usuariosResponse.json();
            const usuarios = usuariosData.usuarios || [];
            
            const tecnicos = usuarios.filter(u => 
                u.rol && (
                    u.rol.toLowerCase().includes('técnico') || 
                    u.rol.toLowerCase().includes('tecnico') ||
                    u.rol.toLowerCase().includes('supervisor')
                )
            );
            
            console.log(`🔧 Total técnicos encontrados: ${tecnicos.length}`);
            
            const tecnicosActivos = tecnicos.filter(t => t.activo === true);
            console.log(`✅ Técnicos activos: ${tecnicosActivos.length}`);
            
            tecnicos.forEach((t, i) => {
                console.log(`   ${i + 1}. ${t.nombre}`);
                console.log(`      Rol: ${t.rol}`);
                console.log(`      Activo: ${t.activo === true ? 'SÍ ✅' : t.activo === false ? 'NO ❌' : 'NO DEFINIDO ❓'}`);
                console.log(`      Username: ${t.username || 'No definido'}`);
            });
            
            if (tecnicosActivos.length === 0) {
                console.log('🚨 PROBLEMA: No hay técnicos activos para asignar');
            }
        }
        
        console.log('');
        console.log('💡 PRÓXIMOS PASOS:');
        console.log('1. Si generacion_automatica está en false, activarla');
        console.log('2. Si no hay técnicos activos, activar al menos uno');
        console.log('3. Verificar que la fecha de próxima ejecución sea correcta');
        
    } catch (error) {
        console.error('❌ Error en diagnóstico:', error);
    }
}

diagnosticoCondicionesGeneracion();