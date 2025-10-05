// Script para generar órdenes de mantenimiento manualmente
// Ejecutar en la consola del navegador (F12)

console.log('🔄 Iniciando generación manual de órdenes...');

async function generarOrdenesManual() {
    try {
        // Obtener token CSRF
        const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content') ||
            document.querySelector('input[name=csrf_token]')?.value;

        if (!csrfToken) {
            console.error('❌ No se encontró token CSRF');
            return;
        }

        console.log('🔑 Token CSRF obtenido');

        const response = await fetch('/planes/api/generar-ordenes-manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        });

        const result = await response.json();

        if (response.ok) {
            console.log('✅ Órdenes generadas exitosamente:', result);
            const ordenes = result.ordenes_generadas || 0;
            mostrarMensaje(`Se generaron ${ordenes} órdenes de mantenimiento`, 'success');
        } else {
            console.error('❌ Error al generar órdenes:', result);
            mostrarMensaje('Error al generar órdenes: ' + (result.error || 'Error desconocido'), 'danger');
        }
    } catch (error) {
        console.error('❌ Error de conexión:', error);
        mostrarMensaje('Error de conexión: ' + error.message, 'danger');
    }
}

// Ejecutar la función
generarOrdenesManual();

console.log('📋 Para ejecutar manualmente en el futuro, escribe: generarOrdenesManual()');