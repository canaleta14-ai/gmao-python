// Script para diagnóstico directo de la base de datos
console.log('🔍 DIAGNÓSTICO DIRECTO - BASE DE DATOS');
console.log('='.repeat(60));

async function diagnosticoBaseDatos() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        console.log('📋 1. VERIFICANDO RESPUESTA COMPLETA DE PLANES...');
        
        // Hacer petición sin filtros para obtener TODOS los planes
        const response = await fetch('/planes/api?per_page=100', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('📊 RESPUESTA COMPLETA:', data);
        console.log('');
        
        // Verificar la estructura de respuesta
        if (data.items) {
            console.log(`📈 Total planes en 'items': ${data.items.length}`);
            console.log('🔍 Estructura esperada por frontend: data.planes');
            console.log('🔍 Estructura actual del backend: data.items');
            console.log('⚠️ PROBLEMA ENCONTRADO: Discrepancia en estructura de datos');
            
            if (data.items.length > 0) {
                console.log('');
                console.log('📋 PLANES ENCONTRADOS:');
                data.items.forEach((plan, index) => {
                    console.log(`   ${index + 1}. ${plan.codigo} - ${plan.nombre}`);
                    console.log(`      Equipo: ${plan.equipo}`);
                    console.log(`      Estado: ${plan.estado}`);
                    console.log(`      Próxima: ${plan.proxima_ejecucion}`);
                    console.log('');
                });
            }
        } else if (data.planes) {
            console.log(`📈 Total planes en 'planes': ${data.planes.length}`);
        } else {
            console.log('❌ Estructura de respuesta desconocida');
        }
        
        // 2. Verificar técnicos con más detalle
        console.log('👥 2. VERIFICANDO TÉCNICOS CON DETALLE...');
        const usuariosResponse = await fetch('/usuarios/api', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        if (usuariosResponse.ok) {
            const usuariosData = await usuariosResponse.json();
            console.log('👥 Respuesta completa usuarios:', usuariosData);
            
            if (usuariosData.usuarios) {
                const tecnicos = usuariosData.usuarios.filter(u => 
                    u.rol && (u.rol.toLowerCase().includes('técnico') || u.rol.toLowerCase().includes('tecnico'))
                );
                
                console.log(`🔧 Total técnicos: ${tecnicos.length}`);
                tecnicos.forEach((t, i) => {
                    console.log(`   ${i + 1}. ${t.nombre || 'Sin nombre'}`);
                    console.log(`      Username: ${t.username || 'Sin username'}`);
                    console.log(`      Rol: ${t.rol || 'Sin rol'}`);
                    console.log(`      Activo: ${t.activo !== undefined ? (t.activo ? 'SÍ ✅' : 'NO ❌') : 'No definido'}`);
                    console.log('');
                });
            }
        }
        
        // 3. Diagnosticar el problema del frontend
        console.log('🔧 3. DIAGNOSTICANDO PROBLEMA FRONTEND...');
        console.log('El frontend busca: data.planes');
        console.log('El backend devuelve: data.items');
        console.log('💡 SOLUCIÓN: Actualizar backend o frontend para que coincidan');
        
    } catch (error) {
        console.error('❌ Error en diagnóstico:', error);
    }
}

diagnosticoBaseDatos();