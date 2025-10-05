/**
 * Script para asignación masiva de técnicos con notificaciones de Bootstrap
 * Usar en la consola del navegador (F12 → Console)
 */

// Función auxiliar para mostrar notificaciones con el sistema de la app
function mostrarNotificacion(mensaje, tipo = 'info', titulo = null) {
    if (window.showNotificationToast) {
        window.showNotificationToast(mensaje, tipo);
    } else {
        // Fallback si la función no está disponible
        console.log(`[${tipo.toUpperCase()}] ${titulo || ''}: ${mensaje}`);
    }
}

// Función auxiliar para mostrar detalles en consola con formato bonito
function mostrarDetalles(detalles) {
    if (!detalles || detalles.length === 0) return;
    
    console.log('%c📊 Detalles de Asignación:', 'font-weight: bold; font-size: 14px; color: #0d6efd;');
    console.table(detalles.map(d => ({
        'Orden': d.numero_orden,
        'Técnico': d.tecnico,
        'ID': d.orden_id
    })));
}

/**
 * PASO 1: Convertirse en Administrador
 */
async function paso1_hacerseAdmin() {
    console.log('%c🔐 PASO 1: Haciéndote administrador...', 'font-weight: bold; font-size: 14px; color: #0d6efd;');
    
    try {
        const response = await fetch('/admin/hacerme-admin', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅', data.message);
            mostrarNotificacion(data.message, 'success');
            return true;
        } else {
            console.error('❌', data.error);
            mostrarNotificacion(data.error, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('Error al actualizar rol: ' + error.message, 'error');
        return false;
    }
}

/**
 * PASO 2: Crear Técnico Demo
 */
async function paso2_crearTecnico() {
    console.log('%c👷 PASO 2: Creando técnico demo...', 'font-weight: bold; font-size: 14px; color: #0d6efd;');
    
    try {
        const response = await fetch('/admin/crear-tecnico-demo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅', data.message);
            mostrarNotificacion(data.message, 'success');
            return true;
        } else {
            console.error('❌', data.error);
            mostrarNotificacion(data.error, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('Error al crear técnico: ' + error.message, 'error');
        return false;
    }
}

/**
 * PASO 3: Asignar Técnicos a Órdenes
 */
async function paso3_asignarTecnicos() {
    console.log('%c📋 PASO 3: Asignando técnicos a órdenes...', 'font-weight: bold; font-size: 14px; color: #0d6efd;');
    
    try {
        const response = await fetch('/admin/asignar-tecnicos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ ÉXITO:', data.message);
            console.log('📊 Órdenes asignadas:', data.asignadas);
            
            mostrarNotificacion(
                `Se asignaron técnicos a ${data.asignadas} órdenes exitosamente`,
                'success'
            );
            
            if (data.detalles && data.detalles.length > 0) {
                mostrarDetalles(data.detalles);
            }
            
            return true;
        } else {
            console.error('❌', data.error);
            mostrarNotificacion(data.error, 'error');
            return false;
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarNotificacion('Error al asignar técnicos: ' + error.message, 'error');
        return false;
    }
}

/**
 * FUNCIÓN PRINCIPAL: Ejecuta todos los pasos en secuencia
 */
async function solucionCompleta() {
    console.log('%c🚀 SOLUCIÓN COMPLETA - Asignación Masiva de Técnicos', 'font-weight: bold; font-size: 16px; color: #198754; background: #d1e7dd; padding: 8px;');
    console.log('%cEjecutando 3 pasos automáticamente...', 'color: #666; font-style: italic;');
    console.log('');
    
    try {
        // Paso 1: Hacerse administrador
        const paso1Ok = await paso1_hacerseAdmin();
        if (!paso1Ok) {
            mostrarNotificacion('No se pudo completar el Paso 1. Revisa la consola.', 'warning');
            return;
        }
        
        // Pequeña pausa entre pasos
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Paso 2: Crear técnico
        const paso2Ok = await paso2_crearTecnico();
        if (!paso2Ok) {
            mostrarNotificacion('No se pudo completar el Paso 2. Revisa la consola.', 'warning');
            return;
        }
        
        // Pequeña pausa antes del paso final
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Paso 3: Asignar técnicos
        const paso3Ok = await paso3_asignarTecnicos();
        if (!paso3Ok) {
            mostrarNotificacion('No se pudo completar el Paso 3. Revisa la consola.', 'warning');
            return;
        }
        
        // Éxito total
        console.log('');
        console.log('%c✅ ¡COMPLETADO CON ÉXITO!', 'font-weight: bold; font-size: 16px; color: #198754; background: #d1e7dd; padding: 8px;');
        console.log('%cRecargando página en 3 segundos...', 'color: #666; font-style: italic;');
        
        mostrarNotificacion(
            '¡Proceso completado! Recargando página en 3 segundos...',
            'success'
        );
        
        // Recargar página después de 3 segundos
        setTimeout(() => {
            location.reload();
        }, 3000);
        
    } catch (error) {
        console.error('%c❌ ERROR CRÍTICO', 'font-weight: bold; color: #dc3545;');
        console.error(error);
        mostrarNotificacion('Error crítico: ' + error.message, 'error');
    }
}

// ==============================================================
// EJECUTAR AUTOMÁTICAMENTE AL CARGAR EL SCRIPT
// ==============================================================

console.log('%c🎯 Script de Asignación de Técnicos Cargado', 'font-weight: bold; font-size: 14px; color: #0d6efd;');
console.log('');
console.log('Funciones disponibles:');
console.log('  • solucionCompleta()     - Ejecuta todos los pasos automáticamente');
console.log('  • paso1_hacerseAdmin()   - Solo convierte en admin');
console.log('  • paso2_crearTecnico()   - Solo crea técnico demo');
console.log('  • paso3_asignarTecnicos() - Solo asigna técnicos');
console.log('');
console.log('%cEjecutando solución completa...', 'color: #198754; font-weight: bold;');
console.log('');

// Ejecutar automáticamente
solucionCompleta();
