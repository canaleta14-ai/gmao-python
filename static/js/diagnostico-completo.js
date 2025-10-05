// Script mejorado para diagnóstico completo
console.log('🔍 DIAGNÓSTICO COMPLETO - PLANES Y TÉCNICOS');
console.log('='.repeat(60));

async function diagnosticoCompleto() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        // 1. Verificar planes
        console.log('📋 1. VERIFICANDO PLANES DE MANTENIMIENTO...');
        const planesResponse = await fetch('/planes/api', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        const planesData = await planesResponse.json();
        const planes = planesData.planes || [];
        console.log(`📈 Total planes: ${planes.length}`);
        
        if (planes.length > 0) {
            const hoy = new Date();
            console.log(`📅 Fecha actual: ${hoy.toLocaleDateString('es-ES')} ${hoy.toLocaleTimeString('es-ES')}`);
            console.log('');
            
            planes.forEach((plan, index) => {
                const fechaEjecucion = new Date(plan.proxima_ejecucion);
                const vencido = fechaEjecucion <= hoy;
                const activo = plan.estado === 'Activo';
                const automatico = plan.generacion_automatica;
                
                console.log(`📋 Plan ${index + 1}:`);
                console.log(`   Nombre: ${plan.nombre || 'Sin nombre'}`);
                console.log(`   Activo: ${plan.activo_nombre || 'N/A'}`);
                console.log(`   Estado: ${plan.estado}`);
                console.log(`   Frecuencia: ${plan.frecuencia} ${plan.tipo_frecuencia}`);
                console.log(`   Próxima ejecución: ${plan.proxima_ejecucion}`);
                console.log(`   Generación automática: ${automatico ? 'SÍ ✅' : 'NO ❌'}`);
                console.log(`   Técnico asignado: ${plan.tecnico_asignado || 'No asignado'}`);
                console.log(`   🔍 Análisis:`);
                console.log(`      - Activo: ${activo ? '✅' : '❌'} (${plan.estado})`);
                console.log(`      - Vencido: ${vencido ? '✅' : '❌'} (${fechaEjecucion.toLocaleDateString('es-ES')} ${vencido ? '<=' : '>'} ${hoy.toLocaleDateString('es-ES')})`);
                console.log(`      - Automático: ${automatico ? '✅' : '❌'}`);
                console.log(`      - ¿Debe generar orden?: ${activo && vencido && automatico ? '🎯 SÍ' : '🚫 NO'}`);
                console.log('');
            });
        }
        
        // 2. Verificar técnicos disponibles
        console.log('👥 2. VERIFICANDO TÉCNICOS DISPONIBLES...');
        const usuariosResponse = await fetch('/usuarios/api', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (usuariosResponse.ok) {
            const usuariosData = await usuariosResponse.json();
            const usuarios = usuariosData.usuarios || [];
            const tecnicos = usuarios.filter(u => u.rol && (u.rol.toLowerCase() === 'técnico' || u.rol.toLowerCase() === 'tecnico'));
            
            console.log(`👥 Total usuarios: ${usuarios.length}`);
            console.log(`🔧 Técnicos encontrados: ${tecnicos.length}`);
            
            if (tecnicos.length > 0) {
                console.log('📝 Lista de técnicos:');
                tecnicos.forEach((tecnico, index) => {
                    console.log(`   ${index + 1}. ${tecnico.nombre} (${tecnico.username}) - Rol: ${tecnico.rol} - Activo: ${tecnico.activo ? 'SÍ' : 'NO'}`);
                });
            } else {
                console.log('❌ No se encontraron técnicos');
                console.log('💡 Verifica que existan usuarios con rol "Técnico"');
            }
        } else {
            console.log('❌ Error al obtener usuarios');
        }
        
        // 3. Verificar órdenes existentes de hoy
        console.log('📋 3. VERIFICANDO ÓRDENES DE HOY...');
        const ordenesResponse = await fetch('/ordenes/api', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (ordenesResponse.ok) {
            const ordenesData = await ordenesResponse.json();
            const ordenes = ordenesData.ordenes || [];
            const hoyStr = new Date().toISOString().split('T')[0];
            const ordenesHoy = ordenes.filter(o => o.fecha_creacion && o.fecha_creacion.startsWith(hoyStr));
            const ordenesPreventivas = ordenesHoy.filter(o => o.tipo === 'Mantenimiento Preventivo');
            
            console.log(`📊 Órdenes totales: ${ordenes.length}`);
            console.log(`📅 Órdenes de hoy: ${ordenesHoy.length}`);
            console.log(`🔧 Órdenes preventivas de hoy: ${ordenesPreventivas.length}`);
            
            if (ordenesPreventivas.length > 0) {
                console.log('📝 Órdenes preventivas de hoy:');
                ordenesPreventivas.forEach((orden, index) => {
                    console.log(`   ${index + 1}. ${orden.numero_orden} - ${orden.activo?.nombre} - Técnico: ${orden.tecnico?.nombre || 'Sin asignar'} - Estado: ${orden.estado}`);
                });
            }
        }
        
        console.log('');
        console.log('🎯 RESUMEN Y RECOMENDACIONES:');
        
        if (planes.length === 0) {
            console.log('❌ No hay planes configurados');
        } else {
            const planesActivos = planes.filter(p => p.estado === 'Activo');
            const planesVencidos = planesActivos.filter(p => new Date(p.proxima_ejecucion) <= new Date());
            const planesAutomaticos = planesVencidos.filter(p => p.generacion_automatica);
            
            console.log(`✅ ${planesActivos.length}/${planes.length} planes activos`);
            console.log(`⏰ ${planesVencidos.length}/${planesActivos.length} planes vencidos`);
            console.log(`🤖 ${planesAutomaticos.length}/${planesVencidos.length} planes con generación automática`);
            
            if (planesAutomaticos.length === 0) {
                console.log('💡 Activar "Generación automática" en los planes vencidos');
            }
        }
        
    } catch (error) {
        console.error('❌ Error en diagnóstico:', error);
    }
}

diagnosticoCompleto();