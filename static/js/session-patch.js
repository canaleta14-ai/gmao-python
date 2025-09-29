// Parche para mejorar el manejo de sesiones expiradas
// Agregar este script después de main.js

// Interceptar todas las peticiones fetch para detectar sesiones expiradas
const originalFetch = window.fetch;
window.fetch = function (...args) {
    return originalFetch.apply(this, args)
        .then(response => {
            // Verificar si es una respuesta HTML cuando esperamos JSON
            const contentType = response.headers.get('Content-Type') || '';
            const url = typeof args[0] === 'string' ? args[0] : args[0].url;

            if (response.ok &&
                contentType.includes('text/html') &&
                (url.includes('/api/') || url.includes('/usuarios/api'))) {

                console.log('🔐 Sesión expirada detectada en:', url);
                // Redirigir al login después de un pequeño delay
                setTimeout(() => {
                    window.location.href = '/login';
                }, 100);

                // Retornar una promesa que nunca se resuelve para evitar errores
                return new Promise(() => { });
            }

            return response;
        });
};

console.log('🔐 Interceptor de sesión cargado');