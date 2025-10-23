// Interceptar TODOS los fetch para debugging
const originalFetch = window.fetch;
window.fetch = function (...args) {
    console.log('🚨 FETCH INTERCEPTADO:', args[0]);
    console.log('🚨 Stack trace:', new Error().stack);

    // Si es el fetch problemático, bloquearlo
    if (args[0] && args[0].includes('/api/alertas-mantenimiento')) {
        console.log('🚨 BLOQUEANDO FETCH DE ALERTAS - NO SE EJECUTARÁ');
        return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
                success: true,
                alertas: []
            })
        });
    }

    // Continuar con fetch normal para otros casos
    return originalFetch.apply(this, args);
};

console.log('🚨 FETCH INTERCEPTOR ACTIVADO - Todos los fetch serán monitoreados');
