// Script de diagnóstico para planes de mantenimiento
// Ejecutar en la consola del navegador después del script anterior

console.log('🔍 DIAGNÓSTICO DE PLANES DE MANTENIMIENTO');
console.log('='.repeat(50));

async function diagnosticarPlanes() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        if (!csrfToken) {
            console.error('❌ No se encontró token CSRF');
            return;
        }
        
        console.log('📋 Verificando planes de mantenimiento...');
        
        // Consultar planes activos
        const response = await fetch('/planes/api', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (!response.ok) {
            console.error('❌ Error al obtener planes:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log('📊 Respuesta completa:', data);
        
        const planes = data.planes || [];
        console.log(`📈 Total planes encontrados: ${planes.length}`);
        
        if (planes.length === 0) {
            console.log('⚠️ No hay planes de mantenimiento configurados');
            console.log('💡 Necesitas crear planes de mantenimiento primero');
            return;
        }
        
        // Analizar cada plan
        const hoy = new Date();
        console.log(`📅 Fecha actual: ${hoy.toLocaleDateString('es-ES')}`);
        console.log('');
        
        planes.forEach((plan, index) => {
            console.log(`📋 Plan ${index + 1}:`);
            console.log(`   ID: ${plan.id}`);
            console.log(`   Activo: ${plan.activo_nombre || 'N/A'}`);
            console.log(`   Estado: ${plan.estado}`);
            console.log(`   Frecuencia: ${plan.frecuencia} ${plan.tipo_frecuencia}`);
            console.log(`   Próxima ejecución: ${plan.proxima_ejecucion}`);
            console.log(`   Generación automática: ${plan.generacion_automatica ? 'SÍ' : 'NO'}`);
            
            // Verificar si está vencido
            const fechaEjecucion = new Date(plan.proxima_ejecucion);
            const vencido = fechaEjecucion <= hoy;
            const activo = plan.estado === 'Activo';
            const automatico = plan.generacion_automatica;
            
            console.log(`   🔍 Análisis:`);
            console.log(`      - Activo: ${activo ? '✅' : '❌'} (${plan.estado})`);
            console.log(`      - Vencido: ${vencido ? '✅' : '❌'} (${fechaEjecucion.toLocaleDateString('es-ES')} ${vencido ? '<=' : '>'} ${hoy.toLocaleDateString('es-ES')})`);
            console.log(`      - Automático: ${automatico ? '✅' : '❌'}`);
            console.log(`      - ¿Debe generar orden?: ${activo && vencido && automatico ? '🎯 SÍ' : '🚫 NO'}`);
            console.log('');
        });
        
        // Resumen
        const planesActivos = planes.filter(p => p.estado === 'Activo');
        const planesVencidos = planesActivos.filter(p => new Date(p.proxima_ejecucion) <= hoy);
        const planesAutomaticos = planesVencidos.filter(p => p.generacion_automatica);
        
        console.log('📊 RESUMEN:');
        console.log(`   Total planes: ${planes.length}`);
        console.log(`   Planes activos: ${planesActivos.length}`);
        console.log(`   Planes vencidos: ${planesVencidos.length}`);
        console.log(`   Planes con generación automática: ${planesAutomaticos.length}`);
        console.log('');
        
        if (planesAutomaticos.length === 0) {
            console.log('💡 RECOMENDACIONES:');
            if (planes.length === 0) {
                console.log('   1. Crear planes de mantenimiento en la sección "Preventivo"');
            } else if (planesActivos.length === 0) {
                console.log('   1. Activar planes existentes (cambiar estado a "Activo")');
            } else if (planesVencidos.length === 0) {
                console.log('   1. Los planes están configurados para fechas futuras');
                console.log('   2. Verificar si las fechas son correctas');
            } else {
                console.log('   1. Habilitar "Generación automática" en los planes vencidos');
            }
        }
        
    } catch (error) {
        console.error('❌ Error en diagnóstico:', error);
    }
}

// Ejecutar diagnóstico
diagnosticarPlanes();