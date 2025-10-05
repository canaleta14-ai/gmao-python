/**
 * Seguridad de Sesión - GMAO Sistema
 * 
 * Este script maneja la seguridad de la sesión:
 * 1. Limpia datos sensibles al cerrar el navegador
 * 2. Detecta inactividad prolongada
 * 3. Advierte antes de perder cambios no guardados
 */

(function() {
    'use strict';

    // Configuración
    const CONFIG = {
        // Tiempo de inactividad antes de advertir (en milisegundos)
        INACTIVITY_WARNING: 15 * 60 * 1000, // 15 minutos
        // Tiempo de inactividad antes de logout automático
        INACTIVITY_LOGOUT: 20 * 60 * 1000,   // 20 minutos
        // Habilitar advertencias de salida
        ENABLE_EXIT_WARNING: false,  // Cambiar a true si hay formularios con datos no guardados
    };

    let inactivityTimer = null;
    let warningTimer = null;

    /**
     * Reinicia el temporizador de inactividad
     */
    function resetInactivityTimer() {
        // Limpiar temporizadores existentes
        clearTimeout(inactivityTimer);
        clearTimeout(warningTimer);

        // Advertencia después de 15 minutos
        warningTimer = setTimeout(() => {
            console.warn('⚠️ Sesión inactiva - Advertencia');
            
            // Mostrar notificación si existe el sistema de notificaciones
            if (window.showNotification) {
                window.showNotification(
                    'Sesión inactiva',
                    'Tu sesión expirará pronto por inactividad. Mueve el mouse para mantenerla activa.',
                    'warning',
                    10000
                );
            }
        }, CONFIG.INACTIVITY_WARNING);

        // Logout después de 20 minutos
        inactivityTimer = setTimeout(() => {
            console.warn('🔒 Sesión expirada por inactividad');
            
            if (window.showNotification) {
                window.showNotification(
                    'Sesión expirada',
                    'Tu sesión ha expirado por inactividad. Serás redirigido al login.',
                    'info',
                    5000
                );
            }

            // Redirigir al logout después de 2 segundos
            setTimeout(() => {
                window.location.href = '/logout';
            }, 2000);
        }, CONFIG.INACTIVITY_LOGOUT);
    }

    /**
     * Limpia datos sensibles del navegador
     */
    function clearSensitiveData() {
        try {
            // Limpiar sessionStorage (datos temporales de esta sesión)
            if (window.sessionStorage) {
                console.log('🧹 Limpiando sessionStorage...');
                sessionStorage.clear();
            }

            // NO limpiar localStorage porque puede tener preferencias del usuario
            // Solo limpiar claves específicas si es necesario
            const keysToRemove = ['temp_order_data', 'draft_solicitud', 'unsaved_changes'];
            keysToRemove.forEach(key => {
                if (localStorage.getItem(key)) {
                    console.log(`🧹 Limpiando localStorage: ${key}`);
                    localStorage.removeItem(key);
                }
            });

            console.log('✅ Datos temporales limpiados');
        } catch (e) {
            console.error('❌ Error al limpiar datos:', e);
        }
    }

    /**
     * Maneja el evento beforeunload (antes de cerrar/recargar página)
     */
    function handleBeforeUnload(event) {
        // Solo advertir si hay cambios no guardados
        if (CONFIG.ENABLE_EXIT_WARNING && hasUnsavedChanges()) {
            const message = '¿Estás seguro? Tienes cambios sin guardar.';
            event.preventDefault();
            event.returnValue = message;
            return message;
        }
    }

    /**
     * Detecta si hay cambios no guardados en formularios
     */
    function hasUnsavedChanges() {
        // Buscar formularios con clase 'unsaved-changes'
        const formsWithChanges = document.querySelectorAll('form.unsaved-changes');
        return formsWithChanges.length > 0;
    }

    /**
     * Maneja el evento unload (cuando se cierra la página)
     */
    function handleUnload() {
        // Limpiar datos temporales
        clearSensitiveData();
        
        // Nota: No podemos hacer logout aquí porque unload no espera requests async
        // El logout automático se maneja con SESSION_PERMANENT=False en Flask
        console.log('👋 Página cerrada - Sesión se cerrará al cerrar navegador');
    }

    /**
     * Marca un formulario como "con cambios no guardados"
     */
    function markFormAsUnsaved(formElement) {
        if (formElement && formElement.tagName === 'FORM') {
            formElement.classList.add('unsaved-changes');
            console.log('📝 Formulario marcado como no guardado');
        }
    }

    /**
     * Marca un formulario como "guardado"
     */
    function markFormAsSaved(formElement) {
        if (formElement && formElement.tagName === 'FORM') {
            formElement.classList.remove('unsaved-changes');
            console.log('✅ Formulario marcado como guardado');
        }
    }

    /**
     * Inicializa los event listeners
     */
    function init() {
        console.log('🔐 Seguridad de sesión activada');

        // Solo activar en páginas autenticadas (que tengan el dashboard)
        const isDashboard = document.body.classList.contains('dashboard-page') ||
                           document.querySelector('.sidebar') !== null;

        if (!isDashboard) {
            console.log('ℹ️ No es una página autenticada, seguridad de sesión no necesaria');
            return;
        }

        // Eventos de actividad del usuario
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        activityEvents.forEach(event => {
            document.addEventListener(event, resetInactivityTimer, { passive: true });
        });

        // Iniciar temporizador
        resetInactivityTimer();

        // Eventos de cierre de página
        window.addEventListener('beforeunload', handleBeforeUnload);
        window.addEventListener('unload', handleUnload);

        // Detectar cambios en formularios automáticamente
        document.addEventListener('input', (e) => {
            if (e.target.form && !e.target.form.classList.contains('unsaved-changes')) {
                markFormAsUnsaved(e.target.form);
            }
        });

        // Marcar como guardado cuando se envía el formulario
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                markFormAsSaved(e.target);
            }
        });

        console.log('✅ Event listeners de seguridad registrados');
    }

    // Exponer funciones públicas
    window.SessionSecurity = {
        markFormAsUnsaved,
        markFormAsSaved,
        clearSensitiveData,
        resetInactivityTimer,
    };

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
