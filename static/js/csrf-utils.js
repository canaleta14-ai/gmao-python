/**
 * Utilidades para CSRF Token en peticiones AJAX
 * Se incluye automáticamente en todas las páginas
 */

// Función para obtener el token CSRF del meta tag
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    console.warn('⚠️ CSRF token no encontrado en meta tag');
    return null;
}

// Función para obtener headers con CSRF token
function getHeadersWithCSRF(additionalHeaders = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...additionalHeaders
    };
    
    const csrfToken = getCSRFToken();
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
    
    return headers;
}

// Interceptor global para fetch - añade CSRF automáticamente
(function() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        let [url, options] = args;
        
        // Solo interceptar peticiones a rutas internas (no CDN, etc.)
        const isInternalRequest = !url.startsWith('http') || url.startsWith(window.location.origin);
        
        // Solo añadir CSRF a métodos que lo requieren
        const methodsRequiringCSRF = ['POST', 'PUT', 'PATCH', 'DELETE'];
        const method = options?.method?.toUpperCase() || 'GET';
        const requiresCSRF = methodsRequiringCSRF.includes(method);
        
        if (isInternalRequest && requiresCSRF) {
            options = options || {};
            options.headers = options.headers || {};
            
            // Convertir Headers object a plain object si es necesario
            if (options.headers instanceof Headers) {
                const plainHeaders = {};
                options.headers.forEach((value, key) => {
                    plainHeaders[key] = value;
                });
                options.headers = plainHeaders;
            }
            
            // Añadir CSRF token si no está presente
            if (!options.headers['X-CSRFToken'] && !options.headers['X-CSRF-Token']) {
                const csrfToken = getCSRFToken();
                if (csrfToken) {
                    options.headers['X-CSRFToken'] = csrfToken;
                    console.log(`🔐 CSRF token añadido a ${method} ${url}`);
                }
            }
        }
        
        return originalFetch.apply(this, [url, options]);
    };
    
    console.log('✅ Interceptor de CSRF configurado para fetch()');
})();

// Exportar funciones para uso manual si es necesario
window.CSRFUtils = {
    getToken: getCSRFToken,
    getHeaders: getHeadersWithCSRF
};
