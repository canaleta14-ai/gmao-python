// Script para activar técnicos y configurar generación automática
console.log('🔧 ACTIVANDO TÉCNICOS Y CONFIGURANDO GENERACIÓN');
console.log('='.repeat(55));

async function activarTecnicosYConfiguracion() {
    try {
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
                         document.querySelector('input[name=csrf_token]')?.value;
        
        console.log('👥 1. ACTIVANDO TÉCNICOS...');
        
        // Obtener lista de usuarios
        const usuariosResponse = await fetch('/usuarios/api', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        if (usuariosResponse.ok) {
            const usuariosData = await usuariosResponse.json();
            const usuarios = usuariosData.usuarios || [];
            
            const tecnicos = usuarios.filter(u => 
                u.rol && (
                    u.rol.toLowerCase().includes('técnico') || 
                    u.rol.toLowerCase().includes('tecnico')
                )
            );
            
            console.log(`🔧 Encontrados ${tecnicos.length} técnicos para activar`);
            
            // Activar cada técnico
            for (const tecnico of tecnicos) {
                console.log(`⚙️ Activando técnico: ${tecnico.nombre} (ID: ${tecnico.id})`);
                
                try {
                    const activarResponse = await fetch(`/usuarios/api/${tecnico.id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            nombre: tecnico.nombre,
                            email: tecnico.email,
                            rol: tecnico.rol,
                            activo: true,  // Activar técnico
                            username: tecnico.username || `${tecnico.nombre.toLowerCase().replace(' ', '')}`
                        })
                    });
                    
                    if (activarResponse.ok) {
                        console.log(`   ✅ ${tecnico.nombre} activado correctamente`);
                    } else {
                        const errorData = await activarResponse.json();
                        console.log(`   ❌ Error activando ${tecnico.nombre}:`, errorData);
                    }
                } catch (error) {
                    console.log(`   ❌ Error activando ${tecnico.nombre}:`, error.message);
                }
            }
        }
        
        console.log('');
        console.log('🤖 2. CONFIGURANDO GENERACIÓN AUTOMÁTICA EN PLANES...');
        
        // Obtener planes
        const planesResponse = await fetch('/planes/api', {
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        if (planesResponse.ok) {
            const planesData = await planesResponse.json();
            const planes = planesData.planes || planesData.items || [];
            
            for (const plan of planes) {
                console.log(`⚙️ Configurando plan: ${plan.codigo} - ${plan.nombre}`);
                
                try {
                    // Obtener detalles actuales del plan
                    const detalleResponse = await fetch(`/planes/api/${plan.id}`, {
                        headers: { 'X-CSRFToken': csrfToken }
                    });
                    
                    if (detalleResponse.ok) {
                        const detalle = await detalleResponse.json();
                        
                        // Actualizar con generación automática activada
                        const actualizarResponse = await fetch(`/planes/api/${plan.id}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken
                            },
                            body: JSON.stringify({
                                ...detalle,
                                generacion_automatica: true,  // Activar generación automática
                                estado: 'Activo'  // Asegurar que esté activo
                            })
                        });
                        
                        if (actualizarResponse.ok) {
                            console.log(`   ✅ Generación automática activada para ${plan.codigo}`);
                        } else {
                            const errorData = await actualizarResponse.json();
                            console.log(`   ❌ Error configurando ${plan.codigo}:`, errorData);
                        }
                    }
                } catch (error) {
                    console.log(`   ❌ Error configurando ${plan.codigo}:`, error.message);
                }
            }
        }
        
        console.log('');
        console.log('✅ 3. CONFIGURACIÓN COMPLETADA');
        console.log('💡 Ahora ejecuta: generarOrdenesManualMejorado() para probar');
        
    } catch (error) {
        console.error('❌ Error en configuración:', error);
    }
}

activarTecnicosYConfiguracion();