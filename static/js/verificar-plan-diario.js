// Script para verificar y crear el plan diario mencionado por el usuario
console.log('🔍 VERIFICANDO PLAN DIARIO...');
console.log('='.repeat(50));

async function verificarPlanDiario() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        // 1. Verificar si existe el plan diario
        console.log('📋 Buscando plan diario específico...');
        
        const response = await fetch('/planes/api?per_page=100', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        const data = await response.json();
        console.log('📊 Respuesta completa:', data);
        
        // 2. Si no hay planes, mostrar formulario para crear uno
        if (!data.planes || data.planes.length === 0) {
            console.log('⚠️ No se encontraron planes. Vamos a verificar los activos disponibles...');
            
            // Verificar activos
            const activosResponse = await fetch('/activos/api', {
                headers: { 'X-CSRFToken': csrfToken }
            });
            
            if (activosResponse.ok) {
                const activosData = await activosResponse.json();
                console.log('🏭 Activos disponibles:', activosData);
            }
            
            // Verificar técnicos activos
            const usuariosResponse = await fetch('/usuarios/api', {
                headers: { 'X-CSRFToken': csrfToken }
            });
            
            if (usuariosResponse.ok) {
                const usuariosData = await usuariosResponse.json();
                const tecnicosActivos = usuariosData.usuarios?.filter(u => 
                    u.rol && u.rol.toLowerCase().includes('técnico') && u.activo
                );
                
                console.log('👥 Técnicos activos:', tecnicosActivos);
                
                if (tecnicosActivos && tecnicosActivos.length === 0) {
                    console.log('🚨 PROBLEMA: No hay técnicos activos');
                    console.log('💡 SOLUCIÓN: Activar técnico en /usuarios');
                }
            }
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

verificarPlanDiario();