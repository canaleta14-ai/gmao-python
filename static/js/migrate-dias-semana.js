/**
 * Script para ejecutar migración del campo dias_semana
 * Ejecutar en consola del navegador (F12 -> Console)
 * 
 * Este script:
 * 1. Ejecuta ALTER TABLE para aumentar dias_semana de VARCHAR(50) a VARCHAR(200)
 * 2. Muestra el resultado de la migración
 */

(async () => {
    const n = (m, t='info') => window.showNotificationToast?.(m, t) || console.log(`[${t}] ${m}`);
    
    try {
        console.log('🗄️ Iniciando migración de campo dias_semana...');
        n('Ejecutando migración de base de datos...', 'info');
        
        const response = await fetch('/admin/migrate-dias-semana', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅', data.message);
            n('✅ Migración completada exitosamente', 'success');
            console.log('📊 Campo dias_semana ahora soporta hasta 200 caracteres');
        } else {
            console.error('❌ Error:', data.error);
            n('Error en migración: ' + data.error, 'error');
        }
        
    } catch (e) {
        console.error('❌ Error ejecutando migración:', e);
        n('Error: ' + e.message, 'error');
    }
})();
