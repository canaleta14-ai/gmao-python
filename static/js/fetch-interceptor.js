// Interceptar TODOS los fetch para debugging
const originalFetch = window.fetch;
window.fetch = function (...args) {
    console.log('ðŸš¨ FETCH INTERCEPTADO:', args[0]);
    console.log('ðŸš¨ Stack trace:', new Error().stack);

    // Si es el fetch problemÃ¡tico, bloquearlo
    if (args[0] && args[0].includes('/api/alertas-mantenimiento')) {
        console.log('ðŸš¨ BLOQUEANDO FETCH DE ALERTAS - NO SE EJECUTARÃ�');
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

console.log('ðŸš¨ FETCH INTERCEPTOR ACTIVADO - Todos los fetch serÃ¡n monitoreados');